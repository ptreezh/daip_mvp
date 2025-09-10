---
id: P0
title: Core Interfaces & Types
status: Finalized
architecture_drivers: [SOLID, KISS, YAGNI, KDD]
---

# P0: Core Interfaces & Types

## 1. Overview

This work package (`P0`) is the foundational, concrete specification layer of the DAIP-LIVE application. It contains no business logic. Its sole purpose is to define the **Data Contracts (Pydantic Models)** and **Interface Contracts (Abstract Base Classes)** shared across all other modules. The stability of this package is the highest priority.

## 2. Data Contracts (Pydantic Models)

These models ensure type-safe data transfer throughout the system. All models inherit from `pydantic.BaseModel`.

### 2.1. Core Data Models

-   **`TodoItem`**: Defines a to-do task.
    -   `id: int` (Read-only, from DB)
    -   `description: str`
    -   `status: Literal["pending", "in_progress", "completed"]`
    -   `priority: int = 1`
-   **`Role`**: Defines an AI agent's configuration.
    -   `name: str`
    -   `persona: str`
    -   `tools: List[str]`
-   **`Session`**: Defines metadata for a user session.
    -   `id: int`
    -   `title: str`
    -   `created_at: datetime`
-   **`Message`**: **[DEPRECATED]** Defines a single chat message. Superseded by `DialogueTurn`.
    -   `role: Literal["user", "assistant"]`
    -   `content: str`
    -   `metadata_json: str` *(Must use a Pydantic validator to ensure valid JSON)*

### 2.2. Workflow & State Models

-   **`AssistantState`**: Represents the unified state of the assistant.
    -   `mode: Literal["NORMAL", "ASSISTANT_ACTIVE"]`
    -   `current_session_id: Optional[int]`
    -   `active_workflow: Optional[str]`
-   **`ConsensusResult`**: Represents the outcome of a multi-agent consensus.
    -   `topic: str`
    -   `proposals: Dict[str, str]` # Key: Role Name, Value: Proposal Text
    -   `final_consensus: str`
    -   `contributing_roles: List[str]`
-   **`AgentState` (Enum)**: Represents the internal state of the `AgentExecutor` and the lifecycle of a `Session`.
    -   **Session States**: `INIT`, `RUNNING`, `COMPLETED`, `FAILED`
    -   **Agent Internal States**: `IDLE`, `OBSERVING`, `THINKING`, `EVALUATING`, `REFLECTING`, `EXECUTING_TOOL`, `RESPONDING`, `FINALIZING`, `ERROR`, `EXPLORING`, `SYNTHESIZING`
-   **`SessionContext`**: Holds contextual information for a session, used for tool preconditions.
    -   `recently_read_resources: Set[str]`

### 2.3. Agent Event Stream Models (`AgentEvent`)

This discriminated union is the **primary contract** for all UIs (`P6`, `P7`).

-   **`ThoughtEvent`**: Represents an internal thought or reasoning step of the agent.
    -   `type: Literal["thought"]`
    -   `content: str`
-   **`ToolCallEvent`**: Represents the agent's decision to call a tool.
    -   `type: Literal["tool_call"]`
    -   `tool_name: str`
    -   `args: Dict[str, Any]`
-   **`ToolOutputEvent`**: Represents the result of a tool execution.
    -   `type: Literal["tool_output"]`
    -   `tool_name: str`
    -   `status: Literal["success", "error"]`
    -   `output: str`
-   **`FinalResponseEvent`**: Represents the agent's final answer to the user.
    -   `type: Literal["final_response"]`
    -   `content: str`
-   **`ErrorEvent`**: Represents an error that occurred during agent execution.
    -   `type: Literal["error"]`
    -   `message: str`
-   **`PermissionRequestEvent`**: Represents a request for user permission to execute a tool.
    -   `type: Literal["permission_request"]`
    -   `tool_name: str`
    -   `args: Dict[str, Any]`
-   **`ResponseChunkEvent`**: Represents a streaming chunk of the final response.
    -   `type: Literal["response_chunk"]`
    -   `delta: str`

The `AgentEvent` type is a `Union` of all the event models listed above.

### 2.4. Knowledge & Sync Models

