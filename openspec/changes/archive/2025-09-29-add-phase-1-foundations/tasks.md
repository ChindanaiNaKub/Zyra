## 1. Engine Core
- [x] 1.1 Implement 0x88 board with state (pieces, colors, rights, ep, clocks)
- [x] 1.2 FEN import/export roundtrip with normalization
- [x] 1.3 Pseudolegal move gen per piece; handle promotions
- [x] 1.4 Legality filter; king safety validation
- [x] 1.5 Special rules: castling and en passant
- [x] 1.6 Make/unmake with reversible state stack
- [x] 1.7 Rules: check, checkmate, stalemate, fifty-move, repetition baseline
- [x] 1.8 Perft for reference positions; document expected counts

## 2. Interfaces: UCI
- [x] 2.1 Support `uci`, `isready`, `ucinewgame`, `position`, `go`, `stop`, `quit`
- [x] 2.2 Legal random move path when no search configured

## 3. CLI
- [x] 3.1 CLI runner: load FEN/startpos, apply moves, print board
- [x] 3.2 CLI perft command `--perft N`

## 4. Tests & Validation
- [x] 4.1 Unit tests for board and moves
- [x] 4.2 Perft correctness tests (depth N)
- [x] 4.3 UCI smoke tests (id, readyok, bestmove)
- [x] 4.4 CLI smoke tests
