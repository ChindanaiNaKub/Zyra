#!/usr/bin/env python3
"""Debug script to understand the pawn move logic issue."""

from core.board import Board, index_to_square, square_to_index


def debug_pawn_logic():
    print("=== Pawn Move Logic Debug ===")

    board = Board()
    board.set_startpos()

    print("Initial position:")
    print(board.to_fen())

    # Get the h7 pawn's position
    h7_idx = square_to_index("h7")
    print(f"h7 index: {h7_idx}")
    print(f"h7 rank_from_top: {(h7_idx >> 4) & 0x7}")
    print(f"h7 piece: '{board.squares[h7_idx]}'")

    # Make e2e4 first
    from core.moves import make_move, parse_uci_move

    e2e4 = parse_uci_move(board, "e2e4")
    print(f"\ne2e4 move: from {e2e4.from_square} to {e2e4.to_square}")
    make_move(board, e2e4)
    print(f"After e2e4: {board.to_fen()}")

    # Now try h7h5
    h7h5 = parse_uci_move(board, "h7h5")
    print(f"\nh7h5 move: from {h7h5.from_square} to {h7h5.to_square}")
    print(f"From rank_from_top: {(h7h5.from_square >> 4) & 0x7}")
    print(f"To rank_from_top: {(h7h5.to_square >> 4) & 0x7}")
    print(f"Distance: {h7h5.to_square - h7h5.from_square}")

    # Check the en passant condition manually
    print("\nEn passant condition check:")
    print(f"Piece at destination: '{board.squares[h7h5.to_square]}'")
    print(f"Side to move: '{board.side_to_move}'")
    print(f"From rank == 1: {(h7h5.from_square >> 4) == 1}")
    print(f"To rank == 3: {(h7h5.to_square >> 4) == 3}")
    print(f"Piece is pawn: {board.squares[h7h5.from_square].lower() == 'p'}")

    # Make the move
    make_move(board, h7h5)
    print(f"\nAfter h7h5: {board.to_fen()}")

    # Check all relevant squares
    squares_to_check = [23, 39, 55]  # h7, h6, h5
    for idx in squares_to_check:
        square = index_to_square(idx)
        piece = board.squares[idx]
        print(f"{square} (index {idx}): '{piece}'")


if __name__ == "__main__":
    debug_pawn_logic()
