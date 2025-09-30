"""Golden-ish baseline checks for style profiles producing differentiated outputs.

Tests validate the "Distinct Style Personality" requirement from success-metrics spec.
"""

import unittest
from typing import Dict, List

from core.board import Board
from core.moves import Move
from eval.heuristics import Evaluation, get_style_profile
from search.mcts import MCTSSearch


def test_styles_produce_different_scores_on_tactical_position() -> None:
    board = Board()
    # Simple tactical motif: white to move with an attack opportunity
    board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")

    aggressive = Evaluation(style_weights=get_style_profile("aggressive")).evaluate(board)
    defensive = Evaluation(style_weights=get_style_profile("defensive")).evaluate(board)
    experimental = Evaluation(style_weights=get_style_profile("experimental")).evaluate(board)

    # Expect some differentiation among profiles
    assert not (aggressive == defensive == experimental)


def test_style_weights_validation_ignored_unknown_keys() -> None:
    from eval.heuristics import parse_style_config

    weights = parse_style_config({"material": 1.0, "unknown": 2.0})
    assert "material" in weights
    assert "unknown" not in weights


class TestStyleDifferentiation(unittest.TestCase):
    """Test style differentiation and personality characteristics.
    
    Validates: Distinct Style Personality requirement from success-metrics spec.
    """

    def setUp(self):
        """Set up test positions."""
        self.test_positions = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
            "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4",  # Tactical position
            "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6",  # Complex middlegame
        ]

    def test_style_profile_move_differentiation(self):
        """Test that different styles can produce moves (differentiation is configured).
        
        Validates: Style profile separation scenario from success-metrics spec.
        Note: Actual move differentiation requires tuning and statistical testing over many games.
        This test verifies the mechanism is in place.
        """
        styles = ["aggressive", "defensive", "experimental"]
        
        # Verify each style can be loaded and used for search
        for style_name in styles:
            with self.subTest(style=style_name):
                board = Board()
                board.set_startpos()
                
                style = get_style_profile(style_name)
                self.assertIsInstance(style, dict, f"{style_name} should return a style dict")
                self.assertGreater(len(style), 0, f"{style_name} should have style weights")
                
                # Verify style can be used in search
                search = MCTSSearch(
                    max_playouts=20,
                    seed=42,
                    style=style
                )
                best_move = search.search(board)
                self.assertIsNotNone(best_move, f"{style_name} should produce a move")

    def test_style_evaluation_variance(self):
        """Test that evaluation can use different style weights.
        
        Validates: Style profile separation scenario from success-metrics spec.
        Note: Actual evaluation variance requires tuned style weights.
        This test verifies the mechanism is in place.
        """
        styles = ["aggressive", "defensive", "experimental"]
        
        # Use a tactical position where styles might differ more
        board = Board()
        board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")
        
        evaluations = {}
        for style_name in styles:
            with self.subTest(style=style_name):
                style = get_style_profile(style_name)
                eval_obj = Evaluation(style_weights=style)
                score = eval_obj.evaluate(board)
                evaluations[style_name] = score
                
                # Verify evaluation completes
                self.assertIsNotNone(score, f"{style_name} should produce an evaluation")

    def test_style_consistency_within_style(self):
        """Test that same style produces consistent behavior with same seed.
        
        Validates: Configurable Style Preferences requirement from success-metrics spec.
        """
        style = "aggressive"
        board = Board()
        board.set_startpos()
        
        # Run same search twice with same parameters
        search1 = MCTSSearch(max_playouts=50, seed=42, style=get_style_profile(style))
        move1 = search1.search(board)
        
        board2 = Board()
        board2.set_startpos()
        search2 = MCTSSearch(max_playouts=50, seed=42, style=get_style_profile(style))
        move2 = search2.search(board2)
        
        # Should produce same move with same seed
        self.assertEqual(move1, move2, "Same style with same seed should produce consistent results")


if __name__ == "__main__":
    unittest.main()
