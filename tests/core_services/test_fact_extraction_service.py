import json
import logging
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.core_services.fact_extraction_service import FactExtractionService
from src.core_services.memory_service import MemoryService
from src.kernel.llm_interface import LLMInterface


@pytest.fixture()
def mock_llm_interface() -> AsyncMock:
    """Fixture for a mocked LLM interface."""
    return AsyncMock(spec=LLMInterface)


@pytest.fixture()
def mock_memory_service() -> MagicMock:
    """Fixture for a mocked MemoryService."""
    return MagicMock(spec=MemoryService)


@pytest.fixture()
def fact_extraction_service(
    mock_llm_interface: AsyncMock, mock_memory_service: MagicMock
) -> FactExtractionService:
    """Fixture for the FactExtractionService instance."""
    return FactExtractionService(
        llm_interface=mock_llm_interface,
        memory_service=mock_memory_service,
        confidence_threshold=0.8,
    )


@pytest.mark.asyncio()
async def test_extract_and_save_facts_success(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: AsyncMock,
    mock_memory_service: MagicMock,
):
    """Test successful extraction and saving of facts."""
    # Arrange
    llm_response = [
        {"subject": "Fact 1", "predicate": "is", "object": "good", "confidence": 0.9},
        {"subject": "Fact 2", "predicate": "is", "object": "bad", "confidence": 0.7},
    ]
    mock_llm_interface.generate.return_value = {"content": json.dumps(llm_response)}
    source_metadata = {"source": "test_success"}

    # Act
    await fact_extraction_service.extract_and_save_facts(
        "some text", source_metadata
    )

    # Assert
    mock_llm_interface.generate.assert_called_once()
    # Fact 1 should be pending, Fact 2 should be rejected due to confidence threshold
    expected_calls = [
        call(
            "Fact 1", "is", "good", confidence=0.9, status="pending", metadata=source_metadata
        ),
        call(
            "Fact 2", "is", "bad", confidence=0.7, status="rejected", metadata=source_metadata
        ),
    ]
    mock_memory_service.add_fact_to_staging.assert_has_calls(
        expected_calls, any_order=True
    )
    assert mock_memory_service.add_fact_to_staging.call_count == 2


@pytest.mark.asyncio()
async def test_extract_retries_on_invalid_response_type_then_succeeds(
    fact_extraction_service: FactExtractionService,
    mock_llm_interface: AsyncMock,
    mock_memory_service: MagicMock,
    caplog,
):
    """Verify that the service retries when the LLM returns a valid JSON
    but not a list, then succeeds on the second attempt.
    """
    # Arrange
    caplog.set_level(logging.WARNING)
    # 1. First call: returns a JSON dictionary (invalid type)
    # 2. Second call: returns a JSON list (valid type)
    successful_response = [
        {"subject": "Test", "predicate": "is", "object": "successful", "confidence": 0.9}
    ]
    mock_llm_interface.generate.side_effect = [
        {"content": '{"error": "I returned a dictionary, not a list."}'},
        {"content": json.dumps(successful_response)},
    ]
    source_metadata = {"source": "test_retry"}

    # Act
    await fact_extraction_service.extract_and_save_facts(
        "some text", source_metadata, max_retries=2
    )

    # Assert
    # Check that the LLM was called twice
    assert mock_llm_interface.generate.call_count == 2

    # Check that the memory service was called with the fact from the *second* response
    mock_memory_service.add_fact_to_staging.assert_called_once_with(
        "Test", "is", "successful", confidence=0.9, status="pending", metadata=source_metadata
    )

    # Check that the retry warning was logged
    assert "A retryable error occurred (InvalidResponseTypeError)" in caplog.text
