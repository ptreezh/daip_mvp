import uuid
from unittest.mock import MagicMock

import pytest


# Dummy classes for testing purposes
class Task:
    def __init__(self, id, title, status="pending"):
        self.id = id
        self.title = title
        self.status = status

class TaskManager:
    def __init__(self, db_session):
        self.db = db_session
        self.tasks = {}

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def add_task(self, task):
        self.tasks[task.id] = task

@pytest.fixture()
def task_manager_with_task():
    """Sets up a TaskManager with a pre-added task."""
    mock_db = MagicMock()
    task_manager = TaskManager(mock_db)
    task1 = Task(id=str(uuid.uuid4()), title="Test Task 1")
    task_manager.add_task(task1)
    return task_manager, task1

def test_get_task_by_id(task_manager_with_task):
    """Test retrieving a task by its ID.
    FIX: Replaced task.task_id with task.id to match the Task model.
    """
    task_manager, task1 = task_manager_with_task
    # Act
    retrieved_task = task_manager.get_task(task1.id)
    # Assert
    assert retrieved_task is not None
    assert retrieved_task.id == task1.id
    assert retrieved_task.title == "Test Task 1"
