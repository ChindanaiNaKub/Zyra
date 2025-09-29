"""Tests for board representation and state management."""

import pytest

from core.board import Board, index_to_square, square_to_index


class TestBoard:
    """Test cases for Board class."""

    def test_board_initialization(self) -> None:
        """Test that board initializes correctly."""
        board = Board()
        assert board is not None
        assert board.side_to_move == "w"
        assert board.castling == "-"
        assert board.ep_square is None
        assert board.halfmove_clock == 0
        assert board.fullmove_number == 1

    def test_square_conversion(self) -> None:
        """Test square to index and index to square conversion."""
        # Test corner squares
        assert square_to_index("a1") == 112  # bottom-left
        assert square_to_index("h1") == 119  # bottom-right
        assert square_to_index("a8") == 0  # top-left
        assert square_to_index("h8") == 7  # top-right
        assert square_to_index("e4") == 68  # center

        # Test reverse conversion
        assert index_to_square(112) == "a1"
        assert index_to_square(119) == "h1"
        assert index_to_square(0) == "a8"
        assert index_to_square(7) == "h8"
        assert index_to_square(68) == "e4"

    def test_set_startpos(self) -> None:
        """Test setting the standard starting position."""
        board = Board()
        board.set_startpos()

        # Check some key pieces
        assert board.squares[square_to_index("e1")] == "K"  # White king
        assert board.squares[square_to_index("e8")] == "k"  # Black king
        assert board.squares[square_to_index("d1")] == "Q"  # White queen
        assert board.squares[square_to_index("d8")] == "q"  # Black queen
        assert board.squares[square_to_index("e2")] == "P"  # White pawn
        assert board.squares[square_to_index("e7")] == "p"  # Black pawn

    def test_fen_loading_startpos(self) -> None:
        """Test FEN position loading with starting position."""
        board = Board()
        startpos_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board.load_fen(startpos_fen)

        assert board.side_to_move == "w"
        assert board.castling == "KQkq"
        assert board.ep_square is None
        assert board.halfmove_clock == 0
        assert board.fullmove_number == 1

        # Verify some pieces
        assert board.squares[square_to_index("e1")] == "K"
        assert board.squares[square_to_index("e8")] == "k"

    def test_fen_loading_custom_position(self) -> None:
        """Test FEN position loading with custom position."""
        board = Board()
        custom_fen = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
        board.load_fen(custom_fen)

        assert board.side_to_move == "w"
        assert board.castling == "kq"  # Only black kingside and queenside
        assert board.ep_square is None
        assert board.halfmove_clock == 0
        assert board.fullmove_number == 1

    def test_fen_loading_with_en_passant(self) -> None:
        """Test FEN position loading with en passant square."""
        board = Board()
        fen_with_ep = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        board.load_fen(fen_with_ep)

        assert board.side_to_move == "b"
        assert board.ep_square == square_to_index("e3")

    def test_fen_export_roundtrip(self) -> None:
        """Test FEN export and import roundtrip."""
        board = Board()
        original_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board.load_fen(original_fen)
        exported_fen = board.to_fen()

        # Should match exactly (FEN is normalized)
        assert exported_fen == original_fen

    def test_fen_export_custom_position(self) -> None:
        """Test FEN export with custom position."""
        board = Board()
        board.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")  # Empty board
        fen = board.to_fen()
        assert fen == "8/8/8/8/8/8/8/8 w - - 0 1"

    def test_fen_export_with_counters(self) -> None:
        """Test FEN export with move counters."""
        board = Board()
        board.load_fen("8/8/8/8/8/8/8/8 w - - 5 10")
        fen = board.to_fen()
        assert "5 10" in fen  # halfmove and fullmove counters

    def test_invalid_fen_handling(self) -> None:
        """Test handling of invalid FEN strings."""
        board = Board()

        # Too few fields (only placement)
        with pytest.raises(ValueError):
            board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

        # Invalid rank count
        with pytest.raises(ValueError):
            board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1")

        # Invalid square index (too many pieces in a rank)
        with pytest.raises(ValueError):
            board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNRR w KQkq - 0 1")
