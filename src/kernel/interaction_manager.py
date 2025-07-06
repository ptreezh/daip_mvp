# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : interaction_manager.py
@Description:
    Handles communication with a local LLM via Ollama.
"""
import logging

import ollama
from ollama import ResponseError

logger = logging.getLogger(__name__)


class InteractionManager:
    """Handles communication with a local LLM via Ollama."""

    def __init__(self, client: ollama.AsyncClient, model: str = "llama3:8b-instruct-q5_K_M"):
        """
        Initializes the InteractionManager.

        Args:
            client (ollama.AsyncClient): An instance of the Ollama async client.
            model (str): The name of the Ollama model to use.
        """
        self.model = model
        self.client = client

    async def get_response(self, role_id: str, context: str) -> str:
        """Gets a response from the configured LLM for a given role and context."""
        system_prompt = (
            f"You are an AI assistant playing the role of '{role_id}'. "
            "Your task is to provide a concise opinion based on the debate context. "
            "Do not add any preamble or explanation of your role. "
            "Directly state your opinion."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Debate Context:\n---\n{context}\n---\nYour Opinion:"},
        ]

        try:
            logger.info(f"Requesting response from model '{self.model}' for role '{role_id}'")
            response = await self.client.chat(model=self.model, messages=messages)
            return response.get("message", {}).get("content", "").strip()
        except ResponseError as e:
            logger.error(f"Ollama API error for model '{self.model}': {e.error}")
            return f"Error: Could not get a response for {role_id}. The model '{self.model}' may not be available. (Details: {e.error})"
        except Exception as e:
            logger.exception("An unexpected error occurred while communicating with Ollama.")
            return f"Error: An unexpected issue occurred while trying to contact the LLM for {role_id}."