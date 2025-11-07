"""Event type definitions for the agent engine event system."""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Enumeration of all possible event types in the system."""

    # Session lifecycle events
    SESSION_STARTED = "session_started"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"

    # Task lifecycle events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"

    # Agent execution events
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_OUTPUT = "tool_output"
    FINAL_RESPONSE = "final_response"

    # Permission events
    PERMISSION_REQUEST = "permission_request"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"

    # State management events
    STATE_CHANGED = "state_changed"

    # Error events
    ERROR = "error"

    # System events
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"

    # Service integration events
    INTENT_RECOGNIZED = "intent_recognized"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    PERMISSION_CHECKED = "permission_checked"
    SERVICE_HEALTH_CHANGED = "service_health_changed"
    METRICS = "metrics"


class BaseEvent(BaseModel, ABC):
    """Base class for all events in the system."""

    # Core event metadata
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    task_id: Optional[str] = None

    # Event metadata
    source: str = Field(default="agent_engine")
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None  # The event that caused this event

    # Event data
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

    @abstractmethod
    def get_summary(self) -> str:
        """Get a human-readable summary of the event."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        """Create event from dictionary."""
        # Map event_type string to EventType enum
        if isinstance(data.get("event_type"), str):
            data["event_type"] = EventType(data["event_type"])

        # Convert timestamp string back to datetime
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        # Convert UUID strings back to UUID objects
        for field in ["event_id", "correlation_id", "causation_id"]:
            if isinstance(data.get(field), str):
                data[field] = UUID(data[field])

        return cls(**data)


# Session Events
class SessionStartedEvent(BaseEvent):
    """Event emitted when a new session is started."""

    event_type: EventType = EventType.SESSION_STARTED

    # Session-specific data
    goal: str
    session_type: str = "default"
    participant_ids: list[str] = []

    def get_summary(self) -> str:
        return f"Session '{self.session_id}' started with goal: {self.goal[:50]}..."


class SessionCompletedEvent(BaseEvent):
    """Event emitted when a session is completed successfully."""

    event_type: EventType = EventType.SESSION_COMPLETED

    # Completion data
    final_response: Optional[str] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    duration_seconds: float = 0.0

    def get_summary(self) -> str:
        return f"Session '{self.session_id}' completed. {self.completed_tasks}/{self.total_tasks} tasks done in {self.duration_seconds:.1f}s"


class SessionFailedEvent(BaseEvent):
    """Event emitted when a session fails."""

    event_type: EventType = EventType.SESSION_FAILED

    # Error data
    error_message: str
    error_type: str
    completed_tasks: int = 0

    def get_summary(self) -> str:
        return f"Session '{self.session_id}' failed: {self.error_message[:50]}..."


# Task Events
class TaskStartedEvent(BaseEvent):
    """Event emitted when a new task is started."""

    event_type: EventType = EventType.TASK_STARTED

    # Task-specific data
    task_description: str
    task_type: str = "default"
    priority: int = 0

    def get_summary(self) -> str:
        return f"Task '{self.task_id}' started: {self.task_description[:50]}..."


class TaskCompletedEvent(BaseEvent):
    """Event emitted when a task is completed successfully."""

    event_type: EventType = EventType.TASK_COMPLETED

    # Completion data
    result: Optional[Any] = None
    duration_seconds: float = 0.0

    def get_summary(self) -> str:
        return f"Task '{self.task_id}' completed in {self.duration_seconds:.1f}s"


class TaskFailedEvent(BaseEvent):
    """Event emitted when a task fails."""

    event_type: EventType = EventType.TASK_FAILED

    # Error data
    error_message: str
    error_type: str
    retry_count: int = 0

    def get_summary(self) -> str:
        return f"Task '{self.task_id}' failed: {self.error_message[:50]}..."


# Agent Execution Events
class ThoughtEvent(BaseEvent):
    """Event representing agent's internal thinking process."""

    event_type: EventType = EventType.THOUGHT

    # Thought data
    content: str
    confidence: Optional[float] = None  # 0.0 to 1.0
    reasoning_type: str = "general"  # general, planning, reflection, etc.

    def get_summary(self) -> str:
        confidence_str = f" (confidence: {self.confidence:.2f})" if self.confidence else ""
        return f"Agent thought: {self.content[:50]}...{confidence_str}"


class ToolCallEvent(BaseEvent):
    """Event representing a tool call by the agent."""

    event_type: EventType = EventType.TOOL_CALL

    # Tool call data
    tool_name: str
    tool_args: Dict[str, Any]
    tool_id: Optional[str] = None

    def get_summary(self) -> str:
        args_str = str(self.tool_args)[:30] if self.tool_args else "{}"
        return f"Tool call: {self.tool_name}({args_str}...)"


class ToolOutputEvent(BaseEvent):
    """Event representing the output from a tool call."""

    event_type: EventType = EventType.TOOL_OUTPUT

    # Tool output data
    tool_name: str
    tool_id: Optional[str] = None
    output: Any
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None

    def get_summary(self) -> str:
        status = "success" if self.success else "failed"
        output_preview = str(self.output)[:30] if self.output else "None"
        return f"Tool {self.tool_name} {status}: {output_preview}..."


