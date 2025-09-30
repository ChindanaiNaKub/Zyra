"""CLI runner for chess engine testing and analysis.

This module provides command-line utilities for testing the engine,
running analysis, and interactive gameplay.
"""

import argparse
import datetime
import random
from typing import Dict, List, Optional, Tuple

from core.board import Board
from core.moves import generate_moves, make_move, parse_uci_move, perft, unmake_move
from eval.heuristics import create_evaluator, parse_style_config
from interfaces.uci import UCIEngine
from performance.metrics import create_run_metadata
from search.mcts import MCTSSearch, heuristic_move_ordering


def print_run_metadata(seed: Optional[int], style_profile: Optional[str] = None) -> None:
    """Print reproducibility metadata block at startup."""
    metadata = create_run_metadata(seed=seed, style_profile=style_profile)
    print("=== Run Metadata ===")
    print(metadata.to_json())
    print("===================")


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


def run_analysis(
    position: str,
    export_pgn: Optional[str] = None,
    seed: Optional[int] = None,
    style: Optional[str] = None,
) -> None:
    """Run position analysis with a simple board dump and legal moves.

    Optionally export to PGN if export_pgn path is provided.
    """
    board = Board()
    board.load_fen(position)
    print("Position:")
    print(_ascii_board(board))
    moves = generate_moves(board)
    print(f"Legal moves: {len(moves)}")

    # If PGN export requested, analyze position and export
    if export_pgn:
        weights = parse_style_config(style) if style else {}
        evaluator = create_evaluator(weights)

        # Analyze current position
        eval_result = evaluator.explain_evaluation(board)
        print(f"\nEvaluation: {eval_result['total']:.2f}cp")

        # For analysis mode, create a single-move "game" with current position eval
        moves_with_eval = []
        # Export just the position evaluation
        export_game_pgn(
            moves_with_eval,
            export_pgn,
            seed=seed,
            style_profile=style,
            starting_fen=position,
        )


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


def _move_to_san(board: Board, move) -> str:
    """Convert a move to SAN (Standard Algebraic Notation) - simplified version."""
    # This is a simplified SAN converter for basic moves
    from_file = move.from_square & 0x7
    from_rank = move.from_square >> 4
    to_file = move.to_square & 0x7
    to_rank = move.to_square >> 4

    piece = board.squares[move.from_square]
    target = board.squares[move.to_square]

    san = ""

    # Piece notation (skip for pawns)
    if piece.lower() != "p":
        san += piece.upper()

    # Capture notation
    if target != "\u0000":
        if piece.lower() == "p":
            san += "abcdefgh"[from_file]
        san += "x"

    # Destination square
    san += f"{'abcdefgh'[to_file]}{to_rank + 1}"

    # Promotion
    if move.promotion:
        san += "=" + move.promotion.upper()

    return san


