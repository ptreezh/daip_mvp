"""
EnhancedDebateManager Dict错误修复测试
遵循TDD原则：先写失败测试，再实现修复
针对role_config.frequency_penalty应该为model_config.frequency_penalty的错误
"""

from unittest.mock import Mock

import pytest

from daip_live.core.models import AgentState, Session
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import Role, RoleManager
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig
from daip_live.p4_role_manager_tools.role_model_manager import (
    RoleModelManager,
    RoleModelMapping,
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager


class TestEnhancedDebateManagerDictError:
    """测试EnhancedDebateManager的dict属性错误"""

    @pytest.fixture
    def mock_dependencies(self):
        """创建Mock依赖"""
        mock_session_manager = Mock(spec=SessionManager)
        mock_role_manager = Mock(spec=RoleManager)
        mock_model_provider = Mock(spec=LiteLLMProvider)
        mock_role_model_manager = Mock(spec=RoleModelManager)

        # 创建mock角色
        mock_role1 = Mock(spec=Role)
        mock_role1.name = "pro_arguer"
        mock_role1.persona = "I am a pro arguer"
        mock_role1.system_prompt = "You are a pro arguer"

        mock_role2 = Mock(spec=Role)
        mock_role2.name = "con_arguer"
        mock_role2.persona = "I am a con arguer"
        mock_role2.system_prompt = "You are a con arguer"

        mock_role_manager.get_role_by_name.side_effect = lambda name: {
            "pro_arguer": mock_role1,
            "con_arguer": mock_role2,
        }.get(name)

        # 创建mock model config - 使用本地测试模型
        mock_model_config1 = Mock(spec=RoleModelConfig)
        mock_model_config1.model_name = "test-model"
        mock_model_config1.provider = "local"
        mock_model_config1.temperature = 0.7
        mock_model_config1.max_tokens = 1000
        mock_model_config1.top_p = 0.9
        mock_model_config1.frequency_penalty = 0.1
        mock_model_config1.presence_penalty = 0.1

        mock_model_config2 = Mock(spec=RoleModelConfig)
        mock_model_config2.model_name = "mock-llm"
        mock_model_config2.provider = "local"
        mock_model_config2.temperature = 0.8
        mock_model_config2.max_tokens = 1200
        mock_model_config2.top_p = 0.95
        mock_model_config2.frequency_penalty = 0.2
        mock_model_config2.presence_penalty = 0.15

        # 创建mock role model mapping
        mock_mapping1 = Mock(spec=RoleModelMapping)
        mock_mapping1.role_name = "pro_arguer"
        mock_mapping1.model_config = mock_model_config1  # 注意：这里是model_config
        mock_mapping1.role_model_config = (
            mock_model_config1  # 注意：这里是role_model_config
        )
        mock_mapping1.priority = 1

        mock_mapping2 = Mock(spec=RoleModelMapping)
        mock_mapping2.role_name = "con_arguer"
        mock_mapping2.model_config = mock_model_config2  # 注意：这里是model_config
        mock_mapping2.role_model_config = (
            mock_model_config2  # 注意：这里是role_model_config
        )
        mock_mapping2.priority = 2

        mock_role_model_manager.get_debate_model_mappings.return_value = [
            mock_mapping1,
            mock_mapping2,
        ]

        # 创建mock session
        mock_session = Mock(spec=Session)
        mock_session.session_id = "test_session_001"
        mock_session.history = []
        mock_session.status = AgentState.RUNNING
        mock_session.summary = None
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.save_session.return_value = None

        return {
            "session_manager": mock_session_manager,
            "role_manager": mock_role_manager,
            "model_provider": mock_model_provider,
            "role_model_manager": mock_role_model_manager,
            "mock_role1": mock_role1,
            "mock_role2": mock_role2,
            "mock_session": mock_session,
            "mock_mapping1": mock_mapping1,
            "mock_mapping2": mock_mapping2,
        }

    def test_legacy_mode_role_config_attribute_error_fixed(self, mock_dependencies):
        """GREEN测试：验证role_config.frequency_penalty错误已被修复"""
        # Arrange
        debate_manager = EnhancedDebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            role_model_manager=mock_dependencies["role_model_manager"],
            model_provider=mock_dependencies["model_provider"],
            use_optimized_architecture=False,  # 使用legacy模式
        )

        # Mock model_provider.generate返回值 - 现在使用正确的provider
        mock_content = "This is my argument"
        mock_usage = {"total_tokens": 100}

        # 设置mock以返回正确的结果
        async def mock_generate(*args, **kwargs):
            # 验证传入的参数包含正确的model
            assert "model" in kwargs
            model = kwargs["model"]
            assert model in ["test-model", "mock-llm"]
            return mock_content, mock_usage

        mock_dependencies["model_provider"].generate = mock_generate

        # Act - 这应该成功，不再抛出AttributeError
        import asyncio

        async def run_debate():
            events = []
            async for event in debate_manager.run_debate(
                topic="AI能够取代人类大部分工作",
                roles_names=["pro_arguer", "con_arguer"],
                num_rounds=1,
            ):
                events.append(event)
            return events

        # 验证debate成功运行，没有AttributeError
        events = asyncio.run(run_debate())

        # Assert - 验证辩论成功完成
        assert len(events) > 0
        # 验证不再有role_config相关的错误

    def test_role_model_mapping_has_correct_attributes(self, mock_dependencies):
        """GREEN测试：验证RoleModelMapping有正确的属性"""
        mapping = mock_dependencies["mock_mapping1"]

        # 这些属性应该存在
        assert hasattr(mapping, "role_name")
        assert hasattr(mapping, "model_config")
        assert hasattr(mapping, "role_model_config")
        assert hasattr(mapping, "priority")

        # role_config不应该存在（这是错误的属性名）
        assert not hasattr(mapping, "role_config")

        # 验证model_config有frequency_penalty属性
        assert hasattr(mapping.model_config, "frequency_penalty")
        assert hasattr(mapping.model_config, "presence_penalty")
        assert hasattr(mapping.role_model_config, "frequency_penalty")
        assert hasattr(mapping.role_model_config, "presence_penalty")

    def test_enhanced_debate_manager_creation(self, mock_dependencies):
        """测试EnhancedDebateManager创建"""
        debate_manager = EnhancedDebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            role_model_manager=mock_dependencies["role_model_manager"],
            model_provider=mock_dependencies["model_provider"],
        )

        assert debate_manager is not None
        assert isinstance(debate_manager, EnhancedDebateManager)
        assert debate_manager.use_optimized_architecture is True

    def test_legacy_mode_debate_manager_creation(self, mock_dependencies):
        """测试legacy模式EnhancedDebateManager创建"""
        debate_manager = EnhancedDebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            role_model_manager=mock_dependencies["role_model_manager"],
            model_provider=mock_dependencies["model_provider"],
            use_optimized_architecture=False,
        )

        assert debate_manager is not None
        assert isinstance(debate_manager, EnhancedDebateManager)
        assert debate_manager.use_optimized_architecture is False

    def test_legacy_mode_fixed_role_config_error(self, mock_dependencies):
        """GREEN测试：验证修复后的legacy模式能正常工作"""
        # Arrange
        debate_manager = EnhancedDebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            role_model_manager=mock_dependencies["role_model_manager"],
            model_provider=mock_dependencies["model_provider"],
            use_optimized_architecture=False,  # 使用legacy模式
        )

        # Mock model_provider.generate返回值
        mock_content = "This is my argument"
        mock_usage = {"total_tokens": 100}
        mock_dependencies["model_provider"].generate.return_value = (
            mock_content,
            mock_usage,
        )

        # Act - 这应该不再抛出AttributeError
        import asyncio

        async def run_debate():
            events = []
            async for event in debate_manager.run_debate(
                topic="AI能够取代人类大部分工作",
                roles_names=["pro_arguer", "con_arguer"],
                num_rounds=1,
            ):
                events.append(event)
            return events

        events = asyncio.run(run_debate())

        # Assert - 验证辩论成功完成
        assert len(events) > 0
        # 应该有辩论开始事件
        start_events = [e for e in events if hasattr(e, "topic")]
        assert len(start_events) > 0

        # 应该有辩论完成事件
        complete_events = [e for e in events if hasattr(e, "summary")]
        assert len(complete_events) > 0

        # 验证没有错误发生
        error_events = [
            e
            for e in events
            if hasattr(e, "message") and "error" in str(type(e)).lower()
        ]
        assert len(error_events) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
