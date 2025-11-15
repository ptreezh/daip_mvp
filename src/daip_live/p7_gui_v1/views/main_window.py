"""
Main Window View

This module implements the main window view for the P7 GUI application using CustomTkinter.
It implements the View portion of the MVVM architecture and binds to the MainViewModel.
"""

import customtkinter as ctk
from typing import Dict, Any, Optional
from .base import View
from ..viewmodel.main_viewmodel import MainViewModel


class MainWindow(View):
    """
    Main application window view.
    
    This view implements the main application interface with:
    - Navigation sidebar
    - Content area for different views
    - Status bar
    - Menu system
    """
    
    def __init__(self, parent: ctk.CTk, viewmodel: MainViewModel, theme_manager=None):
        """
        Initialize the MainWindow.
        
        Args:
            parent: Parent window (root CTk instance)
            viewmodel: MainViewModel instance to bind to
            theme_manager: Optional theme manager for theming
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._theme_manager = theme_manager
        self._current_view = 'chat'
        self._visible = False
        
        # Component references
        self._sidebar_frame: Optional[ctk.CTkFrame] = None
        self._main_container: Optional[ctk.CTkFrame] = None
        self._content_area: Optional[ctk.CTkFrame] = None
        self._navigation_frame: Optional[ctk.CTkFrame] = None
        self._status_bar: Optional[ctk.CTkFrame] = None
        self._input_area: Optional[ctk.CTkFrame] = None
        
        self._menu_buttons: Dict[str, ctk.CTkButton] = {}
        self._view_frames: Dict[str, ctk.CTkFrame] = {}
        
        # Initialize UI
        self._setup_window()
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_window(self):
        """Configure the main window properties."""
        self._parent.title("DAIP-LIVE P7 GUI")
        self._parent.geometry("1200x800")
        self._parent.minsize(800, 600)
        
        # Configure grid weights for responsive layout
        self._parent.grid_rowconfigure(0, weight=1)
        self._parent.grid_columnconfigure(1, weight=1)
    
    def _setup_components(self):
        """Create and arrange all UI components."""
        # Create sidebar frame
        self._sidebar_frame = ctk.CTkFrame(self._parent, width=200, corner_radius=0)
        self._sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self._sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Create logo label
        logo_label = ctk.CTkLabel(
            self._sidebar_frame, 
            text="DAIP-LIVE", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Create navigation buttons
        views = [
            ('Chat', 'chat'),
            ('Roles', 'roles'), 
            ('Sessions', 'sessions'),
            ('Debate', 'debate'),
            ('Knowledge', 'knowledge'),
            ('Settings', 'settings')
        ]
        
        row_offset = 1
        for display_name, view_name in views:
            button = ctk.CTkButton(
                self._sidebar_frame,
                text=display_name,
                command=lambda v=view_name: self.navigate_to_view(v)
            )
            button.grid(row=row_offset, column=0, padx=20, pady=5, sticky="ew")
            self._menu_buttons[view_name] = button
            row_offset += 1
        
        # Create main container
        self._main_container = ctk.CTkFrame(self._parent, fg_color="transparent")
        self._main_container.grid(row=0, column=1, sticky="nsew", padx=(20, 20), pady=(20, 0))
        self._main_container.grid_rowconfigure(0, weight=1)
        self._main_container.grid_columnconfigure(0, weight=1)
        
        # Create content area
        self._content_area = ctk.CTkFrame(self._main_container)
        self._content_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self._content_area.grid_rowconfigure(0, weight=1)
        self._content_area.grid_columnconfigure(0, weight=1)
        
        # Create status bar
        self._status_bar = ctk.CTkFrame(self._parent, height=30)
        self._status_bar.grid(row=1, column=1, sticky="ew", padx=(20, 20), pady=(0, 20))
        self._status_bar.grid_propagate(False)  # Keep constant height
        
        # Create status labels
        self._status_label = ctk.CTkLabel(self._status_bar, text="Ready", anchor="w")
        self._status_label.pack(side="left", padx=10, pady=5)
        
        self._view_status_label = ctk.CTkLabel(self._status_bar, text="Chat View", anchor="e")
        self._view_status_label.pack(side="right", padx=10, pady=5)
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('current_view', self._on_viewmodel_property_change)
        self._viewmodel.subscribe_property_change('is_processing', self._on_processing_change)
        self._viewmodel.subscribe_property_change('current_session', self._on_session_change)
        self._viewmodel.subscribe_property_change('available_sessions', self._on_sessions_change)
        self._viewmodel.subscribe_property_change('available_roles', self._on_roles_change)
        
        # Update initial state from ViewModel
        current_view = self._viewmodel.get_property('current_view', 'chat')
        self._current_view = current_view
        self._update_view_display(current_view)
        
        # Update other properties
        is_processing = self._viewmodel.get_property('is_processing', False)
        self._update_processing_state(is_processing)
        
        current_session = self._viewmodel.get_property('current_session', None)
        if current_session:
            self._update_session_info(current_session)
    
    def _on_viewmodel_property_change(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel property change notifications.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        if name == 'current_view':
            self._current_view = new_value
            self._update_view_display(new_value)
        elif name == 'is_processing':
            self._update_processing_state(new_value)
        elif name == 'current_session':
            self._update_session_info(new_value)
    
    def _on_processing_change(self, name: str, new_value: Any, old_value: Any):
        """Handle processing state changes."""
        self._update_processing_state(new_value)
    
    def _on_session_change(self, name: str, new_value: Any, old_value: Any):
        """Handle current session changes."""
        self._update_session_info(new_value)
    
    def _on_sessions_change(self, name: str, new_value: Any, old_value: Any):
        """Handle available sessions list changes."""
        self._update_sessions_list(new_value)
    
    def _on_roles_change(self, name: str, new_value: Any, old_value: Any):
        """Handle available roles list changes."""
        self._update_roles_list(new_value)
    
    def _update_view_display(self, view_name: str):
        """
        Update the displayed view.
        
        Args:
            view_name: Name of the view to display
        """
        # Update the view status label
        self._view_status_label.configure(text=f"{view_name.capitalize()} View")
        
        # Highlight the active menu button
        for button_view, button in self._menu_buttons.items():
            if button_view == view_name:
                button.configure(fg_color=("gray75", "gray25"))
            else:
                button.configure(fg_color=("gray90", "gray10"))
    
    def _update_processing_state(self, is_processing: bool):
        """
        Update the UI to reflect processing state.
        
        Args:
            is_processing: Whether the application is currently processing
        """
        if is_processing:
            self._status_label.configure(text="Processing...")
        else:
            self._status_label.configure(text="Ready")
    
    def _update_session_info(self, session_id: Optional[str]):
        """
        Update the UI to reflect current session info.
        
        Args:
            session_id: ID of the current session, or None if no session
        """
        if session_id:
            self._status_label.configure(text=f"Session: {session_id}")
        else:
            self._status_label.configure(text="No active session")
    
    def _update_sessions_list(self, sessions: list):
        """
        Update the UI to reflect available sessions list.
        
        Args:
            sessions: List of available session dictionaries
        """
        # In a real implementation, this would update a sessions dropdown/list
        pass
    
    def _update_roles_list(self, roles: list):
        """
        Update the UI to reflect available roles list.
        
        Args:
            roles: List of available role dictionaries
        """
        # In a real implementation, this would update a roles dropdown/list
        pass
    
    def navigate_to_view(self, view_name: str):
        """
        Navigate to a specific view.
        
        Args:
            view_name: Name of the view to navigate to
        """
        if view_name in self._menu_buttons:
            # Update ViewModel to switch view
            self._viewmodel.execute_command('switch_view', view_name)
    
    def show(self):
        """Display the main window."""
        if not self._visible:
            self._visible = True
            self._parent.deiconify()
    
    def hide(self):
        """Hide the main window."""
        if self._visible:
            self._visible = False
            self._parent.withdraw()
    
    def run(self):
        """Start the main event loop."""
        self.show()
        self._parent.mainloop()
    
    def destroy(self):
        """Destroy the main window."""
        self._parent.destroy()
    
    def update_status(self, message: str):
        """
        Update the status message.
        
        Args:
            message: New status message to display
        """
        self._status_label.configure(text=message)
    
    def get_current_view(self) -> str:
        """Get the currently displayed view."""
        return self._current_view
    
    def refresh_display(self):
        """Refresh the entire display."""
        # Force a UI update
        self._parent.update()
    
    # Public methods for view-specific operations
    def switch_to_chat_view(self):
        """Switch to the chat view."""
        self.navigate_to_view('chat')
    
    def switch_to_roles_view(self):
        """Switch to the roles view."""
        self.navigate_to_view('roles')
    
    def switch_to_sessions_view(self):
        """Switch to the sessions view."""
        self.navigate_to_view('sessions')
    
    def switch_to_debate_view(self):
        """Switch to the debate view."""
        self.navigate_to_view('debate')
    
    def switch_to_knowledge_view(self):
        """Switch to the knowledge view."""
        self.navigate_to_view('knowledge')
    
    def switch_to_settings_view(self):
        """Switch to the settings view."""
        self.navigate_to_view('settings')
    
    # View-specific content management
    def set_content_frame(self, view_name: str, frame: ctk.CTkFrame):
        """
        Set the content frame for a specific view.
        
        Args:
            view_name: Name of the view
            frame: Frame to display for the view
        """
        # Remove current content
        for widget in self._content_area.winfo_children():
            widget.destroy()
        
        # Add new content
        frame.pack(fill="both", expand=True)
        self._view_frames[view_name] = frame