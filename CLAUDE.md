# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE) is an intelligent collaboration platform that supports multi-AI role collaboration, debate systems, and knowledge management. The system is built with Python FastAPI for the backend and includes CLI tools, web interfaces, and various AI/ML components.

## Common Development Commands

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core_scenarios.py

# Run with coverage
pytest --cov=src

# Run tests with verbose output
pytest -v --tb=short
```

### Code Quality
```bash
# Lint with ruff
ruff check src/ tests/

# Format code with black
black src/ tests/

# Type checking with mypy
mypy src/
```

### CLI Usage
```bash
# Run the main CLI
python -m src.cli.main

# Start a debate
python -m src.cli.main debate start "AI Ethics Discussion" --role "AI Ethicist" --role "Philosopher"

# Check system status
python -m src.cli.main status

# Interactive mode (no arguments)
python -m src.cli.main
```

### API Server
```bash
# Start FastAPI server
uvicorn src.main:app --reload

# Run on specific port
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Architecture Overview

### Core Components

1. **FastAPI Backend** (`src/main.py`)
   - Main API server with comprehensive routing
   - Central application state management
   - Health check and status endpoints

2. **Application Layer** (`src/application/`)
   - `personal_assistant_router.py` - Routes user queries to appropriate services
   - `session_manager.py` - Manages user sessions and context
   - `task_orchestrator.py` - Coordinates complex task execution

3. **Core Services** (`src/core_services/`)
   - `role_manager.py` - Manages AI roles and their definitions
   - `wiki_service.py` - Wiki collaboration and version control
   - `memory_service.py` - Memory management and retrieval
   - `synthesis_engine.py` - Content synthesis and analysis
   - `debate_manager.py` - Multi-role debate coordination

4. **CLI Interface** (`src/cli/`)
   - `main.py` - Main CLI entry point with Typer
   - `chat_commands.py` - Chat and communication commands
   - `wiki_commands.py` - Wiki management commands
   - `commands/` - Various command implementations

5. **Virtual Role Chat** (`src/virtual_role_chat/`)
   - `chat_coordinator.py` - Coordinates multi-role conversations
   - `chat_room_manager.py` - Manages chat rooms and sessions
   - `models.py` - Data models for chat system

### Key Dependencies

- **FastAPI** - Web framework for API
- **Typer** - CLI framework
- **ChromaDB** - Vector database for role embeddings
- **Ollama** - Local LLM provider
- **Pydantic** - Data validation and settings management
- **Rich** - CLI formatting and output

### Configuration System

Configuration is managed through `src/config.py` with Pydantic models:
- `config.yaml` - Main configuration file
- Environment variables override config values
- Settings include LLM configuration, vector store paths, logging levels

### Data Storage

- **Vector Database**: ChromaDB for role embeddings and semantic search
- **File Storage**: JSON files for wiki content, chat logs, user profiles
- **Memory Banks**: Structured memory storage in `data/memory_banks/`
- **Wiki Data**: Markdown files with version control in `data/wiki/`

### Testing Structure

- `tests/` - Root test directory
- `tests/core_services/` - Tests for core services
- `tests/cli/` - CLI interface tests
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Pytest configuration and fixtures

### Code Style and Quality

- **Line Length**: 120 characters
- **Formatter**: Black (configured in `pyproject.toml`)
- **Linter**: Ruff with custom rules (configured in `ruff.toml`)
- **Type Hints**: Required for all new code
- **Docstrings**: Google-style docstrings preferred

## Development Guidelines

### Project Structure Conventions

1. **Service Layer**: Core business logic in `src/core_services/`
2. **Application Layer**: Use cases and orchestration in `src/application/`
3. **CLI Layer**: Command-line interface in `src/cli/`
4. **API Layer**: REST API endpoints in `src/api/`
5. **Models**: Data models near their usage context

### Error Handling

- Use custom exceptions from `src/core/exceptions.py`
- Implement proper logging with appropriate levels
- Graceful degradation for non-critical services
- User-friendly error messages in CLI responses

### Asynchronous Patterns

- Use `asyncio` for I/O-bound operations
- Proper error handling in async contexts
- Avoid blocking operations in async functions
- Use `asyncio.run()` for async entry points

### Configuration Management

- Use `src.config.settings` for accessing configuration
- Never hardcode configuration values
- Support environment variable overrides
- Validate configuration at startup

### Memory and State Management

- Use `AppState` class for shared application state
- Implement proper caching strategies
- Handle service initialization order carefully
- Use lazy loading for optional services

### Testing Best Practices

- Write unit tests for core services
- Include integration tests for complex workflows
- Mock external dependencies (LLM calls, database)
- Test both success and error scenarios
- Use fixtures for common test setup

### CLI Development

- Use Typer for command-line interfaces
- Provide helpful error messages and usage examples
- Support both interactive and batch modes
- Include proper input validation
- Use Rich for formatted output

## Common Issues and Solutions

### Service Initialization Order

Some services depend on others being initialized first. The `AppState` class handles this automatically through its initialization order. When adding new services, consider their dependencies.

### Vector Database Issues

If ChromaDB fails to initialize:
1. Check if the data directory exists and is writable
2. Verify the ChromaDB version compatibility
3. Try deleting the vector database to force re-initialization

### LLM Connection Problems

If Ollama connections fail:
1. Verify Ollama is running on the configured port
2. Check if the required models are downloaded
3. Test the connection manually with `ollama list`

### Memory Management

For memory-related issues:
1. Check memory bank directory permissions
2. Verify memory consolidation service is running
3. Monitor memory usage and implement cleanup if needed

### CLI Performance

For slow CLI operations:
1. Implement proper caching for repeated operations
2. Use async operations for I/O-bound tasks
3. Consider pagination for large result sets

## Extension Points

### Adding New AI Roles

1. Create role definition JSON files in `roles/`
2. Add role to `configs/roles.yaml` if needed
3. Update role embeddings in vector database
4. Test role functionality with sample queries

### Creating New Commands

1. Add command functions in appropriate CLI module
2. Register with Typer app in `src/cli/main.py`
3. Add tests in `tests/cli/`
4. Update help documentation

### Extending Core Services

1. Follow the existing service pattern
2. Add proper dependency injection
3. Include comprehensive error handling
4. Write unit and integration tests

### Adding New API Endpoints

1. Create router in `src/api/routers/`
2. Add proper request/response models
3. Include authentication if needed
4. Register router in `src/main.py`

## Performance Considerations

- Use lazy loading for heavy services
- Implement proper caching strategies
- Monitor memory usage, especially for vector operations
- Consider connection pooling for database operations
- Use async operations for I/O-bound tasks

## Security Considerations

- Never commit API keys or sensitive configuration
- Validate all user inputs properly
- Implement proper authentication for protected endpoints
- Use environment variables for sensitive configuration
- Follow principle of least privilege for service permissions