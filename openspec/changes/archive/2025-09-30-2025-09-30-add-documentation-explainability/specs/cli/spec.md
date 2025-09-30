## ADDED Requirements
### Requirement: Deterministic Seeding and Metadata Output
The CLI SHALL accept a `--seed` parameter and print a machine-readable metadata block at startup that includes the seed, style profile, and configuration snapshot location.

#### Scenario: CLI accepts and echoes --seed
- **WHEN** the user provides `--seed 12345`
- **THEN** the CLI initializes randomness with that seed and echoes it in the startup metadata

#### Scenario: Metadata block printed
- **WHEN** starting a run via CLI
- **THEN** a metadata block (e.g., JSON) is printed to stdout or a log file with seed, profile name, and config snapshot path
