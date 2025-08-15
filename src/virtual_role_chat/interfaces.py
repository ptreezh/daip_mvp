"""Interfaces for the Virtual Role Chat System.

This module defines the interfaces for the main components of the Virtual Role Chat System,
including ChatRoomManager, ChatSessionService, RoleInteractionEngine, and ChatAnalyticsService.
"""

<<<<<<< HEAD
from typing import Any, Dict, List, Literal, Optional, Protocol, runtime_checkable
=======
from typing import Any, Literal, Optional, Protocol, runtime_checkable
>>>>>>> feature/core-services-refactor

from .models import (
    ChatMessage,
    ChatRoom,
    ChatRoomConfig,
    ChatRoomID,
    ChatRoomSummary,
    QualityIssue,
    QualityMetrics,
    ResolutionResult,
    RolePerformance,
    SessionID,
    SessionMetrics,
    SessionSummary,
    SubTopic,
    TransparencyLevel,
    ValidationResult,
)


@runtime_checkable
class ChatRoomManagerInterface(Protocol):
    """Interface for managing chat rooms."""

    def create_chat_room(self, config: ChatRoomConfig) -> ChatRoomID:
        """Create a new chat room with the given configuration.
        
        Args:
            config: The configuration for the chat room.
            
        Returns:
            The ID of the created chat room.

        """
        ...

    def get_chat_room(self, room_id: ChatRoomID) -> ChatRoom:
        """Get a chat room by its ID.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            The chat room.
            
        Raises:
            ValueError: If the chat room does not exist.

        """
        ...

    def update_chat_room(self, room_id: ChatRoomID, config: ChatRoomConfig) -> bool:
        """Update a chat room with the given configuration.
        
        Args:
            room_id: The ID of the chat room.
            config: The new configuration for the chat room.
            
        Returns:
            True if the chat room was updated successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.

        """
        ...

    def delete_chat_room(self, room_id: ChatRoomID) -> bool:
        """Delete a chat room.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            True if the chat room was deleted successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.

        """
        ...
<<<<<<< HEAD

    def list_chat_rooms(self) -> List[ChatRoomSummary]:
=======
    
    def list_chat_rooms(self) -> list[ChatRoomSummary]:
>>>>>>> feature/core-services-refactor
        """List all chat rooms.
        
        Returns:
            A list of chat room summaries.

        """
        ...


@runtime_checkable
class ChatSessionServiceInterface(Protocol):
    """Interface for managing chat sessions."""

    def start_session(self, room_id: ChatRoomID) -> SessionID:
        """Start a new chat session in the given chat room.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            The ID of the created session.
            
        Raises:
            ValueError: If the chat room does not exist.

        """
        ...

    def end_session(self, session_id: SessionID) -> bool:
        """End a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was ended successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def pause_session(self, session_id: SessionID) -> bool:
        """Pause a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was paused successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def resume_session(self, session_id: SessionID) -> bool:
        """Resume a paused chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was resumed successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist or is not paused.

        """
        ...

    def add_message(self, session_id: SessionID, message: ChatMessage) -> bool:
        """Add a message to a chat session.
        
        Args:
            session_id: The ID of the session.
            message: The message to add.
            
        Returns:
            True if the message was added successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def get_messages(self, session_id: SessionID, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
=======
    
    def get_messages(self, session_id: SessionID, limit: int = 50, offset: int = 0) -> list[ChatMessage]:
>>>>>>> feature/core-services-refactor
        """Get messages from a chat session.
        
        Args:
            session_id: The ID of the session.
            limit: The maximum number of messages to return.
            offset: The offset from which to start returning messages.
            
        Returns:
            A list of messages.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def get_session_summary(self, session_id: SessionID) -> SessionSummary:
        """Get a summary of a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            A summary of the session.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def export_session(self, session_id: SessionID, format: Literal["json", "markdown", "pdf"]) -> bytes:
        """Export a chat session in the given format.
        
        Args:
            session_id: The ID of the session.
            format: The format to export the session in.
            
        Returns:
            The exported session as bytes.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def set_transparency_level(self, session_id: SessionID, level: TransparencyLevel) -> bool:
        """Set the transparency level for a chat session.
        
        Args:
            session_id: The ID of the session.
            level: The transparency level to set.
            
        Returns:
            True if the transparency level was set successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...


@runtime_checkable
class RoleInteractionEngineInterface(Protocol):
    """Interface for orchestrating interactions between roles."""

    def process_user_input(self, session_id: SessionID, user_input: str) -> None:
        """Process user input and trigger role responses.
        
        Args:
            session_id: The ID of the session.
            user_input: The user input to process.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def generate_role_response(self, session_id: SessionID, role_id: str) -> ChatMessage:
        """Generate a response from a role.
        
        Args:
            session_id: The ID of the session.
            role_id: The ID of the role.
            
        Returns:
            The generated message.
            
        Raises:
            ValueError: If the session does not exist or the role is not in the session.

        """
        ...
