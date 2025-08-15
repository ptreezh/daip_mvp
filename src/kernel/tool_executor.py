"""@Time    : 2025-07-24 11:00:00
@Author  : DAIP-LIVE Team
@File    : tool_executor.py
@Description:
    Executes tools, including consensus strategies.
    This acts as a bridge between the protocol layer and the specific
    tool/strategy implementations.
"""
import logging
from collections.abc import Callable
from typing import Any


class ToolExecutor:
    """A unified executor that registers and runs tools by name."""

    def __init__(self):
        """Initializes the ToolExecutor with an empty tool registry."""
        self.tools: dict[str, Callable] = {}
        self.tool_definitions: dict[str, dict] = {}
        logging.info("ToolExecutor initialized.")

    def register_tool(self, tool_func: Callable, definition: dict):
        """Registers a tool function and its JSON schema definition."""
        try:
            tool_name = definition["function"]["name"]
            self.tools[tool_name] = tool_func
            self.tool_definitions[tool_name] = definition
            logging.info(f"Successfully registered tool: '{tool_name}'")
        except KeyError:
            logging.exception(f"Failed to register tool. The definition is missing 'function' or 'name': {definition}")

    def execute(self, tool_name: str, **kwargs) -> dict[str, Any]:
        """Executes a named tool with the given keyword arguments."""
        if tool_name not in self.tools:
            logging.error(f"Execution failed: Tool '{tool_name}' is not registered.")
            return {"status": "error", "message": f"Tool '{tool_name}' not found."}

        try:
            logging.info(f"Executing tool '{tool_name}' with args: {kwargs}")
            tool_func = self.tools[tool_name]
            result = tool_func(**kwargs)
            return {"status": "success", "result": result}
        except Exception as e:
            logging.exception(f"Failed to execute tool '{tool_name}'")
            return {"status": "error", "message": str(e)}