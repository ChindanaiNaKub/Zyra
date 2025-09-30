## ADDED Requirements
### Requirement: Opening Principles Heuristics (Lightweight)
The system SHALL include simple opening-phase heuristics without using large opening books, focusing on development, center control, and king safety triggers.

#### Scenario: Development incentives
- **WHEN** in the opening phase (by move count or material heuristic)
- **THEN** the system rewards developing minor pieces and controlling central squares

#### Scenario: Early king safety triggers
- **WHEN** typical castling opportunities arise in the opening
- **THEN** the system awards modest incentives for castling toward safety

#### Scenario: No large book dependency
- **WHEN** evaluating the opening phase
- **THEN** no external large opening book files are required; heuristics operate purely from position features
