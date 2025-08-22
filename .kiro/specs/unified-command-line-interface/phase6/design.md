# Phase 6: Advanced Interactive CLI - Design

## 1. Introduction

This document outlines the technical design for Phase 6: Advanced Interactive CLI. The goal is to create a sophisticated, full-screen Terminal User Interface (TUI) using the `prompt_toolkit` library. This TUI will provide a persistent, mode-based interaction model with comprehensive keyboard shortcuts, enhancing user productivity and experience.

## 2. Architecture Overview

The design centers around a new module, `src/cli/interactive_tui.py`, which will house the `prompt_toolkit`-based application. This application will manage the TUI lifecycle, handle user input, route commands, and render output. It will interact with existing core services and CLI command handlers through well-defined interfaces.

### 2.1. Key Components

1.  **`InteractiveTUIApp` Class**: The main application class responsible for initializing and running the `prompt_toolkit` TUI.
2.  **`prompt_toolkit.Application`**: The core `prompt_toolkit` application instance that manages the event loop, input, and rendering.
3.  **Layout System (`HSplit`, `VSplit`, `Window`)**: Defines the visual structure of the TUI, including the main output area, status bar, and input area.
4.  **Key Bindings (`KeyBindings`)**: Manages all keyboard shortcuts and their associated actions.
5.  **State Manager (`AppState`)**: A class or set of variables to track the application's state (e.g., current mode, active session ID).
6.  **Command Router (`CommandRouter`)**: Parses user input and dispatches it to the appropriate handler (either a built-in TUI action or an existing CLI command).
7.  **Mode Handlers**: Specific classes or functions to handle the logic for each major mode (Personal Assistant, Debate, Chat, Wiki).
8.  **Output Renderer**: A component responsible for formatting and displaying text, tables, and other output in the main output area.

### 2.2. Data Flow

1.  **Initialization**: `src/cli/main.py` calls `InteractiveTUIApp().run()`.
2.  **TUI Setup**: `InteractiveTUIApp` initializes the `prompt_toolkit.Application` with its layout, key bindings, and initial state.
3.  **User Input**: User types into the input area and presses Enter or a shortcut key.
4.  **Input Processing**:
    *   If it's a key binding (e.g., `Ctrl+P`), the corresponding handler in `KeyBindings` is executed.
    *   If it's a command (text input + Enter), the `CommandRouter` parses the input.
5.  **Command Execution**:
    *   The `CommandRouter` determines if the command is a TUI-specific action or an existing CLI command.
    *   For CLI commands, it calls the appropriate function from the existing CLI modules (e.g., `src/cli/main.py` functions or refactored logic).
6.  **Output Generation**: The result of the command execution is formatted (if necessary) and sent to the `Output Renderer`.
7.  **Rendering**: The `Output Renderer` updates the content of the main output area.
8.  **State Update**: If the command changes the application state (e.g., switches mode), the `AppState` is updated, and the UI (e.g., status bar) reflects this change.

## 3. Detailed Design

### 3.1. `src/cli/interactive_tui.py`

This is the primary file for the interactive TUI implementation.

#### 3.1.1. `InteractiveTUIApp` Class

*   **`__init__(self)`**:
    *   Initializes `AppState`.
    *   Creates `TextArea` widgets for output and input.
    *   Defines the `Layout` using `HSplit`.
    *   Creates `KeyBindings`.
    *   Initializes `prompt_toolkit.Application`.
*   **`run(self)`**: Starts the `prompt_toolkit` application event loop.
*   **`_create_layout(self)`**: Defines the visual structure of the TUI.
*   **`_create_key_bindings(self)`**: Sets up all keyboard shortcuts.
*   **`_execute_command(self, command_text)`**: Routes and executes user commands.
*   **`_update_status_bar(self)`**: Updates the status bar based on `AppState`.

#### 3.1.2. `AppState` Class/Structure

*   **`current_mode`**: Enum (e.g., `Mode.PERSONAL_ASSISTANT`, `Mode.DEBATE_SETUP`, `Mode.CHAT`, `Mode.WIKI`).
*   **`active_session_id`**: String identifier for the current session (e.g., PA session ID, Chat room ID).
*   **`status_message`**: String for temporary status messages.

#### 3.1.3. Key Bindings

*   **`Ctrl+P`**: `switch_to_personal_assistant_mode()`
*   **`Ctrl+D`**: `initiate_debate_setup()`
*   **`Ctrl+T`**: `switch_to_chat_mode()`
*   **`Ctrl+W`**: `switch_to_wiki_mode()`
*   **`Ctrl+H`**: `show_help_screen()`
*   **`Ctrl+Q`**: `request_quit()` (Sets a flag; second press exits)
*   **`ESC`**: `abort_current_operation()` or `clear_input_line()`
*   **`Ctrl+Enter`**: `restart_last_operation()`
*   **`Enter`** (in input area): Calls `_execute_command()` with the current input text.

#### 3.1.4. Command Router

*   A function `_route_command(command_text: str)` that parses the input string.
*   It checks for built-in TUI commands (e.g., `/clear`, `/help`).
*   If not a TUI command, it maps the command to an existing CLI function (e.g., `pa chat` -> `personal_assistant_router.process_query`).

### 3.2. Integration with Existing CLI

To avoid duplicating logic, the TUI should reuse existing CLI command implementations as much as possible.

*   **Refactor CLI Commands**: Extract the core logic from `@app.command()` functions into separate, testable functions. For example, the logic inside `pa_chat` in `src/cli/main.py` should be moved to a function like `async def handle_pa_chat_query(query: str, ...)` which is then called by both the Typer command and the TUI command router.
*   **Dependency Management**: Ensure the TUI app has access to all necessary service instances (e.g., `PersonalAssistantRouter`, `ChatCoordinator`) that the CLI commands depend on.

### 3.3. Mode Handlers

Each mode (Personal Assistant, Debate, Chat, Wiki) might require specific handling for input/output and state transitions.

*   **Personal Assistant Mode**:
    *   Input: Treats all input as a query to the PA unless it's a command (e.g., `/help`).
    *   Output: Displays PA responses in a conversational format.
*   **Debate Setup Mode**:
    *   Input: Guides the user through the debate setup steps (topic, roles, etc.) using prompts in the output area and input area.
    *   Output: Shows setup prompts and confirmation messages.
*   **Chat Mode**:
    *   Input: Treats input as a message to the current chat room.
    *   Output: Displays chat history and new messages.
*   **Wiki Mode**:
    *   Input: Guides creation/editing workflow.
    *   Output: Shows wiki page previews, edit prompts, and confirmation messages.

### 3.4. User Experience Considerations

*   **Visual Design**: Use `prompt_toolkit` styles to color-code different types of output (user input, system messages, AI responses).
*   **Scrolling**: The main output area (`TextArea`) should support scrolling through history.
*   **History**: Implement command history accessible via Up/Down arrow keys in the input area.
*   **Help System**: The `/help` command and `Ctrl+H` shortcut should provide clear, searchable documentation.

## 4. Technology Stack

*   **Primary Framework**: `prompt_toolkit` for TUI creation and management.
*   **Existing Libraries**: `rich` for rich text formatting (if needed, though `prompt_toolkit` has its own formatting capabilities).
*   **Core Services**: Reuse all existing DAIP-LIVE backend services (PersonalAssistantRouter, ChatCoordinator, WikiService, etc.).