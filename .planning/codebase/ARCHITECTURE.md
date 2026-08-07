# Architecture

**Analysis Date:** 2026-08-07

## Pattern Overview

**Overall:** Modular Monolith with Layered Architecture

**Key Characteristics:**
- Single-process local execution (privacy-first)
- Async/First design for responsive UI
- Dependency injection for loose coupling
- Interface-based contracts for all major components
- Event-driven communication patterns

## Layers

**User Interface Layer (P6, P7):**
- Purpose: User interaction and visualization
- Location: `src/daip_live/cli/`, `src/daip_live/tui/`, `src/daip_live/p7_gui/`
- Contains: CLI commands, TUI screens, GUI API
- Depends on: Core Logic Layer, Service Layer
- Used by: End users

**Core Logic Layer (P5):**
- Purpose: Agent execution, debate orchestration, intent recognition
- Location: `src/daip_live/agent_engine/`, `src/daip_live/p8_debate_system/`, `src/daip_live/intent_recognition/`
- Contains: AgentExecutor, DebateManager, IntentRecognizer, task decomposition
- Depends on: Service Layer
- Used by: User Interface Layer

**Service Layer (P1-P4):**
- Purpose: Data access, model access, tool management
- Location: `src/daip_live/persistence/`, `src/daip_live/knowledge/`, `src/daip_live/model_provider/`, `src/daip_live/p4_role_manager_tools/`
- Contains: DatabaseManager, KnowledgeManager, LiteLLMProvider, RoleManager, ToolManager
- Depends on: Core interfaces, data stores
- Used by: Core Logic Layer

**Core Layer (P0):**
- Purpose: Shared interfaces, models, exceptions
- Location: `src/daip_live/core/`
- Contains: IModelProvider, IKnowledgeManager, ITool, IDebateManager, Pydantic models
- Depends on: None (foundation)
- Used by: All layers

## Data Flow

**Agent Execution Flow:**

1. User input (CLI/TUI) → IntentRecognizer
2. Intent → AgentExecutor.run() or chat_run()
3. Task decomposition (if complex) → TaskDecompositionEngine
4. Todo list generation → MemoryService
5. Step execution → StepExecutor
6. Tool execution (with permission checks) → ToolManager
7. Response generation → ModelProvider
8. Event streaming → UI update

**Debate Flow:**

1. CLI command: `daip debate start`
2. DebateManager initialization (with session, roles, models)
3. Round-by-round execution with async generators
4. Per-role model invocation via RoleModelManager
5. Event emission (DebateStartEvent, DebateRoundStartEvent, etc.)
6. History tracking via DebateHistoryTracker
7. Session persistence in database

**Knowledge Search Flow:**

1. Query text → KnowledgeManager.search()
2. Embedding generation → ModelProvider.embed()
3. FAISS vector search → distance + IDs
4. Database lookup → KnowledgeSource records
5. Result formatting → ordered list with metadata

**State Management:**
- Session state: AgentState enum (IDLE, RUNNING, COMPLETED, FAILED, etc.)
- Database persistence: SQLite with SQLAlchemy
- In-memory: asyncio.Queue for user input
- Event-driven: AsyncGenerator for real-time updates

## Key Abstractions

**IModelProvider (`src/daip_live/core/interfaces.py`):**
- Purpose: Unified interface for LLM generation and embeddings
- Examples: `src/daip_live/model_provider/provider.py`
- Pattern: Adapter pattern (LiteLLM adapter)

**IKnowledgeManager (`src/daip_live/core/interfaces.py`):**
- Purpose: Knowledge base search and synchronization
- Examples: `src/daip_live/knowledge/manager.py`
- Pattern: Repository pattern

**ITool (`src/daip_live/core/interfaces.py`):**
- Purpose: Extensible tool execution framework
- Examples: `src/daip_live/basic_tools/`, `src/daip_live/p4_role_manager_tools/tools.py`
- Pattern: Strategy pattern

**IDebateManager (`src/daip_live/core/interfaces.py`):**
- Purpose: Multi-agent debate orchestration
- Examples: `src/daip_live/p8_debate_system/enhanced_debate_manager.py`
- Pattern: Async generator pattern for event streaming

**AgentEvent Union Type (`src/daip_live/core/models.py`):**
- Purpose: Type-safe event communication
- Examples: ThoughtEvent, ToolCallEvent, DebateCompleteEvent, PermissionRequestEvent
- Pattern: Union type with discriminated literals

## Entry Points

**CLI Entry Point:**
- Location: `src/daip_live/cli/main.py`
- Triggers: `daip` command or `python -m daip_live.cli.main`
- Responsibilities: Command routing (debate, doc, wiki, knowledge)

**TUI Entry Point:**
- Location: `src/daip_live/tui/simplified_main.py` (via `src/daip_live/tui_modular.py`)
- Triggers: `daip run` command
- Responsibilities: Interactive terminal interface

**API Entry Point:**
- Location: `src/daip_live/p7_gui/main.py`
- Triggers: HTTP requests to FastAPI server
- Responsibilities: WebSocket for real-time updates, REST endpoints

**Dependency Injection:**
- Location: `src/daip_live/container.py`
- Triggers: Application initialization
- Responsibilities: Singleton service provisioning

## Error Handling

**Strategy:** Exception-based with custom error types

**Patterns:**
- Custom exceptions in `src/daip_live/core/exceptions.py`
- ModelError for LLM-related errors
- ModelAuthenticationError for auth failures
- ToolError for tool execution failures
- Try-except with specific exception types
- Logging for all error paths

## Cross-Cutting Concerns

**Logging:** Python logging module ( INFO level)
**Validation:** Pydantic models with ConfigDict
**Authentication:** Local session management (no external auth)
**Permission:** PermissionManager with user interaction
**Configuration:** YAML-based with ConfigManager
**Async/Await:** Core execution paths are async

---

*Architecture analysis: 2026-08-07*
