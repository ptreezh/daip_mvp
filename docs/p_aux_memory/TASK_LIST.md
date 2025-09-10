# P-AUX-MEMORY: Multi-Agent Session Management Task List

This task list is aligned with the **Multi-Agent Session Management Specification**.

## Stage 1: Core Service Implementation (TDD)

- [ ] **Task 1.1 (MODEL)**: Define the `DialogueTurn` and the new `Session` Pydantic models in `src/daip_live/core/models.py` as per the new specification.
    - **Acceptance Criteria**: The models are defined correctly. `mypy` passes.

- [ ] **Task 1.2 (TEST-RED)**: Create `tests/memory/test_session_manager.py`. Add a test case `test_full_session_lifecycle` that attempts to use a (not-yet-implemented) `SessionManager` to:
    1. Create a 'debate' session with multiple participants.
    2. Add several `DialogueTurn` instances to it.
    3. End the session.
    4. Retrieve the session and verify its contents (participants, history, status).
    - **Acceptance Criteria**: The test file and the failing test case are committed.

- [ ] **Task 1.3 (SERVICE-GREEN)**: Create `src/daip_live/memory/session_manager.py`. Implement the `SessionManager` class with `create_session`, `add_dialogue_turn`, `end_session`, `get_session`, and `list_sessions` methods. Make the test from Task 1.2 pass.
    - **Acceptance Criteria**: The `test_full_session_lifecycle` test passes.

- [ ] **Task 1.4 (TEST-REFACTOR)**: Add tests for edge cases, such as listing sessions when none exist or getting a non-existent session.
    - **Acceptance Criteria**: Test coverage for `SessionManager` is comprehensive.

## Stage 2: CLI Integration

- [ ] **Task 2.1 (CLI-LIST)**: Implement the `daip session list` command in `src/daip_live/cli.py`.
    - **Acceptance Criteria**: The command lists all sessions without their history.

- [ ] **Task 2.2 (CLI-VIEW)**: Implement the `daip session view <session_id>` command in `src/daip_live/cli.py`.
    - **Acceptance Criteria**: The command displays the full session details, including the formatted dialogue history.

- [ ] **Task 2.3 (TEST-CLI)**: Add tests for both `list` and `view` session commands in `tests/test_cli/`.
    - **Acceptance Criteria**: The CLI commands' outputs are verified by test cases.

## Stage 3: Documentation & Logging

- [ ] **Task 3.1 (DOCS)**: Update the main `README.md` or relevant documents to reflect the new session management capabilities.

- [ ] **Task 3.2 (LOG)**: Update `log/WORK_LOG.md` to mark the completion of this work package.