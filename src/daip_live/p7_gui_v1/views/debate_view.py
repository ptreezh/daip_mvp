"""
Debate View

This module implements the debate view for the P7 GUI application using CustomTkinter.
It provides interface for multi-agent debates with participant management and argument tracking.
"""

import customtkinter as ctk
from typing import Any, Dict, List, Optional
from .base import View
from ..viewmodel.debate_viewmodel import DebateViewModel


class DebateView(View):
    """
    Debate view implementation for the P7 GUI application.
    
    This view provides:
    - Debate creation interface
    - Participant management
    - Argument display and submission
    - Debate progress tracking
    - Voting mechanism
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: DebateViewModel):
        """
        Initialize the DebateView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: DebateViewModel instance to bind to
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._debate_topic_entry: Optional[ctk.CTkEntry] = None
        self._participants_frame: Optional[ctk.CTkScrollableFrame] = None
        self._arguments_frame: Optional[ctk.CTkScrollableFrame] = None
        self._argument_input: Optional[ctk.CTkTextbox] = None
        self._submit_argument_button: Optional[ctk.CTkButton] = None
        self._vote_frame: Optional[ctk.CTkFrame] = None
        self._start_debate_button: Optional[ctk.CTkButton] = None
        self._end_debate_button: Optional[ctk.CTkButton] = None
        self._debate_status_label: Optional[ctk.CTkLabel] = None
        self._current_debate_id: Optional[str] = None
        
        # Initialize UI
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all debate view components."""
        # Configure parent frame
        self._parent.grid_rowconfigure(0, weight=0)  # Controls row
        self._parent.grid_rowconfigure(1, weight=1)  # Content row
        self._parent.grid_columnconfigure(0, weight=1)
        
        # Create control frame
        control_frame = ctk.CTkFrame(self._parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=0)
        control_frame.grid_columnconfigure(2, weight=0)
        
        # Debate topic entry
        self._debate_topic_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Enter debate topic...",
            height=40
        )
        self._debate_topic_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Start debate button
        self._start_debate_button = ctk.CTkButton(
            control_frame,
            text="Start Debate",
            command=self._start_debate,
            fg_color=("green", "darkgreen"),
            height=40
        )
        self._start_debate_button.grid(row=0, column=1, padx=(0, 5))
        
        # End debate button
        self._end_debate_button = ctk.CTkButton(
            control_frame,
            text="End Debate",
            command=self._end_debate,
            fg_color=("red", "darkred"),
            height=40
        )
        self._end_debate_button.grid(row=0, column=2)
        
        # Create main content frame with split for participants and arguments
        content_frame = ctk.CTkFrame(self._parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=0)  # Participants column
        content_frame.grid_columnconfigure(1, weight=1)  # Arguments column
        
        # Create participants frame
        participants_container = ctk.CTkFrame(content_frame)
        participants_container.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=0)
        participants_container.grid_rowconfigure(1, weight=1)
        participants_container.grid_columnconfigure(0, weight=1)
        
        # Participants header
        ctk.CTkLabel(
            participants_container,
            text="Participants",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Participants list
        self._participants_frame = ctk.CTkScrollableFrame(
            participants_container,
            label_text="Debate Participants",
            height=400,
            width=200
        )
        self._participants_frame.grid(row=1, column=0, sticky="ns", padx=10, pady=(5, 10))
        
        # Create arguments frame
        arguments_container = ctk.CTkFrame(content_frame)
        arguments_container.grid(row=0, column=1, sticky="nsew", pady=0)
        arguments_container.grid_rowconfigure(1, weight=1)
        arguments_container.grid_columnconfigure(0, weight=1)
        
        # Arguments header
        ctk.CTkLabel(
            arguments_container,
            text="Arguments",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Arguments display
        self._arguments_frame = ctk.CTkScrollableFrame(
            arguments_container,
            label_text="Debate Arguments",
            height=400
        )
        self._arguments_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        arguments_container.grid_rowconfigure(1, weight=1)
        
        # Create input area for new arguments
        input_frame = ctk.CTkFrame(self._parent)
        input_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)
        
        # Argument input
        self._argument_input = ctk.CTkTextbox(
            input_frame,
            height=60
        )
        self._argument_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Submit button
        self._submit_argument_button = ctk.CTkButton(
            input_frame,
            text="Submit Argument",
            command=self._submit_argument,
            height=60
        )
        self._submit_argument_button.grid(row=0, column=1)
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('current_debate_id', self._on_current_debate_changed)
        self._viewmodel.subscribe_property_change('participants', self._on_participants_changed)
        self._viewmodel.subscribe_property_change('arguments', self._on_arguments_changed)
        self._viewmodel.subscribe_property_change('debate_status', self._on_debate_status_changed)
        self._viewmodel.subscribe_property_change('is_active_debate', self._on_active_debate_changed)
        
        # Update initial state from ViewModel
        current_debate_id = self._viewmodel.get_property('current_debate_id')
        if current_debate_id:
            self._current_debate_id = current_debate_id
            self._update_participants_display()
            self._update_arguments_display()
    
    def _on_current_debate_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel current debate ID change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._current_debate_id = new_value
        # Update UI based on debate ID change
        if new_value:
            self._start_debate_button.configure(state="disabled")
            self._end_debate_button.configure(state="normal")
        else:
            self._start_debate_button.configure(state="normal")
            self._end_debate_button.configure(state="disabled")
    
    def _on_participants_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel participants list change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_participants_display()
    
    def _on_arguments_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel arguments list change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_arguments_display()
    
    def _on_debate_status_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel debate status change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        # Update status display
        if self._debate_status_label:
            self._debate_status_label.configure(text=f"Status: {new_value}")
    
    def _on_active_debate_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel active debate status change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        # Update UI based on active debate status
        if new_value:
            self._argument_input.configure(state="normal")
            self._submit_argument_button.configure(state="normal")
        else:
            self._argument_input.configure(state="disabled")
            self._submit_argument_button.configure(state="disabled")
    
    def _update_participants_display(self):
        """Update the display of debate participants."""
        participants = self._viewmodel.get_available_participants()
        
        if self._participants_frame:
            # Clear existing participants
            for widget in self._participants_frame.winfo_children():
                widget.destroy()
            
            # Add participants to display
            for participant in participants:
                participant_name = participant.get('name', 'Unknown')
                participant_status = participant.get('status', 'active')
                
                label_text = f"{participant_name} - {participant_status}"
                participant_label = ctk.CTkLabel(
                    self._participants_frame,
                    text=label_text,
                    wraplength=180
                )
                participant_label.pack(pady=2, padx=5)
    
    def _update_arguments_display(self):
        """Update the display of debate arguments."""
        arguments = self._viewmodel.get_debate_arguments()
        
        if self._arguments_frame:
            # Clear existing arguments
            for widget in self._arguments_frame.winfo_children():
                widget.destroy()
            
            # Add arguments to display (sorted by timestamp/create order)
            for argument in arguments:
                speaker = argument.get('speaker', 'Unknown')
                content = argument.get('content', '')
                timestamp = argument.get('timestamp', '')
                
                arg_frame = ctk.CTkFrame(self._arguments_frame)
                arg_frame.pack(fill="x", pady=2, padx=5)
                
                # Speaker information
                speaker_label = ctk.CTkLabel(
                    arg_frame,
                    text=f"{speaker}:",
                    font=ctk.CTkFont(weight="bold")
                )
                speaker_label.pack(anchor="w", padx=5, pady=(5, 0))
                
                # Argument content
                content_label = ctk.CTkLabel(
                    arg_frame,
                    text=content,
                    wraplength=400
                )
                content_label.pack(fill="x", padx=5, pady=(2, 5))
                
                if timestamp:
                    time_label = ctk.CTkLabel(
                        arg_frame,
                        text=timestamp,
                        font=ctk.CTkFont(size=10)
                    )
                    time_label.pack(anchor="e", padx=5, pady=(0, 2))
    
    def _start_debate(self):
        """Handle start debate button click."""
        topic = self._debate_topic_entry.get().strip()
        if not topic:
            # Show error message
            print("Please enter a debate topic")
            return
        
        # Execute start debate command
        self._viewmodel.execute_command('start_debate', topic)
    
    def _end_debate(self):
        """Handle end debate button click."""
        if not self._current_debate_id:
            # No active debate to end
            print("No active debate to end")
            return
        
        # Execute end debate command
        self._viewmodel.execute_command('end_debate')
    
    def _submit_argument(self):
        """Handle submit argument button click."""
        if not self._current_debate_id:
            # No active debate to submit to
            print("No active debate to submit argument to")
            return
        
        argument_text = self._argument_input.get("1.0", "end").strip()
        if not argument_text:
            # No argument to submit
            print("Please enter an argument to submit")
            return
        
        # Execute submit argument command
        self._viewmodel.execute_command('submit_argument', argument_text)
        
        # Clear input
        self._argument_input.delete("1.0", "end")
    
    def show(self):
        """Show the debate view."""
        if not self._visible:
            self._visible = True
            self._parent.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Hide the debate view."""
        if self._visible:
            self._visible = False
            self._parent.grid_remove()
    
    def refresh(self):
        """Refresh the debate view display."""
        self._update_participants_display()
        self._update_arguments_display()
    
    def get_current_debate_id(self) -> Optional[str]:
        """
        Get the ID of the current debate.
        
        Returns:
            Current debate ID, or None if no debate active
        """
        return self._current_debate_id
    
    def is_debate_active(self) -> bool:
        """
        Check if a debate is currently active.
        
        Returns:
            True if debate active, False otherwise
        """
        return self._viewmodel.is_debate_active()
    
    def get_participants_count(self) -> int:
        """
        Get the number of participants in the current debate.
        
        Returns:
            Number of participants
        """
        return len(self._viewmodel.get_available_participants())
    
    def get_arguments_count(self) -> int:
        """
        Get the number of arguments in the current debate.
        
        Returns:
            Number of arguments
        """
        return len(self._viewmodel.get_debate_arguments())
    
    def clear_current_debate(self):
        """Clear the current debate information."""
        self._current_debate_id = None
        self._update_participants_display()
        self._update_arguments_display()