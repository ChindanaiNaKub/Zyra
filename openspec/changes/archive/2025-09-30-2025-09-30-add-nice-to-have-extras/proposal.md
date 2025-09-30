## Why
The roadmap lists Nice-to-Have features to enhance explainability and usability: visualizing search behavior, lightweight opening heuristics (avoiding large books), and exporting PGNs with evaluation annotations. Capturing these as a scoped change clarifies expectations and sequencing without impacting core v1 targets.

## What Changes
- Add search tree/playout statistics visualization hooks and a simple textual renderer
- Add simple opening principles heuristics (no large opening books)
- Add CLI command to export PGN with inline annotations derived from evaluation terms

## Impact
- Affected specs: `search`, `evaluation`, `cli`
- Affected code: `search/mcts.py`, `eval/heuristics.py`, `zyra/cli/runner.py` and related interfaces
