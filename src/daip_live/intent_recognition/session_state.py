"""
会话状态数据模型
遵循单一职责原则 - 仅负责会话状态数据表示
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .task_context import TaskContext


@dataclass
class SessionState:
    """
    会话状态数据模型
    遵循单一职责原则 - 专门负责会话状态数据的表示
    """

    session_id: str
    current_task: TaskContext = None  # 当前任务上下文
    history: list[dict[str, Any]] = field(default_factory=list)  # 会话历史
    created_at: datetime = field(default_factory=datetime.now)  # 会话创建时间
    last_accessed: datetime = field(default_factory=datetime.now)  # 最后访问时间

    def update_last_accessed(self) -> None:
        """
        更新最后访问时间
        """
        self.last_accessed = datetime.now()

    def add_to_history(self, entry: dict[str, Any]) -> None:
        """
        添加条目到会话历史

        Args:
            entry: 要添加的历史条目
        """
        # 先更新访问时间以确保时间戳不同
        self.update_last_accessed()
        self.history.append(entry)

    def has_active_task(self) -> bool:
        """
        检查会话是否有活跃任务

        Returns:
            如果会话有活跃任务则返回True，否则返回False
        """
        return self.current_task is not None and self.current_task.status == "active"
