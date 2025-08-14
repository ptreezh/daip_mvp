"""@Time    : 2025-07-04 12:00:00
@Author  : DAIP-LIVE Team
@File    : fact_extraction_service.py
@Description:
    A service to automatically extract structured facts from text using an LLM
    and store them in the MemoryService's SSKG.
"""
import asyncio
import json
import logging
from typing import Any, Dict

from src.core_services.memory_service import MemoryService
from src.kernel.llm_interface import LLMInterface


class InvalidResponseTypeError(Exception):
    """Custom exception for when LLM response has an unexpected type."""

    pass

logger = logging.getLogger(__name__)

FACT_EXTRACTION_PROMPT_TEMPLATE = """
Your task is to act as a meticulous knowledge engineer. Analyze the following text and extract all factual statements.
Represent each fact as a structured triple of (Subject, Predicate, Object).
For each fact, also provide a 'confidence' score from 0.0 to 1.0, representing how certain you are that the statement is a correct and objective fact based on the text.

Return your findings as a JSON list of objects. Each object must have four keys: "subject", "predicate", "object", and "confidence".
If no facts can be extracted, return an empty list: [].

Example:
Text: "The DAIP-LIVE system, which I think was developed by the core team, uses Python."
Output:
[
    {{"subject": "DAIP-LIVE system", "predicate": "uses_language", "object": "Python", "confidence": 1.0}},
    {{"subject": "DAIP-LIVE system", "predicate": "is_developed_by", "object": "core team", "confidence": 0.7}}
]

Now, analyze the following text:
---
{text_to_analyze}
---
"""


class FactExtractionService:
    """Extracts structured facts from unstructured text and saves them to the SSKG.
    """

    def __init__(
        self, llm_interface: LLMInterface, memory_service: MemoryService, confidence_threshold: float = 0.75
    ):
        """Initializes the FactExtractionService.

        Args:
            llm_interface: The interface to interact with the language model.
            memory_service: The service to store the extracted facts.
            confidence_threshold: The minimum confidence score to stage a fact for review.

        """
        self.llm_interface = llm_interface
        self.memory_service = memory_service
        self.confidence_threshold = confidence_threshold

    async def extract_and_save_facts(self, text: str, source_metadata: Dict[str, Any], max_retries: int = 3):
        """Analyzes text, extracts facts, and saves them to the SSKG."""
        prompt = FACT_EXTRACTION_PROMPT_TEMPLATE.format(text_to_analyze=text)

        # Define exceptions that should trigger a retry.
        # This should be expanded with transient network/API errors from the LLM client library
        # (e.g., httpx.ReadTimeout, httpx.ConnectError, specific 5xx/429 status exceptions).
        RETRYABLE_EXCEPTIONS = (json.JSONDecodeError, asyncio.TimeoutError, InvalidResponseTypeError)

        for attempt in range(max_retries):
            try:
                # Assume llm_interface has a method to generate structured output
                response = await self.llm_interface.generate(messages=[{"role": "user", "content": prompt}])
                response_text = response.get("content", "[]")

                extracted_data = json.loads(response_text)

                if not isinstance(extracted_data, list):
                    # Raise a specific error to be caught by the retry mechanism.
                    raise InvalidResponseTypeError(f"LLM did not return a list, but a {type(extracted_data)}")

                extracted_facts = extracted_data
                break  # Success, exit loop

            except RETRYABLE_EXCEPTIONS as e:
                logger.warning(
                    "Attempt %d/%d: A retryable error occurred (%s). Retrying in %d seconds...",
                    attempt + 1, max_retries, type(e).__name__, attempt + 1
                )
                if attempt + 1 == max_retries:
                    logger.error("All retry attempts failed for text: %.100s...", text, exc_info=True)
                    return
                await asyncio.sleep(attempt + 1)  # Simple incremental backoff
            except Exception as e:
                # Catch any other, non-retryable exceptions
                logger.error("An unrecoverable error occurred during fact extraction: %s", e, exc_info=True)
                return
        else: # This 'else' belongs to the 'for' loop, and runs if the loop completes without 'break'
            return # All retries failed, so we exit.

        if isinstance(extracted_facts, list):
            pending_count = 0
            rejected_count = 0
            for fact in extracted_facts:
                if not isinstance(fact, dict):
                    logger.warning(
                        "Skipping non-dictionary item in extracted facts list: %s", fact
                    )
                    continue
                if all(k in fact for k in ["subject", "predicate", "object", "confidence"]):
                    confidence = float(fact.get("confidence", 0.0))
                    if confidence >= self.confidence_threshold:
                        self.memory_service.add_fact_to_staging(
                            fact["subject"], fact["predicate"], fact["object"],
                            confidence=confidence, status="pending", metadata=source_metadata
                        )
                        pending_count += 1
                    else:
                        # Automatically reject low-confidence facts
                        self.memory_service.add_fact_to_staging(
                            fact["subject"], fact["predicate"], fact["object"],
                            confidence=confidence, status="rejected", metadata=source_metadata
                        )
                        rejected_count += 1
            logger.info(
                "Fact extraction complete. Staged for review: %d. Auto-rejected: %d.",
                pending_count, rejected_count
            )
