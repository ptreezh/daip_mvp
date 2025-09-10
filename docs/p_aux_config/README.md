# P-AUX-CONFIG: Configuration Management Specification

This document specifies the requirements, design, and implementation plan for a centralized configuration management system for the DAIP-LIVE project, following the Kiro Spec standard.

---

## 1. Requirements

### 1.1. User Stories

- **As a Developer**, I want to switch the language model (e.g., from a local Ollama model to GPT-4o) by changing a single text file, so that I can easily experiment and adapt to different environments without altering the source code.
- **As a Developer**, I want the application to fail fast with a clear error message if the configuration is invalid, so that I can quickly diagnose and fix setup issues.
- **As an Operator**, I want to define the location of the knowledge base directory and the database file, so that I can manage project data and structure according to my own needs.

### 1.2. Functional Requirements

- **FR1**: The system **MUST** load all external configurations from a single `config.yaml` file located at the project root.
- **FR2**: The system **MUST** validate the entire configuration at startup.
- **FR3**: The system **MUST** terminate with a descriptive error message if the configuration is missing or invalid.
- **FR4**: The configuration system **MUST** provide a simple, typed interface for other services to access configuration values.

---

## 2. Design

### 2.1. Guiding Principles

The implementation will adhere to the following principles:

- **TDD (Test-Driven Development)**: Development will begin with tests for each functional requirement (e.g., test_load_valid_config, test_load_invalid_config) before writing implementation code.
- **YAGNI (You Ain't Gonna Need It)**: The initial version will only implement the schema and loading mechanism defined below. Advanced features like environment variable overrides or dynamic reloading will not be added until explicitly required.
- **SOLID**:
  - **Single Responsibility**: A `ConfigManager` class will be solely responsible for loading, validating, and providing access to the configuration.
  - **Open/Closed**: The system will be open to extension (adding new configuration sections) but closed for modification (services consuming the config will not need to change if new, unrelated sections are added).
  - **Dependency Inversion**: High-level modules will depend on the `ConfigManager` abstraction, not directly on the `yaml` file or `Pydantic` models.

### 2.2. Configuration File Contract

-   **File Location**: `(project_root)/config.yaml`
-   **File Format**: YAML
-   **Schema Definition**: The Pydantic models defining this schema are located in `src/daip_live/core/models.py` (P0).

```yaml
# config.yaml

database:
  path: "daip_live.db"

llm_provider:
  default_model: "ollama/llama3"
  embedding_model: "all-MiniLM-L6-v2"

knowledge_base:
  directory: "docs/"
```

### 2.3. Loading and Validation

- A `ConfigManager` class will be implemented as a singleton.
- It will use the `PyYAML` library to load the file and `Pydantic` models (imported from P0) to parse and validate the data against the schema.

### 2.4. Access Pattern

- A global instance of the `ConfigManager` will be created upon application startup.
- Services will import this instance to access strongly-typed configuration objects.
  ```python
  # Example Usage in cli.py
  from .config import config_manager

  db_path = config_manager.database.path
  model = config_manager.llm_provider.default_model
  ```

---

## 3. Task List (Implementation Plan)

- [ ] **P-AUX-CONFIG-T1**: Create Pydantic models that mirror the `config.yaml` schema.
- [ ] **P-AUX-CONFIG-T2**: Create the `ConfigManager` class with a `load()` method.
- [ ] **P-AUX-CONFIG-T3**: Write a unit test to verify loading a valid `config.yaml` file.
- [ ] **P-AUX-CONFIG-T4**: Implement the loading and validation logic in `ConfigManager`.
- [ ] **P-AUX-CONFIG-T5**: Write unit tests for missing and invalid `config.yaml` files.
- [ ] **P-AUX-CONFIG-T6**: Implement the error handling for missing/invalid files.
- [ ] **P-AUX-CONFIG-T7**: Create the global `config_manager` instance.
- [ ] **P-AUX-CONFIG-T8**: Refactor `src/daip_live/cli.py` to remove hardcoded values and use the `config_manager`.
- [ ] **P-AUX-CONFIG-T9**: Verify that the existing integration test `tests/test_cli/test_run_command_integration.py` still passes after the refactoring.
- [ ] **P-AUX-CONFIG-T10**: Manually run the application to confirm it works with the new configuration system.
