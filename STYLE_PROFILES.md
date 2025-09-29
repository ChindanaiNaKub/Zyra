# Style Profiles Configuration

Zyra chess engine supports configurable playing styles through weight profiles that influence evaluation and search behavior.

## Overview

Style profiles allow you to customize the engine's playing personality by adjusting the relative importance of different evaluation factors. This creates distinct playing styles while maintaining explainable, transparent decision-making.

## Predefined Profiles

### Aggressive Style
Favors attacking moves, tactical complications, and dynamic play.

```python
AGGRESSIVE_WEIGHTS = {
    "material": 1.0,
    "attacking_motifs": 1.3,   # Bonus for attacking enemy pieces and sacs
    "center_control": 1.2,      # Emphasis on central squares
    "rook_files": 1.1,          # Prefer open/semi-open files
    "mobility": 1.15,           # Rewards active piece placement
    "king_safety": 1.0,         # Standard safety consideration
    "initiative": 1.2,          # Emphasize maintaining initiative
}
```

**Characteristics:**
- Seeks immediate tactical shots
- Prioritizes piece activity over safety
- Willing to sacrifice material for initiative
- Favors open, tactical positions

### Defensive Style
Prioritizes king safety, solid positional play, and avoiding risks.

```python
DEFENSIVE_WEIGHTS = {
    "material": 1.05,
    "attacking_motifs": 0.9,
    "center_control": 1.0,
    "rook_files": 1.0,
    "mobility": 0.95,
    "king_safety": 1.3,
    "initiative": 0.9,
}
```

**Characteristics:**
- Prioritizes king safety above all
- Builds solid, defensive positions
- Avoids tactical complications
- Prefers closed, positional games

### Experimental Style
Explores unusual moves and creative patterns for educational value.

```python
EXPERIMENTAL_WEIGHTS = {
    "material": 0.95,
    "attacking_motifs": 1.2,
    "center_control": 1.05,
    "rook_files": 1.05,
    "mobility": 1.25,
    "king_safety": 0.9,
    "initiative": 1.1,
}
```

**Characteristics:**
- Explores unconventional move patterns
- Balances creativity with soundness
- Provides educational insights
- Shows alternative approaches to common positions

## Custom Profiles

You can create custom style profiles by defining your own weight dictionaries:

```python
CUSTOM_STYLE = {
    "attack_bonus": 1.2,
    "king_safety": 1.1,
    "center_control": 1.3,
    "pawn_structure": 1.0,
    "piece_mobility": 1.1,
    "endgame_technique": 1.2,
}
```

### Available Weight Categories (implemented)

- `material`: Standard piece values (centipawns)
- `attacking_motifs`: Attacks on enemy pieces and sacrifice motifs
- `center_control`: Occupancy of d4/e4/d5/e5
- `rook_files`: Rooks on open/semi-open files
- `mobility`: Number of legal moves differential
- `king_safety`: Pawn shield near king
- `initiative`: Derived from mobility to reward maintaining pressure

## Search Integration

Style profiles integrate with the MCTS search engine through multiple mechanisms:

### Style-Aware MCTS Search
```python
from search.mcts import MCTSSearch
from eval.heuristics import get_style_profile

# Create search with style profile directly
search = MCTSSearch(
    max_playouts=1000,
    style="aggressive"  # Can use string name or weights dict
)

# Search with full style integration
best_move = search.search(position)
```

### Style-Aware Playout Policies
The MCTS simulation phase now uses style-weighted move selection instead of pure random selection:

- **Style-weighted probability distribution**: Moves are selected based on evaluation scores using softmax with temperature
- **Bounded randomness**: Maintains exploration while allowing style expression
- **Configurable temperature**: Controls the balance between randomness and style influence

### Style-Aware Move Ordering
```python
from search.mcts import MCTSSearch, style_aware_move_ordering
from eval.heuristics import get_style_profile

# Load style profile
weights = get_style_profile("aggressive")

# Create search with style-aware move ordering hook
search = MCTSSearch(
    max_playouts=1000,
    move_ordering_hook=lambda pos, moves: style_aware_move_ordering(pos, moves, weights),
    style=weights  # Also applies to playout policy
)

# Search with style influence
best_move = search.search(position)
```

### Evaluation-Based Tie-Breaking
When moves have equal heuristic priority, style profiles influence the ordering through evaluation scores:

- **Heuristic priority first**: Captures, promotions, checks maintain highest priority
- **Style-weighted tie-breaking**: Within each priority group, moves are ordered by style-influenced evaluation
- **Consistent ordering**: Same style profile always produces the same move ordering

