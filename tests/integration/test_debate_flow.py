"""@Time    : 2025-07-20 12:00:00
@Author  : DAIP-LIVE Team
@File    : test_debate_flow.py
@Description: Integration tests for basic debate flow functionality.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.kernel.core import Kernel
from src.models import DebateConfig
from src.protocols.debate_protocol import DebateProtocol

# Mark all tests in this file as asyncio
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
    kernel.llm_interface = MagicMock()
    kernel.llm_interface.generate = AsyncMock()
    return kernel


@pytest.fixture()
def event_queue():
    """Fixture for a new asyncio.Queue for each test."""
    return asyncio.Queue()


@pytest.fixture()
def simple_debate_config():
    """Fixture for a simple DebateConfig."""
    return DebateConfig(
        topic="Should we use renewable energy?",
        roles=["Environmental Expert", "Economic Analyst"],
        rounds=2,
        consensus_strategy="simple_majority_vote"
    )


async def test_basic_debate_flow(mock_kernel, event_queue, simple_debate_config):
    """Test basic debate flow with two participants and two rounds."""
    # Arrange
    mock_kernel.synthesis_engine.summarize_context.side_effect = [
        "Context for Environmental Expert",
        "Context for Economic Analyst",
        "Context for Environmental Expert round 2",
        "Context for Economic Analyst round 2"
    ]
    mock_kernel.llm_interface.generate.side_effect = [
        {"content": "Renewable energy is essential for our future"},
        {"content": "We must consider the economic implications"},
        {"content": "The long-term benefits outweigh short-term costs"},
        {"content": "Gradual transition is more economically viable"}
    ]
    mock_kernel.tool_executor.execute_tool.return_value = {
        "status": "success",
        "result": "Both perspectives agree on gradual transition"
    }
    mock_kernel.synthesis_engine.synthesize_opinions.return_value = (
        "A balanced approach combining environmental urgency with economic pragmatism"
    )

    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=simple_debate_config)

    # Assert
    # Verify that all expected interactions occurred
    assert mock_kernel.synthesis_engine.summarize_context.call_count == 4  # 2 roles × 2 rounds
    assert mock_kernel.llm_interface.generate.call_count == 4
    mock_kernel.tool_executor.execute_tool.assert_called_once()
    mock_kernel.synthesis_engine.synthesize_opinions.assert_called_once()

    # Verify debate history was built correctly
    assert len(protocol.history) == 4
    assert protocol.history[0].role_id == "Environmental Expert"
    assert protocol.history[1].role_id == "Economic Analyst"
    assert protocol.history[2].role_id == "Environmental Expert"
    assert protocol.history[3].role_id == "Economic Analyst"


async def test_single_round_debate_flow(mock_kernel, event_queue):
    """Test debate flow with single round."""
    # Arrange
    config = DebateConfig(
        topic="Quick decision needed",
        roles=["Expert"],
        rounds=1,
        consensus_strategy="simple_majority_vote"
    )

    mock_kernel.synthesis_engine.summarize_context.return_value = "Initial context"
    mock_kernel.llm_interface.generate.return_value = {"content": "Expert opinion"}
    mock_kernel.tool_executor.execute_tool.return_value = {"status": "success", "result": "Decision made"}
    mock_kernel.synthesis_engine.synthesize_opinions.return_value = "Final decision"

    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=config)

    # Assert
    assert len(protocol.history) == 1
    assert protocol.history[0].role_id == "Expert"
    assert protocol.history[0].round == 1
    mock_kernel.synthesis_engine.summarize_context.assert_called_once()
    mock_kernel.llm_interface.generate.assert_called_once()


async def test_multi_participant_debate_flow(mock_kernel, event_queue):
    """Test debate flow with multiple participants."""
    # Arrange
    config = DebateConfig(
        topic="Complex multi-stakeholder issue",
        roles=["Scientist", "Economist", "Ethicist", "Politician"],
        rounds=1,
        consensus_strategy="simple_majority_vote"
    )

    mock_kernel.synthesis_engine.summarize_context.side_effect = [
        "Context for Scientist",
        "Context for Economist",
        "Context for Ethicist",
        "Context for Politician"
    ]
    mock_kernel.llm_interface.generate.side_effect = [
        {"content": "Scientific perspective"},
        {"content": "Economic perspective"},
        {"content": "Ethical perspective"},
        {"content": "Political perspective"}
    ]
    mock_kernel.tool_executor.execute_tool.return_value = {"status": "success", "result": "Consensus reached"}
    mock_kernel.synthesis_engine.synthesize_opinions.return_value = "Multi-stakeholder agreement"

    protocol = DebateProtocol(kernel=mock_kernel, event_queue=event_queue)

    # Act
    await protocol.run(config=config)

    # Assert
    assert len(protocol.history) == 4
    role_ids = [turn.role_id for turn in protocol.history]
    assert "Scientist" in role_ids
    assert "Economist" in role_ids
    assert "Ethicist" in role_ids
    assert "Politician" in role_ids

    # All should be round 1
    assert all(turn.round == 1 for turn in protocol.history)
