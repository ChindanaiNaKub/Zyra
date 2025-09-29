"""Board representation and state management.

This module implements the 0x88 mailbox board representation for efficient
chess position handling and state management.
"""

from __future__ import annotations

from typing import List, Optional

FILES = "abcdefgh"
RANKS = "12345678"


def square_to_index(square: str) -> int:
    """Convert algebraic square like 'e4' to 0x88 index.

    a1 -> 0, b1 -> 1, ..., a8 -> 112
    """
    file_char = square[0]
    rank_char = square[1]
    file_idx = FILES.index(file_char)
    rank_idx_from_top = 8 - int(rank_char)  # rank '8' is top row
    return (rank_idx_from_top << 4) | file_idx


def index_to_square(index: int) -> str:
    """Convert 0x88 index to algebraic square like 'e4'."""
    file_idx = index & 0x7
    rank_idx_from_top = (index >> 4) & 0x7
    return f"{FILES[file_idx]}{8 - rank_idx_from_top}"


class Board:
    """Represents a chess board with 0x88 mailbox representation."""

    def __init__(self) -> None:
        """Initialize an empty board and default state."""
        # 128-length 0x88 board; use '\u0000' for empty squares
        self.squares: List[str] = ["\u0000"] * 128
        self.side_to_move: str = "w"
        self.castling: str = "-"
        self.ep_square: Optional[int] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1

    # -------------------- FEN Handling --------------------
    def load_fen(self, fen: str) -> None:
        """Load a position from FEN notation.

        Supports standard 6-field FEN: piece placement, side, castling, ep, halfmove, fullmove
        """
        fields = fen.strip().split()
        if len(fields) < 2:
            raise ValueError("Invalid FEN: missing required fields")

        placement = fields[0]
        self.side_to_move = fields[1]
        self.castling = fields[2] if len(fields) > 2 else "-"
        ep_field = fields[3] if len(fields) > 3 else "-"
        self.halfmove_clock = int(fields[4]) if len(fields) > 4 else 0
        self.fullmove_number = int(fields[5]) if len(fields) > 5 else 1

        # Reset board
        for i in range(128):
            if (i & 0x88) == 0:
                self.squares[i] = "\u0000"

        ranks = placement.split("/")
        if len(ranks) != 8:
            raise ValueError("Invalid FEN: expected 8 ranks")

        for rank_idx_from_top, rank in enumerate(ranks):
            file_idx = 0
            for ch in rank:
                if ch.isdigit():
                    file_idx += int(ch)
                else:
                    idx = (rank_idx_from_top << 4) | file_idx
                    if (idx & 0x88) != 0:
                        raise ValueError("Invalid square index while parsing FEN")
                    self.squares[idx] = ch
                    file_idx += 1

        if ep_field == "-":
            self.ep_square = None
        else:
            self.ep_square = square_to_index(ep_field)

    def to_fen(self) -> str:
        """Convert current position to FEN notation."""
        rank_strs: List[str] = []
        for rank_idx_from_top in range(8):
            empties = 0
            parts: List[str] = []
            for file_idx in range(8):
                idx = (rank_idx_from_top << 4) | file_idx
                piece = self.squares[idx]
                if piece == "\u0000":
                    empties += 1
                else:
                    if empties:
                        parts.append(str(empties))
                        empties = 0
                    parts.append(piece)
            if empties:
                parts.append(str(empties))
            rank_strs.append("".join(parts))

        placement = "/".join(rank_strs)
        side = self.side_to_move
        castling = self.castling if self.castling != "" else "-"
        ep = index_to_square(self.ep_square) if self.ep_square is not None else "-"
        return f"{placement} {side} {castling} {ep} {self.halfmove_clock} {self.fullmove_number}"

    # -------------------- Utilities --------------------
    def set_startpos(self) -> None:
        """Load the standard chess starting position."""
        self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
