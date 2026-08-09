"""
ask 命令防回归测试

背景（2026-08-09 grill-down 实测）：`daip ask "你好"` 零用户输出、exit 0——
`_handle_conversation_intent` 消费事件后丢弃（pass），无任何用户可见回答。

修复目标：
- `_handle_conversation_intent` 必须打印 FinalResponseEvent.content（用户可见回答）
- 模型失败时必须输出错误提示而非静默吞掉
"""

from unittest.mock import MagicMock, patch

import pytest

from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType
from daip_live.cli.main import _handle_conversation_intent
from daip_live.core.models import ErrorEvent, FinalResponseEvent


def _make_intent(content: str = "你好") -> Intent:
    return Intent(
        name="chat",
        intent_type=IntentType.CHAT,
        description="chat",
        confidence=0.9,
        parameters={"chat_content": content},
    )


def _async_gen(items):
    async def _gen():
        for item in items:
            yield item

    return _gen()


@pytest.fixture
def container_mocks():
    """Mock container + agent/step_executor 依赖。"""
    agent = MagicMock()
    executor = MagicMock()
    agent.step_executor = executor
    session = MagicMock()
    agent.session_manager.create_session.return_value = session
    container = MagicMock()
    container.agent_executor.return_value = agent
    return agent, executor, container


class TestHandleConversationIntent:
    @pytest.mark.asyncio
    async def test_chat_intent_produces_visible_output(self, capsys, container_mocks):
        """chat 意图必须打印 FinalResponseEvent.content（用户可见回答）。"""
        agent, executor, container = container_mocks
        executor.execute_step.return_value = _async_gen(
            [FinalResponseEvent(content="你好！有什么可以帮你？")]
        )

        with patch("daip_live.cli.main.container", container):
            await _handle_conversation_intent(_make_intent())

        captured = capsys.readouterr()
        assert "你好！有什么可以帮你？" in captured.out
        executor.execute_step.assert_called_once()
        agent.session_manager.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_intent_prints_error_event(self, capsys, container_mocks):
        """ErrorEvent 必须打印错误提示。"""
        agent, executor, container = container_mocks
        executor.execute_step.return_value = _async_gen(
            [ErrorEvent(message="model unavailable")]
        )

        with patch("daip_live.cli.main.container", container):
            await _handle_conversation_intent(_make_intent())

        captured = capsys.readouterr()
        assert "model unavailable" in captured.out

    @pytest.mark.asyncio
    async def test_chat_intent_no_events_shows_fallback(self, capsys, container_mocks):
        """无任何回答事件时必须显示模型服务提示（不静默）。"""
        agent, executor, container = container_mocks
        executor.execute_step.return_value = _async_gen([])

        with patch("daip_live.cli.main.container", container):
            await _handle_conversation_intent(_make_intent())

        captured = capsys.readouterr()
        assert "未能生成回答" in captured.out
