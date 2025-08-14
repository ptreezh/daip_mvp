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
    global_conditions: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class WorkflowExecution(BaseModel):
    """Represents an active workflow execution."""

    id: str
    workflow_id: str
    session_id: SessionID
    state: WorkflowState
    current_step: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = {}
    events: List[WorkflowEvent] = []
    error_message: Optional[str] = None


class TaskDecomposition(BaseModel):
    """Represents a task decomposition strategy."""

    id: str
    name: str
    description: str = ""
    complexity_threshold: float = 0.7  # Above this, decompose
    max_subtasks: int = 5
    strategy_type: str  # "expertise_based", "sequential", "parallel"
    parameters: Dict[str, Any] = {}


class ProcessingChain(BaseModel):
    """Represents a chain of processing tasks."""

    id: str
    name: str
    description: str = ""
    tasks: List[str]  # Task IDs in execution order
    execution_mode: str  # "sequential", "parallel", "adaptive"
    current_task: Optional[str] = None
    completed_tasks: List[str] = []
    failed_tasks: List[str] = []
    metadata: Dict[str, Any] = {}


@runtime_checkable
class WorkflowEngineInterface(Protocol):
    """Interface for the PocketFlow workflow engine."""

    def create_workflow(self, workflow: ConversationWorkflow) -> str:
        """Create a new workflow definition.
        
        Args:
            workflow: The workflow definition.
            
        Returns:
            The ID of the created workflow.

        """
        ...

    def start_workflow(self, workflow_id: str, session_id: SessionID, context: Optional[Dict[str, Any]] = None) -> str:
        """Start a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow to start.
            session_id: The ID of the session.
            context: Initial context for the workflow.
            
        Returns:
            The ID of the workflow execution.

        """
        ...

    def pause_workflow(self, execution_id: str) -> bool:
        """Pause a workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            True if paused successfully, False otherwise.

        """
        ...

    def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            True if resumed successfully, False otherwise.

        """
        ...

    def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            True if cancelled successfully, False otherwise.

        """
        ...

    def send_event(self, execution_id: str, event: WorkflowEvent) -> bool:
        """Send an event to a workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            event: The event to send.
            
        Returns:
            True if event was processed successfully, False otherwise.

        """
        ...

    def get_execution_status(self, execution_id: str) -> WorkflowExecution:
        """Get the status of a workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            The workflow execution status.

        """
        ...

    def get_execution_context(self, execution_id: str) -> Dict[str, Any]:
        """Get the context of a workflow execution.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            The workflow execution context.

        """
        ...


@runtime_checkable
class WorkflowStateManagerInterface(Protocol):
    """Interface for managing workflow state."""

    def save_state(self, execution_id: str, state: Dict[str, Any]) -> bool:
        """Save workflow state.
        
        Args:
            execution_id: The ID of the workflow execution.
            state: The state to save.
            
        Returns:
            True if saved successfully, False otherwise.

        """
        ...

    def load_state(self, execution_id: str) -> Dict[str, Any]:
        """Load workflow state.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            The loaded state.

        """
        ...

    def delete_state(self, execution_id: str) -> bool:
        """Delete workflow state.
        
        Args:
            execution_id: The ID of the workflow execution.
            
        Returns:
            True if deleted successfully, False otherwise.

        """
        ...


@runtime_checkable
class TaskDecompositionServiceInterface(Protocol):
    """Interface for task decomposition services."""

    def analyze_complexity(self, task: str, context: Dict[str, Any]) -> float:
        """Analyze the complexity of a task.
        
        Args:
            task: The task to analyze.
            context: Context for the analysis.
            
        Returns:
            A complexity score between 0 and 1.

        """
        ...

    def decompose_task(self, task: str, strategy: TaskDecomposition, context: Dict[str, Any]) -> List[str]:
        """Decompose a task into subtasks.
        
        Args:
            task: The task to decompose.
            strategy: The decomposition strategy to use.
            context: Context for the decomposition.
            
        Returns:
            A list of subtasks.

        """
        ...

    def create_processing_chain(self, tasks: List[str], execution_mode: str) -> ProcessingChain:
        """Create a processing chain from tasks.
        
        Args:
            tasks: The tasks to include in the chain.
            execution_mode: The execution mode for the chain.
            
        Returns:
            A processing chain.

        """
        ...


