---
id: P6
title: Terminal Interfaces (CLI & TUI)
status: Rewritten
architecture_drivers: [SOLID, KISS]
---

# P6: Terminal Interfaces (CLI & TUI)

## 1. Principle-Driven Refactoring

This specification has been rewritten based on core software design principles. The primary goal is to define a clear, simple, and robust interface layer that is decoupled from the agent's core logic.

-   **Single Responsibility (SRP)**: This package is solely responsible for presenting the agent's state to the user in a terminal and accepting user input.
-   **Interface Segregation**: This package depends *only* on the abstract event stream produced by `P5`, not its implementation details.

## 2. Overview

This package provides two user entry points, both interacting with the `P5` agent engine:

1.  **CLI (Command Line Interface)**: A non-interactive tool (`daip`) for scripting and direct commands, built on `Typer`.
2.  **TUI (Textual User Interface)**: A rich, interactive, full-screen application for conversational interaction, built on `Textual`.

## 3. The Engine-UI Contract (The Event Stream)

The single most important contract in this package is the event stream yielded by `P5.AgentExecutor.run()`. P6 consumes this stream. The Pydantic models for these events are defined in `P0` (`src/daip_live/core/models.py`). Example event structures:

```json
{"type": "thought", "content": "I need to find the file first."}
{"type": "tool_call", "tool_name": "read_file", "args": {"path": "/path/to/file"}}
{"type": "tool_output", "tool_name": "read_file", "status": "success", "output": "File content..."}
{"type": "final_response", "content": "Here is the final answer."}
{"type": "permission_request", "tool_name": "delete_file", "args": {...}}
```

## 4. CLI Specification

The `daip` command focuses on core agent execution and management.

-   `daip run "<goal>" [--role <name>]`: **Primary entry point.** Starts the interactive TUI session to accomplish a goal.
-   `daip project scaffold --description "..."`: Generates project file structures from a natural language description using an LLM.
-   `daip knowledge sync`: Manually triggers the knowledge base sync process from `P2`.
-   `daip session list`: Lists previous sessions from `P1`.
-   `daip session view <id>`: Displays the full dialogue for a specific session.
-   `daip role list`: Lists all available roles.
-   `daip role view <name>`: Displays details for a specific role.

## 5. TUI Specification

The TUI provides the core interactive experience.

-   **Architecture**: The TUI is a reactive component that renders widgets based on the event stream from the `P5` engine.
-   **Layout**: A simple, three-part layout: a scrollable message history, a status bar, and an input box.
-   **Status Bar**: Displays data queried from the `P5` engine (e.g., via a `get_status()` method), such as `(Model: llama3, Tokens: 4096/8192, Status: Executing tool)`.
-   **Asynchronous Input**: User input is captured and put onto an `asyncio.Queue`, which is passed to the `P5` engine during initialization. This decouples user input from the agent's execution cycle.
-   **Permission Handling**: When a `permission_request` event is received, the TUI must push a modal dialog screen to capture user confirmation (Y/N) and send the response back to the engine.

## 6. Task List (TDD)

-   **CLI**: Use `typer.testing.CliRunner` to test each command. Mock the `P5` engine dependency.
-   **TUI**: Use `Textual.run_test` to test the application headless.
    1.  Test that the TUI correctly renders a mock stream of `AgentEvent` objects into the correct widgets.
    2.  Test the permission dialog flow.
    3.  Test that user input is correctly placed on the message queue.

## 7. Key Architectural Decisions & Open Issues

-   **Decision (SRP/KISS)**: The TUI's only job is to render events. It contains no business logic. All logic resides in `P5`.
-   **Open Issue (P5)**: A `get_status()` API on the `AgentExecutor` needs to be implemented to provide real-time model, token, and status data to the TUI status bar. This is a blocker for full TUI functionality.

## 8. Implementation Status (as of 2025-09-05)

-   **CLI Commands**:
    -   `daip run`: Implemented and functional.
    -   `daip knowledge sync`: Implemented and functional.
    -   `daip session list/view`: Implemented and functional.
    -   `daip role list/view`: Implemented and functional.
    -   `daip project scaffold`: Implemented and functional.
    -   `daip config`: **Not Implemented.**

-   **TUI Core**: A sophisticated TUI is implemented with advanced features, including multiple screens, focus management, and a shortcut command system. The documentation was severely outdated and described it as "basic".

-   **Status Bar**: Implemented, but uses hardcoded values for model name and token counts. It is partially integrated with the event stream for status updates but requires the `get_status` API from P5 for full functionality.

-   **Asynchronous Input**: Fully implemented. The TUI correctly captures user input (both regular messages and shortcut commands) and passes it to the agent engine via an `asyncio.Queue`.

-   **Permission Handling**: The UI flow for permission handling is fully implemented, including a modal dialog. The final step of sending the user's decision back to the agent engine requires integration.