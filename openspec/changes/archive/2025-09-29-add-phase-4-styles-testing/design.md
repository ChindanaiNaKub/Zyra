## Context

Phase 4 completes the style system integration by ensuring that style profiles actually influence search behavior, not just evaluation. The current implementation has basic style profiles and MCTS search, but lacks the deeper integration where styles affect move ordering, playout policies, and create measurably different behaviors.

## Goals / Non-Goals

**Goals:**
- Style profiles must create observable behavioral differences in search
- Maintain bounded randomness for reproducible testing while allowing style expression
- Comprehensive behavioral testing to catch regressions
- Style-aware playout policies that reflect personality without breaking determinism

**Non-Goals:**
- Major architectural changes to MCTS or evaluation systems
- Performance optimizations (maintain current ~10-20k nodes/sec target)
- New style profile types (focus on existing aggressive/defensive/experimental)

## Decisions

**Decision: Style-aware playout policies with weighted randomness**
- **What**: Implement style-influenced move selection during MCTS playout phase using weighted random selection
- **Why**: Allows styles to express personality during simulation while maintaining stochastic exploration
- **Alternatives considered**:
  - Deterministic playout (too rigid, loses exploration benefits)
  - Pure random playout (loses style expression)
  - Complex policy networks (overkill for v1)

**Decision: Evaluation-based tie-breaking in move ordering**
- **What**: Use evaluation scores to break ties between moves of equal heuristic priority
- **Why**: Allows styles to influence move selection at the ordering level
- **Alternatives considered**:
  - Random tie-breaking (loses style influence)
  - Complex positional analysis (adds complexity without clear benefit)

**Decision: Golden baseline files for regression testing**
- **What**: Store expected evaluation outputs for key positions as baseline files
- **Why**: Enables automated detection of behavioral drift
- **Alternatives considered**:
  - Live comparison tests (unreliable due to randomness)
  - Manual validation (doesn't scale)

## Risks / Trade-offs

**Risk: Style influence reduces search diversity**
- **Mitigation**: Maintain minimum randomness bounds and test for diversity

**Risk: Regression tests become brittle with randomness**
- **Mitigation**: Use fixed seeds for deterministic baselines, separate stochastic tests

**Risk: Performance impact of style-aware evaluation**
- **Mitigation**: Profile and optimize only if below target performance

**Trade-off: Style expression vs determinism**
- **Resolution**: Use seeded randomness for deterministic testing, allow variation in production

## Migration Plan

1. **Phase 4.1**: Enhance existing style-aware move ordering (backward compatible)
2. **Phase 4.2**: Add style-aware playout policies (new feature)
3. **Phase 4.3**: Implement behavioral testing framework (new infrastructure)
4. **Phase 4.4**: Add regression safeguards (new validation)

No breaking changes - all enhancements are additive to existing functionality.

## Open Questions

- Should style influence be configurable (light/medium/heavy influence)?
- How to handle style conflicts in multi-style testing scenarios?
- What's the appropriate baseline update frequency for regression tests?
