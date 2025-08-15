"""@Time    : 2025-07-25 12:00:00
@Author  : DAIP-LIVE Team
@File    : test_debate_protocol.py
@Description:
    Unit tests for the DebateProtocol orchestrator.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.kernel.core import Kernel
from src.models import (
    DebateConfig,
    DebateEndEvent,
    DebateResult,
    DebateStartEvent,
    DebateTurn,
    ErrorEvent,
    NewTurnEvent,
    TechLogEvent,
    UserInterventionCommand,
)
from src.protocols.debate_protocol import DebateProtocol

# Use pytest_asyncio for all tests in this module
pytestmark = pytest.mark.asyncio


@pytest.fixture()
def mock_kernel():
    """Fixture for a mocked Kernel with its components."""
    kernel = MagicMock(spec=Kernel)
    kernel.interaction_manager = MagicMock()
    kernel.interaction_manager.get_response = AsyncMock()
    kernel.synthesis_engine = MagicMock()
    kernel.synthesis_engine.summarize_context = AsyncMock()
    kernel.synthesis_engine.synthesize_opinions = AsyncMock()
    kernel.tool_executor = MagicMock()
    kernel.tool_executor.execute_tool = MagicMock()
    # Add the missing llm_interface attribute
    kernel.llm_interface = MagicMock()
    kernel.llm_interface.generate = AsyncMock()
    return kernel


@pytest.fixture()
def event_queue():
    """Fixture for a new asyncio.Queue for each test."""
    return asyncio.Queue()


@pytest.fixture()
def debate_config():
    """Fixture for a standard DebateConfig."""
    return DebateConfig(
        topic="Test Topic",
        roles=["RoleA", "RoleB"],
        rounds=1,
        consensus_strategy="test_consensus"
    )


async def get_all_events(queue: asyncio.Queue):
    """Helper to drain an asyncio queue and return all items."""
    events = []
    while not queue.empty():
        events.append(queue.get_nowait())
    return events


async def test_run_successful_debate(mock_kernel, event_queue, debate_config):
    """Tests the full, successful execution path of the debate protocol.
    """
    # Arrange
    mock_kernel.synthesis_engine.summarize_context.side_effect = ["Context for RoleA", "Context for RoleB"]
    mock_kernel.llm_interface.generate.side_effect = [
        {"content": "Opinion from RoleA"},
        {"content": "Opinion from RoleB"}
    ]
    mock_kernel.tool_executor.execute_tool.return_value = {"status": "success", "result": "Consensus reached"}
    mock_kernel.synthesis_engine.synthesize_opinions.return_value = "Final synthesis"

    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=debate_config)

    # Assert
    # Check kernel component calls
    assert mock_kernel.synthesis_engine.summarize_context.call_count == 2
    assert mock_kernel.llm_interface.generate.call_count == 2
    # Verify that generate was called with proper message structure
    generate_calls = mock_kernel.llm_interface.generate.call_args_list
    assert len(generate_calls) == 2
    # Check that each call has the expected message structure
    for call_args in generate_calls:
        messages = call_args[0][0]  # First positional argument
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    mock_kernel.tool_executor.execute_tool.assert_called_once_with(
        tool_name="test_consensus",
        history=protocol.history
    )
    mock_kernel.synthesis_engine.synthesize_opinions.assert_called_once_with(
        topic="Test Topic",
        history=protocol.history
    )

    # Check emitted events
    events = await get_all_events(event_queue)
    assert isinstance(events[0], DebateStartEvent)
    assert isinstance(events[1], TechLogEvent) # "Starting Round 1..."
    assert isinstance(events[2], TechLogEvent) # "Turn for role: RoleA"
    assert isinstance(events[3], NewTurnEvent)
    assert events[3].turn.role_id == "RoleA"
    assert events[3].turn.opinion == "Opinion from RoleA"
    assert isinstance(events[4], TechLogEvent) # "Turn for role: RoleB"
    assert isinstance(events[5], NewTurnEvent)
    assert events[5].turn.role_id == "RoleB"
    assert events[5].turn.opinion == "Opinion from RoleB"
    assert isinstance(events[6], TechLogEvent) # "Moving to consensus."
    assert isinstance(events[7], TechLogEvent) # "Synthesizing final result."
    assert isinstance(events[8], DebateEndEvent)

    final_result = events[8].result
    assert isinstance(final_result, DebateResult)
    assert final_result.consensus_outcome == "Consensus reached"
    assert final_result.synthesis == "Final synthesis"
    assert len(final_result.history) == 2


async def test_run_handles_interaction_failure(mock_kernel, event_queue, debate_config):
    """Tests that an ErrorEvent is emitted if the LLM interface fails.
    """
    # Arrange
    mock_kernel.synthesis_engine.summarize_context.return_value = "Some context"
    mock_kernel.llm_interface.generate.side_effect = Exception("LLM is down")
    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=debate_config)

    # Assert
    events = await get_all_events(event_queue)
    error_event = events[-1]
    assert isinstance(error_event, ErrorEvent)
    assert "LLM is down" in error_event.details


async def test_run_handles_consensus_failure(mock_kernel, event_queue, debate_config):
    """Tests that the debate continues with simple consensus when consensus tool fails.
    """
    # Arrange
    mock_kernel.synthesis_engine.summarize_context.return_value = "Context"
    mock_kernel.llm_interface.generate.return_value = {"content": "Opinion"}
    mock_kernel.tool_executor.execute_tool.return_value = {"status": "error", "message": "tool broke"}
    mock_kernel.synthesis_engine.synthesize_opinions.return_value = "Final synthesis"
    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=debate_config)

    # Assert
    events = await get_all_events(event_queue)
    # Should end successfully with DebateEndEvent, not ErrorEvent
    end_event = events[-1]
    assert isinstance(end_event, DebateEndEvent)
    # Check that consensus fallback was used
    # The consensus outcome is now set by the mock return value
    assert isinstance(end_event.result.consensus_outcome, str)
    assert "No clear consensus" in end_event.result.consensus_outcome
    # Check that a TechLogEvent was emitted about the consensus tool failure
    tech_log_events = [e for e in events if isinstance(e, TechLogEvent)]
    consensus_failure_logs = [e for e in tech_log_events if "Consensus tool failed" in e.message]
    assert len(consensus_failure_logs) > 0


async def test_handle_user_intervention(mock_kernel, event_queue):
    """Tests that a user intervention command is correctly processed.
    """
    # Arrange
    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)
    # Simulate some history to get the round number
    protocol.history.append(DebateTurn(role_id="AI", opinion="...", round=1))
    command = UserInterventionCommand(content="This is my intervention.")

    # Act
    await protocol.handle_command(command)

    # Assert
    assert len(protocol.history) == 2
    intervention_turn = protocol.history[-1]
    assert intervention_turn.role_id == "User (Intervention)"
    assert intervention_turn.opinion == "This is my intervention."
    assert intervention_turn.round == 1

    events = await get_all_events(event_queue)
    assert len(events) == 1
    event = events[0]
    assert isinstance(event, NewTurnEvent)
    assert event.turn == intervention_turn
