import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import tiktoken

# We assume these services exist and provide the required async methods.
from src.core_services.fact_extraction_service import FactExtractionService
from src.core_services.memory_service import MemoryService
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services.wiki_service import WikiService
from src.kernel.llm_interface import LLMInterface


class InteractionManager:
    """
    Manages the content and context of a conversation.

    This class is responsible for enriching the conversation history before it is
    sent to the LLM. Its duties include:
    - Retrieving relevant knowledge using RAG (Retrieval-Augmented Generation).
    - Managing long-term context via summarization.
    - Constructing the final message list for the LLM.
    This class replaces the context management responsibilities of the old `lim.py`.
    """

    def __init__(
        self,
        wiki_service: WikiService,
        memory_service: MemoryService,
        synthesis_engine: SynthesisEngine,
        llm_interface: LLMInterface,
        fact_extraction_service: Optional[FactExtractionService] = None,
        context_token_threshold: int = 4096,
    ):
        """
        Initializes the InteractionManager.

        Args:
            wiki_service: The service for retrieving knowledge from the wiki.
            memory_service: The service for persisting and retrieving summaries.
            synthesis_engine: The service for generating summaries from conversations.
            llm_interface: The interface for communicating with the language model.
            fact_extraction_service: (Optional) Service for extracting facts from text.
            context_token_threshold: The token limit before triggering summarization.
        """
        self.wiki_service = wiki_service
        self.memory_service = memory_service
        self.synthesis_engine = synthesis_engine
        self.llm_interface = llm_interface
        self.fact_extraction_service = fact_extraction_service
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.context_token_threshold = context_token_threshold
        logging.info(
            "InteractionManager (Context Engine) initialized with Wiki, Memory, and Synthesis services."
        )

    def _count_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Counts tokens in a list of messages, similar to lim.py."""
        total_tokens = 0
        for msg in messages:
            for key, value in msg.items():
                if value:
                    total_tokens += len(self.tokenizer.encode(json.dumps(value)))
        return total_tokens

    async def prepare_context(
        self, history: List[Dict[str, Any]], role_id: str, session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Prepares the full, context-rich message list for the LLM.

        This method implements RAG and long-term context management via summarization,
        migrating the core logic from `lim.py`.

        Args:
            history: The current conversation history for this turn.
            role_id: The ID of the role interacting with the user.
            session_id: The unique ID for the current conversation session.

        Returns:
            The complete list of messages to be sent to the LLM.
        """
        processed_history = list(history)

        # 1. Summarization: Check if context is too long and summarize if needed.
        token_count = self._count_tokens(processed_history)
        if token_count > self.context_token_threshold:
            logging.info(
                f"Context token count {token_count} exceeds threshold {self.context_token_threshold}. Summarizing..."
            )
            # We summarize all but the last message, which is the current user query.
            history_to_summarize = processed_history[:-1]
            if history_to_summarize:
                summary_text = await self.synthesis_engine.summarize_conversation(
                    history_to_summarize
                )
                # Save the summary for long-term recall
                await self.memory_service.save_summary(role_id, session_id, summary_text)
                logging.info("Conversation summarized and new summary saved.")
                # Replace the summarized part of the history with the summary itself
                processed_history = [{"role": "system", "content": f"Summary of prior conversation: {summary_text}"}, processed_history[-1]]

        # 2. Context Injection: Gather all context for the system prompt.
        user_query = ""
        if processed_history and processed_history[-1].get("role") == "user":
            user_query = processed_history[-1].get("content", "")

        # RAG from Wiki
        relevant_docs = []
        if user_query.strip():
            relevant_docs = await self.wiki_service.search_entries(user_query)
            logging.info(f"RAG retrieved {len(relevant_docs)} documents for the query.")

        # Get all historical summaries for long-term context
        all_summaries = await self.memory_service.get_all_summaries(role_id, session_id)

        # 3. Build the final system prompt.
        system_prompt = "You are a helpful AI assistant."
        if all_summaries:
            summaries_str = "\n".join(f"- {s}" for s in all_summaries)
            system_prompt += f"\n\nHere are summaries of past conversations (long-term memory):\n{summaries_str}"

        if relevant_docs:
            context_str = "\n".join(f"- {doc}" for doc in relevant_docs)
            system_prompt += f"\n\nHere is some relevant context from the wiki (retrieved knowledge):\n{context_str}"

        system_prompt += "\n\nPlease use all available context to inform your response."

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(processed_history)
        logging.info(
            f"Prepared context with {len(messages)} messages, including {len(relevant_docs)} RAG documents and {len(all_summaries)} summaries."
        )
        return messages

    async def get_response(self, role_id: str, user_input: str, session_id: str) -> str:
        """
        Orchestrates a full request-response cycle, including fact extraction.

        Args:
            role_id: The ID of the role interacting with the user.
            user_input: The text from the user.
            session_id: The unique ID for the current conversation session.

        Returns:
            The final response from the language model.
        """
        # A real implementation requires fetching history from MemoryService.
        # This assumes a method like `get_dialogue_history(session_id)` exists.
        try:
            current_history = await self.memory_service.get_dialogue_history(session_id)
        except Exception as e:
            logging.warning(f"Could not retrieve history for session {session_id}, starting new history. Error: {e}")
            current_history = []

        current_history.append({"role": "user", "content": user_input})

        # Step 1: Save user message and trigger background fact extraction.
        # Note: In a real system, you might await this or ensure it completes before the next step.
        user_message_id = await self.memory_service.add_memory(
            role_id=role_id,
            content=user_input,
            memory_type="dialogue",
            session_id=session_id,
            metadata={"sender": "user"},
        )

        if self.fact_extraction_service:
            user_metadata = {"message_id": user_message_id, "session_id": session_id, "author": "user"}
            asyncio.create_task(
                self.fact_extraction_service.extract_and_save_facts(
                    text=user_input, source_metadata=user_metadata
                )
            )

        # Step 2: Prepare context for the LLM.
        context_messages = await self.prepare_context(current_history, role_id, session_id)

        # Step 3: Get response from the language model.
        try:
            response_dict = await self.llm_interface.generate(context_messages)
            llm_response = response_dict.get("content", "Sorry, I could not generate a response.")
        except Exception as e:
            logging.error(f"Error getting response from LLM: {e}", exc_info=True)
            return "I'm sorry, but I encountered an error while trying to generate a response."

        # Step 4: Save AI response and trigger background fact extraction.
        ai_message_id = await self.memory_service.add_memory(
            role_id=role_id,
            content=llm_response,
            memory_type="dialogue",
            session_id=session_id,
            metadata={"sender": role_id},
        )
        if self.fact_extraction_service:
            ai_metadata = {"message_id": ai_message_id, "session_id": session_id, "author": role_id}
            asyncio.create_task(
                self.fact_extraction_service.extract_and_save_facts(
                    text=llm_response, source_metadata=ai_metadata
                )
            )

        return llm_response