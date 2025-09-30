"""Optimized Monte Carlo Tree Search implementation.

This module provides performance-optimized MCTS with caching, move ordering,
and efficient memory management to meet 10,000 nodes/sec targets.
"""

import random
import time
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from core.board import Board
from core.moves import Move, generate_moves, make_move, unmake_move
from eval.heuristics import Evaluation, parse_style_config
from performance.profiler import ProfilerContext, profile_function, profile_method


class OptimizedMCTSNode:
    """Optimized MCTS node with performance enhancements."""

    def __init__(
        self,
        position: Board,
        move: Optional[Move] = None,
        parent: Optional["OptimizedMCTSNode"] = None,
    ) -> None:
        """Initialize optimized MCTS node."""
        self.position = position
        self.move = move
        self.parent = parent
        self.visits = 0
        self.value = 0.0
        self.children: List[OptimizedMCTSNode] = []
        self.untried_moves: List[Move] = []
        self._legal_moves_generated = False
        self._cached_legal_moves: Optional[List[Move]] = None

        # Performance optimizations
        self._is_terminal_cached: Optional[bool] = None
        self._is_fully_expanded_cached: Optional[bool] = None

    def is_fully_expanded(self) -> bool:
        """Check if all legal moves have been tried (with caching)."""
        if self._is_fully_expanded_cached is not None:
            return self._is_fully_expanded_cached

        if not self._legal_moves_generated:
            self.untried_moves = self._get_legal_moves()
            self._legal_moves_generated = True

        result = len(self.untried_moves) == 0
        self._is_fully_expanded_cached = result
        return result

    def is_terminal(self) -> bool:
        """Check if this is a terminal node (with caching)."""
        if self._is_terminal_cached is not None:
            return self._is_terminal_cached

        if not self._legal_moves_generated:
            self.untried_moves = self._get_legal_moves()
            self._legal_moves_generated = True

        result = len(self.untried_moves) == 0
        self._is_terminal_cached = result
        return result

    def _get_legal_moves(self) -> List[Move]:
        """Get legal moves with caching."""
        if self._cached_legal_moves is not None:
            return self._cached_legal_moves

        self._cached_legal_moves = generate_moves(self.position)
        return self._cached_legal_moves

    def get_ucb_score(self, exploration_constant: float = 1.414) -> float:
        """Calculate UCB1 score for selection (optimized)."""
        if self.visits == 0:
            return float("inf")

        if self.parent is None:
            return 0.0

        # Optimized UCB1 calculation
        exploitation = self.value / self.visits
        parent_visits = self.parent.visits
        exploration = exploration_constant * (2 * (parent_visits**0.5) / self.visits) ** 0.5
        return exploitation + exploration

    def invalidate_cache(self) -> None:
        """Invalidate cached values when position changes."""
        self._is_terminal_cached = None
        self._is_fully_expanded_cached = None
        self._cached_legal_moves = None


