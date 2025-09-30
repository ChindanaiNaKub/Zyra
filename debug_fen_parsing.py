#!/usr/bin/env python3
"""Debug script to understand FEN parsing issue."""

from core.board import Board, index_to_square


def debug_fen_parsing():
    print("=== FEN Parsing Debug ===")

    # The problematic FEN from the user
    fen = "rnbqkbnr/ppppppp1/7P/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq h6 0 2"

    print(f"Parsing FEN: {fen}")

    ranks = fen.split()[0].split("/")
    print(f"Ranks: {ranks}")

    board = Board()

    for rank_idx_from_top, rank in enumerate(ranks):
        print(f"\nParsing rank {rank_idx_from_top} (from top): '{rank}'")
        file_idx = 0
        for ch in rank:
            if ch.isdigit():
                empty_count = int(ch)
                print(f"  Empty squares: {empty_count}")
                file_idx += empty_count
            else:
                idx = (rank_idx_from_top << 4) | file_idx
                square = index_to_square(idx)
                print(f"  Placing '{ch}' at index {idx} (square {square})")
                if (idx & 0x88) == 0:  # Valid square
                    board.squares[idx] = ch
                file_idx += 1

    print("\nFinal board state:")
    print(f"h5 (index 55): '{board.squares[55]}'")
    print(f"h6 (index 39): '{board.squares[39]}'")
    print(f"h7 (index 23): '{board.squares[23]}'")

    # Let's also check what the to_fen generates
    print(f"\nGenerated FEN: {board.to_fen()}")


if __name__ == "__main__":
    debug_fen_parsing()
