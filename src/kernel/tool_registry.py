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
from src.protocols.consensus_strategies import SimpleMajorityVoteStrategy # Import the strategy

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

# --- Consensus Strategy Tool Definitions ---
SIMPLE_MAJORITY_VOTE_DEF = {
    "type": "function",
    "function": {
        "name": "simple_majority_vote",
        "description": "Determines consensus based on a simple majority vote from debate history.",
        "parameters": {
            "type": "object",
            "properties": {
                "history": {
                    "type": "array",
                    "items": {
                        "type": "object", # Assuming DebateTurn objects, but keeping it generic for schema
                        "properties": {
                            "role_id": {"type": "string"},
                            "opinion": {"type": "string"},
                            "round": {"type": "integer"},
                        }
                    },
                    "description": "The history of debate turns.",
                }
            },
            "required": ["history"],
        },
    },
}


def _create_and_register_tools() -> ToolExecutor:
    """Creates a ToolExecutor instance and registers all available tools."""
    executor = ToolExecutor()
    executor.register_tool(kanban_tools.create_task, CREATE_TASK_DEF)
    executor.register_tool(kanban_tools.list_tasks, LIST_TASKS_DEF)
    executor.register_tool(kanban_tools.update_task, UPDATE_TASK_DEF)
    
    # Register consensus strategy tools
    # Instantiate the strategy to register its instance method
    simple_majority_vote_instance = SimpleMajorityVoteStrategy()
    executor.register_tool(simple_majority_vote_instance.execute, SIMPLE_MAJORITY_VOTE_DEF) # Register the execute method of the instance
    
    return executor


tool_executor_instance = _create_and_register_tools()
