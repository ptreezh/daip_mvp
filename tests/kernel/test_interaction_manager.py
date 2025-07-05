# -*- coding: utf-8 -*-
"""
Unit tests for the InteractionManager class, focusing on context management.
"""

from unittest.mock import AsyncMock

import pytest

from src.kernel.interaction_manager import InteractionManager

# Use pytest-asyncio for all async tests in this module
pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_wiki_service() -> AsyncMock:
    """Fixture for a mocked WikiService."""
    service = AsyncMock()
    service.search_entries.return_value = []
    return service


@pytest.fixture
def mock_memory_service() -> AsyncMock:
    """Fixture for a mocked MemoryService."""
    service = AsyncMock()
    service.get_all_summaries.return_value = []
    return service


@pytest.fixture
def mock_synthesis_engine() -> AsyncMock:
    """Fixture for a mocked SynthesisEngine."""
    service = AsyncMock()
    service.summarize_conversation.return_value = "This is a test summary."
    return service


@pytest.fixture
def interaction_manager(
    mock_wiki_service: AsyncMock,
    mock_memory_service: AsyncMock,
    mock_synthesis_engine: AsyncMock,
) -> InteractionManager:
    """Fixture to create an InteractionManager instance with mocked dependencies."""
    return InteractionManager(
        wiki_service=mock_wiki_service,
        memory_service=mock_memory_service,
        synthesis_engine=mock_synthesis_engine,
    )


def generate_history(num_messages: int, content: str) -> list[dict]:
    """Helper to generate conversation history for testing."""
    history = []
    for i in range(num_messages):
        role = "user" if i % 2 == 0 else "assistant"
        history.append({"role": role, "content": content})
    return history


async def test_prepare_context_below_threshold(interaction_manager: InteractionManager, mock_synthesis_engine: AsyncMock):
    """Tests that summarization is NOT triggered when token count is below the threshold."""
    # Arrange
    short_history = generate_history(5, "This is a short message.")

    # Act
    await interaction_manager.prepare_context(short_history)

    # Assert
    mock_synthesis_engine.summarize_conversation.assert_not_called()


async def test_prepare_context_above_threshold_triggers_summarization(
    interaction_manager: InteractionManager, mock_synthesis_engine: AsyncMock, mock_memory_service: AsyncMock
):
    """Tests that summarization IS triggered when token count is above the threshold."""
    # Arrange: Create content long enough to be sure it exceeds the default token threshold.
    threshold = interaction_manager.context_token_threshold
    long_content = "a" * (threshold + 100)
    long_history = generate_history(2, long_content)
    long_history.append({"role": "user", "content": "Final question."})

    # Act
    result_messages = await interaction_manager.prepare_context(long_history)

    # Assert
    mock_synthesis_engine.summarize_conversation.assert_called_once_with(long_history[:-1])
    expected_summary = await mock_synthesis_engine.summarize_conversation.return_value
    mock_memory_service.save_summary.assert_called_once_with(expected_summary)
    assert len(result_messages) == 2, "History should be pruned to system prompt and last message"
    assert result_messages[0]["role"] == "system"
    assert result_messages[1] == long_history[-1]