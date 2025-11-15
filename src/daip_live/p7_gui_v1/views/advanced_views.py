"""
Advanced Views Implementation

This module implements the advanced views for the DAIP-LIVE system:
- DebateView: For managing debates with multiple participants
- KnowledgeView: For searching and managing knowledge base
"""

import customtkinter as ctk
from typing import Dict, Any, List, Optional
from .base import View
from ..viewmodel.debate_viewmodel import DebateViewModel
from ..viewmodel.knowledge_viewmodel import KnowledgeViewModel


class DebateView(View):
    """
    Debate View for managing multi-party debates.
    
    This view provides an interface for creating, participating in, and managing debates
    with multiple AI agents or human participants.
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: DebateViewModel):
        """
        Initialize the DebateView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: DebateViewModel instance to bind to
        """
        super().__init__(parent)
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._debate_area: Optional[ctk.CTkTextbox] = None
        self._participants_panel: Optional[ctk.CTkFrame] = None
        self._debate_controls: Optional[ctk.CTkFrame] = None
        self._topic_entry: Optional[ctk.CTkEntry] = None
        self._start_button: Optional[ctk.CTkButton] = None
        self._add_participant_button: Optional[ctk.CTkButton] = None
        self._arguments_area: Optional[ctk.CTkTextbox] = None
        self._argument_input: Optional[ctk.CTkTextbox] = None
        self._submit_argument_button: Optional[ctk.CTkButton] = None
        self._vote_area: Optional[ctk.CTkFrame] = None
        self._end_debate_button: Optional[ctk.CTkButton] = None
        
        # Internal state
        self._current_debate_id: Optional[str] = None
        self._participants: List[Dict[str, Any]] = []
        
        # Initialize UI components
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all debate view components."""
        # Configure parent grid
        self._parent.grid_rowconfigure(0, weight=0)  # Controls row
        self._parent.grid_rowconfigure(1, weight=1)  # Content row
        self._parent.grid_rowconfigure(2, weight=0)  # Input row
        self._parent.grid_columnconfigure(0, weight=1)  # Main content
        self._parent.grid_columnconfigure(1, weight=0)  # Participants panel
        
        # Create top controls frame
        controls_frame = ctk.CTkFrame(self._parent)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        controls_frame.grid_columnconfigure(0, weight=1)  # Topic entry
        controls_frame.grid_columnconfigure(1, weight=0)  # Start button
        controls_frame.grid_columnconfigure(2, weight=0)  # End button
        
        # Topic entry
        self._topic_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Enter debate topic...",
            height=40
        )
        self._topic_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._topic_entry.bind("<Return>", lambda e: self._on_start_debate_clicked())
        
        # Start debate button
        self._start_button = ctk.CTkButton(
            controls_frame,
            text="Start Debate",
            command=self._on_start_debate_clicked,
            fg_color="green",
            hover_color="darkgreen",
            height=40
        )
        self._start_button.grid(row=0, column=1, padx=(0, 5))
        
        # End debate button
        self._end_debate_button = ctk.CTkButton(
            controls_frame,
            text="End Debate",
            command=self._on_end_debate_clicked,
            fg_color="red",
            hover_color="darkred",
            height=40
        )
        self._end_debate_button.grid(row=0, column=2)
        self._end_debate_button.configure(state="disabled")  # Disabled until debate active
        
        # Create main content area (split between debate area and participants)
        content_frame = ctk.CTkFrame(self._parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Create debate display area
        self._debate_area = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=12)
        )
        self._debate_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._debate_area.configure(state="disabled")  # Initially disabled until debate starts
        
        # Create participants panel (right side)
        self._participants_panel = ctk.CTkFrame(self._parent)
        self._participants_panel.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        self._participants_panel.grid_rowconfigure(1, weight=1)
        self._participants_panel.grid_columnconfigure(0, weight=1)
        
        # Panel header
        participants_header = ctk.CTkLabel(
            self._participants_panel,
            text="Participants",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        participants_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Participants listbox
        self._participants_listbox = ctk.CTkTextbox(
            self._participants_panel,
            height=200
        )
        self._participants_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self._participants_listbox.configure(state="disabled")
        
        # Add participant button
        self._add_participant_button = ctk.CTkButton(
            self._participants_panel,
            text="+ Add Participant",
            command=self._on_add_participant_clicked,
            height=35
        )
        self._add_participant_button.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # Create input area (below content)
        input_frame = ctk.CTkFrame(self._parent)
        input_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(1, weight=0)
        
        # Argument input
        self._argument_input = ctk.CTkTextbox(
            input_frame,
            height=60,
            font=ctk.CTkFont(size=12)
        )
        self._argument_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Submit argument button
        self._submit_argument_button = ctk.CTkButton(
            input_frame,
            text="Submit\nArgument",
            command=self._on_submit_argument_clicked,
            height=60
        )
        self._submit_argument_button.grid(row=0, column=1)
        self._submit_argument_button.configure(state="disabled")  # Disabled until debate active
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('current_debate_data', self._on_debate_data_changed)
        self._viewmodel.subscribe_property_change('current_participants', self._on_participants_changed)
        self._viewmodel.subscribe_property_change('debate_arguments', self._on_arguments_changed)
        self._viewmodel.subscribe_property_change('is_active_debate', self._on_active_debate_changed)
        
        # Update initial state from ViewModel
        current_debate = self._viewmodel.get_property('current_debate_data')
        if current_debate:
            self._update_debate_display(current_debate)
        
        participants = self._viewmodel.get_property('current_participants', [])
        self._update_participants_display(participants)
        
        is_active = self._viewmodel.get_property('is_active_debate', False)
        self._update_active_state(is_active)
    
    def _on_debate_data_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle debate data changes from ViewModel."""
        self._update_debate_display(new_value)
    
    def _on_participants_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle participants list changes from ViewModel."""
        self._update_participants_display(new_value)
    
    def _on_arguments_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle arguments list changes from ViewModel."""
        self._update_arguments_display(new_value)
    
    def _on_active_debate_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle active debate status changes from ViewModel."""
        self._update_active_state(new_value)
    
    def _update_debate_display(self, debate_data: Optional[Dict[str, Any]]):
        """Update the debate display with new data."""
        if not debate_data:
            # Clear the debate area
            self._debate_area.configure(state="normal")
            self._debate_area.delete("1.0", "end")
            self._debate_area.insert("1.0", "No active debate. Start a new debate to begin.")
            self._debate_area.configure(state="disabled")
            return
        
        # Update debate display with debate information
        self._debate_area.configure(state="normal")
        self._debate_area.delete("1.0", "end")
        
        # Add debate topic
        topic = debate_data.get('topic', 'Unknown Topic')
        self._debate_area.insert("1.0", f" debating: {topic}\n")
        self._debate_area.insert("2.0", "=" * 50 + "\n\n")
        
        # Add arguments
        arguments = debate_data.get('arguments', [])
        for i, arg in enumerate(arguments):
            arg_text = f"🗣️ {arg.get('participant_name', 'Unknown')}:\n{arg['content']}\n\n"
            self._debate_area.insert(f"end", arg_text)
        
        self._debate_area.configure(state="disabled")
        self._debate_area.see("end")  # Scroll to bottom
    
    def _update_participants_display(self, participants: List[Dict[str, Any]]):
        """Update the participants display."""
        self._participants = participants
        
        # Clear and update participants list
        if self._participants_listbox:
            self._participants_listbox.configure(state="normal")
            self._participants_listbox.delete("1.0", "end")
            
            if not participants:
                self._participants_listbox.insert("1.0", "No participants\n")
                self._participants_listbox.configure(state="disabled")
                return
            
            # Add each participant to the display
            for i, participant in enumerate(participants):
                participant_text = f"• {participant.get('name', 'Unknown')}\n"
                if participant.get('status') == 'speaking':
                    participant_text = f"📢 {participant.get('name', 'Unknown')} (Speaking)\n"
                elif participant.get('status') == 'thinking':
                    participant_text = f"🤔 {participant.get('name', 'Unknown')} (Thinking)\n"
                self._participants_listbox.insert(f"{i+1}.0", participant_text)
            
            self._participants_listbox.configure(state="disabled")
    
    def _update_arguments_display(self, arguments: List[Dict[str, Any]]):
        """Update the arguments display."""
        # For now, rely on the overall debate display update
        # In a real implementation, this might update a specific arguments area
        pass
    
    def _update_active_state(self, is_active: bool):
        """Update UI based on whether a debate is active."""
        if is_active:
            # Debate is active - enable controls
            self._debate_area.configure(state="disabled")
            self._argument_input.configure(state="normal")
            self._submit_argument_button.configure(state="normal")
            self._start_button.configure(state="disabled")
            self._end_debate_button.configure(state="normal")
        else:
            # Debate is inactive - disable controls
            self._argument_input.configure(state="disabled")
            self._submit_argument_button.configure(state="disabled") 
            self._start_button.configure(state="normal")
            self._end_debate_button.configure(state="disabled")
    
    def _on_start_debate_clicked(self):
        """Handle Start Debate button click."""
        topic = self._topic_entry.get().strip()
        if not topic:
            # Show error message
            self._show_message("Please enter a debate topic", "error")
            return
        
        # Execute start debate command
        self._viewmodel.execute_command('start_debate', topic)
    
    def _on_end_debate_clicked(self):
        """Handle End Debate button click."""
        # Execute end debate command
        self._viewmodel.execute_command('end_debate')
        self._topic_entry.delete(0, "end")  # Clear topic when debate ends
    
    def _on_add_participant_clicked(self):
        """Handle Add Participant button click."""
        # In a real implementation, this would open a dialog to select participant
        # For now, we'll just execute the command
        self._viewmodel.execute_command('load_available_participants')
    
    def _on_submit_argument_clicked(self):
        """Handle Submit Argument button click."""
        argument = self._argument_input.get("1.0", "end").strip()
        if not argument:
            self._show_message("Please enter an argument", "warning")
            return
        
        # Submit the argument via ViewModel
        self._viewmodel.execute_command('submit_argument', argument)
        
        # Clear the input
        self._argument_input.delete("1.0", "end")
    
    def _show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user."""
        # In a real implementation, this would show a popup or status message
        print(f"[{message_type.upper()}] {message}")
    
    # Public methods for external control
    def start_debate(self, topic: str):
        """Start a new debate with the given topic."""
        self._topic_entry.delete(0, "end")
        self._topic_entry.insert(0, topic)
        self._on_start_debate_clicked()
    
    def end_debate(self):
        """End the current debate."""
        self._on_end_debate_clicked()
    
    def add_participant(self, participant_id: str, name: str):
        """Add a participant to the current debate."""
        self._viewmodel.add_participant(participant_id, name)
    
    def submit_argument(self, argument: str):
        """Submit an argument to the current debate."""
        self._argument_input.delete("1.0", "end")
        self._argument_input.insert("1.0", argument)
        self._on_submit_argument_clicked()
    
    def cast_vote(self, option: str, participant_id: str = None):
        """Cast a vote in the current debate."""
        self._viewmodel.execute_command('cast_vote', option, participant_id)
    
    def get_current_debate_id(self) -> Optional[str]:
        """Get the ID of the current debate."""
        return self._viewmodel.get_active_debate_id()
    
    def is_debate_active(self) -> bool:
        """Check if there's an active debate."""
        return self._viewmodel.is_debate_active()
    
    def get_participants(self) -> List[Dict[str, Any]]:
        """Get the list of participants in the current debate."""
        return self._participants
    
    def clear_current_debate(self):
        """Clear the current debate information."""
        self._debate_area.configure(state="normal")
        self._debate_area.delete("1.0", "end")
        self._debate_area.insert("1.0", "No active debate. Start a new debate to begin.")
        self._debate_area.configure(state="disabled")
        self._update_participants_display([])
        self._topic_entry.delete(0, "end")
    
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
        """Refresh the debate view."""
        # Refresh the display with current ViewModel state
        current_debate = self._viewmodel.get_active_debate_data()
        self._update_debate_display(current_debate)
        
        participants = self._viewmodel.get_current_participants()
        self._update_participants_display(participants)
        
        is_active = self._viewmodel.is_debate_active()
        self._update_active_state(is_active)
    
    def navigate_to_knowledge(self):
        """Navigate to the knowledge view."""
        # This would be handled by the main window controller
        pass


class KnowledgeView(View):
    """
    Knowledge Base View for searching and managing knowledge documents.
    
    This view provides an interface for searching the knowledge base,
    viewing documents, filtering results, and managing document collections.
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: KnowledgeViewModel):
        """
        Initialize the KnowledgeView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: KnowledgeViewModel instance to bind to
        """
        super().__init__(parent)
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._search_frame: Optional[ctk.CTkFrame] = None
        self._search_entry: Optional[ctk.CTkEntry] = None
        self._search_button: Optional[ctk.CTkButton] = None
        self._results_area: Optional[ctk.CTkTextbox] = None
        self._document_viewer: Optional[ctk.CTkTextbox] = None
        self._document_content: Optional[ctk.CTkTextbox] = None
        self._filters_frame: Optional[ctk.CTkFrame] = None
        self._category_filter: Optional[ctk.CTkComboBox] = None
        self._tag_filter: Optional[ctk.CTkEntry] = None
        self._recent_searches: Optional[ctk.CTkTextbox] = None
        self._add_document_button: Optional[ctk.CTkButton] = None
        self._bookmarks_area: Optional[ctk.CTkTextbox] = None
        
        # Internal state
        self._current_document: Optional[Dict[str, Any]] = None
        self._search_results: List[Dict[str, Any]] = []
        
        # Initialize UI components
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all knowledge view components."""
        # Configure parent grid
        self._parent.grid_rowconfigure(0, weight=0)  # Search area
        self._parent.grid_rowconfigure(1, weight=0)  # Filters
        self._parent.grid_rowconfigure(2, weight=1)  # Results/main content
        self._parent.grid_rowconfigure(3, weight=0)  # Document viewer
        self._parent.grid_columnconfigure(0, weight=1)  # Main content
        self._parent.grid_columnconfigure(1, weight=0)  # Side panel
        
        # Create search frame (top)
        self._search_frame = ctk.CTkFrame(self._parent)
        self._search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self._search_frame.grid_columnconfigure(0, weight=1)
        self._search_frame.grid_columnconfigure(1, weight=0)
        self._search_frame.grid_columnconfigure(2, weight=0)
        
        # Search entry
        self._search_entry = ctk.CTkEntry(
            self._search_frame,
            placeholder_text="Search knowledge base...",
            height=40
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._search_entry.bind("<Return>", lambda e: self._on_search_clicked())
        
        # Search button
        self._search_button = ctk.CTkButton(
            self._search_frame,
            text="🔍 Search",
            command=self._on_search_clicked,
            height=40
        )
        self._search_button.grid(row=0, column=1, padx=(0, 5))
        
        # Add document button
        self._add_document_button = ctk.CTkButton(
            self._search_frame,
            text="+ Add Doc",
            command=self._on_add_document_clicked,
            height=40
        )
        self._add_document_button.grid(row=0, column=2)
        
        # Create filters frame (below search)
        self._filters_frame = ctk.CTkFrame(self._parent)
        self._filters_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        self._filters_frame.grid_columnconfigure(0, weight=0)  # Category
        self._filters_frame.grid_columnconfigure(1, weight=0)  # Tags
        self._filters_frame.grid_columnconfigure(2, weight=1)  # Spacing
        self._filters_frame.grid_columnconfigure(3, weight=0)  # Clear filters
        
        # Category filter
        ctk.CTkLabel(self._filters_frame, text="Category:").grid(row=0, column=0, padx=(0, 5), pady=5)
        self._category_filter = ctk.CTkComboBox(
            self._filters_frame,
            values=["All", "Technical", "Research", "Documentation", "Training"],
            state="readonly",
            width=120
        )
        self._category_filter.set("All")
        self._category_filter.grid(row=0, column=1, padx=(0, 10), pady=5)
        self._category_filter.bind("<<ComboboxSelected>>", self._on_category_filter_changed)
        
        # Tags filter
        ctk.CTkLabel(self._filters_frame, text="Tags:").grid(row=0, column=2, padx=(10, 5), pady=5)
        self._tag_filter = ctk.CTkEntry(
            self._filters_frame,
            placeholder_text="Filter by tags...",
            width=100
        )
        self._tag_filter.grid(row=0, column=3, padx=(0, 10), pady=5)
        self._tag_filter.bind("<Return>", lambda e: self._on_tag_filter_applied())
        
        # Clear filters button
        clear_filter_btn = ctk.CTkButton(
            self._filters_frame,
            text="Clear Filters",
            command=self._on_clear_filters_clicked,
            height=25
        )
        clear_filter_btn.grid(row=0, column=4, pady=5)
        
        # Create main content frame (split between results and document viewer)
        content_frame = ctk.CTkFrame(self._parent)
        content_frame.grid(row=2, column=0, sticky="nsew", padx=(10, 5), pady=(0, 5))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Create results area (left side)
        results_header = ctk.CTkLabel(
            content_frame,
            text="Search Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_header.grid(row=0, column=0, padx=10, pady=(0, 5), sticky="w")
        
        self._results_area = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self._results_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._results_area.configure(state="disabled")
        
        # Create document viewer (right side)
        doc_header = ctk.CTkLabel(
            content_frame,
            text="Document Viewer",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        doc_header.grid(row=0, column=1, padx=(5, 10), pady=(0, 5), sticky="w")
        
        self._document_viewer = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=12)
        )
        self._document_viewer.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))
        self._document_viewer.configure(state="disabled")
        
        # Create side panel for recent searches and bookmarks (right side of whole view)
        side_panel = ctk.CTkFrame(self._parent)
        side_panel.grid(row=2, column=1, sticky="nsew", padx=(5, 10), pady=(0, 5))
        side_panel.grid_rowconfigure(1, weight=1)
        side_panel.grid_rowconfigure(3, weight=1)
        side_panel.grid_columnconfigure(0, weight=1)
        
        # Recent searches section
        recent_header = ctk.CTkLabel(
            side_panel,
            text="Recent Searches",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        recent_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self._recent_searches = ctk.CTkTextbox(
            side_panel,
            height=150,
            font=ctk.CTkFont(size=10)
        )
        self._recent_searches.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._recent_searches.configure(state="disabled")
        
        # Bookmarks section
        bookmarks_header = ctk.CTkLabel(
            side_panel,
            text="Bookmarks",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        bookmarks_header.grid(row=2, column=0, padx=10, pady=(5, 5), sticky="w")
        
        self._bookmarks_area = ctk.CTkTextbox(
            side_panel,
            height=150,
            font=ctk.CTkFont(size=10)
        )
        self._bookmarks_area.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self._bookmarks_area.configure(state="disabled")
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('search_results', self._on_search_results_changed)
        self._viewmodel.subscribe_property_change('current_document', self._on_current_document_changed)
        self._viewmodel.subscribe_property_change('recent_searches', self._on_recent_searches_changed)
        self._viewmodel.subscribe_property_change('available_documents', self._on_documents_changed)
        
        # Update initial state from ViewModel
        search_results = self._viewmodel.get_property('search_results', [])
        self._update_search_results_display(search_results)
        
        current_doc = self._viewmodel.get_property('current_document')
        if current_doc:
            self._update_document_display(current_doc)
        
        recent_searches = self._viewmodel.get_property('recent_searches', [])
        self._update_recent_searches_display(recent_searches)
    
    def _on_search_results_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle search results changes from ViewModel."""
        self._search_results = new_value if new_value else []
        self._update_search_results_display(self._search_results)
    
    def _on_current_document_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle current document changes from ViewModel."""
        self._current_document = new_value
        self._update_document_display(new_value)
    
    def _on_recent_searches_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle recent searches changes from ViewModel."""
        self._update_recent_searches_display(new_value if new_value else [])
    
    def _on_documents_changed(self, name: str, new_value: Any, old_value: Any):
        """Handle available documents changes from ViewModel."""
        # This could update the document listings
        pass
    
    def _update_search_results_display(self, results: List[Dict[str, Any]]):
        """Update the search results display."""
        if not self._results_area:
            return
        
        self._results_area.configure(state="normal")
        self._results_area.delete("1.0", "end")
        
        if not results:
            self._results_area.insert("1.0", "No results found.\n\nEnter a search query above to search the knowledge base.")
            self._results_area.configure(state="disabled")
            return
        
        # Display search results
        for i, result in enumerate(results):
            title = result.get('title', 'Untitled Document')
            content_preview = result.get('content', '')[:200]  # Preview first 200 chars
            score = result.get('score', 0)
            
            result_text = f"📄 {title} (Score: {score:.2f})\n"
            result_text += f"  {content_preview}...\n\n"
            
            self._results_area.insert(f"{i*3+1}.0", result_text)
        
        self._results_area.configure(state="disabled")
    
    def _update_document_display(self, document: Optional[Dict[str, Any]]):
        """Update the document viewer display."""
        if not self._document_viewer:
            return
        
        self._document_viewer.configure(state="normal")
        self._document_viewer.delete("1.0", "end")
        
        if not document:
            self._document_viewer.insert("1.0", "No document selected.\n\nSelect a document from the search results to view its content.")
            self._document_viewer.configure(state="disabled")
            return
        
        # Display document content
        title = document.get('title', 'Untitled Document')
        content = document.get('content', 'No content available')
        category = document.get('category', 'Uncategorized')
        tags = ', '.join(document.get('tags', []))
        
        doc_text = f"📄 {title}\n"
        doc_text += f"📁 Category: {category}\n"
        if tags:
            doc_text += f"🏷️ Tags: {tags}\n"
        doc_text += "\n" + "="*50 + "\n\n"
        doc_text += content
        
        self._document_viewer.insert("1.0", doc_text)
        self._document_viewer.configure(state="disabled")
    
    def _update_recent_searches_display(self, searches: List[str]):
        """Update the recent searches display."""
        if not self._recent_searches:
            return
        
        self._recent_searches.configure(state="normal")
        self._recent_searches.delete("1.0", "end")
        
        if not searches:
            self._recent_searches.insert("1.0", "No recent searches.\n")
        else:
            for i, search in enumerate(searches):
                self._recent_searches.insert(f"{i+1}.0", f"• {search}\n")
        
        self._recent_searches.configure(state="disabled")
    
    def _on_search_clicked(self):
        """Handle Search button click."""
        query = self._search_entry.get().strip()
        if not query:
            self._show_message("Please enter a search query", "warning")
            return
        
        # Execute search command via ViewModel
        self._viewmodel.execute_command('search_knowledge', query)
    
    def _on_add_document_clicked(self):
        """Handle Add Document button click."""
        # In a real implementation, this would open a file dialog
        # For now, we'll just execute the command
        self._viewmodel.execute_command('add_document_dialog')
    
    def _on_category_filter_changed(self, event=None):
        """Handle category filter change."""
        selected_category = self._category_filter.get()
        # Execute filter command
        if selected_category.lower() != 'all':
            self._viewmodel.execute_command('filter_by_category', selected_category)
        else:
            self._viewmodel.execute_command('clear_category_filter')
    
    def _on_tag_filter_applied(self, event=None):
        """Handle tag filter application."""
        tag_filter = self._tag_filter.get().strip()
        if tag_filter:
            self._viewmodel.execute_command('filter_by_tags', tag_filter.split(','))
        else:
            self._viewmodel.execute_command('clear_tag_filter')
    
    def _on_clear_filters_clicked(self):
        """Handle Clear Filters button click."""
        self._category_filter.set("All")
        self._tag_filter.delete(0, "end")
        self._viewmodel.execute_command('clear_all_filters')
    
    def _show_message(self, message: str, message_type: str = "info"):
        """Show a message to the user."""
        # In a real implementation, this would show a popup or status message
        print(f"[{message_type.upper()}] {message}")
    
    # Public methods for external control
    def perform_search(self, query: str):
        """Perform a search in the knowledge base."""
        self._search_entry.delete(0, "end")
        self._search_entry.insert(0, query)
        self._on_search_clicked()
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Display search results."""
        self._update_search_results_display(results)
    
    def view_document(self, doc_id: str):
        """View a specific document."""
        self._viewmodel.select_document(doc_id)
    
    def filter_results(self, filters: Dict[str, Any]):
        """Filter search results based on criteria."""
        if 'category' in filters:
            self._category_filter.set(filters['category'])
            self._on_category_filter_changed()
        if 'tags' in filters:
            self._tag_filter.delete(0, "end")
            self._tag_filter.insert(0, ','.join(filters['tags']))
            self._on_tag_filter_applied()
    
    def add_document(self):
        """Initiate adding a new document."""
        self._on_add_document_clicked()
    
    def bookmark_document(self, doc_id: str):
        """Bookmark the current document."""
        self._viewmodel.execute_command('bookmark_document', doc_id)
    
    def get_search_query(self) -> str:
        """Get the current search query."""
        return self._search_entry.get() if self._search_entry else ""
    
    def get_current_document(self) -> Optional[Dict[str, Any]]:
        """Get the currently displayed document."""
        return self._current_document
    
    def get_search_results(self) -> List[Dict[str, Any]]:
        """Get the current search results."""
        return self._search_results
    
    def get_recent_searches(self) -> List[str]:
        """Get the recent searches list."""
        return self._viewmodel.get_recent_searches()
    
    def clear_search(self):
        """Clear the search query and results."""
        if self._search_entry:
            self._search_entry.delete(0, "end")
        self._update_search_results_display([])
        self._update_document_display(None)
    
    def show(self):
        """Show the knowledge view."""
        if not self._visible:
            self._visible = True
            self._parent.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        """Hide the knowledge view."""
        if self._visible:
            self._visible = False
            self._parent.grid_remove()
    
    def refresh(self):
        """Refresh the knowledge view."""
        # Refresh with current ViewModel state
        search_results = self._viewmodel.get_search_results()
        self._update_search_results_display(search_results)
        
        current_doc = self._viewmodel.get_current_document()
        self._update_document_display(current_doc)
        
        recent_searches = self._viewmodel.get_recent_searches()
        self._update_recent_searches_display(recent_searches)
    
    def navigate_to_debate(self):
        """Navigate to the debate view."""
        # This would be handled by the main window controller
        pass