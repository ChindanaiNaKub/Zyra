"""CLI runner for chess engine testing and analysis.

This module provides command-line utilities for testing the engine,
running analysis, and interactive gameplay.
"""

import argparse
from typing import List, Optional

from core.board import Board
from core.moves import generate_moves, make_move, parse_uci_move, perft, unmake_move


def run_perft_test(depth: int, fen: Optional[str] = None) -> None:
    """Run perft test for move generation validation."""
    print(f"Running perft test to depth {depth}")
    board = Board()
    if fen:
        board.load_fen(fen)
    else:
        board.set_startpos()
    count = perft(board, depth)
    print(f"Perft({depth}) = {count}")


def run_analysis(position: str) -> None:
    """Run position analysis with a simple board dump and legal moves."""
    board = Board()
    board.load_fen(position)
    print("Position:")
    print(_ascii_board(board))
    moves = generate_moves(board)
    print(f"Legal moves: {len(moves)}")


def _ascii_board(board: Board) -> str:
    lines: List[str] = []
    for rank_idx_from_top in range(8):
        line: List[str] = []
        for file_idx in range(8):
            idx = (rank_idx_from_top << 4) | file_idx
            piece = board.squares[idx]
            line.append(piece if piece != "\u0000" else ".")
        lines.append(" ".join(line))
    # Add a simple footer with side to move
    lines.append(f"STM: {board.side_to_move}")
    return "\n".join(lines)


def run_apply_moves(moves: List[str], fen: Optional[str]) -> None:
    """Apply a sequence of UCI moves to a position and print the board."""
    board = Board()
    if fen:
        board.load_fen(fen)
    else:
        board.set_startpos()
    for u in moves:
        try:
            mv = parse_uci_move(board, u)
            # Apply only if legal
            legal = generate_moves(board)
            ok = False
            for lm in legal:
                if (
                    lm.from_square == mv.from_square
                    and lm.to_square == mv.to_square
                    and lm.promotion == mv.promotion
                ):
                    make_move(board, mv)
                    ok = True
                    break
            if not ok:
                print(f"Ignoring illegal move: {u}")
        except Exception as ex:
            print(f"Skipping malformed move '{u}': {ex}")
    print(_ascii_board(board))


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Zyra Chess Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Perft command
    perft_parser = subparsers.add_parser("perft", help="Run perft test")
    perft_parser.add_argument("depth", type=int, help="Search depth")
    perft_parser.add_argument("--fen", help="Starting position in FEN")

    # Analysis command
    analysis_parser = subparsers.add_parser("analyze", help="Analyze position")
    analysis_parser.add_argument("fen", help="Position in FEN notation")

    # Apply moves command
    apply_parser = subparsers.add_parser("apply", help="Apply UCI moves and print board")
    apply_parser.add_argument("moves", nargs="+", help="Sequence of UCI moves, e.g., e2e4 e7e5")
    apply_parser.add_argument("--fen", help="Starting position in FEN (default startpos)")

    args = parser.parse_args()

    if args.command == "perft":
        run_perft_test(args.depth, args.fen)
    elif args.command == "analyze":
        run_analysis(args.fen)
    elif args.command == "apply":
        run_apply_moves(args.moves, args.fen)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
