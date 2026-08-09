"""
嵌套Todo列表和任务分解系统
实现三层嵌套的待办事项管理，支持任务分解和逐层执行
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class NestedTodoItem:
    """
    支持嵌套的待办事项项目
    最多支持三层嵌套：任务 -> 子任务 -> 细节步骤
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    # 第一层嵌套：子任务
    subtasks: list["NestedTodoItem"] = field(default_factory=list)
    # 第二层嵌套：细节步骤
    details: list["NestedTodoItem"] = field(default_factory=list)
    # 指向上级任务的引用
    parent_id: Optional[str] = None
    # 前置依赖任务
    dependencies: list[str] = field(default_factory=list)
    # 额外元数据
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_subtask(self, subtask: "NestedTodoItem") -> None:
        """添加子任务"""
        subtask.parent_id = self.id
        self.subtasks.append(subtask)
        self.updated_at = datetime.now()

    def add_detail(self, detail: "NestedTodoItem") -> None:
        """添加细节步骤"""
        detail.parent_id = self.id
        self.details.append(detail)
        self.updated_at = datetime.now()

    def mark_in_progress(self) -> None:
        """标记为进行中"""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def mark_completed(self) -> None:
        """标记为完成"""
        self.status = TaskStatus.COMPLETED
        self.updated_at = datetime.now()

        # 如果有子任务，也标记为完成
        for subtask in self.subtasks:
            if subtask.status != TaskStatus.COMPLETED:
                subtask.mark_completed()

        # 如果有细节步骤，也标记为完成
        for detail in self.details:
            if detail.status != TaskStatus.COMPLETED:
                detail.mark_completed()

    def mark_cancelled(self) -> None:
        """标记为取消"""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()

    def mark_failed(self) -> None:
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.updated_at = datetime.now()

    def is_ready_to_start(self) -> bool:
        """检查是否所有依赖都已完成，可以开始"""
        for dep_id in self.dependencies:
            # 这里需要在完整的TodoManager中查找依赖状态
            pass
        return True

    def get_level(self) -> int:
        """获取任务层级：0=根任务，1=子任务，2=细节步骤"""
        if self.parent_id is None:
            return 0
        elif self.details:  # 如果有细节步骤，说明是子任务
            return 1
        else:  # 如果没有细节步骤但有父任务，可能是子任务或细节步骤
            # 需要通过父任务的结构来确定层级
            return 1  # 简化处理：假设直接子任务为1级

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "subtasks": [subtask.to_dict() for subtask in self.subtasks],
            "details": [detail.to_dict() for detail in self.details],
            "parent_id": self.parent_id,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


