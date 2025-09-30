#!/usr/bin/env python3
"""Debug script to understand to_fen generation."""

from core.board import Board


def debug_to_fen():
    print("=== to_fen Debug ===")

    # Create the position after e2e4 h7h5 moves
    board = Board()
    board.set_startpos()

    # Make e2e4
    from core.moves import make_move, parse_uci_move

    move1 = parse_uci_move(board, "e2e4")
    make_move(board, move1)
    print(f"After e2e4: {board.to_fen()}")

    # Make h7h5
    move2 = parse_uci_move(board, "h7h5")
    make_move(board, move2)
    print(f"After h7h5: {board.to_fen()}")

    # Now let's manually check what to_fen is doing
    print("\n=== Manual to_fen analysis ===")
    rank_strs = []
    for rank_idx_from_top in range(8):
        print(f"\nRank {rank_idx_from_top} (from top):")
        empties = 0
        parts = []
        for file_idx in range(8):
            idx = (rank_idx_from_top << 4) | file_idx
            piece = board.squares[idx]
            print(f"  {chr(97 + file_idx)}{8 - rank_idx_from_top}: index={idx}, piece='{piece}'")
            if piece == "\u0000":
                empties += 1
            else:
                if empties:
                    parts.append(str(empties))
                    empties = 0
                parts.append(piece)
        if empties:
            parts.append(str(empties))
        rank_str = "".join(parts)
        rank_strs.append(rank_str)
        print(f"  Rank string: '{rank_str}'")

    placement = "/".join(rank_strs)
    side = board.side_to_move
    castling = board.castling if board.castling != "" else "-"
    ep = "h6" if board.ep_square == 39 else "-"
    manual_fen = (
        f"{placement} {side} {castling} {ep} {board.halfmove_clock} {board.fullmove_number}"
    )
    print(f"\nManual FEN: {manual_fen}")
    print(f"Actual FEN: {board.to_fen()}")


if __name__ == "__main__":
    debug_to_fen()
