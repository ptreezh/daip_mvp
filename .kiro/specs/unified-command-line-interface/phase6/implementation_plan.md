# Phase 6: Advanced Interactive CLI - Implementation Plan

This document details the step-by-step implementation plan for the Advanced Interactive CLI, following the Kiro SPECS principles (Requirements -> Design -> Tasks) and a TDD-driven approach. It outlines the sequence of tasks, key considerations, and expected outcomes for each stage.

## 1. Pre-Implementation Phase

*   **Review and Finalize**: Ensure the `requirements.md`, `design.md`, `tasks.md`, and `test_plan.md` documents are thoroughly reviewed and finalized. All stakeholders should agree on the scope and details.
*   **Environment Setup**: Confirm the development environment has `prompt_toolkit` installed and is configured for TDD with `pytest`.

## 2. Iteration 1: Foundation and Basic Structure (Estimated: 2-3 days)

*   **Goal**: Establish the core TUI application structure, basic layout, and the fundamental quit functionality.
*   **Tasks**:
    *   **Task 1.1**: Create `src/cli/interactive_tui.py`.
        *   **TDD**: Write and pass tests for file creation and `InteractiveTUIApp` initialization.
        *   **Implementation**: Create the file and basic class.
    *   **Task 1.2**: Implement Basic TUI Layout.
        *   **TDD**: Write and pass tests for `prompt_toolkit.Application` creation and layout structure.
        *   **Implementation**: Implement `_create_layout` and integrate it into the `Application`.
    *   **Task 1.3**: Add Basic Key Bindings (`Ctrl+Q`).
        *   **TDD**: Write and pass tests for key binding registration and quit functionality.
        *   **Implementation**: Implement `_create_key_bindings` and the quit handler.
*   **Outcome**: A minimal, runnable TUI application that opens a window with a basic layout and can be exited with `Ctrl+Q`.

## 3. Iteration 2: State Management and Command Execution Core (Estimated: 3-4 days)

*   **Goal**: Implement the application state, status bar updates, and the foundational command execution and routing mechanism.
*   **Tasks**:
    *   **Task 2.1**: Implement `AppState` Management.
        *   **TDD**: Write and pass unit tests for the `AppState` class.
        *   **Implementation**: Define and implement `AppState`.
    *   **Task 2.2**: Implement Status Bar Updates.
        *   **TDD**: Write and pass tests for `_update_status_bar`.
        *   **Implementation**: Implement `_update_status_bar` and integrate it.
    *   **Task 2.3**: Implement Command Input and Basic Execution.
        *   **TDD**: Write and pass tests for Enter key binding, command routing (echo), and output display.
        *   **Implementation**: Add Enter key binding, basic `_execute_command`, and placeholder `_route_command`.
*   **Outcome**: The TUI can manage its state, display it in the status bar, receive text input, and echo it to the output area.

## 4. Iteration 3: CLI Integration and Command Routing (Estimated: 4-5 days)

*   **Goal**: Refactor existing CLI commands for reuse and build a robust command router to connect TUI input to system functionality.
*   **Tasks**:
    *   **Task 3.1**: Refactor Existing CLI Commands for Reusability.
        *   **TDD**: Write and pass unit tests for the refactored logic functions.
        *   **Implementation**: Extract core logic from `@app.command()` functions in `src/cli/main.py` and `src/cli/commands/*.py`.
    *   **Task 3.2**: Implement Command Router.
        *   **TDD**: Write and pass unit tests for `_route_command` covering various command types.
        *   **Implementation**: Implement `_route_command` to parse and dispatch commands.
    *   **Task 3.3**: Integrate Core Services.
        *   **TDD**: Write and pass tests for service dependency injection and command integration.
        *   **Implementation**: Ensure `InteractiveTUIApp` can access and pass services to refactored command functions.
*   **Outcome**: The TUI can correctly interpret and execute standard CLI commands (e.g., `status`, `pa chat ...`) by calling the refactored backend logic.

