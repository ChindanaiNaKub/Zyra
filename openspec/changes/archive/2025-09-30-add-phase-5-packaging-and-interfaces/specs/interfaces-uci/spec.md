## ADDED Requirements
### Requirement: UCI Conformance Validation
The system SHALL interoperate with common UCI GUIs (Cute Chess, Arena) by correctly responding to core commands and maintaining session state across games.

#### Scenario: Identify and acknowledge UCI
- **WHEN** the GUI sends `uci`
- **THEN** the engine responds with `id name`, `id author`, and `uciok`

#### Scenario: Readiness acknowledgement
- **WHEN** the GUI sends `isready`
- **THEN** the engine responds with `readyok`

#### Scenario: New game reset
- **WHEN** the GUI sends `ucinewgame`
- **THEN** the engine resets internal state for a new game

#### Scenario: Position setup with optional moves
- **WHEN** the GUI sends `position startpos` or `position fen <FEN>` with optional `moves`
- **THEN** the engine sets the internal board accordingly and applies moves

#### Scenario: Go/Stop search windowed
- **WHEN** the GUI sends `go movetime X` or `go nodes N` and later `stop`
- **THEN** the engine searches within the bounds and prints `bestmove <move>`

### Requirement: Long-Running Stability
The system SHALL complete full games without crashing under sustained UCI-driven play.

#### Scenario: Full-game stability
- **WHEN** a GUI orchestrates multiple full games (self-play or vs external engine)
- **THEN** the engine completes games without process crashes or protocol deadlocks
