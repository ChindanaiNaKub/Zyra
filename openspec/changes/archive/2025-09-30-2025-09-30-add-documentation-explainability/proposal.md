## Why
Engine explainability and reproducibility are core goals but not yet specified as concrete requirements. We need clear documentation standards and structured evaluation logs that attribute decisions to heuristic terms, plus deterministic seeding to reproduce results.

## What Changes
- Add documentation standards across modules: module docstrings for subsystems; function docstrings for public APIs.
- Add explainable evaluation logging: record per-term contributions in evaluation traces.
- Add reproducibility metadata: persist seeds, style profile, and config in run artifacts and CLI output.
- Extend CLI to accept and echo `--seed` and to print run metadata in a machine-readable block.

## Impact
- Affected specs: evaluation, project-infrastructure, cli
- Affected code: `eval/heuristics.py`, `eval/heuristics_optimized.py`, `performance/metrics.py`, `zyra/cli/runner.py`, logging and config surfaces.
