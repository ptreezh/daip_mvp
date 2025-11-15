"""
Session Management View

This module implements the session management view for the P7 GUI application using CustomTkinter.
It displays available sessions and allows for session selection, creation, and management, binding to the SessionViewModel.
"""

import customtkinter as ctk
from typing import Dict, Any, List, Optional
from .base import View
from ..viewmodel.session_viewmodel import SessionViewModel


class SessionView(View):
    """
    Session management view implementation for the P7 GUI application.
    
    This view handles:
    - Display of available sessions in a list
    - Selection of sessions
    - Display of session details
    - Session search and filtering
    - Session creation and deletion
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: SessionViewModel):
        """
        Initialize the SessionView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: SessionViewModel instance to bind to
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._session_listbox: Optional[ctk.CTkTextbox] = None
        self._session_details_frame: Optional[ctk.CTkFrame] = None
        self._session_id_label: Optional[ctk.CTkLabel] = None
        self._session_title_label: Optional[ctk.CTkLabel] = None
        self._session_status_label: Optional[ctk.CTkLabel] = None
        self._session_created_label: Optional[ctk.CTkLabel] = None
        self._session_goal_text: Optional[ctk.CTkTextbox] = None
        self._load_button: Optional[ctk.CTkButton] = None
        self._delete_button: Optional[ctk.CTkButton] = None
        self._new_session_button: Optional[ctk.CTkButton] = None
        self._search_entry: Optional[ctk.CTkEntry] = None
        self._refresh_button: Optional[ctk.CTkButton] = None
        
        # Internal data
        self._available_sessions: List[Dict[str, Any]] = []
        self._selected_session_id: Optional[str] = None
        
        # Initialize UI
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all session view components."""
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
            placeholder_text="Search sessions...",
            height=35
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._on_search_changed)
        
        # Create refresh button
        self._refresh_button = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self._refresh_sessions,
            width=80,
            height=35
        )
        self._refresh_button.grid(row=0, column=1, padx=(0, 5))
        
        # Create new session button
        self._new_session_button = ctk.CTkButton(
            controls_frame,
            text="New Session",
            command=self._create_new_session,
            width=100,
            height=35
        )
        self._new_session_button.grid(row=0, column=2)
        
        # Create center frame for session list and details
        center_frame = ctk.CTkFrame(self._parent)
        center_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))
        center_frame.grid_columnconfigure(0, weight=0)  # Session list column
        center_frame.grid_columnconfigure(1, weight=1)  # Details column
        
        # Create session list section (left side)
        session_list_frame = ctk.CTkFrame(center_frame)
        session_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        session_list_frame.grid_rowconfigure(1, weight=1)
        session_list_frame.grid_columnconfigure(0, weight=1)
        
        # Session list header
        session_list_header = ctk.CTkLabel(
            session_list_frame,
            text="Available Sessions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        session_list_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Create session list textbox (for displaying and selecting sessions)
        self._session_listbox = ctk.CTkTextbox(
            session_list_frame,
            height=300,
            width=200
        )
        self._session_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self._session_listbox.bind("<ButtonRelease-1>", self._on_session_selected)
        
        # Create session details section (right side)
        self._session_details_frame = ctk.CTkFrame(center_frame)
        self._session_details_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self._session_details_frame.grid_rowconfigure(5, weight=1)  # Goal text area
        self._session_details_frame.grid_columnconfigure(1, weight=1)
        
        # Session details header
        session_details_header = ctk.CTkLabel(
            self._session_details_frame,
            text="Session Details",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        session_details_header.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 10), sticky="w")
        
        # Session ID
        session_id_label = ctk.CTkLabel(
            self._session_details_frame,
            text="ID:",
            font=ctk.CTkFont(weight="bold")
        )
        session_id_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._session_id_label = ctk.CTkLabel(
            self._session_details_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self._session_id_label.grid(row=1, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Session title
        session_title_label = ctk.CTkLabel(
            self._session_details_frame,
            text="Title:",
            font=ctk.CTkFont(weight="bold")
        )
        session_title_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._session_title_label = ctk.CTkLabel(
            self._session_details_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self._session_title_label.grid(row=2, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Session status
        session_status_label = ctk.CTkLabel(
            self._session_details_frame,
            text="Status:",
            font=ctk.CTkFont(weight="bold")
        )
        session_status_label.grid(row=3, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._session_status_label = ctk.CTkLabel(
            self._session_details_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self._session_status_label.grid(row=3, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Session created date
        session_created_label = ctk.CTkLabel(
            self._session_details_frame,
            text="Created:",
            font=ctk.CTkFont(weight="bold")
        )
        session_created_label.grid(row=4, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self._session_created_label = ctk.CTkLabel(
            self._session_details_frame,
            text="-",
            font=ctk.CTkFont(size=12)
        )
        self._session_created_label.grid(row=4, column=1, columnspan=2, padx=(5, 10), pady=5, sticky="w")
        
        # Session goal
        session_goal_label = ctk.CTkLabel(
            self._session_details_frame,
            text="Goal:",
            font=ctk.CTkFont(weight="bold")
        )
        session_goal_label.grid(row=5, column=0, padx=(10, 5), pady=(10, 5), sticky="nw")
        
        self._session_goal_text = ctk.CTkTextbox(
            self._session_details_frame,
            height=100
        )
        self._session_goal_text.grid(row=5, column=1, columnspan=2, sticky="nsew", padx=10, pady=(10, 10))
        self._session_goal_text.configure(state="disabled")  # Initially disabled until session selected
        
        # Action buttons frame
        action_buttons_frame = ctk.CTkFrame(self._parent)
        action_buttons_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        action_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Load button
        self._load_button = ctk.CTkButton(
            action_buttons_frame,
            text="Load Session",
            command=self._load_selected_session,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green"),
            height=35
        )
        self._load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self._load_button.configure(state="disabled")  # Disabled until session selected
        
        # Delete button
        self._delete_button = ctk.CTkButton(
            action_buttons_frame,
            text="Delete Session",
            command=self._delete_selected_session,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            height=35
        )
        self._delete_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self._delete_button.configure(state="disabled")  # Disabled until session selected
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('available_sessions', self._on_available_sessions_changed)
        self._viewmodel.subscribe_property_change('current_session_id', self._on_current_session_changed)
        self._viewmodel.subscribe_property_change('session_filter', self._on_session_filter_changed)
        self._viewmodel.subscribe_property_change('is_loading_sessions', self._on_loading_sessions_changed)
        
        # Update initial state from ViewModel
        sessions = self._viewmodel.get_property('available_sessions', [])
        self._update_sessions_display(sessions)
        
        current_session_id = self._viewmodel.get_property('current_session_id')
        if current_session_id:
            self._update_session_selection(current_session_id)
    
    def _on_available_sessions_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel available sessions change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_sessions_display(new_value)
    
    def _on_current_session_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel current session change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_session_selection(new_value)
    
    def _on_session_filter_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel session filter change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        # In a real implementation, this would apply the filter to the display
        pass
    
    def _on_loading_sessions_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel loading sessions change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        if new_value:
            # Disable controls during loading
            self._disable_controls()
        else:
            # Re-enable controls after loading
            self._enable_controls()
    
    def _update_sessions_display(self, sessions: List[Dict[str, Any]]):
        """
        Update the sessions display with new sessions data.
        
        Args:
            sessions: List of session dictionaries to display
        """
        self._available_sessions = sessions
        
        # Clear and update the sessions list display
        if self._session_listbox:
            self._session_listbox.delete("1.0", "end")
            
            if not sessions:
                self._session_listbox.insert("1.0", "No sessions available")
                self._session_listbox.configure(state="disabled")
            else:
                self._session_listbox.configure(state="normal")
                session_titles = [session.get('title', 'Untitled Session') for session in sessions]
                
                for i, title in enumerate(session_titles):
                    self._session_listbox.insert(f"{i+1}.0", f"{title}\n")
                
                self._session_listbox.configure(state="disabled")
    
    def _update_session_selection(self, session_id: Optional[str]):
        """
        Update the UI to reflect the selected session.
        
        Args:
            session_id: ID of the selected session, or None if no selection
        """
        if session_id:
            # Find the selected session details
            selected_session = None
            for session in self._available_sessions:
                if session.get('id') == session_id:
                    selected_session = session
                    break
            
            if selected_session:
                # Enable action buttons when a session is selected
                self._load_button.configure(state="normal")
                self._delete_button.configure(state="normal")
                
                # Highlight the selected session in the listbox
                if self._session_listbox:
                    self._session_listbox.configure(state="normal")
                    self._session_listbox.delete("1.0", "end")
                    
                    for i, session in enumerate(self._available_sessions):
                        session_title = session.get('title', 'Untitled Session')
                        session_id_attr = session.get('id', '')
                        
                        if session_id_attr == session_id:
                            # Highlight selected session
                            self._session_listbox.insert(f"{i+1}.0", f"> {session_title}\n")
                        else:
                            self._session_listbox.insert(f"{i+1}.0", f"  {session_title}\n")
                    
                    self._session_listbox.configure(state="disabled")
                
                # Update session details display
                self._display_session_details(selected_session)
                self._selected_session_id = session_id
        else:
            # Disable action buttons when no session is selected
            self._load_button.configure(state="disabled")
            self._delete_button.configure(state="disabled")
            self._selected_session_id = None
            # Clear the display fields
            self._display_session_details(None)
    
    def _display_session_details(self, session_details: Optional[Dict[str, Any]]):
        """
        Display the details of a selected session.
        
        Args:
            session_details: Session details dictionary to display, or None to clear
        """
        if not session_details:
            # Clear the display fields
            if self._session_id_label:
                self._session_id_label.configure(text="-")
            if self._session_title_label:
                self._session_title_label.configure(text="-")
            if self._session_status_label:
                self._session_status_label.configure(text="-")
            if self._session_created_label:
                self._session_created_label.configure(text="-")
            if self._session_goal_text:
                self._session_goal_text.configure(state="normal")
                self._session_goal_text.delete("1.0", "end")
                self._session_goal_text.configure(state="disabled")
            return
        
        # Update the display fields with session details
        session_id = session_details.get('id', 'N/A')
        title = session_details.get('title', 'N/A')
        status = session_details.get('status', 'N/A')
        created_at = session_details.get('created_at', 'N/A')
        goal = session_details.get('goal', 'N/A')
        
        if self._session_id_label:
            self._session_id_label.configure(text=session_id)
        if self._session_title_label:
            self._session_title_label.configure(text=title)
        if self._session_status_label:
            self._session_status_label.configure(text=status)
        if self._session_created_label:
            self._session_created_label.configure(text=created_at)
        if self._session_goal_text:
            self._session_goal_text.configure(state="normal")
            self._session_goal_text.delete("1.0", "end")
            self._session_goal_text.insert("1.0", goal)
            self._session_goal_text.configure(state="disabled")
    
    def _on_search_changed(self, event=None):
        """Handle changes to the search field."""
        if self._search_entry:
            search_query = self._search_entry.get()
            # Update ViewModel with search query
            self._viewmodel.set_property('search_query', search_query)
            # Apply search filter to sessions list
            filtered_sessions = self._viewmodel.search_sessions(search_query)
            self._update_sessions_display(filtered_sessions)
    
    def _on_session_selected(self, event=None):
        """Handle clicking on a session in the list."""
        # In a real implementation, this would parse the clicked position
        # and select the corresponding session based on the display order
        
        # For now, we'll just refresh the display
        selected_session_id = self._viewmodel.get_property('current_session_id')
        if selected_session_id:
            # In a real implementation, we'd call the viewmodel to select the session
            pass
    
    def _load_selected_session(self):
        """Handle the Load Session button click."""
        if self._selected_session_id:
            # Execute the load session command in the ViewModel
            self._viewmodel.select_session(self._selected_session_id)
    
    def _delete_selected_session(self):
        """Handle the Delete Session button click."""
        if self._selected_session_id:
            # Execute the delete session command in the ViewModel
            try:
                self._viewmodel.delete_session(self._selected_session_id)
                # Update UI after deletion
                self._selected_session_id = None
                self._update_session_selection(None)  # Clear selection
            except ValueError as e:
                # Handle error (session not found, etc.)
                pass
    
    def _create_new_session(self):
        """Handle the Create New Session button click."""
        # This would open a dialog for creating a new session
        # For now, we'll just trigger the refresh
        self._refresh_sessions()
    
    def _refresh_sessions(self):
        """Handle the Refresh button click."""
        # Trigger ViewModel to reload sessions
        self._viewmodel.execute_command('refresh_sessions')
    
    def _disable_controls(self):
        """Disable UI controls during loading."""
        if self._search_entry:
            self._search_entry.configure(state="disabled")
        if self._refresh_button:
            self._refresh_button.configure(state="disabled", text="Reloading...")
        if self._new_session_button:
            self._new_session_button.configure(state="disabled")
        if self._load_button:
            self._load_button.configure(state="disabled")
        if self._delete_button:
            self._delete_button.configure(state="disabled")
    
    def _enable_controls(self):
        """Enable UI controls after loading."""
        if self._search_entry:
            self._search_entry.configure(state="normal")
        if self._refresh_button:
            self._refresh_button.configure(state="normal", text="Refresh")
        if self._new_session_button:
            self._new_session_button.configure(state="normal")
        # Keep action buttons enabled/disabled based on selection status
    
    def show(self):
        """Show the session view."""
        if not self._visible:
            self._visible = True
            self._parent.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Hide the session view."""
        if self._visible:
            self._visible = False
            self._parent.grid_remove()
    
    def refresh(self):
        """Refresh the session view display."""
        self._refresh_sessions()
    
    def select_session(self, session_id: str):
        """
        Select a specific session to display.
        
        Args:
            session_id: ID of the session to select
        """
        self._viewmodel.select_session(session_id)
    
    def get_selected_session_id(self) -> Optional[str]:
        """
        Get the ID of the currently selected session.
        
        Returns:
            ID of the selected session, or None if no session is selected
        """
        return self._viewmodel.get_property('current_session_id')
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get the list of all available sessions.
        
        Returns:
            List of session dictionaries
        """
        return self._available_sessions
    
    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """
        Search sessions by query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching session dictionaries
        """
        self._viewmodel.set_property('search_query', query)
        return self._viewmodel.search_sessions(query)
    
    def populate_sessions_list(self, sessions: List[Dict[str, Any]]):
        """
        Populate the sessions list with data.
        
        Args:
            sessions: List of session dictionaries to populate the list with
        """
        self._update_sessions_display(sessions)
    
    def clear_session_selection(self):
        """Clear the current session selection."""
        self._viewmodel.clear_current_session()
        self._update_session_selection(None)