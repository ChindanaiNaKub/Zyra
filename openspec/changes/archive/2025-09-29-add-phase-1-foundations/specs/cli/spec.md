## ADDED Requirements
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
