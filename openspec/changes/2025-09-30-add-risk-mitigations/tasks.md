## 1. Specification
- [x] 1.1 Draft delta specs under `project-infrastructure` for risk mitigations
- [x] 1.2 Validate change with `openspec validate 2025-09-30-add-risk-mitigations --strict`

## 2. Tooling & Docs (follow-up; separate PRs)
- [ ] 2.1 Ensure CLI exposes `--seed` and logs seed at startup
- [ ] 2.2 Ensure config snapshots (style profile + weights) are saved with runs
- [ ] 2.3 Add profiling guidance and scripts; gate optimizations on profiling data
- [ ] 2.4 Document style tuning workflow in `STYLE_PROFILES.md` with safe bounds

## 3. Validation
- [ ] 3.1 Add/extend tests to assert determinism when seed is fixed
- [ ] 3.2 Add/extend performance tests to require profiling evidence before changes (process doc)
- [ ] 3.3 Add tests validating style profile application affects outputs while remaining deterministic with fixed seed
