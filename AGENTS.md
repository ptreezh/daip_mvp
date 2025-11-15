# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

DAIP-LIVE (Dynamic AI-driven Project-execution LIVE system) is a local-first AI agent workstation designed for single-user environments. It's a modular monolith application that enables multi-AI role collaboration, structured debates, and local knowledge management with a focus on privacy, transparency, and user control.

## Core Architecture Principles

- **Local-First**: All core data (knowledge base, configurations, session history) stored locally in SQLite and file system
- **Modular Monolith**: Single Python process with clear module boundaries communicating via direct function calls
- **Event-Driven Agent Execution**: Dynamic agent loops rather than static workflows
- **Transparency**: Real-time display of AI thinking processes and user intervention capabilities

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running the Application
```bash
# Start interactive TUI session
poetry run daip run

# Sync knowledge base manually
poetry run daip sync

# Manage sessions
poetry run daip session list
poetry run daip session show <session_id>

# Run debates
poetry run daip debate start <topic>
poetry run daip debate list

# Manage AI roles
poetry run daip role list
poetry run daip role show <role_name>

# Manage models
poetry run daip model list
poetry run daip model status

# Project scaffolding
poetry run daip project create <name>
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_cli.py

# Run tests with verbose output
poetry run pytest -v

# Run tests with coverage
poetry run pytest --cov=src

# Run only specific test patterns
poetry run pytest -k "test_debate"

# Run async tests specifically
poetry run pytest --asyncio-mode=auto
```

### Code Quality
```bash
# Lint code
poetry run ruff check src/

# Format code
poetry run ruff format src/

# Type checking
poetry run mypy src/

# Apply lint fixes
poetry run ruff check --fix src/

# Check for specific issues
poetry run ruff check --select E,F,W src/
```

## Key Architecture Components

### Core Modules (P1-P8 Priority System)

**P1 - Data Persistence**: `src/daip_live/persistence/`
- SQLite database management (`database.py`)
- Schema definitions (`tables.py`)
- Knowledge metadata storage

**P2 - Knowledge Management**: `src/daip_live/knowledge/`, `src/daip_live/wiki/`
- Document ingestion and vectorization
- FAISS/ChromaDB vector storage
- Semantic search capabilities

**P3 - Model Provider**: `src/daip_live/model_provider/`
- Unified LLM interface supporting local (Ollama) and cloud models
- Embedding model abstraction
- Model switching capabilities

**P4 - Role & Tool Manager**: `src/daip_live/p4_role_manager_tools/`
- AI role configuration and management
- Tool registration and execution
- Role model configuration

**P5 - Agent Engine**: `src/daip_live/agent_engine/`
- Dynamic agent execution loops
- Intent recognition and workflow orchestration
- Session and state management

**P6 - CLI/TUI Interface**: `src/daip_live/cli.py`, `src/daip_live/tui.py`
- Command-line interface using Typer
- Terminal UI using Textual
- Enhanced TUI with real-time updates
- Keyboard shortcuts:
  - `Ctrl+Q`: Terminate current session / Exit application (press twice)
  - `Ctrl+E`: Exit application (press twice)
  - `Ctrl+C`: Copy selected text
  - `Ctrl+A`: Select all text

**P7 - Web GUI**: `src/daip_live/p7_gui/`
- FastAPI-based web interface
- REST API endpoints

**P8 - Debate System**: `src/daip_live/p8_debate_system/`
- Multi-agent structured debates
- Role selection and argument management
- Enhanced debate orchestration

### Cross-Cutting Services

**Memory System**: `src/daip_live/memory/`
- Short-term session memory
- Long-term knowledge retention
- Layered memory architecture

**Security & Permissions**: `src/daip_live/permission/`, `src/daip_live/security/`
- User permission management
- Tool execution control
- Security rule enforcement

**Container & DI**: `src/daip_live/container.py`
- Dependency injection setup
- Service lifecycle management

## Data Storage Structure

```
data/
├── daip_live.db              # SQLite database
├── knowledge/                # User documents
├── vector_store/            # FAISS/ChromaDB indexes
├── roles/                   # AI role configurations
├── config.yaml             # Main configuration
└── logs/                   # Application logs
```

## Configuration

- Main config: `data/config.yaml`
- Model provider settings (local vs cloud)
- API keys and endpoints
- Role definitions stored as JSON/YAML in `data/roles/`

## Testing Strategy

- Unit tests for individual components
- Integration tests for agent workflows
- Real model integration tests (when available)
- Async testing support with pytest-asyncio
- Mock-based testing for external dependencies

## Development Notes

- Python 3.9+ required (excluding 3.9.7)
- Uses Poetry for dependency management
- Ruff for linting/formatting, MyPy for type checking
- Extensive test coverage with pytest
- Async/await patterns throughout for responsiveness
- Event-driven architecture with asyncio.Queue for user interventions