"""Integration tests for MCTS search interacting with Evaluation and styles."""

from core.board import Board
from search.mcts import MCTSSearch


def test_mcts_with_style_parameter_runs() -> None:
    board = Board()
    board.set_startpos()

    search = MCTSSearch(max_playouts=50, seed=7, style="aggressive")
    move = search.search(board)
    # Returns a move or None if terminal; startpos should give a move
    assert move is not None


def test_mcts_explainable_eval_available() -> None:
    board = Board()
    board.set_startpos()

    search = MCTSSearch(max_playouts=5, seed=1, style="defensive")
    # Run a very small search
    _ = search.search(board)
    # Ensure evaluator can provide an explanation without error
    explain = search.evaluator.explain_evaluation(board)
    assert "total" in explain and "terms" in explain
