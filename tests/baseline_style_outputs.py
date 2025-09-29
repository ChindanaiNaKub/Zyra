"""Style output snapshots for regression testing.

This module generates and validates golden baseline files for style profile outputs
to enable automated detection of behavioral drift.
"""

import json
import os
from typing import Any, Dict, List

from core.board import Board
from core.moves import generate_moves
from eval.heuristics import Evaluation, get_style_profile
from search.mcts import MCTSSearch, style_aware_move_ordering


class StyleOutputSnapshots:
    """Generate and validate style output snapshots for regression testing."""

    def __init__(self, baseline_dir: str = "tests/baselines"):
        self.baseline_dir = baseline_dir
        os.makedirs(baseline_dir, exist_ok=True)

    def generate_baseline(
        self, style_name: str, positions: List[str], max_playouts: int = 100, seed: int = 42
    ) -> Dict[str, Any]:
        """Generate baseline outputs for a style profile."""
        baseline = {
            "style": style_name,
            "style_weights": get_style_profile(style_name),
            "max_playouts": max_playouts,
            "seed": seed,
            "positions": {},
        }

        evaluator = Evaluation(style_weights=get_style_profile(style_name))

        for i, fen in enumerate(positions):
            board = Board()
            board.load_fen(fen)

            # Generate evaluation baseline
            evaluation = evaluator.evaluate(board)
            explanation = evaluator.explain_evaluation(board)

            # Generate move ordering baseline
            moves = generate_moves(board)
            if moves:
                ordered_moves = style_aware_move_ordering(
                    board, moves, get_style_profile(style_name)
                )
                move_ordering = [str(move) for move in ordered_moves[:5]]  # Top 5 moves
            else:
                move_ordering = []

            # Generate MCTS search baseline (limited for consistency)
            search = MCTSSearch(
                max_playouts=max_playouts, seed=seed, style=get_style_profile(style_name)
            )
            best_move = search.search(board)

            baseline["positions"][fen] = {
                "evaluation": evaluation,
                "explanation": explanation,
                "move_ordering": move_ordering,
                "best_move": str(best_move) if best_move else None,
            }

        return baseline

    def save_baseline(self, style_name: str, baseline: Dict[str, Any]) -> str:
        """Save baseline to file."""
        filename = f"{style_name}_baseline.json"
        filepath = os.path.join(self.baseline_dir, filename)

        with open(filepath, "w") as f:
            json.dump(baseline, f, indent=2)

        return filepath

    def load_baseline(self, style_name: str) -> Dict[str, Any]:
        """Load baseline from file."""
        filename = f"{style_name}_baseline.json"
        filepath = os.path.join(self.baseline_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Baseline file not found: {filepath}")

        with open(filepath, "r") as f:
            return json.load(f)

    def validate_against_baseline(
        self, style_name: str, positions: List[str] = None
    ) -> Dict[str, Any]:
        """Validate current outputs against saved baseline."""
        try:
            baseline = self.load_baseline(style_name)
        except FileNotFoundError:
            return {"error": f"No baseline found for style: {style_name}"}

        # Use baseline positions if none provided
        if positions is None:
            positions = list(baseline["positions"].keys())

        validation_results = {
            "style": style_name,
            "matches": 0,
            "mismatches": 0,
            "errors": [],
            "details": {},
        }

        evaluator = Evaluation(style_weights=get_style_profile(style_name))

        for fen in positions:
            if fen not in baseline["positions"]:
                validation_results["errors"].append(f"Position not in baseline: {fen}")
                continue

            board = Board()
            board.load_fen(fen)

            try:
                # Validate evaluation
                current_eval = evaluator.evaluate(board)
                baseline_eval = baseline["positions"][fen]["evaluation"]

                # Allow small floating point differences
                eval_match = abs(current_eval - baseline_eval) < 0.01

                # Validate move ordering (top 3 moves)
                moves = generate_moves(board)
                if moves:
                    current_ordered = style_aware_move_ordering(
                        board, moves, get_style_profile(style_name)
                    )
                    current_top3 = [str(move) for move in current_ordered[:3]]
                    baseline_top3 = baseline["positions"][fen]["move_ordering"][:3]

                    ordering_match = current_top3 == baseline_top3
                else:
                    ordering_match = True

                # Validate MCTS search (with same parameters)
                search = MCTSSearch(
                    max_playouts=baseline["max_playouts"],
                    seed=baseline["seed"],
                    style=get_style_profile(style_name),
                )
                current_best = search.search(board)
                current_best_str = str(current_best) if current_best else None
                baseline_best_str = baseline["positions"][fen]["best_move"]

                best_move_match = current_best_str == baseline_best_str

                # Overall match for this position
                position_match = eval_match and ordering_match and best_move_match

                if position_match:
                    validation_results["matches"] += 1
                else:
                    validation_results["mismatches"] += 1

                validation_results["details"][fen] = {
                    "evaluation_match": eval_match,
                    "ordering_match": ordering_match,
                    "best_move_match": best_move_match,
                    "overall_match": position_match,
                    "current_eval": current_eval,
                    "baseline_eval": baseline_eval,
                    "current_best": current_best_str,
                    "baseline_best": baseline_best_str,
                }

            except Exception as e:
                validation_results["errors"].append(f"Error validating {fen}: {str(e)}")

        return validation_results

    def generate_all_baselines(self) -> Dict[str, str]:
        """Generate baselines for all predefined style profiles."""
        # Standard test positions
        test_positions = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
            "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4",  # Tactical
            "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 2 3",  # Quiet
            "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",  # Complex
        ]

        styles = ["aggressive", "defensive", "experimental"]
        generated_files = {}

        for style in styles:
            print(f"Generating baseline for {style} style...")
            baseline = self.generate_baseline(style, test_positions)
            filepath = self.save_baseline(style, baseline)
            generated_files[style] = filepath
            print(f"Saved baseline to: {filepath}")

        return generated_files


def main():
    """Generate all style output baselines."""
    snapshots = StyleOutputSnapshots()

    print("Generating style output baselines for regression testing...")
    generated_files = snapshots.generate_all_baselines()

    print(f"\nGenerated {len(generated_files)} baseline files:")
    for style, filepath in generated_files.items():
        print(f"  {style}: {filepath}")

    print("\nTo validate against baselines, run:")
    print(
        "  python -c \"from tests.baseline_style_outputs import StyleOutputSnapshots; StyleOutputSnapshots().validate_against_baseline('aggressive')\""
    )


if __name__ == "__main__":
    main()
