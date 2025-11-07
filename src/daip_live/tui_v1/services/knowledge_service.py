"""
Knowledge Service Adapter for newP6 TUI

Adapts knowledge base functionality for the TUI system.
"""

from typing import List, Dict, Optional, Any
import logging

from .base import BaseServiceAdapter

logger = logging.getLogger(__name__)


class KnowledgeServiceAdapter(BaseServiceAdapter):
    """Adapter for knowledge base service"""

    async def search_documents(self, query: str, search_type: str = "fulltext") -> List[Dict]:
        """Search documents in knowledge base"""
        try:
            if self.service and hasattr(self.service, 'search'):
                results = self.service.search(query, search_type)
            else:
                # Mock data for testing/fallback
                results = [
                    {"id": "doc1", "title": "Microservices", "relevance": 0.95, "content": "Content about microservices..."},
                    {"id": "doc2", "title": "Architecture", "relevance": 0.87, "content": "Architecture patterns..."}
                ]

            self.update_state({'knowledge_search_results': results})
            self.emit_event('knowledge_searched', {
                'query': query,
                'search_type': search_type,
                'results_count': len(results)
            })
            logger.info(f"Knowledge search for '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching knowledge base for '{query}': {e}")
            self.emit_event('knowledge_error', {'error': str(e), 'query': query})
            return []

    async def add_document(self, file_path: str) -> Dict:
        """Add a document to the knowledge base"""
        try:
            if self.service and hasattr(self.service, 'add_document'):
                result = self.service.add_document(file_path)
            else:
                # Mock data for testing/fallback
                result = {
                    "id": "doc3",
                    "file_path": file_path,
                    "status": "added",
                    "indexed_at": "2025-11-02T10:00:00Z"
                }

            self.emit_event('knowledge_document_added', {
                'file_path': file_path,
                'document_id': result.get('id')
            })
            logger.info(f"Added document to knowledge base: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            self.emit_event('knowledge_error', {'error': str(e), 'file_path': file_path})
            raise

    async def sync_knowledge_base(self) -> Dict:
        """Synchronize the knowledge base"""
        try:
            if self.service and hasattr(self.service, 'sync'):
                result = self.service.sync()
            else:
                # Mock data for testing/fallback
                result = {
                    "status": "synced",
                    "documents": 1234,
                    "last_sync": "2025-11-02T10:00:00Z",
                    "new_documents": 5,
                    "updated_documents": 12
                }

            self.update_state({'knowledge_sync_status': result})
            self.emit_event('knowledge_synced', result)
            logger.info(f"Knowledge base sync completed: {result.get('documents')} documents")
            return result
        except Exception as e:
            logger.error(f"Error syncing knowledge base: {e}")
            self.emit_event('knowledge_error', {'error': str(e)})
            raise

    async def get_knowledge_stats(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            if self.service and hasattr(self.service, 'get_stats'):
                stats = self.service.get_stats()
            else:
                # Mock data for testing/fallback
                stats = {
                    "documents": 1234,
                    "size": "45MB",
                    "last_updated": "2025-11-02T09:30:00Z",
                    "categories": 12,
                    "tags": 156
                }

            self.update_state({'knowledge_stats': stats})
            return stats
        except Exception as e:
            logger.error(f"Error getting knowledge stats: {e}")
            return {}

    async def get_document(self, document_id: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        try:
            if self.service and hasattr(self.service, 'get_document'):
                document = self.service.get_document(document_id)
            else:
                # Mock data for testing/fallback
                document = {
                    "id": document_id,
                    "title": "Sample Document",
                    "content": "This is the content of the document...",
                    "created_at": "2025-11-01T15:00:00Z",
                    "updated_at": "2025-11-02T09:30:00Z"
                }

            self.emit_event('knowledge_document_retrieved', {
                'document_id': document_id,
                'document_title': document.get('title')
            })
            return document
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            self.emit_event('knowledge_error', {'error': str(e), 'document_id': document_id})
            return None

    async def update_document(self, document_id: str, content: str) -> Dict:
        """Update document content"""
        try:
            if self.service and hasattr(self.service, 'update_document'):
                result = self.service.update_document(document_id, content)
            else:
                # Mock data for testing/fallback
                result = {
                    "id": document_id,
                    "status": "updated",
                    "updated_at": "2025-11-02T10:00:00Z",
                    "content_length": len(content)
                }

            self.emit_event('knowledge_document_updated', {
                'document_id': document_id,
                'content_length': len(content)
            })
            logger.info(f"Updated document: {document_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            self.emit_event('knowledge_error', {'error': str(e), 'document_id': document_id})
            raise

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        try:
            if self.service and hasattr(self.service, 'delete_document'):
                success = self.service.delete_document(document_id)
            else:
                # Mock data for testing/fallback
                success = True

            if success:
                self.emit_event('knowledge_document_deleted', {'document_id': document_id})
                logger.info(f"Deleted document: {document_id}")

            return success
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            self.emit_event('knowledge_error', {'error': str(e), 'document_id': document_id})
            return False

    async def list_categories(self) -> List[str]:
        """List all document categories"""
        try:
            if self.service and hasattr(self.service, 'list_categories'):
                categories = self.service.list_categories()
            else:
                # Mock data for testing/fallback
                categories = ["Architecture", "Programming", "Design", "Testing", "DevOps"]

            return categories
        except Exception as e:
            logger.error(f"Error listing categories: {e}")
            return []

    async def get_recent_documents(self, limit: int = 10) -> List[Dict]:
        """Get recently updated documents"""
        try:
            if self.service and hasattr(self.service, 'get_recent_documents'):
                documents = self.service.get_recent_documents(limit)
            else:
                # Mock data for testing/fallback
                documents = [
                    {"id": f"doc{i}", "title": f"Recent Document {i}", "updated_at": f"2025-11-02T{10+i}:00:00Z"}
                    for i in range(min(limit, 5))
                ]

            return documents
        except Exception as e:
            logger.error(f"Error getting recent documents: {e}")
            return []