# cli Specification

## Purpose
TBD - created by archiving change add-phase-1-foundations. Update Purpose after archive.
## Requirements
### Requirement: CLI Test Runner
The system SHALL provide a CLI to load FEN or startpos, make moves, run perft, and print the board.

#### Scenario: Load and display position
- **WHEN** the user runs the CLI with `--fen` or `--startpos`
- **THEN** the board is loaded and printed to stdout

#### Scenario: Make moves
- **WHEN** the user provides a sequence of SAN/UCT moves
- **THEN** the moves are applied and the final board is printed

#### Scenario: Perft command
- **WHEN** the user runs perft with `--perft N`
- **THEN** the CLI prints the node count for depth N

### Requirement: CLI Perft Command
The system SHALL provide a `perft` command to compute node counts to a specified depth for the current position.

#### Scenario: Run perft at depth N
- **WHEN** the user runs the CLI with `perft --depth N` (with optional `--fen` or `--startpos`)
- **THEN** the CLI prints the node count for depth N and exits with code 0

### Requirement: CLI Play Command
The system SHALL provide a `play` command to run games (self-play or vs legal random) with time/node controls.

#### Scenario: Self-play game completes
- **WHEN** the user runs `play --self --movetime 500` (or `--nodes N`)
- **THEN** the CLI plays a complete game and prints the result in PGN or summary form

### Requirement: CLI Analyze Command
The system SHALL provide an `analyze` command to evaluate a single position and print search/evaluation summaries.

#### Scenario: Analyze position
- **WHEN** the user runs `analyze --fen <FEN> --movetime 1000`
- **THEN** the CLI prints the best move and a brief explanation (depth/nodes/value and key style terms)

### Requirement: CLI Profile-Style Command
The system SHALL provide a `profile-style` command to report style-weight impacts on evaluation terms for a position.

#### Scenario: Profile style terms
- **WHEN** the user runs `profile-style --fen <FEN> --style aggressive`
- **THEN** the CLI prints term-by-term contributions and deltas vs default style

### Requirement: Deterministic Seeding and Metadata Output
The CLI SHALL accept a `--seed` parameter and print a machine-readable metadata block at startup that includes the seed, style profile, and configuration snapshot location.

#### Scenario: CLI accepts and echoes --seed
- **WHEN** the user provides `--seed 12345`
- **THEN** the CLI initializes randomness with that seed and echoes it in the startup metadata

#### Scenario: Metadata block printed
- **WHEN** starting a run via CLI
- **THEN** a metadata block (e.g., JSON) is printed to stdout or a log file with seed, profile name, and config snapshot path
