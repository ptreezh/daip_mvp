from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field


# --- Document Analysis Models ---
class DocumentAnalysisRequest(BaseModel):
    content: str
    use_all_tools: bool = False

class DocumentAnalysisResponse(BaseModel):
    message_type: str
    content: str
    tool_calls: Optional[list] = None
    task_id: Optional[str] = None

class DocumentParsingResponse(BaseModel):
    task_id: str
    status: str
    content: str # Changed from 'message' for consistency
    parsing_stats: Optional[dict[str, Any]] = None
    chunks: Optional[list[dict[str, Any]]] = None

class DocumentUploadResponse(BaseModel):
    task_id: str
    filename: str
    file_size: int
    status: str
    content: str # Changed from 'message' for consistency

# --- Role and Expert Models ---
class Role(BaseModel):
    name: str
    desc: str

class SmartRoleCreateRequest(BaseModel):
    role_name: str
    role_definition: str
    category: Optional[str] = "通用"
    specialties: Optional[list[str]] = []
    skills: Optional[list[str]] = []
    experience_years: Optional[int] = 5
    reputation_score: Optional[float] = 80.0
    languages: Optional[list[str]] = ["中文", "英文"]
    availability: Optional[str] = "可用"
    location: Optional[str] = ""
    education: Optional[list[str]] = []
    certifications: Optional[list[str]] = []
    projects: Optional[list[str]] = []

class BatchRoleImportRequest(BaseModel):
    roles: list[dict[str, Any]]
    overwrite_existing: bool = False
    validate_only: bool = False

# --- Chat Models ---
class ChatMessage(BaseModel):
    sender_name: str = Field(..., description="发送者姓名")
    content: str = Field(..., min_length=1, description="消息内容")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")

class MultiRoleChatRequest(BaseModel):
    topic: str
    roles: list[str]
    messages: list[ChatMessage]

class MultiRoleChatResponse(BaseModel):
    new_message: ChatMessage

# --- Protocol Models ---
class IntelligentProtocolRequest(BaseModel):
    user_request: str = Field(..., description="用户的自然语言需求")
    use_analysis: bool = Field(True, description="是否使用任务分析增强")
    should_validate: bool = Field(True, description="是否验证生成的协议")
    save_to_file: bool = Field(False, description="是否保存到文件")
    output_path: Optional[str] = Field(None, description="输出文件路径")

# --- Tool Models ---
class FileOpRequest(BaseModel):
    path: str
    encoding: Optional[str] = "utf-8"
    content: Optional[str] = None
    tree: Optional[dict] = None

class MemoryBankRequest(BaseModel):
    role_name: str
    content: Optional[str] = None

class MemoryEntryRequest(BaseModel):
    agent_id: str
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    embedding: Optional[list[float]] = None
    memory_id: Optional[str] = None
    limit: Optional[int] = None
    tag: Optional[str] = None
    keyword: Optional[str] = None
    after: Optional[float] = None
    before: Optional[float] = None
    top_k: Optional[int] = None

class WikiEntryRequest(BaseModel):
    entry: str
    content: Optional[str] = None
    editor: Optional[str] = None
    timestamp: Optional[str] = None
    version: Optional[int] = None

class PromptOptimizationRequest(BaseModel):
    user_input: str

class PromptOptimizationResponse(BaseModel):
    insights: list[dict[str, Any]]
    structured_json: Optional[dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None

# --- Fact & Memory Models ---
class PendingFact(BaseModel):
    """Represents a fact that has been extracted but is pending verification and processing.
    This model is used by services like FactExtractionService and MemoryService.
    """

    content: str = Field(..., description="The textual content of the extracted fact.")
    source: str = Field(
        ..., description="The origin of the fact (e.g., document name, agent message ID)."
    )
    confidence: float = Field(
        default=0.5, ge=0.0, le=1.0, description="The confidence score of the extraction (0.0 to 1.0)."
    )
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="Additional metadata about the fact.")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of when the fact was extracted.")

# --- Collaboration Models ---
class TaskStatus(str):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    REJECTED = "rejected"

