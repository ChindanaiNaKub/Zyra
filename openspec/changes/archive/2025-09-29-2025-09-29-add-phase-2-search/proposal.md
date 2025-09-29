## Why
Phase 2 introduces a real search algorithm so the engine can think beyond random move selection, respecting time/node limits and enabling style-aware move ordering hooks.

## What Changes
- Add a Search capability with MCTS as default, playout caps, and seeds.
- Provide hooks for heuristic move ordering and style-aware weights.
- Integrate with UCI  to respect movetime/nodes and return .
- Add tests for determinism with fixed seeds and bounds adherence.

## Impact
- Affected specs: search (new), interfaces-uci (go integration).
- Affected code: search loop, UCI adapter, eval heuristics hooks.
