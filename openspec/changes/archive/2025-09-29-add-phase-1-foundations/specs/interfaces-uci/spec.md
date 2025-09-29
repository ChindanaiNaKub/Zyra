## ADDED Requirements
### Requirement: Initial UCI Commands
The system SHALL support a minimal UCI command set: `uci`, `isready`, `ucinewgame`, `position`, `go`, `stop`, `quit`.

#### Scenario: Identify engine
- **WHEN** the GUI sends `uci`
- **THEN** the engine responds with `id name`, `id author`, and `uciok`

#### Scenario: Readiness
- **WHEN** the GUI sends `isready`
- **THEN** the engine responds with `readyok`

#### Scenario: New game
- **WHEN** the GUI sends `ucinewgame`
- **THEN** the engine resets internal state for a new game

#### Scenario: Position setup
- **WHEN** the GUI sends `position startpos` or `position fen <FEN>` with optional moves
- **THEN** the engine sets the internal board accordingly and applies moves

#### Scenario: Go/Stop minimal search
- **WHEN** the GUI sends `go` and later `stop`
- **THEN** the engine thinks minimally and returns a legal move via `bestmove`

### Requirement: Legal Random Move for Smoke Tests
The system SHALL, in absence of a search configuration, return a uniformly random legal move.

#### Scenario: Random legal move
- **WHEN** `go` is called without search parameters
- **THEN** the engine chooses a random legal move and prints `bestmove <move>`
