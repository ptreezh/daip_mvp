# -*- coding: utf-8 -*-
"""
ChatSessionService implementation for the Virtual Role Chat System.

This module provides the implementation of ChatSessionService that handles
the creation, configuration, and lifecycle management of chat sessions,
as well as message handling within those sessions.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .interfaces import ChatSessionServiceInterface
from .models import (
    ChatMessage,
    ChatSession,
    ChatRoomID,
    SessionID,
    SessionSummary,
)


class ChatSessionServiceError(Exception):
    """Base exception for ChatSessionService errors."""
    pass


class ChatSessionService(ChatSessionServiceInterface):
    """Implementation of ChatSessionService for managing chat sessions."""
    
    # Session status constants
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_COMPLETED = "completed"
    
    def __init__(self, chat_room_manager: "ChatRoomManager", storage_path: Optional[str] = None):
        """Initialize the ChatSessionService.
        
        Args:
            chat_room_manager: An instance of ChatRoomManager to validate chat rooms.
            storage_path: Path to store session data. If None, uses in-memory storage.
        """
        self.chat_room_manager = chat_room_manager
        self.storage_path = Path(storage_path) if storage_path else None
        self._sessions: Dict[SessionID, ChatSession] = {}
        self._load_sessions()
    
    def _load_sessions(self) -> None:
        """Load chat sessions from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                sessions_data = json.load(f)
                
            for session_data in sessions_data:
                # Convert datetime strings back to datetime objects
                session_data['start_time'] = datetime.fromisoformat(session_data['start_time'])
                if session_data.get('end_time'):
                    session_data['end_time'] = datetime.fromisoformat(session_data['end_time'])
                
                session = ChatSession(**session_data)
                self._sessions[session.id] = session
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load chat sessions from storage: {e}")
    
    def _save_sessions(self) -> None:
        """Save chat sessions to storage."""
        if not self.storage_path:
            return
        
        try:
            # Ensure the directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert sessions to serializable format
            sessions_data = []
            for session in self._sessions.values():
                session_dict = session.model_dump()
                # Convert datetime objects to ISO format strings
                session_dict['start_time'] = session.start_time.isoformat()
                if session.end_time:
                    session_dict['end_time'] = session.end_time.isoformat()
                
                # Also convert datetime objects in messages
                for message in session_dict.get('messages', []):
                    if 'timestamp' in message and hasattr(message['timestamp'], 'isoformat'):
                        message['timestamp'] = message['timestamp'].isoformat()
                
                sessions_data.append(session_dict)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save chat sessions to storage: {e}")

    def _update_session(self, session_id: SessionID, **kwargs) -> bool:
        """Update a chat session with the provided attributes.
        
        Args:
            session_id: The ID of the session to update.
            **kwargs: The attributes to update.
            
        Returns:
            True if the session was updated successfully, False otherwise.
        """
        if session_id not in self._sessions:
            return False
            
        try:
            session = self._sessions[session_id]
            # Create a new session with updated attributes
            updated_session = ChatSession(
                id=session.id,
                room_id=session.room_id,
                start_time=session.start_time,
                end_time=kwargs.get('end_time', session.end_time),
                status=kwargs.get('status', session.status),
                messages=kwargs.get('messages', session.messages),
                metadata=kwargs.get('metadata', session.metadata)
            )
            
            self._sessions[session_id] = updated_session
            self._save_sessions()
            return True
            
        except Exception as e:
            print(f"Error updating chat session {session_id}: {e}")
            return False

    def get_session_by_room_id(self, room_id: ChatRoomID) -> Optional[SessionID]:
        """Get the session ID for a given room ID."""
        for session in self._sessions.values():
            if session.room_id == room_id:
                return session.id
        return None

    async def start_session(self, room_id: ChatRoomID) -> SessionID:
        """Start a new chat session in the given chat room.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            The ID of the created session.
            
        Raises:
            ChatSessionServiceError: If the chat room does not exist.
        """
        # Validate that the chat room exists
        try:
            self.chat_room_manager.get_chat_room(room_id)
        except ValueError as e:
            raise ChatSessionServiceError(f"Chat room with ID '{room_id}' does not exist") from e
        
        # Generate a unique ID for the chat session
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Create the chat session
        now = datetime.now()
        session = ChatSession(
            id=session_id,
            room_id=room_id,
            start_time=now,
            status=self.STATUS_ACTIVE
        )
        
        # Store the session
        self._sessions[session_id] = session
        self._save_sessions()
        
        return session_id

    async def end_session(self, session_id: SessionID) -> bool:
        """End a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was ended successfully, False otherwise.
            
        Raises:
            ChatSessionServiceError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ChatSessionServiceError(f"Session with ID '{session_id}' does not exist")
        
        # Update the session status and end time
        return self._update_session(
            session_id,
            status=self.STATUS_COMPLETED,
            end_time=datetime.now()
        )

    async def pause_session(self, session_id: SessionID) -> bool:
        """Pause a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was paused successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session with ID '{session_id}' does not exist")
        
        # Update the session status
        return self._update_session(session_id, status=self.STATUS_PAUSED)

    async def resume_session(self, session_id: SessionID) -> bool:
        """Resume a paused chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            True if the session was resumed successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist or is not paused.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session with ID '{session_id}' does not exist")
        
        session = self._sessions[session_id]
        if session.status != self.STATUS_PAUSED:
            raise ValueError(f"Session with ID '{session_id}' is not paused")
        
        # Update the session status
        return self._update_session(session_id, status=self.STATUS_ACTIVE)

    async def add_message(self, session_id: SessionID, message: ChatMessage) -> bool:
        """Add a message to a chat session.
        
        Args:
            session_id: The ID of the session.
            message: The message to add.
            
        Returns:
            True if the message was added successfully, False otherwise.
            
        Raises:
            ChatSessionServiceError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ChatSessionServiceError(f"Session with ID '{session_id}' does not exist")
        
        # Add the message to the session
        session = self._sessions[session_id]
        updated_messages = session.messages + [message]
        
        # Update the session with the new message
        return self._update_session(session_id, messages=updated_messages)

    async def get_messages(self, session_id: SessionID, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages from a chat session.
        
        Args:
            session_id: The ID of the session.
            limit: The maximum number of messages to return.
            offset: The offset from which to start returning messages.
            
        Returns:
            A list of messages.
            
        Raises:
            ChatSessionServiceError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ChatSessionServiceError(f"Session with ID '{session_id}' does not exist")
        
        session = self._sessions[session_id]
        # Return messages in chronological order (oldest first)
        # Apply limit and offset
        return session.messages[offset:offset+limit]

    async def get_session_summary(self, session_id: SessionID) -> SessionSummary:
        """Get a summary of a chat session.
        
        Args:
            session_id: The ID of the session.
            
        Returns:
            A summary of the session.
            
        Raises:
            ChatSessionServiceError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ChatSessionServiceError(f"Session with ID '{session_id}' does not exist")
        
        session = self._sessions[session_id]
        
        # Get participant roles from the chat room
        try:
            room = self.chat_room_manager.get_chat_room(session.room_id)
            participant_roles = room.config.roles
        except ValueError:
            # If the room no longer exists, use an empty list
            participant_roles = []
        
        # Create the summary
        summary = SessionSummary(
            id=session.id,
            room_id=session.room_id,
            start_time=session.start_time,
            end_time=session.end_time,
            message_count=len(session.messages),
            participant_roles=participant_roles,
            topic="",  # We might want to get this from the room config
            key_points=[]  # This would be populated by an analytics service
        )
        
        return summary

    async def export_session(self, session_id: SessionID, format: str) -> bytes:
        """Export a chat session in the given format.
        
        Args:
            session_id: The ID of the session.
            format: The format to export the session in.
            
        Returns:
            The exported session as bytes.
            
        Raises:
            ValueError: If the session does not exist.
        """
        # This is a placeholder implementation
        # A full implementation would convert the session data to the specified format
        if session_id not in self._sessions:
            raise ValueError(f"Session with ID '{session_id}' does not exist")
        
        # For now, just return some placeholder data
        return b"Exported session data"

    async def set_transparency_level(self, session_id: SessionID, level: str) -> bool:
        """Set the transparency level for a chat session.
        
        Args:
            session_id: The ID of the session.
            level: The transparency level to set.
            
        Returns:
            True if the transparency level was set successfully, False otherwise.
            
        Raises:
            ValueError: If the session does not exist.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session with ID '{session_id}' does not exist")
        
        # Update the session metadata with the transparency level
        session = self._sessions[session_id]
        updated_metadata = session.metadata.copy()
        updated_metadata["transparency_level"] = level
        
        return self._update_session(session_id, metadata=updated_metadata)