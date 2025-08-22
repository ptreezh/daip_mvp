# CLI Phase 3 Tasks Repair Plan

## Current Status Analysis

Based on the review of the tasks.md file and the code, here's a summary of the issues:

1.  **CLI Integration Issues**:
    *   The `chat` and `wiki` commands are registered twice in `src/cli/main.py` (lines 191-194).
    *   There are duplicate sections of code initializing services in `src/cli/main.py`.

2.  **Chat Functionality Issues**:
    *   `chat list`: Not implemented in `chat_commands.py`.
    *   `chat history`: Implemented but relies on placeholder functionality in `ChatCoordinator`.
    *   `chat clear`: Implemented but relies on placeholder functionality in `ChatCoordinator`.
    *   State management issues in `ChatCoordinator` (load/save state).

3.  **Wiki Functionality Issues**:
    *   `wiki delete`: Not implemented, just shows a message in `wiki_commands.py`.
    *   `wiki list`: Implemented with a workaround in `wiki_commands.py`, but `WikiService` has a proper `list_all_entries` method that should be used.
    *   `wiki edit`: Creates proposals but there's no command to approve them.

## Repair Plan

### 1. Fix CLI Integration Issues (High Priority)

**File**: `src/cli/main.py`

*   **Task 1.1**: Remove duplicate `app.add_typer` calls for `chat_app` and `wiki_app` (lines 193-194).
*   **Task 1.2**: Remove duplicate service initialization code (lines 109-117).
*   **Task 1.3**: Ensure `get_wiki_service` function is defined only once.

### 2. Fix Chat Functionality (High Priority)

**File**: `src/cli/chat_commands.py`

*   **Task 2.1**: Implement the `list` command to show all chat rooms.
*   **Task 2.2**: Review and improve the `history` command implementation.
*   **Task 2.3**: Review and improve the `clear` command implementation.

**File**: `src/virtual_role_chat/chat_coordinator.py`

*   **Task 2.4**: Implement proper `get_room_history` method that works with `ChatSessionService`.
*   **Task 2.5**: Implement proper `clear_room_history` method.
*   **Task 2.6**: Fix `load_state` and `save_state` methods to properly manage current room state.

### 3. Fix Wiki Functionality (Medium Priority)

**File**: `src/cli/wiki_commands.py`

*   **Task 3.1**: Implement the `delete` command using `WikiService.delete_entry`.
*   **Task 3.2**: Implement a command to approve edit proposals (e.g., `wiki proposal approve`).
*   **Task 3.3**: Fix the `list` command to use `WikiService.list_all_entries`.

### 4. Testing and Verification (High Priority)

*   **Task 4.1**: Test all chat commands (`start`, `message`, `history`, `clear`, `close`, `delete`, `list`).
*   **Task 4.2**: Test all wiki commands (`create`, `view`, `edit`, `delete`, `search`, `list`, `proposal approve`).
*   **Task 4.3**: Verify that state is properly maintained between CLI invocations.

## Implementation Order

1.  Fix CLI integration issues in `src/cli/main.py`.
2.  Implement missing chat commands and fix `ChatCoordinator` methods.
3.  Implement missing wiki commands.
4.  Test all functionality.