# DAIP-LIVE Development Guide

## Project Overview
DAIP-LIVE is a Dynamic AI-driven Project-execution LIVE system built in Python using Poetry for dependency management. It provides an interactive TUI (Terminal User Interface) for AI agent orchestration, multi-agent debates, knowledge management, and project scaffolding.

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Code Quality & Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/daip_live

# Run specific test file
pytest tests/test_cli/test_cli.py

# Run linting and formatting
ruff check --fix
ruff format

# Run type checking
mypy src/daip_live --strict

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Application Commands
```bash
# Main CLI entry point
poetry run daip "accomplish this goal"

# Personal assistant shortcut
poetry run daip pa "accomplish this goal"

# Start interactive TUI with specific role
poetry run daip run "goal description" --role "role_name"

# Knowledge base sync
poetry run daip sync

# List sessions
poetry run daip session list

# View specific session
poetry run daip session view <session_id>

# Start multi-agent debate
poetry run daip debate "debate topic" --roles "pro_arguer,con_arguer" --rounds 2

# Project scaffolding
poetry run daip project scaffold --description "project description"
```

## Architecture Overview

### Core Components Structure
The project follows a modular architecture with clear separation of concerns:

- **`src/daip_live/core/`** - Core models, interfaces, and exceptions
- **`src/daip_live/agent_engine/`** - AI agent execution engine
- **`src/daip_live/memory/`** - Session and memory management
- **`src/daip_live/knowledge/`** - Knowledge base and document management
- **`src/daip_live/model_provider/`** - LLM provider abstraction (LiteLLM)
- **`src/daip_live/persistence/`** - Database operations (SQLAlchemy)
- **`src/daip_live/p4_role_manager_tools/`** - Role and tool management
- **`src/daip_live/p7_gui/`** - GUI components
- **`src/daip_live/p8_debate_system/`** - Multi-agent debate orchestration
- **`src/daip_live/scaffolding/`** - Project generation and scaffolding

### Key Architectural Patterns

1. **Session-Based Architecture**: All interactions are managed through `Session` objects that track multi-agent conversations, debates, and workflows.

2. **Event-Driven Agent System**: The `AgentExecutor` uses an event system with states like `THINKING`, `EXECUTING_TOOL`, `RESPONDING` for real-time status tracking.

3. **Modular Tool System**: Tools are managed through `ToolManager` with permission-based access control.

4. **Knowledge Management**: Vector-based knowledge retrieval using FAISS with automatic document synchronization.

5. **Multi-Agent Orchestration**: Support for debate systems and role-based agent interactions through `DebateManager` and `RoleManager`.

### Configuration System
- Uses Pydantic models for type-safe configuration validation
- Configuration loaded from `config.yaml` with automatic defaults
- Global `config_manager` instance provides centralized access

### Database Schema
- SQLAlchemy-based persistence layer
- Session history, knowledge sources, and metadata storage
- SQLite database with configurable path

## Critical Development Rules

### Import Convention
**CRITICAL**: All internal module imports MUST use the `daip_live` package prefix:
```python
# ✅ Correct
from daip_live.core.models import Session
from daip_live.agent_engine.executor import AgentExecutor

# ❌ Wrong - will cause import errors
from src.daip_live.core.models import Session
```

### Project Structure Convention
- Follow strict `src-layout` structure
- All source code MUST be in `src/daip_live/` directory
- Check for file/directory naming conflicts before creating new modules
- Each new package directory MUST include `__init__.py`

### TDD Requirements
- Write tests BEFORE implementation (Red-Green-Refactor cycle)
- Maintain 90%+ test coverage
- All code must pass static analysis (ruff, mypy)
- Use pytest with async support for testing

### Code Quality Standards
- Follow SOLID principles
- Use type hints throughout (enforced by mypy --strict)
- Pydantic models for data validation
- Rich console output for user interfaces

## Key Integration Points

### CLI to TUI Flow
The main entry point (`cli.py`) orchestrates component initialization:
1. Config loading and validation
2. Database manager setup
3. Knowledge manager with embedding provider
4. Agent executor with session/memory management
5. TUI launch with all dependencies injected

### Multi-Agent Session Management
Sessions support multiple participant types:
- `user_human` - Human user input
- `role_<name>_<id>` - AI agent roles
- Dialogue turns tracked with timestamps and participant IDs

### Tool Permission System
Tools require explicit permission configuration:
- Default policy: `deny`, `allow`, or `ask`
- Per-tool overrides in configuration
- Runtime permission requests through event system

### Knowledge Base Integration
- Automatic document synchronization from `docs/` directory
- Vector embeddings for semantic search
- File hash tracking for incremental updates
- Integration with agent reasoning through retrieval

## Testing Strategy
- Unit tests for individual components
- Integration tests for multi-component workflows
- TUI interaction tests using textual testing framework
- Mock external dependencies (LLM providers, file system)
- Async test support with pytest-asyncio