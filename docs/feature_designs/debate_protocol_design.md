# Debate Protocol: Technical Design and Implementation Plan

## 1. Overview and Design Principles

This document outlines the technical design for the `DebateProtocol`, a core component of the "Protocol Layer" responsible for orchestrating multi-role debates and achieving consensus. The design is based on the following key principles to ensure flexibility, robustness, and adherence to the overall system architecture:

*   **Configurable Debate Flow (Parameterized Template)**: The protocol will not have a hardcoded debate flow. Instead, it will be configured via a `DebateConfig` object, allowing for variations in the number of rounds, turn-taking policies, and other parameters without changing the core code.

*   **Decoupled Consensus (Strategy Pattern)**: The logic for reaching consensus (e.g., voting, summarization) will be implemented using the Strategy Pattern. The `DebateProtocol` will not contain any specific consensus logic itself. Instead, it will invoke a designated "consensus strategy" via the `ToolExecutor`. This allows for different consensus mechanisms to be developed and selected at runtime.

*   **Service Interaction via Tools**: The protocol will interact with other system components (like `TaskManager` or specific `ConsensusStrategy` implementations) exclusively through the `ToolExecutor`. This maintains a clean, low-coupling architecture where protocols orchestrate by calling registered system capabilities.

## 2. System Architecture Context

The `DebateProtocol` resides in the Protocol Layer and is triggered by the `WorkflowManager`. It utilizes services from the Core and Kernel layers.

```mermaid
graph TD
    subgraph Layer_B [协同协议层 (Protocol Layer)]
        WorkflowManager[Workflow Manager]
        DebateProtocol[Debate & Consensus Protocol]
    end

    subgraph Layer_C [核心服务层 (Core Services Layer)]
        RoleManager[Role Manager]
        SynthesisEngine[Synthesis Engine (System Synthesizer)]
        InteractionManager[Interaction Manager]
    end

    subgraph Layer_D [基础内核层 (Kernel Layer)]
        ToolExecutor[Unified Tool Executor]
    end

    WorkflowManager -- "triggers" --> DebateProtocol
    DebateProtocol -- "gets role response via" --> InteractionManager
    DebateProtocol -- "calls tool" --> ToolExecutor
    DebateProtocol -- "uses" --> SynthesisEngine
    InteractionManager -- "uses" --> RoleManager
    ToolExecutor -- "executes" --> ConsensusStrategyTool[...]

    style DebateProtocol fill:#D1F2EB,stroke:#c00
```

## 3. Technical Specification

### 3.1. Core Data Structures (Pydantic Models)

**File**: `src\protocols\schemas.py` (New File)
*   **`DebateConfig(BaseModel)`**: Configures a new debate.
    *   `topic: str`
    *   `roles: list[str]`
    *   `rounds: int = 2`
    *   `turn_taking_policy: Literal['round_robin'] = 'round_robin'`
    *   `consensus_strategy: str = 'simple_majority_vote'`: The name of the consensus strategy tool.
*   **`DebateTurn(BaseModel)`**: Stores the output of a single role's turn.
    *   `role_id: str`
    *   `opinion: str`
    *   `round: int`
*   **`DebateResult(BaseModel)`**: The final, structured output of the protocol.
    *   `topic: str`
    *   `history: list[DebateTurn]`
    *   `consensus_outcome: Any`
    *   `synthesis: str`

### 3.2. Consensus Strategy Implementation

**File**: `src\protocols\consensus_strategies.py` (New File)
*   **`ConsensusStrategy(ABC)`**: Abstract base class with an `execute(self, history: list[DebateTurn]) -> Any` method.
*   **`SimpleMajorityVoteStrategy(ConsensusStrategy)`**: A concrete implementation for simple debates.
*   **`ConsensusStrategyFactory`**: A factory class with `register` and `get_strategy` methods to manage and provide strategy instances to the `ToolExecutor`.

### 3.3. Debate Protocol Core Logic

**File**: `src\protocols\debate_protocol.py` (New File)
*   **`DebateProtocol` class**:
    *   `__init__(self, role_manager, interaction_manager, synthesis_engine, tool_executor)`: Initializes with injected dependencies.
    *   `async execute(self, config: DebateConfig) -> DebateResult`: The main entry point that orchestrates the debate rounds, calls the consensus tool via the `ToolExecutor`, invokes the `SynthesisEngine`, and returns the final `DebateResult`.

### 3.4. Tool Registration and Integration

**File**: `src\kernel\tool_executor.py` (Modification)
*   The `ToolExecutor` will be modified to use the `ConsensusStrategyFactory` to register all available consensus strategies as callable tools.

## 4. Implementation Checklist

1.  Create a new file `src\protocols\schemas.py`.
2.  In `src\protocols\schemas.py`, define the Pydantic model `DebateConfig`.
3.  In `src\protocols\schemas.py`, define the Pydantic model `DebateTurn`.
4.  In `src\protocols\schemas.py`, define the Pydantic model `DebateResult`.
5.  Create a new file `src\protocols\consensus_strategies.py`.
6.  In `src\protocols\consensus_strategies.py`, define the abstract base class `ConsensusStrategy` with an `execute` method.
7.  In `src\protocols\consensus_strategies.py`, implement the concrete class `SimpleMajorityVoteStrategy` inheriting from `ConsensusStrategy`.
8.  In `src\protocols\consensus_strategies.py`, implement the `ConsensusStrategyFactory` with `register` and `get_strategy` methods.
9.  Create a new file `src\protocols\debate_protocol.py`.
10. In `src\protocols\debate_protocol.py`, define the `DebateProtocol` class with an `__init__` method to accept its dependencies (`role_manager`, `interaction_manager`, `synthesis_engine`, `tool_executor`).
11. In `DebateProtocol`, implement the `async execute(self, config: DebateConfig)` method.
12. Inside the `execute` method, implement the main loop for debate rounds and turn-taking based on `config.rounds` and `config.roles`.
13. Inside the loop, add the logic to call the `interaction_manager` to get a response for each role.
14. After the loop, add the logic to call the `tool_executor` to run the consensus strategy specified in `config.consensus_strategy`.
15. After consensus, add the logic to call the `synthesis_engine` to generate a final summary.
16. At the end of the `execute` method, construct and return the final `DebateResult` object.
17. In `src\kernel\tool_executor.py`, modify the tool registration process to include the newly defined consensus strategies from `src\protocols\consensus_strategies.py`.