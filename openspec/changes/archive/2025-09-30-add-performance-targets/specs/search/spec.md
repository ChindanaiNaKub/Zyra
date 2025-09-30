## ADDED Requirements
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

## MODIFIED Requirements
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
