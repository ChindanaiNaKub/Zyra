"""UCI protocol implementation.

This module provides UCI protocol support for communication with
chess GUIs like Cute Chess and Arena.
"""

import random
import sys
from typing import List, Optional

from core.board import Board
from core.moves import Move, generate_moves, make_move, parse_uci_move, unmake_move


class UCIEngine:
    """UCI protocol engine interface."""

    def __init__(self) -> None:
        """Initialize UCI engine."""
        self.position: Board = Board()
        self.search_engine = None

    def handle_command(self, command: str) -> Optional[str]:
        """Handle UCI protocol commands."""
        parts = command.strip().split()

        if not parts:
            return None

        cmd = parts[0].lower()

        if cmd == "uci":
            # Minimal identity; can be expanded with 'id name' and 'id author'
            return "uciok"
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
            # Minimal: pick a random legal move
            legal_moves = generate_moves(self.position)
            if legal_moves:
                chosen = random.choice(legal_moves)
                uci_move = f"{self._sq(chosen.from_square)}{self._sq(chosen.to_square)}"
                return f"bestmove {uci_move}"
            return "bestmove 0000"
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
                    print(response)
            except EOFError:
                break

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

    def _sq(self, index: int) -> str:
        file_idx = index & 0x7
        rank_idx_from_top = (index >> 4) & 0x7
        files = "abcdefgh"
        return f"{files[file_idx]}{8 - rank_idx_from_top}"
