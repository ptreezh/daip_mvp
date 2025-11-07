"""
RoleDebateSession测试用例
测试角色独立辩论会话功能
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig


class TestRoleDebateSession:
    """角色独立辩论会话测试"""

    def test_role_session_initialization(self):
        """测试角色会话初始化"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        # 创建测试配置
        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        # Create role config (this was just for testing, not used by RoleDebateSession)

        # 创建角色会话
        session = RoleDebateSession(
            role_name="test_role",
            role_persona="You are a test role",
            model_config=model_config,
            system_prompt="Test system prompt"
        )

        # 验证初始化
        assert session.role_name == "test_role"
        assert session.role_persona == "You are a test role"
        assert session.model_config == model_config
        assert session.system_prompt == "Test system prompt"
        assert len(session.personal_history) == 0
        assert len(session.stance_memory) == 0
        assert len(session.argument_tracker) == 0
        assert len(session.round_memories) == 0

    def test_add_personal_history(self):
        """测试添加个人历史"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 添加历史记录
        session.add_personal_history(
            round_num=1,
            content="This is my argument for round 1",
            opponent_summary="Opponent argued about technology"
        )

        # 验证历史记录
        assert len(session.personal_history) == 1
        assert session.personal_history[0]["round"] == 1
        assert session.personal_history[0]["content"] == "This is my argument for round 1"
        assert session.personal_history[0]["opponent_summary"] == "Opponent argued about technology"

    def test_update_stance_memory(self):
        """测试立场记忆更新"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 更新核心立场
        session.update_stance_memory("core_stance", "I believe technology is beneficial")
        session.update_stance_memory("key_arguments", ["Technology improves efficiency", "AI creates new opportunities"])

        # 验证立场记忆
        assert session.stance_memory["core_stance"] == "I believe technology is beneficial"
        assert len(session.stance_memory["key_arguments"]) == 2
        assert "Technology improves efficiency" in session.stance_memory["key_arguments"]

    def test_track_arguments(self):
        """测试论点追踪"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 追踪论点
        session.track_argument(
            round_num=1,
            argument_type="main",
            content="Technology creates economic growth",
            strength=0.8
        )
        session.track_argument(
            round_num=1,
            argument_type="rebuttal",
            content="But we must consider job displacement",
            strength=0.6
        )

        # 验证论点追踪
        assert len(session.argument_tracker) == 1
        assert session.argument_tracker[1]["main"]["content"] == "Technology creates economic growth"
        assert session.argument_tracker[1]["main"]["strength"] == 0.8
        assert session.argument_tracker[1]["rebuttal"]["content"] == "But we must consider job displacement"

    def test_add_round_memory(self):
        """测试轮次记忆"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 添加轮次记忆
        session.add_round_memory(
            round_num=1,
            summary="In round 1, we discussed the economic impact",
            key_points=["Economic growth", "Job creation"],
            opponent_arguments=["Technology causes unemployment"]
        )

        # 验证轮次记忆
        assert session.round_memories[1]["summary"] == "In round 1, we discussed the economic impact"
        assert len(session.round_memories[1]["key_points"]) == 2
        assert "Economic growth" in session.round_memories[1]["key_points"]
        assert session.round_memories[1]["opponent_arguments"] == ["Technology causes unemployment"]

    def test_get_context_summary(self):
        """测试获取上下文摘要"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="You are a technology analyst",
            model_config=model_config
        )

        # 添加一些历史数据
        session.add_personal_history(1, "Technology drives innovation", "Opponent focuses on risks")
        session.update_stance_memory("core_stance", "Technology is fundamentally beneficial")
        session.add_round_memory(1, "Discussed economic impacts", ["Growth", "Innovation"], ["Job loss"])

        # 获取上下文摘要
        context = session.get_context_summary(current_round=2)

        assert "Role: You are a technology analyst" in context
        assert "Core Stance: Technology is fundamentally beneficial" in context
        assert "Round 1 Summary" in context
        assert "Previous Arguments:" in context

    @pytest.mark.asyncio
    async def test_build_context_aware_prompt(self):
        """测试构建上下文感知提示词"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="tech_analyst",
            role_persona="You are a technology analyst who believes in progress",
            model_config=model_config,
            system_prompt="Focus on technological advancement"
        )

        # 添加历史数据
        session.add_personal_history(1, "AI will transform industries", "Opponent worried about ethics")
        session.update_stance_memory("core_stance", "Technological progress is inevitable and beneficial")

        # 构建提示词
        prompt = session.build_context_aware_prompt(
            topic="Artificial Intelligence in healthcare",
            current_round=2
        )

        # 验证提示词内容
        assert "Debate Topic: Artificial Intelligence in healthcare" in prompt
        assert "Current Round: 2" in prompt
        assert "Your Role: You are a technology analyst who believes in progress" in prompt
        assert "Your Assigned Model: test_model" in prompt
        assert "Your Previous Arguments:" in prompt
        assert "AI will transform industries" in prompt
        assert "Your Core Stance: Technological progress is inevitable and beneficial" in prompt
        assert "Opponent Arguments Summary:" in prompt
        assert "Opponent worried about ethics" in prompt

    def test_memory_lifecycle(self):
        """测试记忆生命周期"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 完整的记忆生命周期
        # 1. 添加历史
        session.add_personal_history(1, "First argument", "Opponent response")

        # 2. 更新立场
        session.update_stance_memory("position", "Pro-technology")

        # 3. 追踪论点
        session.track_argument(1, "main", "Technology benefits society", 0.9)

        # 4. 添加轮次记忆
        session.add_round_memory(1, "Initial discussion", ["Benefits"], ["Risks"])

        # 5. 添加第二轮数据
        session.add_personal_history(2, "Refined argument", "Opponent counter")
        session.track_argument(2, "rebuttal", "Benefits outweigh risks", 0.8)
        session.add_round_memory(2, "Deeper analysis", ["Evidence"], ["Concerns"])

        # 验证完整状态
        assert len(session.personal_history) == 2
        assert session.stance_memory["position"] == "Pro-technology"
        assert len(session.argument_tracker) == 2
        assert len(session.round_memories) == 2

        # 获取最终上下文
        context = session.get_context_summary(current_round=3)
        assert "Round 1 Summary" in context
        assert "Round 2 Summary" in context
        assert "Refined argument" in context

    def test_error_handling(self):
        """测试错误处理"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        session = RoleDebateSession(
            role_name="test_role",
            role_persona="Test persona",
            model_config=model_config
        )

        # 测试无效轮次
        with pytest.raises(ValueError):
            session.get_context_summary(current_round=0)

        # 测试空状态
        empty_context = session.get_context_summary(current_round=1)
        assert "Role: Test persona" in empty_context
        assert "No previous arguments" in empty_context

    def test_session_isolation(self):
        """测试会话隔离性"""
        from daip_live.p8_debate_system.role_debate_session import RoleDebateSession
        from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig

        model_config = RoleModelConfig(
            model_name="test_model",
            provider="ollama",
            max_tokens=4000,
            temperature=0.7
        )

        # 创建两个独立会话
        session1 = RoleDebateSession(
            role_name="tech_expert",
            role_persona="Technology expert",
            model_config=model_config
        )

        session2 = RoleDebateSession(
            role_name="ethics_expert",
            role_persona="Ethics expert",
            model_config=model_config
        )

        # 分别添加数据
        session1.add_personal_history(1, "Technology is progress", "Ethics concerns raised")
        session1.update_stance_memory("core_stance", "Pro-technology")

        session2.add_personal_history(1, "Ethics must guide technology", "Progress arguments made")
        session2.update_stance_memory("core_stance", "Pro-ethics")

        # 验证隔离性
        assert session1.role_name == "tech_expert"
        assert session2.role_name == "ethics_expert"
        assert session1.stance_memory["core_stance"] == "Pro-technology"
        assert session2.stance_memory["core_stance"] == "Pro-ethics"
        assert session1.personal_history[0]["content"] == "Technology is progress"
        assert session2.personal_history[0]["content"] == "Ethics must guide technology"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])