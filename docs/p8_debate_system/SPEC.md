# P8: Debate System Specification

## 1. Overview

This document specifies the design for the **Debate System**. This system orchestrates a structured, multi-agent debate on a given topic, leveraging the foundational services of the DAIP-LIVE platform (Session Management, Role Management, Model Provider).

The goal is to produce a comprehensive analysis of a topic from multiple perspectives and generate a consensus report, as outlined in `specifications/DEBATE_SYSTEM_REQUIREMENTS.md`.

## 2. Core Components

### 2.1 `DebateManager` Service

This is the central orchestrator for the debate.

**Location**: `src/daip_live/p8_debate_system/manager.py`

**Dependencies**:
- `SessionManager`: To create and update the debate session record.
- `RoleManager`: To load the personas and configurations of the participating AI agents.
- `ModelProvider`: To generate responses for each agent.

**Logic**:
1.  **Initialization**: Takes a debate topic and a list of role names (e.g., `["pro_arguer", "con_arguer", "neutral_observer"]`).
2.  **Session Creation**: Calls `session_manager.create_session()` with `session_type="debate"`.
3.  **Role Loading**: Calls `role_manager.load_roles()` for the specified participants.
4.  **Turn-Based Execution**: Manages a loop for a predefined number of rounds.
    - In each turn, it constructs a specific prompt for the current speaker, including the debate topic, its persona, and the recent conversation history.
    - It calls `model_provider.generate()` to get the agent's response.
    - It appends the response to the session's history via `session.history.append(DialogueTurn(...)`.
5.  **Consensus Generation**: After the final round, it constructs a final prompt to a summarizer/evaluator model, asking it to analyze the full debate history and produce a summary, identify key arguments, and check for biases.
6.  **Session Finalization**: Calls `session_manager.save_session()` with the final state, including the generated summary.

### 2.2 `RoleManager` (P4) Integration

The `DebateManager` will assume the `RoleManager` (from P4) has a method like `load_role(name: str) -> Role` which returns a `Role` object containing the persona/prompt for that agent.

## 3. CLI Integration

A new CLI command group `daip debate` will be created.

- `daip debate start <topic> --roles <role1>,<role2>,...`: This command will initialize the `DebateManager` and execute the full debate process. The output will be streamed to the console, and the final session ID will be printed for later review.

## 4. Data Flow

1.  User runs `daip debate start ...`.
2.  `CLI` instantiates and calls `DebateManager.run_debate()`.
3.  `DebateManager` creates a `Session` via `SessionManager`.
4.  `DebateManager` loops through turns:
    a. Gets `Role` persona from `RoleManager`.
    b. Gets response from `ModelProvider`.
    c. Appends `DialogueTurn` to the `Session` object in memory.
5.  `DebateManager` generates a final summary.
6.  `DebateManager` calls `SessionManager.save_session()` to persist the entire record.
