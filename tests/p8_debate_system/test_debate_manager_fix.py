"""
辩论系统DialogueTurn验证错误修复测试
遵循TDD原则：先写失败测试，再实现修复
"""

from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from daip_live.core.models import AgentState, DialogueTurn, Session
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager


class TestDebateManagerReturnType:
    """测试DebateManager的返回类型处理问题"""

    @pytest.fixture
    def mock_dependencies(self):
        """创建Mock依赖"""
        mock_session_manager = Mock(spec=SessionManager)
        mock_role_manager = Mock(spec=RoleManager)
        mock_model_provider = Mock(spec=LiteLLMProvider)

        # 创建mock角色
        mock_role1 = Mock()
        mock_role1.name = "pro_arguer"
        mock_role1.persona = "I am a pro arguer"

        mock_role2 = Mock()
        mock_role2.name = "con_arguer"
        mock_role2.persona = "I am a con arguer"

        mock_role_manager.get_role_by_name.side_effect = lambda name: {
            "pro_arguer": mock_role1,
            "con_arguer": mock_role2,
        }.get(name)

        # 创建mock session
        mock_session = Mock(spec=Session)
        mock_session.session_id = "test_session_001"
        mock_session.history = []
        mock_session.status = AgentState.RUNNING
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.save_session.return_value = None

        return {
            "session_manager": mock_session_manager,
            "role_manager": mock_role_manager,
            "model_provider": mock_model_provider,
            "mock_role1": mock_role1,
            "mock_role2": mock_role2,
            "mock_session": mock_session,
        }

    def test_generate_returns_tuple_handling_works(self, mock_dependencies):
        pytest.skip(
            "旧spec：源码 generate 已是 async generator（provider.py:276），tuple 返回契约不存在；当前源码为准"  # noqa: E501
        )
        """GREEN测试：验证model_provider.generate返回tuple时能正确处理"""
        # Arrange
        debate_manager = DebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            model_provider=mock_dependencies["model_provider"],
        )

        # Mock model_provider.generate返回Tuple[str, Any] (这是实际行为)
        mock_content = "This is my argument"
        mock_usage = {"total_tokens": 100}
        mock_dependencies["model_provider"].generate.return_value = (
            mock_content,
            mock_usage,
        )

        # Act - 这应该成功，因为DebateManager正确处理了tuple返回值
        import asyncio

        async def run_debate_and_collect_events():
            events = []
            async for event in debate_manager.run_debate(
                topic="AI能够取代人类大部分工作",
                roles_names=["pro_arguer", "con_arguer"],
                num_rounds=1,
            ):
                events.append(event)
            return events

        # 验证debate成功运行，没有ValidationError
        events = asyncio.run(run_debate_and_collect_events())

        # Assert - 验证辩论成功完成
        assert len(events) > 0
        # 验证没有validation error发生

    def test_direct_dialogue_turn_creation_with_tuple_fails(self):
        """RED测试：直接创建DialogueTurn时传入tuple应该失败"""
        from daip_live.core.models import DialogueTurn

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            # 直接传入tuple应该失败
            DialogueTurn(
                participant_id="test_role",
                content=("tuple content", {"metadata": "data"}),  # 传入tuple而不是str
            )

        # 验证错误信息
        error_message = str(exc_info.value)
        assert "validation error" in error_message.lower()
        assert "string_type" in error_message.lower()

    def test_dialogue_turn_accepts_string_content(self):
        """RED测试：验证DialogueTurn可以接受正常的字符串内容"""
        # 这个测试应该通过，证明DialogueTurn本身工作正常
        turn = DialogueTurn(
            participant_id="test_role", content="This is a valid string content"
        )

        assert turn.participant_id == "test_role"
        assert turn.content == "This is a valid string content"
        assert isinstance(turn.content, str)

    def test_dialogue_turn_rejects_none_content(self):
        """RED测试：验证DialogueTurn拒绝None内容"""
        with pytest.raises(ValueError) as exc_info:
            DialogueTurn(participant_id="test_role", content=None)

        assert "content" in str(exc_info.value).lower()

    def test_debate_manager_fixed_tuple_unpacking(self, mock_dependencies):
        pytest.skip(
            "旧spec：源码 generate 已是 async generator（provider.py:276），tuple 返回契约不存在；当前源码为准"  # noqa: E501
        )
        """GREEN测试：验证修复后的DebateManager能正确处理tuple返回值"""
        # Arrange
        debate_manager = DebateManager(
            session_manager=mock_dependencies["session_manager"],
            role_manager=mock_dependencies["role_manager"],
            model_provider=mock_dependencies["model_provider"],
        )

        # Mock model_provider.generate返回Tuple[str, Any]
        mock_content = "This is my argument"
        mock_usage = {"total_tokens": 100}
        mock_dependencies["model_provider"].generate.return_value = (
            mock_content,
            mock_usage,
        )

        # Act - 这应该不再抛出ValidationError
        import asyncio

        async def run_debate_and_get_session():
            # Track the session that would be created and updated
            mock_session = mock_dependencies[
                "session_manager"
            ].create_session.return_value

            async for event in debate_manager.run_debate(
                topic="AI能够取代人类大部分工作",
                roles_names=["pro_arguer", "con_arguer"],
                num_rounds=1,
            ):
                pass  # Just run through all events

            return mock_session

        result_session = asyncio.run(run_debate_and_get_session())

        # Assert - 验证辩论成功完成
        assert result_session.status == AgentState.COMPLETED
        assert len(result_session.history) == 2  # 两个角色各发言一次
        assert result_session.history[0].content == mock_content
        assert result_session.history[1].content == mock_content
        assert result_session.summary is not None

        # 验证session_manager.save_session被调用
        mock_dependencies["session_manager"].save_session.assert_called_once()


class TestDebateManagerIntegration:
    """辩论管理器集成测试"""

    @pytest.fixture
    def debate_manager_with_mocks(self):
        """创建带有Mock的辩论管理器"""
        mock_session_manager = Mock(spec=SessionManager)
        mock_role_manager = Mock(spec=RoleManager)
        mock_model_provider = Mock(spec=LiteLLMProvider)

        debate_manager = DebateManager(
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            model_provider=mock_model_provider,
        )

        return (
            debate_manager,
            mock_session_manager,
            mock_role_manager,
            mock_model_provider,
        )

    def test_debate_manager_creation(self, debate_manager_with_mocks):
        """测试辩论管理器创建"""
        debate_manager, _, _, _ = debate_manager_with_mocks
        assert debate_manager is not None
        assert isinstance(debate_manager, DebateManager)

    def test_debate_manager_dependencies(self, debate_manager_with_mocks):
        """测试辩论管理器依赖注入"""
        debate_manager, session_manager, role_manager, model_provider = (
            debate_manager_with_mocks
        )

        assert debate_manager.session_manager is session_manager
        assert debate_manager.role_manager is role_manager
        assert debate_manager.model_provider is model_provider


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
