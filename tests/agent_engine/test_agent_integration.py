import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import FinalResponseEvent, ThoughtEvent, DialogueTurn, Session
from daip_live.memory.service import MemoryService


@pytest.mark.asyncio
async def test_chat_run_integration_with_mock_llm(mocker):
    """
    Tests the full chat_run -> _execute_step -> RESPONDING flow,
    only mocking the actual LLM call.
    """
    # 1. Setup
    # Mock dependencies
    mock_session_manager = MagicMock()
    mock_session = Session(session_id="test_session", goal="test", session_type="chat", participant_ids=["user", "agent"])
    mock_session_manager.create_session.return_value = mock_session

    mock_model_provider = MagicMock()
    # FIX: The mock must be an awaitable (AsyncMock) to be used with 'await'.
    mock_model_provider.generate = AsyncMock(
        return_value=("Final Answer: I am a mock bot.", {"total_tokens": 10})
    )

    # Use a real MemoryService to test prompt construction
    memory_service = MemoryService(model_provider=mock_model_provider)

    user_input_queue = asyncio.Queue()
    agent = AgentExecutor(
        session_manager=mock_session_manager,
        memory_service=memory_service, # Using real service
        knowledge_manager=MagicMock(),
        model_provider=mock_model_provider,
        tool_manager=MagicMock(),
        user_input_queue=user_input_queue,
    )

    # 2. Action
    events = []
    async def consume_chat_run():
        async for event in agent.chat_run(initial_goal="Initial goal"):
            events.append(event)

    # Run chat in background and wait for it to process the initial goal
    chat_task = asyncio.create_task(consume_chat_run())
    await asyncio.sleep(0.1)

    # Simulate user input, which should trigger the full loop
    await user_input_queue.put("Hello, what can you do?")
    await asyncio.sleep(0.2) # Give ample time for the full loop to run

    # 3. Assert
    # Assert that the LLM was called
    mock_model_provider.generate.assert_called()

    # Assert that the prompt passed to the LLM contains the user input
    prompt_arg = mock_model_provider.generate.call_args.args[0]
    assert "Hello, what can you do?" in prompt_arg

    # Assert that we received a FinalResponseEvent
    final_responses = [e for e in events if isinstance(e, FinalResponseEvent)]
    assert len(final_responses) > 0, "Expected a FinalResponseEvent"

    # Assert the content of the final response is correct
    # The agent should strip "Final Answer: " from the LLM output
    assert final_responses[-1].content == "I am a mock bot."

    # 4. Cleanup
    chat_task.cancel()
    try:
        await chat_task
    except asyncio.CancelledError:
        pass
