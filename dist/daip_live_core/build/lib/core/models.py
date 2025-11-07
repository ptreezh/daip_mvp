import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union
from datetime import timezone

from pydantic import BaseModel, Field, ConfigDict


class PermissionResponse(Enum):
    """User response to permission requests."""
    GRANT = "grant"      # Grant this permission
    DENY = "deny"        # Deny this permission  
    ALWAYS = "always"    # Always grant for this tool
    NEVER = "never"      # Never grant for this tool
    CANCEL = "cancel"    # Cancel the operation
    
    @classmethod
    def from_string(cls, input_str: str) -> 'PermissionResponse':
        """Convert string input to PermissionResponse, case-insensitive.
        
        Args:
            input_str: User input string
            
        Returns:
            PermissionResponse: Corresponding permission response
            
        Note:
            Invalid inputs default to DENY for security.
        """
        if not input_str:
            return cls.DENY  # Safety first: default to deny
        
        input_lower = input_str.lower().strip()
        
        # Single character responses
        if input_lower == 'y':
            return cls.GRANT
        elif input_lower == 'n':
            return cls.DENY
        elif input_lower == 'a':
            return cls.ALWAYS
        elif input_lower == 'v':
            return cls.NEVER
        elif input_lower == 'c':
            return cls.CANCEL
        
        # Full word responses
        elif input_lower == 'yes':
            return cls.GRANT
        elif input_lower == 'no':
            return cls.DENY
        elif input_lower == 'always':
            return cls.ALWAYS
        elif input_lower == 'never':
            return cls.NEVER
        elif input_lower == 'cancel':
            return cls.CANCEL
        
        # Default to DENY for security
        else:
            return cls.DENY


class PermissionState(Enum):
    """State of permission request processing."""
    PENDING = "pending"      # Waiting for user response
    GRANTED = "granted"      # Permission granted
    DENIED = "denied"        # Permission denied
    REMEMBERED = "remembered" # User choice remembered
    CANCELLED = "cancelled"  # Operation cancelled


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
    state: int
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
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content: str


class Session(BaseModel):
    """
    Represents the complete record of a multi-agent interaction.
    """
    session_id: str = Field(default_factory=lambda: f"session_{uuid.uuid4()}")
    session_type: Literal["debate", "chat", "workflow", "compression", "auto_compression"]
    goal: str  # The overall goal or topic of the session

    # Participants
    participant_ids: List[str]

    # Timestamps & Status
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
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
    request_id: str = Field(default_factory=lambda: f"perm_{uuid.uuid4().hex[:16]}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: float = Field(default=30.0, description="Timeout for user response")
    risk_level: Literal["low", "medium", "high"] = Field(default="medium", description="Risk level of the requested operation")
    description: Optional[str] = Field(default=None, description="Human-readable description of the operation")


class PermissionResult(BaseModel):
    """Result of permission request processing."""
    granted: bool
    response: PermissionResponse
    request_id: str
    reason: Optional[str] = None
    timeout: bool = False
    duplicate: bool = False
    circuit_breaker_open: bool = False
    remembered: bool = False
    error_message: Optional[str] = None
    needs_manual_review: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_seconds: float = Field(default=0.0, description="Time taken to process the permission request")


class PermissionInteraction(BaseModel):
    """Represents a permission interaction with robust state management."""
    request_id: str = Field(default_factory=lambda: f"perm_{uuid.uuid4().hex[:16]}")
    tool_name: str
    args: Dict[str, Any]
    state: PermissionState = Field(default=PermissionState.PENDING)
    response: Optional[PermissionResponse] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    timeout_seconds: float = Field(default=30.0, description="Timeout for this permission interaction")
    user_choice: Optional[str] = None
    error_count: int = Field(default=0, description="Number of errors encountered during processing")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    max_retries: int = Field(default=3, description="Maximum number of retries allowed")
    circuit_breaker_open: bool = Field(default=False, description="Whether circuit breaker is open for this request")
    is_duplicate: bool = Field(default=False, description="Whether this is a duplicate request")
    
    def update_response(self, response: PermissionResponse) -> None:
        """Update the permission interaction with user response."""
        if self.state != PermissionState.PENDING:
            raise ValueError(f"Cannot update response for non-pending interaction (current state: {self.state})")
        
        self.response = response
        self.last_updated = datetime.now(timezone.utc)
        
        # Update state based on response
        if response == PermissionResponse.GRANT:
            self.state = PermissionState.GRANTED
        elif response == PermissionResponse.DENY:
            self.state = PermissionState.DENIED
        elif response == PermissionResponse.CANCEL:
            self.state = PermissionState.CANCELLED
        elif response in [PermissionResponse.ALWAYS, PermissionResponse.NEVER]:
            self.state = PermissionState.REMEMBERED
    
    def mark_as_remembered(self) -> None:
        """Mark this interaction as remembered."""
        if self.response not in [PermissionResponse.ALWAYS, PermissionResponse.NEVER]:
            raise ValueError("Can only mark as remembered if response is ALWAYS or NEVER")
        self.state = PermissionState.REMEMBERED
        self.last_updated = datetime.now(timezone.utc)
    
    def mark_as_duplicate(self) -> None:
        """Mark this interaction as a duplicate."""
        self.is_duplicate = True
        self.last_updated = datetime.now(timezone.utc)
    
    def increment_error_count(self) -> None:
        """Increment the error count."""
        self.error_count += 1
        self.last_updated = datetime.now(timezone.utc)
    
    def increment_retry_count(self) -> None:
        """Increment the retry count."""
        self.retry_count += 1
        self.last_updated = datetime.now(timezone.utc)
    
    def can_retry(self) -> bool:
        """Check if this interaction can be retried."""
        return self.retry_count < self.max_retries and self.error_count < 5
    
    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        """Check if this permission interaction has expired."""
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        elapsed = (current_time - self.timestamp).total_seconds()
        return elapsed > self.timeout_seconds
    
    def is_stale(self, current_time: Optional[datetime] = None, stale_threshold: float = 300.0) -> bool:
        """Check if this permission interaction is stale (completed but old)."""
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        if self.state == PermissionState.PENDING:
            return False  # Pending interactions are checked with is_expired
        
        elapsed = (current_time - self.last_updated).total_seconds()
        return elapsed > stale_threshold
    
    def to_result(self) -> PermissionResult:
        """Convert this interaction to a PermissionResult."""
        if self.state == PermissionState.PENDING:
            raise ValueError("Cannot convert pending interaction to result")
        
        if self.response is None:
            raise ValueError("Cannot convert interaction without response to result")
        
        granted = self.state == PermissionState.GRANTED
        response_time = (self.last_updated - self.timestamp).total_seconds()
        
        return PermissionResult(
            granted=granted,
            response=self.response,
            request_id=self.request_id,
            timeout=self.is_expired(),
            duplicate=self.is_duplicate,
            circuit_breaker_open=self.circuit_breaker_open,
            remembered=self.state == PermissionState.REMEMBERED,
            response_time_seconds=response_time,
            timestamp=self.last_updated
        )
    
    def validate(self) -> None:
        """Validate this permission interaction."""
        if not self.tool_name or not self.tool_name.strip():
            raise ValueError("Tool name cannot be empty")
        
        if not isinstance(self.args, dict):
            raise ValueError("Args must be a dictionary")
        
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")
        
        if self.response is not None and self.state == PermissionState.PENDING:
            raise ValueError("Cannot have response in PENDING state")
        
        if self.state != PermissionState.PENDING and self.response is None:
            raise ValueError("Non-pending interaction must have response")
    
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)

