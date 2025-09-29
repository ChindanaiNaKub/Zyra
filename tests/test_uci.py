"""Tests for UCI protocol implementation.

These tests verify that the UCI engine responds correctly to basic commands
and can handle the minimal UCI protocol required for GUI integration.
"""

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from interfaces.uci import UCIEngine


class TestUCI:
    """Test cases for UCI protocol implementation."""

    def test_uci_command(self) -> None:
        """Test UCI command response."""
        engine = UCIEngine()
        response = engine.handle_command("uci")
        assert response == "uciok"

    def test_isready_command(self) -> None:
        """Test isready command response."""
        engine = UCIEngine()
        response = engine.handle_command("isready")
        assert response == "readyok"

    def test_ucinewgame_command(self) -> None:
        """Test ucinewgame command."""
        engine = UCIEngine()
        response = engine.handle_command("ucinewgame")
        assert response is None  # No response expected

        # Verify position is set to startpos
        assert engine.position.to_fen().startswith("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    def test_position_startpos_command(self) -> None:
        """Test position startpos command."""
        engine = UCIEngine()
        response = engine.handle_command("position startpos")
        assert response is None  # No response expected

        # Verify position is set to startpos
        assert engine.position.to_fen().startswith("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    def test_position_fen_command(self) -> None:
        """Test position fen command."""
        engine = UCIEngine()
        fen = "8/8/8/8/8/8/8/4K3 w - - 0 1"  # Lone king position
        response = engine.handle_command(f"position fen {fen}")
        assert response is None  # No response expected

        # Verify position is set correctly
        assert engine.position.to_fen() == fen

    def test_position_with_moves(self) -> None:
        """Test position command with moves."""
        engine = UCIEngine()
        response = engine.handle_command("position startpos moves e2e4")
        assert response is None  # No response expected

        # Verify move was applied (white pawn moved from e2 to e4)
        from core.board import square_to_index

        assert engine.position.squares[square_to_index("e4")] == "P"
        assert engine.position.squares[square_to_index("e2")] == "\u0000"
        assert engine.position.side_to_move == "b"  # Black to move

    def test_go_command(self) -> None:
        """Test go command returns a legal move."""
        engine = UCIEngine()
        engine.position.set_startpos()

        response = engine.handle_command("go")
        assert response is not None
        assert response.startswith("bestmove ")

        # Extract the move
        move_str = response.split()[1]
        assert len(move_str) == 4  # Should be like "e2e4"
        assert move_str[0] in "abcdefgh"
        assert move_str[1] in "12345678"
        assert move_str[2] in "abcdefgh"
        assert move_str[3] in "12345678"

    def test_go_command_no_moves(self) -> None:
        """Test go command when no legal moves available."""
        engine = UCIEngine()
        # Set up a position with no legal moves (checkmate)
        engine.position.load_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")

        response = engine.handle_command("go")
        assert response == "bestmove 0000"

    def test_quit_command(self) -> None:
        """Test quit command exits the program."""
        engine = UCIEngine()

        with pytest.raises(SystemExit):
            engine.handle_command("quit")

    def test_unknown_command(self) -> None:
        """Test unknown command returns None."""
        engine = UCIEngine()
        response = engine.handle_command("unknown_command")
        assert response is None

    def test_empty_command(self) -> None:
        """Test empty command returns None."""
        engine = UCIEngine()
        response = engine.handle_command("")
        assert response is None

    def test_whitespace_command(self) -> None:
        """Test command with only whitespace returns None."""
        engine = UCIEngine()
        response = engine.handle_command("   ")
        assert response is None

    def test_position_fen_with_moves(self) -> None:
        """Test position fen command with subsequent moves."""
        engine = UCIEngine()
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        response = engine.handle_command(f"position fen {fen} moves e2e4 e7e5")
        assert response is None

        # Verify both moves were applied
        from core.board import square_to_index

        assert engine.position.squares[square_to_index("e4")] == "P"
        assert engine.position.squares[square_to_index("e5")] == "p"
        assert engine.position.side_to_move == "w"  # White to move after both moves

    def test_position_malformed_fen(self) -> None:
        """Test position command with malformed FEN (should not crash)."""
        engine = UCIEngine()
        response = engine.handle_command("position fen invalid_fen")
        assert response is None  # Should handle gracefully

    def test_position_malformed_move(self) -> None:
        """Test position command with malformed move (should not crash)."""
        engine = UCIEngine()
        response = engine.handle_command("position startpos moves invalid_move")
        assert response is None  # Should handle gracefully

    def test_go_command_consistency(self) -> None:
        """Test that go command returns consistent move format."""
        engine = UCIEngine()
        engine.position.set_startpos()

        # Test multiple times to ensure consistency
        for _ in range(5):
            response = engine.handle_command("go")
            assert response is not None
            assert response.startswith("bestmove ")

            move_str = response.split()[1]
            assert len(move_str) == 4
            assert move_str[0] in "abcdefgh"
            assert move_str[1] in "12345678"
            assert move_str[2] in "abcdefgh"
            assert move_str[3] in "12345678"

    def test_uci_loop_integration(self) -> None:
        """Test UCI loop with simulated input."""
        engine = UCIEngine()

        # Mock input to simulate UCI protocol exchange
        test_input = ["uci", "isready", "position startpos", "go", "quit"]

        with patch("builtins.input", side_effect=test_input):
            with patch("builtins.print") as mock_print:
                with pytest.raises(SystemExit):
                    engine.run_uci_loop()

        # Verify that responses were printed
        assert mock_print.call_count >= 3  # At least uciok, readyok, and bestmove

    def test_square_conversion(self) -> None:
        """Test internal square conversion function."""
        engine = UCIEngine()

        # Test some known conversions
        assert engine._sq(0) == "a8"  # Top-left corner
        assert engine._sq(7) == "h8"  # Top-right corner
        assert engine._sq(112) == "a1"  # Bottom-left corner
        assert engine._sq(119) == "h1"  # Bottom-right corner
        assert engine._sq(68) == "e4"  # Center square

    def test_apply_uci_move_legal(self) -> None:
        """Test applying a legal UCI move."""
        engine = UCIEngine()
        engine.position.set_startpos()

        # Apply e2e4
        engine._apply_uci_move("e2e4")

        # Verify move was applied
        from core.board import square_to_index

        assert engine.position.squares[square_to_index("e4")] == "P"
        assert engine.position.squares[square_to_index("e2")] == "\u0000"

    def test_apply_uci_move_illegal(self) -> None:
        """Test applying an illegal UCI move (should be ignored)."""
        engine = UCIEngine()
        engine.position.set_startpos()

        original_fen = engine.position.to_fen()

        # Try to apply an illegal move
        engine._apply_uci_move("e2e5")  # Not a legal move from startpos

        # Verify position was not changed
        assert engine.position.to_fen() == original_fen

    def test_apply_uci_move_malformed(self) -> None:
        """Test applying a malformed UCI move (should not crash)."""
        engine = UCIEngine()
        engine.position.set_startpos()

        original_fen = engine.position.to_fen()

        # Try to apply malformed moves
        engine._apply_uci_move("invalid")
        engine._apply_uci_move("e2")
        engine._apply_uci_move("e2e4e6")

        # Verify position was not changed
        assert engine.position.to_fen() == original_fen
