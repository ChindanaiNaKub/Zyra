"""UCI protocol implementation.

This module provides UCI protocol support for communication with
chess GUIs like Cute Chess and Arena.
"""

import random
import sys
from typing import List, Optional

from core.board import Board
from core.moves import Move, generate_moves, make_move, parse_uci_move, unmake_move
from search.mcts import heuristic_move_ordering
from search.mcts_optimized import OptimizedMCTSSearch


class UCIEngine:
    """UCI protocol engine interface."""

    def __init__(self) -> None:
        """Initialize UCI engine."""
        self.position: Board = Board()
        self.search_engine: Optional[OptimizedMCTSSearch] = None

    def handle_command(self, command: str) -> Optional[str]:
        """Handle UCI protocol commands."""
        parts = command.strip().split()

        if not parts:
            return None

        cmd = parts[0].lower()

        if cmd == "uci":
            # Provide proper UCI identification and acknowledge
            return "id name Zyra\nid author Zyra Project\nuciok"
        elif cmd == "isready":
            return "readyok"
        elif cmd == "ucinewgame":
            self.position.set_startpos()
            return None
        elif cmd == "position":
            # Supported: 'position startpos [moves ...]' or 'position fen <fen> [moves ...]'
            try:
                self._handle_position(parts[1:])
            except Exception:
                # For robustness in early phase, ignore malformed input silently
                pass
            return None
        elif cmd == "go":
            return self._handle_go_command(parts[1:])
        elif cmd == "quit":
            sys.exit(0)

        return None

    def run_uci_loop(self) -> None:
        """Main UCI protocol loop."""
        while True:
            try:
                command = input().strip()
                response = self.handle_command(command)
                if response:
                    # Always flush so GUIs receive responses immediately
                    print(response, flush=True)
            except EOFError:
                break
            except Exception as e:
                # Log errors to GUI and continue
                print(f"info string Error: {type(e).__name__}: {e}", flush=True)
                # For debugging - also write to stderr
                import traceback

                traceback.print_exc(file=sys.stderr)

    # ---------------- internal helpers ----------------
    def _handle_position(self, args: List[str]) -> None:
        if not args:
            return
        token = args[0]
        idx = 1
        if token == "startpos":
            self.position.set_startpos()
        elif token == "fen":
            # FEN is 6 fields
            fen_fields = args[1:7]
            fen = " ".join(fen_fields)
            self.position.load_fen(fen)
            idx = 7
        # apply moves if present
        if idx < len(args) and args[idx] == "moves":
            for mv in args[idx + 1 :]:
                self._apply_uci_move(mv)

    def _apply_uci_move(self, uci: str) -> None:
        try:
            mv = parse_uci_move(self.position, uci)
            # Apply only if legal
            legal = generate_moves(self.position)
            for lm in legal:
                if (
                    lm.from_square == mv.from_square
                    and lm.to_square == mv.to_square
                    and lm.promotion == mv.promotion
                ):
                    make_move(self.position, mv)
                    return
            # If not legal, ignore in minimal implementation
        except Exception:
            # Ignore malformed moves for robustness in early phase
            return

    def _handle_go_command(self, args: List[str]) -> str:
        """Handle UCI go command with time controls, movetime, and nodes parameters."""
        movetime_ms = None
        max_nodes = None
        seed = None
        wtime = None
        btime = None
        winc = 0
        binc = 0

        # Parse parameters
        i = 0
        while i < len(args):
            if args[i] == "movetime" and i + 1 < len(args):
                movetime_ms = int(args[i + 1])
                i += 2
            elif args[i] == "nodes" and i + 1 < len(args):
                max_nodes = int(args[i + 1])
                i += 2
            elif args[i] == "wtime" and i + 1 < len(args):
                wtime = int(args[i + 1])
                i += 2
            elif args[i] == "btime" and i + 1 < len(args):
                btime = int(args[i + 1])
                i += 2
            elif args[i] == "winc" and i + 1 < len(args):
                winc = int(args[i + 1])
                i += 2
            elif args[i] == "binc" and i + 1 < len(args):
                binc = int(args[i + 1])
                i += 2
            elif args[i] == "depth" and i + 1 < len(args):
                # Unsupported depth flag - log non-fatal note
                print(
                    f"info string Unsupported depth parameter {args[i + 1]}, using default behavior",
                    flush=True,
                )
                i += 2
            else:
                i += 1

        # Calculate move time from clock time if not specified directly
        if movetime_ms is None and (wtime is not None or btime is not None):
            # Use our remaining time (based on side to move)
            # Note: side_to_move is 'w' or 'b', not 0 or 1
            our_time = wtime if self.position.side_to_move == "w" else btime
            if our_time is not None:
                # Simple time management: use 1/30th of remaining time + increment
                our_inc = winc if self.position.side_to_move == "w" else binc
                movetime_ms = max(100, (our_time // 30) + (our_inc // 2))

        # Get legal moves first
        legal_moves = generate_moves(self.position)
        if not legal_moves:
            return "bestmove 0000"

        # If no search parameters, use random move (fallback)
        if movetime_ms is None and max_nodes is None:
            chosen = random.choice(legal_moves)
            uci_move = f"{self._sq(chosen.from_square)}{self._sq(chosen.to_square)}"
            return f"bestmove {uci_move}"

        # Create optimized search engine with parameters
        max_playouts = max_nodes if max_nodes else 10000
        # Use current time as seed for randomness if no seed provided
        if seed is None:
            import time

            seed = int(time.time() * 1000000) % (2**31)

        # Apply a small safety margin to movetime to stabilize PV near deadlines
        if movetime_ms is not None:
            buffered_movetime = max(0, int(movetime_ms * 0.95))
        else:
            buffered_movetime = None

        self.search_engine = OptimizedMCTSSearch(
            max_playouts=max_playouts,
            movetime_ms=buffered_movetime,
            seed=seed,
            move_ordering_hook=heuristic_move_ordering,
            enable_caching=True,
            enable_move_ordering=True,
        )

        # Run search
        best_move = self.search_engine.search(self.position)

        if best_move:
            uci_move = f"{self._sq(best_move.from_square)}{self._sq(best_move.to_square)}"
            if best_move.promotion:
                uci_move += best_move.promotion.lower()
            return f"bestmove {uci_move}"
        else:
            # Fallback to random move if search fails
            chosen = random.choice(legal_moves)
            uci_move = f"{self._sq(chosen.from_square)}{self._sq(chosen.to_square)}"
            return f"bestmove {uci_move}"

    def go(
        self,
        movetime: Optional[int] = None,
        nodes: Optional[int] = None,
        wtime: Optional[int] = None,
        btime: Optional[int] = None,
        winc: Optional[int] = None,
        binc: Optional[int] = None,
    ) -> str:
        """
        Direct method to search for a best move, bypassing UCI command parsing.
        This is used by GUI applications that need direct access to the engine.
        """
        # Build args list similar to what UCI command would provide
        args = []
        if movetime is not None:
            args.extend(["movetime", str(movetime)])
        if nodes is not None:
            args.extend(["nodes", str(nodes)])
        if wtime is not None:
            args.extend(["wtime", str(wtime)])
        if btime is not None:
            args.extend(["btime", str(btime)])
        if winc is not None:
            args.extend(["winc", str(winc)])
        if binc is not None:
            args.extend(["binc", str(binc)])

        return self._handle_go_command(args)

    def _sq(self, index: int) -> str:
        file_idx = index & 0x7
        rank_idx_from_top = (index >> 4) & 0x7
        files = "abcdefgh"
        return f"{files[file_idx]}{8 - rank_idx_from_top}"


def main() -> None:
    """Entrypoint for running the engine in UCI mode."""
    engine = UCIEngine()
    engine.run_uci_loop()


if __name__ == "__main__":
    main()
