## ADDED Requirements
### Requirement: MCTS Transposition Table (Lightweight)
The system SHALL provide a lightweight transposition table for MCTS keyed by a reproducible position hash to reuse statistics and accelerate convergence.

#### Scenario: TT lookup on selection
- **WHEN** selection reaches a node with a known hash in TT
- **THEN** prior/visit/value stats are initialized from TT to guide UCT

#### Scenario: TT store on backprop
- **WHEN** backprop completes for a node
- **THEN** the node's aggregated stats are stored in TT with an appropriate replacement policy

#### Scenario: Performance-safe TT
- **WHEN** TT is enabled with default size
- **THEN** overall nodes/sec does not degrade by more than 10% versus baseline

### Requirement: Heuristic Rollout Cutoff
The system SHALL terminate playouts early when evaluation exceeds win/loss thresholds to save computation while maintaining decision quality.

#### Scenario: Early win cutoff
- **WHEN** playout evaluation exceeds a configured win threshold
- **THEN** the simulation terminates with a win outcome

#### Scenario: Early loss cutoff
- **WHEN** playout evaluation drops below a configured loss threshold
- **THEN** the simulation terminates with a loss outcome

#### Scenario: Bounded bias
- **WHEN** heuristic cutoffs are active
- **THEN** regression tests confirm bestmove stability within acceptable variance compared to full playouts

## MODIFIED Requirements
### Requirement: Search Core (MCTS baseline)
The system SHALL provide a Monte Carlo Tree Search (MCTS) with style-aware integration that creates observable behavioral differences between style profiles while meeting performance targets.

- Node structure including prior/visits/value and parent/children links
- Core loop phases: selection, expansion, simulation (playout), and backpropagation
- Playout policy that supports stochastic exploration with style influence
- Limits: max playouts and optional wall-clock movetime; RNG seeding for reproducibility
- Performance: maintains at least 10,000 nodes/sec baseline performance
- Transposition table reuse of statistics where available
- Optional heuristic rollout cutoffs for early termination

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
