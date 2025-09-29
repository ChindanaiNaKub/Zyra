# Build Plan and Todo List

High-level, actionable tasks derived from `openspec/project.md` and `prd.md`. Use this as the working checklist; keep items checked off as you progress.

## Global Setup
- [ ] Initialize repository structure and tooling
  - [ ] Python 3.11+ interpreter available
  - [ ] Add formatter (`black` with line length 100) and `isort`
  - [ ] Add type checking (`mypy`) for core modules
  - [ ] Configure lint/format pre-commit hooks
  - [ ] Set up trunk-based branching and CI with tests + formatting
- [ ] Project scaffolding
  - [ ] Create modules: `core/`, `search/`, `eval/`, `interfaces/`, `cli/`, `tests/`
  - [ ] Add `pyproject.toml` for tool configs (black, isort, mypy)
  - [ ] Add `README.md` with quick start
  - [ ] Add `STYLE_PROFILES.md` for personality weights

## Phase 1: Foundations (Board + Rules + I/O)
- [ ] Implement 0x88 mailbox board representation
  - [ ] Board state: pieces, colors, side-to-move, castling rights, ep square, halfmove/fullmove counters
  - [ ] FEN import/export
- [ ] Move generation (legal moves)
  - [ ] Pseudolegal moves per piece
  - [ ] Legality filter (king not in check after move)
  - [ ] Special rules: castling, en passant, promotions
  - [ ] Make/unmake move with reversible state
- [ ] Rules engine and validation
  - [ ] Check, checkmate, stalemate detection
  - [ ] Fifty-move rule, repetition counters (simple hash or history)
- [ ] Perft tests (correctness baseline)
  - [ ] Add reference perft positions and expected node counts
  - [ ] Target: match known counts up to depth N (document N)
- [ ] UCI interface (initial)
  - [ ] `uci`, `isready`, `ucinewgame`, `position`, `go`, `stop`, `quit`
  - [ ] Play legal random move for smoke tests
- [ ] CLI test runner
  - [ ] Load FEN / startpos, make moves, run perft, print board

## Phase 2: Search (MCTS or Beam)
- [ ] Select and scaffold search strategy
  - [ ] Choose default: MCTS (with capped playouts)
  - [ ] Alternative: Beam Search with heuristic pruning (behind flag)
- [ ] Core search loop
  - [ ] Node structure with prior/visits/value (MCTS) or beam scoring
  - [ ] Playout policy with stochastic exploration
  - [ ] Time/node limits; seeds for reproducibility
- [ ] Move ordering & pruning
  - [ ] Heuristic ordering (captures, checks, promotions)
  - [ ] Style-aware ordering hook (ties into eval weights)
- [ ] Integration with UCI `go`
  - [ ] Respect movetime, nodes, depth-like constraints where applicable
  - [ ] Best move reporting, pondering stub
- [ ] Search tests
  - [ ] Deterministic behavior with fixed seeds
  - [ ] Bounds respected (playouts, beam width)

## Phase 3: Evaluation (Explainable Heuristics)
- [ ] Material evaluation with twists
  - [ ] Base material values
  - [ ] Bonus for attacking/sacrificial motifs
  - [ ] Penalty for retreating or loss of initiative
- [ ] Positional heuristics
  - [ ] King safety, center control, rook on open/semi-open file
  - [ ] Mobility and piece-square considerations (simple, explainable tables)
- [ ] Style profiles (config-driven)
  - [ ] Define `aggressive`, `defensive`, `experimental` weight sets
  - [ ] Config parsing and runtime selection
  - [ ] Logging of term breakdown for explainability
- [ ] Evaluation tests
  - [ ] Unit tests per term
  - [ ] Golden baselines for style-weight outputs

## Phase 4: Styles & Testing (Behavioral Validation)
- [ ] Integrate style profiles into search
  - [ ] Influence move ordering, playout policy, and eval blending
- [ ] Behavioral tests
  - [ ] Ensure variety with stochastic exploration (bounded randomness)
  - [ ] Verify style deltas (aggressive vs defensive move preferences)
- [ ] Regression safeguards
  - [ ] Snapshot style outputs to detect drift
  - [ ] End-to-end smoke games (self-play, depth/node limited)

## Phase 5: Packaging & Interfaces
- [ ] UCI conformance
  - [ ] Validate against common GUIs (Cute Chess, Arena)
  - [ ] Long-running stability test (play full games without crash)
- [ ] CLI tooling
  - [ ] Commands: perft, play, analyze, profile-style
- [ ] Distribution
  - [ ] Build simple binary or entrypoint script
  - [ ] Cross-platform notes (Linux/Windows/macOS)
  - [ ] Publish with documentation

## Performance Targets (from specs)
- [ ] Achieve ~10–20k nodes/sec baseline (profiling-guided improvements only)
- [ ] Keep solution lightweight; avoid large nets/books/tablebases

## Success Metrics (from PRD)
- [ ] Plays legal, complete games without crashes
- [ ] Distinct personality vs Stockfish (observable in ~50 games)
- [ ] ≥1500 Elo vs online bots (indicative target)
- [ ] Users can configure style preferences

## Documentation & Explainability
- [ ] Module docstrings for subsystems; function docstrings for public APIs
- [ ] Explain evaluation contributions in logs (term-by-term)
- [ ] Record seeds and config for reproducible runs

## Nice-to-Have (Optional/Stretch)
- [ ] Visualize search tree or playout statistics
- [ ] Simple opening heuristics (no large books)
- [ ] Export game PGNs with annotations from eval terms

## Risk Mitigations
- [ ] If strength too low: tune style weights, refine playout policy
- [ ] Avoid deep premature optimization; profile hotspots first
- [ ] Keep randomness isolated; enable deterministic runs for tests
