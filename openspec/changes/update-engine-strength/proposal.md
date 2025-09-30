## Why
The engine underperforms against baseline bots and fails key tactical spots. We need targeted, minimal enhancements that improve strength without abandoning explainability and style goals.

## What Changes
- Add lightweight transposition table (TT) for MCTS to reuse node statistics by position hash.
- Introduce heuristic rollout cutoffs: terminate clearly won/lost playouts early using evaluation thresholds.
- Expand tactical heuristics: hanging piece detection, simple threat bonus, and check/escape urgency in evaluation.
- Add mate-distance term in evaluation for forced mates discovered during search backprop.
- Tighten UCI search behavior to prefer principal variation stability when movetime is tight.

## Impact
- Affected specs: `search`, `evaluation`, `interfaces-uci` (minor clarification)
- Affected code: `search/mcts.py`, `eval/heuristics.py`, `interfaces/uci.py`