class TaskBase(BaseModel):
    title: str
    description: str = ""
    stage: str
    knowledge_point_id: str = ""
    assigned_to: Optional[str] = None
    due_time: Optional[datetime] = None

class Task(TaskBase):
    id: str
    status: str = TaskStatus.NOT_STARTED
    progress: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    history: list[dict] = Field(default_factory=list)
    comments: list[dict] = Field(default_factory=list)
    signatures: list[dict] = Field(default_factory=list)

# --- Advanced Engine Models ---
class AutoCollabEditRequest(BaseModel):
    instruction: str

class AutoCollabEditResponse(BaseModel):
    entry: str
    topic: str
    experts: list
    rounds: int
    status: str
    consensus_results: list

# --- Virtual Team Models ---
class CreateVirtualProjectRequest(BaseModel):
    name: str
    description: str
    creator: str
    initial_roles: Optional[list[str]] = []
    config: Optional[dict[str, Any]] = {}

class VirtualProject(BaseModel):
    project_id: str
    name: str
    description: str
    status: Any # Will use ProjectStatus enum
    created_at: str
    updated_at: str
    creator: str
    assigned_roles: list[str] = Field(default_factory=list)
    memory_bank_path: str
    config: Dict[str, Any] = Field(default_factory=dict)

class CreateVirtualTaskRequest(BaseModel):
    project_id: str
    title: str
    description: str
    assigned_role: str
    priority: int = 5
    dependencies: Optional[list[str]] = []

from enum import Enum


class ProjectStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    CANCELLED = "cancelled"

class RoleContext(BaseModel):
    role_id: str
    project_id: str
    context_data: dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)

class AssignRoleRequest(BaseModel):
    project_id: str
    role_id: str

# --- Protocol Execution Models ---
class ProtocolExecutionRequest(BaseModel):
    protocol_id: str = Field(..., description="协议ID")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入参数")

# --- Collaboration Models (from legacy) ---
class CollaborationUser(BaseModel):
    id: str
    name: str
    email: str
    role: str
    online: bool = False
    last_activity: str = ""

class CollaborationProject(BaseModel):
    id: str
    name: str
    description: str
    message_type: str
    creator: str
    participants: list[str] = Field(default_factory=list)
    status: str = "active"
    created_at: str
    updated_at: str

# --- Advanced Engine Models (from legacy) ---

# Blockchain Consensus
class ConsensusSessionRequest(BaseModel):
    session_id: str
    algorithm: str = "proof_of_authority"
    topic: str
    description: str = ""

class ExpertRegistrationRequest(BaseModel):
    session_id: str
    expert_id: str
    name: str
    category: str
    reputation_score: float = 80.0
    stake_weight: float = 1.0
    authority_level: int = 3
    specialties: list[str] = Field(default_factory=list)

class OpinionSubmissionRequest(BaseModel):
    session_id: str
    expert_id: str
    content: str
    confidence: float
    supporting_evidence: list[str] = Field(default_factory=list)

# Shor Task Decomposer
class TaskDecompositionRequest(BaseModel):
    task_name: str
    description: str
    complexity: str = "moderate"
    estimated_time: float = 10.0
    required_skills: list[str] = Field(default_factory=list)
    priority: int = 5
    dependencies: list[str] = Field(default_factory=list)

# Cognitive Conflict GAN
class ConflictGenerationRequest(BaseModel):
    session_id: str
    context: dict[str, Any]
    target_intensity: str = "moderate"
    primary_concept: str
    secondary_concept: str = ""

class ContinuousConflictRequest(BaseModel):
    session_id: str
    context: dict[str, Any]
    duration_minutes: int = 60
    conflict_interval_minutes: int = 10

class ConflictFeedbackRequest(BaseModel):
    session_id: str
    conflict_id: str
    user_satisfaction: float
    resolution_time: float
    creativity_boost: float

# Intelligent Chatroom
class ChatSessionRequest(BaseModel):
    user_id: str

class ChatMessageRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")

