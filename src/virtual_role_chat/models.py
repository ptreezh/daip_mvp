"""Core data models for the Virtual Role Chat System.

This module defines the Pydantic models used throughout the Virtual Role Chat System,
including ChatRoom, ChatSession, ChatMessage, and related types.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

# Type aliases for improved readability
ChatRoomID = str
SessionID = str


class ChatRoomConfig(BaseModel):
    """Configuration for a chat room."""

    name: str
    description: str = ""
    topic: str
    roles: List[str]  # Role IDs
    mode: Literal["free_form", "structured", "debate", "turn_based", "random"] = "free_form"
    interaction_rules: Dict[str, Any] = {}  # Mode-specific configuration


class ChatRoom(BaseModel):
    """Represents a chat room where multiple roles can interact."""

    id: ChatRoomID
    config: ChatRoomConfig
    created_at: datetime
    updated_at: datetime
    status: Literal["active", "paused", "archived"] = "active"


class ChatRoomSummary(BaseModel):
    """Summary information about a chat room."""

    id: ChatRoomID
    name: str
    topic: str
    role_count: int
    message_count: int
    status: str
    last_active: datetime


class ChatMessage(BaseModel):
    """Represents a message in a chat session."""

    id: str
    session_id: SessionID
    sender_id: str  # Role ID or user ID
    sender_type: Literal["role", "user", "system"]
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class ChatSession(BaseModel):
    """Represents an active chat session within a chat room."""

    id: SessionID
    room_id: ChatRoomID
    start_time: datetime
    end_time: Optional[datetime] = None
    status: Literal["active", "paused", "completed"] = "active"
    messages: List[ChatMessage] = []
    metadata: Dict[str, Any] = {}


class SessionSummary(BaseModel):
    """Summary information about a chat session."""

    id: SessionID
    room_id: ChatRoomID
    start_time: datetime
    end_time: Optional[datetime]
    message_count: int
    participant_roles: List[str]
    topic: str
    key_points: List[str] = []


class ValidationResult(BaseModel):
    """Result of validating a statement."""

    is_valid: bool
    confidence: float
    reasoning: str
    suggested_correction: Optional[str] = None


class ResolutionResult(BaseModel):
    """Result of resolving conflicting statements."""

    resolved_statement: str
    confidence: float
    reasoning: str
    supporting_facts: List[str] = []


class SubTopic(BaseModel):
    """Represents a sub-topic of a complex topic."""

    id: str
    parent_topic_id: Optional[str]
    content: str
    complexity: float
    required_expertise: List[str]


class TransparencyLevel(str, Enum):
    """Levels of transparency for processing details."""

    MINIMAL = "minimal"
    MODERATE = "moderate"
    DETAILED = "detailed"


class SessionMetrics(BaseModel):
    """Metrics about a chat session."""

    message_count: int
    average_response_time: float
    topic_coherence: float
    engagement_distribution: Dict[str, float]  # Role ID to engagement percentage


class RolePerformance(BaseModel):
    """Performance metrics for a role in a chat session."""

    role_id: str
    message_count: int
    average_response_length: int
    topic_relevance: float
    influence_score: float


class QualityMetrics(BaseModel):
    """Metrics about conversation quality."""

    coherence_score: float
    diversity_score: float
    depth_score: float
    factual_accuracy: float


class QualityIssue(BaseModel):
    """Represents an issue with conversation quality."""

    issue_type: str
    severity: float
    description: str
    affected_messages: List[str]
    suggested_action: str