### Style-Aware UCI Engine
The UCI engine automatically applies style profiles when configured:

```python
from interfaces.uci import UCIEngine
from eval.heuristics import get_style_profile

engine = UCIEngine()
# Engine will use style profiles for move ordering during search
```

## Configuration Usage

### Loading a Profile

```python
from eval.heuristics import get_style_profile, Evaluation

# Load predefined profile
weights = get_style_profile("aggressive")

# Create evaluator with custom weights
evaluator = Evaluation(style_weights=weights)

# Evaluate a position
score = evaluator.evaluate(position)
breakdown = evaluator.explain_evaluation(position)
```

### Runtime Profile Selection

```python
# Command-line usage
python -m zyra.cli.runner analyze --style aggressive "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# UCI engine with style parameter
# Set UCI option: "Style aggressive"
```

## Profile Tuning Guidelines

### Weight Ranges
- **0.0 - 0.5**: Significantly reduces this factor's influence
- **0.6 - 0.9**: Below-average emphasis
- **1.0**: Standard weight (baseline)
- **1.1 - 1.5**: Above-average emphasis
- **1.6+**: High priority, may lead to imbalanced play

### Testing Profiles
1. **Self-play games**: Compare different profiles against each other
2. **Position analysis**: Test on various tactical and positional positions
3. **Engine tournaments**: Compete against other engines with different styles
4. **Human feedback**: Get player impressions of playing style

### Common Adjustments

**For more tactical play:**
- Increase `attack_bonus` and `tactical_complications`
- Decrease `risk_aversion` and `pawn_structure`

**For more positional play:**
- Increase `pawn_structure` and `center_control`
- Decrease `attack_bonus` and `tactical_complications`

**For more aggressive play:**
- Increase `attack_bonus` and `piece_mobility`
- Decrease `king_safety` and `risk_aversion`

## Evaluation Breakdown

Each evaluation includes an explainable breakdown showing how different factors contributed to the final score:

```python
explain = evaluator.explain_evaluation(position)
# Returns:
{
    "total": 35.0,
    "terms": {
        "material": 20.0,
        "attacking_motifs": 10.0,
        "center_control": 10.0,
        "rook_files": 5.0,
        "mobility": -8.0,
        "king_safety": -2.0,
        "initiative": -4.0
    },
    "style_weights": { ... },
    "log": ["Evaluation terms: {...}", "Applied style weights: {...}", "Total score (cp): 35.0"]
}
```

This transparency allows you to understand why the engine prefers certain moves and how style profiles affect decision-making.

## Advanced Configuration

### Dynamic Profiles
Profiles can change based on game phase:

```python
OPENING_PROFILE = {...}  # Emphasis on development and center
MIDGAME_PROFILE = {...}  # Tactical and positional balance
ENDGAME_PROFILE = {...}  # King activity and pawn promotion
```

### Context-Aware Weights
Weights can adjust based on position characteristics:

- **Material advantage**: Increase tactical factors
- **Material disadvantage**: Increase defensive factors
- **Time pressure**: Simplify evaluation
- **Complex positions**: Increase mobility factors

## Contributing New Profiles

To add a new predefined profile:

1. Define the weight dictionary
2. Add it to the `get_style_profile()` function
3. Document its characteristics
4. Add test cases for the profile
5. Update this documentation

## Behavioral Testing

The engine includes comprehensive behavioral testing to ensure style profiles create observable differences:

### Stochastic Exploration Tests
- **Fixed seed determinism**: Same seed produces identical results
- **Varied seed diversity**: Different seeds produce varied but valid results
- **Bounded randomness**: Style influence maintains exploration bounds

### Style Differentiation Tests
- **Aggressive vs defensive**: Test tactical vs positional preferences
- **Experimental patterns**: Verify unconventional style behaviors
- **Position-specific tests**: Validate characteristic behaviors on key positions

### Regression Safeguards
- **Style output snapshots**: Golden baseline files for behavioral drift detection
- **Smoke games**: End-to-end self-play validation with limited depth/nodes
- **Automated validation**: CI integration for behavioral consistency

### Running Behavioral Tests
```bash
# Run all behavioral tests
python -m pytest tests/test_behavioral_style_integration.py -v

# Run smoke games
python -m pytest tests/test_smoke_games.py -v

# Generate style output baselines
python -m tests.baseline_style_outputs
```

## Examples

See the `examples/` directory for:
- Profile comparison games
- Position analysis with different styles
- Custom profile creation scripts
- Style tuning tutorials
- Behavioral testing examples
