## Why
Phase 1 foundations are missing from specs: board representation, move generation, rules, and minimal I/O. We need a formal spec change to drive implementation and validation.

## What Changes
- Add `engine-core` capability requirements for 0x88 board, FEN I/O, move generation, rules engine, and perft.
- Add `interfaces-uci` capability initial UCI command handling and legal random move for smoke tests.
- Add `cli` capability for a simple test runner to load FEN/startpos, make moves, run perft, and print board.

## Impact
- Affected specs: `engine-core`, `interfaces-uci`, `cli` (new capabilities)
- Affected code: `core/board.py`, `core/moves.py`, `interfaces/uci.py`, `cli/runner.py`, `tests/*`
