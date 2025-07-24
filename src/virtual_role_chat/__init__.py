"""
Virtual Role Chat System - A comprehensive system for managing dynamic chat environments with multiple AI roles.

This package implements a flexible chat system that allows users to create and manage virtual chat rooms
with multiple AI roles, facilitating dynamic discussions and collaborative problem-solving sessions.
"""

__version__ = "0.1.0"

# Import core data models
from .models import (
    ChatRoom,
    ChatRoomConfig,
    ChatRoomID,
    ChatRoomSummary,
    ChatMessage,
    ChatSession,
    SessionID,
    SessionSummary,
    ValidationResult,
    ResolutionResult,
    SubTopic,
    TransparencyLevel,
    SessionMetrics,
    RolePerformance,
    QualityMetrics,
    QualityIssue,
)

# Import interfaces
from .interfaces import (
    ChatRoomManagerInterface,
    ChatSessionServiceInterface,
    RoleInteractionEngineInterface,
    ChatAnalyticsServiceInterface,
)

# Import workflow components
from .workflow import (
    WorkflowState,
    WorkflowEventType,
    WorkflowEvent,
    WorkflowAction,
    WorkflowStep,
    ConversationWorkflow,
    WorkflowExecution,
    TaskDecomposition,
    ProcessingChain,
    WorkflowEngineInterface,
    WorkflowStateManagerInterface,
    TaskDecompositionServiceInterface,
    WorkflowAdapterInterface,
    FREE_FORM_WORKFLOW,
    STRUCTURED_WORKFLOW,
    DEBATE_WORKFLOW,
)

# PocketFlow integration will be implemented in a separate task
# Placeholder for future implementation
try:
    from .pocketflow_adapter import (
        workflow_engine,
        WorkflowEngineImpl,
        PocketFlowAdapter,
    )
    POCKETFLOW_AVAILABLE = True
except ImportError:
    import logging
    logging.warning("PocketFlow not available. Workflow functionality will be limited.")
    workflow_engine = None
    WorkflowEngineImpl = None
    PocketFlowAdapter = None
    POCKETFLOW_AVAILABLE = False

__all__ = [
    # Core models
    "ChatRoom",
    "ChatRoomConfig", 
    "ChatRoomID",
    "ChatRoomSummary",
    "ChatMessage",
    "ChatSession",
    "SessionID",
    "SessionSummary",
    "ValidationResult",
    "ResolutionResult",
    "SubTopic",
    "TransparencyLevel",
    "SessionMetrics",
    "RolePerformance",
    "QualityMetrics",
    "QualityIssue",
    
    # Interfaces
    "ChatRoomManagerInterface",
    "ChatSessionServiceInterface", 
    "RoleInteractionEngineInterface",
    "ChatAnalyticsServiceInterface",
    
    # Workflow components
    "WorkflowState",
    "WorkflowEventType",
    "WorkflowEvent",
    "WorkflowAction",
    "WorkflowStep",
    "ConversationWorkflow",
    "WorkflowExecution",
    "TaskDecomposition",
    "ProcessingChain",
    "WorkflowEngineInterface",
    "WorkflowStateManagerInterface",
    "TaskDecompositionServiceInterface",
    "WorkflowAdapterInterface",
    "FREE_FORM_WORKFLOW",
    "STRUCTURED_WORKFLOW",
    "DEBATE_WORKFLOW",
    
    # PocketFlow integration
    "workflow_engine",
    "WorkflowEngineImpl",
    "PocketFlowAdapter",
    "POCKETFLOW_AVAILABLE",
]
