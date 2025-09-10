import os
from typing import List, Optional

from src.daip_live.config import config_manager
from src.daip_live.core.models import Session, TodoItem
from src.daip_live.model_provider.provider import LiteLLMProvider


class MemoryService:
    """A simple placeholder for the agent's memory service."""

    def __init__(self, model_provider: LiteLLMProvider):
        # Load the long term memory file path from the configuration
        config = config_manager.get_config()
        self.long_term_memory_file = os.path.join(os.path.dirname(config.database.path), "project_context.md")
        self.model_provider = model_provider
        self.todo_list: List[TodoItem] = []

    def get_long_term_memory(self) -> str:
        """Gets the long term memory from a file."""
        if os.path.exists(self.long_term_memory_file):
            with open(self.long_term_memory_file, encoding="utf-8") as f:
                return f.read()
        return ""

    def add_todo_item(self, item: TodoItem) -> None:
        """Adds an item to the to-do list."""
        self.todo_list.append(item)

    async def get_todo_list(self) -> List[TodoItem]:
        """Returns a list of tasks to be completed."""
        return self.todo_list

    async def is_todo_list_complete(self) -> bool:
        """Checks if the to-do list is complete."""
        return all(item.status == "completed" for item in self.todo_list)

    async def compress_history(self, session: Session) -> None:
        """
        Compresses the history using an LLM to create a structured summary,
        as per the requirements.
        """
        if len(session.history) <= 10:  # Only compress if history is sufficiently long
            return

        # 1. Format dialogue history into a string
        history_string = "\n".join(
            f"{turn.participant_id}: {turn.content}" for turn in session.history
        )

        # 2. Create the summarization prompt
        prompt = f"""You are a summarization expert. Condense the following dialogue history into a structured summary covering these 8 aspects:
1.  **Background Context**: What was the initial situation or problem?
2.  **Key Decisions**: What were the most important decisions made?
3.  **User Intent Evolution**: How did the user's goal change over time?
4.  **Key Information**: What are the most critical pieces of information or data mentioned?
5.  **Agent's Actions**: What were the main actions or tools used by the assistant?
6.  **Unresolved Questions**: What questions remain unanswered?
7.  **Next Steps**: What are the implied or stated next actions?
8.  **Final Goal**: What is the user's ultimate objective in this conversation?

Dialogue History:
---
{history_string}
---
Structured Summary:
"""

        # 3. Call the LLM to get the summary
        summary, _ = await self.model_provider.generate(prompt)

        # 4. Store the summary
        session.compressed_history = summary

    async def construct_prompt(
        self,
        goal: str,
        last_tool_result: Optional[str],
        last_llm_response: Optional[str],
        session: Session,
    ) -> str:
        """Constructs a simple prompt for the LLM."""
        # Compress history if it is too long
        if len(session.history) > 15:  # Threshold for compression
            await self.compress_history(session)

        prompt = f"Goal: {goal}\n"

        # Add long term memory
        long_term_memory = self.get_long_term_memory()
        if long_term_memory:
            prompt += f"Long term memory: {long_term_memory}\n"

        if last_tool_result:
            prompt += f"Last tool result: {last_tool_result}\n"
        if last_llm_response:
            prompt += f"Previous model response: {last_llm_response}\n"

        # Add compressed history if available
        if session.compressed_history:
            prompt += f"Compressed history: {session.compressed_history}\n"

        # Add recent dialogue history
        for turn in session.history[-10:]:  # Last 10 turns
            prompt += f"{turn.participant_id}: {turn.content}\n"

        prompt += "Please analyze the situation and decide whether to use a tool or respond. Format for tool use: Use Tool: tool_name(arg1=value1, ...). Format for final answer: Final Answer. Confidence: X.X"
        return prompt
