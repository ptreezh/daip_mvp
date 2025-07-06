# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : synthesis_engine.py
@Description:
    Implementation for the SynthesisEngine that uses an LLM to perform
    summarization and synthesis.
"""
import logging
from typing import List

import ollama
from ollama import ResponseError

from src.models import DebateTurn
from . import prompts

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """Uses an LLM to summarize and synthesize debate content."""

    def __init__(self, client: ollama.AsyncClient, model: str):
        """
        Initializes the SynthesisEngine.

        Args:
            client (ollama.AsyncClient): An instance of the Ollama async client.
            model (str): The name of the Ollama model to use for synthesis.
        """
        self.client = client
        self.model = model

    async def summarize_context(self, history: List[DebateTurn]) -> str:
        """Summarizes the debate history for context using an LLM."""
        if not history:
            return "The debate has just started."

        history_text = "\n".join(
            [f"Round {turn.round} - {turn.role_id}: {turn.opinion}" for turn in history]
        )

        messages = [
            {"role": "system", "content": prompts.SUMMARIZATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Debate History:\n---\n{history_text}\n---\nSummary:"},
        ]

        try:
            logger.info(f"Requesting context summary from model '{self.model}'")
            response = await self.client.chat(model=self.model, messages=messages)
            return response.get("message", {}).get("content", "").strip()
        except ResponseError as e:
            logger.error(f"Ollama API error during summarization: {e.error}")
            return f"Error: Could not summarize context. (Details: {e.error})"
        except Exception:
            logger.exception("An unexpected error occurred during context summarization.")
            return "Error: An unexpected issue occurred during summarization."

    async def synthesize_opinions(self, topic: str, history: List[DebateTurn]) -> str:
        """Synthesizes the final conclusion of the debate using an LLM."""
        if not history:
            return "No debate history available to synthesize."

        history_text = "\n".join(
            [f"Round {turn.round} - {turn.role_id}: {turn.opinion}" for turn in history]
        )

        messages = [
            {"role": "system", "content": prompts.SYNTHESIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Debate Topic: {topic}\n\nDebate History:\n---\n{history_text}\n---\nFinal Synthesized Conclusion:",
            },
        ]

        try:
            logger.info(f"Requesting final synthesis from model '{self.model}'")
            response = await self.client.chat(model=self.model, messages=messages)
            return response.get("message", {}).get("content", "").strip()
        except ResponseError as e:
            logger.error(f"Ollama API error during synthesis: {e.error}")
            return f"Error: Could not synthesize a conclusion. (Details: {e.error})"
        except Exception:
            logger.exception("An unexpected error occurred during opinion synthesis.")
            return "Error: An unexpected issue occurred during synthesis."