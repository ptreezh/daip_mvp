"""
Session Management ViewModel

This module implements the ViewModel for session management in the P7 GUI application.
It manages session listing, creation, selection, and lifecycle functionality.
"""

from typing import Any, Dict, List, Optional
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class SessionViewModel(ViewModel):
    """
    ViewModel for session management functionality.
    
    This ViewModel manages:
    - Available sessions from the system
    - Session creation and loading
    - Current session selection
    - Session state management
    - Session filtering and search
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the SessionViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('available_sessions', [])  # List of session dictionaries
        self.set_property('current_session_id', None)  # Currently active session ID
        self.set_property('current_session_data', None)  # Full data of current session
        self.set_property('is_loading_sessions', False)  # Whether sessions are being loaded
        self.set_property('session_filter', 'all')  # Filter for session display ('all', 'active', 'completed')
        self.set_property('session_count', 0)  # Total number of sessions
        self.set_property('active_sessions_count', 0)  # Count of active sessions
        self.set_property('search_query', '')  # Current search query
        self.set_property('recent_sessions', [])  # Recently accessed sessions
        self.set_property('session_history_limit', 100)  # Limit for session history
        
        # Register session-specific commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Session management commands
        self.register_command('load_sessions', self._load_sessions_command)
        self.register_command('create_session', self._create_session_command)
        self.register_command('select_session', self._select_session_command)
        self.register_command('delete_session', self._delete_session_command)
        self.register_command('end_current_session', self._end_current_session_command)
        self.register_command('search_sessions', self._search_sessions_command)
        self.register_command('filter_sessions', self._filter_sessions_command)
        self.register_command('refresh_sessions', self._refresh_sessions_command)
        
        # Session state commands
        self.register_command('archive_session', self._archive_session_command)
        self.register_command('restore_session', self._restore_session_command)
        self.register_command('export_session', self._export_session_command)
    
    def _load_sessions_command(self) -> str:
        """
        Command to initiate session loading (will be called asynchronously).
        
        Returns:
            Status message
        """
        # This is a synchronous command that signals async work should begin
        self.set_property('is_loading_sessions', True)
        return "Loading sessions initiated"
    
    async def _create_session_command(self, goal: str) -> str:
        """
        Command to create a new session.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Confirmation message
        """
        new_session = await self.create_session(goal)
        return f"Created session: {new_session.get('id', 'unknown')}"
    
    def _select_session_command(self, session_id: str) -> str:
        """
        Command to select a session.
        
        Args:
            session_id: ID of the session to select
            
        Returns:
            Confirmation message
        """
        return self.select_session(session_id)
    
    def _delete_session_command(self, session_id: str) -> str:
        """
        Command to delete a session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            Confirmation message
        """
        return self.delete_session(session_id)
    
    def _end_current_session_command(self) -> str:
        """
        Command to end the current session.
        
        Returns:
            Confirmation message
        """
        current_session_id = self.get_property('current_session_id')
        if not current_session_id:
            return "No active session to end"
        
        # In a real implementation, this would end the session in the backend
        # For now, just clear the current session
        self.set_property('current_session_id', None)
        self.set_property('current_session_data', None)
        return f"Ended session: {current_session_id}"
    
    def _search_sessions_command(self, query: str) -> str:
        """
        Command to search sessions.
        
        Args:
            query: Search query
            
        Returns:
            Confirmation message
        """
        self.set_property('search_query', query)
        return f"Searched for: {query}"
    
    def _filter_sessions_command(self, filter_type: str) -> str:
        """
        Command to filter sessions.
        
        Args:
            filter_type: Type of filter ('all', 'active', 'completed', etc.)
            
        Returns:
            Confirmation message
        """
        self.set_property('session_filter', filter_type)
        return f"Filter applied: {filter_type}"
    
    def _refresh_sessions_command(self) -> str:
        """
        Command to refresh the session list.
        
        Returns:
            Confirmation message
        """
        # This would trigger a reload of sessions
        self.set_property('is_loading_sessions', True)
        return "Session refresh initiated"
    
    def _archive_session_command(self, session_id: str) -> str:
        """
        Command to archive a session.
        
        Args:
            session_id: ID of the session to archive
            
        Returns:
            Confirmation message
        """
        # In real implementation, this would call backend to archive session
        # For now, we'll just mark it as archived in our local data
        sessions = self.get_property('available_sessions', [])
        for session in sessions:
            if session.get('id') == session_id:
                session['status'] = 'archived'
                session['archived_at'] = self._get_current_timestamp()
                break
        
        self.set_property('available_sessions', sessions)
        return f"Archived session: {session_id}"
    
    def _restore_session_command(self, session_id: str) -> str:
        """
        Command to restore a session.
        
        Args:
            session_id: ID of the session to restore
            
        Returns:
            Confirmation message
        """
        # In real implementation, this would call backend to restore session
        # For now, we'll just mark it as active in our local data
        sessions = self.get_property('available_sessions', [])
        for session in sessions:
            if session.get('id') == session_id:
                session['status'] = 'active'
                session.pop('archived_at', None)  # Remove archive timestamp
                break
        
        self.set_property('available_sessions', sessions)
        return f"Restored session: {session_id}"
    
    def _export_session_command(self, session_id: str) -> str:
        """
        Command to export a session.
        
        Args:
            session_id: ID of the session to export
            
        Returns:
            Confirmation message
        """
        # In real implementation, this would export session data
        # For now, just return a message
        return f"Exported session: {session_id}"
    
    def select_session(self, session_id: str) -> str:
        """
        Select a session by ID.
        
        Args:
            session_id: ID of the session to select
            
        Returns:
            Confirmation message
        """
        # Find the session in available sessions
        available_sessions = self.get_property('available_sessions', [])
        selected_session = None
        
        for session in available_sessions:
            if session.get('id') == session_id:
                selected_session = session
                break
        
        if selected_session is None:
            raise ValueError(f"Session with ID '{session_id}' not found in available sessions")
        
        # Update properties
        self.set_property('current_session_id', session_id)
        self.set_property('current_session_data', selected_session)
        
        # Add to recent sessions list
        self._add_to_recent_sessions(selected_session)
        
        return f"Selected session: {session_id}"
    
    def delete_session(self, session_id: str) -> str:
        """
        Delete a session by ID.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            Confirmation message
        """
        sessions = self.get_property('available_sessions', [])
        session_to_remove = None
        
        for i, session in enumerate(sessions):
            if session.get('id') == session_id:
                session_to_remove = session
                del sessions[i]
                break
        
        if session_to_remove is None:
            raise ValueError(f"Session with ID '{session_id}' not found in available sessions")
        
        # Update available sessions
        self.set_property('available_sessions', sessions)
        self.set_property('session_count', len(sessions))
        
        # If this was the current session, clear current session data
        if self.get_property('current_session_id') == session_id:
            self.set_property('current_session_id', None)
            self.set_property('current_session_data', None)
        
        return f"Deleted session: {session_id}"
    
    def get_sessions_by_status(self, status: str = 'all') -> List[Dict[str, Any]]:
        """
        Get sessions filtered by status.
        
        Args:
            status: Status to filter by ('all', 'active', 'completed', 'pending', 'archived')
            
        Returns:
            List of matching sessions
        """
        available_sessions = self.get_property('available_sessions', [])
        
        if status == 'all':
            return available_sessions
        
        filtered_sessions = []
        for session in available_sessions:
            session_status = session.get('status', 'unknown')
            if status == 'active' and session_status in ['active', 'running']:
                filtered_sessions.append(session)
            elif status == 'completed' and session_status == 'completed':
                filtered_sessions.append(session)
            elif status == 'pending' and session_status == 'pending':
                filtered_sessions.append(session)
            elif status == 'archived' and session_status == 'archived':
                filtered_sessions.append(session)
            elif status == session_status:  # Generic catch-all for other statuses
                filtered_sessions.append(session)
        
        return filtered_sessions
    
    def _add_to_recent_sessions(self, session: Dict[str, Any]) -> None:
        """
        Add a session to the recent sessions list.
        
        Args:
            session: Session to add to recent list
        """
        recent = self.get_property('recent_sessions', [])
        
        # Remove if already exists
        recent = [s for s in recent if s.get('id') != session.get('id')]
        
        # Add to front
        recent.insert(0, session)
        
        # Limit to configured number
        limit = self.get_property('session_history_limit', 10)
        recent = recent[:limit]
        
        self.set_property('recent_sessions', recent)
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp (placeholder for real implementation).
        
        Returns:
            Timestamp string
        """
        return "2025-11-08T00:00:00Z"  # Placeholder
    
    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """Get the list of available sessions."""
        return self.get_property('available_sessions', [])
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the ID of the current session."""
        return self.get_property('current_session_id')
    
    def get_current_session_data(self) -> Optional[Dict[str, Any]]:
        """Get the data of the current session."""
        return self.get_property('current_session_data')
    
    def is_loading_sessions(self) -> bool:
        """Check if sessions are currently being loaded."""
        return self.get_property('is_loading_sessions', False)
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return self.get_property('session_count', 0)
    
    def get_active_sessions_count(self) -> int:
        """Get number of active sessions."""
        return self.get_property('active_sessions_count', 0)
    
    def get_session_filter(self) -> str:
        """Get the current session filter."""
        return self.get_property('session_filter', 'all')
    
    def get_recent_sessions(self) -> List[Dict[str, Any]]:
        """Get recently accessed sessions."""
        return self.get_property('recent_sessions', [])
    
    def get_search_query(self) -> str:
        """Get the current search query."""
        return self.get_property('search_query', '')
    
    def clear_current_session(self) -> None:
        """Clear the current session data."""
        self.set_property('current_session_id', None)
        self.set_property('current_session_data', None)
    
    # Public async methods for coordinating with interaction layer
    async def load_sessions(self) -> List[Dict[str, Any]]:
        """
        Load list of available sessions from backend.
        
        Returns:
            List of session dictionaries
        """
        try:
            self.set_property('is_loading_sessions', True)
            
            # Get sessions from interaction layer
            sessions = await self._interaction_layer.get_sessions()
            
            # Update available sessions
            self.set_property('available_sessions', sessions)
            self.set_property('session_count', len(sessions))
            
            # Count active sessions
            active_count = len(self.get_sessions_by_status('active'))
            self.set_property('active_sessions_count', active_count)
            
            return sessions
        finally:
            self.set_property('is_loading_sessions', False)
    
    async def create_session(self, goal: str) -> Dict[str, Any]:
        """
        Create a new session via the backend.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Created session data
        """
        self.set_property('is_loading_sessions', True)
        try:
            # Create session via interaction layer
            session = await self._interaction_layer.create_session(goal)
            
            # Update local session list
            sessions = self.get_property('available_sessions', [])
            sessions.append(session)
            self.set_property('available_sessions', sessions)
            self.set_property('session_count', len(sessions))
            
            # Set as current session
            self.set_property('current_session_id', session['id'])
            self.set_property('current_session_data', session)
            
            # Add to recent sessions
            self._add_to_recent_sessions(session)
            
            return session
        finally:
            self.set_property('is_loading_sessions', False)
    
    async def refresh_sessions(self) -> List[Dict[str, Any]]:
        """
        Refresh the list of available sessions.
        
        Returns:
            Updated list of session dictionaries
        """
        return await self.load_sessions()
    
    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """
        Search sessions by query (locally).
        
        Args:
            query: Search query string
            
        Returns:
            List of matching session dictionaries
        """
        self.set_property('search_query', query)
        
        if not query:
            return self.get_sessions_by_status(self.get_session_filter())
        
        available_sessions = self.get_property('available_sessions', [])
        query_lower = query.lower()
        
        matching_sessions = []
        for session in available_sessions:
            title = session.get('title', '').lower()
            goal = session.get('goal', '').lower()
            session_id = session.get('id', '').lower()
            
            if query_lower in title or query_lower in goal or query_lower in session_id:
                matching_sessions.append(session)
        
        return matching_sessions