# P5: Agent Engine Specification

## 1. Overview

The Agent Engine (`AgentExecutor`) is the core of the DAIP-LIVE system. It is a state machine that drives the agent through the process of understanding a goal, planning, executing tools, and responding to the user.

## 2. `get_status` API

To facilitate real-time monitoring by interfaces like the TUI (P6), the `AgentExecutor` must provide a status API.

### 2.1. Method Signature

Located in the `AgentExecutor` class:

```python
def get_status() -> AgentStatus:
```

### 2.2. Data Contract (`AgentStatus` Model)

This API will return a Pydantic model that provides a snapshot of the agent's current state. This model will be defined in `src/daip_live/core/models.py`.

```python
from pydantic import BaseModel
from daip_live.core.models import AgentState

class AgentStatus(BaseModel):
    """A snapshot of the AgentExecutor's real-time state."""
    state: AgentState
    model_name: str
    tokens_used: int
    tokens_total: int
```

### 2.3. Data Sourcing

The `AgentExecutor` will source the data for the `AgentStatus` model as follows:

-   `state`: Directly from the `self.state: AgentState` attribute of the executor.
-   `model_name`: From the configuration of the loaded model provider: `self.model_provider.config.model`.
-   `tokens_used`: **This requires implementation.** The `AgentExecutor` must be modified to inspect the response object from `litellm.completion` after each call and accumulate the `usage.total_tokens` value.
-   `tokens_total`: This will be based on the context window of the current `model_name`. A mapping of model names to context window sizes will need to be added to the system, likely within the `ModelProvider` or a new configuration service.

## 3. Execution Modes

The Agent Engine supports two distinct execution modes to handle different use cases: a task-oriented mode for automated workflows and a conversational mode for interactive sessions.

### 3.1. Task-Oriented Mode (`run`)

-   **Method**: `async def run(self, goal: str, ...) -> AsyncGenerator[AgentEvent, None]`
-   **Purpose**: To execute a predefined, non-interactive sequence of tasks.
-   **Mechanism**: This mode is driven by a `todo_list` or a formal `workflow_definition`. The agent executes each step in the sequence until the list is complete or a failure occurs.
-   **Use Case**: Ideal for automated workflows where the agent is given a complex goal that can be broken down into a plan and executed without user intervention.
-   **Lifecycle**: The `run` method terminates once the task sequence is finished. It is not designed for persistent, back-and-forth interaction.

### 3.2. Conversational Mode (`chat_run`)

-   **Method**: `async def chat_run(self, initial_goal: str) -> AsyncGenerator[AgentEvent, None]`
-   **Purpose**: To engage in an open-ended, interactive conversation with a user.
-   **Mechanism**: This mode is driven by a `user_input_queue`. After processing the `initial_goal`, the agent enters a persistent loop, waiting for new input from the queue. Each new input is treated as the next conversational turn.
-   **Use Case**: The primary mode for the "Personal Assistant" (`/pa`) feature in the TUI, where the user expects a continuous dialogue.
-   **Lifecycle**: The `chat_run` method runs indefinitely until the session is explicitly terminated, allowing for a stateful, multi-turn conversation.
