import asyncio
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.core_services.collaboration_service import CollaborationService
from src.models import Task, TaskBase, WikiEntryRequest

class TestCollaborationService(unittest.TestCase):
    def setUp(self):
        self.mock_app_state = MagicMock()
        self.mock_app_state.tasks_db = {}
        self.mock_app_state.collaboration_users = []
        self.mock_app_state.collaboration_projects = []
        self.service = CollaborationService(self.mock_app_state)

    def test_get_wiki_content(self):
        self.mock_app_state.load_wiki_content.return_value = "Mocked wiki content"
        content = self.service.get_wiki_content("test_entry")
        self.assertEqual(content, "Mocked wiki content")
        self.mock_app_state.load_wiki_content.assert_called_once_with("test_entry")

    def test_save_wiki_version(self):
        request = WikiEntryRequest(
            entry="test_entry",
            content="New content",
            editor="test_editor",
            timestamp=datetime.now().isoformat()
        )
        self.service.save_wiki_version(request)
        self.mock_app_state.save_wiki_version.assert_called_once_with(
            request.entry,
            request.content,
            request.editor,
            request.timestamp
        )

    def test_create_task(self):
        task_base = TaskBase(
            title="Test Task",
            description="Description for test task",
            stage="todo",
            assigned_to="user1",
            status="pending"
        )
        task = self.service.create_task(task_base)
        self.assertIsInstance(task, Task)
        self.assertIsNotNone(task.id)
        self.assertEqual(self.mock_app_state.tasks_db[task.id], task)

    def test_list_tasks(self):
        task1 = Task(id="1", title="Task 1", stage="todo", assigned_to="user1", status="pending")
        task2 = Task(id="2", title="Task 2", stage="in_progress", assigned_to="user2", status="pending")
        task3 = Task(id="3", title="Task 3", stage="todo", assigned_to="user1", status="completed")
        self.mock_app_state.tasks_db = {"1": task1, "2": task2, "3": task3}

        # No filters
        tasks = self.service.list_tasks(None, None, None)
        self.assertEqual(len(tasks), 3)

        # Filter by stage
        tasks = self.service.list_tasks("todo", None, None)
        self.assertEqual(len(tasks), 2)
        self.assertIn(task1, tasks)
        self.assertIn(task3, tasks)

        # Filter by assigned_to
        tasks = self.service.list_tasks(None, "user2", None)
        self.assertEqual(len(tasks), 1)
        self.assertIn(task2, tasks)

        # Filter by status
        tasks = self.service.list_tasks(None, None, "completed")
        self.assertEqual(len(tasks), 1)
        self.assertIn(task3, tasks)

        # Multiple filters
        tasks = self.service.list_tasks("todo", "user1", "pending")
        self.assertEqual(len(tasks), 1)
        self.assertIn(task1, tasks)

    def test_update_task_success(self):
        task = Task(id="1", title="Task 1", stage="todo", assigned_to="user1", status="pending")
        self.mock_app_state.tasks_db = {"1": task}

        updated_task = self.service.update_task("1", status="in_progress", progress=50, comment="Started work")
        self.assertEqual(updated_task.status, "in_progress")
        self.assertEqual(updated_task.progress, 50)
        self.assertEqual(len(updated_task.comments), 1)
        self.assertEqual(updated_task.comments[0]["content"], "Started work")
        self.assertEqual(len(updated_task.history), 1)
        self.assertIn("status", updated_task.history[0]["update"])

    def test_update_task_not_found(self):
        with self.assertRaisesRegex(ValueError, "Task not found"):
            self.service.update_task("non_existent", status="in_progress")

if __name__ == "__main__":
    unittest.main()
