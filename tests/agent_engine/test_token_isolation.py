"""
Token usage isolation test - 第一性原理验证 token 积累机制
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import TodoItem

pytestmark = pytest.mark.asyncio


@pytest.fixture
def isolated_agent_executor():
    """创建完全隔离的 AgentExecutor 用于 token 测试"""
    # 创建所有必要的 mock 对象
    session_manager = MagicMock()
    memory_service = AsyncMock()
    knowledge_manager = AsyncMock()
    model_provider = AsyncMock()
    tool_manager = AsyncMock()
    user_input_queue = asyncio.Queue()

    # 设置 tool_manager 的 _registry 属性
    tool_manager._registry = {
        "search_web": MagicMock(),
    }

    # 配置 memory service
    memory_service.get_todo_list.return_value = [
        TodoItem(id=1, description="test task", status="pending", priority=1)
    ]
    memory_service.is_todo_list_complete.side_effect = [False, True]
    memory_service.update_todo_status = AsyncMock()

    agent = AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
    )

    return agent


async def test_token_update_isolation_test(isolated_agent_executor):
    """
    隔离测试：验证 state_manager 的 token 更新机制
    """
    agent = isolated_agent_executor

    # 验证初始 token 计数为 0
    assert agent.state_manager.tokens_used == 0

    # 模拟两次 generate 调用，每次返回 100 tokens
    usage_dict = {"total_tokens": 100}
    agent.model_provider.generate.side_effect = [
        ("Use Tool: search_web(query='test')", usage_dict),
        ("Final Answer.", usage_dict)
    ]

    # 配置工具管理器，使 search_web 工具可用
    agent.tool_manager.execute_tool = MagicMock(return_value="mock result")

    # 执行 agent
    events = [event async for event in agent.run("test task")]

    # 验证最终的 token 计数
    print(f"Final tokens used: {agent.state_manager.tokens_used}")
    print(f"Model provider call count: {agent.model_provider.generate.call_count}")

    # 检查是否有 TokenUsageEvent
    token_events = [e for e in events if hasattr(e, 'usage_info')]
    print(f"Token usage events: {len(token_events)}")
    for i, event in enumerate(token_events):
        print(f"  Event {i+1}: {event.usage_info}")

    # 检查工具调用事件
    tool_call_events = [e for e in events if hasattr(e, 'tool_name')]
    print(f"Tool call events: {len(tool_call_events)}")
    for i, event in enumerate(tool_call_events):
        print(f"  Tool Event {i+1}: {event.tool_name}")

    # 这应该通过，但实际可能会失败
    assert agent.state_manager.tokens_used == 200


async def test_state_manager_direct_update(isolated_agent_executor):
    """
    直接测试 StateManager 的 token 更新功能
    """
    state_manager = isolated_agent_executor.state_manager

    # 验证初始状态
    assert state_manager.tokens_used == 0

    # 直接调用 token 更新方法
    state_manager.update_tokens(100)
    assert state_manager.tokens_used == 100

    # 再次调用
    state_manager.update_tokens(100)
    assert state_manager.tokens_used == 200

    print("StateManager token update works correctly")