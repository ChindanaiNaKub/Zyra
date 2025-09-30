## Why
Zyra currently exposes a UCI interface and CLI flows but lacks a user-friendly web interface. A minimal, chess.com-like web play surface will improve accessibility for casual users to play against the engine, visualize moves, and adjust styles.

## What Changes
- Introduce a lightweight web UI to play against Zyra with a familiar chessboard layout and move interactions, including visible, draggable pieces rendered in starting positions.
- Provide backend endpoints to bridge the web client to the existing UCI/engine core.
- Support basic features: start/reset game, make moves via drag/drop, see engine reply, switch style profile, choose time controls (simple per-move delay), and show evaluation/last move. Layout mirrors chess.com conventions: board left; controls above; history/eval panel right; legal-move highlights.
- Ensure portability: run locally with a single command; no external DB required.

## Impact
- Affected specs: `interfaces-uci`, `cli` (optional launch), new `web-ui` capability.
- Affected code: new lightweight web server and static assets; small integration shim to engine move generation.
- Non-goals: online multiplayer, accounts, persistence, advanced analysis boards.
