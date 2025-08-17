"""Defines a unified, pluggable interface for interacting with various Large Language Models (LLMs).

This module provides an abstract base class (LLMInterface) and concrete implementations
for different LLM providers (e.g., OpenAI, Ollama). A factory class (LLMFactory)
allows for easy instantiation of a specific LLM client based on a configuration object.

The interface now includes token management capabilities for cost tracking and context optimization.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import ollama
from openai import AsyncOpenAI
from pydantic import BaseModel

if TYPE_CHECKING:
    from src.core_services.token_management_service import TokenManagementService


class LLMConfig(BaseModel):
    """Configuration model for initializing an LLM interface.
    
    Attributes:
        provider (str): The LLM provider, e.g., "openai", "ollama".
        model (str): The specific model name to use.
        api_key (Optional[str]): The API key for cloud-based services.
        base_url (Optional[str]): The base URL for the API endpoint.
        temperature (float): The sampling temperature.
        max_tokens (int): The maximum number of tokens to generate.

    """

    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048


class LLMInterface(ABC):
    """Abstract Base Class for LLM interactions with token management."""

    @abstractmethod
    def __init__(self, config: LLMConfig, token_service: Optional['TokenManagementService'] = None):
        """Initializes the LLM interface with a given configuration and optional token service."""
        self.config = config
        self.token_service = token_service

    @abstractmethod
    async def generate(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        """Generates a single, non-streaming response from the LLM.
        
        Args:
            messages: List of message dictionaries
            participant_id: Optional identifier for token tracking
            **kwargs: Additional arguments for the LLM
            
        Returns:
            Dictionary containing the response and token usage information

        """
        pass

    @abstractmethod
    async def generate_stream(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> AsyncIterator[str]:
        """Generates a response as a stream of text chunks.
        
        Args:
            messages: List of message dictionaries
            participant_id: Optional identifier for token tracking
            **kwargs: Additional arguments for the LLM
            
        Yields:
            String chunks of the response

        """
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]:
        """Generates a single embedding vector for the given text."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a list of texts."""
        pass


class OpenAIInterface(LLMInterface):
    """LLM Interface for OpenAI-compatible APIs with token management."""

    def __init__(self, config: LLMConfig, token_service: Optional['TokenManagementService'] = None):
        super().__init__(config, token_service)
        self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)

    async def generate(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        # Optimize context if token service is available
        if self.token_service:
            context_window = self.token_service.prepare_context_for_llm(messages, self.config.model, participant_id)
            optimized_messages = context_window.messages
        else:
            optimized_messages = messages

        completion = await self.client.chat.completions.create(
            model=self.config.model,
            messages=optimized_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=False,
            **kwargs,
        )

        # Extract response and token usage
        response_message = completion.choices[0].message
        usage = completion.usage

        # Record token usage if service is available
        if self.token_service and usage:
            self.token_service.record_usage(
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                model=self.config.model,
                participant_id=participant_id
            )

        # Return response with token information
        result = response_message.model_dump(exclude_unset=True)
        if usage:
            result["token_usage"] = {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }

        return result

    async def generate_stream(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> AsyncIterator[str]:
        # Optimize context if token service is available
        if self.token_service:
            context_window = self.token_service.prepare_context_for_llm(messages, self.config.model, participant_id)
            optimized_messages = context_window.messages
        else:
            optimized_messages = messages

        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=optimized_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
            **kwargs,
        )

        # Track tokens for streaming (approximate)
        output_tokens = 0
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                if self.token_service:
                    output_tokens += self.token_service.count_tokens(content, self.config.model)
                yield content

        # Record approximate usage for streaming
        if self.token_service:
            input_tokens = self.token_service.count_messages_tokens(optimized_messages, self.config.model)
            self.token_service.record_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.config.model,
                participant_id=participant_id
            )

    async def get_embedding(self, text: str) -> list[float]:
        """Generates a single embedding vector for the given text."""
        # Note: OpenAI's API can take a list, but we expose a single-text method for interface consistency.
        response = await self.client.embeddings.create(model=self.config.model, input=[text])
        return response.data[0].embedding

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a list of texts."""
        if not texts:
            return []
        response = await self.client.embeddings.create(model=self.config.model, input=texts)
        return [item.embedding for item in response.data]


class OllamaInterface(LLMInterface):
    """LLM Interface for Ollama with token management."""

    def __init__(self, config: LLMConfig, token_service: Optional['TokenManagementService'] = None):
        super().__init__(config, token_service)
        # The 'ollama' library uses 'host' instead of 'base_url'
        self.client = ollama.AsyncClient(host=config.base_url)

    async def generate(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        # Optimize context if token service is available
        if self.token_service:
            context_window = self.token_service.prepare_context_for_llm(messages, self.config.model, participant_id)
            optimized_messages = context_window.messages
        else:
            optimized_messages = messages

        response = await self.client.chat(
            model=self.config.model,
            messages=optimized_messages,
            stream=False,
            options={"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
            **kwargs,
        )

        # Calculate token usage if service is available
        if self.token_service:
            input_tokens = self.token_service.count_messages_tokens(optimized_messages, self.config.model)
            output_tokens = self.token_service.count_tokens(response["message"]["content"], self.config.model)

            self.token_service.record_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.config.model,
                participant_id=participant_id
            )

            # Add token usage to response
            response["token_usage"] = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            }

        return response["message"]

    async def generate_stream(self, messages: list[dict[str, Any]], participant_id: Optional[str] = None, **kwargs: Any) -> AsyncIterator[str]:
        # Optimize context if token service is available
        if self.token_service:
            context_window = self.token_service.prepare_context_for_llm(messages, self.config.model, participant_id)
            optimized_messages = context_window.messages
        else:
            optimized_messages = messages

        stream = await self.client.chat(
            model=self.config.model,
            messages=optimized_messages,
            stream=True,
            options={"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
            **kwargs,
        )

        # Track tokens for streaming
        output_tokens = 0
        async for chunk in stream:
            content = chunk["message"]["content"]
            if self.token_service:
                output_tokens += self.token_service.count_tokens(content, self.config.model)
            yield content

        # Record usage for streaming
        if self.token_service:
            input_tokens = self.token_service.count_messages_tokens(optimized_messages, self.config.model)
            self.token_service.record_usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.config.model,
                participant_id=participant_id
            )

    async def get_embedding(self, text: str) -> list[float]:
        """Generates a single embedding vector for the given text."""
        try:
            response = await self.client.embeddings(model=self.config.model, prompt=text)
            return response.get("embedding", [])
        except Exception as e:
            logging.error(f"Ollama embedding error for model '{self.config.model}': {e}")
            return []

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generates embedding vectors for a list of texts."""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            if embedding:
                embeddings.append(embedding)
        return embeddings


class LLMFactory:
    """Factory to create LLM interface instances based on configuration."""

    @staticmethod
    def create(config: LLMConfig, token_service: Optional['TokenManagementService'] = None) -> LLMInterface:
        """Creates and returns an LLMInterface instance.

        Args:
            config (LLMConfig): The configuration object.
            token_service: Optional token management service for usage tracking

        Returns:
            LLMInterface: An instance of a concrete LLM interface.

        Raises:
            ValueError: If the provider in the config is not supported.

        """
        provider = config.provider.lower()
        if provider == "openai":
            return OpenAIInterface(config, token_service)
        elif provider == "ollama":
            return OllamaInterface(config, token_service)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")
