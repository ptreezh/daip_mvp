# TASK LIST: Debate Transcript Saving Enhancement

- **SPEC Document**: `IMPROVEMENT_SAVE_TRANSCRIPT_SPEC.md`
- **Overall Goal**: Enhance the debate report to include the full transcript and metadata, not just the summary.

---

### TDD-Driven Task Breakdown

-   [ ] **T01: [RED] Create a Failing Test for Transcript Saving**
    -   **Objective**: Write an integration test that verifies the full debate transcript is saved, not just the summary.
    -   **File**: Create a new test file, e.g., `tests/tui/test_debate_report_saving.py`.
    -   **Method**:
        1.  Set up a mock TUI environment with a `SessionManager` that holds a mock `Session` object containing a history of several `DialogueTurn`s.
        2.  Create a mock `DebateCompleteEvent`.
        3.  Call the `tui._save_debate_results(event)` method. This will create a file in a temporary directory.
        4.  Read the content of the saved file.
        5.  Assert that the file content contains the text from the mock `DialogueTurn`s.
    -   **Expected Result**: The test will fail because the current implementation only writes the summary to the file.

-   [ ] **T02: [GREEN] Modify Save Logic to Access Full History**
    -   **Objective**: Update the `_save_debate_results` method to access the complete debate history.
    -   **File**: `src/daip_live/tui.py`.
    -   **Method**:
        1.  Modify `_save_debate_results` to use the `event.session_id` to fetch the full `Session` object from `self._session_manager`.
        2.  Retrieve the `session.history` list, which contains all `DialogueTurn` objects.

-   [ ] **T03: [GREEN] Construct and Save the Full Report**
    -   **Objective**: Format the full transcript and save it to the report file.
    -   **File**: `src/daip_live/tui.py`.
    -   **Method**:
        1.  Inside `_save_debate_results`, create a list of strings for the report content.
        2.  Add formatted metadata (Topic, Roles, etc.) from the `session` object.
        3.  Iterate through `session.history` and append each turn's speaker and content to the list.
        4.  Append the final `session.summary`.
        5.  Join the list into a single string and write it to the file.

-   [ ] **T04: [GREEN] Verify the Fix**
    -   **Objective**: Ensure the test created in T01 now passes.
    -   **Method**: Run the test file `tests/tui/test_debate_report_saving.py`.
    -   **Expected Result**: The test should now pass, as the full transcript is being saved.

-   [ ] **T05: [REFACTOR] Code Cleanup**
    -   **Objective**: Review the modified code and tests for clarity and efficiency.
    -   **Method**:
        1.  Refactor `_save_debate_results` if needed to improve readability.
        2.  Ensure test code is clean and comments are relevant.
        3.  Remove any temporary debugging statements.

---