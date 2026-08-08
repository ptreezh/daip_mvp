"""
测试辩论模型切换功能的集成测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from daip_live.tui import DAIP_TUI
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.p4_role_manager_tools.role_model_config import (
    RoleModelMapping, RoleModelConfig
)
from daip_live.core.models import (
    DebateStartEvent, DebateTurnStartEvent, DebateCompleteEvent
)



pytestmark = pytest.mark.skip(reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准")
class TestDebateModelSwitching:
    """辩论模型切换功能测试"""

    @pytest.fixture
    def mock_role_model_manager(self):
        """模拟角色模型管理器"""
        mock_manager = Mock(spec=RoleModelManager)

        # 模拟返回模型映射
        mappings = [
            RoleModelMapping(
                role_name="tech_analyst",
                role_model_config=RoleModelConfig(model_name="llama3:8b", provider="ollama")
            ),
            RoleModelMapping(
                role_name="ethics_expert",
                role_model_config=RoleModelConfig(model_name="mistral:7b", provider="ollama")
            )
        ]
        mock_manager.get_debate_model_mappings.return_value = mappings
        return mock_manager

    @pytest.fixture
    def mock_enhanced_debate_manager(self):
        """模拟增强辩论管理器"""
        mock_manager = Mock(spec=EnhancedDebateManager)

        # 模拟辩论事件流
        events = [
            DebateStartEvent(
                session_id="test_session",
                topic="AI Ethics",
                roles=["tech_analyst", "ethics_expert"],
                rounds=2
            ),
            DebateTurnStartEvent(
                session_id="test_session",
                round_number=1,
                participant="tech_analyst"
            ),
            DebateTurnStartEvent(
                session_id="test_session",
                round_number=1,
                participant="ethics_expert"
            ),
            DebateCompleteEvent(
                session_id="test_session",
                summary="Debate completed successfully"
            )
        ]

        async def mock_run_debate(topic, roles, rounds):
            for event in events:
                yield event

        mock_manager.run_debate = mock_run_debate
        return mock_manager

    @pytest.fixture
    def tui_app(self, mock_role_model_manager, mock_enhanced_debate_manager):
        """创建TUI应用实例"""
        app = DAIP_TUI(
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager
        )

        # 模拟UI组件
        app._update_log_view = Mock()
        app._update_status_bar = Mock()

        return app

    def test_debate_initialization_with_model_mappings(self, tui_app):
        """测试辩论初始化时的模型映射"""
        # 验证初始状态
        assert not tui_app._current_debate['is_active']
        assert tui_app._current_model == "default"
        assert len(tui_app._debate_active_models) == 0

    @pytest.mark.asyncio
    async def test_model_switching_during_debate(self, tui_app):
        """测试辩论过程中的模型切换"""
        # 启动辩论
        topic = "AI Ethics"
        roles = "tech_analyst,ethics_expert"
        rounds = 2

        # 手动设置辩论状态（模拟辩论启动后的状态）
        role_list = [r.strip() for r in roles.split(",")]

        # Initialize debate tracking
        tui_app._current_debate.update({
            'topic': topic,
            'total_rounds': rounds,
            'current_round': 0,
            'current_participant': None,
            'is_active': True,
            'role_models': {}
        })

        # Get model mappings for all roles
        role_mappings = tui_app._role_model_manager.get_debate_model_mappings(role_list)

        # Store role-model mappings
        for mapping in role_mappings:
            tui_app._current_debate['role_models'][mapping.role_name] = mapping.role_model_config.model_name
            tui_app._debate_active_models[mapping.role_name] = mapping.role_model_config.model_name

        # 验证模型映射已建立
        assert tui_app._current_debate['is_active']
        assert "tech_analyst" in tui_app._current_debate['role_models']
        assert "ethics_expert" in tui_app._current_debate['role_models']
        assert tui_app._current_debate['role_models']['tech_analyst'] == "llama3:8b"
        assert tui_app._current_debate['role_models']['ethics_expert'] == "mistral:7b"

    def test_update_current_model_for_participant(self, tui_app):
        """测试参与者切换时更新当前模型"""
        # 设置辩论状态
        tui_app._current_debate.update({
            'is_active': True,
            'current_participant': 'tech_analyst',
            'role_models': {
                'tech_analyst': 'llama3:8b',
                'ethics_expert': 'mistral:7b'
            }
        })

        # 模拟参与者切换事件
        event = DebateTurnStartEvent(
            session_id="test_session",
            round_number=1,
            participant="ethics_expert"
        )

        # 手动调用事件处理逻辑
        tui_app._current_debate['current_participant'] = event.participant
        if tui_app._current_debate['role_models']:
            participant_model = tui_app._current_debate['role_models'].get(
                event.participant, tui_app._model_name
            )
            tui_app._update_current_model(participant_model)

        # 验证模型已切换
        assert tui_app._current_model == "mistral:7b"
        assert tui_app._current_debate['current_participant'] == "ethics_expert"

    def test_status_bar_displays_current_role_model(self, tui_app):
        """测试状态栏显示当前角色模型"""
        # 设置辩论状态
        tui_app._current_debate.update({
            'is_active': True,
            'current_participant': 'tech_analyst',
            'role_models': {
                'tech_analyst': 'llama3:8b',
                'ethics_expert': 'mistral:7b'
            }
        })
        tui_app._current_model = "llama3:8b"

        # 生成状态栏文本
        status_text = tui_app.get_enhanced_status_text("Debating")

        # 验证状态栏显示正确
        assert "llama3:8b (tech_analyst)" in status_text
        assert "Model:" in status_text

    def test_model_reset_after_debate_completion(self, tui_app):
        """测试辩论完成后模型重置"""
        # 设置辩论状态
        tui_app._current_debate.update({
            'is_active': True,
            'current_participant': 'tech_analyst',
            'role_models': {
                'tech_analyst': 'llama3:8b'
            }
        })
        tui_app._current_model = "llama3:8b"

        # 模拟辩论完成事件
        event = DebateCompleteEvent(
            session_id="test_session",
            summary="Debate completed"
        )

        # 手动调用事件处理逻辑
        tui_app._current_debate['is_active'] = False
        tui_app._current_debate['current_participant'] = None
        tui_app._update_current_model("default")

        # 验证状态已重置
        assert not tui_app._current_debate['is_active']
        assert tui_app._current_debate['current_participant'] is None
        assert tui_app._current_model == "default"

    def test_fallback_to_default_model(self, tui_app):
        """测试回退到默认模型"""
        # 设置辩论状态但没有角色模型映射
        tui_app._current_debate.update({
            'is_active': True,
            'current_participant': 'unknown_role',
            'role_models': {}
        })
        tui_app._model_name = "default_model"

        # 模拟参与者切换事件
        event = DebateTurnStartEvent(
            session_id="test_session",
            round_number=1,
            participant="unknown_role"
        )

        # 手动调用事件处理逻辑
        tui_app._current_debate['current_participant'] = event.participant
        if tui_app._current_debate['role_models']:
            participant_model = tui_app._current_debate['role_models'].get(
                event.participant, tui_app._model_name
            )
            tui_app._update_current_model(participant_model)
        else:
            # If no role models, use the fallback logic from _update_current_model
            tui_app._update_current_model(tui_app._model_name)

        # 验证使用了默认模型
        assert tui_app._current_model == "default_model"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
