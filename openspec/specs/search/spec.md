# search Specification

## Purpose
TBD - created by archiving change 2025-09-29-add-phase-2-search. Update Purpose after archive.
## Requirements
### Requirement: Search Core (MCTS baseline)
The system SHALL provide a Monte Carlo Tree Search (MCTS) with style-aware integration that creates observable behavioral differences between style profiles while meeting performance targets.

- Node structure including prior/visits/value and parent/children links
- Core loop phases: selection, expansion, simulation (playout), and backpropagation
- Playout policy that supports stochastic exploration with style influence
- Limits: max playouts and optional wall-clock movetime; RNG seeding for reproducibility
- Performance: maintains at least 10,000 nodes/sec baseline performance

#### Scenario: Deterministic with fixed seed
- **WHEN** the search runs with a fixed seed and fixed playout cap
- **THEN** the selected `bestmove` is deterministic across runs

#### Scenario: Playout cap respected
- **WHEN** the search is configured with a playout limit N
- **THEN** the algorithm performs at most N playouts before returning `bestmove`

#### Scenario: Movetime respected
- **WHEN** the search is configured with a movetime budget T ms
- **THEN** the algorithm returns `bestmove` within T + scheduling tolerance

#### Scenario: Style-aware deterministic behavior
- **WHEN** running search with different style profiles and fixed seeds
- **THEN** each style profile produces different but deterministic move selections

#### Scenario: Performance target compliance
- **WHEN** running search with standard settings
- **THEN** the system achieves at least 10,000 nodes per second while maintaining style-aware behavior

### Requirement: Move Ordering & Pruning Hooks
The system SHALL provide heuristic move ordering hooks prioritizing captures, checks, and promotions, and implement style-aware tie-breaking based on evaluation weights with measurable behavioral impact.

#### Scenario: Heuristic ordering available
- **WHEN** generating candidate moves for node expansion
- **THEN** moves are ordered with captures/checks/promotions first, then others

#### Scenario: Style-aware tie-break
- **WHEN** moves have equal heuristic score
- **THEN** style-aware evaluation signals bias ordering consistently with configured weights, creating observable differences between style profiles

#### Scenario: Style influence on move ordering
- **WHEN** applying different style profiles to move ordering
- **THEN** the system produces measurably different move orderings that reflect style characteristics

### Requirement: UCI Integration for Search
The system SHALL integrate with the UCI `go` command, interpreting `movetime`, `nodes`, and ignoring unsupported depth-like flags in v1 with a documented message, while supporting style-aware search behavior.

#### Scenario: Respect movetime and nodes
- **WHEN** `go movetime X` or `go nodes N` is received
- **THEN** search uses the corresponding bound and prints `bestmove <move>`

#### Scenario: Unsupported flags are safe
- **WHEN** `go depth D` is received
- **THEN** the engine proceeds with default behavior and logs a non-fatal note

#### Scenario: Style-aware UCI search
- **WHEN** running UCI search with different style configurations
- **THEN** the engine produces different move selections that reflect the configured style

### Requirement: Style-Aware Playout Policies
The system SHALL implement style-influenced playout policies that maintain bounded randomness while expressing personality characteristics during MCTS simulation.

#### Scenario: Style-weighted move selection
- **WHEN** performing MCTS playout simulation
- **THEN** style weights influence the probability of move selection during random playouts

#### Scenario: Bounded randomness with style expression
- **WHEN** applying style influence to playout policies
- **THEN** the system maintains minimum randomness bounds while allowing style preferences to influence selection

#### Scenario: Deterministic style playouts
- **WHEN** running style-aware playouts with fixed seeds
- **THEN** the system produces deterministic results for testing and validation

#### Scenario: Style playout diversity
- **WHEN** testing style-aware playouts
- **THEN** the system maintains sufficient diversity while expressing style characteristics

### Requirement: Behavioral Search Testing
The system SHALL provide comprehensive testing to validate that style profiles create observable behavioral differences in search decisions and maintain consistency over time.

#### Scenario: Style search differentiation
- **WHEN** running search with different style profiles on the same position
- **THEN** the system demonstrates measurable differences in move selection and search behavior

#### Scenario: Stochastic exploration validation
- **WHEN** testing search with different seeds and same style
- **THEN** the system shows bounded randomness while maintaining style characteristics

#### Scenario: Search behavior consistency
- **WHEN** applying the same style profile to multiple similar positions
- **THEN** the system shows consistent search patterns characteristic of that style

#### Scenario: Search regression detection
- **WHEN** running regression tests against search behavior baselines
- **THEN** the system detects when search behaviors drift from expected style patterns

### Requirement: End-to-End Style Integration
The system SHALL provide end-to-end testing that validates style profiles create complete behavioral differences across the entire search and evaluation pipeline.

#### Scenario: Self-play style differentiation
- **WHEN** running self-play games with different style profiles
- **THEN** the system demonstrates distinct playing patterns and move preferences for each style

#### Scenario: Smoke game validation
- **WHEN** running limited-depth smoke games with style profiles
- **THEN** the system completes games without crashes while maintaining style characteristics

#### Scenario: Style integration regression
- **WHEN** running comprehensive style integration tests
- **THEN** the system validates that style profiles continue to create observable differences after code changes

### Requirement: Search Performance Targets
The system SHALL meet specific performance targets for search operations to ensure practical usability while maintaining style-aware behavioral characteristics.

#### Scenario: Baseline search performance
- **WHEN** running search on a standard position with default settings
- **THEN** the system achieves at least 10,000 nodes per second on a modern laptop

#### Scenario: Performance scaling with complexity
- **WHEN** running search on complex tactical positions
- **THEN** the system maintains at least 5,000 nodes per second even in complex positions

#### Scenario: Movetime performance compliance
- **WHEN** search is configured with a movetime budget
- **THEN** the system returns results within the specified time budget with minimal overhead

#### Scenario: Performance consistency across styles
- **WHEN** running search with different style profiles
- **THEN** performance remains within 20% variance across all style configurations

### Requirement: Search Performance Benchmarking
The system SHALL provide performance benchmarking capabilities to measure and validate search performance against targets.

#### Scenario: Performance benchmark execution
- **WHEN** running performance benchmarks
- **THEN** the system measures and reports nodes per second, memory usage, and search efficiency metrics

#### Scenario: Performance regression detection
- **WHEN** running performance regression tests
- **THEN** the system detects when performance degrades below acceptable thresholds

#### Scenario: Performance profiling integration
- **WHEN** performance profiling is enabled
- **THEN** the system provides detailed timing information for search phases (selection, expansion, simulation, backpropagation)

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
