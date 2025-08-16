"""@Time    : 2025-07-25 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_synthesis_engine.py
@Description:
    Unit tests for the SynthesisEngine.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core_services import prompts
from src.core_services.synthesis_engine import SynthesisEngine
from src.kernel.llm_interface import LLMInterface
from src.models import DebateTurn


@pytest.fixture()
def mock_llm_interface():
    """Fixture for a mocked LLM interface."""
    mock_interface = MagicMock(spec=LLMInterface)
    mock_interface.generate = AsyncMock()
    mock_interface.config = MagicMock()
    mock_interface.config.model = "test-model"
    return mock_interface


@pytest.fixture()
def debate_history():
    """Fixture for a sample debate history."""
    return [
        DebateTurn(role_id="Optimist", opinion="AI will solve all our problems.", round=1),
        DebateTurn(role_id="Pessimist", opinion="AI will cause unforeseen issues.", round=1),
    ]


@pytest.mark.asyncio()
async def test_summarize_context_success(mock_llm_interface, debate_history):
    """Tests successful context summarization."""
    # Arrange
    mock_response = {"content": "A summary of the debate."}
    mock_llm_interface.generate.return_value = mock_response

    engine = SynthesisEngine(llm_interface=mock_llm_interface)

    # Act
    summary = await engine.summarize_context(debate_history)

    # Assert
    assert summary == "A summary of the debate."
    mock_llm_interface.generate.assert_awaited_once()
    messages = mock_llm_interface.generate.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SUMMARIZATION_SYSTEM_PROMPT
    assert "AI will solve all our problems." in messages[1]['content']


@pytest.mark.asyncio()
async def test_summarize_context_empty_history(mock_llm_interface):
    """Tests summarization with no history."""
    # Arrange
    engine = SynthesisEngine(llm_interface=mock_llm_interface)

    # Act
    summary = await engine.summarize_context([])

    # Assert
    assert summary == "The debate has just started."
    mock_llm_interface.generate.assert_not_called()


@pytest.mark.asyncio()
async def test_synthesize_opinions_success(mock_llm_interface, debate_history):
    """Tests successful opinion synthesis."""
    # Arrange
    mock_response = {"content": "A final conclusion."}
    mock_llm_interface.generate.return_value = mock_response

    engine = SynthesisEngine(llm_interface=mock_llm_interface)

    # Act
    synthesis = await engine.synthesize_opinions(topic="Future of AI", history=debate_history)

    # Assert
    assert synthesis == "A final conclusion."
    mock_llm_interface.generate.assert_awaited_once()
    messages = mock_llm_interface.generate.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SYNTHESIS_SYSTEM_PROMPT
    assert "Debate Topic: Future of AI" in messages[1]['content']
