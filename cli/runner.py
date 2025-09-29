"""CLI runner for chess engine testing and analysis.

This module provides command-line utilities for testing the engine,
running analysis, and interactive gameplay.
"""

import argparse
from typing import Optional


def run_perft_test(depth: int, fen: Optional[str] = None) -> None:
    """Run perft test for move generation validation."""
    print(f"Running perft test to depth {depth}")
    if fen:
        print(f"Starting position: {fen}")
    # Implementation will be added later


def run_analysis(position: str) -> None:
    """Run position analysis with evaluation breakdown."""
    print(f"Analyzing position: {position}")
    # Implementation will be added later


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

    args = parser.parse_args()

    if args.command == "perft":
        run_perft_test(args.depth, args.fen)
    elif args.command == "analyze":
        run_analysis(args.fen)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
