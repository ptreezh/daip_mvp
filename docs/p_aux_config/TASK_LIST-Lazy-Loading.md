# P-AUX-CONFIG: Lazy Loading Task List

## Stage 1: TDD

- [ ] **Task 1.1 (TEST-RED)**: Add a new test `test_get_config_lazy_loads` to `tests/test_config.py`. This test will instantiate `ConfigManager` and call `get_config()` directly, asserting that a valid config is returned without an explicit `load()` call. The test must initially fail.

- [ ] **Task 1.2 (GREEN)**: Modify `src/daip_live/config.py`:
    - Rename `load()` to `_load()`.
    - Modify `get_config()` to call `self._load()` if the config is not already loaded.
    - Remove the `load_if_not_loaded()` method.
    - Make the `test_get_config_lazy_loads` test pass.

## Stage 2: Refactoring

- [ ] **Task 2.1 (REFACTOR-TESTS)**: Update the existing tests in `tests/test_config.py` to remove the explicit `manager.load()` calls, relying on the new lazy-loading `get_config()` instead.

- [ ] **Task 2.2 (REFACTOR-CLI)**: Modify `src/daip_live/cli.py`. Remove the `config_manager.load()` call from the `callback()` function.

- [ ] **Task 2.3 (REFACTOR-GUI)**: Modify `src/daip_live/p7_gui/main.py`. Remove the `config_manager.load_if_not_loaded()` call from the `get_session_manager()` dependency.

## Stage 3: Verification

- [ ] **Task 3.1 (VERIFY)**: Run the entire project test suite (`poetry run pytest`) to ensure that the refactoring did not break any other part of the application.

- [ ] **Task 3.2 (LOG)**: Update `log/WORK_LOG.md` to mark the completion of this refactoring task.
