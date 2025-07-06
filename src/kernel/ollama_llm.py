# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-05 17:30:00
@Author  : DAIP-LIVE Team
@File    : ollama_llm.py
@Description: Concrete implementation of LLMInterface for Ollama.
"""
import logging
from typing import Any, AsyncGenerator, Dict, List

import ollama

from src.kernel.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class OllamaLLM(LLMInterface):
    """A concrete implementation of the LLMInterface for Ollama models."""

    def __init__(
        self,
        generation_model: str = "llama3:instruct",
        embedding_model: str = "nomic-embed-text:latest",
        host: str = "http://localhost:11434",
    ):
        """Initializes the Ollama client with separate models for generation and embedding."""
        self.client = ollama.AsyncClient(host=host)
        self.generation_model = generation_model
        self.embedding_model = embedding_model
        logger.info(f"OllamaLLM initialized at host: {host}")
        logger.info(f"  - Generation Model: {self.generation_model}")
        logger.info(f"  - Embedding Model: {self.embedding_model}")

    async def generate(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Generates a response from the Ollama model."""
        try:
            response = await self.client.chat(model=self.generation_model, messages=messages, stream=False, **kwargs)
            return response["message"]
        except Exception as e:
            logger.error(f"Error generating response from Ollama: {e}")
            return {"role": "assistant", "content": f"Error: Could not get response from Ollama. {e}"}

    async def generate_stream(self, messages: List[Dict[str, Any]], **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Generates a streaming response from the Ollama model."""
        try:
            stream = await self.client.chat(model=self.generation_model, messages=messages, stream=True, **kwargs)
            async for chunk in stream:
                if "message" in chunk:
                    yield chunk["message"]
        except Exception as e:
            logger.error(f"Error generating streaming response from Ollama: {e}")
            yield {"role": "assistant", "content": f"Error: Ollama stream failed. {e}"}

    def get_embedding(self, text: str) -> List[float]:
        """Generates an embedding for a given text."""
        response = ollama.embeddings(model=self.embedding_model, prompt=text)
        return response["embedding"]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a list of texts."""
        # The ollama library processes them one by one, so we do the same.
        return [self.get_embedding(text) for text in texts]