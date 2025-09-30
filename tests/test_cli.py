"""Tests for CLI runner functionality.

These tests verify that the CLI commands work correctly and produce expected output.
"""

import subprocess
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from cli.runner import _ascii_board, run_analysis, run_apply_moves, run_perft_test
from core.board import Board


class TestCLI:
    """Test cases for CLI runner functionality."""

    def test_ascii_board_display(self) -> None:
        """Test ASCII board display function."""
        board = Board()
        board.set_startpos()

        ascii_output = _ascii_board(board)
        lines = ascii_output.split("\n")

        # Should have 9 lines (8 ranks + side to move)
        assert len(lines) == 9

        # Check that it contains expected pieces
        assert "r n b q k b n r" in lines[0]  # Black back rank (lowercase)
        assert "p p p p p p p p" in lines[1]  # Black pawns (lowercase)
        assert ". . . . . . . ." in lines[4]  # Empty ranks
        assert "P P P P P P P P" in lines[6]  # White pawns (uppercase)
        assert "R N B Q K B N R" in lines[7]  # White back rank (uppercase)
        assert "STM: w" in lines[8]  # Side to move

    def test_ascii_board_empty(self) -> None:
        """Test ASCII board display for empty position."""
        board = Board()
        board.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")

        ascii_output = _ascii_board(board)
        lines = ascii_output.split("\n")

        # All ranks should be empty
        for i in range(8):
            assert lines[i] == ". . . . . . . ."

        assert "STM: w" in lines[8]

    def test_run_perft_test_startpos(self) -> None:
        """Test perft test with starting position."""
        with patch("builtins.print") as mock_print:
            run_perft_test(1)

            # Verify output
            assert mock_print.call_count == 2
            assert "Running perft test to depth 1" in str(mock_print.call_args_list[0])
            assert "Perft(1) = 20" in str(mock_print.call_args_list[1])

    def test_run_perft_test_custom_fen(self) -> None:
        """Test perft test with custom FEN."""
        fen = "8/8/8/8/8/8/8/4K3 w - - 0 1"  # Lone king
        with patch("builtins.print") as mock_print:
            run_perft_test(1, fen)

            # Verify output
            assert mock_print.call_count == 2
            assert "Running perft test to depth 1" in str(mock_print.call_args_list[0])
            assert "Perft(1) = 5" in str(mock_print.call_args_list[1])  # King has 5 moves

    def test_run_analysis(self) -> None:
        """Test position analysis."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        with patch("builtins.print") as mock_print:
            run_analysis(fen)

            # Verify output
            assert mock_print.call_count == 3
            assert "Position:" in str(mock_print.call_args_list[0])
            assert "Legal moves: 20" in str(mock_print.call_args_list[2])  # Startpos has 20 moves

    def test_run_apply_moves_startpos(self) -> None:
        """Test applying moves from starting position."""
        moves = ["e2e4", "e7e5"]
        with patch("builtins.print") as mock_print:
            run_apply_moves(moves, None)

            # Verify output contains the final position
            output_str = str(mock_print.call_args_list)
            assert "P" in output_str  # Should contain pieces
            assert "STM: w" in output_str  # White to move after both moves

    def test_run_apply_moves_custom_fen(self) -> None:
        """Test applying moves from custom FEN."""
        fen = "8/8/8/8/8/8/8/4K3 w - - 0 1"  # Lone king
        moves = ["e1e2"]
        with patch("builtins.print") as mock_print:
            run_apply_moves(moves, fen)

            # Verify output
            output_str = str(mock_print.call_args_list)
            assert "K" in output_str  # Should contain king
            assert "STM: b" in output_str  # Black to move after white move

    def test_run_apply_moves_illegal(self) -> None:
        """Test applying illegal moves."""
        moves = ["e2e5"]  # Not a legal move from startpos
        with patch("builtins.print") as mock_print:
            run_apply_moves(moves, None)

            # Verify illegal move was ignored
            output_str = str(mock_print.call_args_list)
            assert "Ignoring illegal move: e2e5" in output_str

    def test_run_apply_moves_malformed(self) -> None:
        """Test applying malformed moves."""
        moves = ["invalid", "e2", "e2e4e6"]
        with patch("builtins.print") as mock_print:
            run_apply_moves(moves, None)

            # Verify malformed moves were skipped
            output_str = str(mock_print.call_args_list)
            assert "Skipping malformed move" in output_str

    def test_cli_perft_command(self) -> None:
        """Test CLI perft command."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "perft", "1"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Running perft test to depth 1" in result.stdout
        assert "Perft(1) = 20" in result.stdout

    def test_cli_perft_command_with_fen(self) -> None:
        """Test CLI perft command with custom FEN."""
        fen = "8/8/8/8/8/8/8/4K3 w - - 0 1"
        result = subprocess.run(
            ["python", "-m", "cli.runner", "perft", "1", "--fen", fen],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Running perft test to depth 1" in result.stdout
        assert "Perft(1) = 5" in result.stdout

    def test_cli_analyze_command(self) -> None:
        """Test CLI analyze command."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        result = subprocess.run(
            ["python", "-m", "cli.runner", "analyze", fen],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Position:" in result.stdout
        assert "Legal moves: 20" in result.stdout

    def test_cli_apply_command(self) -> None:
        """Test CLI apply command."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "apply", "e2e4", "e7e5"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "P" in result.stdout  # Should contain pieces
        assert "STM: w" in result.stdout  # White to move after both moves

    def test_cli_apply_command_with_fen(self) -> None:
        """Test CLI apply command with custom FEN."""
        fen = "8/8/8/8/8/8/8/4K3 w - - 0 1"
        result = subprocess.run(
            ["python", "-m", "cli.runner", "apply", "e1e2", "--fen", fen],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "K" in result.stdout  # Should contain king
        assert "STM: b" in result.stdout  # Black to move after white move

    def test_cli_help_command(self) -> None:
        """Test CLI help command."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "--help"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Zyra Chess Engine CLI" in result.stdout
        assert "perft" in result.stdout
        assert "analyze" in result.stdout
        assert "apply" in result.stdout
        assert "play" in result.stdout
        assert "profile-style" in result.stdout

    def test_cli_no_command(self) -> None:
        """Test CLI with no command specified."""
        result = subprocess.run(
            ["python", "-m", "cli.runner"], capture_output=True, text=True, cwd="/home/prab/Zyra"
        )

        assert result.returncode == 0
        assert "Zyra Chess Engine CLI" in result.stdout

    def test_cli_perft_depth_0(self) -> None:
        """Test CLI perft command with depth 0."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "perft", "0"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Running perft test to depth 0" in result.stdout
        assert "Perft(0) = 1" in result.stdout

    def test_cli_perft_depth_2(self) -> None:
        """Test CLI perft command with depth 2."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "perft", "2"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Running perft test to depth 2" in result.stdout
        assert "Perft(2) = 400" in result.stdout

    def test_cli_apply_illegal_move(self) -> None:
        """Test CLI apply command with illegal move."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "apply", "e2e5"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Ignoring illegal move: e2e5" in result.stdout

    def test_cli_apply_malformed_move(self) -> None:
        """Test CLI apply command with malformed move."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "apply", "invalid"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Skipping malformed move" in result.stdout

    def test_cli_analyze_empty_board(self) -> None:
        """Test CLI analyze command with empty board."""
        fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        result = subprocess.run(
            ["python", "-m", "cli.runner", "analyze", fen],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Position:" in result.stdout
        assert "Legal moves: 0" in result.stdout

    def test_cli_play_command(self) -> None:
        """Test CLI play command plays some plies and outputs moves."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "play", "--max-plies", "2"],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Played plies:" in result.stdout
        assert "Final position:" in result.stdout

    def test_cli_profile_style_command(self) -> None:
        """Test CLI profile-style command with aggressive profile."""
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        result = subprocess.run(
            [
                "python",
                "-m",
                "cli.runner",
                "profile-style",
                fen,
                "--profile",
                "aggressive",
            ],
            capture_output=True,
            text=True,
            cwd="/home/prab/Zyra",
        )

        assert result.returncode == 0
        assert "Style profile:" in result.stdout
        assert "Total (cp):" in result.stdout
