---
id: P5
title: Agent Engine Logic
status: In Refactoring
architecture_drivers: [SOLID, KISS, YAGNI, KDD]
---

# P5: Agent Engine Logic

## 1. Overview

This work package (`P5`) is the "brain" of the system, containing the `AgentExecutor`. It orchestrates all underlying services (`P1`-`P4`) to achieve user-defined goals.

This document specifies the **target architecture** for the Agent Engine, which is a **Planning-Driven, Reflection-Enhanced** hybrid model. This supersedes all previous designs. The engine's primary responsibility is to dynamically create and manage a plan (`Todo` list), execute it step-by-step, and apply a reflection mechanism at key points for quality control.

## 2. Core Execution Loop: The Two-Level Cycle

The `AgentExecutor`'s `run` method is structured as two nested loops, separating strategic planning from tactical execution.

### Level 1: The Outer Loop (Strategic Planner)
This `while` loop is driven by the overall completion of the `Todo` list. It acts as the "Project Manager".

1.  **Check Completion**: The loop continues as long as `is_todo_list_complete()` is false.
2.  **Select Task**: It selects the next `TodoItem` from the list to be executed.
3.  **Delegate to Inner Loop**: It activates the Inner Loop to handle the execution of this single task.
4.  **Update Status**: Once the Inner Loop completes a task, the Outer Loop marks the task as complete and proceeds to the next one.

### Level 2: The Inner Loop (Tactical Executor State Machine)
For each `TodoItem` delegated by the Outer Loop, this state machine determines *how* to execute it. It acts as the "Technical Expert". The logic for this entire inner loop is encapsulated within a private `_execute_step` method for clarity and maintainability.

1.  **OBSERVE & STEER**: The loop **always** begins by checking the `user_input_queue` for real-time commands. A user command will interrupt the current flow and force the state to `THINKING` to process the new information.
2.  **THINKING**: The Agent formulates a prompt based on the current task's description and context (e.g., previous tool results or a new user command) and calls the LLM.
3.  **EVALUATING**: The Agent parses the LLM's response. 
    -   If the response is a `ToolCall`, it transitions to `EXECUTING_TOOL`.
    -   If the response is a final answer for the current step, it transitions to `RESPONDING`.
    -   *(Future)*: This is where a "Reflect on Action" quality gate can be added.
4.  **EXECUTING_TOOL**: The Agent calls the specified tool via the `ToolManager`. Upon receiving the result, it transitions back to `THINKING` to evaluate the tool's output and decide on the next move for the *current* task.
5.  **RESPONDING**: The Agent yields the final answer for the current step. This signals to the Outer Loop that this single `TodoItem` is complete.

This two-level design separates the concerns of high-level planning from the details of low-level execution, adhering to the Single Responsibility Principle and making the system more modular and maintainable.

## 3. Core Feature Specifications

### 3.1. Todo List & Planning
- The agent **must** use a `TodoWrite` tool (or similar mechanism) to create and update a `TodoItem` list that is persisted via `P1` and visible in the UI.
- The `Todo` list is the central driver of the agent's execution.

### 3.2. Sub-Agent Delegation (`Task` Tool)
- When the `Task` tool is called, the `AgentExecutor` **must** instantiate a new, separate `AgentExecutor` instance with a fresh memory state to handle the sub-task.

### 3.3. Real-time Steering (Async Queue)
- The `AgentExecutor` **must** accept an `asyncio.Queue` in its constructor.
- The check for this queue **must** occur at the beginning of each execution cycle (the `OBSERVE & STEER` step).

### 3.4. Confidence-Driven Reflection
- The reflection mechanism (parsing a `Confidence: 0.xx` score from the LLM's output) is the primary technique for implementing the "Reflect on Plan" and "Reflect on Result" quality gates.

## 4. Test Plan Summary

- **TDD Approach**: All logic must be test-driven.
- **Dependency Mocking**: All tests **must** use mocked versions of `P1`, `P2`, `P3`, and `P4` services.
- **Key Test Cases**:
    - **Happy Path**: A test that verifies the full `Plan -> Execute -> Complete` cycle for a simple goal.
    - **Plan Reflection**: A test where the LLM mock first returns a poor plan (low confidence), forcing the agent to re-plan before executing.
    - **Result Reflection**: A test where a tool mock returns an error or a low-confidence result, forcing the agent to retry or change the plan.
    - **Steering**: A test where a user command from the queue interrupts the current plan and causes a new plan to be generated.
- **Acceptance**: Test coverage >= 90%; passes `ruff` and `mypy --strict`.

## 5. Implementation Status

-   **`AgentExecutor` Class**: The core class exists but requires a major refactoring to implement the "Plan-Reflect-Execute" cycle.
-   **Confidence-Driven Logic**: A basic version of this exists and can be adapted for the new reflection quality gates.
-   **Todo List & Planning**: **Not yet implemented.**
-   **Sub-Agent Delegation (`Task` Tool)**: **Not yet implemented.**
-   **Real-time Steering (Async Queue)**: The queue is passed in, but the core logic to check and act on it is **not yet implemented**.
