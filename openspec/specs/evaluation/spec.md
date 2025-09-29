# evaluation Specification

## Purpose
TBD - created by archiving change add-phase-3-evaluation. Update Purpose after archive.
## Requirements
### Requirement: Material Evaluation with Twists
The system SHALL provide material evaluation that goes beyond basic piece values to include attacking motifs and initiative bonuses.

#### Scenario: Base material calculation
- **WHEN** evaluating a position for material balance
- **THEN** the system calculates standard piece values (Pawn=1, Knight=3, Bishop=3, Rook=5, Queen=9, King=infinite)

#### Scenario: Attacking motif bonus
- **WHEN** pieces are attacking opponent pieces or key squares
- **THEN** the system awards bonuses proportional to the attacking potential and target value

#### Scenario: Sacrificial motif recognition
- **WHEN** a sacrifice leads to tactical advantages (pins, forks, discovered attacks)
- **THEN** the system recognizes the sacrifice and awards appropriate bonuses

#### Scenario: Initiative and retreat penalties
- **WHEN** pieces retreat from active positions or lose attacking potential
- **THEN** the system applies penalties proportional to the loss of initiative

### Requirement: Positional Heuristics
The system SHALL evaluate positional factors including king safety, center control, piece placement, and mobility using explainable, table-based approaches.

#### Scenario: King safety assessment
- **WHEN** evaluating king safety
- **THEN** the system considers pawn shield integrity, piece attacks on king zone, and king mobility

#### Scenario: Center control evaluation
- **WHEN** assessing center control
- **THEN** the system evaluates pawn and piece occupation of central squares (d4, d5, e4, e5)

#### Scenario: Rook placement bonuses
- **WHEN** evaluating rook positions
- **THEN** the system awards bonuses for rooks on open files, semi-open files, and ranks 7/2

#### Scenario: Piece mobility calculation
- **WHEN** calculating piece mobility
- **THEN** the system counts available moves for each piece and applies mobility bonuses

#### Scenario: Piece-square table evaluation
- **WHEN** evaluating piece placement
- **THEN** the system uses simple, explainable piece-square tables for positional bonuses

### Requirement: Style Profiles System
The system SHALL provide configurable style profiles with predefined weight sets that create distinct playing personalities.

#### Scenario: Predefined style profiles
- **WHEN** initializing the engine
- **THEN** the system supports three predefined styles: aggressive, defensive, experimental

#### Scenario: Style weight configuration
- **WHEN** a style profile is selected
- **THEN** the system applies corresponding weight sets to material and positional evaluation terms

#### Scenario: Config-driven style selection
- **WHEN** the engine receives style configuration
- **THEN** the system parses and validates the configuration, applying appropriate weights

#### Scenario: Runtime style switching
- **WHEN** the engine is running and receives a new style configuration
- **THEN** the system updates the evaluation weights without restarting

### Requirement: Explainable Evaluation Logging
The system SHALL provide detailed logging of evaluation terms to enable understanding of decision-making.

#### Scenario: Term breakdown logging
- **WHEN** evaluating a position
- **THEN** the system logs the contribution of each evaluation term (material, positional, style-weighted)

#### Scenario: Style weight transparency
- **WHEN** applying style profiles to evaluation
- **THEN** the system logs which weights are applied and how they affect the final score

#### Scenario: Move justification
- **WHEN** the engine selects a move
- **THEN** the system provides explainable reasoning based on evaluation term contributions

### Requirement: Evaluation Integration with Search
The system SHALL integrate evaluation signals with the search algorithm for style-aware move ordering and decision-making.

#### Scenario: Style-aware move ordering
- **WHEN** the search algorithm orders candidate moves
- **THEN** evaluation signals influence the ordering based on configured style preferences

#### Scenario: Evaluation performance targets
- **WHEN** running evaluation during search
- **THEN** the system maintains evaluation speed targets (sufficient for ~10-20k nodes/sec search)

#### Scenario: Evaluation caching
- **WHEN** evaluating the same position multiple times
- **THEN** the system may cache evaluation results to improve performance (optional optimization)

### Requirement: Evaluation Testing and Validation
The system SHALL provide comprehensive testing for evaluation components with golden baselines for style outputs.

#### Scenario: Unit tests for evaluation terms
- **WHEN** testing individual evaluation components
- **THEN** each term (material, positional, style) has dedicated unit tests with known position inputs

#### Scenario: Golden baseline tests
- **WHEN** validating style profile outputs
- **THEN** the system compares evaluation results against golden baseline files for regression detection

#### Scenario: Style differentiation validation
- **WHEN** testing different style profiles on the same positions
- **THEN** the system demonstrates measurable differences in evaluation outputs and move preferences

#### Scenario: Integration testing with search
- **WHEN** testing evaluation-search integration
- **THEN** the system validates that evaluation signals properly influence search behavior
