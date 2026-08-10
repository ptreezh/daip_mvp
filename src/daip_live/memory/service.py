from __future__ import annotations

import os
from typing import TYPE_CHECKING

from daip_live.config_bridge import config_bridge
from daip_live.core.models import Session, TodoItem

if TYPE_CHECKING:  # 仅类型注解，避免模块级连带加载 litellm（CLI 冷启动优化 2026-08-10）
    from daip_live.model_provider.provider import LiteLLMProvider


class MemoryService:
    """A simple placeholder for the agent's memory service."""

    def __init__(self, model_provider: LiteLLMProvider):
        # Load the long term memory file path from the configuration
        config = config_bridge.get_config_data()
        db_path = config.get("database", {}).get("path", "daip_live.db")
        self.long_term_memory_file = os.path.join(
            os.path.dirname(db_path), "project_context.md"
        )
        self.model_provider = model_provider
        self.todo_list: list[TodoItem] = []

    def get_long_term_memory(self) -> str:
        """Gets the long term memory from a file."""
        if os.path.exists(self.long_term_memory_file):
            with open(self.long_term_memory_file, encoding="utf-8") as f:
                return f.read()
        return ""

    def add_todo_item(self, item: TodoItem) -> None:
        """Adds an item to the to-do list."""
        self.todo_list.append(item)

    async def get_todo_list(self) -> list[TodoItem]:
        """Returns a list of tasks to be completed."""
        return self.todo_list

    async def is_todo_list_complete(self) -> bool:
        """Checks if the to-do list is complete."""
        return all(item.status == "completed" for item in self.todo_list)

    async def update_todo_status(self, index: int, status: str = "completed") -> None:
        """Updates the status of a to-do item by its index."""
        if 0 <= index < len(self.todo_list):
            self.todo_list[index].status = status

    async def compress_history(self, session: Session) -> None:
        """
        Compresses the history using an LLM to create a structured summary,
        as per the requirements. Triggered at 80% token usage.
        """
        if len(session.history) <= 5:  # Lower threshold for 80% compression
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
"""  # noqa: E501

        # 3. Call the LLM to get the summary
        summary, _ = await self.model_provider.generate(prompt)

        # 4. Store the summary
        session.compressed_history = summary

    async def construct_prompt(
        self,
        goal: str,
        last_tool_result: str | None,
        last_llm_response: str | None,
        session: Session,
    ) -> str:
        """Constructs a simple prompt for the LLM."""
        if len(session.history) > 8:
            await self.compress_history(session)
        prompt = f"Goal: {goal}\n"
        long_term_memory = self.get_long_term_memory()
        if long_term_memory:
            prompt += f"Long term memory: {long_term_memory}\n"
        if last_tool_result:
            prompt += f"Last tool result: {last_tool_result}\n"
        if last_llm_response:
            prompt += f"Previous model response: {last_llm_response}\n"
        if session.compressed_history:
            prompt += f"Compressed history: {session.compressed_history}\n"
        config_data = config_bridge.get_config_data()
        rag_cfg = config_data.get("rag", {})
        if (
            rag_cfg.get("enabled", False)
            and hasattr(self, "knowledge_manager")
            and self.knowledge_manager
        ):
            top_k = rag_cfg.get("top_k", 5)
            results = await self.knowledge_manager.search(goal, top_k=top_k)
            if results:
                prompt += "RAG Snippets:\n"
                for r in results:
                    src = r.get("file_path", "")
                    prompt += f"- Source: {src}\n"
        if hasattr(self, "tool_manager") and getattr(self, "tool_manager", None):
            registry = getattr(self.tool_manager, "_registry", {})
            if registry:
                prompt += "Available Tools:\n"
                for name, fn in registry.items():
                    schema = getattr(fn, "input_schema", None)
                    keys = []
                    if schema and hasattr(schema, "model_fields"):
                        keys = list(schema.model_fields.keys())
                    prompt += f"- {name}({', '.join(keys)})\n"
        for turn in session.history[-10:]:
            prompt += f"{turn.participant_id}: {turn.content}\n"
        prompt += "Please analyze the situation and decide whether to use a tool or respond. Format for tool use: Use Tool: tool_name(arg1=value1, ...). Format for final answer: Final Answer. Confidence: X.X"  # noqa: E501
        return prompt
