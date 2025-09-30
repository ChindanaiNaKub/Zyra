"""Move generation and validation.

This module provides pseudolegal and legal move generation for a 0x88 board,
as well as minimal make/unmake operations required for legality filtering and
perft. Special rules (castling, en passant, promotions) are stubbed or
handled minimally where straightforward; full correctness will evolve with
later tasks.
"""

from typing import Any, List, Optional, Tuple

# Offsets for piece movement in 0x88 representation
KNIGHT_OFFSETS = [31, 33, 14, 18, -31, -33, -14, -18]
BISHOP_DIRECTIONS = [15, 17, -15, -17]
ROOK_DIRECTIONS = [16, -16, 1, -1]
QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS
KING_OFFSETS = [1, -1, 16, -16, 15, 17, -15, -17]


class Move:
    """Represents a chess move."""

    def __init__(self, from_square: int, to_square: int, promotion: Optional[str] = None) -> None:
        self.from_square = from_square
        self.to_square = to_square
        self.promotion = promotion  # e.g., 'q', 'r', 'b', 'n' for UCI

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Move):
            return False
        return (
            self.from_square == other.from_square
            and self.to_square == other.to_square
            and self.promotion == other.promotion
        )

    def __hash__(self) -> int:
        return hash((self.from_square, self.to_square, self.promotion))

    def __repr__(self) -> str:
        return f"Move(from={self.from_square}, to={self.to_square}, promo={self.promotion})"


def _is_offboard(index: int) -> bool:
    return (index & 0x88) != 0


def _is_white(piece: str) -> bool:
    return piece.isupper()


def _is_black(piece: str) -> bool:
    return piece.islower()


def _same_color(p1: str, p2: str) -> bool:
    if p1 == "\u0000" or p2 == "\u0000":
        return False
    return (_is_white(p1) and _is_white(p2)) or (_is_black(p1) and _is_black(p2))


def _generate_pseudolegal(board: Any) -> List[Move]:
    moves: List[Move] = []
    side_white = board.side_to_move == "w"

    for from_sq in range(128):
        if _is_offboard(from_sq):
            continue
        piece = board.squares[from_sq]
        if piece == "\u0000":
            continue
        if side_white and not _is_white(piece):
            continue
        if not side_white and not _is_black(piece):
            continue

        lower = piece.lower()
        if lower == "p":
            _gen_pawn_moves(board, from_sq, piece, moves)
        elif lower == "n":
            _gen_step_moves(board, from_sq, piece, KNIGHT_OFFSETS, sliding=False, moves=moves)
        elif lower == "b":
            _gen_step_moves(board, from_sq, piece, BISHOP_DIRECTIONS, sliding=True, moves=moves)
        elif lower == "r":
            _gen_step_moves(board, from_sq, piece, ROOK_DIRECTIONS, sliding=True, moves=moves)
        elif lower == "q":
            _gen_step_moves(board, from_sq, piece, QUEEN_DIRECTIONS, sliding=True, moves=moves)
        elif lower == "k":
            _gen_step_moves(board, from_sq, piece, KING_OFFSETS, sliding=False, moves=moves)
            _gen_castling_moves(board, from_sq, piece, moves)

    return moves


def _gen_step_moves(
    board: Any, from_sq: int, piece: str, offsets: List[int], *, sliding: bool, moves: List[Move]
) -> None:
    for offset in offsets:
        to_sq = from_sq + offset
        if _is_offboard(to_sq):
            continue
        dest_piece = board.squares[to_sq]
        if dest_piece != "\u0000" and _same_color(piece, dest_piece):
            continue
        moves.append(Move(from_sq, to_sq))
        if sliding:
            # Extend along ray until blocked
            step = offset
            while True:
                to_sq += step
                if _is_offboard(to_sq):
                    break
                dest_piece = board.squares[to_sq]
                if dest_piece != "\u0000" and _same_color(piece, dest_piece):
                    break
                moves.append(Move(from_sq, to_sq))
                if dest_piece != "\u0000":
                    break


