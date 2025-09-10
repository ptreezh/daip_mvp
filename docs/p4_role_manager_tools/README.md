---
id: P4
title: Role & Tool Management
status: Finalized
architecture_drivers: [SOLID, KISS, KDD, Security-First]
---

# P4: Role & Tool Management

## 1. Overview

This work package (`P4`) provides the critical infrastructure for defining agent personas (`RoleManager`) and their capabilities (`ToolManager`). It is the nexus of agent capability and system security, implementing a robust, multi-stage pipeline for all tool executions.

## 2. Role & Prompt Management

-   **`RoleManager`**: A class responsible for loading role definitions from `.yaml` files in the `roles/` directory.
-   **Configuration**: Role definition files **must** be parsed and validated against the `P0.RoleConfig` Pydantic model. This model defines the structure, including `name`, `persona_prompt_file`, and a list of `allowed_tools`.
-   **System Prompt Meta-Instruction**: The `RoleManager` is responsible for injecting a mandatory meta-instruction into every system prompt before it is used. This instruction enables the self-reflection loop in `P5`.
    -   **Instruction Content**: *"After every response, you MUST provide a 'Confidence' score on a scale of 0.00 to 1.00, reflecting your certainty in the factual accuracy and completeness of your answer. Format this as `Confidence: 0.xx`. If your confidence is below 0.95, you MUST also list the specific parts you are least confident about."*

## 3. Tool Management

### 3.1. `@tool` Decorator: The Registration Mechanism

-   The `@tool` decorator is the sole mechanism for registering a function as a tool.
-   **Implementation**: The decorator **must** use Python's `inspect` module to read the function's signature (`__name__`, `__doc__`, and parameter type hints).
-   It **must** then dynamically create a `pydantic.BaseModel` subclass from the function's arguments. This model is used for input validation in the execution pipeline.
-   The function pointer and its generated Pydantic model are stored in the `ToolManager`'s internal registry.

### 3.2. The 6-Stage Secure Execution Pipeline

The `execute_tool(name, args, session_context)` method is the heart of the `ToolManager`. It **must** implement the following 6 stages sequentially:

1.  **Discovery**: Find the tool in the registry. Fail with `ToolNotFoundError` if not found.
2.  **Input Validation**: Validate the `args` dictionary against the tool's registered Pydantic model. Fail with `ToolInputError` on validation failure.
3.  **Precondition Check (Write-After-Read)**: For any tool flagged as a `write` operation, this stage checks if the target resource has been "read" recently. 
    -   **Mechanism**: The `session_context` object must contain a `set` of `recently_read_resources`. Read-tools add their target to this set. Write-tools check for presence in this set. Fail with `ToolPreconditionError` if the check fails.
4.  **Permission Check**: Check the tool against the `ToolPermissionConfig` (loaded from `config.yaml`).
    -   `deny`: Fail immediately with `ToolPermissionError`.
    -   `allow`: Proceed to the next stage.
    -   `ask`: **Raise a `ToolPermissionRequest(tool_name, args)` exception.** This is a control-flow exception designed to be caught by the UI layer (`P6`/`P7`). The UI prompts the user and, if approved, re-calls `execute_tool` with a `confirmation_granted=True` flag, which bypasses this check.
5.  **Execution**: Call the tool's Python function in a `try/except` block, monitored by a timeout.
6.  **Result Formatting**: Standardize the return value or any captured exception into a clean string for the agent.

## 4. Implementation Policies & Requirements

-   **Path Traversal Security**: Any tool that accepts a file path **must** resolve it to an absolute path and verify it is within a pre-configured, allowed project directory. Any attempt to access a parent directory (`../`) that would leave the project root must be rejected.
-   **Dependency Checks**: Tools relying on external command-line programs (e.g., `pandoc`) **must** perform a check for the executable's existence on startup. If the dependency is missing, the tool should be disabled and a warning logged.

## 5. Test Plan Summary

-   **TDD Approach**: All components must be test-driven.
-   **Key Test Cases**:
    -   Verify the `@tool` decorator correctly generates a Pydantic schema from a function signature.
    -   For the execution pipeline, create a specific test for **each failure mode** in each stage (e.g., test for `ToolInputError`, test for `ToolPermissionError`, etc.) to ensure the pipeline aborts correctly.
    -   Test the full, successful execution path.
    -   Test the `ask` permission flow by catching the `ToolPermissionRequest` exception.
    -   Test the path traversal security by providing an invalid path like `"../../etc/passwd"` and asserting it fails.
-   **Acceptance**: Test coverage >= 90%; passes `ruff` and `mypy --strict`.

## 6. Implementation Status

-   **`RoleManager`**: Currently a placeholder. The logic for loading role definitions from YAML files and injecting system prompts is pending implementation.
-   **`@tool` Decorator**: Fully implemented and tested. It correctly registers functions as tools and generates Pydantic models for input validation.
-   **`ToolManager`**: The 6-stage secure execution pipeline is fully implemented and tested, including discovery, input validation, precondition checks, permission checks, execution, and result formatting.
-   **Implementation Policies**: Path traversal security and dependency checks are pending full implementation within specific tools.
