#!/usr/bin/env python3
"""Debug script to understand 0x88 indexing."""

from core.board import index_to_square, square_to_index


def debug_indices():
    print("=== 0x88 Index Debugging ===")

    # Test key squares
    squares = ["h7", "h6", "h5", "e4", "e3", "e2"]
    for sq in squares:
        idx = square_to_index(sq)
        back = index_to_square(idx)
        print(f"{sq} -> index {idx} -> {back}")

    print("\n=== Index calculations ===")
    # Manual calculations for key squares
    for file_char in "abcdefgh":
        for rank_char in "12345678":
            sq = file_char + rank_char
            idx = square_to_index(sq)
            rank_from_top = (idx >> 4) & 0x7
            file_idx = idx & 0x7
            print(f"{sq}: index={idx}, rank_from_top={rank_from_top}, file={file_idx}")

    print("\n=== Testing move calculation ===")
    # For h7h5 move
    h7 = square_to_index("h7")
    h5 = square_to_index("h5")
    print(f"h7 index: {h7}")
    print(f"h5 index: {h5}")
    print(f"Difference: {h5 - h7}")
    print(f"Direction: {'up' if h5 > h7 else 'down'}")

    # Check if the move is +32 (two squares forward for black)
    expected_diff = 32 if h5 > h7 else -32
    print(f"Expected double move diff: {expected_diff}")
    print(f"Actual diff: {h5 - h7}")


if __name__ == "__main__":
    debug_indices()
