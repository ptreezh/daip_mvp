from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core_services import prompts
from src.core_services.synthesis_engine import SynthesisEngine
from src.kernel.llm_interface import LLMInterface
from src.models import DebateTurn

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture()
def mock_llm_interface() -> MagicMock:
    """Fixture for a mocked LLM interface."""
    mock_interface = MagicMock(spec=LLMInterface)
    mock_interface.generate = AsyncMock()
    mock_interface.config = MagicMock()
    mock_interface.config.model = "test-model"
    # Default response for generate method
    mock_interface.generate.return_value = {"content": "This is a summary of the discussion between role1 and role2."}
    return mock_interface


@pytest.fixture()
def synthesis_engine(mock_llm_interface: MagicMock) -> SynthesisEngine:
    """Fixture for the SynthesisEngine instance."""
    # The engine expects an LLM interface
    return SynthesisEngine(llm_interface=mock_llm_interface)


async def test_summarize_conversation_with_correct_data_structure(
    synthesis_engine: SynthesisEngine,
    mock_llm_interface: MagicMock,
) -> None:
    """Test conversation summarization with correctly structured history data."""
    messages: list[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="Point A"),
        DebateTurn(round=2, role_id="role2", opinion="Point B"),
    ]

    summary = await synthesis_engine.summarize_context(messages)

    # Assert the summary content is correct
    assert "This is a summary" in summary

    # Assert that the mocked interface's generate method was called
    mock_llm_interface.generate.assert_awaited_once()


async def test_summarize_context_handles_response_error(
    synthesis_engine: SynthesisEngine,
    mock_llm_interface: MagicMock,
) -> None:
    """Tests that summarize_context returns a formatted error on Exception."""
    # Arrange
    # Configure the mock interface to raise an Exception
    mock_error_details = "The specified model could not be found."
    mock_llm_interface.generate.side_effect = Exception(mock_error_details)

    # Create some dummy history to pass to the function
    messages: list[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="This will fail anyway."),
    ]

    # Act
    summary = await synthesis_engine.summarize_context(messages)

    # Assert
    assert "Error: An unexpected issue occurred during summarization." in summary
    assert mock_error_details in summary
    mock_llm_interface.generate.assert_awaited_once()


async def test_synthesize_opinions_success(
    synthesis_engine: SynthesisEngine,
    mock_llm_interface: MagicMock,
) -> None:
    """Tests successful opinion synthesis."""
    # Arrange
    topic = "The future of AI"
    history: list[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="AI is the future."),
        DebateTurn(round=2, role_id="role2", opinion="AI has risks."),
    ]
    # Configure the mock for this specific test case
    mock_synthesis_response = {"content": "A final synthesized conclusion."}
    mock_llm_interface.generate.return_value = mock_synthesis_response

    # Act
    synthesis = await synthesis_engine.synthesize_opinions(topic=topic, history=history)

    # Assert
    assert synthesis == "A final synthesized conclusion."
    mock_llm_interface.generate.assert_awaited_once()
    messages = mock_llm_interface.generate.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SYNTHESIS_SYSTEM_PROMPT
    assert f"Debate Topic: {topic}" in messages[1]['content']