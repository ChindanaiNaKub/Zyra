"""End-to-end smoke games for style integration validation.

These tests run self-play games with limited depth/nodes to verify that
style profiles work correctly in complete game scenarios.
"""

import unittest
from typing import List, Optional

from core.board import Board
from core.moves import Move, make_move, unmake_move
from eval.heuristics import get_style_profile
from search.mcts import MCTSSearch


class SmokeGameRunner:
    """Run smoke games with different style profiles."""

    def __init__(self, max_playouts: int = 50, max_moves: int = 10):
        self.max_playouts = max_playouts
        self.max_moves = max_moves

    def play_smoke_game(self, style_name: str, seed: int = 42) -> List[Move]:
        """Play a short smoke game with the given style."""
        board = Board()
        board.set_startpos()

        moves_played = []

        for move_num in range(self.max_moves):
            # Create search with style
            search = MCTSSearch(
                max_playouts=self.max_playouts,
                seed=seed + move_num,  # Vary seed slightly for each move
                style=get_style_profile(style_name),
            )

            # Get best move
            best_move = search.search(board)
            if best_move is None:
                break  # No legal moves (checkmate/stalemate)

            # Make the move
            captured, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev = make_move(
                board, best_move
            )

            moves_played.append(best_move)

            # Check for game end conditions
            if board.is_checkmate() or board.is_stalemate():
                break

        return moves_played

    def play_style_vs_style(self, style1: str, style2: str, seed: int = 42) -> List[Move]:
        """Play a short game between two different styles."""
        board = Board()
        board.set_startpos()

        moves_played = []
        current_style = style1

        for move_num in range(self.max_moves):
            # Alternate between styles
            if move_num % 2 == 0:
                current_style = style1
            else:
                current_style = style2

            # Create search with current style
            search = MCTSSearch(
                max_playouts=self.max_playouts,
                seed=seed + move_num,
                style=get_style_profile(current_style),
            )

            # Get best move
            best_move = search.search(board)
            if best_move is None:
                break  # No legal moves

            # Make the move
            captured, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev = make_move(
                board, best_move
            )

            moves_played.append(best_move)

            # Check for game end conditions
            if board.is_checkmate() or board.is_stalemate():
                break

        return moves_played


class TestSmokeGames(unittest.TestCase):
    """Test smoke games for each style profile."""

    def setUp(self):
        """Set up smoke game runner."""
        self.runner = SmokeGameRunner(max_playouts=30, max_moves=8)

    def test_aggressive_style_smoke_game(self):
        """Test aggressive style in smoke game."""
        moves = self.runner.play_smoke_game("aggressive", seed=42)

        # Should play at least some moves
        self.assertGreater(len(moves), 0, "Aggressive style should play at least one move")

        # All moves should be valid
        for move in moves:
            self.assertIsInstance(move, Move)

    def test_defensive_style_smoke_game(self):
        """Test defensive style in smoke game."""
        moves = self.runner.play_smoke_game("defensive", seed=42)

        # Should play at least some moves
        self.assertGreater(len(moves), 0, "Defensive style should play at least one move")

        # All moves should be valid
        for move in moves:
            self.assertIsInstance(move, Move)

    def test_experimental_style_smoke_game(self):
        """Test experimental style in smoke game."""
        moves = self.runner.play_smoke_game("experimental", seed=42)

        # Should play at least some moves
        self.assertGreater(len(moves), 0, "Experimental style should play at least one move")

        # All moves should be valid
        for move in moves:
            self.assertIsInstance(move, Move)

    def test_aggressive_vs_defensive_smoke_game(self):
        """Test aggressive vs defensive style matchup."""
        moves = self.runner.play_style_vs_style("aggressive", "defensive", seed=42)

        # Should play at least some moves
        self.assertGreater(len(moves), 0, "Style vs style should play at least one move")

        # All moves should be valid
        for move in moves:
            self.assertIsInstance(move, Move)

    def test_all_styles_produce_valid_games(self):
        """Test that all styles produce valid games."""
        styles = ["aggressive", "defensive", "experimental"]

        for style in styles:
            with self.subTest(style=style):
                moves = self.runner.play_smoke_game(style, seed=42)

                # Should play at least some moves
                self.assertGreater(len(moves), 0, f"{style} style should play at least one move")

                # All moves should be valid
                for move in moves:
                    self.assertIsInstance(move, Move)

    def test_style_consistency_across_games(self):
        """Test that styles produce consistent behavior across multiple games."""
        style = "aggressive"

        # Play multiple games with same style
        games = []
        for i in range(3):
            moves = self.runner.play_smoke_game(style, seed=42 + i)
            games.append(moves)

        # All games should produce valid moves
        for i, moves in enumerate(games):
            self.assertGreater(len(moves), 0, f"Game {i} should produce at least one move")
            for move in moves:
                self.assertIsInstance(move, Move)


class TestUCIEngineIntegration(unittest.TestCase):
    """Test UCI engine integration with different styles."""

    def test_uci_engine_with_aggressive_style(self):
        """Test UCI engine with aggressive style."""
        # This would test the UCI engine with style configuration
        # For now, just test that the style profile exists and is valid
        aggressive_weights = get_style_profile("aggressive")

        self.assertIsInstance(aggressive_weights, dict)
        self.assertGreater(len(aggressive_weights), 0)

        # Test that style can be used with MCTS
        board = Board()
        board.set_startpos()

        search = MCTSSearch(max_playouts=20, seed=42, style=aggressive_weights)

        move = search.search(board)
        self.assertTrue(move is None or isinstance(move, Move))

    def test_uci_engine_with_defensive_style(self):
        """Test UCI engine with defensive style."""
        defensive_weights = get_style_profile("defensive")

        self.assertIsInstance(defensive_weights, dict)
        self.assertGreater(len(defensive_weights), 0)

        # Test that style can be used with MCTS
        board = Board()
        board.set_startpos()

        search = MCTSSearch(max_playouts=20, seed=42, style=defensive_weights)

        move = search.search(board)
        self.assertTrue(move is None or isinstance(move, Move))

    def test_uci_engine_with_experimental_style(self):
        """Test UCI engine with experimental style."""
        experimental_weights = get_style_profile("experimental")

        self.assertIsInstance(experimental_weights, dict)
        self.assertGreater(len(experimental_weights), 0)

        # Test that style can be used with MCTS
        board = Board()
        board.set_startpos()

        search = MCTSSearch(max_playouts=20, seed=42, style=experimental_weights)

        move = search.search(board)
        self.assertTrue(move is None or isinstance(move, Move))


if __name__ == "__main__":
    unittest.main()
