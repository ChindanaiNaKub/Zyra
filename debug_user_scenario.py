#!/usr/bin/env python3
"""Debug script to reproduce the exact user scenario."""

from core.board import Board


def debug_user_scenario():
    print("=== User Scenario Debug ===")

    # Start with the user's reported problematic FEN
    user_fen = "rnbqkbnr/ppppppp1/7P/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq h6 0 2"

    print(f"User's problematic FEN: {user_fen}")

    # Load this position
    board = Board()
    board.load_fen(user_fen)

    print(f"Loaded position: {board.to_fen()}")

    # Check the problematic squares
    print("Checking problematic squares:")
    print(f"h6 (index 39): '{board.squares[39]}' (should be empty)")
    print(f"h5 (index 55): '{board.squares[55]}' (should be black pawn)")

    # This position is illegal because it has pawns on both h6 and h5
    # Let's see what a correct position should look like

    print("\n=== What the correct position should look like ===")
    correct_fen = "rnbqkbnr/ppppppp1/8/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq h6 0 2"
    correct_board = Board()
    correct_board.load_fen(correct_fen)

    print(f"Correct position FEN: {correct_fen}")
    print(f"Correct h6 (index 39): '{correct_board.squares[39]}'")
    print(f"Correct h5 (index 55): '{correct_board.squares[55]}'")

    # The difference is that user's FEN has '7P' on rank 6, correct has '8' on rank 6
    print("\nThe only difference is:")
    print(f"User rank 6: '7P' (white pawn on h6)")
    print(f"Correct rank 6: '8' (empty)")

    # Let's see what happens if we manually fix the user's FEN
    print("\n=== Manual fix of user's FEN ===")
    fixed_fen = user_fen.replace("7P", "8")
    print(f"Fixed FEN: {fixed_fen}")

    fixed_board = Board()
    fixed_board.load_fen(fixed_fen)
    print(f"Fixed position: {fixed_board.to_fen()}")


if __name__ == "__main__":
    debug_user_scenario()
