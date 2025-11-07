import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import FinalResponseEvent, ToolCallEvent, ToolOutputEvent
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p4_role_manager_tools.tools import tool

pytestmark = pytest.mark.asyncio

# 1. Define a real tool for testing
@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

# 2. Setup fixtures for the integration test
@pytest.fixture
def real_tool_manager() -> ToolManager:
    """Creates a ToolManager with the real 'add' tool registered."""
    manager = ToolManager()
    manager.register_tool(add)
    return manager

@pytest.fixture
def integrated_agent_executor(real_tool_manager) -> AgentExecutor:
    """
    Creates an AgentExecutor with a real ToolManager but mocked
    downstream services (memory, model provider).
    """
    return AgentExecutor(
        session_manager=MagicMock(),
        memory_service=AsyncMock(),
        knowledge_manager=AsyncMock(),
        model_provider=AsyncMock(),
        tool_manager=real_tool_manager,
        user_input_queue=asyncio.Queue(),
    )

# 3. Write the integration test case
async def test_agent_executes_real_tool_via_tool_manager(integrated_agent_executor):
    """
    Integration test to verify AgentExecutor can successfully call a real tool
    through a real ToolManager.
    """
    # Arrange
    agent = integrated_agent_executor
    agent.tool_manager.tool_permission_config.tools['add'] = 'allow'
    
    # Configure memory service mock
    from daip_live.core.models import TodoItem
    agent.memory_service.construct_prompt = AsyncMock(return_value="mocked prompt")
    agent.memory_service.get_todo_list = AsyncMock(return_value=[TodoItem(id=1, description="test", status="pending", priority=1)])
    agent.memory_service.is_todo_list_complete = AsyncMock(side_effect=[False, True])
    agent.memory_service.update_todo_status = AsyncMock()

    # Mock the model_provider to simulate an LLM deciding to use the 'add' tool
    agent.model_provider.generate.side_effect = [
        ("I need to add two numbers. Use Tool: add(a=5, b=10) Confidence: 0.99", {}),
        ("The result of the addition is 15. Confidence: 0.99", {})
    ]

    # Act
    events = [event async for event in agent.run("What is 5 + 10?")]

    # Assert
    # Verify that the ToolCallEvent was emitted correctly
    tool_call_event = next(e for e in events if isinstance(e, ToolCallEvent))
    assert tool_call_event.tool_name == "add"
    assert tool_call_event.args == {'a': 5, 'b': 10}

    # Verify that the ToolOutputEvent contains the *actual* result of add(5, 10)
    tool_output_event = next(e for e in events if isinstance(e, ToolOutputEvent))
    assert tool_output_event.status == "success"
    assert tool_output_event.output == '15'  # 5 + 10 = 15

    # Verify the final response incorporates the tool's output
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert "15" in final_response.content

    # Verify the model provider was called twice (initial call, and call after getting tool result)
    assert agent.model_provider.generate.call_count == 2