class FinalResponseEvent(BaseEvent):
    """Event representing the final response from the agent."""

    event_type: EventType = EventType.FINAL_RESPONSE

    # Response data
    content: str
    response_type: str = "text"  # text, json, etc.

    def get_summary(self) -> str:
        return f"Final response: {self.content[:50]}..."


# Permission Events
class PermissionRequestEvent(BaseEvent):
    """Event representing a permission request from the agent."""

    event_type: EventType = EventType.PERMISSION_REQUEST

    # Permission data
    tool_name: str
    tool_args: Dict[str, Any]
    permission_type: str = "execute"  # execute, read, write, etc.
    risk_level: str = "medium"  # low, medium, high, critical

    def get_summary(self) -> str:
        return f"Permission request: {self.tool_name} ({self.risk_level} risk)"


class PermissionGrantedEvent(BaseEvent):
    """Event representing a granted permission."""

    event_type: EventType = EventType.PERMISSION_GRANTED

    # Permission data
    tool_name: str
    granted_by: str = "user"

    def get_summary(self) -> str:
        return f"Permission granted for {self.tool_name} by {self.granted_by}"


class PermissionDeniedEvent(BaseEvent):
    """Event representing a denied permission."""

    event_type: EventType = EventType.PERMISSION_DENIED

    # Permission data
    tool_name: str
    denied_by: str = "user"
    reason: Optional[str] = None

    def get_summary(self) -> str:
        reason_str = f" ({self.reason})" if self.reason else ""
        return f"Permission denied for {self.tool_name} by {self.denied_by}{reason_str}"


# State Management Events
class StateChangedEvent(BaseEvent):
    """Event representing a state change in the agent or session."""

    event_type: EventType = EventType.STATE_CHANGED

    # State data
    old_state: Optional[str] = None
    new_state: str
    state_type: str = "agent"  # agent, session, task
    reason: Optional[str] = None

    def get_summary(self) -> str:
        old_str = f" from {self.old_state}" if self.old_state else ""
        reason_str = f" ({self.reason})" if self.reason else ""
        return f"{self.state_type.title()} state changed{old_str} to {self.new_state}{reason_str}"


# Error Events
class ErrorEvent(BaseEvent):
    """Event representing an error in the system."""

    event_type: EventType = EventType.ERROR

    # Error data
    error_message: str
    error_type: str
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    severity: str = "error"  # warning, error, critical

    def get_summary(self) -> str:
        return f"Error [{self.severity}]: {self.error_message[:50]}..."


# System Events
class SystemReadyEvent(BaseEvent):
    """Event indicating the system is ready."""

    event_type: EventType = EventType.SYSTEM_READY

    # System data
    version: str = "1.0.0"
    startup_time_ms: Optional[float] = None

    def get_summary(self) -> str:
        return f"System ready (v{self.version})"


class SystemShutdownEvent(BaseEvent):
    """Event indicating system shutdown."""

    event_type: EventType = EventType.SYSTEM_SHUTDOWN

    # Shutdown data
    reason: str = "normal"
    uptime_seconds: Optional[float] = None

    def get_summary(self) -> str:
        return f"System shutdown: {self.reason}"


# Event type mapping for dynamic event creation
EVENT_TYPE_MAP: Dict[EventType, Type[BaseEvent]] = {
    EventType.SESSION_STARTED: SessionStartedEvent,
    EventType.SESSION_COMPLETED: SessionCompletedEvent,
    EventType.SESSION_FAILED: SessionFailedEvent,
    EventType.TASK_STARTED: TaskStartedEvent,
    EventType.TASK_COMPLETED: TaskCompletedEvent,
    EventType.TASK_FAILED: TaskFailedEvent,
    EventType.THOUGHT: ThoughtEvent,
    EventType.TOOL_CALL: ToolCallEvent,
    EventType.TOOL_OUTPUT: ToolOutputEvent,
    EventType.FINAL_RESPONSE: FinalResponseEvent,
    EventType.PERMISSION_REQUEST: PermissionRequestEvent,
    EventType.PERMISSION_GRANTED: PermissionGrantedEvent,
    EventType.PERMISSION_DENIED: PermissionDeniedEvent,
    EventType.STATE_CHANGED: StateChangedEvent,
    EventType.ERROR: ErrorEvent,
    EventType.SYSTEM_READY: SystemReadyEvent,
    EventType.SYSTEM_SHUTDOWN: SystemShutdownEvent,
}


