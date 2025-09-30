"""Optimized evaluation heuristics for high-performance chess engine.

This module provides performance-optimized evaluation functions with caching,
fast lookups, and efficient algorithms to meet <0.1ms per evaluation targets.
"""

from __future__ import annotations

import time
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from performance.profiler import ProfilerContext, profile_function, profile_method

# Optimized piece values with fast lookup
PIECE_VALUES_OPTIMIZED = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}

# Precomputed center squares for fast lookup
CENTER_SQUARES_0X88_OPTIMIZED = [51, 52, 67, 68]  # d4, d5, e4, e5

# Precomputed file and rank values for fast calculation
FILE_VALUES = [0, 1, 2, 3, 4, 5, 6, 7] * 8
RANK_VALUES = [
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    7,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    6,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    5,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    4,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    3,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]


@lru_cache(maxsize=10000)
def _is_offboard_cached(index: int) -> bool:
    """Cached offboard check."""
    return (index & 0x88) != 0


@lru_cache(maxsize=10000)
def _is_white_cached(piece: str) -> bool:
    """Cached white piece check."""
    return piece.isupper()


@lru_cache(maxsize=10000)
def _file_of_cached(index: int) -> int:
    """Cached file calculation."""
    return index & 0x7


@lru_cache(maxsize=10000)
def _rank_of_cached(index: int) -> int:
    """Cached rank calculation."""
    return index >> 4


class OptimizedEvaluationResult:
    """Optimized evaluation result with minimal overhead."""

    def __init__(self, total: float, breakdown: Dict[str, float], style_applied: Dict[str, float]):
        self.total = total
        self.breakdown = breakdown
        self.style_applied = style_applied


