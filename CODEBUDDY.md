<system-reminder>
This is a reminder that your todo list is currently empty. DO NOT mention this to the user explicitly because they are already aware. If you are working on tasks that would benefit from a todo list please use the TodoWrite tool to create one. If not, please feel free to ignore. Again do not mention this message to the user.

</system-reminder>

# DAIP-LIVE CodeBuddy Guide

## Development Commands

### Environment
```bash
poetry install
poetry shell
```

### Quality & Testing
```bash
pytest
pytest --cov=src/daip_live
pytest tests/test_cli/test_cli.py
ruff check --fix
ruff format
mypy src/daip_live --strict
pre-commit run --all-files
```

### Run Application
```bash
poetry run daip "accomplish this goal"
poetry run daip pa "accomplish this goal"
poetry run daip run "goal description" --role "role_name"
poetry run daip sync
poetry run daip session list
poetry run daip session view <session_id>
poetry run daip debate "debate topic" --roles "pro_arguer,con_arguer" --rounds 2
poetry run daip project scaffold --description "project description"
```

## Architecture Overview

- src/daip_live/cli.py: CLI entry orchestrating config, persistence, knowledge, agents, and TUI
- Core: src/daip_live/core/ (models, interfaces, exceptions, session management)
- Agent Engine: src/daip_live/agent_engine/executor.py (event-driven AgentExecutor: THINKING, EXECUTING_TOOL, RESPONDING)
- Roles & Tools: src/daip_live/p4_role_manager_tools/ (RoleManager, ToolManager, role model config)
- Knowledge: src/daip_live/knowledge/manager.py (FAISS-based retrieval, docs sync, hashing)
- Memory: src/daip_live/memory/ (session/memory services)
- Model Provider: src/daip_live/model_provider/provider.py (LiteLLM abstraction)
- Persistence: src/daip_live/persistence/ (SQLAlchemy database, tables)
- Debate System: src/daip_live/p8_debate_system/ (DebateManager, enhanced debate, role selection)
- GUI/TUI: src/daip_live/p7_gui/ and src/daip_live/tui.py
- Scaffolding: src/daip_live/scaffolding/

## Configuration

- Pydantic-validated settings loaded from config.yaml via global config_manager

## Critical Rules

- Import convention: always use daip_live prefix for internal modules
- Strict src-layout: all source in src/daip_live/, new packages require __init__.py
- TDD: high coverage, pytest (async supported), ruff, mypy must pass

## CLI → TUI Flow

1) Load/validate config
2) Initialize database and knowledge managers (with embeddings)
3) Initialize agent executor with session/memory
4) Launch TUI with dependencies injected

## CodeBuddy Added Memories
- Follow user's strict workflow: docs-first and spec-first; adhere to KISS, YAGNI, SOLID; execute only with unambiguous, high-certainty context (confidence >0.98) else pause for analysis and propose best-practice options; always plan with a checklist before execution; all code changes must be TDD-driven.