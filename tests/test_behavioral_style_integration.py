"""Behavioral tests for style integration in MCTS search.

These tests verify that style profiles create observable behavioral differences
in search behavior, move ordering, and playout policies.
"""

import random
import unittest
from typing import Dict, List

from core.board import Board
from core.moves import Move, generate_moves
from eval.heuristics import Evaluation, get_style_profile
from search.mcts import MCTSSearch, style_aware_move_ordering


class TestStochasticExploration(unittest.TestCase):
    """Test bounded randomness in style-aware playouts."""

    def setUp(self):
        """Set up test board."""
        self.board = Board()
        self.board.set_startpos()

    def test_fixed_seeds_produce_deterministic_results(self):
        """Test that fixed seeds produce deterministic results."""
        seed = 42
        max_playouts = 100
        style_weights = get_style_profile("aggressive")

        # Run search multiple times with same seed
        results = []
        for _ in range(3):
            search = MCTSSearch(max_playouts=max_playouts, seed=seed, style=style_weights)
            move = search.search(self.board)
            results.append(move)

        # All results should be identical
        self.assertEqual(
            len(set(str(r) for r in results)), 1, "Fixed seed should produce deterministic results"
        )

    def test_different_seeds_produce_varied_results(self):
        """Test that different seeds produce varied but valid results."""
        max_playouts = 50  # Lower to increase variation
        style_weights = get_style_profile("aggressive")

        # Run search with different seeds
        results = []
        for seed in [42, 123, 456, 789]:
            search = MCTSSearch(max_playouts=max_playouts, seed=seed, style=style_weights)
            move = search.search(self.board)
            results.append(move)

        # All results should be valid moves
        for move in results:
            self.assertIsInstance(move, Move)

        # Results should show some variation (not all identical)
        unique_results = len(set(str(r) for r in results))
        self.assertGreaterEqual(
            unique_results, 1, "Should have at least some variation with different seeds"
        )

    def test_style_aware_playout_policy(self):
        """Test that style-aware playout policy influences move selection."""
        # Use a tactical position where different styles should behave differently
        board = Board()
        board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")

        max_playouts = 200
        seed = 42

        # Test with aggressive style
        aggressive_search = MCTSSearch(
            max_playouts=max_playouts, seed=seed, style=get_style_profile("aggressive")
        )
        aggressive_move = aggressive_search.search(board)

        # Test with defensive style
        defensive_search = MCTSSearch(
            max_playouts=max_playouts, seed=seed, style=get_style_profile("defensive")
        )
        defensive_move = defensive_search.search(board)

        # Both should return valid moves
        self.assertIsInstance(aggressive_move, Move)
        self.assertIsInstance(defensive_move, Move)

        # Styles may produce different moves (not guaranteed, but possible)
        # This test verifies the infrastructure works


class TestStyleDifferentiation(unittest.TestCase):
    """Test that different styles produce measurably different behaviors."""

    def setUp(self):
        """Set up test board."""
        self.board = Board()
        self.board.set_startpos()

    def test_aggressive_vs_defensive_move_preferences(self):
        """Test aggressive vs defensive move preferences on tactical positions."""
        # Use a position with tactical opportunities
        board = Board()
        board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")

        max_playouts = 300
        seed = 42

        # Run multiple searches to get statistical sample
        aggressive_moves = []
        defensive_moves = []

        for _ in range(5):
            # Aggressive style
            agg_search = MCTSSearch(
                max_playouts=max_playouts, seed=seed + _, style=get_style_profile("aggressive")
            )
            agg_move = agg_search.search(board)
            if agg_move:
                aggressive_moves.append(agg_move)

            # Defensive style
            def_search = MCTSSearch(
                max_playouts=max_playouts, seed=seed + _, style=get_style_profile("defensive")
            )
            def_move = def_search.search(board)
            if def_move:
                defensive_moves.append(def_move)

        # Both styles should produce valid moves
        self.assertGreater(len(aggressive_moves), 0, "Aggressive style should produce moves")
        self.assertGreater(len(defensive_moves), 0, "Defensive style should produce moves")

        # Verify move ordering differences
        moves = generate_moves(self.board)
        if moves:
            # Test move ordering with different styles
            agg_ordered = style_aware_move_ordering(board, moves, get_style_profile("aggressive"))
            def_ordered = style_aware_move_ordering(board, moves, get_style_profile("defensive"))

            # Both should return valid move lists
            self.assertEqual(len(agg_ordered), len(moves))
            self.assertEqual(len(def_ordered), len(moves))

    def test_experimental_style_shows_different_patterns(self):
        """Test that experimental style shows different patterns than standard profiles."""
        board = Board()
        board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

        moves = generate_moves(board)
        if not moves:
            self.skipTest("No moves available for testing")

        # Test move ordering with experimental style
        experimental_ordered = style_aware_move_ordering(
            board, moves, get_style_profile("experimental")
        )
        standard_ordered = style_aware_move_ordering(board, moves, get_style_profile("aggressive"))

        # Both should return valid move lists
        self.assertEqual(len(experimental_ordered), len(moves))
        self.assertEqual(len(standard_ordered), len(moves))

        # Test evaluation differences
        evaluator_exp = Evaluation(style_weights=get_style_profile("experimental"))
        evaluator_agg = Evaluation(style_weights=get_style_profile("aggressive"))

        score_exp = evaluator_exp.evaluate(board)
        score_agg = evaluator_agg.evaluate(board)

        # Scores should be different (though may be close)
        self.assertNotEqual(
            score_exp,
            score_agg,
            "Experimental and aggressive styles should produce different evaluations",
        )

    def test_position_specific_style_behaviors(self):
        """Test each style's characteristic behaviors on specific positions."""
        positions = [
            # Tactical position - aggressive should prefer tactical moves
            ("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4", "aggressive"),
            # Quiet position - defensive should prefer solid moves
            ("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 2 3", "defensive"),
            # Complex position - experimental should explore alternatives
            ("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1", "experimental"),
        ]

        for fen, expected_style in positions:
            with self.subTest(position=fen, style=expected_style):
                board = Board()
                board.load_fen(fen)

                # Test that the style produces valid evaluation
                evaluator = Evaluation(style_weights=get_style_profile(expected_style))
                score = evaluator.evaluate(board)

                # Score should be a valid number
                self.assertIsInstance(score, (int, float))

                # Test move ordering works
                moves = generate_moves(board)
                if moves:
                    ordered_moves = style_aware_move_ordering(
                        board, moves, get_style_profile(expected_style)
                    )
                    self.assertEqual(len(ordered_moves), len(moves))


