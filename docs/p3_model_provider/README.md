---
id: P3
title: Model Provider Service
status: Ongoing
architecture_drivers: [SOLID, KISS, KDD, Adapter Pattern]
---

# P3: Model Provider Service

## 1. Overview

This work package (`P3`) acts as a standardized bridge to various Large Language Models (LLMs). It provides a unified `IModelProvider` interface, decoupling the rest of the application from the specifics of any single LLM backend. Its responsibility is to standardize and proxy all calls to LLMs.

To achieve this with maximum efficiency and model support, P3's implementation uses an **Adapter pattern**. It wraps the powerful `litellm` library, which provides a unified API for over 100 LLMs. This approach gives us broad model compatibility while maintaining a stable, consistent interface within our system.

## 2. Implementation Strategy & Specification

The public API of this package remains a factory function that returns a provider instance conforming to the `IModelProvider` interface. However, the internal implementation is now consolidated into a single, powerful adapter class.

-   **`LiteLLMProvider`**: A single class that implements the `IModelProvider` interface. It acts as an adapter, translating calls from our system into calls to the `litellm` library.
-   **`get_provider` Factory**: The factory is now simplified, its sole responsibility being to instantiate and return a configured `LiteLLMProvider`.

```python
# Models are imported from P0
from P0_Core_Interfaces_Types import IModelProvider, ProviderConfig, ModelError, ModelAuthenticationError
import litellm

class LiteLLMProvider(IModelProvider):
    """An adapter that uses the litellm library to fulfill the IModelProvider contract."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        try:
            # Responsibility: Translate config and call litellm
            params = self._build_litellm_params(prompt, **kwargs)
            response = litellm.completion(**params)
            return response.choices[0].message.content
        except litellm.exceptions.AuthenticationError as e:
            # Responsibility: Translate exceptions
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            raise ModelError(f"LiteLLM generic error: {e}") from e

    def _build_litellm_params(self, prompt: str, **kwargs) -> dict:
        # ... Logic to translate ProviderConfig into litellm parameters
        pass

def get_provider(config: ProviderConfig) -> IModelProvider:
    """Factory function that returns the singleton LiteLLMProvider instance."""
    return LiteLLMProvider(config)

```

## 3. Implementation Policies & Requirements

These are mandatory technical requirements for the `LiteLLMProvider` adapter.

-   **Configuration**: The provider **must** be initialized with a `ProviderConfig` object (defined in `P0`). This object is the sole source of configuration for the adapter.

-   **API Key Management**: The adapter is responsible for extracting the API key and passing it to `litellm`. The loading sequence **must** be:
    1.  Attempt to use the key from the `api_key` field in the `ProviderConfig` object.
    2.  If not present, `litellm`'s default behavior of reading from environment variables (e.g., `OPENAI_API_KEY`) will be used.
    3.  If no key is found, the adapter must catch the resulting `litellm.AuthenticationError` and re-raise it as a `P0.ModelAuthenticationError`.

-   **Unified Exception Handling**: The adapter **must** catch specific `litellm` exceptions (e.g., `litellm.RateLimitError`, `litellm.APIConnectionError`) and re-raise them as the appropriate, standardized `ModelError` subclass defined in `P0`. This maintains the stable error contract with the rest of the application.

-   **Request Retries**: The adapter **must** leverage `litellm`'s internal retry mechanism. It should configure `litellm`'s retry parameters (e.g., `num_retries`) based on values from the `ProviderConfig`. The adapter **must not** implement its own retry logic using libraries like `tenacity`.

-   **Parameter Mapping**: The adapter's primary responsibility is to map the standard parameters from `ProviderConfig` (e.g., `temperature`, `max_tokens`) and runtime arguments into the dictionary of parameters required by the `litellm.completion` function.

## 4. Test Plan Summary

-   **TDD Approach**: The `LiteLLMProvider` adapter must be developed via TDD.
-   **Dependency Mocking**: All external calls made by the `litellm` library **must** be mocked in unit tests. The primary target for mocking will be the `litellm.completion` function, using `pytest-mock`'s `mocker.patch`.

-   **Key Test Cases**:
    -   Verify the `get_provider` factory returns a `LiteLLMProvider` instance.
    -   Test the adapter's parameter mapping logic: ensure `ProviderConfig` values are correctly translated into the `params` dictionary for `litellm.completion`.
    -   Test the adapter's exception wrapping logic: for each relevant `litellm` exception, verify that the correct `P0.ModelError` subclass is raised.
    -   Test the API key handling logic.

    -   **Integration Tests**: A small suite of tests marked `@pytest.mark.integration` should be included to test the adapter against live APIs via `litellm`. These will be skipped in CI.
-   **Acceptance**: Test coverage >= 90%; passes `ruff` and `mypy --strict`.

## 5. Future Enhancements

### 5.1. LiteLLM Router Integration for Multi-LLM Management

**Objective**: To enable DAIP-LIVE to transparently manage and utilize multiple LLM instances (local and cloud) for dynamic model selection, load balancing, and failover, enhancing the agent's flexibility and robustness.

**Description**: This enhancement will involve integrating LiteLLM's Router capabilities into the `ModelProvider` service. Instead of configuring a single `default_model`, the system will be able to define a list of available models and their respective configurations. The Router will then intelligently route requests to the appropriate LLM based on predefined strategies (e.g., cost, latency, capability, or availability).

**Key Considerations**:
-   **Configuration**: Extend the `LLMProviderConfig` (in P0) to support a list of models and router-specific settings.
-   **Dynamic Selection**: Implement logic within the `ModelProvider` to leverage the LiteLLM Router for dynamic model selection based on task requirements or agent strategy.
-   **Error Handling & Fallback**: Utilize the Router's built-in failover mechanisms to ensure continuous operation even if a primary model becomes unavailable.
-   **Monitoring**: Explore integration with LiteLLM's monitoring features to track model usage, costs, and performance.



## 6. Implementation Status

-   **`LiteLLMProvider` Class**: The class structure is defined, and the constructor is implemented. It is integrated into the `cli.py` for application startup.
-   **`generate` Method**: The core logic for text generation is implemented.
-   **`embed` Method**: The core logic for text embedding is implemented.
-   **`_build_litellm_params` Method**: This method is currently a placeholder. The actual parameter mapping logic is pending implementation.
-   **API Key Management**: The API key management logic is pending implementation.
-   **Unified Exception Handling**: The unified exception handling is partially implemented.
-   **Request Retries**: The request retry mechanism is pending implementation.
-   **LiteLLM Router Integration**: This is a future enhancement and is not yet implemented.

