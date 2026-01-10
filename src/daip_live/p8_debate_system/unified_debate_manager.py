"""
统一辩论管理器 - 整合SimpleDebateManager和EnhancedDebateManager的功能
"""
import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional

from daip_live.core.models import (
    AgentEvent, DebateCompleteEvent, DebateRoundStartEvent,
    DebateStartEvent, DebateTurnStartEvent, DebateTurnCompleteEvent, DebateTurnStartEvent,
    DialogueTurn, Role, Session, ThoughtEvent, TokenUsageEvent
)
from daip_live.core.interfaces import IDebateManager, IModelProvider
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.simple_debate_manager import SimpleDebateManager
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager


class UnifiedDebateManager(IDebateManager):
    """
    统一的辩论管理器，支持两种模式：
    1. 简单模式 - 使用SimpleDebateManager（快速测试）
    2. 完整模式 - 使用EnhancedDebateManager（真实AI辩论）
    """

    def __init__(
        self,
        session_manager: SessionManager,
        role_manager: RoleManager,
        model_provider: IModelProvider,
        use_enhanced: bool = True,  # 默认使用增强模式
        max_turn_time: int = 120,  # 每轮最大时间（秒）
        thinking_time: int = 30  # 思考时间
    ):
        """初始化统一辩论管理器"""
        super().__init__(session_manager, role_manager, model_provider, False)
        self.use_enhanced = use_enhanced
        self.max_turn_time = max_turn_time
        self.thinking_time = thinking_time

        # 根据模式选择合适的管理器
        if use_enhanced:
            self.debate_manager = EnhancedDebateManager(
                session_manager, role_manager, model_provider, max_turn_time
            )
        else:
            self.debate_manager = SimpleDebateManager.create_simple_debate(
                session_manager, role_manager, model_provider
            )

        # 为CLI提供方法
        self.session_manager = session_manager
        self.role_manager = role_manager

    async def run_debate(
        self,
        topic: str,
        roles: List[str],
        rounds: int,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行统一辩论"""
        if session_id is None:
            session_id = f"unified_debate_{int(asyncio.get_event_loop().time())}"

        # 初始化辩论状态
        await self.debate_manager.start_debate(topic, roles, rounds)

        # 运行辩论
        async for event in self.debate_manager.run_debate(topic, roles, rounds):
            yield event

    async def get_debate_model_summary(self, roles: List[str]) -> Dict[str, Any]:
        """获取辩论模型配置摘要"""
        if hasattr(self.debate_manager, 'get_debate_model_summary'):
            return await self.debate_manager.get_debate_model_summary(roles)
        else:
            # SimpleDebateManager没有这个方法，提供基础信息
            return {
                'model_assignments': {role: self.model_provider.get_default_model() for role in roles},
                'total_models': 1,
                'provider_type': 'SimpleProvider'
            }

    async def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return await self.debate_manager.get_available_models()

    async def get_default_model(self) -> str:
        """获取默认模型"""
        return await self.debate_manager.get_default_model()