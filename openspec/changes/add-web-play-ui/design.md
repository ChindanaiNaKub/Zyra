## Context
We will add a minimal local web interface to play against Zyra. Keep dependencies light and reuse engine code. Serve a static SPA with a small JSON API.

## Goals / Non-Goals
- Goals: Local play UI, style selection, basic eval display, simple launch
- Non-Goals: Accounts, persistence, multiplayer, cloud deployment

## Decisions
- Use Python (FastAPI or Flask) for a small HTTP API serving static assets.
- Use a lightweight JS board (e.g., chessboard-element or simple drag/drop) with chess.js for legality on the client; backend validates too. Ensure visible SVG piece assets and default theme with strong contrast on dark/light squares.
- Maintain a server-side game session (FEN, move list); compute engine reply via existing search/eval.
- Layout: board left, controls above board, history/eval panel right, responsive down to 1024px with panels stacking on narrow screens.

## Risks / Trade-offs
- Long engine think may block; mitigate with a worker thread/process.
- Keep CORS and security simple for localhost only.
 - Asset licensing and clarity: prefer MIT/CC0 chess piece SVGs bundled locally to avoid CDN reliance.

## Open Questions
- Which style profiles are exposed in UI (all existing)?
- Preferred framework (FastAPI vs Flask)? Default to FastAPI for typing and docs.
