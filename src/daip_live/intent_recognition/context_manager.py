"""
上下文管理器实现
遵循单一职责原则 - 仅负责上下文管理
"""

from typing import Any, Optional

from .context_interfaces import IContextManager
from .session_state import SessionState
from .task_context import TaskContext


class ContextManager(IContextManager):
    """
    上下文管理器实现
    遵循单一职责原则 - 专门负责上下文管理
    """

    def __init__(self):
        self.sessions: dict[str, SessionState] = {}

    def set_context(self, session_id: str, context: dict[str, Any]) -> None:
        """
        设置特定会话的上下文

        Args:
            session_id: 会话标识符
            context: 上下文数据，应包含task_type和required_params
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionState(session_id=session_id)

        session_state = self.sessions[session_id]

        # 创建新的任务上下文
        task_type = context.get("task_type", "")
        required_params = context.get("required_params", [])
        task_context = TaskContext(task_type=task_type, required_params=required_params)

        session_state.current_task = task_context
        session_state.update_last_accessed()

    def get_context(self, session_id: str) -> Optional[dict[str, Any]]:
        """
        获取特定会话的上下文

        Args:
            session_id: 会话标识符

        Returns:
            会话上下文数据，如果不存在则返回None
        """
        if session_id not in self.sessions:
            return None

        session_state = self.sessions[session_id]
        if session_state.current_task is None:
            return None

        return {
            "task_type": session_state.current_task.task_type,
            "parameters": session_state.current_task.parameters,
            "required_params": session_state.current_task.required_params,
            "filled_params": session_state.current_task.filled_params,
            "status": session_state.current_task.status,
        }

    def clear_context(self, session_id: str) -> None:
        """
        清除特定会话的上下文

        Args:
            session_id: 会话标识符
        """
        if session_id in self.sessions:
            self.sessions[session_id].current_task = None
            self.sessions[session_id].update_last_accessed()

    def is_in_task(self, session_id: str) -> bool:
        """
        检查会话是否正在进行任务

        Args:
            session_id: 会话标识符

        Returns:
            如果会话正在进行任务则返回True，否则返回False
        """
        if session_id not in self.sessions:
            return False

        return self.sessions[session_id].has_active_task()

    def add_task_parameter(
        self, session_id: str, param_name: str, param_value: Any
    ) -> bool:
        """
        为指定会话的任务添加参数

        Args:
            session_id: 会话标识符
            param_name: 参数名称
            param_value: 参数值

        Returns:
            如果成功添加参数则返回True，否则返回False
        """
        if (
            session_id not in self.sessions
            or self.sessions[session_id].current_task is None
        ):
            return False

        self.sessions[session_id].current_task.add_parameter(param_name, param_value)
        self.sessions[session_id].update_last_accessed()
        return True

    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """
        获取会话状态对象

        Args:
            session_id: 会话标识符

        Returns:
            会话状态对象，如果不存在则返回None
        """
        return self.sessions.get(session_id)
