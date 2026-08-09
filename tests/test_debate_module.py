"""
多角色多模型辩论模块的TDD测试
"""

import asyncio
from unittest.mock import Mock, patch

import pytest

from src.daip_live.debate_module.clean_simple_debate import CleanSimpleDebateEngine
from src.daip_live.debate_module.core import DebateConfig, DebateCore, DebateResult
from src.daip_live.debate_module.simple_debate import SimpleDebateEngine


class TestDebateConfig:
    """测试辩论配置类"""

    def test_debate_config_creation(self):
        """测试辩论配置创建"""
        config = DebateConfig(
            topic="人工智能的伦理问题",
            roles=["专家", "质疑者"],
            rounds=3,
            max_turns_per_role=5,
        )

        assert config.topic == "人工智能的伦理问题"
        assert config.roles == ["专家", "质疑者"]
        assert config.rounds == 3
        assert config.max_turns_per_role == 5


class TestDebateCore:
    """测试辩论核心功能"""

    def test_debate_core_initialization(self):
        """测试辩论核心初始化"""
        config = DebateConfig(topic="测试话题", roles=["角色A", "角色B"], rounds=2)

        debate_core = DebateCore(config)

        assert debate_core.config == config

    async def test_run_debate_basic(self):
        """测试基本辩论运行"""
        config = DebateConfig(topic="测试话题", roles=["角色A", "角色B"], rounds=1)

        debate_core = DebateCore(config)
        result = await debate_core.run_debate()

        assert isinstance(result, DebateResult)
        assert result.topic == "测试话题"
        assert result.session_id.startswith("debate_")
        assert len(result.turns) > 0  # 应该有开始和结束事件以及发言事件
        assert result.conclusion.startswith("辩论 '测试话题' 已完成")
        # 由于可能执行时间太短，允许为0或大于0
        assert result.execution_time >= 0

    async def test_run_debate_multiple_rounds(self):
        """测试多轮辩论运行"""
        config = DebateConfig(
            topic="多轮测试话题", roles=["支持者", "反对者"], rounds=2
        )

        debate_core = DebateCore(config)
        result = await debate_core.run_debate()

        assert result.topic == "多轮测试话题"
        assert result.conclusion == "辩论 '多轮测试话题' 已完成，共进行了 2 轮"
        # 检查事件流是否正确
        start_event = next(e for e in result.turns if e["type"] == "start")
        assert start_event["rounds"] == 2
        assert start_event["topic"] == "多轮测试话题"

        # 确保每轮每个角色都有发言
        turn_events = [e for e in result.turns if e["type"] == "turn_complete"]
        assert len(turn_events) == 4  # 2轮 * 2角色

    async def test_stream_events(self):
        """测试事件流输出"""
        config = DebateConfig(topic="流测试话题", roles=["A", "B"], rounds=1)

        debate_core = DebateCore(config)
        result = await debate_core.run_debate()

        # 模拟流输出
        events = []
        async for event in debate_core.stream_events(result):
            events.append(event)

        # 应该至少有完成事件
        assert len(events) >= 1
        assert events[-1]["type"] == "complete"


class TestSimpleDebateEngine:
    """测试简单辩论引擎"""

    @pytest.fixture
    def debate_engine(self):
        """辩论引擎测试夹具"""
        return SimpleDebateEngine()

    async def test_start_debate_with_config(self):
        """测试使用配置开始辩论"""
        debate_engine = SimpleDebateEngine()

        # 直接测试引擎功能
        debate_events = []
        async for event in debate_engine.run_debate(
            "测试辩论主题", ["角色1", "角色2"], rounds=2
        ):
            debate_events.append(event)

        # 验证开始事件
        start_events = [
            e for e in debate_events if hasattr(e, "type") and e.type == "debate_start"
        ]
        assert len(start_events) == 1
        assert start_events[0].topic == "测试辩论主题"
        assert len(start_events[0].roles) == 2

        # 验证完成事件
        complete_events = [
            e
            for e in debate_events
            if hasattr(e, "type") and e.type == "debate_complete"
        ]
        assert len(complete_events) == 1
        assert complete_events[0].session_id.startswith("simple_debate_")

    async def test_debate_with_multiple_roles(self):
        """测试多角色辩论"""
        debate_engine = SimpleDebateEngine()

        debate_events = []
        async for event in debate_engine.run_debate(
            "多角色辩论", ["支持者", "反对者", "中立者"], rounds=1
        ):
            debate_events.append(event)

        # 验证发言事件
        turn_events = [
            e
            for e in debate_events
            if hasattr(e, "type") and e.type == "debate_turn_complete"
        ]
        assert len(turn_events) == 3  # 3个角色，每角色1次发言
        # 检查每个角色都有发言
        role_names = [e.participant for e in turn_events]
        assert "支持者" in role_names
        assert "反对者" in role_names
        assert "中立者" in role_names


class TestCleanSimpleDebateEngine:
    """测试清理后的简单辩论引擎"""

    def test_clean_debate_engine_initialization(self):
        """测试清理后辩论引擎的初始化"""
        debate = CleanSimpleDebateEngine()
        # 初始化不抛出异常
        assert debate is not None


class TestDebateIntegration:
    """辩论模块集成测试"""

    async def test_role_model_integration(self):
        """测试角色模型集成"""
        # 模拟角色模型管理器和模型提供者
        with (
            patch(
                "src.daip_live.p4_role_manager_tools.role_model_manager.RoleModelManager"
            ) as mock_role_manager,
            patch("src.daip_live.model_provider.provider.LiteLLMProvider"),
        ):
            # 配置模拟对象
            mock_mapping = Mock()
            mock_mapping.role_model_config = Mock()
            mock_mapping.role_model_config.model_name = "gpt-3.5-turbo"
            mock_mapping.role_model_config.temperature = 0.7
            mock_mapping.role_model_config.max_tokens = 150

            mock_role_manager.get_role_model_mapping.return_value = mock_mapping

            # 创建配置
            config = DebateConfig(
                topic="集成测试话题", roles=["专家", "新手"], rounds=1
            )

            debate_core = DebateCore(config)
            result = await debate_core.run_debate()

            # 验证结果
            assert result.topic == "集成测试话题"
            assert result.conclusion.startswith("辩论 '集成测试话题' 已完成")


# 异步测试运行器
async def run_all_async_tests():
    """运行所有异步测试"""
    test_instance = TestDebateCore()

    await test_instance.test_run_debate_basic()
    await test_instance.test_run_debate_multiple_rounds()
    await test_instance.test_stream_events()

    simple_test = TestSimpleDebateEngine()
    await simple_test.test_start_debate_with_config()
    await simple_test.test_debate_with_multiple_roles()

    integration_test = TestDebateIntegration()
    await integration_test.test_role_model_integration()


def test_sync_runner():
    """同步测试运行器"""
    # 运行同步测试
    test_config = TestDebateConfig()
    test_config.test_debate_config_creation()

    test_core = TestDebateCore()
    test_core.test_debate_core_initialization()

    # 运行异步测试
    asyncio.run(run_all_async_tests())


if __name__ == "__main__":
    test_sync_runner()