def export_game_pgn(
    moves: List[Tuple[str, Dict[str, any]]],
    output_path: str,
    seed: Optional[int] = None,
    style_profile: Optional[str] = None,
    starting_fen: Optional[str] = None,
) -> None:
    """Export a game to PGN format with evaluation annotations.

    Args:
        moves: List of (uci_move, evaluation_dict) tuples
        output_path: Path to write PGN file
        seed: Random seed for reproducibility metadata
        style_profile: Style profile name for metadata
        starting_fen: Starting position (None for standard start)
    """
    pgn_lines = []

    # PGN headers
    pgn_lines.append('[Event "Zyra Engine Analysis"]')
    pgn_lines.append(f'[Date "{datetime.datetime.now().strftime("%Y.%m.%d")}"]')
    pgn_lines.append('[White "Zyra"]')
    pgn_lines.append('[Black "Zyra"]')
    pgn_lines.append('[Result "*"]')

    # Add reproducibility metadata
    if seed is not None:
        pgn_lines.append(f'[Seed "{seed}"]')
    if style_profile is not None:
        pgn_lines.append(f'[StyleProfile "{style_profile}"]')
    if starting_fen:
        pgn_lines.append(f'[FEN "{starting_fen}"]')

    pgn_lines.append("")

    # Game moves with annotations
    move_text = []
    board = Board()
    if starting_fen:
        board.load_fen(starting_fen)
    else:
        board.set_startpos()

    for i, (uci_move, eval_dict) in enumerate(moves):
        move_num = (i // 2) + 1

        # Add move number for white's moves
        if i % 2 == 0:
            move_text.append(f"{move_num}.")

        # Parse and convert to SAN
        try:
            move = parse_uci_move(board, uci_move)
            san = _move_to_san(board, move)
            move_text.append(san)

            # Add evaluation annotation as comment
            if eval_dict:
                comment = _format_eval_comment(eval_dict)
                move_text.append(f"{{ {comment} }}")

            # Apply move to board
            make_move(board, move)
        except Exception as ex:
            # If parsing fails, just use UCI notation
            move_text.append(uci_move)
            move_text.append(f"{{ Error: {ex} }}")

    # Format moves (wrap at reasonable line length)
    current_line = ""
    for token in move_text:
        if len(current_line) + len(token) + 1 > 80:
            pgn_lines.append(current_line)
            current_line = token
        else:
            current_line += (" " + token) if current_line else token

    if current_line:
        pgn_lines.append(current_line)

    pgn_lines.append("")
    pgn_lines.append("*")

    # Write to file
    with open(output_path, "w") as f:
        f.write("\n".join(pgn_lines))

    print(f"PGN exported to: {output_path}")


def _format_eval_comment(eval_dict: Dict[str, any]) -> str:
    """Format evaluation dictionary into a concise PGN comment."""
    parts = []

    # Total score
    if "total" in eval_dict:
        parts.append(f"eval: {eval_dict['total']:.2f}cp")

    # Key terms (limit to most important)
    if "terms" in eval_dict:
        terms = eval_dict["terms"]
        key_terms = ["material", "center_control", "mobility", "king_safety", "opening_principles"]
        for term in key_terms:
            if term in terms and abs(terms[term]) > 1:  # Only show non-trivial values
                parts.append(f"{term}: {terms[term]:.1f}")

    return ", ".join(parts) if parts else "eval: N/A"


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
    fen: Optional[str],
    movetime: Optional[int],
    nodes: Optional[int],
    max_plies: int,
    export_pgn: Optional[str] = None,
    seed: Optional[int] = None,
    style: Optional[str] = None,
) -> None:
    """Play a self-play game for a limited number of plies.

    - Uses MCTS when movetime or nodes is provided; otherwise plays random legal moves.
    - Prints each move in UCI along with side to move and a simple board snapshot at the end.
    - Optionally exports game to PGN with annotations.
    """
    board = Board()
    starting_fen = fen
    if fen:
        board.load_fen(fen)
    else:
        board.set_startpos()

    engine = UCIEngine()
    engine.position = board

    # For PGN export, track moves with evaluations
    moves_with_eval: List[Tuple[str, Dict]] = []
    evaluator = None
    if export_pgn:
        weights = parse_style_config(style) if style else {}
        evaluator = create_evaluator(weights)

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

        # Capture evaluation before making the move
        eval_dict = None
        if evaluator:
            eval_dict = evaluator.explain_evaluation(engine.position)

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
            if export_pgn:
                moves_with_eval.append((uci, eval_dict))
        except Exception as ex:
            print(f"info string Failed to apply move {uci}: {ex}")
            break

    print(f"Played plies: {len(played)}")
    if played:
        print("Moves:", " ".join(played))
    print("Final position:")
    print(_ascii_board(engine.position))

    # Export PGN if requested
    if export_pgn and moves_with_eval:
        export_game_pgn(
            moves_with_eval,
            export_pgn,
            seed=seed,
            style_profile=style,
            starting_fen=starting_fen,
        )


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
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Perft command
    perft_parser = subparsers.add_parser("perft", help="Run perft test")
    perft_parser.add_argument("depth", type=int, help="Search depth")
    perft_parser.add_argument("--fen", help="Starting position in FEN")

    # Analysis command
    analysis_parser = subparsers.add_parser("analyze", help="Analyze position")
    analysis_parser.add_argument("fen", help="Position in FEN notation")
    analysis_parser.add_argument("--export-pgn", help="Export analysis to PGN file")
    analysis_parser.add_argument("--style", help="Style profile for evaluation")

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
    play_parser.add_argument("--export-pgn", help="Export game to PGN file with annotations")
    play_parser.add_argument("--style", help="Style profile for evaluation in PGN annotations")

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

    # Initialize seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print_run_metadata(args.seed)

    if args.command == "perft":
        run_perft_test(args.depth, args.fen)
    elif args.command == "analyze":
        run_analysis(
            args.fen,
            export_pgn=getattr(args, "export_pgn", None),
            seed=args.seed,
            style=getattr(args, "style", None),
        )
    elif args.command == "apply":
        run_apply_moves(args.moves, args.fen)
    elif args.command == "play":
        run_play(
            args.fen,
            getattr(args, "movetime", None),
            getattr(args, "nodes", None),
            args.max_plies,
            export_pgn=getattr(args, "export_pgn", None),
            seed=args.seed,
            style=getattr(args, "style", None),
        )
    elif args.command == "profile-style":
        profile_name = getattr(args, "profile", None)
        if args.seed is not None and profile_name:
            # Re-print with profile context
            print_run_metadata(args.seed, profile_name)
        run_profile_style(args.fen, profile_name)
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
