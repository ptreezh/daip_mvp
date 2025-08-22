# -*- coding: utf-8 -*-
"""Tests for the enhanced ChatCoordinator implementation."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

# Import the classes we need for testing
from src.virtual_role_chat.chat_coordinator import ChatCoordinator
from src.virtual_role_chat.chat_room_manager import ChatRoomManager
from src.virtual_role_chat.chat_session_service import ChatSessionService
from src.virtual_role_chat.models import ChatRoomConfig
from src.core_services.role_manager import Role
from src.institutional_primitives.base import InstitutionalPrimitive
from src.core_services.wiki_service import WikiService


class TestChatCoordinator:
    """Test cases for enhanced ChatCoordinator."""

    @pytest.fixture
    def mock_chat_room_manager(self):
        """Create a mock ChatRoomManager instance for testing."""
        return Mock(spec=ChatRoomManager)

    @pytest.fixture
    def mock_chat_session_service(self):
        """Create a mock ChatSessionService instance for testing."""
        return Mock(spec=ChatSessionService)

    @pytest.fixture
    def mock_role_manager(self):
        """Create a mock RoleManager instance for testing."""
        return Mock()

    @pytest.fixture
    def mock_primitive_registry(self):
        """Create a mock PrimitiveRegistry instance for testing."""
        return Mock()

    @pytest.fixture
    def mock_wiki_service(self):
        """Create a mock WikiService instance for testing."""
        return Mock(spec=WikiService)

    @pytest.fixture
    def chat_coordinator(self, mock_chat_room_manager, mock_chat_session_service, 
                          mock_role_manager, mock_primitive_registry, mock_wiki_service):
        """Create a ChatCoordinator instance with all services for testing."""
        return ChatCoordinator(
            chat_room_manager=mock_chat_room_manager,
            chat_session_service=mock_chat_session_service,
            role_manager=mock_role_manager,
            primitive_registry=mock_primitive_registry,
            wiki_service=mock_wiki_service
        )

    def test_initialization_with_all_services(self, chat_coordinator, mock_chat_room_manager, 
                                               mock_chat_session_service, mock_role_manager, 
                                               mock_primitive_registry, mock_wiki_service):
        """Test that ChatCoordinator is initialized correctly with all services."""
        assert chat_coordinator.chat_room_manager == mock_chat_room_manager
        assert chat_coordinator.chat_session_service == mock_chat_session_service
        assert chat_coordinator.role_manager == mock_role_manager
        assert chat_coordinator.primitive_registry == mock_primitive_registry
        assert chat_coordinator.wiki_service == mock_wiki_service

    def test_initialization_with_minimal_services(self, mock_chat_room_manager, mock_chat_session_service):
        """Test that ChatCoordinator works with minimal services."""
        coordinator = ChatCoordinator(
            chat_room_manager=mock_chat_room_manager,
            chat_session_service=mock_chat_session_service
        )
        assert coordinator.chat_room_manager == mock_chat_room_manager
        assert coordinator.chat_session_service == mock_chat_session_service
        assert coordinator.role_manager is None
        assert coordinator.primitive_registry is None
        assert coordinator.wiki_service is None

    def test_recommend_roles_for_topic(self, chat_coordinator, mock_role_manager):
        """Test role recommendation based on topic."""
        # Setup mock roles
        mock_role1 = Role("1", "AI Expert", "Expert in artificial intelligence", "prompt", ["ai"])
        mock_role2 = Role("2", "Data Scientist", "Expert in data analysis", "prompt", ["data"])
        mock_role3 = Role("3", "Philosopher", "Expert in philosophy", "prompt", ["philosophy"])
        
        # Make sure list_roles returns a list, not the mock itself
        mock_role_manager.list_roles.return_value = [mock_role1, mock_role2, mock_role3]
        
        # Test recommendation
        recommendations = chat_coordinator.recommend_roles_for_topic("AI and data science")
        
        # Should recommend AI Expert and Data Scientist
        assert len(recommendations) == 2
        role_names = [r["name"] for r in recommendations]
        assert "AI Expert" in role_names
        assert "Data Scientist" in role_names
        
        # Check scoring
        ai_role = next(r for r in recommendations if r["name"] == "AI Expert")
        data_role = next(r for r in recommendations if r["name"] == "Data Scientist")
        assert ai_role["score"] >= 2  # Matches "AI" in name
        assert data_role["score"] >= 1  # Matches "data" in description

    def test_recommend_roles_without_role_manager(self, chat_coordinator):
        """Test role recommendation when role manager is not available."""
        # Create coordinator without role manager
        coordinator = ChatCoordinator(
            chat_room_manager=Mock(spec=ChatRoomManager),
            chat_session_service=Mock(spec=ChatSessionService)
        )
        
        recommendations = coordinator.recommend_roles_for_topic("AI topic")
        assert recommendations == []

    def test_get_available_chat_primitives(self, chat_coordinator, mock_primitive_registry):
        """Test getting available chat primitives."""
        # Setup mock primitive
        class MockPrimitive(InstitutionalPrimitive):
            __doc__ = "Mock primitive for testing"
            
            @classmethod
            def get_info(cls):
                return "Mock primitive for testing"
        
        # Setup the mock registry to return a proper dictionary
        mock_primitive_registry._primitives = {"test_primitive": MockPrimitive}
        
        # Get primitives
        primitives = chat_coordinator.get_available_chat_primitives()
        
        assert len(primitives) == 1
        assert primitives[0]["type"] == "test_primitive"
        # The description comes from __doc__ attribute
        assert "Mock primitive for testing" in primitives[0]["description"]

    def test_get_available_primitives_without_registry(self, chat_coordinator):
        """Test getting primitives when registry is not available."""
        # Create coordinator without primitive registry
        coordinator = ChatCoordinator(
            chat_room_manager=Mock(spec=ChatRoomManager),
            chat_session_service=Mock(spec=ChatSessionService)
        )
        
        primitives = coordinator.get_available_chat_primitives()
        assert primitives == []

    def test_upload_document_to_chat_success(self, chat_coordinator, mock_wiki_service, tmp_path):
        """Test successful document upload to chat."""
        # Create a temporary document
        doc_file = tmp_path / "test_document.txt"
        doc_content = "This is a test document for chat upload."
        doc_file.write_text(doc_content)
        
        # Setup mock wiki service
        mock_wiki_service.create_entry.return_value = MagicMock()
        
        # Upload document
        result = chat_coordinator.upload_document_to_chat("room123", str(doc_file), "Test document")
        
        # Verify success
        assert result is True
        # Verify wiki service was called
        mock_wiki_service.create_entry.assert_called_once()
        call_args = mock_wiki_service.create_entry.call_args[1]
        assert "ChatDocument_room123_test_document" in call_args["entry_name"]
        assert call_args["content"] == doc_content
        assert "chat_document" in call_args["tags"]

    def test_upload_document_nonexistent_file(self, chat_coordinator):
        """Test document upload with non-existent file."""
        result = chat_coordinator.upload_document_to_chat("room123", "/nonexistent/file.txt")
        assert result is False

    def test_upload_document_without_wiki_service(self, chat_coordinator, tmp_path):
        """Test document upload when wiki service is not available."""
        # Create coordinator without wiki service
        coordinator = ChatCoordinator(
            chat_room_manager=Mock(spec=ChatRoomManager),
            chat_session_service=Mock(spec=ChatSessionService)
        )
        
        # Create a temporary document
        doc_file = tmp_path / "test_document.txt"
        doc_file.write_text("Test content")
        
        # Upload should still succeed (just doesn't create wiki page)
        result = coordinator.upload_document_to_chat("room123", str(doc_file))
        assert result is True

    def test_get_chat_consensus_info(self, chat_coordinator):
        """Test getting chat consensus information."""
        # Setup mock history
        chat_coordinator.get_room_history = Mock(return_value=[
            {"content": "I agree with the proposal", "sender": "User1"},
            {"content": "I disagree with some parts", "sender": "User2"},
            {"content": "Let's find a compromise", "sender": "User3"}
        ])
        
        # Get consensus info
        consensus = chat_coordinator.get_chat_consensus_info("room123")
        
        # Verify structure
        assert "consensus_level" in consensus
        assert "agreement_points" in consensus
        assert "disagreement_points" in consensus
        assert "total_messages" in consensus
        assert consensus["total_messages"] == 3

    def test_get_chat_consensus_no_history(self, chat_coordinator):
        """Test getting consensus info when no history is available."""
        chat_coordinator.get_room_history = Mock(return_value=[])
        
        consensus = chat_coordinator.get_chat_consensus_info("room123")
        
        assert consensus["consensus_level"] == "no_data"
        assert consensus["agreement_points"] == []
        assert consensus["disagreement_points"] == []

    def test_create_chat_room_with_role_recommendation(self, chat_coordinator, mock_chat_room_manager, mock_role_manager):
        """Test creating chat room with automatic role recommendation."""
        # Setup
        mock_room_id = "room_12345678"
        mock_chat_room_manager.create_chat_room.return_value = mock_room_id
        
        # Setup mock role recommendation
        mock_role1 = Role("role1", "AI Expert", "AI specialist", "prompt", ["ai"])
        mock_role2 = Role("role2", "Data Scientist", "Data expert", "prompt", ["data"])
        # Make sure list_roles returns a list
        mock_role_manager.list_roles.return_value = [mock_role1, mock_role2]
        
        # Create room with auto recommendation
        room_id = chat_coordinator.create_chat_room(
            topic="AI discussion",
            auto_recommend_roles=True
        )
        
        # Verify room was created
        assert room_id == mock_room_id
        mock_chat_room_manager.create_chat_room.assert_called_once()
        
        # Verify role recommendation was used
        call_args = mock_chat_room_manager.create_chat_room.call_args[0][0]
        assert len(call_args.roles) > 0

    def test_send_message_to_room(self, chat_coordinator, mock_chat_session_service):
        """Test sending message to chat room."""
        # Setup - ChatSessionService uses add_message, not send_message
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        mock_chat_session_service.add_message = AsyncMock(side_effect=ChatSessionServiceError("Session does not exist"))
        chat_coordinator._current_room_id = "current_room"
        
        # Send message to current room
        result = chat_coordinator.send_message_to_room(message="Hello world")
        
        # Verify failure - expected to fail since session doesn't exist
        assert result is False

    def test_send_message_to_specific_room(self, chat_coordinator, mock_chat_session_service):
        """Test sending message to specific room."""
        # Setup - ChatSessionService uses add_message, not send_message
        from src.virtual_role_chat.chat_session_service import ChatSessionServiceError
        mock_chat_session_service.add_message = AsyncMock(side_effect=ChatSessionServiceError("Session does not exist"))
        
        # Send message to specific room
        result = chat_coordinator.send_message_to_room(
            room_id="specific_room",
            message="Hello specific room",
            sender="custom_user"
        )
        
        # Verify failure - expected to fail since session doesn't exist
        assert result is False

    def test_send_message_no_current_room(self, chat_coordinator):
        """Test sending message when no current room is set."""
        chat_coordinator._current_room_id = None
        
        result = chat_coordinator.send_message_to_room(message="Hello world")
        assert result is False

    def test_get_room_history_uses_current_room(self, chat_coordinator, mock_chat_session_service):
        """Test that getting history uses current room when no room specified."""
        # Setup - need to mock getting messages from session
        from src.virtual_role_chat.models import ChatMessage
        from datetime import datetime
        
        # Create a proper ChatMessage object
        mock_message = ChatMessage(
            id="msg1",
            session_id="session_current_room",
            sender_id="user",
            sender_type="user",
            content="Test message",
            timestamp=datetime.now()
        )
        
        mock_session = Mock()
        mock_session.messages = [mock_message]
        mock_chat_session_service.get_messages = AsyncMock(return_value=[mock_message])
        chat_coordinator._current_room_id = "current_room"
        
        # Get history without specifying room
        history = chat_coordinator.get_room_history()
        
        # Should return the messages from the session
        assert len(history) == 1
        assert history[0]["content"] == "Test message"

    def test_clear_room_history_uses_current_room(self, chat_coordinator, mock_chat_session_service):
        """Test that clearing history uses current room when no room specified."""
        # Clear history isn't directly available in ChatSessionService
        # For now, we'll test that it handles the case gracefully
        chat_coordinator._current_room_id = "current_room"
        
        # Clear history without specifying room
        result = chat_coordinator.clear_room_history()
        
        # Should handle gracefully (return False since method doesn't exist)
        assert result is False

    def test_current_room_management(self, chat_coordinator, mock_chat_room_manager):
        """Test current room management functionality."""
        # Setup
        mock_chat_room_manager.get_chat_room.return_value = True  # Room exists
        
        # Test setting current room
        result = chat_coordinator.set_current_room("test_room")
        assert result is True
        assert chat_coordinator.get_current_room_id() == "test_room"
        
        # Test closing current room - ChatSessionService uses end_session, not close_session
        mock_chat_session_service = chat_coordinator.chat_session_service
        mock_chat_session_service.end_session = AsyncMock(return_value=True)
        
        result = chat_coordinator.close_current_room()
        # Should return True since we mocked end_session to return True
        assert result is True
        # And current room should be cleared
        assert chat_coordinator.get_current_room_id() is None

    def test_delete_room_clears_current_room(self, chat_coordinator, mock_chat_room_manager):
        """Test that deleting current room clears the current room reference."""
        # Setup
        chat_coordinator._current_room_id = "room_to_delete"
        mock_chat_room_manager.delete_chat_room.return_value = True
        
        # Delete the current room
        result = chat_coordinator.delete_room("room_to_delete")
        
        # Verify success and that current room was cleared
        assert result is True
        assert chat_coordinator.get_current_room_id() is None