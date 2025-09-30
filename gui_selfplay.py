#!/usr/bin/env python3
"""
Zyra GUI Self-Play

Simple desktop viewer that runs a self-play game and visualizes it with:
- Board with animated piece moves (left)
- SAN notation move list with move numbers (right)

Usage examples:
  python gui_selfplay.py --movetime 300 --animate --delay 80
  python gui_selfplay.py --nodes 2000

This uses the existing Board and engine components from the project.
"""

from __future__ import annotations

import argparse
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

from core.board import Board, index_to_square
from core.moves import Move, generate_moves, make_move
from interfaces.uci import UCIEngine

FILES = "abcdefgh"


def square_to_coords(square_index: int) -> Tuple[int, int]:
    file_idx = square_index & 0x7
    rank_idx_from_top = (square_index >> 4) & 0x7
    return file_idx, rank_idx_from_top


def coords_to_canvas_xy(file_idx: int, rank_idx_from_top: int, cell: int) -> Tuple[int, int]:
    return file_idx * cell, rank_idx_from_top * cell


def move_to_san(board: Board, move: Move) -> str:
    # Lightweight SAN similar to cli.runner._move_to_san usage but reimplemented locally
    # to avoid import cycle; prefer uci text when SAN uncertain
    try:
        from cli.runner import _move_to_san as core_move_to_san  # type: ignore

        return core_move_to_san(board, move)
    except Exception:
        from_file = move.from_square & 0x7
        from_rank = move.from_square >> 4
        to_file = move.to_square & 0x7
        to_rank = move.to_square >> 4
        uci = f"{FILES[from_file]}{from_rank + 1}{FILES[to_file]}{to_rank + 1}"
        if move.promotion:
            uci += move.promotion.lower()
        return uci


@dataclass
class Theme:
    light: str = "#f0d9b5"
    dark: str = "#b58863"
    highlight: str = "#f6f669"


