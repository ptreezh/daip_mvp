# SPEC: Multi-Model Support for Wiki Collaboration

- **Version**: 1.0
- **Status**: Proposed
- **Applies to**: `wiki` command, `WikiManager`
- **Author**: TestCraft AI

---

## 1. Feature Goal

As a user, when multiple roles collaborate on editing or creating a Wiki page, I want each role to use its own specifically configured AI model, ensuring that contributions are stylistically and functionally distinct, similar to the `debate` feature.

## 2. Acceptance Criteria

1.  **Role-Specific Model Usage**: When a function involving a role's contribution to a wiki is called, the `WikiManager` must use the model specified in that role's configuration (`debate_model_config` or primary `model_configs`).
2.  **Clear Logging**: The system must generate a `ThoughtEvent` or a clear log message indicating which role is contributing and which model is being used for the generation (e.g., "Role 'researcher' is contributing to wiki page 'AI_History' using model 'gpt-4'.").
3.  **Default Model Fallback**: If a role has no specific model configuration, the system should fall back to the application's global default model without crashing.
4.  **No Regression**: Existing single-user wiki commands (e.g., `wiki list`, `wiki export`) should remain unaffected.

## 3. Technical Design & Approach

1.  **Dependency Injection**:
    -   The `WikiManager` class in `src/daip_live/wiki/manager.py` will be modified to accept `RoleModelManager` and `LiteLLMProvider` as dependencies in its `__init__` method.
    -   The instantiation of `WikiManager` in `tui.py` (within the `_handle_wiki_...` commands) will be updated to pass these dependencies.

2.  **Logic Modification**:
    -   Any method within `WikiManager` that orchestrates a role's contribution (e.g., a hypothetical `add_section_by_role(page_title: str, role_name: str, instruction: str)`) must be updated.
    -   Inside such methods, the `RoleModelManager` will be used to fetch the `RoleModelMapping` for the given `role_name`.
    -   The model configuration from the mapping will be used to get a specific `LiteLLMProvider` instance (or use the `OllamaInstanceManager` as seen in the `EnhancedDebateManager` for efficiency).
    -   This provider instance will be used to generate the text content for the wiki contribution.

3.  **Architectural Consistency**: The implementation should follow the pattern established by the `EnhancedDebateManager` to ensure architectural consistency across multi-agent features.

---
