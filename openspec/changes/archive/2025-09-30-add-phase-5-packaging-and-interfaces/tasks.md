## 1. UCI Conformance & Stability
- [x] 1.1 Validate `uci`, `isready`, `ucinewgame`, `position`, `go`, `stop`, `quit` against Cute Chess
- [x] 1.2 Validate the same against Arena
- [x] 1.3 Run long-running stability test: full self-play games without crashes

## 2. CLI Tooling
- [x] 2.1 Implement `perft` command entry in CLI
- [x] 2.2 Implement `play` command (self-play or vs engine with time/nodes)
- [x] 2.3 Implement `analyze` command (single position evaluation/search summary)
- [x] 2.4 Implement `profile-style` command (report style-weight impacts)

## 3. Distribution & Docs
- [x] 3.1 Provide entrypoint script or simple binary build notes
- [x] 3.2 Add cross-platform notes (Linux/Windows/macOS) in README
- [x] 3.3 Write publishing steps and documentation pointers

## 4. Validation
- [x] 4.1 Write/extend tests to cover new CLI commands
- [x] 4.2 Document UCI conformance steps and outcomes
