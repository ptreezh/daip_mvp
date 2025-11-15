"""
Knowledge Base View

This module implements the knowledge base view for the P7 GUI application using CustomTkinter.
It provides search functionality, document management, and knowledge browsing capabilities.
"""

import customtkinter as ctk
from typing import Any, Dict, List, Optional
from .base import View
from ..viewmodel.knowledge_viewmodel import KnowledgeViewModel


class KnowledgeView(View):
    """
    Knowledge base view implementation for the P7 GUI application.
    
    This view provides:
    - Knowledge search functionality
    - Document management interface
    - Search result display
    - Knowledge browsing
    - Document preview
    """
    
    def __init__(self, parent: ctk.CTkFrame, viewmodel: KnowledgeViewModel):
        """
        Initialize the KnowledgeView.
        
        Args:
            parent: Parent frame to contain this view
            viewmodel: KnowledgeViewModel instance to bind to
        """
        self._parent = parent
        self._viewmodel = viewmodel
        self._visible = False
        
        # Component references
        self._search_entry: Optional[ctk.CTkEntry] = None
        self._search_button: Optional[ctk.CTkButton] = None
        self._results_frame: Optional[ctk.CTkScrollableFrame] = None
        self._document_preview: Optional[ctk.CTkTextbox] = None
        self._document_details: Optional[ctk.CTkFrame] = None
        self._add_document_button: Optional[ctk.CTkButton] = None
        self._sync_button: Optional[ctk.CTkButton] = None
        self._search_history_frame: Optional[ctk.CTkScrollableFrame] = None
        self._knowledge_stats_label: Optional[ctk.CTkLabel] = None
        self._search_results: List[Dict[str, Any]] = []
        self._current_document: Optional[Dict[str, Any]] = None
        
        # Initialize UI
        self._setup_components()
        self._bind_to_viewmodel()
    
    def _setup_components(self):
        """Create and arrange all knowledge view components."""
        # Configure parent frame
        self._parent.grid_rowconfigure(0, weight=0)  # Header row (search/stats)
        self._parent.grid_rowconfigure(1, weight=1)  # Content row (results/preview)
        self._parent.grid_columnconfigure(0, weight=1)  # Main content
        
        # Create header frame with search and stats
        header_frame = ctk.CTkFrame(self._parent)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)  # Search entry
        header_frame.grid_columnconfigure(1, weight=0)  # Search button
        header_frame.grid_columnconfigure(2, weight=0)  # Add document button
        header_frame.grid_columnconfigure(3, weight=0)  # Sync button
        
        # Search entry
        self._search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search knowledge base...",
            height=40
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Search button
        self._search_button = ctk.CTkButton(
            header_frame,
            text="Search",
            command=self._perform_search,
            height=40
        )
        self._search_button.grid(row=0, column=1, padx=(0, 5))
        
        # Add document button
        self._add_document_button = ctk.CTkButton(
            header_frame,
            text="+ Add Doc",
            command=self._add_document,
            height=40
        )
        self._add_document_button.grid(row=0, column=2, padx=(0, 5))
        
        # Sync button
        self._sync_button = ctk.CTkButton(
            header_frame,
            text="Sync",
            command=self._sync_knowledge,
            height=40
        )
        self._sync_button.grid(row=0, column=3, padx=(0, 5))
        
        # Knowledge statistics
        self._knowledge_stats_label = ctk.CTkLabel(
            header_frame,
            text="Loading stats...",
            font=ctk.CTkFont(size=12)
        )
        self._knowledge_stats_label.grid(row=1, column=0, columnspan=4, sticky="w", padx=0, pady=(5, 0))
        
        # Create content frame with split for results and preview
        content_frame = ctk.CTkFrame(self._parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)  # Results column
        content_frame.grid_columnconfigure(1, weight=0)  # Preview column
        
        # Create results frame (left side)
        results_container = ctk.CTkFrame(content_frame)
        results_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        results_container.grid_rowconfigure(1, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        
        # Results header
        results_header = ctk.CTkLabel(
            results_container,
            text="Search Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Results display
        self._results_frame = ctk.CTkScrollableFrame(
            results_container,
            label_text="Knowledge Search Results",
            height=500
        )
        self._results_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self._results_frame.grid_columnconfigure(0, weight=1)
        results_container.grid_rowconfigure(1, weight=1)
        
        # Create document preview frame (right side)
        preview_container = ctk.CTkFrame(content_frame)
        preview_container.grid(row=0, column=1, sticky="nsew", pady=0)
        preview_container.grid_rowconfigure(1, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # Preview header
        preview_header = ctk.CTkLabel(
            preview_container,
            text="Document Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        preview_header.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Document preview area
        self._document_preview = ctk.CTkTextbox(
            preview_container,
            height=500
        )
        self._document_preview.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        preview_container.grid_rowconfigure(1, weight=1)
        
        # Initialize with some stats
        self._update_knowledge_statistics()
    
    def _bind_to_viewmodel(self):
        """Bind view components to ViewModel properties."""
        # Subscribe to ViewModel property changes
        self._viewmodel.subscribe_property_change('search_results', self._on_search_results_changed)
        self._viewmodel.subscribe_property_change('current_document', self._on_current_document_changed)
        self._viewmodel.subscribe_property_change('knowledge_base_status', self._on_knowledge_status_changed)
        self._viewmodel.subscribe_property_change('search_query', self._on_search_query_changed)
        self._viewmodel.subscribe_property_change('is_loading_knowledge', self._on_loading_status_changed)
        
        # Update initial state from ViewModel
        search_results = self._viewmodel.get_property('search_results', [])
        self._update_results_display(search_results)
        
        current_doc = self._viewmodel.get_property('current_document')
        if current_doc:
            self._current_document = current_doc
            self._update_document_preview(current_doc)
        
        status = self._viewmodel.get_property('knowledge_base_status')
        if status:
            self._update_knowledge_statistics()
    
    def _on_search_results_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel search results change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._search_results = new_value or []
        self._update_results_display(self._search_results)
    
    def _on_current_document_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel current document change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._current_document = new_value
        self._update_document_preview(new_value)
    
    def _on_knowledge_status_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel knowledge base status change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        self._update_knowledge_statistics()
    
    def _on_search_query_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel search query change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        if self._search_entry and new_value:
            self._search_entry.delete(0, "end")
            self._search_entry.insert(0, new_value)
    
    def _on_loading_status_changed(self, name: str, new_value: Any, old_value: Any):
        """
        Handle ViewModel loading status change.
        
        Args:
            name: Property name that changed
            new_value: New property value
            old_value: Previous property value
        """
        if self._search_button:
            if new_value:
                self._search_button.configure(state="disabled", text="Searching...")
            else:
                self._search_button.configure(state="normal", text="Search")
    
    def _update_results_display(self, results: List[Dict[str, Any]]):
        """
        Update the display of search results.
        
        Args:
            results: List of search result dictionaries
        """
        if not self._results_frame:
            return
        
        # Clear existing results
        for widget in self._results_frame.winfo_children():
            widget.destroy()
        
        if not results:
            no_results_label = ctk.CTkLabel(
                self._results_frame,
                text="No results found. Enter a search query above.",
                font=ctk.CTkFont(size=12, slant="italic")
            )
            no_results_label.pack(pady=20)
            return
        
        # Add results to display
        for i, result in enumerate(results):
            # Create result card
            result_card = ctk.CTkFrame(self._results_frame)
            result_card.grid(row=i, column=0, sticky="ew", padx=5, pady=5, ipadx=5, ipady=5)
            result_card.grid_columnconfigure(0, weight=1)
            
            # Document title
            title = result.get('title', result.get('name', 'Untitled Document'))
            title_label = ctk.CTkLabel(
                result_card,
                text=title,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2))
            
            # Document preview snippet
            content = result.get('content', result.get('text', result.get('body', '')))
            preview_text = (content[:200] + "...") if len(content) > 200 else content
            preview_label = ctk.CTkLabel(
                result_card,
                text=preview_text,
                font=ctk.CTkFont(size=11),
                wraplength=300
            )
            preview_label.grid(row=1, column=0, sticky="w", padx=10, pady=(2, 5))
            
            # Document metadata
            metadata_frame = ctk.CTkFrame(result_card, fg_color="transparent")
            metadata_frame.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
            
            if 'source' in result:
                source_label = ctk.CTkLabel(metadata_frame, text=f"📚 {result['source']}", font=ctk.CTkFont(size=10))
                source_label.pack(side="left", padx=(0, 10))
            
            if 'created_at' in result:
                time_label = ctk.CTkLabel(metadata_frame, text=f"🕒 {result['created_at'][:10]}", font=ctk.CTkFont(size=10))
                time_label.pack(side="left")
            
            # Click handler
            def make_handler(r):
                return lambda e: self._on_result_selected(r)
            
            result_card.bind("<Button-1>", make_handler(result))
            title_label.bind("<Button-1>", make_handler(result))
            preview_label.bind("<Button-1>", make_handler(result))
    
    def _update_document_preview(self, document: Optional[Dict[str, Any]]):
        """
        Update the document preview display.
        
        Args:
            document: Document dictionary to preview, or None to clear
        """
        if not self._document_preview:
            return
        
        self._document_preview.configure(state="normal")
        self._document_preview.delete("1.0", "end")
        
        if not document:
            self._document_preview.insert("1.0", "No document selected.\n\nSelect a search result to preview its content here.")
            self._document_preview.configure(state="disabled")
            return
        
        # Display document content with formatting
        doc_title = document.get('title', document.get('name', 'Untitled Document'))
        doc_content = document.get('content', document.get('text', document.get('body', '')))
        doc_source = document.get('source', 'Unknown Source')
        doc_created = document.get('created_at', 'Unknown Date')
        
        # Add document metadata
        self._document_preview.insert("1.0", f"📄 {doc_title}\n\n")
        self._document_preview.insert("end", f"📚 Source: {doc_source}\n")
        self._document_preview.insert("end", f"📅 Created: {doc_created}\n\n")
        
        # Add content
        self._document_preview.insert("end", doc_content)
        
        # Apply formatting to header
        self._document_preview.tag_add("title", "1.0", "1.end")
        self._document_preview.tag_configure("title", font=ctk.CTkFont(size=14, weight="bold"))
        
        self._document_preview.configure(state="disabled")
    
    def _update_knowledge_statistics(self):
        """Update the knowledge base statistics display."""
        status = self._viewmodel.get_property('knowledge_base_status')
        
        if status:
            total_docs = status.get('total_documents', 0)
            last_sync = status.get('last_sync', 'Never')
            status_text = status.get('status', 'Unknown')
            
            stats_text = f"📊 Index: {total_docs} docs | 🔄 Last sync: {last_sync[:10]} | 🟢 Status: {status_text}"
        else:
            stats_text = "📊 Knowledge base stats: Loading..."
        
        if self._knowledge_stats_label:
            self._knowledge_stats_label.configure(text=stats_text)
    
    def _perform_search(self):
        """Handle search button click or Enter key press."""
        query = self._search_entry.get().strip()
        if not query:
            # Show error or just return
            print("Please enter a search query")
            return
        
        # Clear previous results
        self._search_results = []
        self._current_document = None
        self._update_results_display([])
        self._update_document_preview(None)
        
        # Execute search via ViewModel
        self._viewmodel.set_property('search_query', query)
        # In a real implementation, this would trigger async search
        # For now, we'll just execute the command
        self._viewmodel.execute_command('search_knowledge', query)
    
    def _on_result_selected(self, result: Dict[str, Any]):
        """Handle when a search result is selected."""
        # Set as current document in ViewModel
        self._viewmodel.set_property('current_document', result)
        
        # Update preview display
        self._update_document_preview(result)
        
        # Update current selected document
        self._current_document = result
    
    def _add_document(self):
        """Handle add document button click.""" 
        # Execute add document command via ViewModel
        self._viewmodel.execute_command('add_document_dialog')
    
    def _sync_knowledge(self):
        """Handle sync button click."""
        # Execute sync knowledge command via ViewModel
        self._viewmodel.set_property('is_loading_knowledge', True)
        self._viewmodel.execute_command('sync_knowledge_base')
    
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
        """Refresh the knowledge view display."""
        self._update_knowledge_statistics()
        self._update_results_display(self._search_results)
        
        if self._current_document:
            self._update_document_preview(self._current_document)
    
    def get_search_query(self) -> str:
        """
        Get the current search query.
        
        Returns:
            Current search query string
        """
        if self._search_entry:
            return self._search_entry.get()
        return ""
    
    def get_search_results_count(self) -> int:
        """
        Get the number of search results.
        
        Returns:
            Number of search results
        """
        return len(self._search_results)
    
    def get_current_document(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently selected document.
        
        Returns:
            Currently selected document dictionary, or None
        """
        return self._current_document
    
    def search_knowledge(self, query: str):
        """
        Perform a knowledge search.
        
        Args:
            query: Search query string
        """
        if self._search_entry:
            self._search_entry.delete(0, "end")
            self._search_entry.insert(0, query)
        
        self._perform_search()
    
    def clear_search_results(self):
        """Clear the current search results."""
        self._search_results = []
        self._current_document = None
        self._update_results_display([])
        self._update_document_preview(None)
    
    def focus_search_input(self):
        """Focus the search input field."""
        if self._search_entry:
            self._search_entry.focus()
    
    def update_knowledge_base(self):
        """Manually update the knowledge base."""
        self._sync_knowledge()
    
    def export_search_results(self) -> List[Dict[str, Any]]:
        """
        Export current search results.
        
        Returns:
            List of current search result dictionaries
        """
        return self._search_results.copy()
    
    def get_knowledge_status_info(self) -> Dict[str, Any]:
        """
        Get knowledge base status information.
        
        Returns:
            Dictionary with knowledge base status information
        """
        return self._viewmodel.get_property('knowledge_base_status', {})