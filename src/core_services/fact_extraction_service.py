# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-04 12:00:00
@Author  : DAIP-LIVE Team
@File    : fact_extraction_service.py
@Description:
    A service to automatically extract structured facts from text using an LLM
    and store them in the MemoryService's SSKG.
"""
import json
import logging
from typing import Any, Dict, List

from src.core_services.memory_service import MemoryService
from src.kernel.llm_interface import LLMInterface

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
    {"subject": "DAIP-LIVE system", "predicate": "uses_language", "object": "Python", "confidence": 1.0},
    {"subject": "DAIP-LIVE system", "predicate": "is_developed_by", "object": "core team", "confidence": 0.7}
]

Now, analyze the following text:
---
{text_to_analyze}
---
"""


class FactExtractionService:
    """
    Extracts structured facts from unstructured text and saves them to the SSKG.
    """

    def __init__(
        self, llm_interface: LLMInterface, memory_service: MemoryService, confidence_threshold: float = 0.75
    ):
        """
        Initializes the FactExtractionService.

        Args:
            llm_interface: The interface to interact with the language model.
            memory_service: The service to store the extracted facts.
            confidence_threshold: The minimum confidence score to stage a fact for review.
        """
        self.llm_interface = llm_interface
        self.memory_service = memory_service
        self.confidence_threshold = confidence_threshold

    async def extract_and_save_facts(self, text: str, source_metadata: Dict[str, Any]):
        """Analyzes text, extracts facts, and saves them to the SSKG."""
        prompt = FACT_EXTRACTION_PROMPT_TEMPLATE.format(text_to_analyze=text)

        try:
            # Assume llm_interface has a method to generate structured output
            response = await self.llm_interface.generate(messages=[{"role": "user", "content": prompt}])
            response_text = response.get("content", "[]")
            extracted_facts = json.loads(response_text)

            if not isinstance(extracted_facts, list):
                logger.warning("Fact extraction did not return a list. Response: %s", response_text)
                return

            pending_count = 0
            rejected_count = 0
            for fact in extracted_facts:
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

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from LLM response for fact extraction.")
        except Exception as e:
            logger.error("An error occurred during fact extraction: %s", e)