"""@Time    : 2025-07-03 17:37:40
@Author  : DAIP-LIVE Team
@File    : task_manager.py
@Description:
    Manages tasks with dependencies (DAG-aware).
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

import frontmatter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Task:
    """Represents a single task in the system."""

    def __init__(
        self,
        task_id: str,
        title: str,
        status: str = "to_do",
        assignee: Optional[str] = None,
        dependencies: Optional[list[str]] = None,
        description: str = "",
        deliverable_path: Optional[str] = None,
    ):
        self.task_id = task_id
        self.title = title
        self.status = status  # to_do, in_progress, done, blocked
        self.assignee = assignee
        self.dependencies = dependencies or []
        self.description = description
        self.deliverable_path = deliverable_path

    def to_dict(self) -> dict[str, Any]:
        """Converts the task to a dictionary."""
        return self.__dict__


class TaskManager:
    """Handles the creation, management, and tracking of tasks.
    Aware of task dependencies, forming a Directed Acyclic Graph (DAG).
    """

    def __init__(self, task_directory: str = "daip_mvp_project/memory_bank/tasks/"):
        """Initializes the TaskManager.

        Args:
        ----
            task_directory (str): The path to the directory for storing task files.

        """
        self._task_directory = Path(task_directory)
        os.makedirs(self._task_directory, exist_ok=True)
        logging.info(f"TaskManager initialized. Task directory: {self._task_directory}")

    def create_task(self, metadata: dict[str, Any], description: str) -> Task:
        """Creates a new task and persists it to a Markdown file.

        Args:
        ----
            metadata (Dict[str, Any]): A dictionary containing task metadata.
            description (str): The detailed description of the task.

        Returns:
        -------
            Task: The newly created Task object.

        """
        task_id = metadata["task_id"]
        logging.info(f"Creating task: {task_id} - {metadata.get('title')}")

        task = Task(
            task_id=task_id,
            title=metadata.get("title", "Untitled Task"),
            status=metadata.get("status", "to_do"),
            assignee=metadata.get("assignee"),
            dependencies=metadata.get("dependencies"),
            description=description,
            deliverable_path=metadata.get("deliverable_path"),
        )

        post = frontmatter.Post(content=task.description)
        post.metadata = task.to_dict()
        del post.metadata["task_id"]  # task_id is the filename

        file_path = self._task_directory / f"{task_id}.md"
        with open(file_path, "wb") as f:
            frontmatter.dump(post, f, encoding="utf-8")

        logging.info(f"Task '{task_id}' saved to {file_path}")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieves a task by its ID from the file system.

        Args:
        ----
            task_id (str): The ID of the task to retrieve.

        Returns:
        -------
            Optional[Task]: The Task object if found, otherwise None.

        """
        logging.info(f"Retrieving task: {task_id}")
        file_path = self._task_directory / f"{task_id}.md"

        if not file_path.is_file():
            logging.warning(f"Task file not found: {file_path}")
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                post = frontmatter.load(f)

            task_data = post.metadata
            task_data["task_id"] = task_id
            task_data["description"] = post.content

            return Task(**task_data)
        except Exception as e:
            logging.error(f"Error loading task '{task_id}' from {file_path}: {e}")
            return None

    def update_task_status(self, task_id: str, new_status: str) -> bool:
        """Updates the status of a specific task by modifying its file.

        Args:
        ----
            task_id (str): The ID of the task to update.
            new_status (str): The new status for the task.

        Returns:
        -------
            bool: True if the update was successful, False otherwise.

        """
        logging.info(f"Updating status for task '{task_id}' to '{new_status}'.")
        file_path = self._task_directory / f"{task_id}.md"

        if not file_path.is_file():
            logging.warning(f"Cannot update status. Task file not found: {file_path}")
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                post = frontmatter.load(f)

            post.metadata["status"] = new_status

            with open(file_path, "wb") as f:
                frontmatter.dump(post, f, encoding="utf-8")

            logging.info(f"Successfully updated status for task '{task_id}'.")
            return True
        except Exception as e:
            logging.error(f"Error updating task '{task_id}': {e}")
            return False

    def get_ready_tasks(self) -> list[Task]:
        """Gets a list of all tasks that are ready to be worked on (status 'to_do'
        and all dependencies are 'done').

        Returns
        -------
            List[Task]: A list of ready Task objects.

        """
        logging.info("Scanning for ready tasks...")
        ready_tasks = []
        all_task_files = [f for f in self._task_directory.glob("*.md")]

        for task_file in all_task_files:
            task_id = task_file.stem
            task = self.get_task(task_id)

            if task and task.status == "to_do":
                dependencies_met = True
                if not task.dependencies:
                    ready_tasks.append(task)
                    continue

                for dep_id in task.dependencies:
                    dep_task = self.get_task(dep_id)
                    if not dep_task or dep_task.status != "done":
                        dependencies_met = False
                        logging.debug(
                            f"Task '{task_id}' is waiting for dependency '{dep_id}' (status: {dep_task.status if dep_task else 'Not Found'})."
                        )
                        break

                if dependencies_met:
                    logging.info(f"Task '{task_id}' is ready.")
                    ready_tasks.append(task)

        logging.info(f"Found {len(ready_tasks)} ready tasks.")
        return ready_tasks

    def get_task_context(self, task_id: str) -> str:
        """Gets the full context for a task by recursively gathering the
        deliverables from all its dependencies.

        Args:
        ----
            task_id (str): The ID of the task to get context for.

        Returns:
        -------
            str: A string containing the concatenated content of all dependency deliverables.

        """
        logging.info(f"Getting context for task '{task_id}'...")
        task = self.get_task(task_id)
        if not task:
            return ""

        all_deps = self._get_all_dependencies(task_id)

        context_parts = []
        for dep_id in all_deps:
            dep_task = self.get_task(dep_id)
            if dep_task and dep_task.deliverable_path:
                deliverable_file = self._task_directory / dep_task.deliverable_path
                if deliverable_file.is_file():
                    try:
                        content = deliverable_file.read_text(encoding="utf-8")
                        context_parts.append(
                            f"--- Context from {dep_id} ---\n{content}\n"
                        )
                    except Exception as e:
                        logging.warning(
                            f"Could not read deliverable for task '{dep_id}': {e}"
                        )

        full_context = "\n".join(context_parts)
        logging.info(
            f"Generated context of length {len(full_context)} for task '{task_id}'."
        )
        return full_context

    def _get_all_dependencies(self, task_id: str) -> set:
        """Recursively finds all unique dependencies for a given task."""
        task = self.get_task(task_id)
        if not task:
            return set()

        deps = set(task.dependencies)
        for dep_id in task.dependencies:
            deps.update(self._get_all_dependencies(dep_id))

        return deps
