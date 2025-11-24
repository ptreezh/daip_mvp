"""
Clarification models for context-aware intent recognition.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


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
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ClarificationRequest(BaseModel):
    """Request for missing information or clarification."""
    type: ClarificationType
    message: str
    options: Optional[List[ClarificationOption]] = Field(default_factory=list)
    required_parameters: Optional[List[str]] = Field(default_factory=list)
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ContextualIntentResult(BaseModel):
    """Intent result that includes clarification status."""
    original_intent: str
    confidence: float
    parameters: Dict[str, Any]
    requires_clarification: bool = False
    clarification_request: Optional[ClarificationRequest] = None
    resolved_parameters: bool = False