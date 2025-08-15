"""@Time    : 2025-07-25 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_interaction_manager.py
@Description:
    Unit tests for the InteractionManager.
"""
from unittest.mock import AsyncMock, MagicMock

import ollama
import pytest
from ollama import ResponseError

from src.kernel.interaction_manager import InteractionManager


@pytest.fixture()
def mock_ollama_client():
    """Fixture for a mocked Ollama async client."""
    client = MagicMock(spec=ollama.AsyncClient)
    client.chat = AsyncMock()
    return client


@pytest.mark.asyncio()
async def test_get_response_success(mock_ollama_client):
    """Tests that get_response successfully returns content from the LLM."""
    # Arrange
    mock_response = {"message": {"content": "A clear opinion."}}
    mock_ollama_client.chat.return_value = mock_response

    manager = InteractionManager(client=mock_ollama_client, model="test-model")

    # Act
    response = await manager.get_response(role_id="TestRole", context="Some debate context.")

    # Assert
    assert response == "A clear opinion."
    mock_ollama_client.chat.assert_awaited_once()
    messages = mock_ollama_client.chat.call_args.kwargs['messages']
    assert messages[0]['role'] == 'system'
    assert "You are an AI assistant playing the role of 'TestRole'" in messages[0]['content']
    assert messages[1]['role'] == 'user'
    assert "Some debate context." in messages[1]['content']


@pytest.mark.asyncio()
async def test_get_response_handles_response_error(mock_ollama_client):
    """Tests that get_response handles Ollama ResponseError gracefully."""
    # Arrange
    mock_ollama_client.chat.side_effect = ResponseError("Model not found", 404)
    manager = InteractionManager(client=mock_ollama_client, model="bad-model")

    # Act
    response = await manager.get_response(role_id="TestRole", context="Some context.")

    # Assert
    assert "Error: Could not get a response" in response
    assert "Model not found" in response


@pytest.mark.asyncio()
async def test_get_response_handles_unexpected_error(mock_ollama_client):
    """Tests that get_response handles unexpected exceptions."""
    # Arrange
    mock_ollama_client.chat.side_effect = Exception("A network failure")
    manager = InteractionManager(client=mock_ollama_client)

    # Act
    response = await manager.get_response(role_id="TestRole", context="Some context.")

    # Assert
    assert "Error: An unexpected issue occurred" in response