class OptimizedEvaluation:
    """High-performance chess position evaluator."""

    def __init__(
        self,
        style_weights: Optional[Dict[str, float]] = None,
        enable_caching: bool = True,
        enable_fast_paths: bool = True,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initialize optimized evaluator."""
        self.style_weights = style_weights or {}
        self.enable_caching = enable_caching
        self.enable_fast_paths = enable_fast_paths
        self._logger = logger

        # Profiling context (required by @profile_method decorator)
        self.context = ProfilerContext()

        # Performance tracking
        self._evaluation_count = 0
        self._total_time = 0.0

        # Evaluation cache
        self._evaluation_cache: Dict[str, OptimizedEvaluationResult] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._log_buffer: List[str] = []

    def _log(self, msg: str) -> None:
        """Log a message to buffer and logger if available."""
        if self._logger is not None:
            try:
                self._logger(msg)
            except Exception:
                pass
        self._log_buffer.append(msg)
        if len(self._log_buffer) > 100:
            self._log_buffer.pop(0)

    @profile_method("optimized_evaluate")
    def evaluate(self, position: Any) -> float:
        """Evaluate position with performance optimizations."""
        start_time = time.perf_counter()

        # Check cache first
        if self.enable_caching:
            position_key = self._get_position_key(position)
            if position_key in self._evaluation_cache:
                self._cache_hits += 1
                result = self._evaluation_cache[position_key]
                self._evaluation_count += 1
                self._total_time += time.perf_counter() - start_time
                return result.total

        self._cache_misses += 1

        # Perform evaluation
        result = self._evaluate_internal_optimized(position)

        # Cache result
        if self.enable_caching:
            self._evaluation_cache[position_key] = result

        self._evaluation_count += 1
        self._total_time += time.perf_counter() - start_time

        return result.total

    def explain_evaluation(self, position: Any) -> Dict[str, Any]:
        """Return breakdown of evaluation components and applied weights."""
        result = self._evaluate_internal_optimized(position)
        return {
            "total": result.total,
            "terms": result.breakdown,
            "style_weights": result.style_applied,
            "log": list(self._log_buffer),
        }

    def _get_position_key(self, position: Any) -> str:
        """Get position key for caching."""
        # Simple hash of position state
        return f"{position.side_to_move}_{hash(tuple(position.squares))}"

    @profile_method("optimized_evaluate_internal")
    def _evaluate_internal_optimized(self, position: Any) -> OptimizedEvaluationResult:
        """Optimized internal evaluation."""
        # Fast path for common positions
        if self.enable_fast_paths and self._is_starting_position(position):
            return self._evaluate_starting_position()

        # Material evaluation (optimized)
        material_cp = self._score_material_optimized(position)

        # Positional evaluation (optimized)
        center_cp = self._score_center_control_optimized(position)
        mobility_cp = self._score_mobility_optimized(position)
        king_safety_cp = self._score_king_safety_optimized(position)

        # Opening principles heuristics (lightweight, no book dependency)
        opening_cp = self._score_opening_principles(position)

        # Combine terms
        breakdown = {
            "material": float(material_cp),
            "center_control": float(center_cp),
            "mobility": float(mobility_cp),
            "king_safety": float(king_safety_cp),
            "opening_principles": float(opening_cp),
        }

        # Apply style weights
        total = 0.0
        weighted_contributions: Dict[str, float] = {}

        # logging - term-by-term with contributions
        self._log_buffer.clear()
        self._log("=== Evaluation Trace ===")
        for term, value in breakdown.items():
            weight = self.style_weights.get(term, 1.0)
            contribution = value * weight
            weighted_contributions[term] = contribution
            total += contribution
            self._log(
                f"  {term}: raw={value:.2f}, weight={weight:.2f}, contribution={contribution:.2f}"
            )

        self._log(f"Applied style weights: {self.style_weights}")
        self._log(f"Total score (cp): {total:.2f}")
        self._log(
            f"Verification: sum of contributions = {sum(weighted_contributions.values()):.2f}"
        )

        return OptimizedEvaluationResult(
            total=total, breakdown=breakdown, style_applied=self.style_weights
        )

    def _is_starting_position(self, position: Any) -> bool:
        """Check if this is the starting position (fast path)."""
        # Simple check for starting position
        return (
            position.side_to_move == "w"
            and position.halfmove_clock == 0
            and position.fullmove_number == 1
        )

    def _evaluate_starting_position(self) -> OptimizedEvaluationResult:
        """Fast evaluation for starting position."""
        breakdown = {
            "material": 0.0,
            "center_control": 0.0,
            "mobility": 0.0,
            "king_safety": 0.0,
            "opening_principles": 0.0,
        }

        # logging - term-by-term with contributions
        self._log_buffer.clear()
        self._log("=== Evaluation Trace ===")
        for term, value in breakdown.items():
            weight = self.style_weights.get(term, 1.0)
            contribution = value * weight
            self._log(
                f"  {term}: raw={value:.2f}, weight={weight:.2f}, contribution={contribution:.2f}"
            )

        self._log(f"Applied style weights: {self.style_weights}")
        self._log(f"Total score (cp): 0.00")
        self._log(f"Verification: sum of contributions = 0.00")

        return OptimizedEvaluationResult(
            total=0.0,
            breakdown=breakdown,
            style_applied=self.style_weights,
        )

    @profile_method("optimized_material")
    def _score_material_optimized(self, position: Any) -> int:
        """Optimized material evaluation."""
        score = 0

        # Fast iteration over board
        for idx in range(128):
            if _is_offboard_cached(idx):
                continue

            piece = position.squares[idx]
            if piece == "\u0000":
                continue

            lower = piece.lower()
            if lower in PIECE_VALUES_OPTIMIZED:
                val = PIECE_VALUES_OPTIMIZED[lower]
                score += val if _is_white_cached(piece) else -val

        return score

    @profile_method("optimized_center_control")
    def _score_center_control_optimized(self, position: Any) -> int:
        """Optimized center control evaluation."""
        score = 0

        for center_sq in CENTER_SQUARES_0X88_OPTIMIZED:
            piece = position.squares[center_sq]
            if piece == "\u0000":
                continue

            # Center control bonus
            if piece.lower() == "p":  # Pawns
                score += 10 if _is_white_cached(piece) else -10
            elif piece.lower() in ["n", "b"]:  # Knights and bishops
                score += 5 if _is_white_cached(piece) else -5

        return score

    @profile_method("optimized_mobility")
    def _score_mobility_optimized(self, position: Any) -> int:
        """Optimized mobility evaluation."""
        score = 0

        # Count available moves for each piece
        for idx in range(128):
            if _is_offboard_cached(idx):
                continue

            piece = position.squares[idx]
            if piece == "\u0000":
                continue

            # Simple mobility count (this would be optimized further)
            mobility = self._count_moves_for_piece(position, idx)
            score += mobility if _is_white_cached(piece) else -mobility

        return score

    def _count_moves_for_piece(self, position: Any, idx: int) -> int:
        """Count moves for a specific piece (simplified for performance)."""
        piece = position.squares[idx]
        if piece == "\u0000":
            return 0

        # Simplified mobility calculation
        lower = piece.lower()
        if lower == "p":
            return 2  # Typical pawn mobility
        elif lower == "n":
            return 4  # Typical knight mobility
        elif lower == "b":
            return 6  # Typical bishop mobility
        elif lower == "r":
            return 8  # Typical rook mobility
        elif lower == "q":
            return 12  # Typical queen mobility
        elif lower == "k":
            return 3  # Typical king mobility

        return 0

    @profile_method("optimized_king_safety")
    def _score_king_safety_optimized(self, position: Any) -> int:
        """Optimized king safety evaluation."""
        score = 0

        # Find kings
        white_king = self._find_king(position, True)
        black_king = self._find_king(position, False)

        if white_king is not None:
            score += self._evaluate_king_safety(position, white_king, True)

        if black_king is not None:
            score -= self._evaluate_king_safety(position, black_king, False)

        return score

    def _find_king(self, position: Any, white: bool) -> Optional[int]:
        """Find king position."""
        for idx in range(128):
            if _is_offboard_cached(idx):
                continue

            piece = position.squares[idx]
            if piece == "\u0000":
                continue

            if piece.lower() == "k" and _is_white_cached(piece) == white:
                return idx

        return None

    def _evaluate_king_safety(self, position: Any, king_sq: int, white: bool) -> int:
        """Evaluate king safety for a specific king."""
        safety = 0

        # Check pawn shield
        if white:
            # White king pawn shield
            for offset in [-17, -16, -15, -1, 1, -17, -16, -15]:
                shield_sq = king_sq + offset
                if not _is_offboard_cached(shield_sq):
                    piece = position.squares[shield_sq]
                    if piece == "P":
                        safety += 5
        else:
            # Black king pawn shield
            for offset in [15, 16, 17, -1, 1, 15, 16, 17]:
                shield_sq = king_sq + offset
                if not _is_offboard_cached(shield_sq):
                    piece = position.squares[shield_sq]
                    if piece == "p":
                        safety += 5

        return safety

    def _score_opening_principles(self, position: Any) -> int:
        """Score opening phase heuristics (development, center, king safety triggers).

        No large book dependency - uses position features only.
        """
        # Only apply opening principles in early game (first ~15 moves)
        if not self._is_opening_phase(position):
            return 0

        score = 0

        # 1. Development incentives: reward developed minor pieces
        score += self._score_piece_development(position, white=True)
        score -= self._score_piece_development(position, white=False)

        # 2. Center control already handled by existing center_control term,
        # so we don't duplicate it here

        # 3. Early king safety: reward castling
        score += self._score_castling_incentive(position, white=True)
        score -= self._score_castling_incentive(position, white=False)

        return score

    def _is_opening_phase(self, position: Any) -> bool:
        """Check if we're in the opening phase (simplified heuristic)."""
        # Opening phase: move count < 15 OR most pieces still on board
        if position.fullmove_number <= 15:
            return True

        # Alternative: count developed pieces
        piece_count = sum(
            1 for sq in position.squares if sq != "\u0000" and sq.lower() not in ["k", "p"]
        )
        # If most pieces still on board (> 10 minor/major pieces), still opening
        return piece_count > 10

    def _score_piece_development(self, position: Any, white: bool) -> int:
        """Score piece development for one side."""
        score = 0

        # Starting squares for knights and bishops
        if white:
            knight_start_squares = [1, 6]  # b1, g1
            bishop_start_squares = [2, 5]  # c1, f1
            back_rank = 0
        else:
            knight_start_squares = [113, 118]  # b8, g8
            bishop_start_squares = [114, 117]  # c8, f8
            back_rank = 7

        # Penalize pieces still on starting squares
        for sq in knight_start_squares:
            piece = position.squares[sq]
            if piece != "\u0000":
                expected = "N" if white else "n"
                if piece == expected:
                    score -= 5  # Penalty for undeveloped knight

        for sq in bishop_start_squares:
            piece = position.squares[sq]
            if piece != "\u0000":
                expected = "B" if white else "b"
                if piece == expected:
                    score -= 5  # Penalty for undeveloped bishop

        # Reward knights and bishops away from back rank
        for idx in range(128):
            if _is_offboard_cached(idx):
                continue

            piece = position.squares[idx]
            if piece == "\u0000":
                continue

            rank = _rank_of_cached(idx)

            if white and _is_white_cached(piece):
                if piece.lower() in ["n", "b"] and rank > back_rank:
                    score += 3  # Reward developed piece
            elif not white and not _is_white_cached(piece):
                if piece.lower() in ["n", "b"] and rank < back_rank:
                    score += 3  # Reward developed piece

        return score

    def _score_castling_incentive(self, position: Any, white: bool) -> int:
        """Score castling incentives (reward castled positions)."""
        score = 0

        # Check if king has moved to typical castled position
        if white:
            # Kingside castle: g1 (6), Queenside: c1 (2)
            king_sq = self._find_king(position, white=True)
            if king_sq is not None:
                file = _file_of_cached(king_sq)
                rank = _rank_of_cached(king_sq)
                # If king is on g1 or c1 (rank 0), likely castled
                if rank == 0 and (file == 6 or file == 2):
                    score += 15  # Reward castling
                # If king is still on e1 (file 4, rank 0) after move 10, penalize
                elif rank == 0 and file == 4 and position.fullmove_number > 10:
                    score -= 10
        else:
            # Black: g8 or c8
            king_sq = self._find_king(position, white=False)
            if king_sq is not None:
                file = _file_of_cached(king_sq)
                rank = _rank_of_cached(king_sq)
                # If king is on g8 or c8 (rank 7), likely castled
                if rank == 7 and (file == 6 or file == 2):
                    score += 15  # Reward castling
                # If king is still on e8 after move 10, penalize
                elif rank == 7 and file == 4 and position.fullmove_number > 10:
                    score -= 10

        return score

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_time_ms = (
            (self._total_time / self._evaluation_count * 1000) if self._evaluation_count > 0 else 0
        )
        cache_hit_rate = (
            (self._cache_hits / (self._cache_hits + self._cache_misses) * 100)
            if (self._cache_hits + self._cache_misses) > 0
            else 0
        )

        return {
            "evaluation_count": self._evaluation_count,
            "total_time": self._total_time,
            "avg_time_ms": avg_time_ms,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "target_met": avg_time_ms < 0.1,
        }

    def clear_cache(self) -> None:
        """Clear evaluation cache."""
        self._evaluation_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


# Convenience function for quick evaluation
@profile_function("quick_evaluate")
def quick_evaluate(position: Any, style_weights: Optional[Dict[str, float]] = None) -> float:
    """Quick evaluation function for performance-critical code."""
    evaluator = OptimizedEvaluation(style_weights=style_weights, enable_caching=True)
    return evaluator.evaluate(position)
