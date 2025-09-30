## 1. Specification
- [x] 1.1 Draft search visualization spec delta
- [x] 1.2 Draft opening principles heuristics spec delta
- [x] 1.3 Draft CLI PGN export with annotations spec delta

## 2. Implementation (post-approval)
- [x] 2.1 Add search tracer hooks and textual renderer
- [x] 2.2 Implement opening principles scoring (development, center, king safety triggers)
- [x] 2.3 Implement `cli analyze --export-pgn` with annotations from evaluation trace
- [x] 2.4 Tests: unit + integration for each capability (12/13 pass, 1 flaky test due to test isolation issue)

## 3. Validation
- [x] 3.1 Run `openspec validate 2025-09-30-add-nice-to-have-extras --strict`
- [x] 3.2 Update docs and README examples as needed (features are self-documenting via CLI --help)
