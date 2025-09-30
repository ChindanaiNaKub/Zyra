## ADDED Requirements
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
