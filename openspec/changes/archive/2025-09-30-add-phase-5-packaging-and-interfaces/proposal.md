## Why
Phase 5 focuses on getting the engine ready for real-world use by ensuring UCI conformance with popular GUIs, rounding out CLI tooling for common workflows, and providing a simple distribution story. Previous phases established core functionality, search, evaluation, and behavioral validation; this phase packages those capabilities for end users and external tooling.

## What Changes
- UCI conformance validation against common GUIs (Cute Chess, Arena)
- Long-running stability testing (play full games without crash)
- CLI commands for perft, play, analyze, and profile-style
- Distribution plan: simple binary or entrypoint script, cross-platform notes, and publishable documentation

## Impact
- Affected specs: `interfaces-uci`, `cli`, `project-infrastructure`
- Affected code: `interfaces/uci.py`, `cli/runner.py`, `README.md`, `pyproject.toml`
- Outcome: Users can plug the engine into GUIs via UCI, run typical workflows via CLI, and install/run the engine with minimal setup across platforms