def _gen_pawn_moves(board: Any, from_sq: int, piece: str, moves: List[Move]) -> None:
    is_white = _is_white(piece)
    forward = -16 if is_white else 16
    start_rank_from_top = 6 if is_white else 1  # rank 2 for white, rank 7 for black

    one_ahead = from_sq + forward
    if not _is_offboard(one_ahead) and board.squares[one_ahead] == "\u0000":
        _append_pawn_move_with_promo(moves, from_sq, one_ahead, is_white, one_ahead)
        # Double push
        rank_from_top = (from_sq >> 4) & 0x7
        two_ahead = from_sq + 2 * forward
        if rank_from_top == start_rank_from_top and board.squares[two_ahead] == "\u0000":
            moves.append(Move(from_sq, two_ahead))

    # Captures
    for diag in [-1, 1]:
        to_sq = from_sq + forward + diag
        if _is_offboard(to_sq):
            continue
        dest_piece = board.squares[to_sq]
        if dest_piece != "\u0000" and not _same_color(piece, dest_piece):
            _append_pawn_move_with_promo(moves, from_sq, to_sq, is_white, to_sq)
        # En passant capture
        if board.ep_square is not None and to_sq == board.ep_square:
            _append_pawn_move_with_promo(moves, from_sq, to_sq, is_white, to_sq)


def _gen_castling_moves(board: Any, from_sq: int, piece: str, moves: List[Move]) -> None:
    """Generate castling moves if conditions are met."""
    is_white = _is_white(piece)
    castling_rights = board.castling

    # Check if king is in check
    if _square_attacked_by(board, from_sq, by_white=not is_white):
        return

    # Kingside castling
    if (is_white and "K" in castling_rights) or (not is_white and "k" in castling_rights):
        kingside_rook_sq = from_sq + 3  # e1->h1 or e8->h8
        if (
            not _is_offboard(kingside_rook_sq)
            and board.squares[kingside_rook_sq] == ("R" if is_white else "r")
            and board.squares[from_sq + 1] == "\u0000"
            and board.squares[from_sq + 2] == "\u0000"
            and not _square_attacked_by(board, from_sq + 1, by_white=not is_white)
            and not _square_attacked_by(board, from_sq + 2, by_white=not is_white)
        ):
            moves.append(Move(from_sq, from_sq + 2, promotion="O-O"))  # Special marker for castling

    # Queenside castling
    if (is_white and "Q" in castling_rights) or (not is_white and "q" in castling_rights):
        queenside_rook_sq = from_sq - 4  # e1->a1 or e8->a8
        if (
            not _is_offboard(queenside_rook_sq)
            and board.squares[queenside_rook_sq] == ("R" if is_white else "r")
            and board.squares[from_sq - 1] == "\u0000"
            and board.squares[from_sq - 2] == "\u0000"
            and board.squares[from_sq - 3] == "\u0000"
            and not _square_attacked_by(board, from_sq - 1, by_white=not is_white)
            and not _square_attacked_by(board, from_sq - 2, by_white=not is_white)
        ):
            moves.append(
                Move(from_sq, from_sq - 2, promotion="O-O-O")
            )  # Special marker for castling


def _append_pawn_move_with_promo(
    moves: List[Move], from_sq: int, to_sq: int, is_white: bool, dest_sq: int
) -> None:
    target_rank_from_top = (dest_sq >> 4) & 0x7
    if target_rank_from_top == 0 or target_rank_from_top == 7:
        # Add promotion choices; minimal set with queen to keep early flow simple
        moves.append(Move(from_sq, to_sq, promotion="q"))
    else:
        moves.append(Move(from_sq, to_sq))


def _locate_king(board: Any, white: bool) -> Optional[int]:
    target = "K" if white else "k"
    for i in range(128):
        if _is_offboard(i):
            continue
        if board.squares[i] == target:
            return i
    return None