# Expert Library
class ExpertSearchRequest(BaseModel):
    query: str = ""
    category: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    limit: int = 10

class ExpertCreateRequest(BaseModel):
    name: str
    title: str = ""
    category: str = "通用"
    specialties: list[str] = Field(default_factory=list)
    description: str = ""
    experience_years: int = 0
    reputation_score: float = 80.0
    contact_info: dict[str, str] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["中文"])
    availability: str = "可用"
    hourly_rate: Optional[float] = None
    location: str = ""
    education: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    bio: str = ""

class ExpertUpdateRequest(BaseModel):
    updates: dict[str, Any]

# --- Debate Protocol Models ---
class DebateConfig(BaseModel):
    """Configuration for a new debate session.

    This model defines all the parameters required to initialize and run a debate,
    including the topic, participants, and rules of engagement.
    """

    topic: str = Field(..., description="The central topic of the debate.")
    roles: list[str] = Field(..., description="A list of role IDs participating in the debate.")
    rounds: int = Field(default=2, description="The number of full rounds in the debate.")
    turn_taking_policy: Literal['round_robin'] = Field(
        default='round_robin', description="The policy for turn-taking among roles."
    )
    consensus_strategy: str = Field(
        default='simple_majority_vote',
        description="The name of the consensus strategy tool to be executed."
    )


class DebateTurn(BaseModel):
    """Represents a single turn taken by a role during the debate.

    This model captures the output of a role's contribution at a specific point
    in the debate.
    """

    role_id: str = Field(..., description="The ID of the role that took the turn.")
    opinion: str = Field(..., description="The content of the role's opinion or argument.")
    round: int = Field(..., description="The debate round number in which this turn occurred.")


class DebateResult(BaseModel):
    """The final, structured output of a completed debate protocol.

    This model aggregates the entire debate history, the outcome of the consensus
    process, and the final synthesized summary.
    """

    topic: str = Field(..., description="The original topic of the debate.")
    history: list[DebateTurn] = Field(
        ..., description="A complete history of all turns taken during the debate."
    )
    consensus_outcome: Any = Field(
        ..., description="The result from the executed consensus strategy."
    )
    synthesis: str = Field(
        ..., description="A final, synthesized summary of the entire debate."
    )

# --- Debate Protocol Events & Commands ---
# These models are used for communication between the debate engine and clients like the TUI.

# --- Commands ---
class UserInterventionCommand(BaseModel):
    """Command sent when a user intervenes with their own input."""

    command_type: Literal["user_intervention"] = "user_intervention"
    content: str

# A union of all possible commands
commands = Union[
    UserInterventionCommand,
]


# --- Events ---
class Event(BaseModel):
    """The base model for all events, containing common fields."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str


class DebateStartEvent(Event):
    """Event fired when a debate officially begins."""

    event_type: Literal["debate_start"] = "debate_start"
    config: DebateConfig


class NewTurnEvent(Event):
    """Event fired when a new turn (AI or user) is added to the history."""

    event_type: Literal["new_turn"] = "new_turn"
    turn: DebateTurn


class TechLogEvent(Event):
    """Event for displaying internal technical processes to the user.
    Used for the --verbose mode. Contains structured information for better debugging.
    """

    event_type: Literal["tech_log"] = "tech_log"
    source: str  # e.g., "SynthesisEngine", "MemoryService"
    message: str
    module: Optional[str] = None
    function: Optional[str] = None


class DebateEndEvent(Event):
    """Event fired when the debate has concluded and results are available."""

    event_type: Literal["debate_end"] = "debate_end"
    result: DebateResult


class ErrorEvent(Event):
    """Event for reporting an error from the backend engine."""

    event_type: Literal["error"] = "error"
    error_message: str
    details: str | None = None


class ClearScreenEvent(Event):
    """Event that signals the UI to clear the main output area."""

    event_type: Literal["clear_screen"] = "clear_screen"


DebateEvent = Union[
    DebateStartEvent,
    NewTurnEvent,
    TechLogEvent,
    DebateEndEvent,
    ErrorEvent,
    ClearScreenEvent,
]
