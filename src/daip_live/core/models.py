import uuid
from datetime import datetime
from enum import Enum, auto
from typing import List, Literal, Optional, Dict, Any, Set, Tuple, Union

from pydantic import BaseModel, Field, field_validator


class AgentState(Enum):
    """Represents the internal state of the AgentExecutor."""
    IDLE = auto()
    INIT = auto()  # Added for session status
    RUNNING = auto() # Added for session status
    COMPLETED = auto() # Added for session status
    FAILED = auto() # Added for session status
    OBSERVING = auto()
    THINKING = auto()
    EVALUATING = auto()
    REFLECTING = auto()
    EXPLORING = auto()
    SYNTHESIZING = auto()
    EXECUTING_TOOL = auto()
    RESPONDING = auto()
    FINALIZING = auto()
    ERROR = auto()


class AgentStatus(BaseModel):
    """A snapshot of the AgentExecutor's real-time state."""
    state: AgentState
    model_name: str
    tokens_used: int
    tokens_total: int


class TodoItem(BaseModel):
    id: Optional[int] = None
    description: str
    status: Literal["pending", "in_progress", "completed"] = "pending"
    priority: int = 1


class Role(BaseModel):
    name: str
    persona: str
    tools: List[str]


# --- New Session and Dialogue Models (Multi-Agent) ---

class DialogueTurn(BaseModel):
    """A single utterance from a participant in a session."""
    participant_id: str  # e.g., "user_human", "role_pro_01", "role_con_02"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str


class Session(BaseModel):
    """
    Represents the complete record of a multi-agent interaction.
    """
    session_id: str = Field(default_factory=lambda: f"session_{uuid.uuid4()}")
    session_type: Literal["debate", "chat", "workflow"]
    goal: str  # The overall goal or topic of the session

    # Participants
    participant_ids: List[str]

    # Timestamps & Status
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    status: AgentState = AgentState.INIT # Represents the state of the session orchestration

    # Content
    history: List[DialogueTurn] = []
    compressed_history: Optional[str] = None  # Mid-term memory
    summary: Optional[str] = None


# --- End New Session Models ---


class AssistantState(BaseModel):
    mode: Literal["NORMAL", "ASSISTANT_ACTIVE"] = "NORMAL"
    current_session_id: Optional[int] = None
    active_workflow: Optional[str] = None


class ConsensusResult(BaseModel):
    topic: str
    proposals: Dict[str, str]
    final_consensus: str
    contributing_roles: List[str]


class ThoughtEvent(BaseModel):
    type: Literal["thought"] = "thought"
    content: str

class ToolCallEvent(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    tool_name: str
    args: Dict[str, Any]

class ToolOutputEvent(BaseModel):
    type: Literal["tool_output"] = "tool_output"
    tool_name: str
    status: Literal["success", "error"]
    output: str

class ResponseChunkEvent(BaseModel):
    type: Literal["response_chunk"] = "response_chunk"
    delta: str

class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str

class PermissionRequestEvent(BaseModel):
    type: Literal["permission_request"] = "permission_request"
    tool_name: str
    args: Dict[str, Any]

class FinalResponseEvent(BaseModel):
    type: Literal["final_response"] = "final_response"
    content: str


AgentEvent = Union[
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    ResponseChunkEvent,
    ErrorEvent,
    PermissionRequestEvent,
    FinalResponseEvent,
]


class KnowledgeSource(BaseModel):
    file_path: str
    file_hash: str
    status: Literal["indexed", "pending", "error"] = "pending"
    id: Optional[int] = None
    indexed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeBaseChanges(BaseModel):
    added: List[str] = Field(default_factory=list)
    updated: List[Tuple[str, KnowledgeSource]] = Field(default_factory=list)
    deleted: List[KnowledgeSource] = Field(default_factory=list)
    unchanged: List[KnowledgeSource] = Field(default_factory=list)


class ProviderConfig(BaseModel):
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    num_retries: int = 3


# New: SessionContext for ToolManager preconditions
class SessionContext(BaseModel):
    recently_read_resources: Set[str] = Field(default_factory=set)


class ToolPermissionConfig(BaseModel):
    default: Literal["allow", "deny", "ask"] = "deny"
    tools: Dict[str, Literal["allow", "deny", "ask"]] = Field(default_factory=dict)


# --- Configuration Models ---
# Moved from config.py to be part of the core project contract (P0)

class DatabaseConfig(BaseModel):
    """Pydantic model for database configuration."""
    path: str = Field(..., description="Path to the SQLite database file.")

class LLMProviderConfig(BaseModel):
    """Pydantic model for LLM provider configuration."""
    default_model: str = Field(..., description="The default model for generation tasks.")
    embedding_model: str = Field(..., description="The model used for creating embeddings.")

class KnowledgeBaseConfig(BaseModel):
    """Pydantic model for knowledge base configuration."""
    directory: str = Field(..., description="Path to the root directory for knowledge documents.")

class RoleManagerConfig(BaseModel):
    """Pydantic model for role manager configuration."""
    roles_dir: str = Field(..., description="Path to the directory containing role definitions.")

class AppConfig(BaseModel):
    """Top-level Pydantic model for the entire application configuration."""
    database: DatabaseConfig
    llm_provider: LLMProviderConfig
    knowledge_base: KnowledgeBaseConfig
    role_manager: RoleManagerConfig