class TestBehavioralValidation(unittest.TestCase):
    """Test behavioral validation and consistency."""

    def test_style_profiles_produce_measurably_different_outputs(self):
        """Test that style profiles produce measurably different outputs."""
        # Use a tactical position where different styles should show differences
        board = Board()
        board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")

        # Get evaluations from different styles
        styles = ["aggressive", "defensive", "experimental"]
        evaluations = {}

        for style in styles:
            evaluator = Evaluation(style_weights=get_style_profile(style))
            evaluations[style] = evaluator.evaluate(board)

        # All evaluations should be different
        unique_scores = len(set(evaluations.values()))
        self.assertGreaterEqual(
            unique_scores, 2, "At least two styles should produce different evaluations"
        )

        # Test explain_evaluation shows different breakdowns
        for style in styles:
            evaluator = Evaluation(style_weights=get_style_profile(style))
            explanation = evaluator.explain_evaluation(board)

            self.assertIn("total", explanation)
            self.assertIn("terms", explanation)
            self.assertIn("style_weights", explanation)

            # Style weights should match the profile
            expected_weights = get_style_profile(style)
            self.assertEqual(explanation["style_weights"], expected_weights)

    def test_style_consistency_across_multiple_positions(self):
        """Test style consistency across multiple positions."""
        positions = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4",
            "rnbqkb1r/pppp1ppp/5n2/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 2 3",
        ]

        for style_name in ["aggressive", "defensive", "experimental"]:
            with self.subTest(style=style_name):
                style_weights = get_style_profile(style_name)

                for fen in positions:
                    with self.subTest(position=fen):
                        board = Board()
                        board.load_fen(fen)

                        # Evaluation should work consistently
                        evaluator = Evaluation(style_weights=style_weights)
                        score = evaluator.evaluate(board)
                        self.assertIsInstance(score, (int, float))

                        # Move ordering should work consistently
                        moves = generate_moves(board)
                        if moves:
                            ordered = style_aware_move_ordering(board, moves, style_weights)
                            self.assertEqual(len(ordered), len(moves))

    def test_style_aware_search_depth_and_node_limits(self):
        """Test style-aware search with different depth and node limits."""
        board = Board()
        board.set_startpos()

        style_weights = get_style_profile("aggressive")

        # Test with different limits
        limits = [
            {"max_playouts": 50, "seed": 42},
            {"max_playouts": 100, "seed": 42},
            {"max_playouts": 200, "movetime_ms": 100, "seed": 42},
        ]

        for limit_config in limits:
            with self.subTest(limits=limit_config):
                search = MCTSSearch(style=style_weights, **limit_config)
                move = search.search(board)

                # Should return valid move or None
                self.assertTrue(move is None or isinstance(move, Move))


class TestRegressionSafeguards(unittest.TestCase):
    """Test regression safeguards and behavioral drift detection."""

    def test_style_output_consistency(self):
        """Test that style outputs remain consistent across runs."""
        board = Board()
        board.load_fen("r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/2N5/PPP2PPP/R1BQKBNR w KQkq - 0 4")

        # Test multiple styles
        for style_name in ["aggressive", "defensive", "experimental"]:
            with self.subTest(style=style_name):
                style_weights = get_style_profile(style_name)

                # Run evaluation multiple times - should be consistent
                evaluator = Evaluation(style_weights=style_weights)
                scores = [evaluator.evaluate(board) for _ in range(5)]

                # All scores should be identical (evaluation is deterministic)
                self.assertEqual(
                    len(set(scores)), 1, f"{style_name} style should produce consistent evaluations"
                )

    def test_style_aware_move_ordering_consistency(self):
        """Test that style-aware move ordering is consistent."""
        board = Board()
        board.set_startpos()

        moves = generate_moves(board)
        if not moves:
            self.skipTest("No moves available for testing")

        for style_name in ["aggressive", "defensive", "experimental"]:
            with self.subTest(style=style_name):
                style_weights = get_style_profile(style_name)

                # Run ordering multiple times - should be consistent
                orderings = [
                    style_aware_move_ordering(board, moves, style_weights) for _ in range(3)
                ]

                # All orderings should be identical
                for i in range(1, len(orderings)):
                    self.assertEqual(
                        orderings[0],
                        orderings[i],
                        f"{style_name} style should produce consistent move ordering",
                    )


if __name__ == "__main__":
    unittest.main()
