# Style Profiles Configuration

Zyra chess engine supports configurable playing styles through weight profiles that influence evaluation and search behavior.

## Overview

Style profiles allow you to customize the engine's playing personality by adjusting the relative importance of different evaluation factors. This creates distinct playing styles while maintaining explainable, transparent decision-making.

## Predefined Profiles

### Aggressive Style
Favors attacking moves, tactical complications, and dynamic play.

```python
AGGRESSIVE_WEIGHTS = {
    "attack_bonus": 1.5,        # Bonus for attacking enemy pieces
    "center_control": 1.2,      # Emphasis on central squares
    "piece_mobility": 1.3,      # Rewards active piece placement
    "king_safety": 0.8,         # Lower priority for defensive moves
    "pawn_structure": 0.9,      # Less emphasis on pawn chains
    "tactical_complications": 1.4,  # Seeks tactical opportunities
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
    "king_safety": 1.5,         # High priority for king protection
    "pawn_structure": 1.3,      # Values solid pawn chains
    "defensive_moves": 1.2,     # Rewards prophylactic moves
    "attack_bonus": 0.7,        # Lower aggression
    "center_control": 1.0,      # Standard central emphasis
    "risk_aversion": 1.4,       # Avoids unclear positions
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
    "mobility": 1.4,            # High emphasis on piece freedom
    "unusual_moves": 1.1,       # Slight bonus for non-standard moves
    "creative_patterns": 1.2,   # Rewards artistic piece coordination
    "balance": 0.9,             # Slightly less emphasis on material
    "center_control": 1.0,      # Standard central play
    "king_safety": 1.0,         # Standard safety consideration
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

### Available Weight Categories

#### Material Factors
- `material_balance`: Standard piece values (Queen=9, Rook=5, etc.)
- `piece_activity`: Bonus for active vs passive pieces
- `coordination_bonus`: Reward for piece cooperation

#### Positional Factors
- `center_control`: Control of central squares (d4, d5, e4, e5)
- `pawn_structure`: Pawn chain and structure evaluation
- `piece_mobility`: Number of legal moves available
- `king_safety`: King shelter and defensive pieces

#### Tactical Factors
- `attack_bonus`: Bonus for attacking enemy pieces
- `tactical_complications`: Seeks tactical opportunities
- `defensive_moves`: Rewards prophylactic and defensive moves

#### Style Modifiers
- `risk_aversion`: Avoids unclear or risky positions
- `unusual_moves`: Bonus for non-standard move patterns
- `creative_patterns`: Rewards artistic piece coordination
- `balance`: Emphasis on positional balance

## Configuration Usage

### Loading a Profile

```python
from zyra.eval.heuristics import get_style_profile, Evaluation

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
breakdown = evaluator.explain_evaluation(position)
# Returns:
{
    "material": 0.2,
    "center_control": 0.3,
    "king_safety": -0.1,
    "attack_bonus": 0.4,
    "total": 0.8
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

## Examples

See the `examples/` directory for:
- Profile comparison games
- Position analysis with different styles
- Custom profile creation scripts
- Style tuning tutorials
