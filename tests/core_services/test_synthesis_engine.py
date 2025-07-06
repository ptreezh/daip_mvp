# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_synthesis_engine.py
@Description:
    Unit tests for the SynthesisEngine.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import ollama
from ollama import ResponseError

from src.core_services.synthesis_engine import SynthesisEngine
from src.core_services import prompts
from src.models import DebateTurn


@pytest.fixture
def mock_ollama_client():
    """Fixture for a mocked Ollama async client."""
    client = MagicMock(spec=ollama.AsyncClient)
    client.chat = AsyncMock()
    return client


@pytest.fixture
def debate_history():
    """Fixture for a sample debate history."""
    return [
        DebateTurn(role_id="Optimist", opinion="AI will solve all our problems.", round=1),
        DebateTurn(role_id="Pessimist", opinion="AI will cause unforeseen issues.", round=1),
    ]


@pytest.mark.asyncio
async def test_summarize_context_success(mock_ollama_client, debate_history):
    """Tests successful context summarization."""
    # Arrange
    mock_response = {"message": {"content": "A summary of the debate."}}
    mock_ollama_client.chat.return_value = mock_response

    engine = SynthesisEngine(client=mock_ollama_client, model="test-summarizer")

    # Act
    summary = await engine.summarize_context(debate_history)

    # Assert
    assert summary == "A summary of the debate."
    mock_ollama_client.chat.assert_awaited_once()
    messages = mock_ollama_client.chat.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SUMMARIZATION_SYSTEM_PROMPT
    assert "AI will solve all our problems." in messages[1]['content']


@pytest.mark.asyncio
async def test_summarize_context_empty_history(mock_ollama_client):
    """Tests summarization with no history."""
    # Arrange
    engine = SynthesisEngine(client=mock_ollama_client, model="test-model")

    # Act
    summary = await engine.summarize_context([])

    # Assert
    assert summary == "The debate has just started."
    mock_ollama_client.chat.assert_not_called()


@pytest.mark.asyncio
async def test_synthesize_opinions_success(mock_ollama_client, debate_history):
    """Tests successful opinion synthesis."""
    # Arrange
    mock_response = {"message": {"content": "A final conclusion."}}
    mock_ollama_client.chat.return_value = mock_response

    engine = SynthesisEngine(client=mock_ollama_client, model="test-model")

    # Act
    synthesis = await engine.synthesize_opinions(topic="Future of AI", history=debate_history)

    # Assert
    assert synthesis == "A final conclusion."
    mock_ollama_client.chat.assert_awaited_once()
    messages = mock_ollama_client.chat.call_args.kwargs['messages']
    assert messages[0]['content'] == prompts.SYNTHESIS_SYSTEM_PROMPT
    assert "Debate Topic: Future of AI" in messages[1]['content']