# DAIP-LIVE Development Guidelines

## Build Commands
- **Install dependencies**: `poetry install` or `pip install -r requirements.txt`
- **Run tests**: `pytest` (single test: `pytest tests/path/to/test.py::test_name`)
- **Lint code**: `ruff check --fix .`
- **Format code**: `ruff format .`
- **Type check**: `mypy .`
- **Run pre-commit hooks**: `pre-commit run --all-files`
- **Build package**: `poetry build`

## Code Style Guidelines

### Formatting & Linting
- Line length: 120 characters
- Use `ruff` for linting and formatting (configured in pyproject.toml)
- Use `black` code style (120 char lines)
- Pre-commit hooks enforce code quality

### Type Hints
- **Required**: All function signatures and class attributes must have PEP 484 type hints
- Use `from typing import Optional, List, Dict, Union` as needed
- Return types are mandatory for all functions

### Imports
- Use `isort` rules (handled by ruff)
- Group imports: standard library, third-party, local application
- Use absolute imports: `from src.module import thing`
- Avoid circular imports

### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_single_underscore_prefix`

### Error Handling
- Use specific exception types
- Always include context in error messages
- Log errors with appropriate levels
- Use `raise` with meaningful messages

### Documentation
- **Required**: Google-style docstrings for all public modules, classes, and functions
- Use triple quotes: `"""Docstring here"""`
- Include Args, Returns, Raises sections as needed

### Testing
- Use `pytest` framework
- Test files: `test_*.py` in `tests/` directory
- Mock only external dependencies, never internal business logic
- Each test should validate real system functionality

### Logging
- Use lazy formatting: `logger.info("User %s logged in", user_id)`
- Configure logging levels in settings
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### Project Structure
- Production code: `src/` directory
- Tests: `tests/` directory
- CLI entry point: `daip-cli.py` → `src/cli/main.py`
- Configuration: `config.yaml` and `src/config.py`

### Anti-Patterns
- **No stubs or placeholder code** in production
- **No mutable global state** - pass state explicitly
- **No redundant code** - DRY principle strictly enforced
- **No mocking of internal logic** - test real implementations