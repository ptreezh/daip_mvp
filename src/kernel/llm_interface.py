"""
Defines a unified, pluggable interface for interacting with various Large Language Models (LLMs).

This module provides an abstract base class (LLMInterface) and concrete implementations
for different LLM providers (e.g., OpenAI, Ollama). A factory class (LLMFactory)
allows for easy instantiation of a specific LLM client based on a configuration object.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

import ollama
from openai import AsyncOpenAI
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """
    Configuration model for initializing an LLM interface.
    
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
    """Abstract Base Class for LLM interactions."""

    @abstractmethod
    def __init__(self, config: LLMConfig):
        """Initializes the LLM interface with a given configuration."""
        self.config = config

    @abstractmethod
    async def generate(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """Generates a single, non-streaming response from the LLM."""
        pass

    @abstractmethod
    async def generate_stream(self, messages: List[Dict[str, Any]], **kwargs: Any) -> AsyncIterator[str]:
        """Generates a response as a stream of text chunks."""
        pass


class OpenAIInterface(LLMInterface):
    """LLM Interface for OpenAI-compatible APIs."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(api_key=config.api_key, base_url=config.base_url)

    async def generate(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        completion = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=False,
            **kwargs,
        )
        # Return the response message as a dictionary, which may contain 'content' or 'tool_calls'
        response_message = completion.choices[0].message
        return response_message.model_dump(exclude_unset=True)

    async def generate_stream(self, messages: List[Dict[str, Any]], **kwargs: Any) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


class OllamaInterface(LLMInterface):
    """LLM Interface for Ollama."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # The 'ollama' library uses 'host' instead of 'base_url'
        self.client = ollama.AsyncClient(host=config.base_url)

    async def generate(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        response = await self.client.chat(
            model=self.config.model,
            messages=messages,
            stream=False,
            options={"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
            **kwargs,
        )
        return response["message"]

    async def generate_stream(self, messages: List[Dict[str, Any]], **kwargs: Any) -> AsyncIterator[str]:
        stream = await self.client.chat(
            model=self.config.model,
            messages=messages,
            stream=True,
            options={"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
            **kwargs,
        )
        async for chunk in stream:
            yield chunk["message"]["content"]


class LLMFactory:
    """Factory to create LLM interface instances based on configuration."""

    @staticmethod
    def create(config: LLMConfig) -> LLMInterface:
        """
        Creates and returns an LLMInterface instance.

        Args:
            config (LLMConfig): The configuration object.

        Returns:
            LLMInterface: An instance of a concrete LLM interface.

        Raises:
            ValueError: If the provider in the config is not supported.
        """
        provider = config.provider.lower()
        if provider == "openai":
            return OpenAIInterface(config)
        elif provider == "ollama":
            return OllamaInterface(config)
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")