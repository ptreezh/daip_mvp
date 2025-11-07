# SPEC: Debate Transcript Saving Enhancement

- **Version**: 1.0
- **Status**: Proposed
- **Applies to**: `debate` command, `EnhancedDebateManager`
- **Author**: TestCraft AI

---

## 1. Feature Goal

As a user, after a debate concludes, I want the generated report file to contain the full transcript of the debate, not just the final summary, so that I can review the entire reasoning process, including each participant's turn and the agent's thought process.

## 2. Acceptance Criteria

1.  **Full Transcript Saved**: The final Markdown report file must contain the complete, turn-by-turn history of the debate.
2.  **Clear Structure**: The transcript must be clearly structured, indicating the speaker (role name) for each turn.
3.  **Metadata Inclusion**: The report must include key metadata at the top, such as the debate topic, the participating roles, and the model assignments (e.g., `pro_arguer→llama3:instruct`).
4.  **Thought Process Included**: Any `ThoughtEvent`s generated during the debate should be included in the transcript, clearly marked to distinguish them from participant responses.
5.  **Summary Preserved**: The final summary of the debate must still be present at the end of the report.
6.  **File Naming**: The file naming convention (`debate_<topic>_<date>.md`) should remain unchanged.

## 3. Technical Design & Approach

1.  **Locate Saving Logic**: The current saving mechanism is handled by the `_save_debate_results` method within `src/daip_live/tui.py`. This method is triggered by the `DebateCompleteEvent`.

2.  **Data Requirement Analysis**: The `DebateCompleteEvent` currently only provides the `summary`. The saving logic does not have access to the full debate history. This is a flaw. The `DAIP_TUI` class, however, maintains the full context in its `self._current_debate` dictionary and the `SessionManager` holds the full `Session` object.

3.  **Proposed Change**:
    -   Modify the `_save_debate_results` method in `tui.py`.
    -   Instead of just using the `event.summary`, the method should access the full debate context stored within the TUI's state (e.g., `self._current_debate` and the session history from `self._session_manager`).
    -   The method will construct a formatted string containing all the required elements (metadata, turn-by-turn history with thoughts, and final summary).
    -   This complete string will be written to the markdown file.
    -   The `DebateCompleteEvent` model itself does not need to be changed. The required data is already available in the context where the event is handled.

---
