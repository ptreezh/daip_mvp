"""
Chat ViewModel

This module implements the ViewModel for chat functionality in the P7 GUI application.
It manages conversation state, message history, and coordinates with the interaction layer.
"""

from typing import Any, Dict, List, Optional, AsyncGenerator
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class ChatViewModel(ViewModel):
    """
    ViewModel for chat functionality.
    
    This ViewModel manages:
    - Conversation message history
    - Message sending and receiving
    - Chat state (typing indicator, current session)
    - Message formatting and display
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the ChatViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('messages', [])  # List of message dictionaries
        self.set_property('current_session_id', None)
        self.set_property('is_typing', False)  # Whether agent is currently typing
        self.set_property('input_text', '')  # Current input text
        self.set_property('message_count', 0)
        self.set_property('session_title', '')
        
        # Register chat-specific commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Message commands
        self.register_command('send_input', self._send_input_text)
        self.register_command('clear_chat', self._clear_chat)
        self.register_command('set_input_text', self._set_input_text)
        
        # Session commands
        self.register_command('switch_session', self._switch_session)
        self.register_command('end_current_session', self._end_current_session)
    
    def _send_input_text(self) -> str:
        """
        Send the current input text as a message.
        
        Returns:
            Confirmation message
        """
        input_text = self.get_property('input_text', '').strip()
        if not input_text:
            return "No message to send"
        
        # Add user message to history
        self._add_user_message(input_text)
        
        # Clear input
        self.set_property('input_text', '')
        
        return f"Sent message: {input_text[:50]}..."
    
    def _clear_chat(self) -> str:
        """
        Clear the current chat history.
        
        Returns:
            Confirmation message
        """
        self.set_property('messages', [])
        self.set_property('message_count', 0)
        return "Chat cleared"
    
    def _set_input_text(self, text: str) -> str:
        """
        Set the input text.
        
        Args:
            text: Text to set in the input field
            
        Returns:
            Confirmation message
        """
        self.set_property('input_text', text)
        return f"Input text set to: {text[:30]}..."
    
    def _switch_session(self, session_id: str) -> str:
        """
        Switch to a different session.
        
        Args:
            session_id: ID of the session to switch to
            
        Returns:
            Confirmation message
        """
        self.set_property('current_session_id', session_id)
        self.set_property('messages', [])  # Clear messages for new session
        self._load_conversation_history_sync()
        return f"Switched to session: {session_id}"
    
    def _end_current_session(self) -> str:
        """
        End the current session.
        
        Returns:
            Confirmation message
        """
        current_session = self.get_property('current_session_id')
        if not current_session:
            return "No active session"
        
        self.set_property('current_session_id', None)
        self.set_property('messages', [])
        self.set_property('session_title', '')
        return f"Ended session: {current_session}"
    
    def _add_user_message(self, content: str) -> None:
        """
        Add a user message to the history.
        
        Args:
            content: Message content
        """
        message = {
            'id': f'user_msg_{self.get_property("message_count")}',
            'content': content,
            'sender': 'user',
            'timestamp': self._get_current_timestamp(),
            'type': 'message'
        }
        
        messages = self.get_property('messages', [])
        messages.append(message)
        self.set_property('messages', messages)
        self.set_property('message_count', self.get_property('message_count') + 1)
    
    def add_message_to_history(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the chat history.
        
        Args:
            message: Message dictionary with id, content, sender, timestamp
        """
        messages = self.get_property('messages', [])
        messages.append(message)
        self.set_property('messages', messages)
        self.set_property('message_count', self.get_property('message_count') + 1)
    
    def _load_conversation_history_sync(self) -> None:
        """
        Synchronously load conversation history (placeholder for async implementation).
        """
        # In a real implementation, this would load from the interaction layer
        # For now, we just set up the structure
        pass
    
    def _get_current_timestamp(self) -> str:
        """
        Get the current timestamp as an ISO string.
        
        Returns:
            Current timestamp in ISO format
        """
        # In a real implementation, we'd use datetime, but for simplicity:
        return "2025-11-08T00:00:00Z"  # Placeholder
    
    # Public async methods for coordinating with interaction layer
    async def send_message(self, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message to the current session and yield responses.
        
        Args:
            message: Message to send
            
        Yields:
            Response events from the backend
        """
        current_session_id = self.get_property('current_session_id')
        if not current_session_id:
            yield {
                "type": "error",
                "content": "No active session",
                "sender": "system"
            }
            return
        
        # Show user message immediately
        self._add_user_message(message)
        
        # Set typing indicator
        self.set_property('is_typing', True)
        
        try:
            # Send message via interaction layer and get responses
            async for response in self._interaction_layer.send_message(current_session_id, message):
                # Add agent responses to history
                if response.get('type') == 'message_response':
                    agent_message = {
                        'id': f'agent_msg_{self.get_property("message_count")}',
                        'content': response.get('content', ''),
                        'sender': 'agent',
                        'timestamp': response.get('timestamp', self._get_current_timestamp()),
                        'type': 'response'
                    }
                    self.add_message_to_history(agent_message)
                
                yield response
        finally:
            # Clear typing indicator
            self.set_property('is_typing', False)
    
    async def load_conversation_history(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load conversation history for the specified session.
        
        Args:
            session_id: Session ID to load history for (uses current if None)
            
        Returns:
            List of messages in the conversation
        """
        target_session_id = session_id or self.get_property('current_session_id')
        if not target_session_id:
            return []
        
        # In a real implementation, this would fetch from the backend
        # For now, we'll return an empty list; in practice you'd use the interaction layer
        # to fetch conversation history from the backend service
        messages = []
        self.set_property('messages', messages)
        self.set_property('message_count', len(messages))
        
        return messages
    
    async def start_new_conversation(self, goal: str) -> Dict[str, Any]:
        """
        Start a new conversation with the specified goal.
        
        Args:
            goal: Goal for the new conversation
            
        Returns:
            New session information
        """
        # Create a new session via the interaction layer
        new_session = await self._interaction_layer.create_session(goal)
        
        # Update ViewModel state
        self.set_property('current_session_id', new_session['id'])
        self.set_property('session_title', new_session.get('title', goal))
        self.set_property('messages', [])
        self.set_property('message_count', 0)
        
        return new_session
    
    # Property access methods for convenience
    def get_messages(self) -> List[Dict[str, Any]]:
        """Get the current list of messages."""
        return self.get_property('messages', [])
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.get_property('current_session_id')
    
    def is_agent_typing(self) -> bool:
        """Check if the agent is currently typing."""
        return self.get_property('is_typing', False)
    
    def set_input_text(self, text: str) -> None:
        """Set the input text."""
        self.set_property('input_text', text)
    
    def get_input_text(self) -> str:
        """Get the input text."""
        return self.get_property('input_text', '')
    
    def clear_input(self) -> None:
        """Clear the input text."""
        self.set_property('input_text', '')
    
    def get_session_title(self) -> str:
        """Get the current session title."""
        return self.get_property('session_title', 'New Chat')
    
    def get_message_count(self) -> int:
        """Get the number of messages in the current session."""
        return self.get_property('message_count', 0)