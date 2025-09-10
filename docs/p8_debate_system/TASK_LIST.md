# P8: Debate System Task List

This task list breaks down the implementation of the Debate System.

## Stage 1: Role Management Foundation (P4 Enhancement)

- [ ] **Task 1.1 (ROLE-MODEL)**: Verify that the `Role` model in `core/models.py` is sufficient. It should contain at least a `name` and a `persona` (prompt).
- [ ] **Task 1.2 (ROLE-MANAGER)**: Implement the `RoleManager` in `p4_role_manager_tools`. It needs a method `get_role_by_name(name: str) -> Role`. For now, this can be hardcoded to return a few sample roles (e.g., a "pro" arguer and a "con" arguer).
- [ ] **Task 1.3 (TEST-ROLE-MANAGER)**: Write tests for the `RoleManager` to ensure it correctly returns role objects.

## Stage 2: Debate Manager Implementation (TDD)

- [ ] **Task 2.1 (TEST-RED)**: Create `tests/p8_debate_system/test_debate_manager.py`. Write a failing test `test_debate_lifecycle` that mocks all dependencies (`SessionManager`, `RoleManager`, `ModelProvider`) and verifies that a full debate runs, creates a session, calls the model for each turn, and saves the final session with a summary.
- [ ] **Task 2.2 (DEBATE-MANAGER-GREEN)**: Create `src/daip_live/p8_debate_system/manager.py`. Implement the `DebateManager` class and its `run_debate` method to make the test from 2.1 pass.
- [ ] **Task 2.3 (TEST-REFACTOR)**: Add tests for edge cases, like invalid role names.

## Stage 3: CLI Integration

- [ ] **Task 3.1 (CLI)**: Add the `daip debate start` command to `cli.py`.
- [ ] **Task 3.2 (TEST-CLI)**: Write a test for the new CLI command.

## Stage 4: Documentation & Logging

- [ ] **Task 4.1 (DOCS)**: Update `README.md` with the new `debate` command.
- [ ] **Task 4.2 (LOG)**: Update `WORK_LOG.md` to mark the completion of this work package.
