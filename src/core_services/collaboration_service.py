import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from typing import Any, Dict, List, Optional

from src.models import Task, TaskBase, WikiEntryRequest

logger = logging.getLogger(__name__)


class CollaborationService:
    """
    Service layer for handling collaboration features like Wiki and Tasks.
    """

    def __init__(self, app_state: Any): # Use Any to avoid circular import type hint
        self.app_state = app_state

    def get_wiki_content(self, entry: str) -> str:
        """Get the content of a wiki entry."""
        return self.app_state.load_wiki_content(entry)

    def save_wiki_version(self, request: WikiEntryRequest) -> None:
        """Save a new version of a wiki entry."""
        self.app_state.save_wiki_version(
            request.entry,
            request.content or "",
            request.editor or "unknown_editor",
            request.timestamp or time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def create_task(self, task_base: TaskBase) -> Task:
        """Create a new collaborative task."""
        task_id = str(uuid.uuid4())
        new_task = Task(id=task_id, **task_base.model_dump())
        self.app_state.tasks_db[task_id] = new_task
        logger.info(f"Created new task '{new_task.title}' with ID {task_id}.")
        return new_task

    def list_tasks(
        self, stage: Optional[str], assigned_to: Optional[str], status: Optional[str]
    ) -> List[Task]:
        """List and filter all collaborative tasks."""
        tasks = list(self.app_state.tasks_db.values())
        if stage:
            tasks = [t for t in tasks if t.stage == stage]
        if assigned_to:
            tasks = [t for t in tasks if t.assigned_to == assigned_to]
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def update_task(
        self, task_id: str, status: Optional[str], progress: Optional[int], comment: Optional[str]
    ) -> Task:
        """Update a task's status, progress, or add a comment."""
        if task_id not in self.app_state.tasks_db:
            raise ValueError("Task not found")

        task = self.app_state.tasks_db[task_id]
        update_data = {}
        if status:
            task.status = status
            update_data["status"] = status
        if progress is not None:
            task.progress = progress
            update_data["progress"] = progress
        if comment:
            task.comments.append({"content": comment, "time": datetime.now().isoformat()})

        task.updated_at = datetime.now()
        task.history.append({"update": update_data, "timestamp": task.updated_at.isoformat()})
        logger.info(f"Updated task {task_id}: {update_data}")
        return task

    def get_collaboration_users(self) -> List[Dict[str, Any]]:
        """Get the list of collaboration users (mock data)."""
        return self.app_state.collaboration_users

    def get_collaboration_projects(self) -> List[Dict[str, Any]]:
        """Get the list of collaboration projects (mock data)."""
        return self.app_state.collaboration_projects
