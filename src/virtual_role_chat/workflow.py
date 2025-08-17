"""PocketFlow workflow interfaces and integration points for the Virtual Role Chat System.

This module defines the interfaces and models for integrating PocketFlow as a lightweight
workflow engine to orchestrate role interactions and conversation flows.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from pydantic import BaseModel

try:
    from pocketflow import Workflow, WorkflowEngine
    from pocketflow import WorkflowStep as PFWorkflowStep
    POCKETFLOW_AVAILABLE = True
except ImportError:
    POCKETFLOW_AVAILABLE = False
    # Define placeholder classes if PocketFlow is not available
    class Workflow:
        pass
    class WorkflowEngine:
        pass
    class PFWorkflowStep:
        pass

from .models import SessionID


class WorkflowState(str, Enum):
    """States of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowEventType(str, Enum):
    """Types of workflow events."""

    USER_INPUT = "user_input"
    ROLE_RESPONSE = "role_response"
    TOPIC_CHANGE = "topic_change"
    CONFLICT_DETECTED = "conflict_detected"
    CONSENSUS_REACHED = "consensus_reached"
    QUALITY_ISSUE = "quality_issue"
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"
    SESSION_END = "session_end"


class WorkflowEvent(BaseModel):
    """Represents an event in a workflow."""

    id: str
    type: WorkflowEventType
    session_id: SessionID
    timestamp: datetime
    data: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class WorkflowAction(BaseModel):
    """Represents an action to be executed in a workflow."""

    id: str
    name: str
    type: str  # e.g., "role_response", "validation", "synthesis"
    parameters: Dict[str, Any] = {}
    dependencies: List[str] = []  # IDs of actions this depends on
    timeout_seconds: Optional[int] = None


class WorkflowStep(BaseModel):
    """Represents a step in a workflow."""

    id: str
    name: str
    description: str = ""
    actions: List[WorkflowAction] = []
    conditions: Dict[str, Any] = {}  # Conditions for step execution
    next_steps: List[str] = []  # IDs of possible next steps


class ConversationWorkflow(BaseModel):
    """Defines a conversation workflow."""

    id: str
    name: str
    description: str = ""
    mode: str  # "free_form", "structured", "debate"
    initial_step: str
    steps: List[WorkflowStep] = []


class WorkflowExecution(BaseModel):
    """Represents a workflow execution instance."""

    id: str
    workflow_id: str
    session_id: SessionID
    state: WorkflowState
    current_step: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = {}


class TaskDecomposition(BaseModel):
    """Represents a decomposition of a complex task."""

    id: str
    parent_task_id: Optional[str] = None
    title: str
    description: str
    subtasks: List[str] = []
    assigned_roles: List[str] = []
    dependencies: List[str] = []


class ProcessingChain(BaseModel):
    """Represents a chain of processing steps."""

    id: str
    name: str
    steps: List[str] = []
    current_step_index: int = 0
    is_complete: bool = False


@runtime_checkable
class WorkflowEngineInterface(Protocol):
    """Interface for a workflow engine."""

    def start_workflow(self, workflow_id: str, session_id: SessionID) -> WorkflowExecution:
        """Start a workflow execution."""
        ...

    def execute_step(self, execution_id: str, step_id: str) -> bool:
        """Execute a workflow step."""
        ...

    def get_execution_status(self, execution_id: str) -> WorkflowExecution:
        """Get the status of a workflow execution."""
        ...


@runtime_checkable
class WorkflowStateManagerInterface(Protocol):
    """Interface for managing workflow state."""

    def save_state(self, execution: WorkflowExecution) -> bool:
        """Save workflow execution state."""
        ...

    def load_state(self, execution_id: str) -> WorkflowExecution:
        """Load workflow execution state."""
        ...


@runtime_checkable
class TaskDecompositionServiceInterface(Protocol):
    """Interface for task decomposition service."""

    def decompose_task(self, task_description: str) -> TaskDecomposition:
        """Decompose a complex task into subtasks."""
        ...


@runtime_checkable
class WorkflowAdapterInterface(Protocol):
    """Interface for workflow adapter."""

    def adapt_workflow(self, workflow: ConversationWorkflow, context: Dict[str, Any]) -> ConversationWorkflow:
        """Adapt a workflow based on context."""
        ...


# Define standard workflows
FREE_FORM_WORKFLOW = ConversationWorkflow(
    id="free_form",
    name="Free Form Discussion",
    description="A flexible discussion workflow with minimal structure",
    mode="free_form",
    initial_step="start",
    steps=[
        WorkflowStep(
            id="start",
            name="Start Discussion",
            description="Initial discussion phase",
            actions=[
                WorkflowAction(
                    id="user_input",
                    name="Process User Input",
                    type="user_input"
                )
            ]
        )
    ]
)

STRUCTURED_WORKFLOW = ConversationWorkflow(
    id="structured",
    name="Structured Discussion",
    description="A structured discussion workflow with defined phases",
    mode="structured",
    initial_step="topic_introduction",
    steps=[
        WorkflowStep(
            id="topic_introduction",
            name="Topic Introduction",
            description="Introduction and definition of the topic"
        )
    ]
)

DEBATE_WORKFLOW = ConversationWorkflow(
    id="debate",
    name="Debate Discussion",
    description="A debate-style discussion workflow with pros/cons analysis",
    mode="debate",
    initial_step="position_statement",
    steps=[
        WorkflowStep(
            id="position_statement",
            name="Position Statement",
            description="Statement of positions by participants"
        )
    ]
)