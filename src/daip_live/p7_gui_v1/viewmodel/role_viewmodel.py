"""
Role Management ViewModel

This module implements the ViewModel for role management in the P7 GUI application.
It manages role listing, selection, creation, and editing functionality.
"""

from typing import Any, Dict, List, Optional
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class RoleViewModel(ViewModel):
    """
    ViewModel for role management functionality.
    
    This ViewModel manages:
    - Available roles from the system
    - Role selection and switching
    - Role creation and editing
    - Role search and filtering
    - Role-specific configuration
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the RoleViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('available_roles', [])  # List of role dictionaries
        self.set_property('selected_role', None)  # Currently selected role name
        self.set_property('selected_role_details', None)  # Full details of selected role
        self.set_property('is_loading', False)  # Whether roles are being loaded
        self.set_property('search_query', '')  # Current search query
        self.set_property('filtered_roles', [])  # Roles matching search query
        self.set_property('editing_role', None)  # Role being edited (for UI state)
        self.set_property('create_mode', False)  # Whether in role creation mode
        
        # Register role-specific commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Role management commands
        self.register_command('load_roles', self._load_roles_command)
        self.register_command('select_role', self._select_role_command)
        self.register_command('search_roles', self._search_roles_command)
        self.register_command('clear_role_selection', self._clear_role_selection)
        self.register_command('start_role_creation', self._start_role_creation)
        self.register_command('cancel_role_edit', self._cancel_role_edit)
        
        # Editing commands
        self.register_command('apply_role_changes', self._apply_role_changes)
        self.register_command('reset_to_default', self._reset_to_default)
    
    def _load_roles_command(self) -> str:
        """
        Command to initiate role loading (will be called asynchronously).
        
        Returns:
            Status message
        """
        # This is a synchronous command that signals async work should begin
        self.set_property('is_loading', True)
        return "Loading roles initiated"
    
    def _select_role_command(self, role_name: str) -> str:
        """
        Command to select a role.
        
        Args:
            role_name: Name of the role to select
            
        Returns:
            Confirmation message
        """
        return self.select_role(role_name)
    
    def _search_roles_command(self, query: str) -> str:
        """
        Command to search roles.
        
        Args:
            query: Search query
            
        Returns:
            Confirmation message
        """
        self.set_property('search_query', query)
        self.filter_roles_by_name(query)
        return f"Searched for: {query}"
    
    def _clear_role_selection(self) -> str:
        """
        Command to clear role selection.
        
        Returns:
            Confirmation message
        """
        self.set_property('selected_role', None)
        self.set_property('selected_role_details', None)
        return "Role selection cleared"
    
    def _start_role_creation(self) -> str:
        """
        Command to enter role creation mode.
        
        Returns:
            Confirmation message
        """
        self.set_property('create_mode', True)
        self.set_property('editing_role', {
            'name': '',
            'description': '',
            'system_prompt': '',
            'is_new': True
        })
        return "Started role creation mode"
    
    def _cancel_role_edit(self) -> str:
        """
        Command to cancel role editing/creation.
        
        Returns:
            Confirmation message
        """
        self.set_property('create_mode', False)
        self.set_property('editing_role', None)
        return "Cancelled role editing"
    
    def _apply_role_changes(self) -> str:
        """
        Command to apply role changes.
        
        Returns:
            Confirmation message
        """
        # In a complete implementation, this would call backend to save the role
        # For now, we just exit edit mode
        editing_role = self.get_property('editing_role')
        if editing_role and editing_role.get('is_new'):
            # Add new role to available roles (in real impl, would call backend)
            roles = self.get_property('available_roles', [])
            if editing_role not in roles:
                roles.append(editing_role)
                self.set_property('available_roles', roles)
        
        self.set_property('create_mode', False)
        self.set_property('editing_role', None)
        return "Applied role changes"
    
    def _reset_to_default(self) -> str:
        """
        Command to reset selected role to default.
        
        Returns:
            Confirmation message
        """
        # In a real implementation, this would reset to system defaults
        # For now, clear selection
        return self._clear_role_selection()
    
    def select_role(self, role_name: str) -> str:
        """
        Select a role by name.
        
        Args:
            role_name: Name of the role to select
            
        Returns:
            Confirmation message
        """
        # Find the role in available roles
        available_roles = self.get_property('available_roles', [])
        selected_role = None
        
        for role in available_roles:
            if role.get('name') == role_name:
                selected_role = role
                break
        
        if selected_role is None:
            raise ValueError(f"Role '{role_name}' not found in available roles")
        
        # Update properties
        self.set_property('selected_role', role_name)
        self.set_property('selected_role_details', selected_role)
        
        return f"Selected role: {role_name}"
    
    def filter_roles_by_name(self, search_query: str = "") -> List[Dict[str, Any]]:
        """
        Filter available roles by name based on search query.
        
        Args:
            search_query: Query to filter roles by (defaults to property value)
            
        Returns:
            List of matching roles
        """
        if not search_query:
            search_query = self.get_property('search_query', '')
        
        available_roles = self.get_property('available_roles', [])
        
        if not search_query:
            self.set_property('filtered_roles', available_roles)
            return available_roles
        
        # Case-insensitive search in name and description
        filtered = []
        query_lower = search_query.lower()
        
        for role in available_roles:
            name_match = query_lower in role.get('name', '').lower()
            desc_match = query_lower in role.get('description', '').lower()
            prompt_match = query_lower in role.get('system_prompt', '').lower()
            
            if name_match or desc_match or prompt_match:
                filtered.append(role)
        
        self.set_property('filtered_roles', filtered)
        return filtered
    
    def get_available_roles(self) -> List[Dict[str, Any]]:
        """Get the list of available roles."""
        return self.get_property('available_roles', [])
    
    def get_selected_role(self) -> Optional[str]:
        """Get the name of the currently selected role."""
        return self.get_property('selected_role')
    
    def get_selected_role_details(self) -> Optional[Dict[str, Any]]:
        """Get the details of the selected role."""
        return self.get_property('selected_role_details')
    
    def is_loading_roles(self) -> bool:
        """Check if roles are currently being loaded."""
        return self.get_property('is_loading', False)
    
    def get_search_query(self) -> str:
        """Get the current search query."""
        return self.get_property('search_query', '')
    
    def get_filtered_roles(self) -> List[Dict[str, Any]]:
        """Get the list of roles matching the current search filter."""
        return self.get_property('filtered_roles', [])
    
    def in_create_mode(self) -> bool:
        """Check if the ViewModel is in role creation mode."""
        return self.get_property('create_mode', False)
    
    def get_editing_role(self) -> Optional[Dict[str, Any]]:
        """Get the role currently being edited."""
        return self.get_property('editing_role')
    
    # Public async methods for coordinating with interaction layer
    async def load_roles(self) -> List[Dict[str, Any]]:
        """
        Load list of available roles from backend.
        
        Returns:
            List of role dictionaries
        """
        try:
            self.set_property('is_loading', True)
            
            # Get roles from interaction layer
            roles = await self._interaction_layer.get_roles()
            
            # Update available roles
            self.set_property('available_roles', roles)
            
            # Apply any current filter
            self.filter_roles_by_name()
            
            return roles
        finally:
            self.set_property('is_loading', False)
    
    async def refresh_roles(self) -> List[Dict[str, Any]]:
        """
        Refresh the list of available roles.
        
        Returns:
            Updated list of role dictionaries
        """
        return await self.load_roles()
    
    def update_role_details(self, role_name: str, **changes) -> bool:
        """
        Update details of a specific role.
        
        Args:
            role_name: Name of the role to update
            **changes: Field-value pairs to update
            
        Returns:
            True if role was found and updated, False otherwise
        """
        available_roles = self.get_property('available_roles', [])
        
        for role in available_roles:
            if role.get('name') == role_name:
                # Update the role with new values
                for key, value in changes.items():
                    role[key] = value
                
                # If this role is currently selected, update the selection details too
                if self.get_property('selected_role') == role_name:
                    self.set_property('selected_role_details', role)
                
                # Update the property
                self.set_property('available_roles', available_roles)
                return True
        
        return False