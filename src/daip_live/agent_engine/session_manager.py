"""
SessionManager - 会话管理器
专门负责会话的创建、保存和状态管理
遵循KISS/YAGNI/SOLID原则
"""

import logging

from daip_live.core.models import AgentState, Session, ThoughtEvent
from daip_live.memory.session_manager import SessionManager as BaseSessionManager

logger = logging.getLogger(__name__)


class SessionManager:
    """
    会话管理器 - 专门负责会话管理功能
    遵循单一职责原则，只关注会话管理相关功能
    """

    def __init__(self, base_session_manager: BaseSessionManager):
        """
        初始化会话管理器

        Args:
            base_session_manager: 基础会话管理器实例
        """
        self.base_session_manager = base_session_manager
        logger.info("SessionManager initialized")

    def create_session(
        self, goal: str, session_type: str, participant_ids: list[str]
    ) -> Session:
        """
        创建新会话

        Args:
            goal: 会话目标
            session_type: 会话类型
            participant_ids: 参与者ID列表

        Returns:
            Session: 创建的会话实例
        """
        session = self.base_session_manager.create_session(
            goal=goal, session_type=session_type, participant_ids=participant_ids
        )
        logger.info(f"Created session {session.session_id} for goal: {goal}")
        return session

    def save_session(self, session: Session) -> None:
        """
        保存会话

        Args:
            session: 要保存的会话
        """
        # 更新会话状态
        session.status = session.status
        self.base_session_manager.save_session(session)
        logger.info(f"Saved session {session.session_id}")

    def update_session_status(self, session: Session, status: AgentState) -> None:
        """
        更新会话状态

        Args:
            session: 要更新的会话
            status: 新状态
        """
        session.status = status
        logger.info(f"Updated session {session.session_id} status to {status.name}")

    async def create_session_event(
        self, session_id: str, status: AgentState
    ) -> ThoughtEvent:
        """
        创建会话事件

        Args:
            session_id: 会话ID
            status: 状态

        Returns:
            ThoughtEvent: 会话事件
        """
        return ThoughtEvent(
            content=f"Session {session_id} saved with status {status.name}"
        )
