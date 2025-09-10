import asyncio
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.core.models import (
    AgentState,
    AgentStatus,
    FinalResponseEvent,
    Session,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
)

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_usage():
    """Fixture for a mock litellm usage object."""
    usage = MagicMock()
    usage.total_tokens = 100
    return usage

@pytest.fixture
def mock_services():
    """Fixture to create mocked services for the AgentExecutor."""
    return {
        "session_manager": MagicMock(),
        "memory_service": AsyncMock(),
        "knowledge_manager": AsyncMock(),
        "model_provider": AsyncMock(),
        "tool_manager": MagicMock(),
    }

@pytest.fixture
def agent_executor(mock_services):
    """Fixture to create an AgentExecutor instance with mocked services."""
    mock_services["session_manager"].create_session.return_value = Session(goal="test goal", session_type="workflow", participant_ids=[])
    memory_service = mock_services["memory_service"]
    memory_service.get_todo_list.return_value = [MagicMock(description="single mock task")]
    memory_service.is_todo_list_complete.side_effect = [False, True]
    memory_service.update_todo_status.return_value = None
    return AgentExecutor(
        session_manager=mock_services["session_manager"],
        memory_service=mock_services["memory_service"],
        knowledge_manager=mock_services["knowledge_manager"],
        model_provider=mock_services["model_provider"],
        tool_manager=mock_services["tool_manager"],
        user_input_queue=asyncio.Queue(),
        max_reflections=3
    )

async def test_get_status_api(agent_executor, mock_services):
    """Tests the get_status method."""
    mock_model_config = MagicMock()
    mock_model_config.model = "test-model-123"
    type(mock_services["model_provider"]).config = PropertyMock(return_value=mock_model_config)
    agent_executor.state = AgentState.THINKING
    agent_executor.tokens_used = 1024
    agent_executor.tokens_total = 8192
    status = agent_executor.get_status()
    assert isinstance(status, AgentStatus)
    assert status.state == AgentState.THINKING
    assert status.model_name == "test-model-123"
    assert status.tokens_used == 1024
    assert status.tokens_total == 8192

async def test_token_usage_is_accumulated(agent_executor, mock_services, mock_usage):
    """Tests that tokens_used is accumulated after each model call."""
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: search_web(query='test')", mock_usage),
        ("Final Answer.", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result"
    assert agent_executor.tokens_used == 0
    _ = [event async for event in agent_executor.run("test goal")]
    # 2 calls to generate, each using 100 tokens
    assert agent_executor.tokens_used == 200

async def test_high_confidence_flow(agent_executor, mock_services, mock_usage):
    """Test a direct, high-confidence response without tools."""
    mock_services["model_provider"].generate.return_value = ("Final Answer. Confidence: 0.99", mock_usage)
    events = [event async for event in agent_executor.run("test goal")]
    assert isinstance(events[0], ThoughtEvent)
    assert isinstance(events[1], FinalResponseEvent)
    assert events[1].content == "Final Answer."
    mock_services["tool_manager"].execute_tool.assert_not_called()

async def test_tool_execution_flow(agent_executor, mock_services, mock_usage):
    """Test a flow where the agent decides to use a tool."""
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: search_web(query='test') Confidence: 0.98", mock_usage),
        ("Final Answer based on search. Confidence: 0.99", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result: Web search successful."
    events = [event async for event in agent_executor.run("test goal")]
    assert any(isinstance(e, ToolCallEvent) and e.tool_name == "search_web" for e in events)
    assert any(isinstance(e, ToolOutputEvent) and e.output == "Tool Result: Web search successful." for e in events)
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert final_response.content == "Final Answer based on search."
    mock_services["tool_manager"].execute_tool.assert_called_once_with("search_web", {'query': 'test'}, session_context=agent_executor.session_context)

async def test_reflection_loop_flow(agent_executor, mock_services, mock_usage):
    """Test the self-reflection loop for low-confidence answers."""
    mock_services["model_provider"].generate.side_effect = [
        ("I am not sure. Confidence: 0.5", mock_usage),
        ("To be more confident, I should search the web. Use Tool: search_web(query='clarify') Confidence: 0.99", mock_usage),
        ("Based on the web search, the answer is X. Confidence: 0.99", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool Result: The web says X."
    events = [event async for event in agent_executor.run("test goal")]
    thought_events = [e for e in events if isinstance(e, ThoughtEvent)]
    assert any("Confidence is low (" in e.content and "). Reflecting..." in e.content for e in thought_events)
    tool_call_event = next(e for e in events if isinstance(e, ToolCallEvent))
    assert tool_call_event.tool_name == "search_web"
    assert tool_call_event.args == {'query': 'clarify'}
    final_response = next(e for e in events if isinstance(e, FinalResponseEvent))
    assert final_response.content == "Based on the web search, the answer is X."
    assert mock_services["model_provider"].generate.call_count == 3

async def test_run_loop_is_driven_by_todo_list(agent_executor, mock_services, mock_usage):
    """Tests that the main execution loop is driven by the completion of a Todo list."""
    mock_todo_list = [MagicMock(description="call_tool_A", status="pending"), MagicMock(description="call_tool_B", status="pending")]
    memory_service = mock_services["memory_service"]
    memory_service.get_todo_list.return_value = mock_todo_list
    is_complete = False
    def a_is_complete(): return is_complete
    memory_service.is_todo_list_complete.side_effect = a_is_complete
    def a_update_todo_status(index):
        nonlocal is_complete
        mock_todo_list[index].status = "completed"
        if all(item.status == "completed" for item in mock_todo_list): is_complete = True
    memory_service.update_todo_status.side_effect = a_update_todo_status
    mock_services["model_provider"].generate.side_effect = [
        ("Use Tool: ToolA() Confidence: 0.99", mock_usage),
        ("Final answer for task A.", mock_usage),
        ("Use Tool: ToolB() Confidence: 0.99", mock_usage),
        ("Final answer for task B.", mock_usage)
    ]
    mock_services["tool_manager"].execute_tool.return_value = "Tool execution successful."
    _ = [event async for event in agent_executor.run("goal with a todo list")]
    assert mock_services["tool_manager"].execute_tool.call_count == 2
    calls = mock_services["tool_manager"].execute_tool.call_args_list
    assert calls[0].args[0] == "ToolA"
    assert calls[1].args[0] == "ToolB"
    assert agent_executor.state == AgentState.COMPLETED

async def test_run_can_be_steered_by_user_input_queue(agent_executor, mock_services, mock_usage):
    """Tests that a running agent can be steered by a message from the user queue."""
    model_is_paused = asyncio.Event()
    steering_command = "New steering instruction from user."
    async def model_generate_behavior(prompt):
        if steering_command in prompt:
            return ("Steered Action. Confidence: 0.99", mock_usage)
        else:
            await model_is_paused.wait()
            return ("Initial Action. Confidence: 0.99", mock_usage)
    mock_services["model_provider"].generate.side_effect = model_generate_behavior
    async def consume_agent_run():
        _ = [event async for event in agent_executor.run("initial goal")]
    agent_task = asyncio.create_task(consume_agent_run())
    await asyncio.sleep(0.01)
    await agent_executor.user_input_queue.put(steering_command)
    model_is_paused.set()
    await agent_task
    assert mock_services["memory_service"].construct_prompt.call_count > 1
    last_call_args, _ = mock_services["memory_service"].construct_prompt.call_args
    assert steering_command in str(last_call_args)
