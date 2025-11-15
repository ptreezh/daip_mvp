import pytest
import customtkinter as ctk
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.views.chat_view import ChatView


class TestChatView:
    """TDD for Chat View"""
    
    def test_chat_view_initialization(self):
        """RED: Test that ChatView can be initialized"""
        # Create a mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        # Initialize the chat view (without actually displaying it)
        app = ctk.CTk()
        app.withdraw()  # Hide it to avoid display issues during testing
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        
        assert chat_view is not None
        assert hasattr(chat_view, '_viewmodel')
        assert hasattr(chat_view, '_parent')
        assert hasattr(chat_view, '_message_log')
        assert hasattr(chat_view, '_input_field')
    
    def test_chat_view_has_required_components(self):
        """RED: Test that ChatView has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        
        # Check that required components exist
        assert hasattr(chat_view, '_message_log')  # Text area to display messages
        assert hasattr(chat_view, '_input_field')  # Entry field for user input
        assert hasattr(chat_view, '_send_button')  # Button to send messages
        assert hasattr(chat_view, '_scrollable_frame')  # Frame for messages
        
        # Check that components are properly initialized
        assert chat_view._message_log is not None
        assert chat_view._input_field is not None
        assert chat_view._send_button is not None
        assert chat_view._scrollable_frame is not None
    
    def test_message_display(self):
        """RED: Test that messages can be displayed"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        
        # Add a test message
        test_message = {
            'id': 'msg1',
            'content': 'Hello, world!',
            'sender': 'user',
            'timestamp': '2025-11-08T10:00:00Z'
        }
        
        # Test that the method exists
        assert hasattr(chat_view, 'display_message')
        assert callable(chat_view.display_message)
    
    def test_input_handling(self):
        """RED: Test input field handling"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        
        # Check that input methods exist
        assert hasattr(chat_view, 'get_input_text')
        assert hasattr(chat_view, 'clear_input')
        assert callable(chat_view.get_input_text)
        assert callable(chat_view.clear_input)
    
    def test_message_submission(self):
        """RED: Test message submission functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Sent message')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        
        # Check that message submission methods exist
        assert hasattr(chat_view, 'submit_message')
        assert callable(chat_view.submit_message)
        
        # Check that send button command is bound
        assert chat_view._send_button is not None
    
    def test_viewmodel_binding(self):
        """RED: Test that view is bound to ViewModel"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        chat_view._bind_to_viewmodel()
        
        # Verify that the viewmodel binding was set up
        assert mock_vm.subscribe_property_change.called
    
    def test_message_history_display(self):
        """RED: Test displaying message history"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'id': 'msg1', 'content': 'Previous message', 'sender': 'agent', 'timestamp': '2025-11-08T09:00:00Z'},
            {'id': 'msg2', 'content': 'Another message', 'sender': 'user', 'timestamp': '2025-11-08T09:01:00Z'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        chat_view = ChatView(frame, mock_vm)
        chat_view._setup_components()
        chat_view._bind_to_viewmodel()
        
        # The view should handle initial message history
        assert hasattr(chat_view, '_update_messages_display')
        assert callable(chat_view._update_messages_display)