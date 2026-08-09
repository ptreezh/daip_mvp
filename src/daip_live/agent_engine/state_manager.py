"""
StateManager - 状态管理器
专门负责AgentExecutor的状态管理
遵循KISS/YAGNI/SOLID原则
"""

import logging
from typing import Optional

from daip_live.core.models import AgentState, AgentStatus

logger = logging.getLogger(__name__)


class StateManager:
    """
    状态管理器 - 专门负责状态管理功能
    遵循单一职责原则，只关注状态管理相关功能
    """

    def __init__(self, model_provider: Optional[object] = None):
        """
        初始化状态管理器

        Args:
            model_provider: 模型提供者（用于获取模型名称）
        """
        self.state: AgentState = AgentState.IDLE
        self.model_provider = model_provider
        self.tokens_used: int = 0
        self.tokens_total: int = 8192  # Default, should be updated based on model
        logger.info("StateManager initialized")

    def change_state(self, new_state: AgentState) -> None:
        """
        更改状态

        Args:
            new_state: 新状态
        """
        logger.info(f"Changing state from {self.state.name} to {new_state.name}")
        self.state = new_state

    def get_status(self) -> AgentStatus:
        """
        获取当前状态快照

        Returns:
            AgentStatus: 状态快照
        """
        model_name = "unknown"
        if self.model_provider and hasattr(self.model_provider, "config"):
            model_name = getattr(self.model_provider.config, "model", "unknown")

        return AgentStatus(
            state=self.state.value,
            model_name=model_name,
            tokens_used=self.tokens_used,
            tokens_total=self.tokens_total,
        )

    def update_tokens(self, tokens_used: int) -> None:
        """
        更新已使用的令牌数

        Args:
            tokens_used: 新增的令牌使用量
        """
        self.tokens_used += tokens_used
        logger.info(f"Updated tokens used: {self.tokens_used}/{self.tokens_total}")
