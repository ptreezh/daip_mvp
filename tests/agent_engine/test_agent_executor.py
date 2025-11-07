import pytest
from unittest.mock import AsyncMock
@pytest.mark.asyncio
async def test_evaluating_prechecks_tool_and_ignores_if_missing(mocker):
    mock_session_manager = MagicMock()
    mock_session_manager.create_session.return_value = MagicMock()
    user_input_queue = asyncio.Queue()
    from daip_live.core.models import TodoItem
    mock_memory = MagicMock()
    mock_memory.construct_prompt = AsyncMock(return_value="prompt")
    mock_memory.get_todo_list = AsyncMock(return_value=[TodoItem(id=1, description="do", status="pending", priority=1)])
    mock_memory.is_todo_list_complete = AsyncMock(side_effect=[False, True])
    mock_memory.update_todo_status = AsyncMock()
    mock_model = MagicMock()
    mock_model.generate = AsyncMock(return_value=("Use Tool: not_exist(x=1) Confidence: 0.99", {}))
    mock_tools = MagicMock()
    mock_tools.execute_tool.side_effect = Exception("should not be called")
    agent = AgentExecutor(
        session_manager=mock_session_manager,
        memory_service=mock_memory,
        knowledge_manager=MagicMock(),
        model_provider=mock_model,
        tool_manager=mock_tools,
        user_input_queue=user_input_queue,
    )
    events = []
    async for e in agent.run("goal"):
        events.append(e)
        if isinstance(e, FinalResponseEvent):
            break
    assert mock_tools.execute_tool.call_count == 0

@pytest.mark.asyncio
async def test_permission_ask_flow_does_not_fail(mocker):
    from daip_live.p4_role_manager_tools.tool_manager import ToolPermissionRequest
    mock_session_manager = MagicMock()
    mock_session_manager.create_session.return_value = MagicMock()
    user_input_queue = asyncio.Queue()
    from daip_live.core.models import TodoItem
    mock_memory = MagicMock()
    mock_memory.construct_prompt = AsyncMock(return_value="prompt")
    mock_memory.get_todo_list = AsyncMock(return_value=[TodoItem(id=1, description="do", status="pending", priority=1)])
    mock_memory.is_todo_list_complete = AsyncMock(side_effect=[False, True])
    mock_memory.update_todo_status = AsyncMock()
    mock_model = MagicMock()
    mock_model.generate = AsyncMock(return_value=("Use Tool: safe(x=1) Confidence: 0.99", {}))
    mock_tools = MagicMock()
    mock_tools._registry = {"safe": MagicMock()}
    def raise_permission(*args, **kwargs):
        raise ToolPermissionRequest("safe", {"x": 1})
    mock_tools.execute_tool.side_effect = raise_permission
    agent = AgentExecutor(
        session_manager=mock_session_manager,
        memory_service=mock_memory,
        knowledge_manager=MagicMock(),
        model_provider=mock_model,
        tool_manager=mock_tools,
        user_input_queue=user_input_queue,
    )
    events = []
    async for e in agent.run("goal"):
        events.append(e)
        if isinstance(e, FinalResponseEvent):
            break
    assert any(getattr(e, "type", "") == "permission_request" for e in events)

import asyncio
from unittest.mock import MagicMock
from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import ThoughtEvent, FinalResponseEvent

def test_instantiate_executor():
    """Tests if the AgentExecutor can be instantiated without hanging."""
    agent = AgentExecutor(
        session_manager=MagicMock(),
        memory_service=MagicMock(),
        knowledge_manager=MagicMock(),
        model_provider=MagicMock(),
        tool_manager=MagicMock(),
        user_input_queue=asyncio.Queue(),
    )
    assert agent is not None

def test_chat_run_is_callable():
    """Tests that the chat_run attribute exists and is callable."""
    agent = AgentExecutor(
        session_manager=MagicMock(),
        memory_service=MagicMock(),
        knowledge_manager=MagicMock(),
        model_provider=MagicMock(),
        tool_manager=MagicMock(),
        user_input_queue=asyncio.Queue(),
    )
    assert callable(
        getattr(agent, "chat_run", None)
    ), "AgentExecutor should have a callable 'chat_run' method"


@pytest.mark.asyncio
async def test_chat_run_processes_user_input_from_queue(mocker):
    """
    Tests that chat_run waits for and processes a message from the user_input_queue.
    """
    # 1. Setup
    mock_session_manager = MagicMock()
    mock_session_manager.create_session.return_value = MagicMock()
    user_input_queue = asyncio.Queue()
    agent = AgentExecutor(
        session_manager=mock_session_manager,
        memory_service=MagicMock(),
        knowledge_manager=MagicMock(),
        model_provider=MagicMock(),
        tool_manager=MagicMock(),
        user_input_queue=user_input_queue,
    )

    # Define a dummy async generator to be used as the side_effect
    # This correctly mimics the behavior of the real _execute_step
    async def mock_execute_step_gen(*args, **kwargs):
        yield ThoughtEvent(content="Dummy event")

    # Patch the method and use our dummy generator as the side effect.
    # We also need a separate mock to track calls.
    call_tracker = MagicMock()
    def side_effect_wrapper(*args, **kwargs):
        call_tracker(*args, **kwargs)
        return mock_execute_step_gen(*args, **kwargs)

    mocker.patch.object(agent.step_executor, "execute_step", side_effect=side_effect_wrapper)

    # 2. Action
    async def consume_chat_run():
        async for _ in agent.chat_run(initial_goal="test goal"):
            pass

    chat_task = asyncio.create_task(consume_chat_run())
    await asyncio.sleep(0.1)

    test_input = "Hello, agent!"
    await user_input_queue.put(test_input)
    await asyncio.sleep(0.1)

    # 3. Assert
    assert call_tracker.call_count >= 2, "Expected _execute_step to be called for initial goal and user input"
    
    second_call_args = call_tracker.call_args_list[1]
    todo_item_arg = second_call_args.args[0]
    assert todo_item_arg.description == test_input

    # 4. Cleanup
    chat_task.cancel()
    try:
        await chat_task
    except asyncio.CancelledError:
        pass
