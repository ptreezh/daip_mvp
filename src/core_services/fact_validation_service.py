"""@Time    : 2025-07-26 15:00:00
@Author  : DAIP-LIVE Team
@File    : fact_validation_service.py
@Description:
    Service layer for managing the validation of extracted facts.
"""
import logging
from typing import Any, List

from src.models import PendingFact

logger = logging.getLogger(__name__)


class FactValidationService:
    """Handles the business logic for reviewing, approving, and rejecting
    facts that have been staged by the FactExtractionService.
    """

    def __init__(self, app_state: Any): # Use Any to avoid circular import type hint
        self.app_state = app_state
        self.memory_service = app_state.memory_service

    def list_pending_facts(self, limit: int = 50, offset: int = 0) -> List[PendingFact]:
        """Lists all facts currently awaiting review."""
        logger.info(f"Fetching pending facts with limit={limit}, offset={offset}")
        return self.memory_service.get_pending_facts(limit, offset)

    def approve_fact(self, fact_id: str) -> bool:
        """Approves a fact, committing it to the permanent knowledge graph.
        """
        logger.info(f"Attempting to approve fact: {fact_id}")
        success = self.memory_service.approve_fact(fact_id)
        if not success:
            logger.error(f"Failed to approve fact {fact_id}. It may not exist or is not pending.")
        return success

    def reject_fact(self, fact_id: str) -> bool:
        """Rejects a fact, marking it as invalid.
        """
        logger.info(f"Attempting to reject fact: {fact_id}")
        success = self.memory_service.update_pending_fact_status(fact_id, "rejected")
        if not success:
            logger.error(f"Failed to reject fact {fact_id}. It may not exist.")
        return success
