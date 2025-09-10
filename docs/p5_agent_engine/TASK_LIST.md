# P5: Agent Engine Task List

This task list is based on the "Planning-Driven, Reflection-Enhanced" architecture defined in the `README.md`.

## Phase 1: Core Refactoring & Foundational Features

-   [ ] **T-P5-01**: **Implement Real-time Steering**. 
    -   **Description**: Modify the `AgentExecutor.run` loop to check the `user_input_queue` at the start of each cycle (the `OBSERVE & STEER` step). 
    -   **Acceptance Criteria**: A new user message from the queue should be prioritized and can alter the agent's next action. This will be verified by a TDD test case.

-   [ ] **T-P5-02**: **Refactor Main Loop around a `Todo` List**.
    -   **Description**: Change the `while` loop condition from being state-based to being driven by the status of a `Todo` list (e.g., `while not todo_list.is_complete()`).
    -   **Acceptance Criteria**: The agent's lifecycle is tied to the completion of the plan.

-   [ ] **T-P5-03**: **Implement `TodoWrite` Tool and Initial Planning**.
    -   **Description**: Create a basic `TodoWrite` tool. The first step of the `run` method should be to call the LLM to generate a plan and use `TodoWrite` to populate the initial `Todo` list.
    -   **Acceptance Criteria**: Given a goal, the agent generates a multi-step `Todo` list before starting execution.

-   [ ] **T-P5-04**: **Integrate "Reflect on Result" Quality Gate**.
    -   **Description**: After a tool execution, use the existing confidence-parsing logic to evaluate the result. If confidence is low, the agent should log this and decide on a corrective action (e.g., retry, or add a new step to the `Todo` list).
    -   **Acceptance Criteria**: A mocked tool failure should trigger the reflection step.

## Phase 2: Advanced Features

-   [ ] **T-P5-05**: **Integrate "Reflect on Plan" Quality Gate**.
    -   **Description**: After the initial `Todo` list is generated, add a reflection step to evaluate the quality of the plan itself before execution begins.
    -   **Acceptance Criteria**: A test can show that a deliberately poor initial plan is revised by the agent before execution.

-   [ ] **T-P5-06**: **Implement `Task` Tool for Sub-Agent Delegation**.
    -   **Description**: Implement the special logic for the `Task` tool, allowing it to instantiate and run a new, isolated `AgentExecutor`.
    -   **Acceptance Criteria**: A `Todo` item that calls the `Task` tool correctly triggers a sub-agent and gets a result back.
