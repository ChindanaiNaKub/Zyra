## MODIFIED Requirements
### Requirement: Explainable Evaluation Logging
The system SHALL provide detailed logging of evaluation terms to enable understanding of decision-making and style influence tracking.

#### Scenario: Term breakdown logging
- **WHEN** evaluating a position
- **THEN** the system logs the contribution of each evaluation term (material, positional, style-weighted)

#### Scenario: Style weight transparency
- **WHEN** applying style profiles to evaluation
- **THEN** the system logs which weights are applied and how they affect the final score

#### Scenario: Term contributions sum matches total
- **WHEN** an evaluation is computed during search
- **THEN** the trace includes each term's raw value, weight, and weighted contribution
- **AND** the sum of weighted contributions equals the final evaluation (within floating-point tolerance)

#### Scenario: Trace includes style profile context
- **WHEN** a style profile is active (e.g., aggressive)
- **THEN** the trace includes the profile name and the weights applied
