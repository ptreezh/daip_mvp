import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import List
import ollama
from ollama import ResponseError
from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services import prompts
from src.models import DebateTurn

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_ollama_client() -> MagicMock:
    """Fixture for a mocked Ollama async client."""
    client = MagicMock(spec=ollama.AsyncClient)
    # The response from client.chat is a dictionary
    mock_response = {"message": {"content": "This is a summary of the discussion between role1 and role2."}}
    client.chat = AsyncMock(return_value=mock_response)
    return client


@pytest.fixture
def synthesis_engine(mock_ollama_client: MagicMock) -> SynthesisEngine:
    """Fixture for the SynthesisEngine instance."""
    # The engine expects the client and an optional model name
    return SynthesisEngine(client=mock_ollama_client, model="test-model")


async def test_summarize_conversation_with_correct_data_structure(
    synthesis_engine: SynthesisEngine,
    mock_ollama_client: MagicMock,
) -> None:
    """Test conversation summarization with correctly structured history data."""
    messages: List[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="Point A"),
        DebateTurn(round=2, role_id="role2", opinion="Point B"),
    ]

    summary = await synthesis_engine.summarize_context(messages)

    # Assert the summary content is correct
    assert "This is a summary" in summary

    # Assert that the mocked client's chat method was called
    mock_ollama_client.chat.assert_awaited_once()


async def test_summarize_context_handles_response_error(
    synthesis_engine: SynthesisEngine,
    mock_ollama_client: MagicMock,
) -> None:
    """Tests that summarize_context returns a formatted error on ResponseError."""
    # Arrange
    # Configure the mock client to raise a ResponseError
    mock_error_details = "The specified model could not be found."
    mock_ollama_client.chat.side_effect = ResponseError(mock_error_details)

    # Create some dummy history to pass to the function
    messages: List[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="This will fail anyway."),
    ]

    # Act
    summary = await synthesis_engine.summarize_context(messages)

    # Assert
    assert "Error: Could not summarize context." in summary
    assert mock_error_details in summary
    mock_ollama_client.chat.assert_awaited_once()


async def test_synthesize_opinions_success(
    synthesis_engine: SynthesisEngine,
    mock_ollama_client: MagicMock,
) -> None:
    """Tests successful opinion synthesis."""
    # Arrange
    topic = "The future of AI"
    history: List[DebateTurn] = [
        DebateTurn(round=1, role_id="role1", opinion="AI is the future."),
        DebateTurn(round=2, role_id="role2", opinion="AI has risks."),
    ]
    # Configure the mock for this specific test case
    mock_synthesis_response = {"message": {"content": "A final synthesized conclusion."}}
    mock_ollama_client.chat.return_value = mock_synthesis_response

    # Act
    synthesis = await synthesis_engine.synthesize_opinions(topic=topic, history=history)

    # Assert
    assert synthesis == "A final synthesized conclusion."
    mock_ollama_client.chat.assert_awaited_once()
    messages = mock_ollama_client.chat.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SYNTHESIS_SYSTEM_PROMPT
    assert f"Debate Topic: {topic}" in messages[1]['content']