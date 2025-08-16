#!/usr/bin/env python3
"""Personal Intelligence Hub - Task Panel Tests

测试任务管理面板组件功能
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from personal_intelligence_hub.components.task_panel import TaskPanel
from personal_intelligence_hub.models.task_models import (
    Task,
    TaskAssignment,
    TaskDecompositionNode,
    TaskPriority,
    TaskProgress,
    TaskStatus,
    TaskUpdate,
    TaskUpdateSource,
)


class TestTaskPanel:
    """任务面板组件测试类"""

    def setup_method(self):
        """测试前置设置"""
        with patch('lona.View.__init__', return_value=None):
            self.panel = TaskPanel()
            self.panel.tasks = []
            self.panel.task_decompositions = []

    def test_initialization(self):
        """测试组件初始化"""
        with patch('lona.View.__init__', return_value=None):
            panel = TaskPanel()
            assert panel is not None
            assert panel.tasks == []
            assert panel.task_decompositions == []

    def test_get_root_tasks(self):
        """测试获取根任务"""
        # 添加测试任务
        root_task = Task(
            id="root1",
            title="根任务",
            description="根任务描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=2.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        sub_task = Task(
            id="sub1",
            title="子任务",
            description="子任务描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id="root1",
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=1.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        self.panel.tasks = [root_task, sub_task]

        root_tasks = self.panel.get_root_tasks()
        assert len(root_tasks) == 1
        assert root_tasks[0].id == "root1"

    def test_get_subtasks(self):
        """测试获取子任务"""
        parent_task = Task(
            id="parent1",
            title="父任务",
            description="父任务描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=3.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        child_task = Task(
            id="child1",
            title="子任务",
            description="子任务描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id="parent1",
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=1.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        self.panel.tasks = [parent_task, child_task]

        subtasks = self.panel.get_subtasks("parent1")
        assert len(subtasks) == 1
        assert subtasks[0].id == "child1"

    def test_get_task_dependencies(self):
        """测试获取任务依赖"""
        task1 = Task(
            id="task1",
            title="任务1",
            description="任务1描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=2.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        task2 = Task(
            id="task2",
            title="任务2",
            description="任务2描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=["task1"],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=1.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        self.panel.tasks = [task1, task2]

        dependencies = self.panel.get_task_dependencies("task2")
        assert len(dependencies) == 1
        assert dependencies[0].id == "task1"

    def test_render_task(self):
        """测试任务渲染"""
        task = Task(
            id="test_task",
            title="测试任务",
            description="这是一个测试任务",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            parent_id=None,
            assigned_agent="Test-AI",
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=2.0,
            actual_hours=1.0,
            progress=0.5,
            metadata={}
        )

        html = self.panel.render_task(task)
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'

    def test_render_task_summary(self):
        """测试任务摘要渲染"""
        # 添加测试任务
        task1 = Task(
            id="task1",
            title="任务1",
            description="描述1",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=2.0,
            actual_hours=2.0,
            progress=1.0,
            metadata={}
        )

        task2 = Task(
            id="task2",
            title="任务2",
            description="描述2",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=3.0,
            actual_hours=1.5,
            progress=0.5,
            metadata={}
        )

        self.panel.tasks = [task1, task2]

        html = self.panel.render_task_summary()
        assert html is not None
        assert "总任务: 2" in str(html)
        assert "已完成: 1" in str(html)
        assert "进行中: 1" in str(html)

    def test_render_task_decompositions_empty(self):
        """测试空任务分解渲染"""
        html = self.panel.render_task_decompositions()
        assert html is not None

    def test_render_task_decompositions_with_data(self):
        """测试有数据的任务分解渲染"""
        decomp = TaskDecompositionNode(
            id="decomp1",
            original_task="原始任务",
            subtasks=[],
            decomposition_strategy="策略",
            confidence=0.85,
            timestamp=datetime.now(),
            metadata={}
        )

        self.panel.task_decompositions = [decomp]

        html = self.panel.render_task_decompositions()
        assert html is not None
        assert "原始任务" in str(html)

    def test_render_empty_state(self):
        """测试空状态渲染"""
        html = self.panel.render()
        assert html is not None
        assert hasattr(html, 'tag_name')
        assert html.tag_name == 'div'

    def test_render_with_tasks(self):
        """测试带任务的渲染"""
        task = Task(
            id="test_task",
            title="测试任务",
            description="测试描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=1.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        self.panel.tasks = [task]

        html = self.panel.render()
        assert html is not None
        assert "测试任务" in str(html)


class TestTaskModels:
    """任务相关数据模型测试"""

    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            id="test_task",
            title="测试任务",
            description="测试描述",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            parent_id=None,
            assigned_agent="Test-AI",
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=2.0,
            actual_hours=1.0,
            progress=0.5,
            metadata={"type": "test"}
        )

        assert task.id == "test_task"
        assert task.title == "测试任务"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH

    def test_task_update_creation(self):
        """测试任务更新创建"""
        update = TaskUpdate(
            id="update1",
            task_id="task1",
            source=TaskUpdateSource.TASK_DECOMPOSITION,
            content="更新内容",
            timestamp=datetime.now(),
            metadata={"type": "test"}
        )

        assert update.id == "update1"
        assert update.source == TaskUpdateSource.TASK_DECOMPOSITION

    def test_task_decomposition_node_creation(self):
        """测试任务分解节点创建"""
        subtask = Task(
            id="sub1",
            title="子任务",
            description="子任务描述",
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            parent_id=None,
            assigned_agent=None,
            dependencies=[],
            subtasks=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            due_date=None,
            estimated_hours=1.0,
            actual_hours=0.0,
            progress=0.0,
            metadata={}
        )

        decomp = TaskDecompositionNode(
            id="decomp1",
            original_task="原始任务",
            subtasks=[subtask],
            decomposition_strategy="策略",
            confidence=0.85,
            timestamp=datetime.now(),
            metadata={}
        )

        assert decomp.id == "decomp1"
        assert decomp.original_task == "原始任务"
        assert len(decomp.subtasks) == 1

    def test_task_assignment_creation(self):
        """测试任务分配创建"""
        assignment = TaskAssignment(
            task_id="task1",
            agent_id="agent1",
            assigned_at=datetime.now(),
            priority=TaskPriority.HIGH,
            estimated_completion=None,
            metadata={}
        )

        assert assignment.task_id == "task1"
        assert assignment.agent_id == "agent1"
        assert assignment.priority == TaskPriority.HIGH

    def test_task_progress_creation(self):
        """测试任务进度创建"""
        progress = TaskProgress(
            task_id="task1",
            progress=0.75,
            status=TaskStatus.IN_PROGRESS,
            updated_at=datetime.now(),
            notes="进度良好",
            metadata={}
        )

        assert progress.task_id == "task1"
        assert progress.progress == 0.75
        assert progress.status == TaskStatus.IN_PROGRESS


if __name__ == "__main__":
    pytest
