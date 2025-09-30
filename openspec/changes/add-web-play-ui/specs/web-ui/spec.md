## ADDED Requirements

### Requirement: Web Play UI - Core Gameplay
The system SHALL provide a browser-based chessboard to play against Zyra with legal move validation, engine replies, game reset, and move history display.

#### Scenario: Initial position with visible pieces
- **WHEN** the page loads a new game
- **THEN** all standard chess pieces are rendered in their correct starting squares and are visually distinct and draggable

#### Scenario: Load play page and start new game
- **WHEN** the user navigates to the web UI
- **THEN** a new standard chess game is initialized and displayed

#### Scenario: User makes a legal move via drag-and-drop
- **WHEN** the user drags a piece to a legal destination
- **THEN** the move is applied, added to move history, and sent to the engine

#### Scenario: Engine responds with a legal move
- **WHEN** the engine receives the user's move
- **THEN** the engine computes and displays its reply on the board and in history

#### Scenario: Illegal move rejected
- **WHEN** the user attempts an illegal move
- **THEN** the move is rejected and the piece returns to its origin square

#### Scenario: Reset game
- **WHEN** the user clicks reset
- **THEN** a fresh game is started and history is cleared

### Requirement: Web Play UI - Style and Settings
The system SHALL allow selecting a style profile (e.g., aggressive, defensive) and simple time/think settings for the engine.

#### Scenario: Select style profile
- **WHEN** the user selects a style profile from a dropdown
- **THEN** subsequent engine evaluations use the selected profile

#### Scenario: Adjust engine think time
- **WHEN** the user sets a per-move think time
- **THEN** the engine respects the limit for its move computation

### Requirement: Web Play UI - Evaluation and Status
The system SHALL show the latest evaluation score and last engine considerations at a glance.

#### Scenario: Display evaluation after engine move
- **WHEN** the engine plays a move
- **THEN** the latest evaluation score is shown in the UI

### Requirement: Web Play UI - Layout and Presentation
The system SHALL present a familiar chess.com-like layout so users immediately understand how to play.

#### Scenario: Chess.com-like two-pane layout
- **WHEN** the play page is displayed
- **THEN** the board appears on the left and a move history/metadata panel appears on the right, with controls above the board (style selector, think time, new game)

#### Scenario: Piece theming and clarity
- **WHEN** the board renders
- **THEN** pieces use clear SVG or image assets with sufficient contrast on both light and dark squares and remain visible during drag interactions

#### Scenario: Board affordances
- **WHEN** the user drags a piece
- **THEN** legal target squares are highlighted and the origin/last move squares are indicated

### Requirement: Web Play UI - Local Launch
The system SHALL run locally with a single command and require no external services.

#### Scenario: Start local web server
- **WHEN** the developer runs the launch command
- **THEN** the web UI is served on localhost and connects to the engine backend