def _square_attacked_by(board: Any, sq: int, by_white: bool) -> bool:
    # Knights
    for off in KNIGHT_OFFSETS:
        t = sq + off
        if _is_offboard(t):
            continue
        p = board.squares[t]
        if p != "\u0000" and (p == ("N" if by_white else "n")):
            return True

    # Kings
    for off in KING_OFFSETS:
        t = sq + off
        if _is_offboard(t):
            continue
        p = board.squares[t]
        if p != "\u0000" and (p == ("K" if by_white else "k")):
            return True

    # Pawns (attacks are reversed relative to movement)
    if by_white:
        for diag in [-15, -17]:
            t = sq + diag
            if not _is_offboard(t) and board.squares[t] == "P":
                return True
    else:
        for diag in [15, 17]:
            t = sq + diag
            if not _is_offboard(t) and board.squares[t] == "p":
                return True

    # Sliding pieces
    # Bishops/Queens on diagonals
    for d in BISHOP_DIRECTIONS:
        t = sq + d
        while not _is_offboard(t):
            p = board.squares[t]
            if p != "\u0000":
                if by_white and (p == "B" or p == "Q"):
                    return True
                if not by_white and (p == "b" or p == "q"):
                    return True
                break
            t += d
    # Rooks/Queens on files/ranks
    for d in ROOK_DIRECTIONS:
        t = sq + d
        while not _is_offboard(t):
            p = board.squares[t]
            if p != "\u0000":
                if by_white and (p == "R" or p == "Q"):
                    return True
                if not by_white and (p == "r" or p == "q"):
                    return True
                break
            t += d

    return False


def _make_move(board: Any, move: Move) -> Tuple[str, Optional[int], Optional[str], int, int]:
    """Apply a move on the board. Returns (captured_piece, ep_square_prev, rook_from_sq, halfmove_prev, fullmove_prev).

    Handles castling, en passant, and promotion.
    """
    captured = board.squares[move.to_square]
    rook_from_sq = None
    halfmove_prev = board.halfmove_clock
    fullmove_prev = board.fullmove_number

    # Handle castling
    if move.promotion == "O-O":  # Kingside castling
        rook_from_sq = move.from_square + 3  # h-file
        rook_to_sq = move.from_square + 1  # f-file
        board.squares[rook_to_sq] = board.squares[rook_from_sq]
        board.squares[rook_from_sq] = "\u0000"
    elif move.promotion == "O-O-O":  # Queenside castling
        rook_from_sq = move.from_square - 4  # a-file
        rook_to_sq = move.from_square - 1  # d-file
        board.squares[rook_to_sq] = board.squares[rook_from_sq]
        board.squares[rook_from_sq] = "\u0000"

    # Handle en passant capture
    if (
        board.ep_square is not None
        and move.to_square == board.ep_square
        and board.squares[move.from_square].lower() == "p"
    ):
        # Remove the captured pawn (behind the destination square)
        ep_capture_sq = move.to_square + (16 if board.side_to_move == "w" else -16)
        board.squares[ep_capture_sq] = "\u0000"
        captured = "P" if board.side_to_move == "b" else "p"  # The captured pawn

    # Regular move
    board.squares[move.to_square] = board.squares[move.from_square]
    board.squares[move.from_square] = "\u0000"

    # Handle promotion (replace pawn with promoted piece of correct color)
    if move.promotion and move.promotion not in ["O-O", "O-O-O"]:
        promoted = move.promotion
        if board.side_to_move == "w":
            board.squares[move.to_square] = promoted.upper()
        else:
            board.squares[move.to_square] = promoted.lower()

    ep_prev = board.ep_square
    board.ep_square = None

    # Set en passant square for double pawn pushes
    if board.squares[move.to_square].lower() == "p":
        if (
            board.side_to_move == "w"
            and (move.from_square >> 4) == 6
            and (move.to_square >> 4) == 4
        ):
            board.ep_square = move.to_square + 16  # Behind the pawn
        elif (
            board.side_to_move == "b"
            and (move.from_square >> 4) == 1
            and (move.to_square >> 4) == 3
        ):
            board.ep_square = move.to_square - 16  # Behind the pawn

    # Update move counters
    if captured != "\u0000" or board.squares[move.to_square].lower() == "p":
        board.halfmove_clock = 0  # Reset on capture or pawn move
    else:
        board.halfmove_clock += 1

    if board.side_to_move == "b":  # After white's move
        board.fullmove_number += 1

    # flip side to move
    board.side_to_move = "b" if board.side_to_move == "w" else "w"
    return captured, ep_prev, rook_from_sq, halfmove_prev, fullmove_prev


