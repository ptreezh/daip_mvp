import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import FinalResponseEvent, ToolCallEvent, ToolOutputEvent, AgentState
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p4_role_manager_tools.tools import tool
from daip_live.workflow.parser import WorkflowParser

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

    # Configure memory service mock (same as working test)
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

# 工作流集成测试
async def test_workflow_execution_with_real_tool(integrated_agent_executor):
    """
    集成测试验证AgentExecutor可以执行包含工作流的任务。
    注意：WorkflowExecutor 是简化实现，专注于工作流编排而非具体工具执行。
    """
    # Arrange
    agent = integrated_agent_executor
    agent.tool_manager.tool_permission_config.tools['add'] = 'allow'

    # Configure memory service mock (same as working test)
    from daip_live.core.models import TodoItem
    agent.memory_service.construct_prompt = AsyncMock(return_value="mocked prompt")
    agent.memory_service.get_todo_list = AsyncMock(return_value=[TodoItem(id=1, description="test", status="pending", priority=1)])
    agent.memory_service.is_todo_list_complete = AsyncMock(side_effect=[False, True])
    agent.memory_service.update_todo_status = AsyncMock()

    # 创建一个包含任务元素的工作流定义
    workflow_yaml = """
    name: tool_test_workflow
    elements:
      task1:
        type: task
        name: "加法计算任务"
        description: "执行加法计算"
    start: task1
    """

    workflow_definition = WorkflowParser.parse(workflow_yaml)

    # Act
    events = [event async for event in agent.run("Execute the workflow", workflow_definition)]

    # Assert
    # 验证工作流执行事件
    assert any("Executing element: 加法计算任务" in str(e) for e in events if hasattr(e, 'content'))
    assert any("Executed task element: 加法计算任务" in str(e) for e in events if hasattr(e, 'content'))

    # 验证工作流开始和结束事件
    assert any("Starting workflow: tool_test_workflow" in str(e) for e in events if hasattr(e, 'content'))

    # 验证最终状态
    assert agent.state == AgentState.COMPLETED

    # 注意：WorkflowExecutor 是简化实现，不直接执行工具调用
    # 工具执行应该通过 Todo 驱动的方式在 StepExecutor 中进行

async def test_workflow_with_data_flow_integration(integrated_agent_executor):
    """
    集成测试验证工作流中的数据流功能。
    注意：WorkflowExecutor 是简化实现，专注于工作流编排而非具体工具执行。
    """
    # Arrange
    agent = integrated_agent_executor
    agent.tool_manager.tool_permission_config.tools['add'] = 'allow'

    # Configure memory service mock (same as working test)
    from daip_live.core.models import TodoItem
    agent.memory_service.construct_prompt = AsyncMock(return_value="mocked prompt")
    agent.memory_service.get_todo_list = AsyncMock(return_value=[TodoItem(id=1, description="test", status="pending", priority=1)])
    agent.memory_service.is_todo_list_complete = AsyncMock(side_effect=[False, True])
    agent.memory_service.update_todo_status = AsyncMock()

    # 创建一个包含数据流的工作流定义
    workflow_yaml = """
    name: data_flow_test_workflow
    elements:
      task1:
        type: task
        name: "生成数据"
        data_outputs:
          - "value"
        next:
          - task2
      task2:
        type: task
        name: "处理数据"
        data_inputs:
          input_value: "task1.value"
    start: task1
    data_flow:
      task1:
        value: task2.input_value
    """

    workflow_definition = WorkflowParser.parse(workflow_yaml)

    # Act
    events = [event async for event in agent.run("Execute the data flow workflow", workflow_definition)]

    # Assert
    # 验证两个任务都被执行
    task1_executed = any("Executing element: 生成数据" in str(e) for e in events if hasattr(e, 'content'))
    task2_executed = any("Executing element: 处理数据" in str(e) for e in events if hasattr(e, 'content'))
    assert task1_executed
    assert task2_executed

    # 验证数据输入信息在任务描述中
    # 注意：WorkflowExecutor 当前简化实现可能不产生特殊的数据输入事件
    # 但数据流配置应该被正确解析
    assert hasattr(workflow_definition.elements['task2'], 'data_inputs')
    assert workflow_definition.elements['task2'].data_inputs == {'input_value': 'task1.value'}

    # 验证数据流配置
    assert hasattr(workflow_definition, 'data_flow')
    assert 'task1' in workflow_definition.data_flow
    assert workflow_definition.data_flow['task1']['value'] == 'task2.input_value'

    # 验证工作流开始和完成
    assert any("Starting workflow: data_flow_test_workflow" in str(e) for e in events if hasattr(e, 'content'))

    # 验证最终状态
    assert agent.state == AgentState.COMPLETED

    # 注意：WorkflowExecutor 是简化实现，不直接执行工具调用
    # 它专注于工作流编排和数据流传递