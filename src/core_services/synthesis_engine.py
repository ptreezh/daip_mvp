"""@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : synthesis_engine.py
@Description:
    Implementation for the SynthesisEngine that uses an LLM to perform
    summarization and synthesis.
"""
import logging

from src.kernel.llm_interface import LLMInterface
from src.models import DebateTurn

from . import prompts

logger = logging.getLogger(__name__)


class SynthesisEngine:
    """Uses an LLM to summarize and synthesize debate content."""

    def __init__(self, llm_interface: LLMInterface):
        """Initializes the SynthesisEngine.

        Args:
            llm_interface: An instance of a class that adheres to the LLMInterface.
        """
        self.llm_interface = llm_interface

    async def summarize_context(self, history: list[DebateTurn]) -> str:
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
            logger.info(f"Requesting context summary from model '{self.llm_interface.config.model}'")
            response = await self.llm_interface.generate(messages=messages, participant_id="synthesis_engine")
            
            # Log token usage if available
            if "token_usage" in response:
                token_info = response["token_usage"]
                logger.debug(f"Context summary token usage: {token_info['total_tokens']} tokens")
            
            return response.get("content", "").strip()
        except Exception as e:
            logger.exception("An unexpected error occurred during context summarization.")
            return f"Error: An unexpected issue occurred during summarization. Details: {e}"

    async def synthesize_opinions(self, topic: str, history: list[DebateTurn]) -> str:
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
            logger.info(f"Requesting final synthesis from model '{self.llm_interface.config.model}'")
            response = await self.llm_interface.generate(messages=messages, participant_id="synthesis_engine")
            
            # Log token usage if available
            if "token_usage" in response:
                token_info = response["token_usage"]
                logger.debug(f"Final synthesis token usage: {token_info['total_tokens']} tokens")
            
            return response.get("content", "").strip()
        except Exception as e:
            logger.exception("An unexpected error occurred during opinion synthesis.")
            return f"Error: An unexpected issue occurred during synthesis. Details: {e}"
