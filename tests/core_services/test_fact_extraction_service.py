# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-04 12:30:00
@Author  : DAIP-LIVE Team
@File    : test_fact_extraction_service.py
@Description:
    Unit tests for the FactExtractionService.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core_services.fact_extraction_service import FactExtractionService


class MockLLMInterface:
    """A mock LLMInterface for testing purposes."""

    def __init__(self):
        # Use AsyncMock for async methods
        self.generate_text = AsyncMock()

    def set_response(self, response_text: str):
        """Sets the mock response for the generate_text method."""
        self.generate_text.return_value = response_text


@pytest.fixture
def mock_memory_service() -> MagicMock:
    """Provides a mock MemoryService with a mockable add_fact_to_sskg method."""
    service = MagicMock()
    service.add_fact_to_sskg = MagicMock()
    return service


@pytest.fixture
def mock_llm_interface() -> MockLLMInterface:
    """Provides a mock LLMInterface."""
    return MockLLMInterface()


@pytest.fixture
def fact_extraction_service(
    mock_llm_interface: MockLLMInterface, mock_memory_service: MagicMock
) -> FactExtractionService:
    """Provides an instance of FactExtractionService with mocked dependencies."""
    return FactExtractionService(
        llm_interface=mock_llm_interface, memory_service=mock_memory_service
    )


@pytest.mark.asyncio
async def test_extract_and_save_facts_success(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: MockLLMInterface,
    mock_memory_service: MagicMock,
):
    """Tests the successful extraction and saving of multiple facts."""
    # Arrange
    input_text = "Socrates was a philosopher who taught Plato."
    source_metadata = {"message_id": "msg_123"}
    llm_response = json.dumps([
        {"subject": "Socrates", "predicate": "is_a", "object": "philosopher"},
        {"subject": "Socrates", "predicate": "taught", "object": "Plato"},
    ])
    mock_llm_interface.set_response(llm_response)

    # Act
    await fact_extraction_service.extract_and_save_facts(input_text, source_metadata)

    # Assert
    assert mock_memory_service.add_fact_to_sskg.call_count == 2
    mock_memory_service.add_fact_to_sskg.assert_any_call(
        "Socrates", "is_a", "philosopher", metadata=source_metadata
    )
    mock_memory_service.add_fact_to_sskg.assert_any_call(
        "Socrates", "taught", "Plato", metadata=source_metadata
    )


@pytest.mark.asyncio
async def test_extract_handles_invalid_json(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: MockLLMInterface,
    mock_memory_service: MagicMock,
    caplog,
):
    """Tests that the service handles invalid JSON from the LLM gracefully."""
    # Arrange
    mock_llm_interface.set_response("this is not valid json")

    # Act
    await fact_extraction_service.extract_and_save_facts("text", {})

    # Assert
    mock_memory_service.add_fact_to_sskg.assert_not_called()
    assert "Failed to parse JSON from LLM response" in caplog.text


@pytest.mark.asyncio
async def test_extract_handles_malformed_fact_data(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: MockLLMInterface,
    mock_memory_service: MagicMock,
):
    """Tests that facts with missing keys are skipped."""
    # Arrange
    llm_response = json.dumps([{"subject": "Incomplete Fact"}])  # Missing predicate and object
    mock_llm_interface.set_response(llm_response)

    # Act
    await fact_extraction_service.extract_and_save_facts("text", {})

    # Assert
    mock_memory_service.add_fact_to_sskg.assert_not_called()


@pytest.mark.asyncio
async def test_extract_handles_non_list_response(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: MockLLMInterface,
    mock_memory_service: MagicMock,
    caplog,
):
    """Tests that the service handles a JSON response that is not a list."""
    # Arrange
    llm_response = json.dumps({"error": "I returned a dict instead of a list."})
    mock_llm_interface.set_response(llm_response)

    # Act
    await fact_extraction_service.extract_and_save_facts("text", {})

    # Assert
    mock_memory_service.add_fact_to_sskg.assert_not_called()
    assert "Fact extraction did not return a list" in caplog.text