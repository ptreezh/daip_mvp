# P_AUX_DEPENDENCY_INJECTION: Specification

**Status:** Proposed

## 1. Overview

This document specifies the design for a centralized dependency injection (DI) container to manage the lifecycle and wiring of services within the DAIP-LIVE application. This will replace the current manual instantiation of services, reducing boilerplate code, improving maintainability, and simplifying testing.

## 2. Chosen Library

We will use the `dependency-injector` Python library.

## 3. Container Design

The main container will be defined in `src/daip_live/container.py`.

### 3.1. Main Container (`Container`)

The `Container` class will be a `DeclarativeContainer` and will be the single entry point for accessing application services.

```python
# src/daip_live/container.py

from dependency_injector import containers, providers

from daip_live.config import ConfigManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.persistence.database import DatabaseManager
# ... other imports

class Container(containers.DeclarativeContainer):
    """Main application dependency injection container."""

    # 1. Configuration Provider
    # The config provider will load the main config.yaml and provide
    # access to its sections for other services.
    config = providers.Singleton(ConfigManager)

    # 2. Core Service Providers
    # These providers define how each service is created. Most will be Singletons
    # to ensure only one instance of each service exists per application lifecycle.

    db_manager = providers.Singleton(
        DatabaseManager,
        db_path=config.provided.get_config.return_value.database.path
    )

    model_provider = providers.Singleton(
        LiteLLMProvider,
        config=config.provided.get_config.return_value.llm_provider
    )

    knowledge_manager = providers.Singleton(
        KnowledgeManager,
        db_manager=db_manager,
        model_provider=model_provider,
        config=config.provided.get_config.return_value.knowledge_base.to_dict()
    )

    tool_manager = providers.Singleton(ToolManager)

    # ... other services like MemoryService, SessionManager, RoleManager, etc.

    # 3. Agent Executor
    # The AgentExecutor is a factory, as we might need multiple instances,
    # although it will often be used as a singleton in practice.
    agent_executor = providers.Factory(
        AgentExecutor,
        session_manager=session_manager, # Assuming session_manager is defined
        memory_service=memory_service,   # Assuming memory_service is defined
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        # user_input_queue will be passed at runtime
    )

```

### 3.2. Wiring Configuration

The `config` provider is a `Singleton` of `ConfigManager`. Other services access configuration values using the `config.provided` interface, which allows access to the methods and attributes of the `ConfigManager` instance. For example: `config.provided.get_config.return_value.database.path`.

## 4. Usage

### 4.1. Application Entry Point

In the application entry points (`main.py`, `tui.py`), the container will be created, and services will be resolved from it.

```python
# Example in a new tui.py runner

from daip_live.container import Container

def main():
    container = Container()
    container.config.load() # Assuming a load method
    container.wire(modules=[__name__])

    tui_app = container.tui_app() # Assuming tui_app is a provider
    tui_app.run()

if __name__ == "__main__":
    main()
```

### 4.2. Testing

In tests, the container can be used to override specific services with mocks. This is the primary benefit for testability.

```python
# Example in tests/test_some_feature.py

from unittest.mock import Mock
from daip_live.container import Container

def test_feature_with_mocked_llm():
    container = Container()

    # Override the model_provider with a mock
    mock_provider = Mock(spec=LiteLLMProvider)
    with container.model_provider.override(mock_provider):
        # Resolve a service that depends on the model provider
        some_service = container.some_service()

        # Run the test
        some_service.do_something_that_uses_llm()

        # Assert that the mock was called
        mock_provider.generate.assert_called_once()
```

## 5. Task List

1.  **Create SPEC:** Done.
2.  **Create failing test (`tests/core/test_container.py`):** Write a test that tries to import and use the container.
3.  **Implement Container:** Create `src/daip_live/container.py` and implement the `Container` class.
4.  **Integrate Container:** Refactor entry points and tests to use the new container.
