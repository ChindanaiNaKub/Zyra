## Why

The project needs a solid foundation with proper development tooling, repository structure, and Python project configuration before implementing the chess engine components. This establishes code quality standards, testing infrastructure, and modular architecture as specified in the project conventions.

## What Changes

- Initialize Python project with `pyproject.toml` configuration
- Set up code formatting with `black` (line length 100) and `isort`
- Configure type checking with `mypy` for core modules
- Create modular directory structure: `core/`, `search/`, `eval/`, `interfaces/`, `cli/`, `tests/`
- Add pre-commit hooks for linting and formatting
- Create `README.md` with quick start guide
- Add `STYLE_PROFILES.md` for engine personality configuration
- Set up trunk-based branching with CI requirements

## Impact

- Affected specs: New `project-infrastructure` capability
- Affected code: Repository root, new module directories, configuration files
- Establishes foundation for all subsequent chess engine development
