"""
Phase 1 (Wave 0) 红测试：调试绕过移除 + 角色映射缺失必须报错

TDD 原则：先写失败测试（红），再实现修复（绿）。
目标行为（对照 docs/plans/true_state_assessment.md §5 Wave 0 项 2）：
- 模型可用性检查必须真实执行，检查失败时辩论中止（raise ModelError）
- 角色映射缺失/不完整/含 None 项时必须 raise ValueError，而非静默创建默认映射
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from daip_live.core.exceptions import ModelError
from daip_live.core.models import AgentState, Session
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig
from daip_live.p4_role_manager_tools.role_model_manager import (
    RoleModelManager,
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager


def _build_manager(role_model_manager):
    """构造最小依赖的优化架构 EnhancedDebateManager。"""
    mock_session_manager = Mock(spec=SessionManager)
    mock_session = Mock(spec=Session)
    mock_session.session_id = "bypass_test_001"
    mock_session.history = []
    mock_session.status = AgentState.RUNNING
    mock_session.summary = None
    mock_session_manager.create_session.return_value = mock_session
    mock_session_manager.save_session.return_value = None

    mock_role_manager = Mock(spec=RoleManager)
    mock_model_provider = Mock(spec=LiteLLMProvider)

    # 对齐真实契约：LiteLLMProvider.generate 是 async generator（yield 内容块，模型名由 ProviderConfig 持有）  # noqa: E501
    async def _fake_generate(prompt, params=None):
        yield "content"

    mock_model_provider.generate = _fake_generate

    return EnhancedDebateManager(
        session_manager=mock_session_manager,
        role_manager=mock_role_manager,
        role_model_manager=role_model_manager,
        model_provider=mock_model_provider,
    )


def _valid_mapping(role_name, model_name="test-model"):
    """构造有效 RoleModelMapping mock。"""
    config = Mock(spec=RoleModelConfig)
    config.model_name = model_name
    config.provider = "local"
    config.temperature = 0.7
    config.max_tokens = 1000
    config.top_p = 0.9
    config.frequency_penalty = 0.1
    config.presence_penalty = 0.1
    mapping = Mock()
    mapping.role_name = role_name
    mapping.role_model_config = config
    mapping.priority = 1
    return mapping


class TestDebugBypassRemoved:
    """调试绕过（is_model_ok = True 硬编码）必须被真实模型检查取代。"""

    @pytest.mark.asyncio
    async def test_model_check_failure_raises_model_error(self):
        """模型可用性检查失败时，辩论必须中止并 raise ModelError。"""
        role_model_manager = Mock(spec=RoleModelManager)
        role_model_manager.get_debate_model_mappings.return_value = [
            _valid_mapping("pro_arguer"),
            _valid_mapping("con_arguer"),
        ]
        manager = _build_manager(role_model_manager)

        with patch(
            "daip_live.p8_debate_system.enhanced_debate_manager.perform_model_check",
            new=AsyncMock(return_value=(False, "simulated model unavailable")),
        ):
            with pytest.raises(ModelError):
                async for _ in manager.run_debate(
                    "测试话题", ["pro_arguer", "con_arguer"], 1
                ):
                    pass

    @pytest.mark.asyncio
    async def test_healthy_path_with_available_models(self):
        """模型检查通过且映射完整时，辩论应正常产出事件（防回归保障）。"""
        role_model_manager = Mock(spec=RoleModelManager)
        role_model_manager.get_debate_model_mappings.return_value = [
            _valid_mapping("pro_arguer"),
            _valid_mapping("con_arguer"),
        ]
        manager = _build_manager(role_model_manager)

        events = []
        with patch(
            "daip_live.p8_debate_system.enhanced_debate_manager.perform_model_check",
            new=AsyncMock(return_value=(True, "ok")),
        ):
            async for event in manager.run_debate(
                "测试话题", ["pro_arguer", "con_arguer"], 1
            ):
                events.append(event)

        assert len(events) > 0


class TestRoleMappingIntegrity:
    """角色映射缺失/不完整/含无效项时必须 raise ValueError。"""

    @pytest.mark.asyncio
    async def test_incomplete_mappings_raise_value_error(self):
        """映射数量少于角色数量时 raise ValueError（当前被默认映射兜底掩盖）。"""
        role_model_manager = Mock(spec=RoleModelManager)
        role_model_manager.get_debate_model_mappings.return_value = [
            _valid_mapping("pro_arguer"),
        ]
        manager = _build_manager(role_model_manager)

        with patch(
            "daip_live.p8_debate_system.enhanced_debate_manager.perform_model_check",
            new=AsyncMock(return_value=(True, "ok")),
        ):
            with pytest.raises(ValueError):
                async for _ in manager.run_debate(
                    "测试话题", ["pro_arguer", "con_arguer"], 1
                ):
                    pass

    @pytest.mark.asyncio
    async def test_none_mapping_entry_raises_value_error(self):
        """映射列表含 None 项时 raise ValueError（当前被默认映射兜底替换）。"""
        role_model_manager = Mock(spec=RoleModelManager)
        role_model_manager.get_debate_model_mappings.return_value = [
            _valid_mapping("pro_arguer"),
            None,
        ]
        manager = _build_manager(role_model_manager)

        with patch(
            "daip_live.p8_debate_system.enhanced_debate_manager.perform_model_check",
            new=AsyncMock(return_value=(True, "ok")),
        ):
            with pytest.raises(ValueError):
                async for _ in manager.run_debate(
                    "测试话题", ["pro_arguer", "con_arguer"], 1
                ):
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
