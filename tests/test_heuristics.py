"""Unit tests for evaluation heuristics and explainable logging."""

import time

from core.board import Board
from eval.heuristics import Evaluation, get_style_profile, parse_style_config


def test_material_base_values_startpos() -> None:
    board = Board()
    board.set_startpos()
    ev = Evaluation()
    score = ev.evaluate(board)
    # Startpos should be roughly equal; allow small non-zero due to heuristics
    assert abs(score) < 5


def test_attacking_motifs_knight_attacks_queen() -> None:
    board = Board()
    # Place white knight on c3 (c3 -> c file=2, rank=3), black queen on d5 so it can be attacked
    board.load_fen("8/8/3q4/8/8/2N5/8/8 w - - 0 1")
    ev_plain = Evaluation()
    plain = ev_plain.evaluate(board)

    # Aggressive style should weight attacking motifs higher → score increases
    aggressive = Evaluation(style_weights=get_style_profile("aggressive"))
    aggr = aggressive.evaluate(board)

    assert aggr >= plain


def test_explain_logging_contains_terms_and_weights() -> None:
    board = Board()
    board.set_startpos()
    ev = Evaluation(style_weights=parse_style_config("defensive"))
    explain = ev.explain_evaluation(board)
    assert "total" in explain
    assert "terms" in explain
    assert "style_weights" in explain
    assert "log" in explain
    # Ensure expected term keys exist
    for key in [
        "material",
        "attacking_motifs",
        "center_control",
        "rook_files",
        "mobility",
        "king_safety",
        "initiative",
        "hanging_pieces",
        "threat_bonus",
        "check_urgency",
    ]:
        assert key in explain["terms"]


def test_hanging_piece_penalty_simple() -> None:
    board = Board()
    # White queen unprotected attacked by black knight
    board.load_fen("8/8/8/3n4/8/8/8/4Q3 w - - 0 1")
    ev = Evaluation()
    score = ev.evaluate(board)
    # Penalize white for hanging queen -> negative score
    assert score < 0


def test_evaluation_performance_smoke() -> None:
    board = Board()
    board.set_startpos()
    ev = Evaluation(style_weights=get_style_profile("experimental"))
    start = time.time()
    total = 0.0
    for _ in range(100):
        total += ev.evaluate(board)
    elapsed = (time.time() - start) * 1000
    # Expect reasonably fast (< 300ms on typical dev machines)
    assert elapsed < 300
    assert isinstance(total, float)
