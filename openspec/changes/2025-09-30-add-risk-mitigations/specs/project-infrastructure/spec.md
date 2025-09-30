## ADDED Requirements

### Requirement: Deterministic Runs for Testing
The system SHALL support deterministic execution by allowing a fixed random seed and recording it in logs and artifacts.

#### Scenario: Fixed seed yields repeatable bestmove
- **WHEN** search and evaluation run with a fixed seed and identical inputs
- **THEN** the same sequence of decisions and `bestmove` are produced across runs

#### Scenario: Seed logged at startup
- **WHEN** the engine or benchmark starts
- **THEN** the chosen seed value is printed and stored in run artifacts

### Requirement: Configuration Snapshotting for Reproducibility
The system MUST persist a machine-readable snapshot of active configuration including style profile name and weights for each run.

#### Scenario: Style profile snapshot saved
- **WHEN** a run begins with a selected style profile
- **THEN** a JSON snapshot including profile name and weights is written alongside results

### Requirement: Profiling-First Performance Changes
Performance-related changes MUST be justified by profiling data identifying hotspots before optimization is merged.

#### Scenario: Profiling evidence attached
- **WHEN** submitting a performance optimization change
- **THEN** profiling output identifying the hotspot and expected impact is attached to the PR or artifacts

#### Scenario: No premature micro-optimization
- **WHEN** code changes do not target a profiled hotspot
- **THEN** they are deferred or rejected until profiling demonstrates material impact

### Requirement: Safe Style Weight Tuning Workflow
Style weight adjustments SHALL follow a documented workflow with bounds and validation against golden baselines.

#### Scenario: Style change diffs golden baselines
- **WHEN** style weights are modified
- **THEN** evaluation outputs are compared against golden baselines to detect drift, and changes include rationale

#### Scenario: Bounded tuning
- **WHEN** adjusting style weights
- **THEN** changes remain within documented safe bounds unless accompanied by updated baselines and justification
