## ADDED Requirements
### Requirement: 0x88 Board Representation
The system SHALL maintain a 0x88 mailbox board with piece/color arrays, side-to-move, castling rights, en passant square, and halfmove/fullmove counters.

#### Scenario: Initialize start position
- **WHEN** the engine initializes the board to startpos
- **THEN** the board fields reflect the standard chess starting position

#### Scenario: FEN import/export roundtrip
- **WHEN** a valid FEN is loaded and then exported
- **THEN** the exported FEN equals the original (normalized where applicable)

### Requirement: Move Generation (Legal Moves)
The system SHALL generate legal moves including castling, en passant, and promotions, filtering out moves that leave the king in check.

#### Scenario: Pseudolegal moves per piece
- **WHEN** generating pseudolegal moves for each piece type from a given position
- **THEN** the set of moves matches the allowed movement patterns for that piece

#### Scenario: Legality filter
- **WHEN** pseudolegal moves are filtered for king safety
- **THEN** only moves that do not leave own king in check are returned

#### Scenario: Special rules
- **WHEN** castling, en passant, or promotion rules apply
- **THEN** generated legal moves include valid instances of these rules

#### Scenario: Make/unmake with reversible state
- **WHEN** making and unmaking a move
- **THEN** the board state is restored exactly, including counters and rights

### Requirement: Rules Engine and Validation
The system SHALL detect check, checkmate, stalemate, and apply rule counters (fifty-move, repetition baseline).

#### Scenario: Check and mates
- **WHEN** evaluating a position
- **THEN** the system reports check, checkmate, or stalemate status correctly

#### Scenario: Fifty-move rule counter
- **WHEN** halfmove clock reaches 100 plies without capture or pawn move
- **THEN** the position is considered a draw by the fifty-move rule

#### Scenario: Repetition tracking (simple)
- **WHEN** positions repeat via a simple hash or history list
- **THEN** the system can detect threefold repetition eligibility

### Requirement: Perft Correctness Baseline
The system SHALL provide perft counting for reference positions to validate move generator correctness.

#### Scenario: Reference positions
- **WHEN** running perft on documented positions
- **THEN** node counts match the expected values up to the documented depth N
