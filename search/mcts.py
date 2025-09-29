"""Monte Carlo Tree Search implementation.

This module implements MCTS with configurable playout policies and
stochastic exploration for chess engine decision making.
"""

import random
import time
from typing import Any, Callable, List, Optional

from core.board import Board
from core.moves import Move, generate_moves, make_move, unmake_move
from eval.heuristics import Evaluation, parse_style_config


class MCTSNode:
    """Represents a node in the Monte Carlo search tree."""

    def __init__(
        self, position: Board, move: Optional[Move] = None, parent: Optional["MCTSNode"] = None
    ) -> None:
        """Initialize a new MCTS node."""
        self.position = position
        self.move = move
        self.parent = parent
        self.visits = 0
        self.value = 0.0
        self.children: List[MCTSNode] = []
        self.untried_moves: List[Move] = []
        self._legal_moves_generated = False

    def is_fully_expanded(self) -> bool:
        """Check if all legal moves have been tried."""
        if not self._legal_moves_generated:
            self.untried_moves = generate_moves(self.position)
            self._legal_moves_generated = True
        return len(self.untried_moves) == 0

    def is_terminal(self) -> bool:
        """Check if this is a terminal node (no legal moves)."""
        if not self._legal_moves_generated:
            self.untried_moves = generate_moves(self.position)
            self._legal_moves_generated = True
        return len(self.untried_moves) == 0

    def get_ucb_score(self, exploration_constant: float = 1.414) -> float:
        """Calculate UCB1 score for selection."""
        if self.visits == 0:
            return float("inf")

        if self.parent is None:
            return 0.0

        exploitation = self.value / self.visits
        exploration = exploration_constant * (2 * (self.parent.visits**0.5) / self.visits) ** 0.5
        return exploitation + exploration


class MCTSSearch:
    """Monte Carlo Tree Search engine."""

    def __init__(
        self,
        max_playouts: int = 10000,
        movetime_ms: Optional[int] = None,
        seed: Optional[int] = None,
        move_ordering_hook: Optional[Callable] = None,
        style: Optional[dict or str] = None,
    ) -> None:
        """Initialize MCTS with limits and configuration."""
        self.max_playouts = max_playouts
        self.movetime_ms = movetime_ms
        self.move_ordering_hook = move_ordering_hook
        self.exploration_constant = 1.414
        # Evaluation configuration
        self.style_weights = parse_style_config(style)
        self.evaluator = Evaluation(style_weights=self.style_weights)

        # Per-instance RNG for reproducibility and isolation
        self._rng = random.Random(seed)

    def search(self, position: Board) -> Optional[Move]:
        """Perform MCTS search and return best move."""
        if self.movetime_ms is not None:
            start_time = time.time()
            end_time = start_time + (self.movetime_ms / 1000.0)
        else:
            end_time = None

        root = MCTSNode(position)

        # If no legal moves, return None
        if root.is_terminal():
            return None

        playouts = 0

        while playouts < self.max_playouts:
            # Check time limit if specified
            if end_time is not None and time.time() >= end_time:
                break

            # Selection and expansion phase
            node = self._selection(root)
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self._expansion(node)

            # Simulation phase
            result = self._simulation(node)

            # Backpropagation phase
            self._backpropagation(node, result)

            playouts += 1

        # Return best move based on visit count
        if not root.children:
            return None

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _selection(self, node: MCTSNode) -> MCTSNode:
        """Selection phase: traverse tree using UCB1."""
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                node = max(node.children, key=lambda c: c.get_ucb_score(self.exploration_constant))
        return node

    def _expansion(self, node: MCTSNode) -> MCTSNode:
        """Expansion phase: add a new child node."""
        if not node.untried_moves:
            return node

        # Get move to expand
        move = node.untried_moves.pop()

        # Create new position
        new_position = Board()
        new_position.copy_from(node.position)
        make_move(new_position, move)

        # Create child node
        child = MCTSNode(new_position, move, node)
        node.children.append(child)

        return child

    def _simulation(self, node: MCTSNode) -> float:
        """Simulation phase: play random moves to completion."""
        position = Board()
        position.copy_from(node.position)

        # Apply move ordering if hook is provided
        moves = generate_moves(position)
        if self.move_ordering_hook:
            moves = self.move_ordering_hook(position, moves)

        # Limit simulation depth to prevent infinite loops
        max_depth = 100
        depth = 0

        while moves and depth < max_depth:
            # Pick random move using instance RNG
            move = self._rng.choice(moves)
            make_move(position, move)
            depth += 1

            moves = generate_moves(position)
            if self.move_ordering_hook:
                moves = self.move_ordering_hook(position, moves)

        # Return evaluation signal scaled to [0,1] from centipawn score
        # Map centipawns via sigmoid-like scaling for stability
        score_cp = self.evaluator.evaluate(position)
        # Optionally could use explain for logging/debug
        # explain = self.evaluator.explain_evaluation(position)
        # Convert to 0..1 win likelihood-ish value
        # 0 cp -> 0.5; +300 cp -> ~0.73; -300 cp -> ~0.27
        scale = 300.0
        value = 1.0 / (1.0 + pow(10.0, -score_cp / scale))
        return float(value)

    def _backpropagation(self, node: MCTSNode, result: float) -> None:
        """Backpropagation phase: update statistics up the tree."""
        while node is not None:
            node.visits += 1
            node.value += result
            node = node.parent


def heuristic_move_ordering(position: Board, moves: List[Move]) -> List[Move]:
    """Order moves heuristically: captures, checks, promotions first."""

    def move_priority(move: Move) -> int:
        # Priority 1: Captures (check if destination has enemy piece)
        to_piece = position.squares[move.to_square]
        if to_piece != "\u0000":
            # Different color pieces
            if (position.side_to_move == "w" and to_piece.islower()) or (
                position.side_to_move == "b" and to_piece.isupper()
            ):
                return 1

        # Priority 2: Promotions
        if move.promotion is not None:
            return 2

        # Priority 3: Checks (simplified - would need to check if move gives check)
        # For now, we'll use a basic heuristic
        from_piece = position.squares[move.from_square]
        if from_piece.lower() in ["q", "r", "b", "n"]:
            return 3

        # Priority 4: Other moves
        return 4

    # Sort by priority (lower number = higher priority)
    return sorted(moves, key=move_priority)


def style_aware_move_ordering(
    position: Board, moves: List[Move], style_weights: Optional[dict] = None
) -> List[Move]:
    """Apply style-aware ordering with heuristic tie-breaking."""
    # First apply heuristic ordering
    ordered_moves = heuristic_move_ordering(position, moves)

    # If no style weights provided, return heuristic ordering
    if not style_weights:
        return ordered_moves

    # For now, return heuristic ordering as base implementation
    # Future enhancement: apply style weights for tie-breaking
    return ordered_moves