def create_event(event_type: Union[str, EventType], **kwargs) -> BaseEvent:
    """
    Factory function to create events dynamically.

    Args:
        event_type: The type of event to create
        **kwargs: Additional event-specific parameters

    Returns:
        An instance of the appropriate event class

    Raises:
        ValueError: If the event type is unknown
    """
    try:
        if isinstance(event_type, str):
            event_type = EventType(event_type)
    except ValueError as e:
        raise ValueError(f"Unknown event type: {event_type}") from e

    if event_type not in EVENT_TYPE_MAP:
        raise ValueError(f"Unknown event type: {event_type}")

    event_class = EVENT_TYPE_MAP[event_type]
    return event_class(event_type=event_type, **kwargs)


# Event filtering and utility functions
def is_session_event(event: BaseEvent) -> bool:
    """Check if event is related to session lifecycle."""
    return event.event_type in [
        EventType.SESSION_STARTED,
        EventType.SESSION_COMPLETED,
        EventType.SESSION_FAILED
    ]


def is_task_event(event: BaseEvent) -> bool:
    """Check if event is related to task lifecycle."""
    return event.event_type in [
        EventType.TASK_STARTED,
        EventType.TASK_COMPLETED,
        EventType.TASK_FAILED
    ]


def is_execution_event(event: BaseEvent) -> bool:
    """Check if event is related to agent execution."""
    return event.event_type in [
        EventType.THOUGHT,
        EventType.TOOL_CALL,
        EventType.TOOL_OUTPUT,
        EventType.FINAL_RESPONSE
    ]


def is_error_event(event: BaseEvent) -> bool:
    """Check if event represents an error condition."""
    return event.event_type in [
        EventType.ERROR,
        EventType.TASK_FAILED,
        EventType.SESSION_FAILED
    ]


def is_permission_event(event: BaseEvent) -> bool:
    """Check if event is related to permissions."""
    return event.event_type in [
        EventType.PERMISSION_REQUEST,
        EventType.PERMISSION_GRANTED,
        EventType.PERMISSION_DENIED
    ]


# Service Integration Events
class IntentRecognizedEvent(BaseEvent):
    """Event representing intent recognition result."""

    event_type: EventType = EventType.INTENT_RECOGNIZED

    # Intent recognition data
    service_name: str
    intent: str
    confidence: float
    input_text: str
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    strategy_used: Optional[str] = None
    reasoning: Optional[str] = None

    def get_summary(self) -> str:
        return f"Intent recognized: {self.intent} (confidence: {self.confidence:.2f}) by {self.service_name}"


class ExecutionStartedEvent(BaseEvent):
    """Event representing execution started."""

    event_type: EventType = EventType.EXECUTION_STARTED

    # Execution data
    service_name: str
    execution_id: str
    intent: str
    parameters: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

    def get_summary(self) -> str:
        return f"Execution started: {self.execution_id} for intent {self.intent} by {self.service_name}"


class ExecutionCompletedEvent(BaseEvent):
    """Event representing execution completed."""

    event_type: EventType = EventType.EXECUTION_COMPLETED

    # Execution data
    service_name: str
    execution_id: str
    intent: str
    success: bool
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    context: Dict[str, Any] = {}

    def get_summary(self) -> str:
        status = "completed successfully" if self.success else "failed"
        time_str = f" in {self.execution_time_ms:.1f}ms" if self.execution_time_ms else ""
        return f"Execution {status}: {self.execution_id}{time_str} by {self.service_name}"


class PermissionCheckedEvent(BaseEvent):
    """Event representing permission check result."""

    event_type: EventType = EventType.PERMISSION_CHECKED

    # Permission data
    service_name: str
    action: str
    allowed: bool
    confidence: float
    reason: Optional[str] = None
    risk_level: str = "low"
    rules_applied: List[str] = []
    context: Dict[str, Any] = {}

    def get_summary(self) -> str:
        status = "allowed" if self.allowed else "denied"
        return f"Permission {status}: {self.action} by {self.service_name} (risk: {self.risk_level})"


class ServiceHealthChangedEvent(BaseEvent):
    """Event representing service health status change."""

    event_type: EventType = EventType.SERVICE_HEALTH_CHANGED

    # Health data
    service_name: str
    healthy: bool
    details: Dict[str, Any] = {}

    def get_summary(self) -> str:
        status = "healthy" if self.healthy else "unhealthy"
        return f"Service {self.service_name} is now {status}"


class MetricsEvent(BaseEvent):
    """Event representing service metrics."""

    event_type: EventType = EventType.METRICS

    # Metrics data
    service_name: str
    metrics: Dict[str, Any] = {}
    context: Dict[str, Any] = {}

    def get_summary(self) -> str:
        count = len(self.metrics)
        return f"Metrics published by {self.service_name}: {count} metrics"


# Add service integration events to the mapping
EVENT_TYPE_MAP.update({
    EventType.INTENT_RECOGNIZED: IntentRecognizedEvent,
    EventType.EXECUTION_STARTED: ExecutionStartedEvent,
    EventType.EXECUTION_COMPLETED: ExecutionCompletedEvent,
    EventType.PERMISSION_CHECKED: PermissionCheckedEvent,
    EventType.SERVICE_HEALTH_CHANGED: ServiceHealthChangedEvent,
    EventType.METRICS: MetricsEvent,
})