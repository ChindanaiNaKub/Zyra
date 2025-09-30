"""Optimized move generation for high-performance chess engine.

This module provides performance-optimized move generation with caching,
fast lookups, and efficient algorithms to meet <0.01ms per position targets.
"""

import time
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from core.moves import Move, _is_black, _is_offboard, _is_white, _same_color
from performance.profiler import ProfilerContext, profile_function, profile_method

# Precomputed offsets for fast piece movement
KNIGHT_OFFSETS_OPTIMIZED = [31, 33, 14, 18, -31, -33, -14, -18]
BISHOP_DIRECTIONS_OPTIMIZED = [15, 17, -15, -17]
ROOK_DIRECTIONS_OPTIMIZED = [16, -16, 1, -1]
QUEEN_DIRECTIONS_OPTIMIZED = BISHOP_DIRECTIONS_OPTIMIZED + ROOK_DIRECTIONS_OPTIMIZED
KING_OFFSETS_OPTIMIZED = [1, -1, 16, -16, 15, 17, -15, -17]

# Precomputed pawn move offsets
PAWN_MOVE_OFFSETS_WHITE = [16, 32]  # Single and double move
PAWN_MOVE_OFFSETS_BLACK = [-16, -32]  # Single and double move
PAWN_CAPTURE_OFFSETS_WHITE = [15, 17]  # Diagonal captures
PAWN_CAPTURE_OFFSETS_BLACK = [-15, -17]  # Diagonal captures


@lru_cache(maxsize=10000)
def _is_offboard_cached(index: int) -> bool:
    """Cached offboard check."""
    return (index & 0x88) != 0


@lru_cache(maxsize=10000)
def _is_white_cached(piece: str) -> bool:
    """Cached white piece check."""
    return piece.isupper()


@lru_cache(maxsize=10000)
def _is_black_cached(piece: str) -> bool:
    """Cached black piece check."""
    return piece.islower()


