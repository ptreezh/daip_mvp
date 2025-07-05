"""Synthesizes multiple text inputs into a single, coherent summary."""

import logging
from typing import TYPE_CHECKING, Dict, List

from src.kernel.llm_interface import LLMInterface

if TYPE_CHECKING:
    from src.models import DebateTurn


class SynthesisEngine:
    """
    Synthesizes multiple opinions or text inputs into a single, coherent summary
    by leveraging a large language model.
    """

    def __init__(self, llm_interface: LLMInterface):
        """
        Initializes the SynthesisEngine.

        Args:
            llm_interface (LLMInterface): The interface to interact with the language model.
        """
        self.llm_interface = llm_interface
        logging.info("SynthesisEngine initialized with LLMInterface.")

    async def synthesize_opinions(self, topic: str, history: List["DebateTurn"]) -> str:
        """
        Takes a list of debate turns and a topic, then generates a synthesized summary.

        Args:
            topic (str): The central topic of the opinions.
            history (List[DebateTurn]): A list of debate turns, each representing an opinion.

        Returns:
            str: A synthesized text that summarizes and integrates the opinions.
        """
        if not history:
            logging.warning("synthesize_opinions called with no history.")
            return "No opinions were provided to synthesize."

        logging.info(f"Synthesizing {len(history)} opinions on the topic: '{topic}'.")

        prompt = self._build_synthesis_prompt(topic, history)

        try:
            response = await self.llm_interface.generate(
                messages=[{"role": "user", "content": prompt}]
            )
            synthesized_text = response.get("content", "Failed to generate synthesis from LLM response.")
            logging.info("Successfully synthesized opinions.")
            return synthesized_text
        except Exception as e:
            logging.error(f"An error occurred during LLM call for synthesis: {e}", exc_info=True)
            return f"Error: Could not generate synthesis due to an internal error. Details: {e}"

    def _build_synthesis_prompt(self, topic: str, history: List["DebateTurn"]) -> str:
        """Builds a detailed prompt for the LLM to synthesize opinions."""
        prompt_parts = [
            f"You are an expert synthesizer. Your task is to analyze the following debate history on the topic of '{topic}' and produce a coherent, neutral, and comprehensive summary.",
            "The summary should identify common ground, highlight key disagreements, and present the overall spectrum of views without taking a side. Do not invent information. Base your synthesis strictly on the provided text.",
            "\n--- Debate History to Synthesize ---\n",
        ]

        for turn in history:
            prompt_parts.append(f'Opinion from Role "{turn.role_id}" (Round {turn.round}):\n"""\n{turn.opinion}\n"""\n')

        prompt_parts.append("\n--- Synthesis Task ---\nPlease provide your synthesized summary below.")
        return "\n".join(prompt_parts)

    async def summarize_conversation(self, history: List[Dict[str, str]]) -> str:
        """
        Takes a conversation history and generates a concise summary.

        Args:
            history (List[Dict[str, str]]): A list of message dictionaries,
                                            e.g., [{"role": "user", "content": "..."}].

        Returns:
            str: A concise summary of the conversation.
        """
        if not history:
            logging.warning("summarize_conversation called with no history.")
            return "No conversation history was provided to summarize."

        logging.info(f"Summarizing a conversation with {len(history)} turns.")

        prompt_parts = [
            "You are a summarization expert. Your task is to create a concise summary of the following conversation history.",
            "The summary should capture the key points, decisions, and unanswered questions. It will be used as long-term memory for a continuing conversation.",
            "\n--- Conversation to Summarize ---\n",
        ]
        for turn in history:
            prompt_parts.append(f"{turn.get('role', 'participant')}: {turn.get('content', '')}")

        prompt_parts.append("\n--- Summary Task ---\nPlease provide your concise summary below.")
        prompt = "\n".join(prompt_parts)

        try:
            response = await self.llm_interface.generate(messages=[{"role": "user", "content": prompt}])
            return response.get("content", "Failed to generate summary from LLM response.")
        except Exception as e:
            logging.error(f"An error occurred during LLM call for summarization: {e}", exc_info=True)
            return f"Error: Could not generate summary due to an internal error. Details: {e}"