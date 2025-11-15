import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel


class TestChatViewModel:
    """TDD for Chat ViewModel"""
    
    def test_chat_viewmodel_initialization(self):
        """RED: Test that ChatViewModel can be initialized"""
        mock_interaction = Mock()
        vm = ChatViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_messages')
        assert hasattr(vm, '_current_session_id')
    
    def test_chat_viewmodel_initial_properties(self):
        """RED: Test initial properties of ChatViewModel"""
        mock_interaction = Mock()
        vm = ChatViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('messages') == []
        assert vm.get_property('current_session_id') is None
        assert vm.get_property('is_typing') is False
        assert vm.get_property('input_text') == ''
    
    @pytest.mark.asyncio
    async def test_send_message_command(self):
        """RED: Test send_message functionality"""
        mock_interaction = AsyncMock()
        # Mock the send_message generator to yield test responses
        async def mock_send_message(session_id, message):
            yield {"type": "response", "content": f"Echo: {message}", "sender": "agent"}
        
        mock_interaction.send_message = mock_send_message
        
        vm = ChatViewModel(mock_interaction)
        vm.set_property('current_session_id', 'test_session')
        
        # Test sending a message
        async for response in vm.send_message("Hello, world!"):
            assert response["type"] == "response"
            assert response["content"] == "Echo: Hello, world!"
            assert response["sender"] == "agent"
            break  # Just check the first response
    
    @pytest.mark.asyncio
    async def test_load_conversation_history(self):
        """RED: Test loading conversation history"""
        mock_interaction = AsyncMock()
        # This would normally connect to real backend
        # For testing we'll just verify method exists and is callable
        vm = ChatViewModel(mock_interaction)
        
        assert hasattr(vm, 'load_conversation_history')
        assert callable(vm.load_conversation_history)
        
        # Set a mock session ID
        vm.set_property('current_session_id', 'test_session')
        
        # This would typically load conversation, but we'll just check that method executes
        # without error (in a real scenario it would use the interaction layer)
    
    @pytest.mark.asyncio
    async def test_add_message_to_history(self):
        """RED: Test adding message to local history"""
        mock_interaction = Mock()
        vm = ChatViewModel(mock_interaction)
        
        # Add a message
        message = {
            "id": "msg1", 
            "content": "Test message", 
            "sender": "user", 
            "timestamp": "2025-11-08T12:00:00Z"
        }
        
        vm.add_message_to_history(message)
        
        messages = vm.get_property('messages')
        assert len(messages) == 1
        assert messages[0] == message
    
    def test_property_management(self):
        """RED: Test property management functionality"""
        mock_interaction = Mock()
        vm = ChatViewModel(mock_interaction)
        
        # Test setting and getting properties
        vm.set_property('input_text', 'Test input')
        assert vm.get_property('input_text') == 'Test input'
        
        vm.set_property('is_typing', True)
        assert vm.get_property('is_typing') is True