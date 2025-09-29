
---

# PRD: Original Chess Engine

## 1. Purpose

Build a chess engine that plays with a distinct identity. It should not copy well-known engines. Instead, it will combine unique evaluation heuristics, experimental search, and a style-driven play personality. The target audience is developers and chess players who want novelty, not raw strength.

---

## 2. Goals

* Generate legal chess moves and play complete games.
* Implement a non-standard search algorithm (not alpha-beta).
* Encode stylistic preferences (aggressive, defensive, experimental).
* Achieve ~1500–1800 Elo strength on Lichess bots.
* Be lightweight and explainable, not dependent on huge neural networks.

---

## 3. Non-Goals

* Competing with Stockfish, Lc0, or Komodo at the top level.
* Supporting advanced chess variants (initial release is classical chess only).
* Full opening book or tablebase integration.

---

## 4. Core Features

1. **Move Generator**

   * Generate all legal moves with rules (castling, en passant, promotions).
   * Representation: 0x88 or mailbox board for clarity, not optimized bitboards.

2. **Search Algorithm**

   * Monte Carlo Tree Search (MCTS) with playouts capped.
   * Alternative: Beam Search with heuristic pruning.
   * Stochastic exploration for variety.

3. **Evaluation Function**

   * Material balance with twists:

     * Bonus for attacking moves, sacrifices.
     * Penalty for retreating moves.
   * Positional heuristics:

     * King safety, center control, rook on open file.
   * Adjustable “style weights” to create different personalities.

4. **Play Styles (Profiles)**

   * Aggressive: prioritizes sacrifices and attacking chances.
   * Defensive: prefers safety, pawn shields, and simplification.
   * Experimental: randomizes move order more, explores unusual plans.

5. **Interface**

   * UCI protocol support so it can run in any chess GUI.
   * Command-line mode for testing.

6. **Analytics (Optional)**

   * Log evaluations and move choices for debugging.
   * Option to visualize search tree.

---

## 5. Technical Requirements

* Language: Python (prototype), Rust or C++ (optimized).
* Board representation: Mailbox 0x88 for simplicity.
* Strength target: 10–20k nodes/sec on a modern laptop.
* Cross-platform: Linux, Windows, macOS.

---

## 6. Success Metrics

* Plays legal, complete games without crashes.
* Distinct personality compared to Stockfish (can be observed in ~50 games).
* Achieves at least 1500 Elo in online bot matches.
* Users can configure style preferences.

---

## 7. Risks

* Search algorithm may be too weak without alpha-beta.
* Evaluation function may need heavy tuning to avoid blunders.
* Hard to measure uniqueness without comparison games.

---

## 8. Roadmap

**Phase 1: Foundations (2–3 weeks)**

* Implement board, legal move generator, UCI adapter.

**Phase 2: Search (3–4 weeks)**

* Prototype MCTS or beam search.
* Add playouts with heuristic-guided rollouts.

**Phase 3: Evaluation (2 weeks)**

* Implement material, mobility, king safety, and personality weights.

**Phase 4: Styles & Testing (2 weeks)**

* Tune aggressive, defensive, and experimental play profiles.
* Run matches against Stockfish (depth-limited) and humans.

**Phase 5: Packaging (1 week)**

* Build CLI tool and UCI-compatible binary.
* Publish to GitHub with documentation.

---
