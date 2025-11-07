# Manual Testing Walkthrough

This document details the manual testing process for the DAIP-LIVE TUI.

## 1. Initial State & Command Discovery

*   **Action:** Start the TUI.
*   **Expected:** Welcome message is displayed.
*   **Result:** The welcome message is displayed correctly.

*   **Action:** Execute `/help`.
*   **Expected:** Help dialog appears with a list of all commands.
*   **Result:** The help dialog appeared with all commands listed.

## 2. Knowledge Base Interaction

*   **Action:** Execute `/knowledge sync`.
*   **Expected:** Sync process starts and completes, showing a summary.
*   **Result:** The sync process started and completed successfully, showing a summary of the changes.

*   **Action:** Execute `/knowledge search test`.
*   **Expected:** Search results are displayed.
*   **Result:** Search results were displayed correctly.

*   **Action:** Execute `/knowledge search nonexistentterm`.
*   **Expected:** "No results found" message is displayed.
*   **Result:** The "No results found" message was displayed correctly.

## 3. Role Management

*   **Action:** Execute `/role list`.
*   **Expected:** A list of available roles is displayed.
*   **Result:** A list of available roles was displayed correctly.

*   **Action:** Execute `/role view test_role`.
*   **Expected:** Details for the `test_role` are displayed.
*   **Result:** The details for the `test_role` were displayed correctly.

*   **Action:** Execute `/role view non_existent_role`.
*   **Expected:** "Role not found" message is displayed.
*   **Result:** The "Role not found" message was displayed correctly.

## 4. Session Management

*   **Action:** Execute `/session list`.
*   **Expected:** A list of sessions is displayed.
*   **Result:** A list of sessions was displayed correctly.

*   **Action:** Execute `/pa Test the personal assistant`.
*   **Expected:** A new session is created.
*   **Result:** A new session was created successfully.

*   **Action:** Execute `/session list` again.
*   **Expected:** The new session is listed.
*   **Result:** The new session was listed correctly.

*   **Action:** Execute `/session view <new_session_id>`.
*   **Expected:** Details for the new session are displayed.
*   **Result:** The details for the new session were displayed correctly.

## 5. Personal Assistant Interaction

*   **Action:** Send a message: `Hello`.
*   **Expected:** The agent responds.
*   **Result:** The agent responded correctly.

*   **Action:** Use a tool that requires permission.
*   **Expected:** Permission dialog appears.
*   **Result:** The permission dialog appeared correctly.

*   **Action:** Grant permission.
*   **Expected:** The tool executes successfully.
*   **Result:** The tool executed successfully.

*   **Action:** Use a tool that requires permission and deny it.
*   **Expected:** The tool does not execute.
*   **Result:** The tool did not execute.

## 6. UI Interaction

*   **Action:** Toggle focus between input and output panels.
*   **Expected:** The focus changes correctly.
*   **Result:** The focus changed correctly.

*   **Action:** Copy text from the output panel.
*   **Expected:** The text is copied to the clipboard.
*   **Result:** The text was copied to the clipboard correctly.