class FinalResponseEvent(BaseModel):
    type: Literal["final_response"] = "final_response"
    content: str

class TokenUsageEvent(BaseModel):
    type: Literal["token_usage"] = "token_usage"
    usage_info: Dict[str, Any]

class ModelMetricsEvent(BaseModel):
    type: Literal["model_metrics"] = "model_metrics"
    latency: float
    request_count: int

class DebateStartEvent(BaseModel):
    type: Literal["debate_start"] = "debate_start"
    topic: str
    roles: List[str]
    rounds: int
    session_id: str

class DebateRoundStartEvent(BaseModel):
    type: Literal["debate_round_start"] = "debate_round_start"
    round_number: int
    total_rounds: int
    session_id: str

class DebateTurnStartEvent(BaseModel):
    type: Literal["debate_turn_start"] = "debate_turn_start"
    participant: str
    round_number: int
    session_id: str

class DebateTurnCompleteEvent(BaseModel):
    type: Literal["debate_turn_complete"] = "debate_turn_complete"
    participant: str
    round_number: int
    content_preview: str
    session_id: str

class DebateCompleteEvent(BaseModel):
    type: Literal["debate_complete"] = "debate_complete"
    session_id: str
    summary: str

AgentEvent = Union[
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    ResponseChunkEvent,
    ErrorEvent,
    PermissionRequestEvent,
    FinalResponseEvent,
    TokenUsageEvent,
    ModelMetricsEvent,
    DebateStartEvent,
    DebateRoundStartEvent,
    DebateTurnStartEvent,
    DebateTurnCompleteEvent,
    DebateCompleteEvent,
]


class KnowledgeSource(BaseModel):
    file_path: str
    file_hash: str
    status: Literal["indexed", "pending", "error"] = "pending"
    id: Optional[int] = None
    indexed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeBaseChanges(BaseModel):
    added: List[str] = Field(default_factory=list)
    updated: List[Tuple[str, KnowledgeSource]] = Field(default_factory=list)
    deleted: List[KnowledgeSource] = Field(default_factory=list)
    unchanged: List[KnowledgeSource] = Field(default_factory=list)


class ProviderConfig(BaseModel):
    model: str
    embedding_model: Optional[str] = None
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
