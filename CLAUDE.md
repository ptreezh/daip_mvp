# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE) is an intelligent collaboration platform that supports multi-AI role collaboration, debate systems, and knowledge management. The system is built with Python FastAPI for the backend and includes CLI tools, web interfaces, and various AI/ML components.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies with Poetry
poetry install

# Activate virtual environment
poetry shell

# Install specific dependencies
poetry add package_name
```

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

# Run tests and exit on first failure
pytest -x

# Run tests in parallel
pytest -n auto

# Run specific test category
pytest tests/cli/ -v
pytest tests/core_services/ -v
```

### Code Quality
```bash
# Lint with ruff
ruff check src/ tests/

# Format code with black
black src/ tests/

# Type checking with mypy
mypy src/

# Fix linting issues automatically
ruff check --fix src/ tests/
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

# Run with Poetry
poetry run python -m src.cli.main
```

### API Server
```bash
# Start FastAPI server with auto-reload
uvicorn src.main:app --reload

# Run on specific port
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Production deployment (no reload)
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Comprehensive Testing
```bash
# Run the complete test suite
./run_comprehensive_tests.bat  # Windows
./run_comprehensive_tests.sh   # Linux/Mac

# Run DDD integration tests
python tests/ddd/test_runner.py
```

## Architecture Overview

### Core Components

1. **FastAPI Backend** (`src/main.py`)
   - Main API server with comprehensive routing
   - Central application state management
   - Health check and status endpoints
   - CORS middleware configuration

2. **Application Layer** (`src/application/`)
   - `personal_assistant_router.py` - Routes user queries to appropriate services
   - `session_manager.py` - Manages user sessions and context
   - `task_orchestrator.py` - Coordinates complex task execution
   - `entrance_selector.py` - Dual entrance system management

3. **Core Services** (`src/core_services/`)
   - `role_manager.py` - Manages AI roles and their definitions
   - `wiki_service.py` - Wiki collaboration and version control
   - `memory_service.py` - Memory management and retrieval
   - `synthesis_engine.py` - Content synthesis and analysis
   - `debate_manager.py` - Multi-role debate coordination
   - `intent_analysis_service.py` - User intent recognition
   - `user_profile_service.py` - User profile management

4. **CLI Interface** (`src/cli/`)
   - `main.py` - Main CLI entry point with Typer
   - `chat_commands.py` - Chat and communication commands
   - `wiki_commands.py` - Wiki management commands
   - `commands/` - Various command implementations
     - `role_commands.py` - Role management
     - `workflow_commands.py` - Workflow execution
     - `system_commands.py` - System operations
     - `debate_commands.py` - Debate management

5. **Virtual Role Chat** (`src/virtual_role_chat/`)
   - `chat_coordinator.py` - Coordinates multi-role conversations
   - `chat_room_manager.py` - Manages chat rooms and sessions
   - `chat_session_service.py` - Session management
   - `cognitive_agent/` - Advanced cognitive agent implementations

6. **Institutional Primitives** (`src/institutional_primitives/`)
   - Advanced workflow and consensus patterns
   - Customizable debate rules and protocols
   - Multi-perspective analysis frameworks

7. **Domain-Driven Design** (`src/domain/`)
   - Domain models and business logic
   - Aggregates, entities, and value objects
   - Domain services implementation

### Key Dependencies

- **FastAPI** - Web framework for API
- **Typer** - CLI framework
- **ChromaDB** - Vector database for role embeddings
- **Ollama** - Local LLM provider
- **Pydantic** - Data validation and settings management
- **Rich** - CLI formatting and output
- **Poetry** - Dependency management and packaging
- **Pytest** - Testing framework
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **Mypy** - Static type checking

### Configuration System

Configuration is managed through `src/config.py` with Pydantic models:
- `config.yaml` - Main configuration file
- Environment variables override config values
- Settings include LLM configuration, vector store paths, logging levels
- Configuration validation at application startup

### Data Storage

- **Vector Database**: ChromaDB for role embeddings and semantic search
- **File Storage**: JSON files for wiki content, chat logs, user profiles
- **Memory Banks**: Structured memory storage in `data/memory_banks/`
- **Wiki Data**: Markdown files with version control in `data/wiki/`
- **Session Data**: User sessions and authentication in `data/auth/`

### Testing Structure

- `tests/` - Root test directory
- `tests/core_services/` - Tests for core services
- `tests/cli/` - CLI interface tests
- `tests/application/` - Application layer tests
- `tests/integration/` - Integration tests
- `tests/ddd/` - Domain-driven design tests
- `tests/conftest.py` - Pytest configuration and fixtures
- Comprehensive end-to-end testing suite

### Code Style and Quality

- **Line Length**: 120 characters
- **Formatter**: Black (configured in `pyproject.toml`)
- **Linter**: Ruff with custom rules (configured in `ruff.toml`)
- **Type Hints**: Required for all new code
- **Docstrings**: Google-style docstrings preferred
- **Async/Await**: Used for I/O-bound operations

## Development Guidelines

### Project Structure Conventions

1. **Service Layer**: Core business logic in `src/core_services/`
2. **Application Layer**: Use cases and orchestration in `src/application/`
3. **CLI Layer**: Command-line interface in `src/cli/`
4. **API Layer**: REST API endpoints in `src/api/`
5. **Models**: Data models near their usage context
6. **Domain Layer**: Business domain logic in `src/domain/`
7. **Infrastructure**: Technical implementations in `src/infrastructure/`

### Error Handling

- Use custom exceptions from `src/core/exceptions.py`
- Implement proper logging with appropriate levels
- Graceful degradation for non-critical services
- User-friendly error messages in CLI responses
- Comprehensive error handling in API endpoints

### Asynchronous Patterns

- Use `asyncio` for I/O-bound operations
- Proper error handling in async contexts
- Avoid blocking operations in async functions
- Use `asyncio.run()` for async entry points
- Implement proper cancellation handling

### Configuration Management

- Use `src.config.settings` for accessing configuration
- Never hardcode configuration values
- Support environment variable overrides
- Validate configuration at startup
- Use type-safe configuration with Pydantic

### Memory and State Management

- Use `AppState` class for shared application state
- Implement proper caching strategies
- Handle service initialization order carefully
- Use lazy loading for optional services
- Manage vector database connections properly

### Testing Best Practices

- Write unit tests for core services
- Include integration tests for complex workflows
- Mock external dependencies (LLM calls, database)
- Test both success and error scenarios
- Use fixtures for common test setup
- Include comprehensive end-to-end tests

### CLI Development

- Use Typer for command-line interfaces
- Provide helpful error messages and usage examples
- Support both interactive and batch modes
- Include proper input validation
- Use Rich for formatted output
- Implement comprehensive help documentation

## Common Issues and Solutions

### Service Initialization Order

Some services depend on others being initialized first. The `AppState` class handles this automatically through its initialization order. When adding new services, consider their dependencies.

### Vector Database Issues

If ChromaDB fails to initialize:
1. Check if the data directory exists and is writable
2. Verify the ChromaDB version compatibility
3. Try deleting the vector database to force re-initialization
4. Check collection names and configurations

### LLM Connection Problems

If Ollama connections fail:
1. Verify Ollama is running on the configured port
2. Check if the required models are downloaded
3. Test the connection manually with `ollama list`
4. Verify model names in configuration

### Memory Management

For memory-related issues:
1. Check memory bank directory permissions
2. Verify memory consolidation service is running
3. Monitor memory usage and implement cleanup if needed
4. Validate memory storage adapters

### CLI Performance

For slow CLI operations:
1. Implement proper caching for repeated operations
2. Use async operations for I/O-bound tasks
3. Consider pagination for large result sets
4. Optimize vector database queries

## Extension Points

### Adding New AI Roles

1. Create role definition JSON files in `roles/`
2. Add role to `configs/roles.yaml` if needed
3. Update role embeddings in vector database
4. Test role functionality with sample queries
5. Register role in role manager service

### Creating New Commands

1. Add command functions in appropriate CLI module
2. Register with Typer app in `src/cli/main.py`
3. Add tests in `tests/cli/`
4. Update help documentation
5. Include proper error handling

### Extending Core Services

1. Follow the existing service pattern
2. Add proper dependency injection
3. Include comprehensive error handling
4. Write unit and integration tests
5. Document service functionality

### Adding New API Endpoints

1. Create router in `src/api/routers/`
2. Add proper request/response models
3. Include authentication if needed
4. Register router in `src/main.py`
5. Add comprehensive testing

## Performance Considerations

- Use lazy loading for heavy services
- Implement proper caching strategies
- Monitor memory usage, especially for vector operations
- Consider connection pooling for database operations
- Use async operations for I/O-bound tasks
- Optimize vector database queries with proper indexing

## Security Considerations

- Never commit API keys or sensitive configuration
- Validate all user inputs properly
- Implement proper authentication for protected endpoints
- Use environment variables for sensitive configuration
- Follow principle of least privilege for service permissions
- Sanitize user inputs to prevent injection attacks
- Implement proper CORS configuration for production