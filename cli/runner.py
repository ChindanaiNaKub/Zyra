"""CLI runner for chess engine testing and analysis.

This module provides command-line utilities for testing the engine,
running analysis, and interactive gameplay.
"""

import argparse
from typing import Dict, List, Optional

from core.board import Board
from core.moves import generate_moves, make_move, parse_uci_move, perft, unmake_move
from eval.heuristics import create_evaluator, parse_style_config
from interfaces.uci import UCIEngine
from search.mcts import MCTSSearch, heuristic_move_ordering


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


def run_play(
    fen: Optional[str], movetime: Optional[int], nodes: Optional[int], max_plies: int
) -> None:
    """Play a self-play game for a limited number of plies.

    - Uses MCTS when movetime or nodes is provided; otherwise plays random legal moves.
    - Prints each move in UCI along with side to move and a simple board snapshot at the end.
    """
    board = Board()
    if fen:
        board.load_fen(fen)
    else:
        board.set_startpos()

    engine = UCIEngine()
    engine.position = board

    played: List[str] = []
    for ply in range(max_plies):
        legal = generate_moves(engine.position)
        if not legal:
            break
        if movetime is None and nodes is None:
            # Fallback: random move via UCIEngine's go handler without params
            best = engine._handle_go_command([])
        else:
            args: List[str] = []
            if movetime is not None:
                args += ["movetime", str(movetime)]
            if nodes is not None:
                args += ["nodes", str(nodes)]
            best = engine._handle_go_command(args)
        if not best or not best.startswith("bestmove "):
            break
        uci = best.split()[1]
        # Apply
        try:
            mv = parse_uci_move(engine.position, uci)
            legal = generate_moves(engine.position)
            ok = False
            for lm in legal:
                if (
                    lm.from_square == mv.from_square
                    and lm.to_square == mv.to_square
                    and lm.promotion == mv.promotion
                ):
                    make_move(engine.position, mv)
                    ok = True
                    break
            if not ok:
                print(f"info string Skipping illegal selected move {uci}")
                break
            played.append(uci)
        except Exception as ex:
            print(f"info string Failed to apply move {uci}: {ex}")
            break

    print(f"Played plies: {len(played)}")
    if played:
        print("Moves:", " ".join(played))
    print("Final position:")
    print(_ascii_board(engine.position))


def run_profile_style(fen: str, profile: Optional[str]) -> None:
    """Print style weight impacts for a given position and profile name.

    Shows evaluation term values, applied weights, and total.
    """
    board = Board()
    board.load_fen(fen)
    weights: Dict[str, float] = parse_style_config(profile) if profile else {}
    evaluator = create_evaluator(weights)
    result = evaluator.explain_evaluation(board)
    print("Style profile:", profile or "<default>")
    print("Terms:")
    for k, v in result["terms"].items():
        w = result["style_weights"].get(k, 1.0)
        print(f"  {k}: {v:.2f} x {w:.2f} = {v * w:.2f}")
    print(f"Total (cp): {result['total']:.2f}")


def run_stability(
    games: int,
    max_plies: int,
    movetime: Optional[int],
    nodes: Optional[int],
    fen: Optional[str],
    verbose: bool,
) -> None:
    """Run multiple short self-play games to check stability and crash resistance.

    Prints a summary of completed games. Any exception within a game loop will
    be surfaced as output and abort further games.
    """
    completed = 0
    for g in range(1, games + 1):
        if verbose:
            print(f"info string Starting stability game {g}/{games}")
        try:
            run_play(fen, movetime, nodes, max_plies)
            completed += 1
        except Exception as ex:
            print(f"info string Stability run aborted on game {g}: {ex}")
            break
    print(f"Stability: completed {completed}/{games} games")


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

    # Play command
    play_parser = subparsers.add_parser("play", help="Self-play a short game")
    play_parser.add_argument("--fen", help="Starting position in FEN (default startpos)")
    play_parser.add_argument("--movetime", type=int, help="Move time in ms (per move)")
    play_parser.add_argument("--nodes", type=int, help="Max nodes per move")
    play_parser.add_argument(
        "--max-plies", type=int, default=10, help="Maximum number of plies to play"
    )

    # Profile style command
    ps_parser = subparsers.add_parser("profile-style", help="Report style weight impacts")
    ps_parser.add_argument("fen", help="Position in FEN notation")
    ps_parser.add_argument(
        "--profile", help="Style profile name (aggressive, defensive, experimental)"
    )

    # Stability command
    stab_parser = subparsers.add_parser(
        "stability", help="Run multiple short self-play games to check stability"
    )
    stab_parser.add_argument("--games", type=int, default=10, help="Number of games to run")
    stab_parser.add_argument(
        "--max-plies", type=int, default=40, help="Maximum plies per game (short runs recommended)"
    )
    stab_parser.add_argument("--movetime", type=int, help="Move time in ms (per move)")
    stab_parser.add_argument("--nodes", type=int, help="Max nodes per move")
    stab_parser.add_argument("--fen", help="Starting FEN; default startpos")
    stab_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.command == "perft":
        run_perft_test(args.depth, args.fen)
    elif args.command == "analyze":
        run_analysis(args.fen)
    elif args.command == "apply":
        run_apply_moves(args.moves, args.fen)
    elif args.command == "play":
        run_play(
            args.fen, getattr(args, "movetime", None), getattr(args, "nodes", None), args.max_plies
        )
    elif args.command == "profile-style":
        run_profile_style(args.fen, getattr(args, "profile", None))
    elif args.command == "stability":
        run_stability(
            games=getattr(args, "games", 10),
            max_plies=getattr(args, "max_plies", 40),
            movetime=getattr(args, "movetime", None),
            nodes=getattr(args, "nodes", None),
            fen=getattr(args, "fen", None),
            verbose=getattr(args, "verbose", False),
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
