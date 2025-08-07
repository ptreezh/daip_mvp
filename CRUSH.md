# DAIP-MVP Development Commands & Style Guide

## Build & Quality Commands

### Code Quality (MUST PASS BEFORE COMMIT)
```bash
# Format code
black src/ tests/

# Type checking  
mypy src/

# Linting
ruff check src/ tests/
ruff format src/ tests/

# Run all quality checks
black src/ tests/ && ruff check src/ tests/ && mypy src/
```

### Testing
```bash
# Run all tests
pytest

# Run single test file
pytest tests/test_specific_file.py

# Run single test function
pytest tests/test_file.py::test_function_name

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/core_services/
pytest tests/cli/
```

### Development Server
```bash
# Start FastAPI backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Quick start alternatives
python run.py
python real_llm_integrated_demo.py
```

## Code Style Guidelines

### File Headers (MANDATORY)
All .py files must include:
```python
# -*- coding: utf-8 -*-
"""
@Time    : YYYY-MM-DD HH:MM:SS
@Author  : DAIP-LIVE Team
@File    : filename.py
@Description:
    [Purpose description]
"""
```

### Type Annotations
- Complete type hints required for all functions (mypy strict mode)
- Use specific types, avoid Any when possible
- Import from typing module as needed

### Imports
- Use isort formatting (handled by ruff)
- Group imports: standard library, third-party, local application
- Use absolute imports for project modules

### Naming Conventions
- Classes: PascalCase (RoleManager, ConsensusAlgorithm)
- Functions: snake_case (load_roles, calculate_consensus)
- Variables: snake_case (user_input, expert_list)
- Constants: UPPER_SNAKE_CASE (MAX_RETRIES, DEFAULT_PORT)

### Error Handling
- Use specific exceptions, avoid generic except:
- Define custom exceptions in src/core/exceptions.py
- Log errors with appropriate levels
- Implement graceful degradation

### Docstrings
- Google Style format for all functions, classes, modules
- Include Args, Returns, Raises sections as appropriate
- 100% docstring coverage for public APIs

### Testing Standards
- Test files named test_*.py
- Test functions named test_*
- Minimum 80% coverage for new code
- Mock external dependencies (LLM calls, file I/O)

## Architecture Rules
- Strict layered architecture - no cross-layer dependencies
- Use dependency injection through AppState only
- No direct imports between services
- Follow service integration patterns

## CLI Usage
```bash
# CLI entry point
daip-cli status

# Start debates
daip-cli start "topic" --role "expert1" --role "expert2" --rounds 3
```

## Pre-commit Hooks
```bash
# Run all hooks before committing
pre-commit run --all-files
```

## Environment Setup
```bash
# Install dependencies
poetry install

# Install Ollama models
ollama pull llama3:instruct
ollama pull nomic-embed-text:latest
```