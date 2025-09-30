"""Minimal FastAPI web server to play against Zyra locally.

Routes:
- POST /api/new: start a new game session
- POST /api/move: apply a user move and get engine reply
- GET  /api/state: get current game state (fen, history, side, eval)
- GET  /api/legal: list legal target squares for a given origin square

Static assets served from sibling `static/` directory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.board import Board
from core.moves import generate_moves, make_move, parse_uci_move
from eval.heuristics import Evaluation, parse_style_config
from search.mcts import MCTSSearch, heuristic_move_ordering


@dataclass
class GameSession:
    board: Board = field(default_factory=Board)
    history: List[str] = field(default_factory=list)  # UCI moves
    style: Optional[Dict[str, float]] | str = None
    movetime_ms: Optional[int] = 500

    def reset(
        self, style: Optional[Dict[str, float] | str] = None, movetime_ms: Optional[int] = None
    ) -> None:
        self.board.set_startpos()
        self.history.clear()
        if style is not None:
            self.style = style
        if movetime_ms is not None:
            self.movetime_ms = movetime_ms

    def to_state(self, last_eval_cp: Optional[float] = None) -> Dict[str, Any]:
        return {
            "fen": self.board.to_fen(),
            "history": list(self.history),
            "side_to_move": self.board.side_to_move,
            "eval_cp": last_eval_cp,
        }


app = FastAPI(title="Zyra Web UI", version="0.1.0")
session = GameSession()


def _compute_engine_move(
    board: Board, movetime_ms: Optional[int], style: Optional[Dict[str, float] | str]
) -> Optional[str]:
    # Configure search
    search = MCTSSearch(
        max_playouts=10_000,
        movetime_ms=movetime_ms,
        move_ordering_hook=heuristic_move_ordering,
        style=style,
    )
    # IMPORTANT: Run search on a copy to avoid any accidental mutations from
    # move generation/unmake during search corrupting the live game board.
    board_copy = Board()
    board_copy.copy_from(board)
    best = search.search(board_copy)
    if best is None:
        return None
    files = "abcdefgh"

    def sq(idx: int) -> str:
        f = idx & 0x7
        r = (idx >> 4) & 0x7
        return f"{files[f]}{8 - r}"

    uci = f"{sq(best.from_square)}{sq(best.to_square)}"
    if best.promotion and best.promotion not in ("O-O", "O-O-O"):
        uci += best.promotion.lower()
    return uci


def _alg_to_index(alg: str) -> Optional[int]:
    """Convert algebraic square like 'e2' to internal 0x88 index.
    Returns None if invalid input.
    """
    if not alg or len(alg) != 2:
        return None
    files = "abcdefgh"
    file_char = alg[0]
    rank_char = alg[1]
    if file_char not in files or not rank_char.isdigit():
        return None
    file_idx = files.index(file_char)
    rank_num = int(rank_char)
    if rank_num < 1 or rank_num > 8:
        return None
    r = 8 - rank_num
    return (r << 4) | file_idx


@app.post("/api/new")
def api_new(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    style = None
    movetime_ms = None
    if payload:
        style = payload.get("style")
        movetime_ms = payload.get("movetime_ms")
        if isinstance(style, str) or isinstance(style, dict):
            style = parse_style_config(style)
    session.reset(style=style, movetime_ms=movetime_ms)
    return session.to_state()


@app.post("/api/move")
def api_move(payload: Dict[str, Any]) -> Dict[str, Any]:
    uci: str = payload.get("uci")
    promotion: Optional[str] = payload.get("promotion")
    if not uci or len(uci) < 4:
        raise HTTPException(status_code=400, detail="Missing or invalid move")

    # Apply player move if legal
    try:
        if promotion and len(uci) == 4:
            uci = uci + promotion.lower()
        mv = parse_uci_move(session.board, uci)
        legal = generate_moves(session.board)
        is_legal = any(
            lm.from_square == mv.from_square
            and lm.to_square == mv.to_square
            and lm.promotion == mv.promotion
            for lm in legal
        )
        if not is_legal:
            raise HTTPException(status_code=400, detail="Illegal move")
        make_move(session.board, mv)
        session.history.append(uci)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid move: {e}")

    # Engine reply
    engine_uci = _compute_engine_move(session.board, session.movetime_ms, session.style)
    last_eval_cp: Optional[float] = None
    if engine_uci:
        mv2 = parse_uci_move(session.board, engine_uci)
        make_move(session.board, mv2)
        session.history.append(engine_uci)
        evaluator = Evaluation(style_weights=parse_style_config(session.style))
        last_eval_cp = evaluator.evaluate(session.board)

    return session.to_state(last_eval_cp=last_eval_cp)


@app.get("/api/state")
def api_state() -> Dict[str, Any]:
    evaluator = Evaluation(style_weights=parse_style_config(session.style))
    last_eval_cp = evaluator.evaluate(session.board)
    return session.to_state(last_eval_cp=last_eval_cp)


@app.get("/api/legal")
def api_legal(from_sq: str = Query(..., alias="from")) -> Dict[str, Any]:
    """Return legal targets for the given origin algebraic square.
    Response: { "from": "e2", "targets": ["e3", "e4", ...] }
    """
    idx = _alg_to_index(from_sq)
    if idx is None:
        raise HTTPException(status_code=400, detail="Invalid from square")
    legal = generate_moves(session.board)
    files = "abcdefgh"

    def to_alg(index: int) -> str:
        f = index & 0x7
        r = (index >> 4) & 0x7
        return f"{files[f]}{8 - r}"

    targets: List[str] = [to_alg(mv.to_square) for mv in legal if mv.from_square == idx]
    return {"from": from_sq, "targets": targets}


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Zyra Web UI</title>
    <link rel=\"stylesheet\" href=\"/static/style.css\" />
  </head>
  <body>
    <div id=\"app\"></div>
    <script src=\"/static/app.js\"></script>
  </body>
</html>
        """,
        media_type="text/html",
    )


def main() -> None:
    import argparse
    import os

    # Mount static after app creation so CLI entry works
    # Static directory is next to this file under `static/`
    import pathlib
    import socket

    import uvicorn

    static_dir = pathlib.Path(__file__).with_name("static")
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Ensure a session exists
    if not session.history:
        session.reset()

    # Parse host/port from CLI/env with sensible defaults
    parser = argparse.ArgumentParser(prog="zyra-web", add_help=True)
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", os.environ.get("ZYRA_WEB_HOST", "127.0.0.1")),
        help="Host/IP to bind",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", os.environ.get("ZYRA_WEB_PORT", 8000))),
        help="Port to bind",
    )
    parser.add_argument(
        "--allow-port-fallback", action="store_true", help="If port busy, try next ports up to +10"
    )
    args = parser.parse_args()

    host: str = args.host
    port: int = args.port

    def is_port_free(h: str, p: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((h, p))
            except OSError:
                return False
            return True

    selected_port = port
    if args.allow_port_fallback and not is_port_free(host, port):
        for delta in range(1, 11):
            candidate = port + delta
            if is_port_free(host, candidate):
                selected_port = candidate
                break

    uvicorn.run(app, host=host, port=selected_port)


if __name__ == "__main__":
    main()
