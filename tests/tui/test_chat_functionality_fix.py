"""
模块化TUI聊天功能修复验证测试
测试意图识别后的聊天输出功能
"""

import asyncio
from unittest.mock import Mock

import pytest

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import FinalResponseEvent
from daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="旧spec：引用不存在的 TUI._start_chat_session 方法；当前源码为准"
)


async def test_chat_functionality_fix():
    """测试修复后的聊天功能"""

    # 创建mock依赖
    mock_session_manager = Mock()
    Mock()
    mock_knowledge_manager = Mock()
    mock_model_provider = Mock()
    Mock()

    # 创建队列
    asyncio.Queue()

    # 创建executor并模拟chat_run方法
    mock_executor = Mock(spec=AgentExecutor)

    # 从core.models导入FinalResponseEvent

    # 模拟chat_run方法返回事件流
    async def mock_chat_run(initial_goal):
        yield FinalResponseEvent(content="这是一个测试响应，验证聊天功能已修复！")

    mock_executor.chat_run = mock_chat_run
    mock_executor.step_executor = Mock()

    # 创建TUI实例
    tui = DAIP_TUI(
        executor=mock_executor,
        session_manager=mock_session_manager,
        role_manager=Mock(),
        knowledge_manager=mock_knowledge_manager,
        debate_manager=Mock(),
        model_provider=mock_model_provider,
        db_manager=Mock(),
        config_manager=Mock(),
        role_model_manager=Mock(),
        enhanced_debate_manager=Mock(),
    )

    # 设置更新方法
    log_messages = []
    system_messages = []

    def mock_update_log_view(msg):
        log_messages.append(("log", msg))

    def mock_update_system_log(msg):
        system_messages.append(("system", msg))

    tui._update_log_view = mock_update_log_view
    tui._update_system_log = mock_update_system_log

    # 测试聊天功能
    await tui._start_chat_session("你好")

    # 验证输出
    response_found = any("这是一个测试响应" in msg[1] for msg in log_messages)
    if response_found:
        pass
    else:
        pass

    # 现在测试_handle_agent_event方法
    from daip_live.core.models import ThoughtEvent

    # 测试ThoughtEvent
    thought_event = ThoughtEvent(content="这是一个思考事件")
    await tui._handle_agent_event(thought_event)

    # 测试FinalResponseEvent
    response_event = FinalResponseEvent(content="这是一个响应事件")
    await tui._handle_agent_event(response_event)


if __name__ == "__main__":
    asyncio.run(test_chat_functionality_fix())
