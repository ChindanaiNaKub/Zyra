#!/usr/bin/env python3
"""Test script to confirm the fix for the pawn placement bug."""

from core.board import Board
from core.moves import generate_moves, make_move, parse_uci_move


def test_fix():
    print("=== Testing Fix for Pawn Placement Bug ===")

    # Start with standard position
    board = Board()
    board.set_startpos()
    print(f"Initial: {board.to_fen()}")

    # Make e2e4
    e2e4 = parse_uci_move(board, "e2e4")
    legal_moves = generate_moves(board)
    assert any(
        m.from_square == e2e4.from_square and m.to_square == e2e4.to_square for m in legal_moves
    )
    make_move(board, e2e4)
    print(f"After e2e4: {board.to_fen()}")

    # Verify the position is correct
    expected_after_e2e4 = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    actual_after_e2e4 = board.to_fen()
    assert (
        actual_after_e2e4 == expected_after_e2e4
    ), f"Expected {expected_after_e2e4}, got {actual_after_e2e4}"

    # Make h7h5
    h7h5 = parse_uci_move(board, "h7h5")
    legal_moves = generate_moves(board)
    assert any(
        m.from_square == h7h5.from_square and m.to_square == h7h5.to_square for m in legal_moves
    )
    make_move(board, h7h5)
    print(f"After h7h5: {board.to_fen()}")

    # Verify the final position is correct (no illegal white pawn on h6)
    expected_final = "rnbqkbnr/ppppppp1/8/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq h6 0 2"
    actual_final = board.to_fen()
    assert actual_final == expected_final, f"Expected {expected_final}, got {actual_final}"

    # Verify the board state manually
    h5_idx = 55  # h5
    h6_idx = 39  # h6
    h7_idx = 23  # h7

    assert board.squares[h5_idx] == "p", f"h5 should have black pawn, got '{board.squares[h5_idx]}'"
    assert board.squares[h6_idx] == "\u0000", f"h6 should be empty, got '{board.squares[h6_idx]}'"
    assert board.squares[h7_idx] == "\u0000", f"h7 should be empty, got '{board.squares[h7_idx]}'"
    assert board.ep_square == 39, f"EP square should be h6 (39), got {board.ep_square}"

    print("✅ All tests passed! The fix correctly prevents illegal pawn placement.")
    print("✅ En passant functionality works correctly.")
    print("✅ The user's reported illegal FEN is no longer generated.")


if __name__ == "__main__":
    test_fix()
