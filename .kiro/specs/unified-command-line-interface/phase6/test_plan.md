# Phase 6: Advanced Interactive CLI - Test Plan

This document outlines the test plan for Phase 6, ensuring the new Advanced Interactive CLI mode is robust, functional, and meets all requirements. The plan emphasizes Test-Driven Development (TDD) and includes unit, integration, and end-to-end (E2E) tests.

## 1. Testing Strategy

*   **TDD**: All new code for the interactive TUI will be developed using TDD. Tests will be written before the implementation of each logical unit.
*   **Unit Tests**: Focus on testing individual functions and classes in isolation (e.g., `AppState`, command router logic, mode handlers).
*   **Integration Tests**: Verify the interaction between components (e.g., key bindings triggering state changes, command router calling the correct CLI logic, TUI layout rendering).
*   **E2E/Manual Tests**: Simulate complete user workflows to ensure the overall experience is smooth and correct. This includes testing keyboard shortcuts, mode transitions, and complex command execution.

## 2. Test Environment

*   **Framework**: `pytest` for Python.
*   **Dependencies**: All existing project dependencies, plus `prompt_toolkit`.
*   **Test Structure**: Tests will be located in `tests/cli/test_interactive_tui.py` and potentially subdirectories for better organization.

## 3. Test Cases by Component

### 3.1. `InteractiveTUIApp` Core

*   **Initialization**:
    *   **Test**: Verify `InteractiveTUIApp()` initializes without error.
    *   **Test**: Confirm `AppState` is correctly initialized.
    *   **Test**: Ensure `prompt_toolkit.Application` is created with the correct layout and key bindings.
*   **Running**:
    *   **Test**: (Integration) Mock `prompt_toolkit.Application.run()` and verify `InteractiveTUIApp.run()` calls it.

### 3.2. Layout and UI Elements

*   **Layout Structure**:
    *   **Test**: (Integration) Verify the `HSplit` layout contains the expected number and type of child containers/widgets (Output Area, Status Bar, Input Area).
*   **Status Bar**:
    *   **Test**: Verify `_update_status_bar()` correctly updates the status bar text based on `AppState.current_mode`.
    *   **Test**: Ensure status bar text updates after mode changes triggered by key bindings.

### 3.3. Key Bindings

*   **`Ctrl+Q` (Quit)**:
    *   **Test**: Verify the `Ctrl+Q` key binding is registered.
    *   **Test**: (Integration) Simulate `Ctrl+Q` press and assert that the application's exit mechanism is triggered (e.g., `app.exit()` is called).
*   **Mode Switching Shortcuts (`Ctrl+P`, `Ctrl+D`, `Ctrl+T`, `Ctrl+W`)**:
    *   **Test**: Verify each mode-switching key binding is registered.
    *   **Test**: Simulate each key press and assert that `AppState.current_mode` is updated correctly.
    *   **Test**: Assert that the status bar is updated after each mode switch.
*   **Other Shortcuts (`Ctrl+H`, `ESC`, `Ctrl+Enter`)**:
    *   **Test**: Verify registration and basic triggering of these bindings.
    *   **Test**: For `Ctrl+H`, assert that the help screen content is prepared or displayed.

### 3.4. Command Routing and Execution

*   **Command Input**:
    *   **Test**: (Integration) Simulate typing text into the input area and pressing Enter, asserting that the `_execute_command` method is called with the correct text.
*   **Command Router (`_route_command`)**:
    *   **Test**: Unit test `_route_command` with various inputs:
        *   Built-in TUI commands (e.g., `/clear`, `/help`).
        *   Simple existing CLI commands (e.g., `status`).
        *   Complex existing CLI commands (e.g., `pa chat "test query"`, `debate start "Topic"`).
        *   Invalid commands.
    *   **Test**: Assert that valid commands result in the correct handler function being called or prepared for calling.
    *   **Test**: Assert that invalid commands result in an appropriate error message.
*   **Integration with CLI Logic**:
    *   **Test**: (Integration) Mock a refactored CLI command function and simulate its call through `_route_command` and `_execute_command`, asserting that the mock is called with the correct arguments.
    *   **Test**: Simulate a command that produces output and assert that the output area is updated correctly.

### 3.5. `AppState` Management

*   **Test**: Unit test all methods of the `AppState` class/structure for getting and setting state variables (`current_mode`, `active_session_id`, etc.).

### 3.6. Mode-Specific Handlers

*   **Personal Assistant Mode**:
    *   **Test**: Simulate entering PA mode (`Ctrl+P`) and then executing a command/query, asserting that it's routed to the PA logic.
*   **Debate Setup Mode**:
    *   **Test**: Simulate `Ctrl+D` and assert that the debate setup workflow is initiated (e.g., prompts appear in output).
*   **Chat Mode**:
    *   **Test**: Simulate `Ctrl+T` and assert that chat mode is activated.
    *   **Test**: In chat mode, simulate sending a message and assert interaction with the chat service.
*   **Wiki Mode**:
    *   **Test**: Simulate `Ctrl+W` and assert that wiki mode is activated.
    *   **Test**: In wiki mode, simulate a command and assert interaction with the wiki service.

### 3.7. Robustness and Error Handling

*   **Graceful Error Handling**:
    *   **Test**: Mock a CLI command function to raise an exception and simulate its execution, asserting that a user-friendly error message is displayed in the output area and the TUI does not crash.
*   **`Ctrl+C` Interruption**:
    *   **Test**: (Manual/E2E) Start a long-running command and use `Ctrl+C` to cancel it, observing that the operation stops and the prompt returns.

### 3.8. CLI Integration

*   **`interactive` Command**:
    *   **Test**: Using `cli_runner` (like in `tests/cli/test_cli_commands.py`), test that `daip-cli interactive` calls the `InteractiveTUIApp.run()` method.

## 4. Test Execution

*   **Automation**: All unit and integration tests will be automated and run as part of the standard `pytest` suite.
*   **Manual/E2E Testing**: A checklist of key user workflows will be created for manual testing before major releases or after significant changes to the TUI.

## 5. Acceptance Criteria Traceability

Each test case should map back to a specific acceptance criterion in `requirements.md` to ensure full coverage.