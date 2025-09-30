## ADDED Requirements
### Requirement: Distribution Entrypoint
The system SHALL provide a simple entrypoint to run the engine via CLI and UCI without manual PYTHONPATH tweaks.

#### Scenario: Install and run
- **WHEN** a user installs the package and runs `zyra` (or `python -m zyra`)
- **THEN** the CLI is available with documented subcommands and UCI mode

### Requirement: Cross-Platform Notes
The system SHALL document cross-platform considerations for Linux, Windows, and macOS.

#### Scenario: User reads README for platform notes
- **WHEN** a user reads `README.md`
- **THEN** they find guidance for prerequisites and platform-specific instructions

### Requirement: Publishable Documentation
The system SHALL provide steps for building and publishing releases.

#### Scenario: Maintainer publishes a release
- **WHEN** a maintainer follows documented steps
- **THEN** a new version is built and published with changelog and spec references
