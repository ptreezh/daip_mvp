"""
Knowledge Base ViewModel

This module implements the ViewModel for knowledge base functionality in the P7 GUI application.
It manages document search, retrieval, addition, and knowledge base status tracking.
"""

from typing import Any, Dict, List, Optional
from .base import ViewModel
from ..models.interaction_layer import InteractionLayer


class KnowledgeViewModel(ViewModel):
    """
    ViewModel for knowledge base functionality.
    
    This ViewModel manages:
    - Document search and retrieval
    - Knowledge base status tracking
    - Document management operations
    - Search result filtering and sorting
    - Recent search history
    """
    
    def __init__(self, interaction_layer: InteractionLayer):
        """
        Initialize the KnowledgeViewModel.
        
        Args:
            interaction_layer: Layer for communicating with backend services
        """
        super().__init__()
        
        self._interaction_layer = interaction_layer
        
        # Initialize properties with default values
        self.set_property('available_documents', [])  # List of document dictionaries
        self.set_property('search_results', [])  # List of search result documents
        self.set_property('search_query', '')  # Current search query
        self.set_property('current_document', None)  # Currently viewed document
        self.set_property('knowledge_base_status', None)  # Current status of knowledge base
        self.set_property('is_loading_documents', False)  # Whether documents are loading
        self.set_property('is_searching', False)  # Whether search is in progress
        self.set_property('total_documents', 0)  # Total number of documents
        self.set_property('last_sync_date', None)  # Date of last synchronization
        self.set_property('search_filters', {})  # Filters for search results
        self.set_property('document_categories', [])  # Available document categories
        self.set_property('recent_searches', [])  # Recent search queries
        self.set_property('max_recent_searches', 10)  # Max number of recent searches to keep
        
        # Internal data
        self._recent_searches: List[str] = []
        
        # Register knowledge-specific commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all commands that this ViewModel supports."""
        # Search commands
        self.register_command('search_knowledge', self._search_knowledge_command)
        self.register_command('clear_search_results', self._clear_search_results_command)
        self.register_command('get_knowledge_status', self._get_knowledge_status_command)
        self.register_command('load_documents', self._load_documents_command)
        self.register_command('refresh_knowledge_base', self._refresh_knowledge_base_command)
        
        # Document management commands
        self.register_command('add_document', self._add_document_command)
        self.register_command('remove_document', self._remove_document_command)
        self.register_command('update_document', self._update_document_command)
        self.register_command('download_document', self._download_document_command)
        
        # Category management commands
        self.register_command('get_categories', self._get_categories_command)
        self.register_command('filter_by_category', self._filter_by_category_command)
        
        # Bookmark/History commands
        self.register_command('bookmark_document', self._bookmark_document_command)
        self.register_command('get_bookmarks', self._get_bookmarks_command)
        self.register_command('recent_searches', self._recent_searches_command)
    
    def _search_knowledge_command(self, query: str) -> str:
        """
        Command to initiate knowledge search.
        
        Args:
            query: Search query string
            
        Returns:
            Status message
        """
        self.set_property('search_query', query)
        self.set_property('is_searching', True)
        return f"Searching knowledge base for: {query}"
    
    def _clear_search_results_command(self) -> str:
        """
        Command to clear search results.
        
        Returns:
            Status message
        """
        self.set_property('search_results', [])
        self.set_property('search_query', '')
        return "Cleared search results"
    
    def _get_knowledge_status_command(self) -> str:
        """
        Command to get knowledge base status.
        
        Returns:
            Status message
        """
        return "Getting knowledge base status"
    
    def _load_documents_command(self) -> str:
        """
        Command to load documents from knowledge base.
        
        Returns:
            Status message
        """
        self.set_property('is_loading_documents', True)
        return "Loading documents"
    
    def _refresh_knowledge_base_command(self) -> str:
        """
        Command to refresh the knowledge base.
        
        Returns:
            Status message
        """
        self.set_property('is_loading_documents', True)
        return "Refreshing knowledge base"
    
    def _add_document_command(self, doc_info: Dict[str, Any]) -> str:
        """
        Command to add a document to the knowledge base.
        
        Args:
            doc_info: Document information dictionary
            
        Returns:
            Status message
        """
        # In a real implementation, this would call backend to add document
        # For now, just return a status message
        title = doc_info.get('title', 'Untitled Document')
        return f"Adding document: {title}"
    
    def _remove_document_command(self, doc_id: str) -> str:
        """
        Command to remove a document from the knowledge base.
        
        Args:
            doc_id: ID of the document to remove
            
        Returns:
            Status message
        """
        # In a real implementation, this would call backend to remove document
        available_docs = self.get_property('available_documents', [])
        updated_docs = [doc for doc in available_docs if doc.get('id') != doc_id]
        self.set_property('available_documents', updated_docs)
        
        # Also update search results if needed
        search_results = self.get_property('search_results', [])
        updated_results = [doc for doc in search_results if doc.get('id') != doc_id]
        self.set_property('search_results', updated_results)
        
        return f"Removed document: {doc_id}"
    
    def _update_document_command(self, doc_id: str, updates: Dict[str, Any]) -> str:
        """
        Command to update a document in the knowledge base.
        
        Args:
            doc_id: ID of the document to update
            updates: Dictionary of field-value pairs to update
            
        Returns:
            Status message
        """
        # In a real implementation, this would call backend to update document
        # For now, just return a status message
        return f"Updating document: {doc_id}"
    
    def _download_document_command(self, doc_id: str) -> str:
        """
        Command to download a document.
        
        Args:
            doc_id: ID of the document to download
            
        Returns:
            Status message
        """
        return f"Downloading document: {doc_id}"
    
    def _get_categories_command(self) -> str:
        """
        Command to get document categories.
        
        Returns:
            Status message
        """
        return "Retrieving document categories"
    
    def _filter_by_category_command(self, category: str) -> str:
        """
        Command to filter documents by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Status message
        """
        filters = self.get_property('search_filters', {})
        filters['category'] = category
        self.set_property('search_filters', filters)
        return f"Filtered by category: {category}"
    
    def _bookmark_document_command(self, doc_id: str) -> str:
        """
        Command to bookmark a document.
        
        Args:
            doc_id: ID of the document to bookmark
            
        Returns:
            Status message
        """
        # In a real implementation, this would store bookmarks
        return f"Bookmarked document: {doc_id}"
    
    def _get_bookmarks_command(self) -> str:
        """
        Command to get bookmarks.
        
        Returns:
            Status message
        """
        return "Retrieving bookmarks"
    
    def _recent_searches_command(self) -> str:
        """
        Command to get recent searches.
        
        Returns:
            Status message
        """
        return f"Retrieved {len(self.get_property('recent_searches', []))} recent searches"
    
    # Public async methods for interacting with backend
    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Search the knowledge base for documents matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching document dictionaries with scores
        """
        try:
            self.set_property('is_searching', True)
            self.set_property('search_query', query)
            
            # Add to recent searches
            self._add_recent_search(query)
            
            # Perform search via interaction layer
            results = await self._interaction_layer.search_knowledge(query)
            
            # Update search results
            self.set_property('search_results', results)
            
            return results
        finally:
            self.set_property('is_searching', False)
    
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """
        Get the current status of the knowledge base.
        
        Returns:
            Knowledge base status dictionary
        """
        try:
            self.set_property('is_loading_documents', True)
            
            # Get status via interaction layer
            status = await self._interaction_layer.get_knowledge_status()
            
            # Update local properties
            self.set_property('knowledge_base_status', status)
            self.set_property('total_documents', status.get('total_documents', 0))
            self.set_property('last_sync_date', status.get('last_sync', None))
            
            return status
        finally:
            self.set_property('is_loading_documents', False)
    
    async def load_documents(self) -> List[Dict[str, Any]]:
        """
        Load all available documents from the knowledge base.
        
        Returns:
            List of document dictionaries
        """
        try:
            self.set_property('is_loading_documents', True)
            
            # In a real implementation, this would call backend to load documents
            # For now, we'll just return the available documents
            documents = self.get_property('available_documents', [])
            
            # Update total count
            self.set_property('total_documents', len(documents))
            
            return documents
        finally:
            self.set_property('is_loading_documents', False)
    
    async def refresh_knowledge_base(self) -> Dict[str, Any]:
        """
        Refresh the knowledge base by reloading status and available documents.
        
        Returns:
            Updated status information
        """
        status = await self.get_knowledge_status()
        documents = await self.load_documents()
        
        return {
            'status': status,
            'documents_loaded': len(documents),
            'refreshed_at': self._get_current_timestamp()
        }
    
    def add_document(self, document_info: Dict[str, Any]) -> str:
        """
        Add a document to the knowledge base (locally).
        
        Args:
            document_info: Dictionary containing document information
                           Expected keys: id, title, content, category, tags, etc.
            
        Returns:
            Confirmation message
        """
        available_docs = self.get_property('available_documents', [])
        
        # Check if document already exists
        doc_id = document_info.get('id')
        if doc_id and any(doc.get('id') == doc_id for doc in available_docs):
            return f"Document with ID {doc_id} already exists"
        
        # Add the document
        available_docs.append(document_info)
        self.set_property('available_documents', available_docs)
        self.set_property('total_documents', len(available_docs))
        
        return f"Added document: {document_info.get('title', 'Untitled')}"
    
    def remove_document(self, document_id: str) -> str:
        """
        Remove a document from the knowledge base (locally).
        
        Args:
            document_id: ID of the document to remove
            
        Returns:
            Confirmation message
        """
        available_docs = self.get_property('available_documents', [])
        
        # Remove from available documents
        updated_docs = [doc for doc in available_docs if doc.get('id') != document_id]
        self.set_property('available_documents', updated_docs)
        
        # Remove from search results if present
        search_results = self.get_property('search_results', [])
        updated_results = [doc for doc in search_results if doc.get('id') != document_id]
        self.set_property('search_results', updated_results)
        
        # Clear current document if it was removed
        current_doc = self.get_property('current_document')
        if current_doc and current_doc.get('id') == document_id:
            self.set_property('current_document', None)
        
        self.set_property('total_documents', len(updated_docs))
        
        return f"Removed document: {document_id}"
    
    def update_document(self, document_id: str, updates: Dict[str, Any]) -> str:
        """
        Update a document in the knowledge base (locally).
        
        Args:
            document_id: ID of the document to update
            updates: Dictionary of field-value pairs to update
            
        Returns:
            Confirmation message
        """
        available_docs = self.get_property('available_documents', [])
        
        for doc in available_docs:
            if doc.get('id') == document_id:
                doc.update(updates)
                break
        else:
            return f"Document with ID {document_id} not found"
        
        # Update search results if document is there
        search_results = self.get_property('search_results', [])
        for doc in search_results:
            if doc.get('id') == document_id:
                doc.update(updates)
                break
        
        # Update current document if it's the one being updated
        current_doc = self.get_property('current_document')
        if current_doc and current_doc.get('id') == document_id:
            current_doc.update(updates)
            self.set_property('current_document', current_doc)
        
        return f"Updated document: {document_id}"
    
    def select_document(self, document_id: str) -> str:
        """
        Select a document as the current document.
        
        Args:
            document_id: ID of the document to select
            
        Returns:
            Confirmation message
        """
        available_docs = self.get_property('available_documents', [])
        
        selected_doc = next((doc for doc in available_docs if doc.get('id') == document_id), None)
        if not selected_doc:
            # Also try search results
            search_results = self.get_property('search_results', [])
            selected_doc = next((doc for doc in search_results if doc.get('id') == document_id), None)
        
        if not selected_doc:
            return f"Document with ID {document_id} not found"
        
        self.set_property('current_document', selected_doc)
        return f"Selected document: {selected_doc.get('title', 'Untitled')}"
    
    def _filter_results_by_tags(self, results: List[Dict[str, Any]], tags: List[str]) -> List[Dict[str, Any]]:
        """
        Filter search results by tags.
        
        Args:
            results: List of document dictionaries
            tags: List of tags to filter by
            
        Returns:
            Filtered list of documents
        """
        if not tags:
            return results
        
        filtered_results = []
        for doc in results:
            doc_tags = doc.get('tags', [])
            if any(tag in doc_tags for tag in tags):
                filtered_results.append(doc)
        
        return filtered_results
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as an ISO string.
        
        Returns:
            Current timestamp in ISO format
        """
        return "2025-11-08T00:00:00Z"  # Placeholder
    
    def _add_recent_search(self, query: str):
        """
        Add a search query to the recent searches list.
        
        Args:
            query: Search query to add
        """
        recent_searches = self.get_property('recent_searches', [])
        
        # Remove if already exists
        recent_searches = [s for s in recent_searches if s.lower() != query.lower()]
        
        # Add to the beginning
        recent_searches.insert(0, query)
        
        # Limit to max_recent_searches
        max_recent = self.get_property('max_recent_searches', 10)
        recent_searches = recent_searches[:max_recent]
        
        self.set_property('recent_searches', recent_searches)
    
    # Property access methods
    def get_available_documents(self) -> List[Dict[str, Any]]:
        """Get the list of available documents."""
        return self.get_property('available_documents', [])
    
    def get_search_results(self) -> List[Dict[str, Any]]:
        """Get the current search results."""
        return self.get_property('search_results', [])
    
    def get_search_query(self) -> str:
        """Get the current search query."""
        return self.get_property('search_query', '')
    
    def get_current_document(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected document."""
        return self.get_property('current_document')
    
    def get_knowledge_base_status(self) -> Optional[Dict[str, Any]]:
        """Get the current status of the knowledge base."""
        return self.get_property('knowledge_base_status')
    
    def is_loading_documents(self) -> bool:
        """Check if documents are currently loading."""
        return self.get_property('is_loading_documents', False)
    
    def is_searching(self) -> bool:
        """Check if a search is currently in progress."""
        return self.get_property('is_searching', False)
    
    def get_total_documents(self) -> int:
        """Get the total number of documents."""
        return self.get_property('total_documents', 0)
    
    def get_last_sync_date(self) -> Optional[str]:
        """Get the date of the last synchronization."""
        return self.get_property('last_sync_date')
    
    def get_recent_searches(self) -> List[str]:
        """Get the list of recent searches."""
        return self.get_property('recent_searches', [])
    
    def get_document_categories(self) -> List[str]:
        """Get the list of available document categories."""
        return self.get_property('document_categories', [])
    
    def clear_search_history(self):
        """Clear the search query and results."""
        self.set_property('search_query', '')
        self.set_property('search_results', [])
    
    def clear_current_document(self):
        """Clear the currently selected document."""
        self.set_property('current_document', None)
    
    def clear_recent_searches(self):
        """Clear the recent searches list."""
        self.set_property('recent_searches', [])