@runtime_checkable
class WorkflowAdapterInterface(Protocol):
    """Interface for adapting DAIP-LIVE components to PocketFlow workflows."""

    def adapt_role_manager(self, role_manager: Any) -> Dict[str, Any]:
        """Adapt RoleManager for workflow use.
        
        Args:
            role_manager: The RoleManager instance.
            
        Returns:
            Adapted interface for workflow actions.

        """
        ...

    def adapt_memory_service(self, memory_service: Any) -> Dict[str, Any]:
        """Adapt MemoryService for workflow use.
        
        Args:
            memory_service: The MemoryService instance.
            
        Returns:
            Adapted interface for workflow actions.

        """
        ...

    def adapt_synthesis_engine(self, synthesis_engine: Any) -> Dict[str, Any]:
        """Adapt SynthesisEngine for workflow use.
        
        Args:
            synthesis_engine: The SynthesisEngine instance.
            
        Returns:
            Adapted interface for workflow actions.

        """
        ...

    def adapt_fact_services(self, fact_extraction: Any, fact_validation: Any) -> Dict[str, Any]:
        """Adapt fact extraction and validation services for workflow use.
        
        Args:
            fact_extraction: The FactExtractionService instance.
            fact_validation: The FactValidationService instance.
            
        Returns:
            Adapted interface for workflow actions.

        """
        ...


# Predefined workflow templates
FREE_FORM_WORKFLOW = ConversationWorkflow(
    id="free_form_chat",
    name="Free Form Chat",
    description="A flexible workflow for free-form conversations between roles",
    mode="free_form",
    initial_step="initialize_roles",
    steps=[
        WorkflowStep(
            id="initialize_roles",
            name="Initialize Roles",
            description="Initialize all roles in the chat room",
            actions=[
                WorkflowAction(
                    id="load_roles",
                    name="Load Role Definitions",
                    type="role_initialization",
                    parameters={"load_context": True, "validate_roles": True}
                )
            ],
            next_steps=["conversation_loop"]
        ),
        WorkflowStep(
            id="conversation_loop",
            name="Conversation Loop",
            description="Main conversation loop with intelligent turn-taking",
            actions=[
                WorkflowAction(
                    id="select_next_role",
                    name="Select Next Role",
                    type="role_selection",
                    parameters={"strategy": "expertise_based"}
                ),
                WorkflowAction(
                    id="generate_response",
                    name="Generate Role Response",
                    type="role_response",
                    dependencies=["select_next_role"]
                ),
                WorkflowAction(
                    id="validate_response",
                    name="Validate Response",
                    type="validation",
                    dependencies=["generate_response"]
                )
            ],
            conditions={"continue_conversation": True},
            next_steps=["conversation_loop", "end_session"]
        ),
        WorkflowStep(
            id="end_session",
            name="End Session",
            description="End the conversation session",
            actions=[
                WorkflowAction(
                    id="generate_summary",
                    name="Generate Session Summary",
                    type="synthesis",
                    parameters={"include_key_points": True}
                )
            ]
        )
    ]
)

