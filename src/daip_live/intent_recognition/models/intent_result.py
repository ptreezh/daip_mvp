"""
Intent recognition result models for comprehensive intent system.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Types of recognized intents."""

    DEBATE_HISTORY = "debate_history"
    DOCUMENT_CONVERSION = "document_conversion"
    WIKI_MANAGEMENT = "wiki_management"
    PAPER_DOWNLOAD = "paper_download"
    SESSION_MANAGEMENT = "session_management"
    ROLE_MANAGEMENT = "role_management"
    MODEL_MANAGEMENT = "model_management"
    UNKNOWN = "unknown"


class IntentConfidenceLevel(str, Enum):
    """Confidence levels for intent recognition."""

    HIGH = "high"  # > 0.8
    MEDIUM = "medium"  # 0.6 - 0.8
    LOW = "low"  # < 0.6


class IntentRecognitionResult(BaseModel):
    """Result of intent recognition analysis."""

    intent_type: IntentType
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence score between 0 and 1"
    )
    matched_pattern: Optional[str] = Field(
        default=None, description="Pattern that matched the intent"
    )
    extracted_parameters: dict[str, Any] = Field(
        default_factory=dict, description="Parameters extracted from the input"
    )
    matched_text: Optional[str] = Field(
        default=None, description="Text that matched the intent pattern"
    )
    detected_at: datetime = Field(default_factory=datetime.now)

    @property
    def confidence_level(self) -> IntentConfidenceLevel:
        """Get confidence level based on score."""
        if self.confidence > 0.8:
            return IntentConfidenceLevel.HIGH
        elif self.confidence > 0.6:
            return IntentConfidenceLevel.MEDIUM
        else:
            return IntentConfidenceLevel.LOW

    @property
    def should_execute_automatically(self) -> bool:
        """Whether the system should execute the command automatically."""
        return self.confidence >= 0.7


class DebateHistoryIntent(BaseModel):
    """Intent for debate history operations."""

    intent_type: Literal[IntentType] = IntentType.DEBATE_HISTORY
    action: str = Field(..., description="Action type: 'list', 'view', 'search'")
    session_id: Optional[str] = Field(
        default=None, description="Session ID for specific history view"
    )
    topic: Optional[str] = Field(default=None, description="Search topic for debates")


class DocumentConversionIntent(BaseModel):
    """Intent for document conversion operations."""

    intent_type: Literal[IntentType] = IntentType.DOCUMENT_CONVERSION
    action: str = Field(
        default="convert", description="Action type: 'convert', 'format', 'transform'"
    )
    source_format: Optional[str] = Field(
        default=None, description="Source document format"
    )
    target_format: Optional[str] = Field(
        default=None, description="Target document format"
    )
    file_path: Optional[str] = Field(default=None, description="Path to source file")


class WikiManagementIntent(BaseModel):
    """Intent for wiki management operations."""

    intent_type: Literal[IntentType] = IntentType.WIKI_MANAGEMENT
    action: str = Field(
        default="list",
        description="Action type: 'create', 'list', 'view', 'export', 'search'",
    )
    page_title: Optional[str] = Field(
        default=None, description="Title for wiki page operations"
    )
    search_query: Optional[str] = Field(
        default=None, description="Query for wiki search"
    )


class PaperDownloadIntent(BaseModel):
    """Intent for paper download operations."""

    intent_type: Literal[IntentType] = IntentType.PAPER_DOWNLOAD
    action: str = Field(
        default="download", description="Action type: 'download', 'search', 'list'"
    )
    query: Optional[str] = Field(default=None, description="Search query for papers")
    source: Optional[str] = Field(
        default="arxiv", description="Paper source: arxiv, pubmed, etc."
    )


class SessionManagementIntent(BaseModel):
    """Intent for session management operations."""

    intent_type: Literal[IntentType] = IntentType.SESSION_MANAGEMENT
    action: str = Field(
        default="list", description="Action type: 'list', 'view', 'clear', 'search'"
    )
    session_id: Optional[str] = Field(
        default=None, description="Session ID for specific operations"
    )


class RoleManagementIntent(BaseModel):
    """Intent for role management operations."""

    intent_type: Literal[IntentType] = IntentType.ROLE_MANAGEMENT
    action: str = Field(
        default="list", description="Action type: 'list', 'view', 'create', 'edit'"
    )
    role_name: Optional[str] = Field(default=None, description="Specific role name")


class ModelManagementIntent(BaseModel):
    """Intent for model management operations."""

    intent_type: Literal[IntentType] = IntentType.MODEL_MANAGEMENT
    action: str = Field(
        default="list", description="Action type: 'list', 'view', 'switch', 'info'"
    )
    model_name: Optional[str] = Field(default=None, description="Specific model name")
