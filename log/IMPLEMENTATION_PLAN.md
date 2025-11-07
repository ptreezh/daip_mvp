# Refactoring Plan: Centralized Dependency Injection

**Date:** 2025-09-12

**Author:** Gemini

## 1. Problem Analysis

The current application exhibits significant technical debt related to dependency management:

*   **Manual Instantiation:** Services are manually created and passed through multiple constructor arguments. This is verbose, error-prone, and hard to maintain.
*   **Inconsistent Environments:** The TUI runner (`tui_runner.py`) is a development stub that uses mock objects and is out of sync with the proper application assembly shown in integration tests (`tests/test_tui_integration.py`). This creates confusion about the correct way to run the application.
*   **Difficult Mocking:** While tests use mocking, the manual setup is complex and varies between test files. Centralizing dependency management will simplify overriding services for testing.

## 2. Proposed Solution

I will refactor the application to use a centralized dependency injection (DI) container. This will provide a single source of truth for service instantiation and wiring.

**Chosen Library:** `dependency-injector` - It is a popular, mature, and feature-rich library for Python that integrates well with existing code.

## 3. TDD-based Refactoring Workflow

I will follow a strict Test-Driven Development process.

### Step 1: SPEC (Documentation First)

*   **Action:** Create a new specification document: `docs/specifications/P_AUX_DEPENDENCY_INJECTION.md`.
*   **Content:** This document will detail the design of the new DI container. It will define:
    *   The container structure.
    *   How configuration from `config.yaml` will be wired into the container.
    *   A list of all services that will be managed by the container.
    *   Examples of how to resolve services and override them for testing.

### Step 2: RED (Write a Failing Test)

*   **Action:** Create a new test file: `tests/core/test_container.py`.
*   **Content:** The test will attempt to:
    1.  Import a `Container` class from `src/daip_live/container.py`.
    2.  Instantiate the container.
    3.  Resolve a core service (e.g., `KnowledgeManager`) from the container.
    4.  Assert that the resolved service is a valid instance of the expected class.
*   **Expected Outcome:** The test will fail because `src/daip_live/container.py` and the `Container` class do not exist.

### Step 3: GREEN (Implement the Container)

*   **Action:**
    1.  Add `dependency-injector` to the `[tool.poetry.dependencies]` section of `pyproject.toml`.
    2.  Run `poetry install` to install the new dependency.
    3.  Create the `src/daip_live/container.py` file.
    4.  Implement the `Container` class using `dependency_injector.containers.DeclarativeContainer`.
    5.  Define providers for all core application services (e.g., `ConfigManager`, `DatabaseManager`, `LiteLLMProvider`, `ToolManager`, `KnowledgeManager`, etc.).
    6.  Wire the application configuration (`config.yaml`) into the container's providers.
*   **Expected Outcome:** The test created in the RED step will now pass.

### Step 4: REFACTOR (Integrate the Container)

*   **Action:**
    1.  Refactor the main CLI entry point (`main.py` or `src/daip_live/cli.py`) to use the `Container` to get the required services.
    2.  Delete the outdated `tui_runner.py` and create a new, clean entry point for the TUI that uses the `Container`.
    3.  Refactor the integration tests (starting with `tests/test_tui_integration.py`) to use the container for setting up the test environment. This will involve using the container's `override()` feature to inject mocks.
*   **Expected Outcome:** The application (CLI and TUI) will be fully functional, using the new DI container. The test suite will pass, demonstrating that the refactoring has not introduced regressions.

## 4. Next Step

I will now proceed with **Step 1: SPEC** by creating the specification document.