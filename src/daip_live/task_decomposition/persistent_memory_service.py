"""
持久化任务记忆服务
用于存储复杂任务的上下文、状态和执行历史
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SubTask:
    """子任务数据类"""
    subtask_id: str
    parent_task_id: str
    title: str
    description: str
    dependencies: List[str]  # 依赖的子任务ID
    status: TaskStatus
    result: Optional[str] = None
    execution_log: Optional[List[str]] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.execution_log is None:
            self.execution_log = []


@dataclass
class TaskContext:
    """任务上下文数据类"""
    task_id: str
    parent_task_id: Optional[str]
    task_description: str
    subtasks: List[SubTask]
    current_subtask_index: int = 0
    execution_history: Optional[List[Dict[str, Any]]] = None
    overall_progress: float = 0.0
    created_at: datetime = None
    last_updated: datetime = None
    status: TaskStatus = TaskStatus.PENDING

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.execution_history is None:
            self.execution_history = []


class PersistentMemoryService:
    """持久化记忆服务 - 存储任务上下文和状态"""

    def __init__(self):
        # 在实际应用中，这里应该是数据库连接
        # 为了演示，使用内存存储
        self._tasks_storage: Dict[str, TaskContext] = {}
        self._subtasks_storage: Dict[str, SubTask] = {}

    def save_task_context(self, context: TaskContext) -> bool:
        """
        保存任务上下文
        :param context: 任务上下文
        :return: 是否保存成功
        """
        try:
            # 更新最后更新时间
            context.last_updated = datetime.now()
            
            # 存储任务上下文
            self._tasks_storage[context.task_id] = context
            
            # 存储子任务
            for subtask in context.subtasks:
                self._subtasks_storage[subtask.subtask_id] = subtask
            
            return True
        except Exception as e:
            print(f"保存任务上下文失败: {e}")
            return False

    def load_task_context(self, task_id: str) -> Optional[TaskContext]:
        """
        加载任务上下文
        :param task_id: 任务ID
        :return: 任务上下文，如果不存在则返回None
        """
        try:
            return self._tasks_storage.get(task_id)
        except Exception as e:
            print(f"加载任务上下文失败: {e}")
            return None

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        更新任务整体状态
        :param task_id: 任务ID
        :param status: 新状态
        :return: 是否更新成功
        """
        try:
            if task_id in self._tasks_storage:
                self._tasks_storage[task_id].status = status
                self._tasks_storage[task_id].last_updated = datetime.now()
                return True
            return False
        except Exception as e:
            print(f"更新任务状态失败: {e}")
            return False

    def update_subtask_status(self, subtask_id: str, status: TaskStatus, result: Optional[str] = None, error: Optional[str] = None) -> bool:
        """
        更新子任务状态
        :param subtask_id: 子任务ID
        :param status: 新状态
        :param result: 任务结果
        :param error: 错误信息
        :return: 是否更新成功
        """
        try:
            if subtask_id in self._subtasks_storage:
                subtask = self._subtasks_storage[subtask_id]
                subtask.status = status
                if result is not None:
                    subtask.result = result
                if error is not None:
                    subtask.error_message = error
                if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
                    subtask.completed_at = datetime.now()
                
                # 更新父任务进度
                self._update_parent_task_progress(subtask.parent_task_id)
                
                return True
            return False
        except Exception as e:
            print(f"更新子任务状态失败: {e}")
            return False

    def _update_parent_task_progress(self, parent_task_id: str) -> None:
        """更新父任务进度"""
        if parent_task_id not in self._tasks_storage:
            return

        task_context = self._tasks_storage[parent_task_id]
        total_subtasks = len(task_context.subtasks)
        
        if total_subtasks == 0:
            task_context.overall_progress = 0.0
            return

        completed_subtasks = sum(1 for subtask in task_context.subtasks 
                                if subtask.status == TaskStatus.COMPLETED)
        
        task_context.overall_progress = completed_subtasks / total_subtasks

        # 更新父任务状态
        if completed_subtasks == total_subtasks:
            task_context.status = TaskStatus.COMPLETED
        elif any(subtask.status == TaskStatus.FAILED for subtask in task_context.subtasks):
            task_context.status = TaskStatus.FAILED

    def get_subtask(self, subtask_id: str) -> Optional[SubTask]:
        """
        获取子任务
        :param subtask_id: 子任务ID
        :return: 子任务，如果不存在则返回None
        """
        return self._subtasks_storage.get(subtask_id)

    def add_execution_log(self, task_id: str, log: Dict[str, Any]) -> bool:
        """
        添加执行日志
        :param task_id: 任务ID
        :param log: 日志条目
        :return: 是否添加成功
        """
        try:
            if task_id in self._tasks_storage:
                self._tasks_storage[task_id].execution_history.append(log)
                self._tasks_storage[task_id].last_updated = datetime.now()
                return True
            return False
        except Exception as e:
            print(f"添加执行日志失败: {e}")
            return False

    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务进度信息
        :param task_id: 任务ID
        :return: 进度信息字典
        """
        try:
            task_context = self._tasks_storage.get(task_id)
            if not task_context:
                return {}

            total = len(task_context.subtasks)
            completed = sum(1 for subtask in task_context.subtasks 
                           if subtask.status == TaskStatus.COMPLETED)
            in_progress = sum(1 for subtask in task_context.subtasks 
                             if subtask.status == TaskStatus.IN_PROGRESS)
            failed = sum(1 for subtask in task_context.subtasks 
                        if subtask.status == TaskStatus.FAILED)
            pending = sum(1 for subtask in task_context.subtasks 
                         if subtask.status == TaskStatus.PENDING)

            return {
                "total_subtasks": total,
                "completed": completed,
                "in_progress": in_progress,
                "failed": failed,
                "pending": pending,
                "progress_percentage": task_context.overall_progress * 100,
                "overall_status": task_context.status.value
            }
        except Exception as e:
            print(f"获取任务进度失败: {e}")
            return {}


# 全局记忆服务实例
memory_service = PersistentMemoryService()


def get_memory_service() -> PersistentMemoryService:
    """获取持久化记忆服务实例"""
    return memory_service