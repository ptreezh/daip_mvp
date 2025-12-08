# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DAIP-LIVE** (Dynamic AI-driven Project-execution LIVE System) is a sophisticated AI-powered project execution system that combines multiple advanced capabilities into a unified platform. It's built as a modular monolith architecture for local single-user environments, prioritizing performance, privacy, and user experience.

### Core Capabilities
- **Textual User Interface (TUI)**: Rich terminal-based interactive experience
- **Natural Language Processing**: Advanced intent recognition and context-aware conversation
- **Multi-Model Debate System**: Role-based AI agents with different models and perspectives
- **Wiki Collaboration**: Knowledge management and collaborative editing
- **Project Scaffolding**: AI-driven project structure generation
- **Permission Management**: Safe operation with user-controlled permissions

## Development Commands

### Installation & Setup
```bash
# Install dependencies using Poetry (preferred)
poetry install

# Or install with pip
pip install -e .

# Create initial config
python -c "from daip_live.config import create_config_yaml_if_not_exists; create_config_yaml_if_not_exists()"
```

### Running the Application
```bash
# Main TUI interface (primary way to use the system)
daip run

# Alternative ways to start
python -m daip_live.cli_main
python src/daip_live/cli_main.py
```

### CLI Commands
```bash
# Check available commands
daip --help

# Start debates
daip debate start "topic" --roles pro_arguer,con_arguer

# Document processing
daip doc search "machine learning" --source arxiv
daip doc download <paper_id>

# Wiki operations
daip wiki create "page title"
daip wiki search "keyword"
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/daip_live

# Run specific test categories
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v
poetry run pytest tests/e2e/ -v

# Run specific test files
poetry run pytest tests/persistence/test_database.py -v -s
```

### Code Quality
```bash
# Linting
poetry run ruff check src/daip_live

# Formatting
poetry run ruff format src/daip_live

# Type checking
poetry run mypy src/daip_live
```

## Architecture Overview

### Design Principles
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering for single-user use case
- **SOLID**: Clean object-oriented design with single responsibility
- **Async/First**: Fully asynchronous for responsive UI
- **Privacy-First**: All processing occurs locally
- **Modular Monolith**: Clear component boundaries without network overhead

### Layered Architecture
```
┌─────────────────────────────────┐
│      User Interface Layer       │
│  (CLI/TUI, GUI, Web Interface)  │
├─────────────────────────────────┤
│     Core Logic Layer            │
│  (Agent Engine, Debate System) │
├─────────────────────────────────┤
│     Service Layer              │
│  (DB, Knowledge, Models, Tools) │
└─────────────────────────────────┘
```

### Key Components (P1-P8 Modules)

#### P1: Data Persistence (`src/daip_live/persistence/`)
- **SQLite database** with SQLAlchemy ORM
- **Session management** for conversation continuity
- **Database tables** defined in `persistence/tables.py`

#### P2: Knowledge Management (`src/daip_live/wiki/`, `knowledge/`)
- **Vector-based search** using FAISS
- **Wiki system** with tagging and linking
- **Knowledge integration** between wiki and other components

#### P3: Model Provider (`src/daip_live/model_provider/`)
- **LiteLLM integration** supporting multiple LLM providers
- **Local model support** (Ollama, Llama 3, Mistral)
- **Cloud provider support** (OpenAI, Claude, etc.)

#### P4: Role & Tool Management (`src/daip_live/p4_role_manager_tools/`)
- **Dynamic role assignment** with specific models and parameters
- **Tool system** for extensible capabilities
- **Role configuration** from YAML files

#### P5: Agent Engine (`src/daip_live/agent_engine/`)
- **Two-level execution cycle**: Strategic planning + tactical execution
- **Event-driven architecture** with async generators
- **Intent recognition** and context management
- **Step-by-step execution** with real-time steering

#### P6: Terminal Interface (`src/daip_live/cli/`, `src/daip_live/tui_modular.py`)
- **CLI commands** using Typer for scripting
- **TUI interface** using Textual for interactive use
- **Modular TUI** with enhanced navigation and features
- **Entry point**: `cli_main.py` or `daip run`

#### P7: GUI Interface (`src/daip_live/p7_gui/`)
- **Streamlit-based web interface** (in development)
- **API endpoints** for external integration

#### P8: Debate System (`src/daip_live/p8_debate_system/`)
- **Enhanced debate manager** with multiple participants
- **Role-based model assignment** (different models per role)
- **History tracking** with session management
- **Simple and enhanced debate managers** available

## Important Files & Directories

### Core Configuration
- `config.yaml` - Main configuration file (create from example if needed)
- `pyproject.toml` - Project metadata and dependencies
- `src/daip_live/container.py` - Dependency injection container

### Main Entry Points
- `src/daip_live/cli_main.py` - Main CLI entry point with dependency injection
- `src/daip_live/cli/main.py` - CLI command definitions
- `src/daip_live/tui_modular.py` - Main TUI implementation

### Key Implementation Files
- `src/daip_live/config.py` - Configuration management
- `src/daip_live/container.py` - Dependency injection setup
- `src/daip_live/agent_engine/enhanced_chat_executor.py` - Main chat execution
- `src/daip_live/p8_debate_system/enhanced_debate_manager.py` - Debate system

## Development Notes

### Configuration Requirements
The system requires a `config.yaml` file with:
- Database path (`daip_live.db`)
- Model provider settings (Ollama/LiteLLM configuration)
- Wiki and knowledge directories
- Debate system settings

### Current Issues & Solutions
1. **Import Error in CLI**: The `pyproject.toml` entry point is incorrect. Use `python -m daip_live.cli_main` instead
2. **TUI Dependencies**: Requires modern terminal with Textual support
3. **Model Loading**: Requires Ollama running or API keys configured

### Testing Architecture
- **TDD (Test-Driven Development)** throughout the codebase
- **Unit tests** for individual components in `tests/unit/`
- **Integration tests** in `tests/integration/`
- **E2E tests** in `tests/e2e/`
- **Mocking** for external dependencies

### Common Development Workflows
1. **Adding new CLI commands**: Add to `src/daip_live/cli/main.py`
2. **TUI modifications**: Edit `src/daip_live/tui_modular.py`
3. **New debate features**: Extend `src/daip_live/p8_debate_system/`
4. **Agent engine changes**: Modify `src/daip_live/agent_engine/`

## Project Structure Notes

This codebase uses a **modular P1-P8 architecture** where:
- **P1**: Data persistence and database management
- **P2**: Knowledge management and wiki functionality
- **P3**: Model provider abstraction layer
- **P4**: Role and tool management system
- **P5**: Agent execution engine (core logic)
- **P6**: Terminal user interfaces (CLI/TUI)
- **P7**: Graphical user interfaces
- **P8**: Multi-agent debate system

The system is designed as a **privacy-first local application** that can optionally use cloud services. All core functionality works offline with local models.

---
生成时间: 2025-12-02T13:28:23.870Z
