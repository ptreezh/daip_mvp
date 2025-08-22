# -*- coding: utf-8 -*-
"""Tests for the ChatSessionService implementation."""

import asyncio
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

# Import the models we need for testing
from src.virtual_role_chat.models import ChatMessage, ChatSession, ChatRoomConfig, ChatRoom


class TestChatSessionService:
    """Test cases for ChatSessionService."""

    @pytest.fixture
    def mock_chat_room_manager(self):
        """Create a mock ChatRoomManager instance for testing."""
        mock_manager = Mock()
        # Mock the get_chat_room method to return a valid ChatRoom
        mock_room = ChatRoom(
            id="test_room_id",
            config=ChatRoomConfig(
                name="Test Room",
                topic="Test Topic",
                roles=["role1", "role2"]
            ),
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
            status="active"
        )
        mock_manager.get_chat_room.return_value = mock_room
        # Mock the list_chat_rooms method
        mock_manager.list_chat_rooms.return_value = []
        return mock_manager

    @pytest.fixture
    def chat_session_service(self, mock_chat_room_manager):
        """Create a ChatSessionService instance for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "chat_sessions.json"
            from src.virtual_role_chat.chat_session_service import ChatSessionService
            service = ChatSessionService(
                chat_room_manager=mock_chat_room_manager,
                storage_path=str(storage_path)
            )
            yield service

    @pytest.mark.asyncio
    async def test_start_session_success(self, chat_session_service, mock_chat_room_manager):
        """Test that a session can be started successfully."""
        # Start a new session
        session_id = await chat_session_service.start_session("test_room_id")
        
        # Verify that a session ID is returned
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # Verify that the session is stored
        session = chat_session_service._sessions.get(session_id)
        assert session is not None
        assert session.room_id == "test_room_id"
        assert session.status == "active"

    @pytest.mark.asyncio
    async def test_start_session_invalid_room(self, chat_session_service):
        """Test that starting a session with an invalid room ID raises an error."""
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        
        # Configure the mock to raise an error when get_chat_room is called with an invalid ID
        chat_session_service.chat_room_manager.get_chat_room.side_effect = ValueError("Chat room not found")
        
        with pytest.raises(ChatSessionServiceError, match="Chat room with ID 'invalid_room' does not exist"):
            await chat_session_service.start_session("invalid_room")

    @pytest.mark.asyncio
    async def test_end_session_success(self, chat_session_service):
        """Test that a session can be ended successfully."""
        # Start a new session
        session_id = await chat_session_service.start_session("test_room_id")
        
        # End the session
        result = await chat_session_service.end_session(session_id)
        
        # Verify that the operation was successful
        assert result is True
        
        # Verify that the session status is updated
        session = chat_session_service._sessions.get(session_id)
        assert session is not None
        assert session.status == "completed"

    @pytest.mark.asyncio
    async def test_end_session_invalid_session(self, chat_session_service):
        """Test that ending an invalid session raises an error."""
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        
        with pytest.raises(ChatSessionServiceError, match="Session with ID 'invalid_session' does not exist"):
            await chat_session_service.end_session("invalid_session")

    @pytest.mark.asyncio
    async def test_add_message_success(self, chat_session_service):
        """Test that a message can be added to a session successfully."""
        # Start a new session
        session_id = await chat_session_service.start_session("test_room_id")
        
        # Create a test message
        message = ChatMessage(
            id="test_message_id",
            session_id=session_id,
            sender_id="user1",
            sender_type="user",
            content="Hello, world!",
            timestamp="2023-01-01T00:00:00"
        )
        
        # Add the message
        result = await chat_session_service.add_message(session_id, message)
        
        # Verify that the operation was successful
        assert result is True
        
        # Verify that the message was added to the session
        session = chat_session_service._sessions.get(session_id)
        assert session is not None
        assert len(session.messages) == 1
        assert session.messages[0].id == "test_message_id"

    @pytest.mark.asyncio
    async def test_add_message_invalid_session(self, chat_session_service):
        """Test that adding a message to an invalid session raises an error."""
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        
        # Create a mock message
        message = Mock(spec=ChatMessage)
        
        with pytest.raises(ChatSessionServiceError, match="Session with ID 'invalid_session' does not exist"):
            await chat_session_service.add_message("invalid_session", message)

    @pytest.mark.asyncio
    async def test_get_messages_success(self, chat_session_service):
        """Test that messages can be retrieved from a session successfully."""
        # Start a new session
        session_id = await chat_session_service.start_session("test_room_id")
        
        # Get messages (should be empty initially)
        messages = await chat_session_service.get_messages(session_id)
        
        # Verify that an empty list is returned
        assert messages == []

    @pytest.mark.asyncio
    async def test_get_messages_invalid_session(self, chat_session_service):
        """Test that retrieving messages from an invalid session raises an error."""
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        
        with pytest.raises(ChatSessionServiceError, match="Session with ID 'invalid_session' does not exist"):
            await chat_session_service.get_messages("invalid_session")

    @pytest.mark.asyncio
    async def test_get_session_summary_success(self, chat_session_service):
        """Test that a session summary can be retrieved successfully."""
        # Start a new session
        session_id = await chat_session_service.start_session("test_room_id")
        
        # Get the session summary
        summary = await chat_session_service.get_session_summary(session_id)
        
        # Verify the summary fields
        assert summary.id == session_id
        assert summary.room_id == "test_room_id"
        assert summary.message_count == 0

    @pytest.mark.asyncio
    async def test_get_session_summary_invalid_session(self, chat_session_service):
        """Test that retrieving a summary for an invalid session raises an error."""
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        
        with pytest.raises(ChatSessionServiceError, match="Session with ID 'invalid_session' does not exist"):
            await chat_session_service.get_session_summary("invalid_session")


if __name__ == "__main__":
    pytest.main(["-v", __file__])