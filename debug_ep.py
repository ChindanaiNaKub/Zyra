#!/usr/bin/env python3
"""Debug script to understand en passant logic."""

from core.board import Board
from core.moves import make_move, parse_uci_move


def debug_ep():
    print("=== En Passant Debug ===")

    board = Board()
    board.set_startpos()

    # Make e2e4 (white pawn double move)
    e2e4 = parse_uci_move(board, "e2e4")
    print(f"e2e4 move: from {e2e4.from_square} to {e2e4.to_square}")
    print(f"From rank_from_top: {(e2e4.from_square >> 4) & 0x7}")
    print(f"To rank_from_top: {(e2e4.to_square >> 4) & 0x7}")
    print(f"Side to move: '{board.side_to_move}'")
    print(f"Piece at from: '{board.squares[e2e4.from_square]}'")

    make_move(board, e2e4)
    print(f"After e2e4: {board.to_fen()}")
    print(f"EP square: {board.ep_square}")

    # Also test black pawn double move
    board2 = Board()
    board2.set_startpos()
    make_move(board2, e2e4)  # e2e4 first

    h7h5 = parse_uci_move(board2, "h7h5")
    print(f"\nh7h5 move: from {h7h5.from_square} to {h7h5.to_square}")
    print(f"From rank_from_top: {(h7h5.from_square >> 4) & 0x7}")
    print(f"To rank_from_top: {(h7h5.to_square >> 4) & 0x7}")
    print(f"Side to move: '{board2.side_to_move}'")
    print(f"Piece at from: '{board2.squares[h7h5.from_square]}'")

    make_move(board2, h7h5)
    print(f"After h7h5: {board2.to_fen()}")
    print(f"EP square: {board2.ep_square}")


if __name__ == "__main__":
    debug_ep()