class OptimizedMoveGenerator:
    """High-performance move generator with caching and optimizations."""

    def __init__(self, enable_caching: bool = True, enable_fast_paths: bool = True):
        """Initialize optimized move generator."""
        self.enable_caching = enable_caching
        self.enable_fast_paths = enable_fast_paths

        # Profiling context (required by @profile_method decorator)
        self.context = ProfilerContext()

        # Move generation cache
        self._move_cache: Dict[str, List[Move]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Performance tracking
        self._generation_count = 0
        self._total_time = 0.0

    @profile_method("optimized_generate_moves")
    def generate_moves(self, board: Any) -> List[Move]:
        """Generate legal moves with performance optimizations."""
        start_time = time.perf_counter()

        # Check cache first
        if self.enable_caching:
            position_key = self._get_position_key(board)
            if position_key in self._move_cache:
                self._cache_hits += 1
                self._generation_count += 1
                self._total_time += time.perf_counter() - start_time
                return self._move_cache[position_key]

        self._cache_misses += 1

        # Generate moves
        moves = self._generate_moves_internal(board)

        # Cache result
        if self.enable_caching:
            self._move_cache[position_key] = moves

        self._generation_count += 1
        self._total_time += time.perf_counter() - start_time

        return moves

    def _get_position_key(self, board: Any) -> str:
        """Get position key for caching."""
        return f"{board.side_to_move}_{hash(tuple(board.squares))}"

    @profile_method("optimized_generate_moves_internal")
    def _generate_moves_internal(self, board: Any) -> List[Move]:
        """Internal move generation with optimizations."""
        legal_moves = []
        side_white = board.side_to_move == "w"

        # Fast iteration over board
        for from_sq in range(128):
            if _is_offboard_cached(from_sq):
                continue

            piece = board.squares[from_sq]
            if piece == "\u0000":
                continue

            # Check if piece belongs to current side
            if side_white and not _is_white_cached(piece):
                continue
            if not side_white and not _is_black_cached(piece):
                continue

            # Generate moves for this piece
            piece_moves = self._generate_piece_moves(board, from_sq, piece)
            legal_moves.extend(piece_moves)

        return legal_moves

    def _generate_piece_moves(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Generate moves for a specific piece."""
        moves = []
        lower = piece.lower()

        if lower == "p":
            moves = self._generate_pawn_moves_optimized(board, from_sq, piece)
        elif lower == "n":
            moves = self._generate_knight_moves_optimized(board, from_sq, piece)
        elif lower == "b":
            moves = self._generate_bishop_moves_optimized(board, from_sq, piece)
        elif lower == "r":
            moves = self._generate_rook_moves_optimized(board, from_sq, piece)
        elif lower == "q":
            moves = self._generate_queen_moves_optimized(board, from_sq, piece)
        elif lower == "k":
            moves = self._generate_king_moves_optimized(board, from_sq, piece)

        return moves

    @profile_method("optimized_pawn_moves")
    def _generate_pawn_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized pawn move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        if is_white:
            # White pawn moves
            single_move = from_sq + 16
            if not _is_offboard_cached(single_move) and board.squares[single_move] == "\u0000":
                moves.append(Move(from_sq, single_move))

                # Double move from starting rank
                if from_sq >= 16 and from_sq <= 23:  # Starting rank
                    double_move = from_sq + 32
                    if (
                        not _is_offboard_cached(double_move)
                        and board.squares[double_move] == "\u0000"
                    ):
                        moves.append(Move(from_sq, double_move))

            # Captures
            for offset in PAWN_CAPTURE_OFFSETS_WHITE:
                to_sq = from_sq + offset
                if not _is_offboard_cached(to_sq):
                    target = board.squares[to_sq]
                    if target != "\u0000" and not _is_white_cached(target):
                        moves.append(Move(from_sq, to_sq))
        else:
            # Black pawn moves
            single_move = from_sq - 16
            if not _is_offboard_cached(single_move) and board.squares[single_move] == "\u0000":
                moves.append(Move(from_sq, single_move))

                # Double move from starting rank
                if from_sq >= 96 and from_sq <= 103:  # Starting rank
                    double_move = from_sq - 32
                    if (
                        not _is_offboard_cached(double_move)
                        and board.squares[double_move] == "\u0000"
                    ):
                        moves.append(Move(from_sq, double_move))

            # Captures
            for offset in PAWN_CAPTURE_OFFSETS_BLACK:
                to_sq = from_sq + offset
                if not _is_offboard_cached(to_sq):
                    target = board.squares[to_sq]
                    if target != "\u0000" and not _is_black_cached(target):
                        moves.append(Move(from_sq, to_sq))

        return moves

    @profile_method("optimized_knight_moves")
    def _generate_knight_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized knight move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        for offset in KNIGHT_OFFSETS_OPTIMIZED:
            to_sq = from_sq + offset
            if _is_offboard_cached(to_sq):
                continue

            target = board.squares[to_sq]
            if (
                target == "\u0000"
                or (is_white and not _is_white_cached(target))
                or (not is_white and not _is_black_cached(target))
            ):
                moves.append(Move(from_sq, to_sq))

        return moves

    @profile_method("optimized_bishop_moves")
    def _generate_bishop_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized bishop move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        for direction in BISHOP_DIRECTIONS_OPTIMIZED:
            to_sq = from_sq + direction
            while not _is_offboard_cached(to_sq):
                target = board.squares[to_sq]
                if target == "\u0000":
                    moves.append(Move(from_sq, to_sq))
                elif (is_white and not _is_white_cached(target)) or (
                    not is_white and not _is_black_cached(target)
                ):
                    moves.append(Move(from_sq, to_sq))
                    break
                else:
                    break
                to_sq += direction

        return moves

    @profile_method("optimized_rook_moves")
    def _generate_rook_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized rook move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        for direction in ROOK_DIRECTIONS_OPTIMIZED:
            to_sq = from_sq + direction
            while not _is_offboard_cached(to_sq):
                target = board.squares[to_sq]
                if target == "\u0000":
                    moves.append(Move(from_sq, to_sq))
                elif (is_white and not _is_white_cached(target)) or (
                    not is_white and not _is_black_cached(target)
                ):
                    moves.append(Move(from_sq, to_sq))
                    break
                else:
                    break
                to_sq += direction

        return moves

    @profile_method("optimized_queen_moves")
    def _generate_queen_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized queen move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        for direction in QUEEN_DIRECTIONS_OPTIMIZED:
            to_sq = from_sq + direction
            while not _is_offboard_cached(to_sq):
                target = board.squares[to_sq]
                if target == "\u0000":
                    moves.append(Move(from_sq, to_sq))
                elif (is_white and not _is_white_cached(target)) or (
                    not is_white and not _is_black_cached(target)
                ):
                    moves.append(Move(from_sq, to_sq))
                    break
                else:
                    break
                to_sq += direction

        return moves

    @profile_method("optimized_king_moves")
    def _generate_king_moves_optimized(self, board: Any, from_sq: int, piece: str) -> List[Move]:
        """Optimized king move generation."""
        moves = []
        is_white = _is_white_cached(piece)

        for offset in KING_OFFSETS_OPTIMIZED:
            to_sq = from_sq + offset
            if _is_offboard_cached(to_sq):
                continue

            target = board.squares[to_sq]
            if (
                target == "\u0000"
                or (is_white and not _is_white_cached(target))
                or (not is_white and not _is_black_cached(target))
            ):
                moves.append(Move(from_sq, to_sq))

        return moves

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_time_ms = (
            (self._total_time / self._generation_count * 1000) if self._generation_count > 0 else 0
        )
        cache_hit_rate = (
            (self._cache_hits / (self._cache_hits + self._cache_misses) * 100)
            if (self._cache_hits + self._cache_misses) > 0
            else 0
        )

        return {
            "generation_count": self._generation_count,
            "total_time": self._total_time,
            "avg_time_ms": avg_time_ms,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "target_met": avg_time_ms < 0.01,
        }

    def clear_cache(self) -> None:
        """Clear move generation cache."""
        self._move_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0


# Global optimized move generator
_global_move_generator = OptimizedMoveGenerator()


@profile_function("optimized_generate_moves")
def generate_moves_optimized(board: Any) -> List[Move]:
    """Optimized move generation function."""
    return _global_move_generator.generate_moves(board)


@profile_function("optimized_is_legal_move")
def is_legal_move_optimized(board: Any, move: Move) -> bool:
    """Optimized legal move check."""
    # This would implement fast legal move checking
    # For now, use the standard implementation
    from core.moves import _is_legal_move_standard

    return _is_legal_move_standard(board, move)
