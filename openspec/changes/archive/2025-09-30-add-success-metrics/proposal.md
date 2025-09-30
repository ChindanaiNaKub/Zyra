## Why
Success criteria from the PRD are not yet captured in OpenSpec. We need explicit, testable success metrics to guide acceptance and regression checks.

## What Changes
- Add a new `success-metrics` capability spec delta capturing measurable outcomes
- Define requirements for: legal full-game stability, distinct style personality, indicative strength target, configurable style preferences, and performance guardrails
- Link metrics to existing capabilities (engine-core, search, evaluation, interfaces-uci)

## Impact
- Affected specs: `success-metrics` (new), references `engine-core`, `search`, `evaluation`, `interfaces-uci`
- Affected code: test suites under `tests/` and performance tooling under `performance/` for validation
