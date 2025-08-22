# Phase 6: Advanced Interactive CLI - Task List

This document outlines the tasks required to implement the Advanced Interactive CLI as specified in the requirements and designed in the design document. All tasks will follow the Test-Driven Development (TDD) approach, ensuring robustness and correctness from the outset.

## 1. Project Setup and Initial TUI Structure

### 1.1. Create `src/cli/interactive_tui.py`

*   **Task**: Create the main module file for the interactive TUI.
*   **TDD**:
    *   Write a basic test to ensure the file exists and can be imported.
    *   Write a test for the `InteractiveTUIApp` class constructor to verify initial state setup.
*   **Implementation**:
    *   Create the file.
    *   Define the `InteractiveTUIApp` class with a basic `__init__` and `run` method.
    *   Add necessary imports (`prompt_toolkit`).

### 1.2. Implement Basic TUI Layout

*   **Task**: Set up the fundamental layout of the TUI with an output area, status bar, and input area.
*   **TDD**:
    *   Write a test to verify that the `InteractiveTUIApp` creates a `prompt_toolkit.Application` instance.
    *   Write a test (potentially integration-style) to check that the layout contains the expected widgets (3 main sections).
*   **Implementation**:
    *   Implement the `_create_layout` method in `InteractiveTUIApp`.
    *   Use `prompt_toolkit` containers (`HSplit`, `Window`, `TextArea`) to define the structure.
    *   Initialize the `prompt_toolkit.Application` with this layout in the `__init__` method.

### 1.3. Add Basic Key Bindings

*   **Task**: Implement the most fundamental key binding: `Ctrl+Q` to quit.
*   **TDD**:
    *   Write a test to verify that the `KeyBindings` object is created.
    *   Write a test to ensure the `Ctrl+Q` binding is registered.
    *   Write an integration test to simulate `Ctrl+Q` and assert that the application exits (or sets an exit flag).
*   **Implementation**:
    *   Implement the `_create_key_bindings` method in `InteractiveTUIApp`.
    *   Add the `Ctrl+Q` binding logic to exit the application.

## 2. Core TUI Functionality and State Management

### 2.1. Implement `AppState` Management

*   **Task**: Create and integrate the `AppState` to track the current mode and session.
*   **TDD**:
    *   Write unit tests for the `AppState` class (or data structure) to verify initial state and state transition methods (e.g., `set_mode`, `get_mode`).
*   **Implementation**:
    *   Define the `AppState` class or data structure.
    *   Integrate `AppState` into `InteractiveTUIApp`, initializing it in `__init__`.
    *   Implement methods to update and retrieve the state.

### 2.2. Implement Status Bar Updates

*   **Task**: Make the status bar reflect the current `AppState`.
*   **TDD**:
    *   Write a test to verify that the `_update_status_bar` method correctly updates the text of the status bar widget based on `AppState`.
*   **Implementation**:
    *   Implement the `_update_status_bar` method.
    *   Call `_update_status_bar` after initializing the app and after any state change.

### 2.3. Implement Command Input and Basic Execution

*   **Task**: Allow users to type commands into the input area and execute them via the Enter key. Start with a simple echo command.
*   **TDD**:
    *   Write a test to verify that pressing Enter in the input area triggers the command execution logic.
    *   Write a test for the command router to handle a simple "echo" command.
    *   Write an integration test to simulate typing "echo Hello" and pressing Enter, then assert that "Hello" appears in the output area.
*   **Implementation**:
    *   Add an `Enter` key binding for the input area that calls `_execute_command`.
    *   Implement a basic `_execute_command` method that currently just appends the input to the output area.
    *   Create a placeholder `_route_command` function.

## 3. Command Routing and Integration

### 3.1. Refactor Existing CLI Commands for Reusability

*   **Task**: Extract the core logic from existing `@app.command()` functions into reusable, testable functions.
*   **TDD**:
    *   For each major CLI command group (pa, debate, chat, wiki), identify key functions.
    *   Write unit tests for the new, extracted logic functions to ensure they behave identically to the original command handlers.
*   **Implementation**:
    *   Refactor `src/cli/main.py` and `src/cli/commands/*.py`.
    *   Move core logic (e.g., the body of `pa_chat`) into new, standalone async functions (e.g., `async def process_pa_chat_query(...)`).
    *   Update the original `@app.command()` functions to call these new functions.

### 3.2. Implement Command Router

*   **Task**: Build the `_route_command` logic to parse user input and dispatch to the correct handler (CLI logic or TUI action).
*   **TDD**:
    *   Write unit tests for `_route_command` covering various inputs:
        *   Built-in TUI commands (e.g., `/clear`, initially dummy implementations).
        *   Simple CLI commands (e.g., `status`).
        *   Complex CLI commands (e.g., `pa chat "test query"`).
        *   Invalid commands.
*   **Implementation**:
    *   Implement the `_route_command` function.
    *   Add logic to parse the command string and map it to the refactored CLI functions or internal TUI actions.
    *   Integrate `_route_command` into `_execute_command`.

### 3.3. Integrate Core Services

