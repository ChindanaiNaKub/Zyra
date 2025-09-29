# Behavioral Testing Guide

This guide explains how to run and understand the behavioral testing framework for Zyra's style system integration.

## Overview

The behavioral testing framework ensures that style profiles create observable behavioral differences in search behavior, move ordering, and playout policies. It includes stochastic exploration tests, style differentiation tests, and regression safeguards.

## Test Categories

### 1. Stochastic Exploration Tests

These tests verify that style-aware playouts maintain bounded randomness while expressing personality.

#### Key Tests:
- **Fixed seed determinism**: Same seed produces identical results
- **Varied seed diversity**: Different seeds produce varied but valid results
- **Style-aware playout policy**: Styles influence move selection during simulation

#### Running:
```bash
python -m pytest tests/test_behavioral_style_integration.py::TestStochasticExploration -v
```

### 2. Style Differentiation Tests

These tests verify that different styles produce measurably different behaviors.

#### Key Tests:
- **Aggressive vs defensive preferences**: Test tactical vs positional move preferences
- **Experimental style patterns**: Verify unconventional style behaviors
- **Position-specific behaviors**: Validate characteristic behaviors on key positions

#### Running:
```bash
python -m pytest tests/test_behavioral_style_integration.py::TestStyleDifferentiation -v
```

### 3. Behavioral Validation Tests

These tests ensure style profiles produce consistent and valid outputs.

#### Key Tests:
- **Style output differentiation**: Verify styles produce measurably different evaluations
- **Consistency across positions**: Test style behavior across multiple positions
- **Search depth and node limits**: Validate style-aware search with different limits

#### Running:
```bash
python -m pytest tests/test_behavioral_style_integration.py::TestBehavioralValidation -v
```

### 4. Regression Safeguards

These tests detect behavioral drift and ensure consistency over time.

#### Key Tests:
- **Style output consistency**: Verify evaluations remain consistent across runs
- **Move ordering consistency**: Test that style-aware ordering is deterministic
- **Smoke games**: End-to-end validation with self-play games

#### Running:
```bash
python -m pytest tests/test_behavioral_style_integration.py::TestRegressionSafeguards -v
```

## Smoke Games

Smoke games are short self-play games that validate end-to-end functionality.

### Running Smoke Games:
```bash
python -m pytest tests/test_smoke_games.py -v
```

### Smoke Game Types:
- **Single style games**: Each style profile plays against itself
- **Style vs style games**: Different styles compete against each other
- **UCI integration tests**: Validate UCI engine with different styles

## Style Output Snapshots

Style output snapshots provide golden baseline files for regression testing.

### Generating Baselines:
```bash
python -m tests.baseline_style_outputs
```

This creates baseline files in `tests/baselines/` for each style profile containing:
- Evaluation scores for key positions
- Move ordering preferences
- MCTS search results

### Validating Against Baselines:
```python
from tests.baseline_style_outputs import StyleOutputSnapshots

snapshots = StyleOutputSnapshots()
results = snapshots.validate_against_baseline("aggressive")
print(f"Matches: {results['matches']}, Mismatches: {results['mismatches']}")
```

## Test Configuration

### Adjusting Test Parameters:
```python
# In test files, you can adjust:
max_playouts = 100    # Number of MCTS simulations
max_moves = 10        # Maximum moves in smoke games
seed = 42            # Random seed for reproducibility
```

### Performance Considerations:
- Lower `max_playouts` for faster tests (but less statistical confidence)
- Higher `max_playouts` for more reliable results (but slower tests)
- Use fixed seeds for deterministic testing

## Interpreting Results

### Expected Behaviors:
- **Deterministic results**: Fixed seeds should produce identical outputs
- **Style differentiation**: Different styles should show measurable differences
- **Valid outputs**: All styles should produce legal moves and valid evaluations

### Common Issues:
- **No differentiation**: Styles may be too similar or test positions too simple
- **Inconsistent results**: Check for proper seed usage and deterministic behavior
- **Performance issues**: Adjust test parameters or use fewer test positions

## Continuous Integration

The behavioral tests are designed to run in CI environments:

### CI Configuration:
```yaml
# Example GitHub Actions workflow
- name: Run Behavioral Tests
  run: |
    python -m pytest tests/test_behavioral_style_integration.py -v
    python -m pytest tests/test_smoke_games.py -v
```

### Baseline Updates:
When style behavior changes intentionally, update baselines:
```bash
python -m tests.baseline_style_outputs
git add tests/baselines/
git commit -m "Update style output baselines"
```

## Troubleshooting

### Tests Failing:
1. **Check style profile validity**: Ensure style weights are properly configured
2. **Verify deterministic behavior**: Use fixed seeds consistently
3. **Review test parameters**: Adjust playouts/moves if needed
4. **Check for flaky tests**: Increase statistical confidence with more samples

### Performance Issues:
1. **Reduce test scope**: Use fewer positions or lower playouts
2. **Parallel execution**: Run tests in parallel where possible
3. **Selective testing**: Run only relevant test categories

### Baseline Mismatches:
1. **Intentional changes**: Update baselines if behavior changed deliberately
2. **Unintended changes**: Investigate what caused the behavioral drift
3. **Floating point issues**: Check for numerical precision problems

## Contributing

When adding new behavioral tests:

1. **Follow naming conventions**: Use descriptive test names
2. **Include docstrings**: Explain what the test validates
3. **Use subTests**: Group related test cases
4. **Add to appropriate category**: Place tests in the right test class
5. **Update documentation**: Document new test capabilities

### Example Test Structure:
```python
def test_new_behavioral_feature(self):
    """Test that new feature produces expected behavioral differences."""
    # Arrange
    board = Board()
    board.set_startpos()

    # Act
    result = self.run_behavioral_test(board)

    # Assert
    self.assertIsInstance(result, expected_type)
    self.assertTrue(result.meets_behavioral_criteria())
```

## Further Reading

- [Style Profiles Configuration](STYLE_PROFILES.md)
- [MCTS Search Implementation](search/mcts.py)
- [Evaluation Heuristics](eval/heuristics.py)
- [OpenSpec Phase 4 Proposal](openspec/changes/add-phase-4-styles-testing/proposal.md)
