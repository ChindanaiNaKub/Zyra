## ADDED Requirements
### Requirement: Search Visualization Hooks
The system SHALL provide hooks to capture search tree or playout statistics and render a simple textual visualization without external GUI dependencies.

#### Scenario: Enable search tracing
- **WHEN** search runs with tracing enabled
- **THEN** the system records node expansions, visits, values, and principal variation data for the root and top-N children

#### Scenario: Textual tree view
- **WHEN** a textual renderer is invoked
- **THEN** the system prints a hierarchical tree view (limited depth, width) with visits/value and move SAN/USI, suitable for logs

#### Scenario: Performance-safe tracing
- **WHEN** tracing is disabled (default)
- **THEN** the search incurs negligible overhead and maintains baseline performance targets