*   **Task**: Ensure the TUI app has access to and correctly uses all necessary backend services.
*   **TDD**:
    *   Write tests to verify that `InteractiveTUIApp` is initialized with the required service dependencies.
    *   Write integration tests for commands that rely on services (e.g., `pa chat`) to ensure they interact correctly.
*   **Implementation**:
    *   Modify `InteractiveTUIApp.__init__` to accept service dependencies or retrieve them from a central place.
    *   Pass these services to the refactored command functions when they are called.

## 4. Implementing Major Modes and Features

### 4.1. Personal Assistant Mode

*   **Task**: Implement the logic for `Ctrl+P` to switch to and interact with the Personal Assistant.
*   **TDD**:
    *   Write a test for the `Ctrl+P` key binding to verify it updates `AppState` to `PERSONAL_ASSISTANT` mode.
    *   Write a test to ensure the status bar updates correctly.
    *   Write an integration test to simulate `Ctrl+P` followed by typing a query and pressing Enter, then assert that the PA response is displayed.
*   **Implementation**:
    *   Add `Ctrl+P` key binding that calls a `switch_to_personal_assistant_mode` method.
    *   Implement `switch_to_personal_assistant_mode` to update `AppState` and UI.
    *   Modify `_execute_command` or `_route_command` to treat input as a PA query when in `PERSONAL_ASSISTANT` mode.

### 4.2. Debate Setup Mode

*   **Task**: Implement the logic for `Ctrl+D` to initiate the debate setup flow.
*   **TDD**:
    *   Write a test for the `Ctrl+D` key binding.
    *   Write tests for the debate setup steps (topic input, role selection, confirmation).
    *   Write an integration test to simulate the full setup flow.
*   **Implementation**:
    *   Add `Ctrl+D` key binding.
    *   Implement debate setup logic, guiding the user through prompts in the output/input areas.
    *   Interact with the refactored debate creation/start logic.

### 4.3. Chat Mode

*   **Task**: Implement `Ctrl+T` for chat functionalities.
*   **TDD**:
    *   Write tests for `Ctrl+T` key binding.
    *   Write tests for switching/creating chats, sending messages, and displaying history.
    *   Integration test for a simple chat interaction.
*   **Implementation**:
    *   Add `Ctrl+T` key binding.
    *   Implement chat mode logic.
    *   Integrate with `ChatCoordinator` and related services.

### 4.4. Wiki Mode

*   **Task**: Implement `Ctrl+W` for wiki functionalities.
*   **TDD**:
    *   Write tests for `Ctrl+W` key binding.
    *   Tests for creating/editing/viewing wiki pages.
    *   Integration test for a wiki workflow.
*   **Implementation**:
    *   Add `Ctrl+W` key binding.
    *   Implement wiki mode logic.
    *   Integrate with `WikiService`.

### 4.5. Help System

*   **Task**: Implement `Ctrl+H` and `/help` command.
*   **TDD**:
    *   Test `Ctrl+H` key binding.
    *   Test `/help` command parsing and output.
    *   Test `/help <command>` for specific command help.
*   **Implementation**:
    *   Add `Ctrl+H` key binding.
    *   Implement help screen display logic.
    *   Enhance `_route_command` to handle `/help`.

### 4.6. Additional Key Bindings and Features

*   **Task**: Implement `ESC`, `Ctrl+Enter`, and other specified key bindings.
*   **TDD**:
    *   Write tests for each key binding's behavior.
*   **Implementation**:
    *   Add key bindings and their corresponding handler functions.

## 5. Robustness, Performance, and Finalization

### 5.1. Error Handling and Graceful Degradation

*   **Task**: Implement comprehensive error handling within the TUI.
*   **TDD**:
    *   Write tests to simulate errors in command execution and assert that user-friendly messages are displayed.
    *   Test `Ctrl+C` interruption of long-running tasks.
*   **Implementation**:
    *   Wrap command execution in `try...except` blocks.
    *   Display errors in the output area.
    *   Implement `Ctrl+C` handling for cancellable tasks.

### 5.2. Performance Optimization

*   **Task**: Ensure the TUI is responsive.
*   **TDD**:
    *   Manual performance testing or basic automated tests to check for responsiveness lags.
*   **Implementation**:
    *   Optimize rendering logic if necessary.
    *   Ensure async operations do not block the UI thread.

### 5.3. CLI Integration

*   **Task**: Add the `interactive` command to the main CLI.
*   **TDD**:
    *   Write a test to verify that `daip-cli interactive` calls the `InteractiveTUIApp.run()` method.
*   **Implementation**:
    *   Add `@app.command("interactive")` to `src/cli/main.py`.
    *   This command should instantiate and run `InteractiveTUIApp`.

### 5.4. Final Testing and Documentation

*   **Task**: Conduct end-to-end testing of the entire interactive mode and update documentation.
*   **TDD**:
    *   Write broader integration/E2E tests covering major user workflows.
*   **Implementation**:
    *   Perform thorough manual and automated testing.
    *   Update `README.md` or CLI help to document the new `interactive` mode.