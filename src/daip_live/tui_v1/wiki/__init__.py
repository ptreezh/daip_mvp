"""
Wiki Knowledge Base System for newP6 TUI

This module provides comprehensive knowledge management capabilities including:
- Document ingestion and processing
- Vector storage and similarity search
- Semantic and hybrid search capabilities
- Knowledge base management and synchronization
"""

from .document import Document, DocumentStatus, DocumentType
from .ingestion import DocumentIngestor
from .knowledge_base import KnowledgeBase
from .knowledge_manager import KnowledgeManager
from .search import SearchEngine
from .vector_store import SearchResult, VectorStore

__all__ = [
    "Document",
    "DocumentStatus",
    "DocumentType",
    "VectorStore",
    "SearchResult",
    "DocumentIngestor",
    "SearchEngine",
    "KnowledgeManager",
    "KnowledgeBase",
]
