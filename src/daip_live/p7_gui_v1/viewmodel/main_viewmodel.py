"""
Main Window ViewModel

This module implements the ViewModel for the main window of the P7 GUI application.
It manages the application state, navigation, and coordinates with the interaction layer.
"""

from typing import Any, Dict, List, Optional
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class MainViewModel(ViewModel):
    """
    ViewModel for the main application window.
    
    This ViewModel manages:
    - Application state (current view, processing status)
    - Navigation between different views
    - Session management
    - Global application commands
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the MainViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('current_view', 'chat')  # Default to chat view
        self.set_property('is_processing', False)
        self.set_property('current_session', None)
        self.set_property('available_sessions', [])
        self.set_property('available_roles', [])
        self.set_property('user_preferences', {})
        self.set_property('notifications', [])
        self.set_property('input_text', '')
        
        # Register application commands
        self._register_commands()
        
        # Initialize by loading available data
        self._initialize_data()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Navigation commands
        self.register_command('switch_view', self._switch_view)
        self.register_command('show_chat', lambda: self._switch_view('chat'))
        self.register_command('show_roles', lambda: self._switch_view('roles'))
        self.register_command('show_sessions', lambda: self._switch_view('sessions'))
        self.register_command('show_debate', lambda: self._switch_view('debate'))
        self.register_command('show_knowledge', lambda: self._switch_view('knowledge'))
        
        # Session management commands
        self.register_command('create_new_session', self._create_new_session)
        self.register_command('load_session', self._load_session)
        self.register_command('end_session', self._end_session)
        
        # Global commands
        self.register_command('clear_notifications', self._clear_notifications)
        self.register_command('update_preferences', self._update_preferences)
    
    def _initialize_data(self):
        """Initialize ViewModel with default data."""
        # Load initial available sessions and roles
        # This will be done asynchronously when the application starts
        pass
    
    def _switch_view(self, view_name: str) -> str:
        """
        Switch to a different view.
        
        Args:
            view_name: Name of the view to switch to
            
        Returns:
            Confirmation message
        """
        # Validate view name
        valid_views = ['chat', 'roles', 'sessions', 'debate', 'knowledge', 'settings']
        if view_name not in valid_views:
            raise ValueError(f"Invalid view name: {view_name}")
        
        # Update property
        self.set_property('current_view', view_name)
        
        # Log navigation
        self._add_notification(f"Switched to {view_name} view", "info")
        
        return f"Switched to {view_name} view"
    
    def _create_new_session(self, goal: str) -> str:
        """
        Create a new session.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Confirmation message
        """
        # Update processing state
        self.set_property('is_processing', True)
        
        try:
            # This would normally call the interaction layer asynchronously
            # For now we'll just update the state
            new_session = {
                'id': f'session_{len(self.get_property("available_sessions")) + 1}',
                'goal': goal,
                'created_at': '2025-11-08',  # In real implementation, use actual timestamp
                'status': 'active'
            }
            
            # Add to available sessions
            sessions = self.get_property('available_sessions', [])
            sessions.append(new_session)
            self.set_property('available_sessions', sessions)
            
            # Set as current session
            self.set_property('current_session', new_session['id'])
            
            return f"Created new session with goal: {goal}"
        finally:
            # Always reset processing state
            self.set_property('is_processing', False)
    
    def _load_session(self, session_id: str) -> str:
        """
        Load an existing session.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            Confirmation message
        """
        # Update processing state
        self.set_property('is_processing', True)
        
        try:
            sessions = self.get_property('available_sessions', [])
            session = next((s for s in sessions if s['id'] == session_id), None)
            
            if not session:
                raise ValueError(f"Session with ID {session_id} not found")
            
            # Set as current session
            self.set_property('current_session', session_id)
            
            # Switch to chat view to display session
            self._switch_view('chat')
            
            return f"Loaded session: {session_id}"
        finally:
            # Always reset processing state
            self.set_property('is_processing', False)
    
    def _end_session(self) -> str:
        """
        End the current session.
        
        Returns:
            Confirmation message
        """
        current_session = self.get_property('current_session')
        if not current_session:
            return "No active session to end"
        
        # Update processing state
        self.set_property('is_processing', True)
        
        try:
            # In real implementation, this would call the backend
            # For now, just update UI state
            self.set_property('current_session', None)
            
            # Clear any session-specific data
            self.set_property('input_text', '')
            
            return f"Ended session: {current_session}"
        finally:
            # Always reset processing state
            self.set_property('is_processing', False)
    
    def _clear_notifications(self) -> str:
        """Clear all notifications."""
        self.set_property('notifications', [])
        return "Cleared notifications"
    
    def _update_preferences(self, **preferences) -> str:
        """
        Update user preferences.
        
        Args:
            **preferences: Key-value pairs of preferences to update
            
        Returns:
            Confirmation message
        """
        current_prefs = self.get_property('user_preferences', {})
        current_prefs.update(preferences)
        self.set_property('user_preferences', current_prefs)
        
        return f"Updated preferences: {list(preferences.keys())}"
    
    def _add_notification(self, message: str, level: str = "info") -> None:
        """
        Add a notification to the notification list.
        
        Args:
            message: Notification message
            level: Notification level ('info', 'warning', 'error', 'success')
        """
        notifications = self.get_property('notifications', [])
        notification = {
            'id': len(notifications),
            'message': message,
            'level': level,
            'timestamp': '2025-11-08T00:00:00Z'  # In real implementation, use actual timestamp
        }
        notifications.append(notification)
        self.set_property('notifications', notifications)
    
    # Public async methods for coordinating with interaction layer
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of available sessions from the backend.
        
        Returns:
            List of session data
        """
        sessions = await self._interaction_layer.get_sessions()
        self.set_property('available_sessions', sessions)
        return sessions
    
    async def create_session(self, goal: str) -> Dict[str, Any]:
        """
        Create a new session via the backend.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Created session data
        """
        self.set_property('is_processing', True)
        try:
            session = await self._interaction_layer.create_session(goal)
            
            # Update local session list
            sessions = self.get_property('available_sessions', [])
            sessions.append(session)
            self.set_property('available_sessions', sessions)
            self.set_property('current_session', session['id'])
            
            return session
        finally:
            self.set_property('is_processing', False)
    
    async def get_roles(self) -> List[Dict[str, Any]]:
        """
        Get list of available roles from the backend.
        
        Returns:
            List of role data
        """
        roles = await self._interaction_layer.get_roles()
        self.set_property('available_roles', roles)
        return roles
    
    def get_current_view(self) -> str:
        """Get the current view."""
        return self.get_property('current_view', 'chat')
    
    def is_processing(self) -> bool:
        """Check if the application is processing."""
        return self.get_property('is_processing', False)
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the ID of the current session."""
        return self.get_property('current_session')
    
    def set_input_text(self, text: str) -> None:
        """Set the input text."""
        self.set_property('input_text', text)
    
    def get_input_text(self) -> str:
        """Get the input text."""
        return self.get_property('input_text', '')
    
    def clear_input_text(self) -> None:
        """Clear the input text."""
        self.set_property('input_text', '')