"""
Wiki Knowledge Base System for newP6 TUI

This module provides comprehensive knowledge management capabilities including:
- Document ingestion and processing
- Vector storage and similarity search
- Semantic and hybrid search capabilities
- Knowledge base management and synchronization
"""

from .document import Document, DocumentStatus, DocumentType
from .vector_store import VectorStore, SearchResult
from .ingestion import DocumentIngestor
from .search import SearchEngine
from .knowledge_manager import KnowledgeManager
from .knowledge_base import KnowledgeBase

__all__ = [
    "Document",
    "DocumentStatus",
    "DocumentType",
    "VectorStore",
    "SearchResult",
    "DocumentIngestor",
    "SearchEngine",
    "KnowledgeManager",
    "KnowledgeBase"
]