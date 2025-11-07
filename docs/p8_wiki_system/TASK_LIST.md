# TASK LIST: Multi-Model Support for Wiki Collaboration

- **SPEC Document**: `SPEC.md`
- **Overall Goal**: Integrate `RoleModelManager` with `WikiManager` to enable per-role model usage in collaborative wiki tasks.

---

### TDD-Driven Task Breakdown

-   [ ] **T01: [INVESTIGATION] Analyze Current `WikiManager` Implementation**
    -   **Objective**: Understand the existing structure of `WikiManager` and its usage in `tui.py`.
    -   **Method**:
        1.  Read the source code of `src/daip_live/wiki/manager.py`.
        2.  Identify methods that would be used for multi-role collaboration (e.g., creating or editing pages/sections).
        3.  Identify how `WikiManager` is currently instantiated within `tui.py`'s `_handle_wiki_...` commands.

-   [ ] **T02: [RED] Create a Failing Test for Collaborative Model Usage**
    -   **Objective**: Write a test to prove that the current implementation uses the same model for all roles in a collaborative task.
    -   **File**: Create `tests/wiki/test_wiki_collaboration.py`.
    -   **Method**:
        1.  Set up a test with a mock `LiteLLMProvider`.
        2.  Instantiate `WikiManager` as it is currently used.
        3.  Simulate a collaborative action, e.g., `wiki_manager.add_content_by_role('page_title', 'role_A', 'instruction_A')` followed by `...('page_title', 'role_B', 'instruction_B')`.
        4.  Assert that the mock `LiteLLMProvider.generate` method was called with the same model for both calls. This test will initially pass but serves as a baseline.
        5.  Modify the assertion to expect *different* models (as per role configs). The test will now fail, representing our RED state.

-   [ ] **T03: [GREEN] Refactor `WikiManager` for Dependency Injection**
    -   **Objective**: Modify `WikiManager` to accept necessary dependencies.
    -   **File**: `src/daip_live/wiki/manager.py` and `src/daip_live/tui.py`.
    -   **Method**:
        1.  Update `WikiManager.__init__` to accept `role_model_manager: RoleModelManager` and `model_provider: LiteLLMProvider`.
        2.  Update the instantiation of `WikiManager` inside the relevant `_handle_wiki_...` command(s) in `tui.py` to pass the TUI's existing instances of these managers.

-   [ ] **T04: [GREEN] Implement Role-Specific Model Logic**
    -   **Objective**: Use the injected managers to select the correct model per role.
    -   **File**: `src/daip_live/wiki/manager.py`.
    -   **Method**:
        1.  In the collaborative method (e.g., `add_content_by_role`), use `self.role_model_manager` to get the `RoleModelMapping` for the specified `role_name`.
        2.  Use the `model_config` from the mapping to call `self.model_provider.generate` with the correct `model` parameter.

-   [ ] **T05: [GREEN] Verify the Fix**
    -   **Objective**: Ensure the test created in T02 now passes.
    -   **Method**: Run `pytest tests/wiki/test_wiki_collaboration.py`.
    -   **Expected Result**: The test should now pass, as the mock provider will be called with different models for `role_A` and `role_B`.

-   [ ] **T06: [REFACTOR] Code Cleanup**
    -   **Objective**: Review the modified code for clarity and adherence to project standards.
    -   **Method**: Refactor `WikiManager` and the test code as needed. Ensure logging is clear.

---