class OptimizedMCTSSearch:
    """Performance-optimized Monte Carlo Tree Search engine."""

    def __init__(
        self,
        max_playouts: int = 10000,
        movetime_ms: Optional[int] = None,
        seed: Optional[int] = None,
        move_ordering_hook: Optional[Callable] = None,
        style: Optional[dict or str] = None,
        enable_caching: bool = True,
        enable_move_ordering: bool = True,
    ) -> None:
        """Initialize optimized MCTS with performance features."""
        self.max_playouts = max_playouts
        self.movetime_ms = movetime_ms
        self.move_ordering_hook = move_ordering_hook
        self.exploration_constant = 1.414
        self.enable_caching = enable_caching
        self.enable_move_ordering = enable_move_ordering

        # Profiling context (required by @profile_method decorator)
        self.context = ProfilerContext()

        # Evaluation configuration
        self.style_weights = parse_style_config(style)
        self.evaluator = Evaluation(style_weights=self.style_weights)

        # Per-instance RNG for reproducibility and isolation
        self._rng = random.Random(seed)

        # Performance tracking
        self._nodes_processed = 0
        self._start_time = 0.0

        # Move ordering cache
        self._move_ordering_cache: Dict[str, List[Move]] = {}

    @profile_method("mcts_search")
    def search(self, position: Board) -> Optional[Move]:
        """Perform optimized MCTS search and return best move."""
        self._start_time = time.perf_counter()
        self._nodes_processed = 0

        if self.movetime_ms is not None:
            start_time = time.time()
            end_time = start_time + (self.movetime_ms / 1000.0)
        else:
            end_time = None

        root = OptimizedMCTSNode(position)

        # If no legal moves, return None
        if root.is_terminal():
            return None

        playouts = 0

        # Pre-order moves at root for better performance
        if self.enable_move_ordering and self.move_ordering_hook:
            root.untried_moves = self._order_moves(root.position, root.untried_moves)

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
            self._nodes_processed += 1

        # Return best move based on visit count
        if not root.children:
            return None

        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    @profile_method("mcts_selection")
    def _selection(self, node: OptimizedMCTSNode) -> OptimizedMCTSNode:
        """Selection phase: traverse tree using UCB1 (optimized)."""
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return node
            else:
                # Use optimized child selection
                best_child = None
                best_score = float("-inf")

                for child in node.children:
                    score = child.get_ucb_score(self.exploration_constant)
                    if score > best_score:
                        best_score = score
                        best_child = child

                if best_child is None:
                    break
                node = best_child
        return node

    @profile_method("mcts_expansion")
    def _expansion(self, node: OptimizedMCTSNode) -> OptimizedMCTSNode:
        """Expansion phase: add a new child node (optimized)."""
        if not node.untried_moves:
            return node

        # Select move with move ordering if enabled
        if self.enable_move_ordering and self.move_ordering_hook:
            move = self._select_ordered_move(node)
        else:
            move = self._rng.choice(node.untried_moves)

        # Remove selected move from untried moves
        node.untried_moves.remove(move)

        # Create new child node
        child_position = self._make_move_copy(node.position, move)
        child = OptimizedMCTSNode(child_position, move, node)
        node.children.append(child)

        return child

    def _select_ordered_move(self, node: OptimizedMCTSNode) -> Move:
        """Select move using move ordering."""
        if not node.untried_moves:
            return self._rng.choice(node.untried_moves)

        # Use move ordering hook if available
        if self.move_ordering_hook:
            ordered_moves = self.move_ordering_hook(node.position, node.untried_moves)
            # Select from top moves with some randomness
            top_moves = ordered_moves[: max(1, len(ordered_moves) // 3)]
            return self._rng.choice(top_moves)

        return self._rng.choice(node.untried_moves)

    @profile_method("mcts_simulation")
    def _simulation(self, node: OptimizedMCTSNode) -> float:
        """Simulation phase: playout with style-aware policies (optimized)."""
        position = node.position
        depth = 0
        max_depth = 50  # Prevent infinite playouts

        while depth < max_depth:
            legal_moves = generate_moves(position)
            if not legal_moves:
                # Terminal position - return evaluation
                return self._evaluate_position(position)

            # Style-aware move selection
            move = self._select_playout_move(position, legal_moves)

            # Make move
            position = self._make_move_copy(position, move)
            depth += 1

        # Return evaluation of final position
        return self._evaluate_position(position)

    def _select_playout_move(self, position: Board, legal_moves: List[Move]) -> Move:
        """Select move for playout with style influence."""
        if not legal_moves:
            return None

        # Apply style influence to move selection
        if self.style_weights:
            # Use evaluation to bias move selection
            move_scores = []
            for move in legal_moves:
                # Quick evaluation of move
                score = self._quick_evaluate_move(position, move)
                move_scores.append((move, score))

            # Weight moves by style preferences
            weighted_moves = []
            for move, score in move_scores:
                weight = 1.0 + (score / 1000.0)  # Normalize score
                weighted_moves.extend([move] * max(1, int(weight)))

            return self._rng.choice(weighted_moves)

        return self._rng.choice(legal_moves)

    def _quick_evaluate_move(self, position: Board, move: Move) -> float:
        """Quick evaluation of a move for playout selection."""
        # Simple heuristic evaluation
        piece = position.squares[move.from_square]
        target = position.squares[move.to_square]

        score = 0.0

        # Capture bonus
        if target != "\u0000":
            score += 100

        # Center control bonus
        if move.to_square in [51, 52, 67, 68]:  # d4, d5, e4, e5
            score += 10

        return score

    @profile_method("mcts_backpropagation")
    def _backpropagation(self, node: OptimizedMCTSNode, result: float) -> None:
        """Backpropagation phase: update values up the tree (optimized)."""
        while node is not None:
            node.visits += 1
            node.value += result

            # Invalidate cache for parent nodes
            if node.parent:
                node.parent.invalidate_cache()

            node = node.parent

    def _evaluate_position(self, position: Board) -> float:
        """Evaluate position using the configured evaluator."""
        return self.evaluator.evaluate(position)

    def _make_move_copy(self, position: Board, move: Move) -> Board:
        """Make a move and return new board position (optimized)."""
        # Create a copy of the position
        new_position = Board()
        new_position.squares = position.squares.copy()
        new_position.side_to_move = position.side_to_move
        new_position.castling = position.castling
        new_position.ep_square = position.ep_square
        new_position.halfmove_clock = position.halfmove_clock
        new_position.fullmove_number = position.fullmove_number

        # Apply the move
        make_move(new_position, move)

        return new_position

    def _order_moves(self, position: Board, moves: List[Move]) -> List[Move]:
        """Order moves for better performance."""
        if not self.move_ordering_hook:
            return moves

        # Use cached ordering if available
        position_key = self._get_position_key(position)
        if position_key in self._move_ordering_cache:
            return self._move_ordering_cache[position_key]

        # Apply move ordering
        ordered_moves = self.move_ordering_hook(position, moves)

        # Cache the result
        if self.enable_caching:
            self._move_ordering_cache[position_key] = ordered_moves

        return ordered_moves

    def _get_position_key(self, position: Board) -> str:
        """Get a key for position caching."""
        # Simple position key for caching
        return f"{position.side_to_move}_{hash(tuple(position.squares))}"

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        elapsed_time = time.perf_counter() - self._start_time
        nodes_per_second = self._nodes_processed / elapsed_time if elapsed_time > 0 else 0

        return {
            "nodes_processed": self._nodes_processed,
            "elapsed_time": elapsed_time,
            "nodes_per_second": nodes_per_second,
            "cache_hits": len(self._move_ordering_cache),
            "target_met": nodes_per_second >= 10000,
        }
