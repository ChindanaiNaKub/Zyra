## ADDED Requirements
### Requirement: Documentation Standards
The project SHALL include module-level docstrings for subsystems and function-level docstrings for all public APIs.

#### Scenario: Module docstrings present
- **WHEN** reading any subsystem module (e.g., `core/board.py`, `eval/heuristics.py`)
- **THEN** the file begins with a module docstring describing purpose and key concepts

#### Scenario: Public API docstrings present
- **WHEN** inspecting public functions/classes exported by subsystems
- **THEN** they include concise docstrings covering parameters, returns, and side-effects

### Requirement: Reproducibility Metadata
Runs MUST record the random seed, active style profile, and configuration snapshot to support reproducible experiments.

#### Scenario: Seed recorded in artifacts
- **WHEN** running benchmarks or CLI games
- **THEN** the chosen seed is stored in logs/artifacts and printed at start-up

#### Scenario: Config snapshot stored
- **WHEN** a run is initiated with a style profile and parameters
- **THEN** a machine-readable snapshot (e.g., JSON) containing profile name and weights is saved alongside results
