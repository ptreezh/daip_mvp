# -*- coding: utf-8 -*-
"""
@Time    : 2024-07-16 10:00:00
@Author  : DAIP-LIVE Team
@File    : tool_registry.py
@Description:
    Central registry for all tools available to the system.
    This module instantiates the ToolExecutor and registers all tool
    functions with their corresponding JSON Schema definitions.
"""

from src.kernel.tool_executor import ToolExecutor
from src.tools import kanban_tools

# --- Tool Definitions (JSON Schema for LLM Function Calling) ---

CREATE_TASK_DEF = {
    "type": "function",
    "function": {
        "name": "create_task",
        "description": "Creates a new task on the Kanban board.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "The title of the task."},
                "description": {
                    "type": "string",
                    "description": "A detailed description of the task.",
                },
                "status": {
                    "type": "string",
                    "description": "The initial status of the task (e.g., 'TODO', 'IN_PROGRESS', 'DONE').",
                },
            },
            "required": ["title", "description"],
        },
    },
}

LIST_TASKS_DEF = {
    "type": "function",
    "function": {
        "name": "list_tasks",
        "description": "Lists tasks from the Kanban board, optionally filtering by status.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "If provided, only tasks with this status will be listed.",
                }
            },
            "required": [],
        },
    },
}

UPDATE_TASK_DEF = {
    "type": "function",
    "function": {
        "name": "update_task",
        "description": "Updates the status or description of an existing task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "The ID of the task to update."},
                "new_status": {
                    "type": "string",
                    "description": "The new status to set for the task.",
                },
                "new_description": {
                    "type": "string",
                    "description": "The new description to set for the task.",
                },
            },
            "required": ["task_id"],
        },
    },
}


def _create_and_register_tools() -> ToolExecutor:
    """Creates a ToolExecutor instance and registers all available tools."""
    executor = ToolExecutor()
    executor.register_tool(kanban_tools.create_task, CREATE_TASK_DEF)
    executor.register_tool(kanban_tools.list_tasks, LIST_TASKS_DEF)
    executor.register_tool(kanban_tools.update_task, UPDATE_TASK_DEF)
    return executor


tool_executor_instance = _create_and_register_tools()