@dataclass
class TodoListContext:
    """待办列表上下文，支持任务分解和状态管理"""

    name: str = "Default Todo List"
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    owner_id: Optional[str] = None
    # 根任务列表
    root_tasks: list[NestedTodoItem] = field(default_factory=list)
    # 任务ID到任务对象的映射，便于快速查找
    task_map: dict[str, NestedTodoItem] = field(default_factory=dict)
    # 当前活跃任务栈
    active_stack: list[str] = field(default_factory=list)
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_root_task(self, task: NestedTodoItem) -> None:
        """添加根任务"""
        self.root_tasks.append(task)
        self._update_task_map(task)

    def _update_task_map(self, task: NestedTodoItem) -> None:
        """更新任务映射表"""
        self.task_map[task.id] = task

        for subtask in task.subtasks:
            self._update_task_map(subtask)

        for detail in task.details:
            self._update_task_map(detail)

    def get_task(self, task_id: str) -> Optional[NestedTodoItem]:
        """根据ID获取任务"""
        return self.task_map.get(task_id)

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """更新任务状态"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.now()
            return True
        return False

    def get_active_tasks(self) -> list[NestedTodoItem]:
        """获取当前活跃的任务（未完成的）"""
        active = []

        def traverse_tasks(tasks: list[NestedTodoItem]):
            for task in tasks:
                if task.status not in [
                    TaskStatus.COMPLETED,
                    TaskStatus.CANCELLED,
                    TaskStatus.FAILED,
                ]:
                    active.append(task)
                    traverse_tasks(task.subtasks)
                    traverse_tasks(task.details)

        traverse_tasks(self.root_tasks)
        return active

    def get_completed_tasks(self) -> list[NestedTodoItem]:
        """获取已完成的任务"""
        completed = []

        def traverse_tasks(tasks: list[NestedTodoItem]):
            for task in tasks:
                if task.status == TaskStatus.COMPLETED:
                    completed.append(task)
                else:
                    traverse_tasks(task.subtasks)
                    traverse_tasks(task.details)

        traverse_tasks(self.root_tasks)
        return completed

    def get_task_hierarchy(self) -> dict[str, Any]:
        """获取任务层次结构"""
        return {
            "name": self.name,
            "description": self.description,
            "total_tasks": len(self.task_map),
            "active_tasks": len(self.get_active_tasks()),
            "completed_tasks": len(self.get_completed_tasks()),
            "root_tasks": [task.to_dict() for task in self.root_tasks],
        }

    def remove_task(self, task_id: str) -> bool:
        """移除任务及其所有子任务"""
        task = self.get_task(task_id)
        if not task or not task.parent_id:
            # 如果是根任务
            for i, root_task in enumerate(self.root_tasks):
                if root_task.id == task_id:
                    del self.root_tasks[i]
                    self._remove_from_task_map(task_id)
                    return True
        else:
            # 如果是子任务或细节步骤，需要从父任务中移除
            parent = self.get_task(task.parent_id)
            if parent:
                # 检查是否在子任务中
                for i, subtask in enumerate(parent.subtasks):
                    if subtask.id == task_id:
                        del parent.subtasks[i]
                        self._remove_from_task_map(task_id)
                        return True
                # 检查是否在细节步骤中
                for i, detail in enumerate(parent.details):
                    if detail.id == task_id:
                        del parent.details[i]
                        self._remove_from_task_map(task_id)
                        return True
        return False

    def _remove_from_task_map(self, task_id: str) -> None:
        """从任务映射表中移除任务及其子任务"""
        task = self.task_map.get(task_id)
        if task:
            # 递归移除所有子任务
            for subtask in task.subtasks:
                self._remove_from_task_map(subtask.id)
            for detail in task.details:
                self._remove_from_task_map(detail.id)
            # 移除自身
            del self.task_map[task_id]


class TodoManager:
    """待办事项管理器"""

    def __init__(self):
        self.contexts: dict[str, TodoListContext] = {}
        self.current_context: Optional[str] = None

    def create_context(self, name: str, description: str = "") -> TodoListContext:
        """创建新的待办列表上下文"""
        context = TodoListContext(name=name, description=description)
        context_id = str(uuid.uuid4())
        self.contexts[context_id] = context
        if self.current_context is None:
            self.current_context = context_id
        return context

    def switch_context(self, context_id: str) -> bool:
        """切换到指定的待办列表上下文"""
        if context_id in self.contexts:
            self.current_context = context_id
            return True
        return False

    def get_current_context(self) -> Optional[TodoListContext]:
        """获取当前待办列表上下文"""
        if self.current_context and self.current_context in self.contexts:
            return self.contexts[self.current_context]
        return None

    def add_task_to_current_context(self, task: NestedTodoItem) -> bool:
        """向当前上下文添加任务"""
        context = self.get_current_context()
        if context:
            context.add_root_task(task)
            return True
        return False

    def get_tasks_by_status(self, status: TaskStatus) -> list[NestedTodoItem]:
        """获取指定状态的任务"""
        context = self.get_current_context()
        if context:
            if status == TaskStatus.COMPLETED:
                return context.get_completed_tasks()
            else:
                # 返回所有该状态的任务（包括嵌套的）
                result = []

                def find_tasks_with_status(
                    tasks: list[NestedTodoItem], target_status: TaskStatus
                ):
                    for task in tasks:
                        if task.status == target_status:
                            result.append(task)
                        find_tasks_with_status(task.subtasks, target_status)
                        find_tasks_with_status(task.details, target_status)

                find_tasks_with_status(context.root_tasks, status)
                return result
        return []


# 示例任务分解器
class HierarchicalTaskDecomposer:
    """分层任务分解器"""

    @staticmethod
    def decompose_task(task_description: str, level: int = 0) -> list[NestedTodoItem]:
        """
        将任务分解为子任务
        level: 0=根任务, 1=子任务, 2=细节步骤
        """
        if level >= 2:  # 最多分解两层
            # 返回细节步骤
            return [
                NestedTodoItem(
                    title=f"执行: {task_description}",
                    description=f"执行任务 '{task_description}' 的具体步骤",
                    priority=TaskPriority.MEDIUM,
                )
            ]

        # 根据任务类型进行分解

        # 识别不同类型的任务
        if "分析" in task_description or "research" in task_description.lower():
            # 分析类任务分解
            subtasks = []

            if level == 0:
                # 第一层：分析的不同方面
                aspects = ["背景调研", "现状分析", "问题识别", "解决方案", "结论总结"]
            else:
                # 第二层：具体的分析步骤
                aspects = ["数据收集", "数据处理", "数据分析", "结果验证"]

            for i, aspect in enumerate(aspects):
                subtask = NestedTodoItem(
                    title=f"{aspect}",
                    description=f"针对 '{task_description}' 进行{aspect}",
                    priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                )

                # 为每个子任务进一步分解细节
                if level == 0:
                    details = HierarchicalTaskDecomposer.decompose_task(
                        f"{aspect} for {task_description}", level + 1
                    )
                    for detail in details:
                        subtask.add_detail(detail)

                subtasks.append(subtask)

        elif (
            "写" in task_description
            or "撰写" in task_description
            or "create" in task_description.lower()
        ):
            # 写作类任务分解
            if level == 0:
                stages = ["大纲规划", "初稿撰写", "内容审核", "修改完善", "最终检查"]
            else:
                stages = ["收集素材", "组织结构", "撰写内容", "校对润色"]

            subtasks = []
            for i, stage in enumerate(stages):
                subtask = NestedTodoItem(
                    title=f"{stage}",
                    description=f"{task_description} -> {stage}",
                    priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                )

                # 进一步分解细节
                if level == 0:
                    details = HierarchicalTaskDecomposer.decompose_task(
                        f"{stage} for {task_description}", level + 1
                    )
                    for detail in details:
                        subtask.add_detail(detail)

                subtasks.append(subtask)
        else:
            # 一般任务分解
            if level == 0:
                phases = ["准备阶段", "执行阶段", "检验阶段", "收尾阶段"]
            else:
                phases = ["步骤1", "步骤2", "步骤3"]

            subtasks = []
            for i, phase in enumerate(phases):
                subtask = NestedTodoItem(
                    title=f"{phase}",
                    description=f"{task_description} -> {phase}",
                    priority=TaskPriority.HIGH if i == 0 else TaskPriority.MEDIUM,
                )

                if level == 0:
                    details = HierarchicalTaskDecomposer.decompose_task(
                        f"{phase} for {task_description}", level + 1
                    )
                    for detail in details:
                        subtask.add_detail(detail)

                subtasks.append(subtask)

        return subtasks


if __name__ == "__main__":
    # 创建待办列表管理器
    todo_manager = TodoManager()
    context = todo_manager.create_context("项目开发", "软件开发项目任务分解")

    # 创建根任务
    main_task = NestedTodoItem(
        title="开发新功能模块",
        description="实现用户管理系统的核心功能",
        priority=TaskPriority.HIGH,
    )

    # 分解任务
    subtasks = HierarchicalTaskDecomposer.decompose_task("开发用户管理系统", 0)
    for subtask in subtasks:
        main_task.add_subtask(subtask)

    # 添加到上下文
    context.add_root_task(main_task)

    # 显示任务层次结构
    hierarchy = context.get_task_hierarchy()

    # 显示根任务
    for root_task in context.root_tasks:
        for subtask in root_task.subtasks[:2]:  # 只显示前两个
            pass
