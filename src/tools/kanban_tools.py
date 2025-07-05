import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

# Define a path for the Kanban board data file
DATA_DIR = Path("data")
BOARD_FILE = DATA_DIR / "kanban_board.json"


class KanbanToolError(Exception):
    """Custom exception for Kanban tool errors."""
    pass


def _load_board() -> Dict[str, Any]:
    """Loads the Kanban board from the JSON file."""
    # Let exceptions like FileNotFoundError, json.JSONDecodeError, and IOError
    # propagate to the caller for more specific handling.
    if not BOARD_FILE.exists():
        # This is a normal condition for the first run.
        return {"tasks": {}}
    with BOARD_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_board(board: Dict[str, Any]) -> None:
    """Saves the Kanban board to the JSON file."""
    # Implement atomic write to prevent data corruption.
    DATA_DIR.mkdir(exist_ok=True)
    temp_file = BOARD_FILE.with_suffix(".json.tmp")
    with temp_file.open("w", encoding="utf-8") as f:
        json.dump(board, f, indent=4, ensure_ascii=False)
    # This is an atomic operation on most OSes.
    os.rename(temp_file, BOARD_FILE)


def create_task(title: str, description: str, status: str = "TODO") -> str:
    """
    Creates a new task on the Kanban board.

    Args:
        title: The title of the task.
        description: A detailed description of the task.
        status: The initial status of the task (e.g., 'TODO', 'IN_PROGRESS', 'DONE').

    Returns:
        A confirmation message with the new task's ID.
    """
    try:
        board = _load_board()
        task_id = str(uuid.uuid4())[:8]
        if "tasks" not in board:
            board["tasks"] = {}
        board["tasks"][task_id] = {
            "title": title,
            "description": description,
            "status": status,
        }
        _save_board(board)
        logging.info(f"Created new task {task_id}: {title}")
        return f"Successfully created task with ID: {task_id}"
    except (IOError, json.JSONDecodeError) as e:
        error_msg = f"Failed to create task due to a storage error: {e}"
        logging.error(error_msg)
        raise KanbanToolError(error_msg) from e


def list_tasks(status: Optional[str] = None) -> str:
    """
    Lists tasks from the Kanban board, optionally filtering by status.

    Args:
        status: If provided, only tasks with this status will be listed.

    Returns:
        A formatted string of tasks or a message if no tasks are found.
    """
    try:
        board = _load_board()
        tasks = board.get("tasks", {})

        if not tasks:
            return "No tasks found on the board."

        tasks_to_show = (
            {tid: t for tid, t in tasks.items() if t.get("status") == status}
            if status
            else tasks
        )

        if not tasks_to_show:
            return f"No tasks found with status '{status}'."

        output = [
            f"- ID: {task_id}, Status: [{task_info.get('status', 'N/A')}], Title: {task_info.get('title', 'N/A')}"
            for task_id, task_info in tasks_to_show.items()
        ]

        return "\n".join(output)
    except (IOError, json.JSONDecodeError) as e:
        error_msg = f"Failed to list tasks due to a storage error: {e}"
        logging.error(error_msg)
        raise KanbanToolError(error_msg) from e


def update_task(
    task_id: str,
    new_status: Optional[str] = None,
    new_description: Optional[str] = None,
) -> str:
    """
    Updates the status or description of an existing task.

    Args:
        task_id: The ID of the task to update.
        new_status: The new status to set for the task.
        new_description: The new description to set for the task.

    Returns:
        A confirmation or error message.
    """
    if not new_status and not new_description:
        return "Error: You must provide either a new status or a new description to update the task."

    try:
        board = _load_board()
        if task_id not in board.get("tasks", {}):
            return f"Error: Task with ID '{task_id}' not found."

        updated_fields = []
        if new_status:
            board["tasks"][task_id]["status"] = new_status
            updated_fields.append(f"status to '{new_status}'")
        if new_description:
            board["tasks"][task_id]["description"] = new_description
            updated_fields.append("description")

        _save_board(board)
        logging.info(f"Updated task {task_id}: set {' and '.join(updated_fields)}")
        return f"Successfully updated task '{task_id}'."
    except (IOError, json.JSONDecodeError) as e:
        error_msg = f"Failed to update task {task_id} due to a storage error: {e}"
        logging.error(error_msg)
        raise KanbanToolError(error_msg) from e
    except KeyError:
        # This can happen if board.get("tasks", {}) passes but board["tasks"][task_id] fails.
        error_msg = f"Error: Task with ID '{task_id}' not found during update."
        logging.warning(error_msg)
        return error_msg