def _unmake_move(
    board: Any,
    move: Move,
    captured: str,
    ep_prev: Optional[int],
    moved_piece: Optional[str] = None,
    rook_from_sq: Optional[int] = None,
    halfmove_prev: Optional[int] = None,
    fullmove_prev: Optional[int] = None,
) -> None:
    # flip back side
    board.side_to_move = "b" if board.side_to_move == "w" else "w"

    # Handle castling unmake
    if move.promotion == "O-O":  # Kingside castling
        rook_to_sq = move.from_square + 1  # f-file
        rook_from_sq = move.from_square + 3  # h-file
        board.squares[rook_from_sq] = board.squares[rook_to_sq]
        board.squares[rook_to_sq] = "\u0000"
    elif move.promotion == "O-O-O":  # Queenside castling
        rook_to_sq = move.from_square - 1  # d-file
        rook_from_sq = move.from_square - 4  # a-file
        board.squares[rook_from_sq] = board.squares[rook_to_sq]
        board.squares[rook_to_sq] = "\u0000"

    # Handle en passant unmake
    if (
        board.ep_square is not None
        and move.to_square == board.ep_square
        and moved_piece
        and moved_piece.lower() == "p"
    ):
        # Restore the captured pawn
        ep_capture_sq = move.to_square + (16 if board.side_to_move == "w" else -16)
        board.squares[ep_capture_sq] = captured

    # Regular move unmake
    piece = board.squares[move.to_square]
    if move.promotion and move.promotion not in ["O-O", "O-O-O"]:
        # Restore pawn color according to side that originally moved
        if board.side_to_move == "w":
            piece = "P"
        else:
            piece = "p"
    board.squares[move.from_square] = piece if moved_piece is None else moved_piece
    board.squares[move.to_square] = captured
    board.ep_square = ep_prev

    # Restore move counters
    if halfmove_prev is not None:
        board.halfmove_clock = halfmove_prev
    if fullmove_prev is not None:
        board.fullmove_number = fullmove_prev


def generate_moves(board: Any) -> List[Move]:
    """Generate all legal moves for the current position."""
    if board is None:
        return []
    legal: List[Move] = []
    for mv in _generate_pseudolegal(board):
        moved_piece = board.squares[mv.from_square]
        captured, ep_prev, rook_from_sq, halfmove_prev, fullmove_prev = _make_move(board, mv)
        king_sq = _locate_king(
            board, white=(board.side_to_move == "b")
        )  # after move, opponent to move
        in_check = False
        if king_sq is not None:
            in_check = _square_attacked_by(board, king_sq, by_white=(board.side_to_move == "w"))
        _unmake_move(
            board,
            mv,
            captured,
            ep_prev,
            moved_piece=moved_piece,
            rook_from_sq=rook_from_sq,
            halfmove_prev=halfmove_prev,
            fullmove_prev=fullmove_prev,
        )
        if not in_check:
            legal.append(mv)
    return legal


def is_legal_move(board: Any, move: Move) -> bool:
    """Check if a move is legal in the current position."""
    if board is None:
        return False
    for mv in generate_moves(board):
        if mv.from_square == move.from_square and mv.to_square == move.to_square:
            # If promotion is specified, match it as well when present
            if (mv.promotion or move.promotion) and mv.promotion != move.promotion:
                continue
            return True
    return False


def parse_uci_move(board: Any, uci: str) -> Move:
    """Parse a UCI move like 'e2e4' or 'e7e8q' into a Move object."""
    from core.board import square_to_index  # local import to avoid cycles

    uci = uci.strip()
    from_sq = square_to_index(uci[0:2])
    to_sq = square_to_index(uci[2:4])
    promo = uci[4].lower() if len(uci) > 4 else None
    return Move(from_sq, to_sq, promo)


