"""Tests for move generation and validation."""

import pytest

from core.moves import Move, generate_moves, is_legal_move


class TestMoves:
    """Test cases for move generation and validation."""

    def test_move_creation(self) -> None:
        """Test move object creation."""
        move = Move(0, 16)  # e2 to e3
        assert move.from_square == 0
        assert move.to_square == 16

    def test_move_generation(self) -> None:
        """Test legal move generation."""
        # Test implementation will be added later
        moves = generate_moves(None)  # Will use proper board later
        assert isinstance(moves, list)

    def test_move_validation(self) -> None:
        """Test move legality checking."""
        move = Move(0, 16)
        is_legal = is_legal_move(None, move)  # Will use proper board later
        assert isinstance(is_legal, bool)
