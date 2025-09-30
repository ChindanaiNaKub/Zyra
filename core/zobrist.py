"""Zobrist hashing utilities for 0x88 board representation.

Provides a reproducible position hash for use with transposition tables.
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from .board import Board

# Piece set for hashing
_PIECES = "PNBRQKpnbrqk"


class ZobristTable:
    """Holds Zobrist random keys and computes hashes for boards."""

    def __init__(self, seed: int = 0x9E3779B9) -> None:
        rng = random.Random(seed)

        # 128 squares for 0x88 board, though offboard indices won't be used
        self.piece_square: Dict[str, List[int]] = {
            p: [rng.getrandbits(64) for _ in range(128)] for p in _PIECES
        }
        self.side_to_move: int = rng.getrandbits(64)

        # Castling rights bits for characters in FEN castling field
        self.castling_rights: Dict[str, int] = {}
        for flag in ["K", "Q", "k", "q"]:
            self.castling_rights[flag] = rng.getrandbits(64)

        # En-passant file keys (a..h). We ignore rank to keep it simple and cheap
        self.ep_file: List[int] = [rng.getrandbits(64) for _ in range(8)]

    def hash_board(self, board: Board) -> int:
        h = 0

        # Pieces
        for idx in range(128):
            piece = board.squares[idx]
            if piece == "\u0000":
                continue
            table = self.piece_square.get(piece)
            if table is not None:
                h ^= table[idx]

        # Side to move
        if board.side_to_move == "w":
            h ^= self.side_to_move

        # Castling rights
        castling = board.castling if board.castling else "-"
        if castling and castling != "-":
            for ch in castling:
                key = self.castling_rights.get(ch)
                if key is not None:
                    h ^= key

        # En-passant file (if present)
        if board.ep_square is not None:
            file_idx = board.ep_square & 0x7
            h ^= self.ep_file[file_idx]

        return h


_GLOBAL_ZOBRIST: Optional[ZobristTable] = None


def zobrist_hash(board: Board) -> int:
    """Compute Zobrist hash for the given board using a global table.

    The table is initialized deterministically on first use.
    """
    global _GLOBAL_ZOBRIST
    if _GLOBAL_ZOBRIST is None:
        _GLOBAL_ZOBRIST = ZobristTable()
    return _GLOBAL_ZOBRIST.hash_board(board)