def make_move(
    board: Any, move: Move
) -> Tuple[str, Optional[int], Optional[str], Optional[int], int, int]:
    """Public make move that returns data needed for unmake.

    Returns (captured_piece, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev).
    """
    moved_piece = board.squares[move.from_square]
    captured, ep_prev, rook_from_sq, halfmove_prev, fullmove_prev = _make_move(board, move)
    return captured, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev


def unmake_move(
    board: Any,
    move: Move,
    captured: str,
    ep_prev: Optional[int],
    moved_piece: Optional[str],
    rook_from_sq: Optional[int],
    halfmove_prev: int,
    fullmove_prev: int,
) -> None:
    _unmake_move(
        board,
        move,
        captured,
        ep_prev,
        moved_piece=moved_piece,
        rook_from_sq=rook_from_sq,
        halfmove_prev=halfmove_prev,
        fullmove_prev=fullmove_prev,
    )


def perft(board: Any, depth: int) -> int:
    """Compute perft to the given depth using legal move generation."""
    if depth == 0:
        return 1
    nodes = 0
    for mv in generate_moves(board):
        captured, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev = make_move(
            board, mv
        )
        nodes += perft(board, depth - 1)
        unmake_move(
            board, mv, captured, ep_prev, moved_piece, rook_from_sq, halfmove_prev, fullmove_prev
        )
    return nodes


def is_in_check(board: Any) -> bool:
    """Check if the current side to move is in check."""
    white_to_move = board.side_to_move == "w"
    king_sq = _locate_king(board, white=white_to_move)
    if king_sq is None:
        return False
    return _square_attacked_by(board, king_sq, by_white=not white_to_move)


def is_checkmate(board: Any) -> bool:
    """Check if the current position is checkmate."""
    return is_in_check(board) and len(generate_moves(board)) == 0


def is_stalemate(board: Any) -> bool:
    """Check if the current position is stalemate."""
    return not is_in_check(board) and len(generate_moves(board)) == 0


def is_fifty_move_draw(board: Any) -> bool:
    """Check if the position is drawn by the fifty-move rule."""
    return board.halfmove_clock >= 100


def is_threefold_repetition(board: Any, position_history: List[str]) -> bool:
    """Check if the current position has occurred 3 times (simple implementation).

    Args:
        board: Current board position
        position_history: List of FEN strings representing previous positions

    Returns:
        True if the current position has occurred 3 or more times
    """
    current_fen = board.to_fen()
    count = sum(1 for fen in position_history if fen == current_fen)
    return count >= 2  # Current position + 2 previous occurrences = 3 total


def get_game_result(board: Any, position_history: List[str]) -> str:
    """Determine the game result.

    Returns:
        "checkmate" if checkmate
        "stalemate" if stalemate
        "fifty-move" if fifty-move draw
        "repetition" if threefold repetition
        "ongoing" if game continues
    """
    if is_checkmate(board):
        return "checkmate"
    elif is_stalemate(board):
        return "stalemate"
    elif is_fifty_move_draw(board):
        return "fifty-move"
    elif is_threefold_repetition(board, position_history):
        return "repetition"
    else:
        return "ongoing"


# ============================================================================
# PERFORMANCE OPTIMIZATION: Use optimized versions when available
# ============================================================================
try:
    from core.moves_optimized import (
        OptimizedMoveGenerator,
        generate_moves_optimized,
        is_legal_move_optimized,
    )

    # Override standard functions with optimized versions for better performance
    _generate_moves_standard = generate_moves
    _is_legal_move_standard = is_legal_move

    generate_moves = generate_moves_optimized  # type: ignore
    is_legal_move = is_legal_move_optimized  # type: ignore

    # Export the optimized generator
    __all__ = [
        "Move",
        "generate_moves",
        "is_legal_move",
        "make_move",
        "unmake_move",
        "parse_uci_move",
        "perft",
        "OptimizedMoveGenerator",
    ]

except ImportError:
    # Optimized version not available, use standard implementation
    __all__ = [
        "Move",
        "generate_moves",
        "is_legal_move",
        "make_move",
        "unmake_move",
        "parse_uci_move",
        "perft",
    ]
