import os
from typing import Optional
from src.daip_live.core.models import Session, AppConfig
from src.daip_live.config import config_manager

class MemoryService:
    """A simple placeholder for the agent's memory service."""
    
    def __init__(self):
        # Load the long term memory file path from the configuration
        config = config_manager.get_config()
        self.long_term_memory_file = os.path.join(os.path.dirname(config.database.path), "project_context.md")

    def get_long_term_memory(self) -> str:
        """Gets the long term memory from a file."""
        if os.path.exists(self.long_term_memory_file):
            with open(self.long_term_memory_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    async def get_todo_list(self):
        """Returns a list of tasks to be completed."""
        return []

    async def is_todo_list_complete(self) -> bool:
        """Checks if the to-do list is complete."""
        return True
        
    def compress_history(self, session: Session) -> None:
        """Compresses the history if it is too long."""
        # For now, we'll just take the first 5 and last 5 turns and concatenate them
        # In a real implementation, this would call an LLM to summarize the history
        if len(session.history) > 10:
            compressed = "Summary of conversation:\n"
            for turn in session.history[:5]:
                compressed += f"{turn.participant_id}: {turn.content}\n"
            compressed += "...\n"
            for turn in session.history[-5:]:
                compressed += f"{turn.participant_id}: {turn.content}\n"
            session.compressed_history = compressed
            # In a real implementation, we might want to truncate the history
            # session.history = session.history[-5:]

    def construct_prompt(
        self, 
        goal: str,
        last_tool_result: Optional[str],
        last_llm_response: Optional[str],
        session: Session,
    ) -> str:
        """Constructs a simple prompt for the LLM."""
        # Compress history if it is too long
        if len(session.history) > 15:  # Threshold for compression
            self.compress_history(session)
            
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
