## Context
Phase 3 introduces the evaluation engine that will give the chess engine its distinct personality and playing style. This is a critical component that bridges the tactical search capabilities with strategic decision-making, enabling the engine to make moves that reflect configurable preferences rather than just raw strength.

The evaluation system must be explainable, allowing users to understand why the engine makes specific moves, and configurable through style profiles that can be tuned for different playing personalities.

## Goals / Non-Goals
- **Goals**:
  - Provide explainable evaluation heuristics that guide move selection
  - Enable configurable style profiles with distinct playing personalities
  - Integrate seamlessly with existing search infrastructure
  - Maintain performance targets for evaluation speed
- **Non-Goals**:
  - Complex neural network evaluations (keep simple, explainable heuristics)
  - Opening book integration (evaluation only, no opening theory)
  - Advanced endgame tablebase integration

## Decisions
- **Decision**: Use simple, explainable heuristics over complex algorithms
  - **Rationale**: Aligns with project goal of explainable engine personality
  - **Alternatives considered**: Neural networks, complex positional evaluation
- **Decision**: Implement config-driven style profiles with predefined weight sets
  - **Rationale**: Enables distinct personalities while keeping complexity manageable
  - **Alternatives considered**: Dynamic learning, user-defined custom profiles
- **Decision**: Separate material and positional evaluation into distinct components
  - **Rationale**: Enables fine-grained control and easier testing/debugging
  - **Alternatives considered**: Monolithic evaluation function

## Risks / Trade-offs
- **Risk**: Evaluation complexity may impact search performance
  - **Mitigation**: Profile evaluation performance and optimize hot paths only
- **Risk**: Style profiles may not create sufficiently distinct personalities
  - **Mitigation**: Extensive testing with different profiles and iterative tuning
- **Risk**: Over-engineering evaluation for premature optimization
  - **Mitigation**: Start with simple heuristics and add complexity only when needed

## Migration Plan
- Add evaluation capability as new module without breaking existing search
- Gradually integrate evaluation signals into search move ordering
- Maintain backward compatibility with existing UCI interface

## Open Questions
- Should evaluation be cached for repeated positions?
- How detailed should the explainable logging be for performance vs clarity trade-off?
- What are the specific weight ranges that create meaningful style differences?
