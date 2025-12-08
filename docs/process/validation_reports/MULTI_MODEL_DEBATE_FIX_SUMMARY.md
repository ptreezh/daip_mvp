# Multi-Model Debate Fix Summary

## Problem
The multi-model debate functionality was failing with an AttributeError indicating that a dictionary object was missing the 'model_name' attribute. This occurred when the TUI tried to access model configuration information for debate participants.

## Root Cause
The error was in the TUI code in the `_start_debate` method. The code was incorrectly trying to access:
```python
mapping.model_config.model_name
```

However, `RoleModelMapping` objects have a `role_model_config` attribute (which is a `RoleModelConfig` object with a `model_name` attribute) and a `model_config` attribute (which is an internal Pydantic dictionary without a `model_name` attribute).

## Solution
Fixed the attribute access in `src/daip_live/tui.py` in the `_start_debate` method:

**Before (incorrect):**
```python
self._current_debate['role_models'][mapping.role_name] = mapping.model_config.model_name
self._debate_active_models[mapping.role_name] = mapping.model_config.model_name
```

**After (correct):**
```python
self._current_debate['role_models'][mapping.role_name] = mapping.role_model_config.model_name
self._debate_active_models[mapping.role_name] = mapping.role_model_config.model_name
```

## Verification
Created and ran tests to verify:
1. `RoleModelMapping` objects have the correct `role_model_config` attribute
2. `RoleModelMapping` objects have an internal `model_config` dictionary (but it's not what we want)
3. The correct attribute access works properly
4. The incorrect attribute access fails as expected

## Impact
This fix resolves the multi-model debate failure and allows users to:
- Run debates with different models assigned to different roles
- See proper model assignments in the TUI
- Have debates complete successfully without AttributeError crashes

The fix is minimal and targeted, changing only the incorrect attribute access while preserving all other functionality.