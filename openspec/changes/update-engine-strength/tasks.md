## 1. Implementation
- [x] 1.1 Add TT interface and 0x88 Zobrist hashing utility (reuse-safe)
- [x] 1.2 Integrate TT lookup/store into `search/mcts.py` selection/expansion
- [x] 1.3 Add heuristic rollout cutoff using evaluation thresholds
- [x] 1.4 Expand evaluation: hanging piece, threat bonus, check/escape urgency
- [x] 1.5 Add mate-distance scoring and propagation in backprop
- [x] 1.6 Update UCI `go` handling to stabilize PV near deadline

## 2. Validation
- [x] 2.1 Update/add tests in `tests/test_mcts.py` and `tests/test_mcts_integration_eval.py`
- [x] 2.2 Add evaluation unit tests for new heuristics in `tests/test_heuristics.py`
- [ ] 2.3 Add performance guard in `tests/test_performance_regression.py` (no worse than +10% runtime)

## 3. Tooling & Docs
- [x] 3.1 Document new options (TT on/off, rollout threshold) in README and `zyra_engine.sh.uci_options`
- [ ] 3.2 Add OpenSpec validation step to CI script (local doc)
