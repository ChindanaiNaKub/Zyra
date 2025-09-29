# search Specification

## Purpose
TBD - created by archiving change 2025-09-29-add-phase-2-search. Update Purpose after archive.
## Requirements
### Requirement: Search Core (MCTS baseline)
The system SHALL provide a Monte Carlo Tree Search (MCTS) with:
- Node structure including prior/visits/value and parent/children links
- Core loop phases: selection, expansion, simulation (playout), and backpropagation
- Playout policy that supports stochastic exploration
- Limits: max playouts and optional wall-clock movetime; RNG seeding for reproducibility

#### Scenario: Deterministic with fixed seed
- **WHEN** the search runs with a fixed seed and fixed playout cap
- **THEN** the selected `bestmove` is deterministic across runs

#### Scenario: Playout cap respected
- **WHEN** the search is configured with a playout limit N
- **THEN** the algorithm performs at most N playouts before returning `bestmove`

#### Scenario: Movetime respected
- **WHEN** the search is configured with a movetime budget T ms
- **THEN** the algorithm returns `bestmove` within T + scheduling tolerance

### Requirement: Move Ordering & Pruning Hooks
The system SHALL provide heuristic move ordering hooks prioritizing captures, checks, and promotions, and allow style-aware tie-breaking based on evaluation weights.

#### Scenario: Heuristic ordering available
- **WHEN** generating candidate moves for node expansion
- **THEN** moves are ordered with captures/checks/promotions first, then others

#### Scenario: Style-aware tie-break
- **WHEN** moves have equal heuristic score
- **THEN** a style-aware signal may bias ordering consistently with configured weights

### Requirement: UCI Integration for Search
The system SHALL integrate with the UCI `go` command, interpreting `movetime`, `nodes`, and ignoring unsupported depth-like flags in v1 with a documented message.

#### Scenario: Respect movetime and nodes
- **WHEN** `go movetime X` or `go nodes N` is received
- **THEN** search uses the corresponding bound and prints `bestmove <move>`

#### Scenario: Unsupported flags are safe
- **WHEN** `go depth D` is received
- **THEN** the engine proceeds with default behavior and logs a non-fatal note