STRUCTURED_WORKFLOW = ConversationWorkflow(
    id="structured_chat",
    name="Structured Chat",
    description="A structured workflow with defined phases and turn-taking rules",
    mode="structured",
    initial_step="setup_structure",
    steps=[
        WorkflowStep(
            id="setup_structure",
            name="Setup Structure",
            description="Set up the structured conversation format",
            actions=[
                WorkflowAction(
                    id="define_phases",
                    name="Define Conversation Phases",
                    type="structure_definition",
                    parameters={"phases": ["introduction", "exploration", "synthesis"]}
                )
            ],
            next_steps=["introduction_phase"]
        ),
        WorkflowStep(
            id="introduction_phase",
            name="Introduction Phase",
            description="Roles introduce their perspectives",
            actions=[
                WorkflowAction(
                    id="role_introductions",
                    name="Role Introductions",
                    type="structured_response",
                    parameters={"phase": "introduction", "time_limit": 120}
                )
            ],
            next_steps=["exploration_phase"]
        ),
        WorkflowStep(
            id="exploration_phase",
            name="Exploration Phase",
            description="Deep exploration of the topic",
            actions=[
                WorkflowAction(
                    id="topic_exploration",
                    name="Topic Exploration",
                    type="structured_response",
                    parameters={"phase": "exploration", "allow_interruptions": True}
                )
            ],
            next_steps=["synthesis_phase"]
        ),
        WorkflowStep(
            id="synthesis_phase",
            name="Synthesis Phase",
            description="Synthesize insights and reach conclusions",
            actions=[
                WorkflowAction(
                    id="synthesize_insights",
                    name="Synthesize Insights",
                    type="synthesis",
                    parameters={"phase": "synthesis", "require_consensus": False}
                )
            ],
            next_steps=["end_session"]
        ),
        WorkflowStep(
            id="end_session",
            name="End Session",
            description="End the structured conversation",
            actions=[
                WorkflowAction(
                    id="final_summary",
                    name="Generate Final Summary",
                    type="synthesis",
                    parameters={"include_phase_summaries": True}
                )
            ]
        )
    ]
)

DEBATE_WORKFLOW = ConversationWorkflow(
    id="debate_chat",
    name="Debate Chat",
    description="A formal debate workflow with structured arguments and rebuttals",
    mode="debate",
    initial_step="setup_debate",
    steps=[
        WorkflowStep(
            id="setup_debate",
            name="Setup Debate",
            description="Initialize debate format and assign positions",
            actions=[
                WorkflowAction(
                    id="assign_positions",
                    name="Assign Debate Positions",
                    type="debate_setup",
                    parameters={"format": "oxford", "assign_moderator": True}
                )
            ],
            next_steps=["opening_statements"]
        ),
        WorkflowStep(
            id="opening_statements",
            name="Opening Statements",
            description="Each side presents opening statements",
            actions=[
                WorkflowAction(
                    id="opening_arguments",
                    name="Present Opening Arguments",
                    type="debate_response",
                    parameters={"phase": "opening", "time_limit": 180}
                )
            ],
            next_steps=["rebuttals"]
        ),
        WorkflowStep(
            id="rebuttals",
            name="Rebuttals",
            description="Structured rebuttals and counter-arguments",
            actions=[
                WorkflowAction(
                    id="present_rebuttals",
                    name="Present Rebuttals",
                    type="debate_response",
                    parameters={"phase": "rebuttal", "allow_cross_examination": True}
                )
            ],
            next_steps=["closing_statements"]
        ),
        WorkflowStep(
            id="closing_statements",
            name="Closing Statements",
            description="Final closing statements from each side",
            actions=[
                WorkflowAction(
                    id="closing_arguments",
                    name="Present Closing Arguments",
                    type="debate_response",
                    parameters={"phase": "closing", "time_limit": 120}
                )
            ],
            next_steps=["consensus_building"]
        ),
        WorkflowStep(
            id="consensus_building",
            name="Consensus Building",
            description="Attempt to build consensus or determine outcome",
            actions=[
                WorkflowAction(
                    id="build_consensus",
                    name="Build Consensus",
                    type="consensus",
                    parameters={"strategy": "synthesis", "require_majority": False}
                )
            ],
            next_steps=["end_debate"]
        ),
        WorkflowStep(
            id="end_debate",
            name="End Debate",
            description="Conclude the debate session",
            actions=[
                WorkflowAction(
                    id="debate_summary",
                    name="Generate Debate Summary",
                    type="synthesis",
                    parameters={"include_positions": True, "include_outcome": True}
                )
            ]
        )
    ]
)
