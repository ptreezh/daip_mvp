# P4-Enhancement: Roles from File Task List

## Stage 1: Setup & TDD-RED

- [ ] **Task 1.1 (Dependency)**: Add `PyYAML` to the project dependencies using `poetry add pyyaml`.
- [ ] **Task 1.2 (Create Test YAML)**: Create a sample `tests/p4_role_manager_tools/sample_roles.yaml` file for testing purposes.
- [ ] **Task 1.3 (TEST-RED)**: Modify `tests/p4_role_manager_tools/test_role_manager.py`. Add a new test case, `test_load_roles_from_file`, that initializes `RoleManager` with the path to the sample YAML file and asserts that a role from the file can be successfully retrieved. This test must fail initially because the file loading logic is not implemented.

## Stage 2: Implementation (GREEN)

- [ ] **Task 2.1 (Implement)**: Modify `src/daip_live/p4_role_manager_tools/role_manager.py`. 
    - Update the `__init__` method to accept a file path.
    - Implement the logic to read, parse, and validate the YAML file, populating the internal roles dictionary.
    - Make the test from Task 1.3 pass.

## Stage 3: Refactoring & Edge Cases

- [ ] **Task 3.1 (TEST-REFACTOR)**: Add tests for error handling scenarios:
    - Test for behavior when the YAML file is missing.
    - Test for behavior when the YAML file is malformed.
    - Test for behavior when the data in the YAML file does not match the `Role` schema.
- [ ] **Task 3.2 (REFACTOR)**: Implement the error handling logic in `RoleManager` to make the new tests pass.

## Stage 4: Finalization

- [ ] **Task 4.1 (Cleanup)**: Create a default `roles.yaml` in the project root directory with the standard roles.
- [ ] **Task 4.2 (LOG)**: Update `log/WORK_LOG.md` to mark the completion of this enhancement.
