## ADDED Requirements
### Requirement: PGN Export with Annotations
The CLI SHALL export game PGNs with lightweight annotations derived from evaluation terms and search insights.

#### Scenario: Export annotated PGN from analyze/play
- **WHEN** the user runs `cli analyze --export-pgn <path>` or completes a `cli play` session with an export flag
- **THEN** the CLI writes a PGN file including comments per move for key evaluation terms and the principal variation

#### Scenario: Minimal, readable comments
- **WHEN** annotations are generated
- **THEN** the comments include concise term summaries (e.g., material, mobility, king safety) and top PV in SAN; avoid verbose dumps by default

#### Scenario: Reproducibility metadata
- **WHEN** exporting
- **THEN** the PGN includes seed and style profile metadata in headers for traceability