-   **`KnowledgeSource`**: Represents a source document in the knowledge base.
    -   `file_path: str`
    -   `file_hash: str`
    -   `status: Literal["indexed", "pending", "error"]`
    -   `id: Optional[int]`
    -   `indexed_at: Optional[datetime]`
    -   `created_at: Optional[datetime]`
-   **`KnowledgeBaseChanges`**: A data contract for the result of detecting changes in the knowledge base.
    -   `added: List[str]`
    -   `updated: List[Tuple[str, KnowledgeSource]]`
    -   `deleted: List[KnowledgeSource]]`
    -   `unchanged: List[KnowledgeSource]`

### 2.5. Application Configuration Models

These models define the schema for the global `config.yaml` file. They are the single source of truth for application configuration.

-   **`DatabaseConfig`**: Defines the database connection settings.
    -   `path: str`
-   **`LLMProviderConfig`**: Defines the models to be used for generation and embedding.
    -   `default_model: str`
    -   `embedding_model: str`
-   **`KnowledgeBaseConfig`**: Defines the settings for the knowledge base.
    -   `directory: str`
-   **`AppConfig`**: The top-level configuration model that nests all other configuration models.
    -   `database: DatabaseConfig`
    -   `llm_provider: LLMProviderConfig`
    -   `knowledge_base: KnowledgeBaseConfig`

### 2.6. Service-Specific Configuration Models

-   **`ProviderConfig`**: **[DEPRECATED]** This will be replaced by direct usage of `LLMProviderConfig` values. It defines the configuration for a specific model provider instance.
    -   `model: str`
    -   `api_key: Optional[str]`
    -   `base_url: Optional[str]`
    -   `temperature: Optional[float]`
    -   `max_tokens: Optional[int]`
    -   `num_retries: int = 3`
-   **`ToolPermissionConfig`**: Defines the permission settings for tool execution.
    -   `default: Literal["allow", "deny", "ask"]`
    -   `tools: Dict[str, Literal["allow", "deny", "ask"]]`

## 3. Interface Contracts (Abstract Base Classes)

These abstract classes (`abc.ABC`) define the methods that core services *must* implement.

-   **`IModelProvider`**
    -   `generate(prompt: str, params: Dict) -> AsyncGenerator[str, None]`
    -   `embed(text: str) -> List[float]`
-   **`IKnowledgeManager`**
    -   `search(query_text: str, top_k: int) -> List[Dict]`
    -   `sync_knowledge_base() -> Dict`
-   **`ITool`**
    -   `execute(**kwargs) -> Any`

## 4. Exception Hierarchy

A unified exception hierarchy ensures predictable error handling.

```python
class DAIPError(Exception):
    """Base exception for all application-specific errors."""
    pass

class ModelError(DAIPError):
    """Errors related to the Model Provider (P3)."""
    pass

class ModelConnectionError(ModelError):
    pass

class ModelAuthenticationError(ModelError):
    pass

class ToolError(DAIPError):
    """Errors related to Tool execution (P4)."""
    pass

class ToolInputError(ToolError):
    pass

class ToolPermissionError(ToolError):
    pass
```

## 5. Task List & Test Plan Summary

-   **TDD Approach**: Development must be test-driven.
-   **Models**: For each Pydantic model, tests must verify:
    1.  `ValidationError` on missing required fields.
    2.  `ValidationError` on incorrect field types.
    3.  Successful creation with valid data.
-   **Interfaces**: For each ABC, tests must verify that direct instantiation, or instantiation of an incomplete implementation, raises a `TypeError`.
-   **Acceptance**: Test coverage >= 95%; passes `ruff` and `mypy --strict`.

## 6. Implementation Status

-   **Data Contracts (Pydantic Models)**: All models defined in `src/daip_live/core/models.py` have been implemented and are in use.
-   **Interface Contracts (Abstract Base Classes)**: All interfaces defined in `src/daip_live/core/interfaces.py` have been defined. Implementations are provided by respective work packages (e.g., `IModelProvider` by P3, `IKnowledgeManager` by P2).
-   **Exception Hierarchy**: The custom exception hierarchy has been implemented and is in use.
