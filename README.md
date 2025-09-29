# Zyra Chess Engine

An original chess engine with explainable playing style, prioritizing unique evaluation heuristics and experimental search over raw strength.

## Overview

Zyra is designed for developers and chess players seeking novelty and insight rather than top-tier ELO. The engine features:

- **Explainable Evaluation**: Clear, configurable heuristics with term-by-term breakdowns
- **Distinct Personality**: Multiple playing styles (aggressive, defensive, experimental)
- **Modular Architecture**: Clean separation of core logic, search, and evaluation
- **UCI Protocol Support**: Compatible with popular chess GUIs

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Git (for development)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd zyra
   ```

2. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Verify installation:
   ```bash
   python -c "import zyra; print('Zyra installed successfully!')"
   ```

### Basic Usage

#### UCI Mode
Run Zyra as a UCI engine for use with chess GUIs:

```bash
python -m zyra.interfaces.uci
```

#### CLI Tools
Use the command-line interface for testing and analysis:

```bash
# Run perft test for move generation validation
python -m zyra.cli.runner perft 4

# Analyze a position
python -m zyra.cli.runner analyze "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
```

## Development

### Code Quality

The project uses automated formatting and type checking:

- **Black**: Code formatting (line length 100)
- **isort**: Import organization
- **mypy**: Type checking for core modules
- **Pre-commit hooks**: Automatic quality checks on commit

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=zyra

# Run specific test file
pytest tests/test_board.py
```

### Code Style

Follow these conventions:

- Use descriptive, intention-revealing identifiers
- Prefer verb-based function names, noun-based types/values
- Add type hints for all public APIs
- Include docstrings for modules and public functions

## Architecture

### Core Components

- **`core/`**: Board representation, move generation, game rules
- **`search/`**: Monte Carlo Tree Search (MCTS) with configurable playout policies
- **`eval/`**: Explainable evaluation heuristics
- **`interfaces/`**: UCI protocol and CLI adapters
- **`cli/`**: Command-line tools and utilities
- **`tests/`**: Comprehensive test suite

### Design Principles

- **Simplicity First**: Readability over micro-optimizations
- **Modular Design**: Clear separation of concerns
- **Configurable Styles**: Style profiles for different playing personalities
- **Explainable AI**: Transparent evaluation with term breakdowns

## Style Profiles

Zyra supports multiple playing styles through configurable weight profiles:

- **Aggressive**: Favors attacking moves and tactical complications
- **Defensive**: Prioritizes king safety and solid positional play
- **Experimental**: Explores unusual moves and creative patterns

See `STYLE_PROFILES.md` for detailed configuration options.

## Performance Targets

- **Speed**: ~10-20k nodes/sec baseline search
- **Strength**: ~1500-1800 Elo vs online bots (indicative target)
- **Reliability**: Complete games without crashes
- **Explainability**: Clear evaluation breakdowns

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes following the code style guidelines
4. Add tests for new functionality
5. Ensure all pre-commit hooks pass
6. Submit a pull request

### Development Workflow

This project uses trunk-based development:

- Short-lived feature branches
- Pull requests required before merge
- CI must pass tests and formatting
- Conventional commit messages

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by the need for explainable AI in chess engines
- Built with modern Python tooling and best practices
- Designed for educational and experimental purposes

## Search Engine

Zyra uses Monte Carlo Tree Search (MCTS) as its primary search algorithm with the following features:

### MCTS Configuration
- **Playout Limits**: Configurable maximum playouts per search
- **Time Control**: Movetime limits for tournament play
- **Deterministic Mode**: Fixed seed support for reproducible analysis
- **Move Ordering**: Heuristic prioritization of captures, checks, and promotions

### UCI Integration
- **`go movetime X`**: Search with X milliseconds time limit
- **`go nodes N`**: Search with N maximum playouts
- **`go depth D`**: Unsupported (logs non-fatal warning)
- **`bestmove`**: Returns the selected move in UCI format

### Usage Examples
```bash
# UCI mode with time control
echo "go movetime 1000" | python -m zyra.interfaces.uci

# Programmatic search
from search.mcts import MCTSSearch
from core.board import Board

board = Board()
board.set_startpos()
search = MCTSSearch(max_playouts=1000, seed=42)
best_move = search.search(board)
```

## Roadmap

- [x] Complete board representation and move generation
- [x] Implement MCTS search with configurable policies
- [ ] Add explainable evaluation heuristics
- [ ] UCI protocol compliance testing
- [ ] Performance optimization and profiling
- [ ] Style profile tuning and validation
