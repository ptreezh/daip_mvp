# Codebase Structure

**Analysis Date:** 2026-08-07

## Directory Layout

```
D:\DAIP\refactdoc/
├── .planning/              # Planning and codebase analysis documents
├── archive/                # Archived code (tui, debate modules, etc.)
├── claude_skills/          # Claude skill definitions
├── config.yaml             # Main configuration file
├── daip_live.db            # SQLite database (runtime-generated)
├── docs/                   # Comprehensive documentation
├── examples/               # Example usage and demos
├── knowledge/              # Knowledge base storage
│   ├── debate/            # Debate logs
│   ├── paper/             # Downloaded papers
│   └── wiki/              # Wiki pages
├── log/                   # Application logs
├── prompts/               # System prompts
├── roles/                 # Role definitions (YAML)
├── specs/                 # Specification documents
├── src/daip_live/         # Main source code (P1-P8 modules)
│   ├── agent_engine/      # P5: Agent execution engine
│   ├── basic_tools/       # Built-in tools
│   ├── cli/               # P6: CLI commands
│   ├── core/              # P0: Core interfaces and models
│   ├── debate_module/     # Debate components
│   ├── doc/               # Document processing
│   ├── intent_recognition/ # NLP intent recognition
│   ├── knowledge/         # P2: Knowledge management
│   ├── memory/            # Session and memory services
│   ├── model_provider/    # P3: LLM provider abstraction
│   ├── multi_agent_collab/ # Wiki collaboration
│   ├── p4_role_manager_tools/ # P4: Role and tool management
│   ├── p7_gui/            # P7: GUI (FastAPI)
│   ├── p7_gui_v1/         # P7 v1: Alternative GUI
│   ├── p8_debate_system/  # P8: Multi-agent debate
│   ├── permission/        # Permission management
│   ├── persistence/       # P1: Database layer
│   ├── scaffolding/       # Project scaffolding
│   ├── skills/            # Skill management
│   ├── task_decomposition/ # Task breakdown
│   ├── todo/              # Todo management
│   ├── tui/               # P6: TUI components
│   ├── workflow/          # Workflow execution
│   └── [module files]     # Core module files
├── tests/                 # Test suite (194 test files)
│   ├── basic_tools/
│   ├── cli/
│   ├── config/
│   ├── core/
│   ├── doc/
│   ├── e2e/
│   ├── functional/
│   ├── integration/
│   ├── interactive/
│   ├── knowledge/
│   ├── memory/
│   ├── model_provider/
│   ├── p4_role_manager_tools/
│   └── conftest.py
├── pyproject.toml         # Poetry configuration
├── poetry.lock           # Locked dependencies
└── README.md              # Project documentation
```

## Directory Purposes

**`src/daip_live/`:**
- Purpose: Main application source code (357 Python files)
- Contains: All P1-P8 modules, core interfaces, utilities
- Key files: `container.py`, `config.py`, `tui_modular.py`

**`docs/`:**
- Purpose: Comprehensive project documentation
- Contains: Specs, architecture docs, procedures, research
- Key files: `MAIN_CONTROL_DOCUMENT.md`, `specs/SYSTEM_ARCHITECTURE.md`

**`tests/`:**
- Purpose: Test suite (194 test files, TDD approach)
- Contains: Unit, integration, e2e tests mirroring source structure
- Key files: `conftest.py` (pytest fixtures)

**`knowledge/`:**
- Purpose: Runtime data storage (git-ignored)
- Contains: Wiki pages, debate logs, downloaded papers

**`roles/`:**
- Purpose: Agent role definitions in YAML format
- Contains: Role personas, tool assignments, model configurations

## Key File Locations

**Entry Points:**
- `src/daip_live/cli/main.py`: CLI command definitions (Typer)
- `src/daip_live/tui/simplified_main.py`: Main TUI implementation
- `src/daip_live/tui_modular.py`: TUI factory for backward compatibility
- `src/daip_live/p7_gui/main.py`: FastAPI server for GUI

**Configuration:**
- `config.yaml`: Main configuration (database, models, paths)
- `.env`: Environment variables (git-ignored, secrets)
- `pyproject.toml`: Project metadata and dependencies
- `src/daip_live/config.py`: ConfigManager implementation

**Core Logic:**
- `src/daip_live/agent_engine/executor.py`: Main agent execution
- `src/daip_live/p8_debate_system/enhanced_debate_manager.py`: Debate orchestration
- `src/daip_live/agent_engine/enhanced_intent_recognizer.py`: NLP intent parsing

**Core Interfaces (P0):**
- `src/daip_live/core/interfaces.py`: ABC contracts (IModelProvider, IKnowledgeManager, etc.)
- `src/daip_live/core/models.py`: Pydantic models (Session, AgentEvent, etc.)
- `src/daip_live/core/exceptions.py`: Custom exceptions

**Testing:**
- `tests/unit/`: Component-level tests
- `tests/integration/`: Cross-module tests
- `tests/e2e/`: End-to-end workflow tests

## Naming Conventions

**Files:**
- `snake_case.py` for modules: `chat_executor.py`, `role_manager.py`
- `UPPERCASE.md` for documentation: `STACK.md`, `ARCHITECTURE.md`
- `snake_case.yaml` for configuration: `config.yaml`

**Directories:**
- `snake_case` for modules: `agent_engine/`, `model_provider/`
- `p#_name` for numbered modules: `p4_role_manager_tools/`, `p8_debate_system/`

**Classes:**
- `PascalCase`: `AgentExecutor`, `KnowledgeManager`, `LiteLLMProvider`
- `I` prefix for interfaces: `IModelProvider`, `IKnowledgeManager`

**Functions/Variables:**
- `snake_case`: `run_debate()`, `get_session()`, `db_manager`

## Where to Add New Code

**New Feature:**
- Primary code: `src/daip_live/{module_name}/`
- Tests: `tests/{module_name}/` or `tests/unit/`

**New CLI Command:**
- Implementation: `src/daip_live/cli/commands/{command_name}.py`
- Register in: `src/daip_live/cli/main.py`

**New TUI Screen:**
- Implementation: `src/daip_live/tui/screens.py` (or new file)
- Integration: `src/daip_live/tui/simplified_main.py`

**New Tool:**
- Implementation: `src/daip_live/basic_tools/{tool_name}.py`
- Registration: Via ToolManager or in role definitions

**New Role:**
- Definition: `roles/{role_name}.yaml`
- Integration: Automatic via RoleManager

**Utilities:**
- Shared helpers: `src/daip_live/core/` or module-specific utils/

## Special Directories

**`archive/`:**
- Purpose: Deprecated/removed code for reference
- Generated: No (manually maintained)
- Committed: Yes

**`knowledge/`:**
- Purpose: Runtime knowledge storage (wiki, papers, debates)
- Generated: Yes (populated during runtime)
- Committed: No (git-ignored)

**`log/`:**
- Purpose: Application logs
- Generated: Yes
- Committed: No (git-ignored)

**`__pycache__/`:**
- Purpose: Python bytecode cache
- Generated: Yes
- Committed: No (git-ignored)

---

*Structure analysis: 2026-08-07*
