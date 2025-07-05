"""@Time    : 2025-07-03 20:20:00
@Author  : DAIP-LIVE Team
@File    : test_task_manager.py
@Description:
    Unit tests for the TaskManager service.
"""

import os
import shutil
from pathlib import Path

import pytest
from daip_mvp_project.src.core_services.task_manager import TaskManager


# Define a temporary directory for tasks for testing purposes
@pytest.fixture
def temp_task_dir(tmp_path):
    """Provides a temporary directory for task files."""
    task_dir = tmp_path / "test_tasks"
    os.makedirs(task_dir, exist_ok=True)
    yield str(task_dir)
    shutil.rmtree(task_dir)  # Clean up after tests


@pytest.fixture
def task_manager(temp_task_dir):
    """Provides a TaskManager instance initialized with a temporary directory."""
    return TaskManager(task_directory=temp_task_dir)


def test_create_and_get_task(task_manager):
    """Tests if a task can be created and retrieved correctly."""
    metadata = {
        "task_id": "T001",
        "title": "Initial Setup",
        "status": "to_do",
        "assignee": "Dev",
        "dependencies": [],
        "deliverable_path": "path/to/deliverable.py",
    }
    description = "Set up the basic project structure."

    created_task = task_manager.create_task(metadata, description)
    assert created_task is not None
    assert created_task.task_id == "T001"
    assert created_task.title == "Initial Setup"
    assert created_task.status == "to_do"
    assert created_task.description == description

    retrieved_task = task_manager.get_task("T001")
    assert retrieved_task is not None
    assert retrieved_task.task_id == "T001"
    assert retrieved_task.title == "Initial Setup"
    assert retrieved_task.status == "to_do"
    assert retrieved_task.description == description
    assert retrieved_task.assignee == "Dev"
    assert retrieved_task.dependencies == []
    assert retrieved_task.deliverable_path == "path/to/deliverable.py"


def test_get_non_existent_task(task_manager):
    """Tests retrieving a task that does not exist."""
    task = task_manager.get_task("NON_EXISTENT_TASK")
    assert task is None


def test_create_task_with_minimal_metadata(task_manager):
    """Tests creating a task with only required metadata."""
    metadata = {"task_id": "T002"}
    description = "A task with minimal info."
    created_task = task_manager.create_task(metadata, description)
    assert created_task.task_id == "T002"
    assert created_task.title == "Untitled Task"  # Default title
    assert created_task.status == "to_do"  # Default status
    assert created_task.description == description

    retrieved_task = task_manager.get_task("T002")
    assert retrieved_task.title == "Untitled Task"
    assert retrieved_task.status == "to_do"


def test_update_task_status(task_manager):
    """Tests if task status can be updated correctly."""
    metadata = {"task_id": "T003", "title": "Task to Update", "status": "to_do"}
    description = "This task will be updated."
    task_manager.create_task(metadata, description)

    # Update status to in_progress
    success = task_manager.update_task_status("T003", "in_progress")
    assert success is True
    updated_task = task_manager.get_task("T003")
    assert updated_task.status == "in_progress"

    # Update status to done
    success = task_manager.update_task_status("T003", "done")
    assert success is True
    updated_task = task_manager.get_task("T003")
    assert updated_task.status == "done"


def test_update_status_non_existent_task(task_manager):
    """Tests updating status for a non-existent task."""
    success = task_manager.update_task_status("NON_EXISTENT_TASK", "done")
    assert success is False


def test_get_ready_tasks_no_dependencies(task_manager):
    """Tests getting ready tasks with no dependencies."""
    task_manager.create_task(
        {"task_id": "T004", "title": "Task A", "status": "to_do"}, "Desc A"
    )
    task_manager.create_task(
        {"task_id": "T005", "title": "Task B", "status": "in_progress"}, "Desc B"
    )
    task_manager.create_task(
        {"task_id": "T006", "title": "Task C", "status": "to_do"}, "Desc C"
    )

    ready_tasks = task_manager.get_ready_tasks()
    assert len(ready_tasks) == 2
    assert {t.task_id for t in ready_tasks} == {"T004", "T006"}


