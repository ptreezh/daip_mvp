# LLM Interface Design Document

## 1. Background

The current system's `InteractionManager` directly uses `ollama.AsyncClient` for chat completions but lacks a dedicated mechanism for generating text embeddings. This limitation prevents services like `RoleRecommenderService` from directly leveraging LLM-based embedding capabilities, leading to potential architectural inconsistencies and difficulties in extending LLM functionalities.

## 2. Goal

To create a unified and abstracted LLM interface that provides both chat completion and text embedding functionalities. This interface will centralize LLM interaction logic, separate concerns, and ensure consistent access to LLM capabilities across different services.

## 3. Design

### 3.1. `LLMInterface` Class Definition

A new class, `LLMInterface`, will be introduced in `src/kernel/llm_interface.py`.

```python
# src/kernel/llm_interface.py
import logging
from typing import List, Dict, Any

import ollama
from ollama import ResponseError

logger = logging.getLogger(__name__)

class LLMInterface:
    """
    A unified interface for interacting with Large Language Models (LLMs)
    via Ollama, providing both chat completion and text embedding functionalities.
    """

    def __init__(self, client: ollama.AsyncClient, model: str = "llama3:8b-instruct-q5_K_M"):
        """
        Initializes the LLMInterface.

        Args:
            client (ollama.AsyncClient): An instance of the Ollama async client.
            model (str): The name of the Ollama model to use for chat completions and embeddings.
        """
        self.client = client
        self.model = model
        logger.info(f"LLMInterface initialized with model: {self.model}")

    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Sends a list of messages to the LLM for chat completion and returns the response.

        Args:
            messages (List[Dict[str, str]]): A list of message dictionaries,
                                              e.g., [{"role": "user", "content": "Hello"}]

        Returns:
            str: The content of the LLM's response.
        """
        try:
            logger.debug(f"Sending chat request to model '{self.model}'")
            response = await self.client.chat(model=self.model, messages=messages)
            return response.get("message", {}).get("content", "").strip()
        except ResponseError as e:
            logger.error(f"Ollama API chat error for model '{self.model}': {e.error}")
            return f"Error: Could not get a chat response. Model '{self.model}' may not be available or accessible. (Details: {e.error})"
        except Exception as e:
            logger.exception("An unexpected error occurred during LLM chat interaction.")
            return f"Error: An unexpected issue occurred while trying to contact the LLM for chat: {e}"

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generates a single embedding vector for the given text.

        Args:
            text (str): The input text to embed.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        try:
            logger.debug(f"Generating embedding for text (first 50 chars): '{text[:50]}...'")
            response = await self.client.embeddings(model=self.model, prompt=text)
            return response.get("embedding", [])
        except ResponseError as e:
            logger.error(f"Ollama API embedding error for model '{self.model}': {e.error}")
            return [] # Return empty list on error
        except Exception as e:
            logger.exception("An unexpected error occurred during LLM embedding generation.")
            return [] # Return empty list on error

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embedding vectors for a list of texts.

        Args:
            texts (List[str]): A list of input texts to embed.

        Returns:
            List[List[float]]: A list of embedding vectors.
        """
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            if embedding: # Only add if embedding was successfully generated
                embeddings.append(embedding)
        return embeddings
```

### 3.2. Integration with Existing Components

*   **`src/kernel/core.py` (Kernel Class):**
    *   The `Kernel` class will be responsible for instantiating `LLMInterface`.
    *   It will pass the `ollama.AsyncClient` and model name to `LLMInterface`.
    *   `LLMInterface` instance will be exposed as `self.llm_interface`.
    *   `InteractionManager` will receive `self.llm_interface` during its initialization.

*   **`src/kernel/interaction_manager.py` (InteractionManager Class):**
    *   The `__init__` method will be updated to accept an `LLMInterface` instance instead of `ollama.AsyncClient`.
    *   The `get_response` method will be modified to use `self.llm_interface.chat()` for LLM interactions.

*   **`src/core_services/role_recommender_service.py` (RoleRecommenderService Class):**
    *   Its `__init__` method already expects an `llm_interface`. This will now be the `LLMInterface` instance from `Kernel`.
    *   Its `build_index` and `recommend_roles` methods will use `self.llm_interface.get_embedding()` and `self.llm_interface.get_embeddings()` respectively.

*   **`src/composition.py` (Composition Root):**
    *   The `create_application_dependencies` function will be updated to correctly wire up `LLMInterface`, `Kernel`, `InteractionManager`, and `RoleRecommenderService` according to the new dependency flow.

## 4. Error Handling Strategy

*   The `LLMInterface` methods (`chat`, `get_embedding`, `get_embeddings`) will include `try-except` blocks to catch `ollama.ResponseError` (for Ollama-specific API issues) and general `Exception` types.
*   In case of an error, appropriate logging will be performed, and a clear error message or an empty/default value (e.g., empty list for embeddings) will be returned to prevent cascading failures. This allows calling services to handle the absence of LLM output gracefully.

## 5. Benefits

*   **Abstraction:** Provides a clean, unified API for all LLM interactions, decoupling services from direct Ollama client dependencies.
*   **Reusability:** `LLMInterface` can be easily reused by any service requiring LLM chat or embedding capabilities.
*   **Maintainability:** Changes to LLM integration (e.g., switching to a different LLM provider) can be localized within `LLMInterface`.
*   **Testability:** Easier to mock and test LLM interactions in isolation.
*   **Extensibility:** Simplifies the addition of new LLM-related functionalities (e.g., fine-tuning, specific prompt engineering patterns).