<<<<<<< HEAD

    def get_next_role(self, session_id: SessionID, context: Optional[Dict[str, Any]] = None) -> str:
=======
    
    def get_next_role(self, session_id: SessionID, context: Optional[dict[str, Any]] = None) -> str:
>>>>>>> feature/core-services-refactor
        """Get the next role that should respond.
        
        Args:
            session_id: The ID of the session.
            context: Additional context for role selection.
            
        Returns:
            The ID of the next role.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def validate_statement(self, session_id: SessionID, statement: str) -> ValidationResult:
        """Validate a statement using cross-role validation.
        
        Args:
            session_id: The ID of the session.
            statement: The statement to validate.
            
        Returns:
            The validation result.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def resolve_conflict(self, session_id: SessionID, conflicting_statements: List[str]) -> ResolutionResult:
=======
    
    def resolve_conflict(self, session_id: SessionID, conflicting_statements: list[str]) -> ResolutionResult:
>>>>>>> feature/core-services-refactor
        """Resolve conflicting statements.
        
        Args:
            session_id: The ID of the session.
            conflicting_statements: The conflicting statements to resolve.
            
        Returns:
            The resolution result.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def suggest_topic_refocus(self, session_id: SessionID) -> str:
        """Suggest a topic refocus to keep the conversation on track.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            A suggested topic refocus.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def decompose_complex_topic(self, session_id: SessionID, topic: str) -> List[SubTopic]:
=======
    
    def decompose_complex_topic(self, session_id: SessionID, topic: str) -> list[SubTopic]:
>>>>>>> feature/core-services-refactor
        """Decompose a complex topic into simpler sub-topics.
        
        Args:
            session_id: The ID of the session.
            topic: The topic to decompose.
            
        Returns:
            A list of sub-topics.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def assign_subtopics_to_roles(self, session_id: SessionID, subtopics: List[SubTopic]) -> Dict[str, List[str]]:
=======
    
    def assign_subtopics_to_roles(self, session_id: SessionID, subtopics: list[SubTopic]) -> dict[str, list[str]]:
>>>>>>> feature/core-services-refactor
        """Assign sub-topics to roles based on expertise.
        
        Args:
            session_id: The ID of the session.
            subtopics: The sub-topics to assign.
            
        Returns:
            A mapping from role IDs to lists of sub-topic IDs.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def get_processing_transparency(self, session_id: SessionID) -> TransparencyLevel:
        """Get the current transparency level for a session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            The current transparency level.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...


@runtime_checkable
class ChatAnalyticsServiceInterface(Protocol):
    """Interface for analyzing chat sessions."""

    def get_session_metrics(self, session_id: SessionID) -> SessionMetrics:
        """Get metrics for a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            Metrics for the session.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

    def get_role_performance(self, session_id: SessionID, role_id: str) -> RolePerformance:
        """Get performance metrics for a role in a chat session.
        
        Args:
            session_id: The ID of the session.
            role_id: The ID of the role.
            
        Returns:
            Performance metrics for the role.
            
        Raises:
            ValueError: If the session does not exist or the role is not in the session.

        """
        ...

    def get_conversation_quality(self, session_id: SessionID) -> QualityMetrics:
        """Get quality metrics for a conversation.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            Quality metrics for the conversation.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def detect_quality_issues(self, session_id: SessionID) -> List[QualityIssue]:
=======
    
    def detect_quality_issues(self, session_id: SessionID) -> list[QualityIssue]:
>>>>>>> feature/core-services-refactor
        """Detect quality issues in a conversation.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            A list of detected quality issues.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...
<<<<<<< HEAD

    def generate_analytics_report(self, session_id: SessionID) -> Dict[str, Any]:
=======
    
    def generate_analytics_report(self, session_id: SessionID) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Generate a comprehensive analytics report for a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            An analytics report.
            
        Raises:
            ValueError: If the session does not exist.

        """
        ...

