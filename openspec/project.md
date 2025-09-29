# Project Context

## Purpose
Build an original chess engine with a distinct, explainable playing style. The engine prioritizes unique evaluation heuristics and experimental search over raw strength. Target users are developers and chess players seeking novelty and insight rather than top-tier ELO.

## Tech Stack
- Primary language: Python (prototype)
- Future optimization: Rust or C++ (select performance-critical modules)
- Board representation: Mailbox 0x88
- Search: Monte Carlo Tree Search (MCTS) or Beam Search with heuristic pruning
- Interface: UCI protocol and CLI tools
- OS targets: Linux, Windows, macOS

## Project Conventions

### Code Style
Python: PEP 8, black formatting (line length 100), isort for imports, mypy for optional typing in core modules.
Rust: rustfmt defaults, clippy clean on warning level.
Naming: descriptive, intention-revealing identifiers (no abbreviations), verb-based function names, noun-based types/values.
Error handling: prefer explicit Result/Option (Rust) and raised exceptions with precise messages (Python). Avoid silent failures.
Documentation: module docstrings for subsystems; function docstrings for public APIs; short comments only where non-obvious rationale exists.

### Architecture Patterns
- Modular engine with clear subsystems:
  - Core: board, move generation, rules (castling, en passant, promotions)
  - Search: MCTS/Beam implementations with playout controls and stochastic exploration
  - Evaluation: material, positional heuristics, personality/style weights
  - Interfaces: UCI adapter and CLI runner
- Data flow: deterministic core logic; randomness isolated to search exploration seeds.
- Config-driven styles: style profiles (aggressive/defensive/experimental) defined via tunable weights.
- Simplicity-first: readability over micro-optimizations; upgrade hotspots only when profiled.

### Testing Strategy
- Move generator: exhaustive unit tests for legality rules; perft-style node count tests for reference positions.
- Search: behavioral tests ensuring playout limits, stochastic bounds, and beam width respected.
- Evaluation: unit tests for material and positional terms; golden-file baselines for style-weight outputs.
- Integration: UCI protocol conformance tests; CLI end-to-end game smoke tests.
- Regression: style profile snapshots to detect drift in engine personality.

### Git Workflow
- Branching: trunk-based with short-lived feature branches; PRs required before merge.
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`). Squash on merge.
- Reviews: require at least one review; CI must pass tests and formatting.

## Domain Context
- Classical chess only (no variants) in initial release.
- Full legality: castling rights tracking, en passant squares, promotion handling.
- Engine personality is a first-class goal; strength target is moderate (≈1500–1800 Elo vs online bots).
- Board representation favors clarity (0x88/mailbox) over bitboard performance for v1.

## Important Constraints
- Do not integrate large neural networks or massive opening books/tablebases in v1.
- Cross-platform compatibility required (Linux, Windows, macOS).
- Performance target: ~10–20k nodes/sec on a modern laptop for baseline search.
- Emphasis on explainability and configurability over peak ELO.

## External Dependencies
- UCI-compatible GUIs for testing (e.g., Cute Chess, Arena) via the UCI protocol.
- Python 3.11+ runtime for the prototype.
- Optional: toolchains for Rust/C++ if/when optimizing critical paths.
