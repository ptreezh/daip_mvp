# P4-Enhancement: Roles from Directory Task List

## Stage 1: Setup & TDD-RED

- [ ] **Task 1.1 (Create Test Directory)**: Create a `tests/p4_role_manager_tools/test_roles/` directory.
- [ ] **Task 1.2 (Create Test Role Files)**: Create individual role files inside the test directory (e.g., `pro.yaml`, `con_arguer.yaml`).
- [ ] **Task 1.3 (TEST-RED)**: Modify `tests/p4_role_manager_tools/test_role_manager.py`. Add a new test case, `test_load_roles_from_directory`, that initializes `RoleManager` with the path to the test directory and asserts that roles can be successfully retrieved. This test must fail initially.

## Stage 2: Implementation (GREEN)

- [ ] **Task 2.1 (Implement)**: Modify `src/daip_live/p4_role_manager_tools/role_manager.py`. 
    - Update the `__init__` method to accept a directory path.
    - Implement the logic to scan the directory, read each file, parse the YAML, and populate the internal roles dictionary.
    - Make the test from Task 1.3 pass.

## Stage 3: Refactoring & Edge Cases

- [ ] **Task 3.1 (TEST-REFACTOR)**: Add tests for error handling scenarios:
    - Test for behavior when the directory is missing.
    - Test for behavior when a file in the directory is malformed YAML.
    - Test for behavior when a file's data is invalid.
- [ ] **Task 3.2 (REFACTOR)**: Implement the error handling logic in `RoleManager` to make the new tests pass.

## Stage 4: Finalization

- [ ] **Task 4.1 (Cleanup)**: Create the default `roles/` directory and place the standard role files within it.
- [ ] **Task 4.2 (LOG)**: Update `log/WORK_LOG.md` to mark the completion of this enhancement.
