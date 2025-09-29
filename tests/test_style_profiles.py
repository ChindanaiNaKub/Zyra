"""Golden-ish baseline checks for style profiles producing differentiated outputs."""

from core.board import Board
from eval.heuristics import Evaluation, get_style_profile


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
