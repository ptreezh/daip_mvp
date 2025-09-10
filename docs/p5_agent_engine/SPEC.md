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
