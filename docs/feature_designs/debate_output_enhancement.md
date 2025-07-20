# Debate Output Enhancement Design Document

## 1. Background

The current Terminal User Interface (TUI) for debates in DAIP-LIVE displays role IDs for each turn, e.g., `[role_id]: opinion`. While functional, this can be less user-friendly, especially if role IDs are not immediately recognizable or descriptive. The user explicitly requested clearer role attribution in the debate output.

## 2. Goal

To enhance the debate output in the TUI by displaying more user-friendly role names instead of just role IDs, thereby improving readability and clarity for the user.

## 3. Design

### 3.1. Output Format Change

The primary change will be in the `ui_renderer` function within `src/cli/main.py`. When a `NewTurnEvent` is received, the output format for each turn will be modified.

*   **Current Format:** `[{event.turn.role_id}]: {event.turn.opinion}`
*   **Proposed Format:** `[{role_name}]: {event.turn.opinion}` or `[{role_name} ({event.turn.role_id})]: {event.turn.opinion}`. The simpler `[{role_name}]: {event.turn.opinion}` is preferred for conciseness, assuming `role_name` is sufficiently descriptive. If `role_name` is not unique or descriptive enough, the format including `role_id` in parentheses can be considered. For this design, we will aim for `[{role_name}]: {event.turn.opinion}`.

### 3.2. Role Name Retrieval

To display the `role_name`, the `ui_renderer` will need access to the `RoleManager`.

*   The `create_application_dependencies` function in `src/composition.py` already returns the `role_manager` instance.
*   The `run_application` function in `src/cli/main.py` receives the `deps` dictionary. This `role_manager` instance will be passed to the `ui_renderer` (or made accessible within its scope).
*   Inside `ui_renderer`, when a `NewTurnEvent` occurs, `role_manager.get_role_by_id(event.turn.role_id)` will be called to retrieve the `Role` object, from which `role.name` can be extracted.

### 3.3. Key Components and Interactions

*   **`src/cli/main.py` (`ui_renderer` function):** This is the main point of modification. It will be updated to fetch the role name and format the output.
*   **`src/models.py` (`NewTurnEvent`):** This event already contains `role_id`, which is sufficient for looking up the role name. No changes are expected here.
*   **`src/core_services/role_manager.py`:** The `get_role_by_id` method will be used to retrieve the `Role` object.
*   **`src/composition.py`:** Ensures `role_manager` is instantiated and passed as a dependency.

## 4. Benefits

*   **Improved Readability:** Users can quickly identify who is speaking by a more descriptive role name.
*   **Enhanced User Experience:** Makes the debate flow easier to follow and understand.
*   **Consistency:** Aligns the TUI output with the concept of named roles rather than abstract IDs.