## 5. Iteration 4: Implementing Major Modes (Estimated: 5-7 days)

*   **Goal**: Develop the specific logic and user interactions for each major system mode (Personal Assistant, Debate, Chat, Wiki).
*   **Tasks**:
    *   **Task 4.1**: Personal Assistant Mode.
        *   **TDD**: Write and pass tests for `Ctrl+P` binding, mode switch, and PA query handling.
        *   **Implementation**: Add `Ctrl+P` binding, implement PA mode switch, integrate PA query handling.
    *   **Task 4.2**: Debate Setup Mode.
        *   **TDD**: Write and pass tests for `Ctrl+D` binding and setup flow steps.
        *   **Implementation**: Add `Ctrl+D` binding, implement guided debate setup workflow.
    *   **Task 4.3**: Chat Mode.
        *   **TDD**: Write and pass tests for `Ctrl+T` binding and chat message handling.
        *   **Implementation**: Add `Ctrl+T` binding, implement chat mode logic and message exchange.
    *   **Task 4.4**: Wiki Mode.
        *   **TDD**: Write and pass tests for `Ctrl+W` binding and wiki command handling.
        *   **Implementation**: Add `Ctrl+W` binding, implement wiki mode logic.
    *   **Task 4.5**: Help System.
        *   **TDD**: Write and pass tests for `Ctrl+H` and `/help` command.
        *   **Implementation**: Add `Ctrl+H` binding, implement help screen and command-specific help.
*   **Outcome**: All major system modes are accessible via keyboard shortcuts and provide a basic level of interactive functionality within the TUI.

## 6. Iteration 5: Advanced Features, Robustness, and Finalization (Estimated: 3-4 days)

*   **Goal**: Add remaining keyboard shortcuts, enhance error handling, optimize performance, and integrate the new mode into the main CLI.
*   **Tasks**:
    *   **Task 5.1**: Additional Key Bindings and Features.
        *   **TDD**: Write and pass tests for `ESC`, `Ctrl+Enter`, and other specified bindings.
        *   **Implementation**: Implement logic for `ESC` (abort/clear) and `Ctrl+Enter` (restart).
    *   **Task 5.2**: Error Handling and Graceful Degradation.
        *   **TDD**: Write and pass tests for error handling in command execution.
        *   **Implementation**: Wrap command execution in try/except blocks, display user-friendly errors.
    *   **Task 5.3**: Performance Optimization.
        *   **TDD**: Perform manual testing for responsiveness.
        *   **Implementation**: Optimize any identified bottlenecks in UI updates or command processing.
    *   **Task 5.4**: CLI Integration.
        *   **TDD**: Write and pass a test for the `daip-cli interactive` command.
        *   **Implementation**: Add the `@app.command("interactive")` to `src/cli/main.py`.
*   **Outcome**: A feature-complete, robust, and performant interactive TUI mode that is accessible from the main CLI.

## 7. Post-Implementation Phase

*   **Comprehensive Testing**: Execute the full suite of automated unit, integration, and E2E tests. Perform thorough manual testing based on the checklist.
*   **Documentation Update**: Update `README.md` and CLI `help` text to document the new `interactive` mode, its commands, and keyboard shortcuts.
*   **Code Review**: Conduct a peer code review to ensure code quality and adherence to design.
*   **Deployment**: Merge the feature branch into the main branch after all tests pass and review is complete.

## 8. Risk Management

*   **`prompt_toolkit` Complexity**: The library is powerful but can be complex. Allocate time for learning and troubleshooting.
*   **Integration Challenges**: Ensuring seamless integration with existing async services might require careful handling of event loops.
*   **Performance Bottlenecks**: Rendering large amounts of text or handling rapid input could impact responsiveness. Profiling might be necessary.

This plan provides a structured, TDD-driven approach to building the Advanced Interactive CLI, ensuring quality and alignment with the specified requirements and design.