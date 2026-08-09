"""
Clarification models for context-aware intent recognition.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ClarificationType(str, Enum):
    """Type of clarification needed."""

    MISSING_KEYWORDS = "missing_keywords"
    MISSING_PARAMETERS = "missing_parameters"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    CONTEXT_NEEDED = "context_needed"


class ClarificationOption(BaseModel):
    """Option for multiple-choice clarification."""

    id: str
    text: str
    intent_action: Optional[str] = None
    parameters: Optional[dict[str, Any]] = Field(default_factory=dict)


class ClarificationRequest(BaseModel):
    """Request for missing information or clarification."""

    type: ClarificationType
    message: str
    options: Optional[list[ClarificationOption]] = Field(default_factory=list)
    required_parameters: Optional[list[str]] = Field(default_factory=list)
    context_data: Optional[dict[str, Any]] = Field(default_factory=dict)


class ContextualIntentResult(BaseModel):
    """Intent result that includes clarification status."""

    original_intent: str
    confidence: float
    parameters: dict[str, Any]
    requires_clarification: bool = False
    clarification_request: Optional[ClarificationRequest] = None
    resolved_parameters: bool = False
