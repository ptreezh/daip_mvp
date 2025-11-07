# DAIP-LIVE Development Guidelines

Auto-generated from all feature plans. Last updated: [DATE]

## Active Technologies

- Python 3.9+
- Typer (CLI framework)
- Textual (TUI framework)
- Pydantic (data validation)
- SQLAlchemy (database ORM)
- FAISS (vector storage)
- LangChain (LLM orchestration)
- Dependency-Injector (dependency injection)
- Asyncio (async operations)

## Project Structure

```text
src/
└── daip_live/
    ├── agent_engine/          # Agent execution engine
    ├── basic_tools/          # Basic tools implementation
    ├── core/                 # Core models and interfaces
    ├── doc/                  # Documentation tools
    ├── knowledge/           # Knowledge management
    ├── memory/              # Memory services
    ├── model_provider/      # LLM provider abstraction
    ├── p4_role_manager_tools/  # Role and tool management
    ├── p7_gui/              # GUI components
    ├── p8_debate_system/    # Debate system
    ├── permission/          # Permission management
    ├── persistence/         # Data persistence
    ├── scaffolding/         # Project scaffolding
    ├── security/            # Security features
    ├── tui_v1/              # TUI components
    ├── vcs/                 # Version control integration
    ├── wiki/                # Wiki management
    ├── workflow/            # Workflow orchestration
    ├── cli.py              # CLI interface
    ├── tui.py              # TUI implementation
    └── container.py        # Dependency injection container
```

## Commands

### CLI Commands:
- `daip` - Main command entry point
- `daip run <goal>` - Run agent with goal
- `daip session list/view/clear` - Session management
- `daip role list/view` - Role management
- `daip debate start` - Start debate
- `daip model list` - List available models
- `daip project scaffold` - Project scaffolding
- `daip knowledge sync/search` - Knowledge base operations

### TUI Commands:
- `/pa <goal>` - Personal assistant mode
- `/session list/view/clear/reset` - Session management
- `/role list/view` - Role management
- `/debate start <topic> [options]` - Debate system
- `/model` - Model selection
- `/project scaffold [options]` - Project scaffolding
- `/knowledge sync/search <query>` - Knowledge operations
- `/doc download/list/search` - Document operations
- `/wiki create/list/export` - Wiki management
- `/permission list/grant/revoke/check/reset` - Permission management

## Code Style

### General Principles (DAIP-LIVE Constitution):
1. Module-First Design: All features as well-defined modules in src/daip_live
2. CLI/TUI Interface: All functionality accessible via both interfaces
3. Test-First (NON-NEGOTIABLE): ≥90% test coverage requirement
4. Event-Driven Architecture: Communication via typed events from core/models.py
5. Convention over Configuration: Follow established naming and structure

### Python Style:
- Use Pydantic models for all data structures
- Follow async/await patterns for non-blocking operations
- Use dependency injection via container.py
- Import convention: `from daip_live.core import...` (not from src.daip_live...)
- Type hints on all public interfaces
- Clear error messages and structured logging

### Event System:
- All component communication via typed events defined in core/models.py
- Use proper event models (ThoughtEvent, ToolCallEvent, etc.)
- Implement proper async event processing with asyncio.Queue

## Recent Changes

[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
