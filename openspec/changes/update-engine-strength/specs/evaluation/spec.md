## ADDED Requirements
### Requirement: Tactical Heuristics Expansion
The system SHALL extend evaluation with hanging piece detection, direct threat bonuses, and check/escape urgency to better reflect tactical realities.

#### Scenario: Hanging piece penalty
- **WHEN** a piece is attacked and insufficiently defended
- **THEN** the evaluation applies a penalty proportional to piece value and exposure

#### Scenario: Immediate threat bonus
- **WHEN** a move creates a direct capture threat on a higher-value target
- **THEN** the evaluation applies a bonus scaled by target value and proximity

#### Scenario: Check/escape urgency
- **WHEN** the side to move is in check
- **THEN** the evaluation prioritizes escape resources by applying urgency adjustments

### Requirement: Mate Distance Term
The system SHALL incorporate mate distance scoring when forced mates are detected by search, preferring faster mates and delaying being mated.

#### Scenario: Prefer faster mate
- **WHEN** multiple mating lines exist
- **THEN** the evaluation prefers the line with smaller mate distance

#### Scenario: Delay being mated
- **WHEN** all lines lead to mate against
- **THEN** the evaluation prefers lines that maximize mate distance

## MODIFIED Requirements
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

#### Scenario: Tactical corrections applied
- **WHEN** positional evaluation conflicts with clear tactical losses (e.g., hanging major piece)
- **THEN** tactical heuristics adjustments override or dampen positional bonuses to prevent blunders
