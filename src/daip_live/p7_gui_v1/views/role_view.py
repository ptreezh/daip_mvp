"""
Role Management View

This module implements the role management view for the P7 GUI application using CustomTkinter.
It displays available roles and allows for role selection and management, binding to the RoleViewModel.
"""

import customtkinter as ctk
from typing import Dict, Any, List, Optional
from .base import View
from ..viewmodel.role_viewmodel import RoleViewModel


class RoleView(View):
    """
    Role management view implementation for the P7 GUI application.
    
    This view handles:
    - Display of available roles in a list
    - Selection of roles
    - Display of role details
    - Role search and filtering
    - Role creation and editing
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: RoleViewModel):
        """
        Initialize the RoleView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: RoleViewModel instance to bind to
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._roles_listbox: Optional[ctk.CTkOptionMenu] = None  # Using OptionMenu for role selection
        self._role_details_frame: Optional[ctk.CTkFrame] = None
        self._role_name_label: Optional[ctk.CTkLabel] = None
        self._role_description_label: Optional[ctk.CTkLabel] = None
        self._role_system_prompt_text: Optional[ctk.CTkTextbox] = None
        self._select_button: Optional[ctk.CTkButton] = None
        self._search_entry: Optional[ctk.CTkEntry] = None
        self._refresh_button: Optional[ctk.CTkButton] = None
        self._create_button: Optional[ctk.CTkButton] = None
        self._edit_button: Optional[ctk.CTkButton] = None
        self._delete_button: Optional[ctk.CTkButton] = None
        
        # Internal data
        self._available_roles: List[Dict[str, Any]] = []
        
        # Initialize UI
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all role view components."""
        # Configure the parent frame
        self._parent.grid_rowconfigure(0, weight=1)
        self._parent.grid_columnconfigure(1, weight=1)
        
        # Create top controls frame (search and refresh)
        controls_frame = ctk.CTkFrame(self._parent)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_columnconfigure(1, weight=0)
        controls_frame.grid_columnconfigure(2, weight=0)
        
        # Create search entry
        self._search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Search roles...",
            height=35
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # Create refresh button
        self._refresh_button = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self._refresh_roles,
            width=80,
            height=35
        )
        self._refresh_button.grid(row=0, column=1, padx=(0, 5))
        
        # Create create button
        self._create_button = ctk.CTkButton(
            controls_frame,
            text="New Role",
            command=self._create_new_role,
            width=90,
            height=35
        )
        self._create_button.grid(row=0, column=2)
        
        # Create center frame for role list and details
        center_frame = ctk.CTkFrame(self._parent)
        center_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        center_frame.grid_columnconfigure(0, weight=0)  # Role list column
        center_frame.grid_columnconfigure(1, weight=1)  # Details column
        
        # Create role list section (left side)
        role_list_frame = ctk.CTkFrame(center_frame)
        role_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        role_list_frame.grid_rowconfigure(1, weight=1)
        role_list_frame.grid_columnconfigure(0, weight=1)
        
        # Role list header
        role_list_header = ctk.CTkLabel(
            role_list_frame,
            text="Available Roles",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        role_list_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Create role list textbox (for displaying and selecting roles)
        self._roles_listbox = ctk.CTkTextbox(
            role_list_frame,
            height=300,
            width=200
        )
        self._roles_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self._roles_listbox.bind("<ButtonRelease-1>", self._on_role_selected)
        
        # Create role details section (right side)
        self._role_details_frame = ctk.CTkFrame(center_frame)
        self._role_details_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self._role_details_frame.grid_rowconfigure(4, weight=1)  # System prompt text area
        self._role_details_frame.grid_columnconfigure(1, weight=1)
        
        # Role details header
        role_details_header = ctk.CTkLabel(
            self._role_details_frame,
            text="Role Details",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        role_details_header.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 10), sticky="w")
        
        # Role name
        role_name_label = ctk.CTkLabel(
            self._role_details_frame,
            text="Name:",
            font=ctk.CTkFont(weight="bold")
        )
        role_name_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._role_name_label = ctk.CTkLabel(
            self._role_details_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self._role_name_label.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Role description
        role_description_label = ctk.CTkLabel(
            self._role_details_frame,
            text="Description:",
            font=ctk.CTkFont(weight="bold")
        )
        role_description_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._role_description_label = ctk.CTkLabel(
            self._role_details_frame,
            text="-",
            font=ctk.CTkFont(size=12),
            wraplength=400
        )
        self._role_description_label.grid(row=2, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Role system prompt
        system_prompt_label = ctk.CTkLabel(
            self._role_details_frame,
            text="System Prompt:",
            font=ctk.CTkFont(weight="bold")
        )
        system_prompt_label.grid(row=3, column=0, padx=(10, 5), pady=(10, 5), sticky="nw")
        
        self._role_system_prompt_text = ctk.CTkTextbox(
            self._role_details_frame,
            height=100
        )
        self._role_system_prompt_text.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=(5, 10))
        self._role_system_prompt_text.configure(state="disabled")  # Initially disabled until role selected
        
        # Action buttons frame
        action_buttons_frame = ctk.CTkFrame(self._parent)
        action_buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        action_buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Select button
        self._select_button = ctk.CTkButton(
            action_buttons_frame,
            text="Select Role",
            command=self._select_role,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green"),
            height=35
        )
        self._select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Edit button
        self._edit_button = ctk.CTkButton(
            action_buttons_frame,
            text="Edit Role",
            command=self._edit_role,
            fg_color=("orange", "brown"),
            hover_color=("brown", "orange"),
            height=35
        )
        self._edit_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._edit_button.configure(state="disabled")  # Disabled until role selected
        
        # Delete button
        self._delete_button = ctk.CTkButton(
            action_buttons_frame,
            text="Delete Role",
            command=self._delete_role,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            height=35
        )
        self._delete_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        self._delete_button.configure(state="disabled")  # Disabled until role selected
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('available_roles', self._on_available_roles_changed)
        self._viewmodel.subscribe_property_change('selected_role', self._on_selected_role_changed)
        self._viewmodel.subscribe_property_change('selected_role_details', self._on_selected_role_details_changed)
        self._viewmodel.subscribe_property_change('is_loading', self._on_loading_changed)
        
        # Update initial state from ViewModel
        roles = self._viewmodel.get_property('available_roles', [])
        self._update_roles_display(roles)
        
        selected_role = self._viewmodel.get_property('selected_role')
        if selected_role:
            self._update_role_selection(selected_role)
    
    def _on_available_roles_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel available roles change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_roles_display(new_value)
    
    def _on_selected_role_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel selected role change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_role_selection(new_value)
    
    def _on_selected_role_details_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel selected role details change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._display_role_details(new_value)
    
    def _on_loading_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel loading state change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        # Update UI to reflect loading state
        if new_value:
            # Disable controls during loading
            self._disable_controls()
        else:
            # Re-enable controls after loading
            self._enable_controls()
    
    def _update_roles_display(self, roles: List[Dict[str, Any]]):
        """
        Update the roles display with new roles data.
        
        Args:
            roles: List of role dictionaries to display
        """
        self._available_roles = roles
        
        # Clear and update the roles list display
        if self._roles_listbox:
            self._roles_listbox.delete("1.0", "end")
            
            if not roles:
                self._roles_listbox.insert("1.0", "No roles available")
                self._roles_listbox.configure(state="disabled")
            else:
                self._roles_listbox.configure(state="normal")
                role_names = [role.get('name', 'Unknown Role') for role in roles]
                
                for i, role_name in enumerate(role_names):
                    self._roles_listbox.insert(f"{i+1}.0", f"{role_name}\n")
                
                self._roles_listbox.configure(state="disabled")
    
    def _update_role_selection(self, role_name: Optional[str]):
        """
        Update the UI to reflect the selected role.
        
        Args:
            role_name: Name of the selected role, or None if no selection
        """
        if role_name:
            # Enable action buttons when a role is selected
            self._select_button.configure(state="normal")
            self._edit_button.configure(state="normal")
            self._delete_button.configure(state="normal")
            
            # Highlight the selected role in the listbox
            if self._roles_listbox:
                self._roles_listbox.configure(state="normal")
                self._roles_listbox.delete("1.0", "end")
                
                for i, role in enumerate(self._available_roles):
                    role_name_text = role.get('name', 'Unknown Role')
                    if role_name_text == role_name:
                        # Highlight selected role
                        self._roles_listbox.insert(f"{i+1}.0", f"> {role_name_text}\n")
                    else:
                        self._roles_listbox.insert(f"{i+1}.0", f"  {role_name_text}\n")
                
                self._roles_listbox.configure(state="disabled")
        else:
            # Disable action buttons when no role is selected
            self._select_button.configure(state="disabled")
            self._edit_button.configure(state="disabled")
            self._delete_button.configure(state="disabled")
    
    def _display_role_details(self, role_details: Optional[Dict[str, Any]]):
        """
        Display the details of a selected role.
        
        Args:
            role_details: Role details dictionary to display, or None to clear
        """
        if not role_details:
            # Clear the display fields
            if self._role_name_label:
                self._role_name_label.configure(text="-")
            if self._role_description_label:
                self._role_description_label.configure(text="-")
            if self._role_system_prompt_text:
                self._role_system_prompt_text.configure(state="normal")
                self._role_system_prompt_text.delete("1.0", "end")
                self._role_system_prompt_text.configure(state="disabled")
            return
        
        # Update the display fields with role details
        name = role_details.get('name', 'N/A')
        description = role_details.get('description', 'No description available')
        system_prompt = role_details.get('system_prompt', 'No system prompt available')
        
        if self._role_name_label:
            self._role_name_label.configure(text=name)
        if self._role_description_label:
            self._role_description_label.configure(text=description)
        if self._role_system_prompt_text:
            self._role_system_prompt_text.configure(state="normal")
            self._role_system_prompt_text.delete("1.0", "end")
            self._role_system_prompt_text.insert("1.0", system_prompt)
            self._role_system_prompt_text.configure(state="disabled")
    
    def _on_search_changed(self, event=None):
        """Handle changes to the search field."""
        if self._search_entry:
            search_query = self._search_entry.get()
            # Update ViewModel with search query
            self._viewmodel.set_property('search_query', search_query)
            # In a real implementation, this would filter the roles display
            # For now, we'll just trigger a refresh
            self._refresh_roles()
    
    def _on_role_selected(self, event=None):
        """Handle clicking on a role in the list."""
        # In a real implementation, this would parse the clicked position
        # and select the corresponding role
        
        # For now, we'll just refresh the display
        selected_role = self._viewmodel.get_property('selected_role')
        if selected_role:
            self._viewmodel.select_role(selected_role)
    
    def _select_role(self):
        """Handle the Select Role button click."""
        selected_role = self._viewmodel.get_property('selected_role')
        if selected_role:
            result = self._viewmodel.select_role(selected_role)
            # In a real implementation, you might display a confirmation
            # or trigger a navigation to update the main application
    
    def _edit_role(self):
        """Handle the Edit Role button click."""
        # In a real implementation, this would open a role editor form
        pass
    
    def _delete_role(self):
        """Handle the Delete Role button click."""
        # In a real implementation, this would handle role deletion
        pass
    
    def _create_new_role(self):
        """Handle the Create New Role button click."""
        # In a real implementation, this would open a role creation form
        pass
    
    def _refresh_roles(self):
        """Handle the Refresh button click."""
        # Trigger ViewModel to reload roles
        self._viewmodel.execute_command('load_roles')
    
    def _disable_controls(self):
        """Disable UI controls during loading."""
        if self._search_entry:
            self._search_entry.configure(state="disabled")
        if self._refresh_button:
            self._refresh_button.configure(state="disabled", text="Loading...")
        if self._create_button:
            self._create_button.configure(state="disabled")
        if self._select_button:
            self._select_button.configure(state="disabled")
        if self._edit_button:
            self._edit_button.configure(state="disabled")
        if self._delete_button:
            self._delete_button.configure(state="disabled")
    
    def _enable_controls(self):
        """Enable UI controls after loading."""
        if self._search_entry:
            self._search_entry.configure(state="normal")
        if self._refresh_button:
            self._refresh_button.configure(state="normal", text="Refresh")
        if self._create_button:
            self._create_button.configure(state="normal")
        # Keep action buttons enabled/disabled based on selection status
    
    def show(self):
        """Show the role view."""
        if not self._visible:
            self._visible = True
            self._parent.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Hide the role view."""
        if self._visible:
            self._visible = False
            self._parent.grid_remove()
    
    def refresh(self):
        """Refresh the role view display."""
        self._refresh_roles()
    
    def get_selected_role(self) -> Optional[str]:
        """
        Get the currently selected role name.
        
        Returns:
            Name of the selected role, or None if no role is selected
        """
        return self._viewmodel.get_property('selected_role')
    
    def get_all_roles(self) -> List[Dict[str, Any]]:
        """
        Get the list of all available roles.
        
        Returns:
            List of role dictionaries
        """
        return self._viewmodel.get_property('available_roles', [])
    
    def search_roles(self, query: str) -> List[Dict[str, Any]]:
        """
        Search roles by query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching role dictionaries
        """
        self._viewmodel.set_property('search_query', query)
        return self._viewmodel.filter_roles_by_name(query)
    
    def populate_roles_list(self, roles: List[Dict[str, Any]]):
        """
        Populate the roles list with data.
        
        Args:
            roles: List of role dictionaries to populate the list with
        """
        self._update_roles_display(roles)
    
    def clear_role_selection(self):
        """Clear the current role selection."""
        self._viewmodel.execute_command('clear_role_selection')