def test_get_ready_tasks_with_dependencies(task_manager):
    """Tests getting ready tasks with dependencies."""
    # T007 (done) -> T008 (to_do) -> T009 (to_do)
    # T010 (to_do)
    task_manager.create_task(
        {"task_id": "T007", "title": "Dep Task", "status": "done"}, "Dep A"
    )
    task_manager.create_task(
        {
            "task_id": "T008",
            "title": "Task with Dep",
            "status": "to_do",
            "dependencies": ["T007"],
        },
        "Task B",
    )
    task_manager.create_task(
        {
            "task_id": "T009",
            "title": "Task with Multi Dep",
            "status": "to_do",
            "dependencies": ["T007", "T008"],
        },
        "Task C",
    )
    task_manager.create_task(
        {"task_id": "T010", "title": "Independent Task", "status": "to_do"}, "Task D"
    )

    ready_tasks = task_manager.get_ready_tasks()
    assert len(ready_tasks) == 2
    assert {t.task_id for t in ready_tasks} == {
        "T008",
        "T010",
    }  # T009 is not ready yet because T008 is not done

    # Mark T008 as done, then T009 should become ready
    task_manager.update_task_status("T008", "done")
    ready_tasks = task_manager.get_ready_tasks()
    assert len(ready_tasks) == 2
    assert {t.task_id for t in ready_tasks} == {"T009", "T010"}


def test_get_ready_tasks_blocked_dependency(task_manager):
    """Tests tasks blocked by an incomplete dependency."""
    task_manager.create_task(
        {"task_id": "T011", "title": "Dep Task", "status": "to_do"}, "Dep A"
    )
    task_manager.create_task(
        {
            "task_id": "T012",
            "title": "Task with Dep",
            "status": "to_do",
            "dependencies": ["T011"],
        },
        "Task B",
    )

    ready_tasks = task_manager.get_ready_tasks()
    assert len(ready_tasks) == 1
    assert {t.task_id for t in ready_tasks} == {"T011"}  # T012 is blocked


def test_get_task_context_no_dependencies(task_manager, temp_task_dir):
    """Tests getting context for a task with no dependencies, which should be empty."""
    task_manager.create_task(
        {
            "task_id": "C001",
            "title": "No Dep Task",
            "deliverable_path": "deliverable_c001.txt",
        },
        "Desc C001",
    )

    context = task_manager.get_task_context("C001")
    assert context == ""


def test_get_task_context_with_dependencies(task_manager, temp_task_dir):
    """Tests getting context for a task with dependencies."""
    # D001 (deliverable) -> D002 (deliverable) -> D003 (no deliverable)
    task_manager.create_task(
        {
            "task_id": "D001",
            "title": "Dep 1",
            "status": "done",
            "deliverable_path": "deliverable_d001.txt",
        },
        "Desc D001",
    )
    task_manager.create_task(
        {
            "task_id": "D002",
            "title": "Dep 2",
            "status": "done",
            "dependencies": ["D001"],
            "deliverable_path": "deliverable_d002.txt",
        },
        "Desc D002",
    )
    task_manager.create_task(
        {
            "task_id": "D003",
            "title": "Main Task",
            "status": "to_do",
            "dependencies": ["D002"],
        },
        "Desc D003",
    )

    # Create mock deliverable files
    task_dir = Path(temp_task_dir)
    (task_dir / "deliverable_d001.txt").write_text("Content of D001.")
    (task_dir / "deliverable_d002.txt").write_text("Content of D002.")

    context = task_manager.get_task_context("D003")
    assert "Content of D001." in context
    assert "Content of D002." in context
    assert "--- Context from D001 ---" in context
    assert "--- Context from D002 ---" in context
    assert (
        "Desc D003" not in context
    )  # Main task description itself is not part of context
