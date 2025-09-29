## Why

Phase 4 completes the chess engine's style system by integrating style profiles into search behavior, implementing comprehensive behavioral testing, and establishing regression safeguards. While Phases 1-3 provided the foundation (board representation, MCTS search, and evaluation heuristics), Phase 4 ensures that style profiles actually influence search decisions and that the system maintains behavioral consistency over time.

## What Changes

- **Enhanced style integration**: Style profiles will influence move ordering, playout policy, and evaluation blending in MCTS search
- **Behavioral testing framework**: Comprehensive tests to ensure style differentiation, stochastic exploration bounds, and move preference verification
- **Regression safeguards**: Style output snapshots and end-to-end smoke games to detect behavioral drift
- **Search policy enhancement**: Style-aware playout policies that maintain bounded randomness while expressing personality

## Impact

- Affected specs: `evaluation`, `search`
- Affected code: `search/mcts.py`, `eval/heuristics.py`, `tests/` (new behavioral tests)
- New capabilities: style-aware playout policies, behavioral validation framework, regression testing infrastructure
