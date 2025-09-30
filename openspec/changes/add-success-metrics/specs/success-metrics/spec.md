## ADDED Requirements
### Requirement: Legal Full-Game Stability
The system SHALL play legal, complete games without crashes under sustained play via UCI or CLI runners.

#### Scenario: UCI full-game stability
- **WHEN** a GUI orchestrates multiple full games (self-play or vs external engine)
- **THEN** the engine completes games without process crashes or protocol deadlocks

#### Scenario: CLI smoke game stability
- **WHEN** running smoke games via CLI with default settings
- **THEN** the engine completes full games with only legal moves and proper end states

### Requirement: Distinct Style Personality
The system SHALL exhibit distinct playing personalities versus a baseline engine and across configured styles, observable over a statistically meaningful sample.

#### Scenario: Differentiation vs Stockfish baseline
- **WHEN** running ~50 games (rapid settings) against a Stockfish baseline or similar
- **THEN** the engine displays distinct behavioral patterns (move choices, openings, risk profiles) compared to the baseline

#### Scenario: Style profile separation
- **WHEN** running the same positions or self-play games across aggressive, defensive, and experimental styles
- **THEN** move preferences and evaluation outputs differ measurably between styles with statistical significance

### Requirement: Indicative Strength Target
The system SHOULD achieve an indicative strength of ≥1500 Elo against online bots under standard test conditions.

#### Scenario: Elo indicator vs online bots
- **WHEN** evaluating strength with a recognized pool of online bots
- **THEN** the measured performance indicates ≥1500 Elo, acknowledging variance and non-laboratory conditions

### Requirement: Configurable Style Preferences
The system SHALL allow users to configure style preferences via documented interfaces and apply them during search and evaluation.

#### Scenario: UCI style configuration
- **WHEN** the engine receives style configuration via supported UCI options or CLI flags
- **THEN** the selected style profile is applied and influences move ordering, playouts, and evaluation

#### Scenario: Runtime style switch
- **WHEN** a new style configuration is applied mid-session where supported
- **THEN** subsequent evaluations and searches reflect the new configuration without restart

### Requirement: Performance Guardrails for Usability
The system SHALL maintain search throughput and evaluation speed sufficient for practical play on a modern laptop.

#### Scenario: Nodes per second baseline
- **WHEN** running search with standard settings on a modern laptop
- **THEN** the engine achieves ≥10,000 nodes/sec baseline throughput

#### Scenario: Evaluation latency bound
- **WHEN** running evaluation within search loops
- **THEN** average single-position evaluation completes in under 0.1ms
