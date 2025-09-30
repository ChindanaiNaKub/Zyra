#!/usr/bin/env python3
"""Debug script to reproduce the pawn placement bug."""

from core.board import Board, index_to_square
from core.moves import generate_moves, make_move, parse_uci_move


def debug_bug():
    print("=== Reproducing the pawn bug ===")

    # Start with standard position
    board = Board()
    board.set_startpos()
    print(f"Initial position: {board.to_fen()}")

    # Make the move e2e4
    move = parse_uci_move(board, "e2e4")
    print(f"Parsed move: from {move.from_square} to {move.to_square}")

    # Check if move is legal
    legal_moves = generate_moves(board)
    print(f"Number of legal moves: {len(legal_moves)}")

    # Find e2e4 in legal moves
    e2e4_move = None
    for mv in legal_moves:
        if mv.from_square == move.from_square and mv.to_square == move.to_square:
            e2e4_move = mv
            break

    if e2e4_move is None:
        print("ERROR: e2e4 not found in legal moves!")
        return

    print(f"Found e2e4 in legal moves: {e2e4_move}")

    # Make the move
    print("Making move e2e4...")
    make_move(board, e2e4_move)
    print(f"After e2e4: {board.to_fen()}")

    # Now try to make h7h5
    print("\nTrying to make h7h5...")
    move_h7h5 = parse_uci_move(board, "h7h5")
    print(f"Parsed h7h5: from {move_h7h5.from_square} to {move_h7h5.to_square}")

    legal_moves = generate_moves(board)
    print(f"Number of legal moves after e2e4: {len(legal_moves)}")

    h7h5_found = False
    for mv in legal_moves:
        if mv.from_square == move_h7h5.from_square and mv.to_square == move_h7h5.to_square:
            print(f"Found h7h5 in legal moves: {mv}")
            h7h5_found = True
            print("Making move h7h5...")
            make_move(board, mv)
            break

    if not h7h5_found:
        print("ERROR: h7h5 not found in legal moves!")

    print(f"Final position: {board.to_fen()}")

    # Check for the problematic pawns
    # In 0x88 format: rank 8 (top) = 0, rank 1 (bottom) = 7
    # From the index debugging, we know:
    # h7: index 23 (rank_from_top=1, file=7)
    # h6: index 39 (rank_from_top=2, file=7)
    # h5: index 55 (rank_from_top=3, file=7)
    h5_idx = 55  # h5
    h6_idx = 39  # h6

    print(f"Pawn at h5 (index {h5_idx}): '{board.squares[h5_idx]}'")
    print(f"Pawn at h6 (index {h6_idx}): '{board.squares[h6_idx]}'")
    print(f"EP square: {board.ep_square}")
    if board.ep_square is not None:
        print(f"EP square algebraic: {index_to_square(board.ep_square)}")

    # Let's also check what squares h7 and h5 should be
    h7_idx = 1 * 16 + 7  # h7 (rank 1 from top)
    print(f"Pawn at h7 (index {h7_idx}): '{board.squares[h7_idx]}'")
    print(f"Pawn at h5 (index {h5_idx}): '{board.squares[h5_idx]}'")

    # Expected: h7 should be empty, h5 should have black pawn 'p', h6 should be empty
    if (
        board.squares[h7_idx] != "\u0000"
        or board.squares[h5_idx] != "p"
        or board.squares[h6_idx] != "\u0000"
    ):
        print("BUG CONFIRMED: Unexpected pawns found!")
        print(
            f"Expected h7='', h5='p', h6='', got h7='{board.squares[h7_idx]}', h5='{board.squares[h5_idx]}', h6='{board.squares[h6_idx]}'"
        )
    else:
        print("No unexpected pawns found")

    print("\n=== Checking if this matches the user's reported FEN ===")
    expected_fen = "rnbqkbnr/ppppppp1/7P/7p/4P3/8/PPPP1PPP/RNBQKBNR w KQkq h6 0 2"
    print(f"Expected FEN: {expected_fen}")
    print(f"Actual FEN:   {board.to_fen()}")
    print(f"Match: {expected_fen == board.to_fen()}")

    # Let's also check what the user's FEN looks like when parsed
    print("\n=== Parsing the user's reported FEN ===")
    test_board = Board()
    test_board.load_fen(expected_fen)
    print(f"Parsed FEN: {test_board.to_fen()}")

    # Check the problematic squares in the parsed FEN
    print(f"Parsed - h5 (index 55): '{test_board.squares[55]}'")
    print(f"Parsed - h6 (index 39): '{test_board.squares[39]}'")
    print(f"Parsed - h7 (index 23): '{test_board.squares[23]}'")

    # Check if the parsed FEN has the same issue
    if test_board.squares[55] != "p" or test_board.squares[39] != "\u0000":
        print("USER'S FEN ALSO HAS THE BUG!")
        print(f"User's FEN shows h5='{test_board.squares[55]}', h6='{test_board.squares[39]}'")
    else:
        print("User's FEN is actually correct")


if __name__ == "__main__":
    debug_bug()
