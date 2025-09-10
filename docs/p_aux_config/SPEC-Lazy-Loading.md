# P-AUX-CONFIG: Lazy Loading Refactoring Specification

## 1. Overview

This document specifies the refactoring of the `ConfigManager` to implement a lazy-loading pattern. This will make the configuration loading process transparent to the consumers of the configuration, increasing robustness and simplifying the calling code.

## 2. Current Behavior

- Consumers of `ConfigManager` must explicitly call `config_manager.load()` or `config_manager.load_if_not_loaded()` before calling `config_manager.get_config()`.
- Failure to do so results in a `ValueError`.
- This places the burden of initialization on every consumer.

## 3. Target Behavior

- The `ConfigManager.get_config()` method will be modified.
- When `get_config()` is called, it will internally check if the configuration has already been loaded.
- If the configuration is not loaded, `get_config()` will internally and automatically call the `load()` method.
- If the configuration is already loaded, `get_config()` will simply return the existing config object.
- The `load()` method will be made private (renamed to `_load()`) as it should no longer be called directly from outside the class.
- The `load_if_not_loaded()` method will be removed as it becomes redundant.

## 4. Impact

- All application code (e.g., in `cli.py`, `p7_gui/main.py`) that currently calls `load()` or `load_if_not_loaded()` must be refactored to remove these calls.
- The public API of the `ConfigManager` will be simplified to essentially one method: `get_config()`.
- The overall system becomes more robust as it's impossible to get a config without it being loaded first.