class BoardCanvas(tk.Canvas):
    def __init__(self, master: tk.Widget, cell_size: int = 72, theme: Theme = Theme()):
        super().__init__(
            master, width=cell_size * 8, height=cell_size * 8, bg="white", highlightthickness=0
        )
        self.cell = cell_size
        self.theme = theme
        self._images: Dict[str, tk.PhotoImage] = {}
        self._piece_items: Dict[int, int] = {}
        self._draw_squares()

    def _draw_squares(self) -> None:
        c = self.cell
        for r in range(8):
            for f in range(8):
                x0, y0 = f * c, r * c
                x1, y1 = x0 + c, y0 + c
                is_light = (r + f) % 2 == 0
                self.create_rectangle(
                    x0, y0, x1, y1, fill=self.theme.light if is_light else self.theme.dark, width=0
                )

    def draw_board(self, board: Board) -> None:
        # Clear old pieces
        for item in list(self._piece_items.values()):
            self.delete(item)
        self._piece_items.clear()

        # Draw pieces as text glyphs for simplicity (fast, no assets)
        c = self.cell
        for rank_idx_from_top in range(8):
            for file_idx in range(8):
                idx = (rank_idx_from_top << 4) | file_idx
                piece = board.squares[idx]
                if piece == "\u0000":
                    continue
                x = file_idx * c + c // 2
                y = rank_idx_from_top * c + c // 2
                font = ("Segoe UI Symbol", int(c * 0.6))
                glyph = self._piece_glyph(piece)
                self._piece_items[idx] = self.create_text(x, y, text=glyph, font=font)

    def animate_move(self, board: Board, move: Move, duration_ms: int = 200) -> None:
        # Move the piece smoothly from origin to target while not mutating board until end
        origin = move.from_square
        target = move.to_square
        from_f, from_r = square_to_coords(origin)
        to_f, to_r = square_to_coords(target)
        c = self.cell
        start_x = from_f * c + c // 2
        start_y = from_r * c + c // 2
        end_x = to_f * c + c // 2
        end_y = to_r * c + c // 2

        # Find or create a temporary glyph for animation
        piece = board.squares[origin]
        glyph = self._piece_glyph(piece)
        font = ("Segoe UI Symbol", int(c * 0.6))
        temp = self.create_text(start_x, start_y, text=glyph, font=font)

        steps = max(1, duration_ms // 16)
        for i in range(1, steps + 1):
            t = i / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            self.coords(temp, x, y)
            self.update_idletasks()
            self.after(16)

        self.delete(temp)

    def _piece_glyph(self, p: str) -> str:
        mapping = {
            "P": "♙",
            "N": "♘",
            "B": "♗",
            "R": "♖",
            "Q": "♕",
            "K": "♔",
            "p": "♟",
            "n": "♞",
            "b": "♝",
            "r": "♜",
            "q": "♛",
            "k": "♚",
        }
        return mapping.get(p, "?")


class SelfPlayApp(tk.Tk):
    def __init__(self, args: argparse.Namespace):
        super().__init__()
        self.title("Zyra Self-Play")
        self.geometry("980x620")

        # Left: board; Right: move list
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.board_widget = BoardCanvas(self, cell_size=70)
        self.board_widget.grid(row=0, column=0, padx=16, pady=16)

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=16)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(right, textvariable=self.status_var, font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, sticky="w"
        )

        self.move_list = tk.Listbox(right, font=("Consolas", 12))
        self.move_list.grid(row=1, column=0, sticky="nsew")

        controls = ttk.Frame(right)
        controls.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(controls, text="Start Self-Play", command=self.start_game).pack(side=tk.LEFT)
        ttk.Button(controls, text="Quit", command=self.destroy).pack(side=tk.RIGHT)

        # Engine state
        self.args = args
        self.board = Board()
        if args.fen:
            self.board.load_fen(args.fen)
        else:
            self.board.set_startpos()

        self.engine = UCIEngine()
        self.engine.position = self.board

        self.board_widget.draw_board(self.board)

        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()

    def start_game(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self.move_list.delete(0, tk.END)
        self.status_var.set("Running self-play...")
        self._thread = threading.Thread(target=self._run_game_loop, daemon=True)
        self._thread.start()

    def _run_game_loop(self) -> None:
        ply = 0
        while not self._stop.is_set():
            # Think
            best = self.engine.go(
                movetime=self.args.movetime,
                nodes=self.args.nodes,
            )
            if not best or not best.startswith("bestmove "):
                self._set_status("No bestmove; stopping.")
                break
            uci = best.split()[1]

            # Parse to Move using existing helpers
            from core.moves import parse_uci_move  # local import avoids cycle at module import

            try:
                mv = parse_uci_move(self.engine.position, uci)
            except Exception:
                self._set_status(f"Illegal or parse error for {uci}; stopping.")
                break

            # Validate move is legal - the engine should have already done this, but double-check
            from core.moves import is_legal_move

            if not is_legal_move(self.engine.position, mv):
                self._set_status(f"Engine chose illegal move {uci}; stopping.")
                break

            # Animate then apply
            if self.args.animate:
                self._animate_on_ui(mv, self.args.delay)

            san = move_to_san(self.engine.position, mv)
            make_move(self.engine.position, mv)

            # Update list and board
            ply += 1
            move_num = (ply + 1) // 2
            prefix = f"{move_num}. " if ply % 2 == 1 else f"{move_num}... "
            self._append_move(prefix + san)
            self._redraw_board()

            # Simple termination: stop at mate/stalemate or max plies
            if self.args.max_plies and ply >= self.args.max_plies:
                self._set_status("Reached max plies; done.")
                break

        self._set_status("Stopped.")

    def _animate_on_ui(self, move: Move, delay_ms: int) -> None:
        # Must schedule on main thread
        result = threading.Event()

        def do_anim() -> None:
            self.board_widget.animate_move(self.engine.position, move, duration_ms=delay_ms)
            result.set()

        self.after(0, do_anim)
        result.wait()

    def _append_move(self, text: str) -> None:
        def on_ui() -> None:
            self.move_list.insert(tk.END, text)
            self.move_list.yview_moveto(1.0)

        self.after(0, on_ui)

    def _redraw_board(self) -> None:
        def on_ui() -> None:
            self.board_widget.draw_board(self.engine.position)

        self.after(0, on_ui)

    def _set_status(self, text: str) -> None:
        def on_ui() -> None:
            self.status_var.set(text)

        self.after(0, on_ui)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zyra GUI self-play viewer")
    parser.add_argument("--fen", default=None, help="Starting FEN")
    parser.add_argument("--movetime", type=int, default=300, help="Movetime per ply in ms")
    parser.add_argument("--nodes", type=int, default=None, help="Node limit per ply")
    parser.add_argument("--max-plies", type=int, default=120, help="Maximum plies to play")
    parser.add_argument("--animate", action="store_true", help="Animate piece movement")
    parser.add_argument("--delay", type=int, default=200, help="Animation duration in ms")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = SelfPlayApp(args)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
