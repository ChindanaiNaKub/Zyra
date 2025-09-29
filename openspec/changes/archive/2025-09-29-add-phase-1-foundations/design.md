## Context
Phase 1 introduces the core chess engine substrate with a 0x88 board, legal move generation, and minimal I/O for UCI and CLI. Simplicity and correctness take precedence over performance.

## Goals / Non-Goals
- Goals: Correctness, spec-driven implementation, testability, minimal viable UCI/CLI
- Non-Goals: Bitboards, advanced search, transposition tables, opening books

## Decisions
- Board: 0x88 mailbox for clarity and straightforward boundary checks
- State: Explicit fields for side-to-move, castling, ep square, halfmove/fullmove
- Make/Unmake: Stack-based reversible state for perft validation
- UCI: Minimal command handling; random legal move when no search config provided
- CLI: Single entrypoint supporting FEN/startpos, perft, and board printing

## Risks / Trade-offs
- 0x88 is slower than bitboards → acceptable for v1; revisit after perft correctness
- Random move can hide bugs → pair with perft and legality tests to ensure baseline correctness

## Migration Plan
- Implement engine-core features behind stable interfaces in `core/`
- Integrate UCI adapter using the core board and move generator
- Provide CLI wrapper for manual validation and CI smoke tests

## Open Questions
- Depth N for guaranteed perft agreement? (e.g., N=4 or N=5)
- SAN vs UCI move notation for CLI input? Prefer UCI for simplicity initially.
