"""
简化辩论管理器 - 用于调试和模块化
避免复杂的依赖和初始化问题
"""

import asyncio
from typing import AsyncGenerator, List, Optional, Dict, Any
import logging

from daip_live.core.models import (
    AgentEvent, DebateCompleteEvent, DebateRoundStartEvent,
    DebateStartEvent, DebateTurnCompleteEvent, DebateTurnStartEvent,
    DialogueTurn, Role, Session, ThoughtEvent
)

log = logging.getLogger(__name__)


class SimpleDebateManager:
    """简化的辩论管理器，避免复杂依赖"""

    def __init__(self, session_manager, role_manager, role_model_manager, model_provider):
        self.session_manager = session_manager
        self.role_manager = role_manager
        self.role_model_manager = role_model_manager
        self.model_provider = model_provider
        self.use_optimized_architecture = False  # 禁用优化架构

    async def run_debate(
        self,
        topic: str,
        roles_names: List[str],
        num_rounds: int
    ) -> AsyncGenerator[AgentEvent, None]:
        """运行简化的辩论"""

        log.info("Starting simple debate manager...")

        # 立即产生开始事件
        yield DebateStartEvent(
            topic=topic,
            roles=roles_names,
            rounds=num_rounds,
            session_id=f"simple_debate_{int(asyncio.get_event_loop().time())}"
        )

        log.info("Debate started, yielding completion...")

        # 简单的辩论完成事件（用于测试）
        yield DebateCompleteEvent(
            session_id=f"simple_debate_{int(asyncio.get_event_loop().time())}",
            topic=topic,
            turns=[],
            conclusion="Simple debate completed successfully!",
            role_performances={},
            summary="Simple debate test completed - debate system is working!"
        )

        log.info("Simple debate completed")

    def start_debate(self, topic: str, roles: List[str], session_id: Optional[str] = None) -> str:
        """
        Start a new debate session.

        Args:
            topic: The debate topic
            roles: List of role names to participate
            session_id: Optional session ID, will generate one if not provided

        Returns:
            Session ID of the started debate
        """
        if session_id is None:
            session_id = f"debate_{int(asyncio.get_event_loop().time())}"

        # Store debate info for later retrieval
        if not hasattr(self, '_active_debates'):
            self._active_debates = {}

        self._active_debates[session_id] = {
            'topic': topic,
            'roles': roles,
            'started_at': asyncio.get_event_loop().time(),
            'status': 'active'
        }

        log.info(f"Started debate with session_id: {session_id}, topic: {topic}")
        return session_id

    def add_participant(self, session_id: str, role_name: str, model_name: Optional[str] = None) -> bool:
        """
        Add a participant to an existing debate.

        Args:
            session_id: Debate session ID
            role_name: Role name for the participant
            model_name: Optional model name for the role

        Returns:
            True if participant added successfully, False otherwise
        """
        if not hasattr(self, '_active_debates') or session_id not in self._active_debates:
            return False

        debate = self._active_debates[session_id]
        if 'participants' not in debate:
            debate['participants'] = []

        participant_info = {
            'role': role_name,
            'model': model_name or 'default'
        }

        debate['participants'].append(participant_info)
        log.info(f"Added participant {role_name} to debate {session_id}")
        return True

    def next_round(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Advance to the next round of debate.

        Args:
            session_id: Debate session ID

        Returns:
            Round information or None if debate doesn't exist
        """
        if not hasattr(self, '_active_debates') or session_id not in self._active_debates:
            return None

        debate = self._active_debates[session_id]
        if 'current_round' not in debate:
            debate['current_round'] = 0

        debate['current_round'] += 1

        round_info = {
            'round_number': debate['current_round'],
            'topic': debate['topic'],
            'participants': debate.get('participants', [])
        }

        log.info(f"Advanced to round {debate['current_round']} in debate {session_id}")
        return round_info

    def end_debate(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        End a debate session.

        Args:
            session_id: Debate session ID

        Returns:
            Debate summary or None if debate doesn't exist
        """
        if not hasattr(self, '_active_debates') or session_id not in self._active_debates:
            return None

        debate = self._active_debates[session_id]
        debate['status'] = 'completed'

        summary = {
            'session_id': session_id,
            'topic': debate['topic'],
            'roles': debate['roles'],
            'participants': debate.get('participants', []),
            'rounds_completed': debate.get('current_round', 0),
            'status': 'completed'
        }

        log.info(f"Ended debate {session_id}")
        return summary

    def get_debate_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a debate.

        Args:
            session_id: Debate session ID

        Returns:
            Current debate status or None if debate doesn't exist
        """
        if not hasattr(self, '_active_debates') or session_id not in self._active_debates:
            return None

        debate = self._active_debates[session_id]
        return {
            'session_id': session_id,
            'topic': debate['topic'],
            'status': debate['status'],
            'current_round': debate.get('current_round', 0),
            'participants': debate.get('participants', []),
            'started_at': debate['started_at']
        }

    @classmethod
    def create_simple_debate(cls, session_manager, role_manager, model_provider):
        """创建简化辩论实例"""
        # 创建简单的角色模型管理器模拟
        class MockRoleModelManager:
            def get_debate_model_mappings(self, roles):
                return []

        return cls(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=MockRoleModelManager(),
            model_provider=model_provider
        )

    def get_debate_model_summary(self, roles: List[str]) -> Dict[str, Any]:
        """获取辩论模型配置摘要 - 用于CLI显示"""
        return {
            'model_assignments': {
                role: self.model_provider.get_default_model() or 'default'
                for role in roles
            },
            'total_models': len(set([self.model_provider.get_default_model() or 'default'])),
            'provider_type': 'SimpleProvider'
        }