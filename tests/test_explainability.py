"""Tests for explainability and reproducibility features."""

import json
import subprocess
from typing import Dict

import pytest

from core.board import Board
from eval.heuristics import Evaluation, create_evaluator, parse_style_config
from performance.metrics import RunMetadata, create_run_metadata


class TestEvaluationLogging:
    """Test evaluation term-by-term logging."""

    def test_evaluation_trace_includes_term_contributions(self):
        """Verify evaluation trace includes raw values, weights, and contributions."""
        board = Board()
        board.set_startpos()

        style_weights = {"material": 1.0, "mobility": 1.5}
        evaluator = create_evaluator(style_weights)

        result = evaluator.explain_evaluation(board)

        # Check structure
        assert "terms" in result
        assert "style_weights" in result
        assert "total" in result
        assert "log" in result

        # Check that log contains trace
        log_text = "\n".join(result["log"])
        assert "Evaluation Trace" in log_text
        assert "raw=" in log_text
        assert "weight=" in log_text
        assert "contribution=" in log_text

    def test_evaluation_trace_sum_equals_total(self):
        """Verify sum of weighted contributions equals final evaluation."""
        board = Board()
        board.set_startpos()

        style_weights = {"material": 1.0, "mobility": 1.5, "king_safety": 0.8}
        evaluator = create_evaluator(style_weights)

        result = evaluator.explain_evaluation(board)

        # Calculate sum of contributions manually
        total_contribution = 0.0
        for term, value in result["terms"].items():
            weight = result["style_weights"].get(term, 1.0)
            total_contribution += value * weight

        # Check within floating-point tolerance
        assert abs(total_contribution - result["total"]) < 1e-6

    def test_evaluation_trace_includes_style_profile_context(self):
        """Verify trace includes style profile name and weights."""
        board = Board()
        board.set_startpos()

        # Use aggressive profile
        evaluator = create_evaluator("aggressive")
        result = evaluator.explain_evaluation(board)

        # Check that style weights are present
        assert result["style_weights"]
        assert "attacking_motifs" in result["style_weights"]

        # Check log includes style info
        log_text = "\n".join(result["log"])
        assert "style weights" in log_text.lower()


class TestReproducibilityMetadata:
    """Test reproducibility metadata emission."""

    def test_run_metadata_includes_seed(self):
        """Verify run metadata includes seed."""
        metadata = create_run_metadata(seed=12345)

        assert metadata.seed == 12345
        assert metadata.timestamp is not None

    def test_run_metadata_includes_style_profile(self):
        """Verify run metadata includes style profile."""
        metadata = create_run_metadata(seed=42, style_profile="aggressive")

        assert metadata.style_profile == "aggressive"

    def test_run_metadata_includes_config_snapshot(self):
        """Verify run metadata includes config snapshot."""
        config = {"movetime": 1000, "nodes": 5000}
        metadata = create_run_metadata(seed=42, config=config)

        assert metadata.config_snapshot == config

    def test_run_metadata_serializes_to_json(self):
        """Verify metadata can be serialized to JSON."""
        metadata = create_run_metadata(seed=12345, style_profile="defensive", config={"depth": 3})

        json_str = metadata.to_json()
        parsed = json.loads(json_str)

        assert parsed["seed"] == 12345
        assert parsed["style_profile"] == "defensive"
        assert parsed["config_snapshot"]["depth"] == 3
        assert "timestamp" in parsed


class TestCLISeedAndMetadata:
    """Test CLI --seed parameter and metadata output."""

    def test_cli_accepts_seed_parameter(self):
        """Verify CLI accepts --seed parameter."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "--seed", "12345", "perft", "1"],
            capture_output=True,
            text=True,
        )

        # Should not error
        assert result.returncode == 0
        # Should echo metadata
        assert "Run Metadata" in result.stdout
        assert "12345" in result.stdout

    def test_cli_prints_metadata_block(self):
        """Verify CLI prints machine-readable metadata block."""
        result = subprocess.run(
            ["python", "-m", "cli.runner", "--seed", "42", "perft", "1"],
            capture_output=True,
            text=True,
        )

        # Check for metadata markers
        assert "=== Run Metadata ===" in result.stdout

        # Check it's valid JSON by extracting and parsing
        lines = result.stdout.split("\n")
        json_lines = []
        in_json = False
        for line in lines:
            if "=== Run Metadata ===" in line:
                in_json = True
                continue
            if in_json:
                if "===================" in line:
                    break
                json_lines.append(line)

        if json_lines:
            json_str = "\n".join(json_lines)
            metadata = json.loads(json_str)
            assert metadata["seed"] == 42

    def test_cli_profile_style_includes_profile_in_metadata(self):
        """Verify profile-style command includes profile name in metadata."""
        result = subprocess.run(
            [
                "python",
                "-m",
                "cli.runner",
                "--seed",
                "123",
                "profile-style",
                "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "--profile",
                "aggressive",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "aggressive" in result.stdout
