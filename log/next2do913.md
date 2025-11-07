# Next Steps - 2025-09-13

## Current Task: TUI Refactoring - Decoupling chat_run from /pa command

### Phase: TDD Implementation - Fixing Test Suite Rot

### Immediate Problem: Runtime AttributeError in TUI

**Description:**
When attempting to run `/role list` in the TUI, the application throws an `AttributeError: 'Provide' object has no attribute 'list_roles'`. This indicates a dependency injection issue where the TUI is trying to call methods directly on a `Provide` object instead of the actual service instance it provides.

**Context:**
- The `DAIP_TUI` class initializes `self.session_manager`, `self.role_manager`, and `self.knowledge_manager` using `Provide[...]`.
- The code then attempts to call methods like `list_roles` directly on these `Provide` objects (e.g., `self.role_manager.list_roles()`), which is incorrect.
- The correct way to access the service instance is by calling the `Provide` object (e.g., `self.role_manager()`).

**Proposed Fix:**
Modify `src/daip_live/tui.py` to change all direct accesses to `self.session_manager`, `self.role_manager`, and `self.knowledge_manager` to `self.session_manager()`, `self.role_manager()`, and `self.knowledge_manager()` respectively.

**Last Action Performed:**
Searched for `self.role_manager` in `src/daip_live/tui.py` to identify all usage points. The output of this search is pending.

**Next Action:**
Based on the search results, apply the fix to `src/daip_live/tui.py` by replacing `self.role_manager.` with `self.role_manager().` (and similarly for session_manager and knowledge_manager). Then, re-run the TUI to verify the fix.
