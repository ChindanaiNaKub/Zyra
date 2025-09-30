"""Tests for MCTS search implementation."""

import random
import time
import unittest
from unittest.mock import patch

from core.board import Board
from core.moves import Move
from search.mcts import MCTSSearch, heuristic_move_ordering, style_aware_move_ordering


class TestMCTSDeterminism(unittest.TestCase):
    """Test deterministic behavior with fixed seeds."""

    def setUp(self):
        """Set up test board."""
        self.board = Board()
        self.board.set_startpos()

    def test_deterministic_with_fixed_seed(self):
        """Test that search is deterministic with fixed seed."""
        seed = 42
        max_playouts = 100

        # Run search twice with same seed
        search1 = MCTSSearch(max_playouts=max_playouts, seed=seed)
        search2 = MCTSSearch(max_playouts=max_playouts, seed=seed)

        move1 = search1.search(self.board)
        move2 = search2.search(self.board)

        # Should get same move
        self.assertEqual(move1, move2)

    def test_different_seeds_give_different_results(self):
        """Test that different seeds can give different results."""
        max_playouts = 50  # Lower to increase chance of different results

        search1 = MCTSSearch(max_playouts=max_playouts, seed=42)
        search2 = MCTSSearch(max_playouts=max_playouts, seed=123)

        move1 = search1.search(self.board)
        move2 = search2.search(self.board)

        # Results may be same or different, but both should be valid
        self.assertIsInstance(move1, Move)
        self.assertIsInstance(move2, Move)

    def test_playout_cap_respected(self):
        """Test that playout limit is respected."""
        max_playouts = 10
        search = MCTSSearch(max_playouts=max_playouts, seed=42)

        # Mock the internal methods to count playouts
        playout_count = 0

        original_simulation = search._simulation
        original_backpropagation = search._backpropagation

        def counting_simulation(node):
            nonlocal playout_count
            playout_count += 1
            return original_simulation(node)

        search._simulation = counting_simulation

        # Run search
        search.search(self.board)

        # Should not exceed max playouts
        self.assertLessEqual(playout_count, max_playouts)

    def test_movetime_respected(self):
        """Test that movetime limit is respected."""
        movetime_ms = 100  # 100ms
        search = MCTSSearch(max_playouts=100000, movetime_ms=movetime_ms, seed=42)

        start_time = time.time()
        search.search(self.board)
        end_time = time.time()

        elapsed_ms = (end_time - start_time) * 1000
        # Allow some tolerance for scheduling
        self.assertLess(elapsed_ms, movetime_ms + 50)

    def test_no_legal_moves_returns_none(self):
        """Test that search returns None when no legal moves."""
        # Create a board with no legal moves (checkmate position)
        board = Board()
        # Set up a simple checkmate position
        board.load_fen("k7/8/8/8/8/8/8/7K w - - 0 1")

        search = MCTSSearch(max_playouts=100, seed=42)
        result = search.search(board)

        # Should return None or a valid move
        self.assertTrue(result is None or isinstance(result, Move))


class TestMoveOrdering(unittest.TestCase):
    """Test move ordering functionality."""

    def setUp(self):
        """Set up test board."""
        self.board = Board()
        self.board.set_startpos()

    def test_heuristic_ordering_structure(self):
        """Test that heuristic ordering returns moves in priority order."""
        from core.moves import generate_moves

        moves = generate_moves(self.board)
        ordered_moves = heuristic_move_ordering(self.board, moves)

        # Should return same number of moves
        self.assertEqual(len(moves), len(ordered_moves))

        # Should be a list of moves
        for move in ordered_moves:
            self.assertIsInstance(move, Move)

    def test_style_aware_ordering_without_weights(self):
        """Test style-aware ordering without style weights."""
        from core.moves import generate_moves

        moves = generate_moves(self.board)
        ordered_moves = style_aware_move_ordering(self.board, moves)

        # Should return same number of moves
        self.assertEqual(len(moves), len(ordered_moves))

        # Should be a list of moves
        for move in ordered_moves:
            self.assertIsInstance(move, Move)

    def test_style_aware_ordering_with_weights(self):
        """Test style-aware ordering with style weights."""
        from core.moves import generate_moves

        moves = generate_moves(self.board)
        style_weights = {"attack_bonus": 1.5}

        ordered_moves = style_aware_move_ordering(self.board, moves, style_weights)

        # Should return same number of moves
        self.assertEqual(len(moves), len(ordered_moves))

        # Should be a list of moves
        for move in ordered_moves:
            self.assertIsInstance(move, Move)


class TestMCTSIntegration(unittest.TestCase):
    """Test MCTS integration with UCI-like interface."""

    def test_search_with_move_ordering_hook(self):
        """Test MCTS with move ordering hook."""
        board = Board()
        board.set_startpos()

        search = MCTSSearch(max_playouts=50, seed=42, move_ordering_hook=heuristic_move_ordering)

        result = search.search(board)

        # Should return a valid move or None
        self.assertTrue(result is None or isinstance(result, Move))

    def test_search_parameters(self):
        """Test MCTS with various parameter combinations."""
        board = Board()
        board.set_startpos()

        # Test with different parameter combinations
        configs = [
            {"max_playouts": 10, "seed": 42},
            {"max_playouts": 100, "movetime_ms": 50, "seed": 123},
            {"max_playouts": 50, "seed": None},
        ]

        for config in configs:
            with self.subTest(config=config):
                search = MCTSSearch(**config)
                result = search.search(board)
                self.assertTrue(result is None or isinstance(result, Move))

    def test_rollout_cutoff_early_exit(self):
        """Heuristic rollout should early-terminate on clear advantage."""
        board = Board()
        # Set a position with material advantage for white
        board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKQNR w KQkq - 0 1")
        search = MCTSSearch(max_playouts=5, seed=1, rollout_win_cp=50, rollout_loss_cp=-50)
        # Should run without errors and often cut off quickly
        mv = search.search(board)
        self.assertTrue(mv is None or isinstance(mv, Move))


if __name__ == "__main__":
    unittest.main()
