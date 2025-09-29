## Why
Phase 3 adds the evaluation engine that provides explainable heuristics to guide chess move selection. This capability is essential for creating the engine's distinct personality and style, enabling it to make decisions that reflect configurable preferences rather than just raw tactical strength.

## What Changes
- **NEW**: Evaluation capability with material, positional, and style profile components
- **NEW**: Config-driven style profiles (aggressive, defensive, experimental) with tunable weights
- **NEW**: Explainable evaluation logging that breaks down decision factors
- **NEW**: Integration points with search for style-aware move ordering

## Impact
- Affected specs: New `evaluation` capability
- Affected code: New `eval/` module with heuristics, style profiles, and integration hooks
- Integration: Search module will consume evaluation signals for move ordering
- Testing: Comprehensive evaluation tests with golden baselines for style outputs
