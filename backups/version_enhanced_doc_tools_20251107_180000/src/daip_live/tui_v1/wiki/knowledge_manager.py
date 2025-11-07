"""
Knowledge Manager for Wiki Knowledge Base

High-level management of knowledge base operations including ingestion,
search, synchronization, and persistence.
"""

from typing import List, Dict, Any, Optional, Union
import json
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
import asyncio
import zipfile

from .document import Document, DocumentStatus
from .vector_store import VectorStore, SearchResult
from .ingestion import DocumentIngestor
from .search import SearchEngine

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """High-level knowledge base manager"""

    def __init__(
        self,
        data_dir: str,
        embedding_dimension: int = 768,
        index_type: str = "faiss",
        auto_save: bool = True,
        max_vector_size: int = 10000
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dimension = embedding_dimension
        self.auto_save = auto_save
        self.max_vector_size = max_vector_size

        # Initialize components
        self.vector_store = VectorStore(
            dimension=embedding_dimension,
            index_type=index_type,
            persist_path=str(self.data_dir / "vector_store"),
            max_size=max_vector_size
        )
        self.ingestor = DocumentIngestor()
        self.search_engine = SearchEngine(self.vector_store)

        # Statistics and metadata
        self.stats_file = self.data_dir / "stats.json"
        self.config_file = self.data_dir / "config.json"
        self.created_at = datetime.now()
        self.updated_at = self.created_at

        # Load existing data if available
        self.load()

        logger.info(f"Initialized KnowledgeManager at {self.data_dir}")

    def add_document(self, document: Document) -> Optional[str]:
        """Add a document to the knowledge base"""
        try:
            # Generate embedding if document doesn't have one
            if not document.embedding:
                embedding = self.ingestor._generate_embedding(document.content)
                if embedding:
                    document.set_embedding(embedding)
                    document.update_status(DocumentStatus.PROCESSED)
                else:
                    document.update_status(DocumentStatus.FAILED, "Failed to generate embedding")
                    logger.error(f"Failed to generate embedding for document {document.id}")
                    return None

            # Add to vector store
            if self.vector_store.add_document(document):
                if self.auto_save:
                    self.save()
                logger.info(f"Added document {document.id} to knowledge base")
                return document.id
            else:
                logger.error(f"Failed to add document {document.id} to vector store")
                return None

        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return None

    def add_documents_batch(self, documents: List[Document]) -> List[str]:
        """Add multiple documents in batch"""
        added_ids = []
        for document in documents:
            doc_id = self.add_document(document)
            if doc_id:
                added_ids.append(doc_id)

        logger.info(f"Added {len(added_ids)}/{len(documents)} documents in batch")
        return added_ids

    def ingest_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Ingest and add a file to the knowledge base"""
        try:
            document = self.ingestor.ingest_file(file_path, metadata)
            if document:
                return self.add_document(document)
            else:
                logger.error(f"Failed to ingest file: {file_path}")
                return None

        except Exception as e:
            logger.error(f"Error ingesting file {file_path}: {e}")
            return None

    def ingest_files_batch(
        self,
        file_paths: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Ingest multiple files in batch"""
        documents = self.ingestor.ingest_files_batch(file_paths, metadata)
        return self.add_documents_batch(documents)

    def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """Ingest all files from a directory"""
        documents = self.ingestor.ingest_directory(
            directory_path, recursive, metadata, include_patterns, exclude_patterns
        )
        return self.add_documents_batch(documents)

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        search_type: str = "hybrid",
        include_chunks: bool = False
    ) -> List[SearchResult]:
        """Search the knowledge base"""
        try:
            if search_type == "semantic":
                return self.search_engine.search(query, top_k, filters, include_chunks)
            elif search_type == "text":
                return self.search_engine.text_search(query, top_k, filters)
            elif search_type == "hybrid":
                return self.search_engine.hybrid_search(query, top_k, filters, include_chunks=include_chunks)
            else:
                logger.warning(f"Unknown search type: {search_type}, using hybrid")
                return self.search_engine.hybrid_search(query, top_k, filters, include_chunks=include_chunks)

        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.vector_store.get_document(document_id)

    def get_all_documents(self) -> List[Document]:
        """Get all documents in the knowledge base"""
        return self.vector_store.get_all_documents()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the knowledge base"""
        try:
            success = self.vector_store.delete_document(document_id)
            if success and self.auto_save:
                self.save()
            return success

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False

    def update_document(self, document_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document"""
        try:
            document = self.get_document(document_id)
            if not document:
                logger.warning(f"Document {document_id} not found")
                return False

            # Apply updates
            if "title" in updates:
                document.title = updates["title"]
            if "content" in updates:
                document.content = updates["content"]
                # Regenerate embedding
                embedding = self.ingestor._generate_embedding(document.content)
                if embedding:
                    document.set_embedding(embedding)
                    document.update_status(DocumentStatus.PROCESSED)
            if "metadata" in updates:
                document.metadata.update(updates["metadata"])
            if "tags" in updates:
                document.tags = updates["tags"]
                document.metadata["tags"] = updates["tags"]

            # Update the document in vector store
            self.vector_store.delete_document(document_id)
            self.vector_store.add_document(document)

            if self.auto_save:
                self.save()

            logger.info(f"Updated document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics"""
        try:
            # Vector store statistics
            vector_stats = self.vector_store.get_statistics()

            # Document statistics
            all_documents = self.vector_store.get_all_documents()
            doc_stats = {
                "total_word_count": sum(doc.get_word_count() for doc in all_documents),
                "total_character_count": sum(doc.get_character_count() for doc in all_documents),
                "average_document_size": sum(doc.get_character_count() for doc in all_documents) / len(all_documents) if all_documents else 0
            }

            # Status distribution
            status_counts = {}
            for doc in all_documents:
                status = doc.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            # Search analytics
            search_analytics = self.search_engine.get_search_analytics()

            return {
                "knowledge_base_id": str(self.data_dir),
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "vector_store": vector_stats,
                "documents": doc_stats,
                "status_distribution": status_counts,
                "search_analytics": search_analytics,
                "configuration": {
                    "embedding_dimension": self.embedding_dimension,
                    "auto_save": self.auto_save,
                    "max_vector_size": self.max_vector_size
                }
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}

    def get_categories(self) -> Dict[str, int]:
        """Get document categories and their counts"""
        categories = {}
        for document in self.vector_store.get_all_documents():
            category = document.metadata.get("category", "Uncategorized")
            categories[category] = categories.get(category, 0) + 1
        return categories

    def get_recent_documents(self, limit: int = 10) -> List[Document]:
        """Get recently added documents"""
        all_documents = self.vector_store.get_all_documents()
        sorted_docs = sorted(all_documents, key=lambda x: x.created_at, reverse=True)
        return sorted_docs[:limit]

    def export_knowledge_base(self, export_path: str) -> bool:
        """Export knowledge base to file"""
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            # Export data
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "knowledge_base_id": str(self.data_dir),
                    "version": "1.0"
                },
                "documents": [doc.to_dict() for doc in self.vector_store.get_all_documents()],
                "statistics": self.get_statistics()
            }

            if export_path.suffix.lower() == '.zip':
                # Create zip export
                with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Add documents as JSON
                    json_data = json.dumps(export_data, indent=2)
                    zipf.writestr("knowledge_base.json", json_data)

                    # Add vector store data if available
                    if self.vector_store.persist_path:
                        for file_path in self.vector_store.persist_path.rglob("*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(self.vector_store.persist_path)
                                zipf.write(file_path, f"vector_store/{arcname}")

            else:
                # JSON export
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported knowledge base to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting knowledge base: {e}")
            return False

    def import_knowledge_base(self, import_path: str) -> bool:
        """Import knowledge base from file"""
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                logger.error(f"Import file not found: {import_path}")
                return False

            if import_path.suffix.lower() == '.zip':
                # Import from zip
                with zipfile.ZipFile(import_path, 'r') as zipf:
                    # Extract documents
                    if "knowledge_base.json" in zipf.namelist():
                        with zipf.open("knowledge_base.json") as f:
                            import_data = json.load(f)
                    else:
                        logger.error("No knowledge_base.json found in zip file")
                        return False

                    # Extract vector store data
                    vector_store_dir = self.data_dir / "vector_store"
                    vector_store_dir.mkdir(exist_ok=True)

                    for file_info in zipf.infolist():
                        if file_info.filename.startswith("vector_store/"):
                            relative_path = file_info.filename[len("vector_store/"):]
                            if relative_path:
                                target_path = vector_store_dir / relative_path
                                target_path.parent.mkdir(parents=True, exist_ok=True)
                                with zipf.open(file_info) as source, open(target_path, "wb") as target:
                                    shutil.copyfileobj(source, target)

            else:
                # Import from JSON
                with open(import_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)

            # Import documents
            documents_data = import_data.get("documents", [])
            imported_count = 0

            for doc_data in documents_data:
                try:
                    document = Document.from_dict(doc_data)
                    if self.vector_store.add_document(document):
                        imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing document: {e}")

            logger.info(f"Imported {imported_count} documents from {import_path}")
            self.updated_at = datetime.now()

            if self.auto_save:
                self.save()

            return True

        except Exception as e:
            logger.error(f"Error importing knowledge base: {e}")
            return False

    def sync_knowledge_base(self, sync_source: Optional[str] = None) -> Dict[str, Any]:
        """Synchronize knowledge base with external source"""
        # This is a placeholder for sync functionality
        # In a real implementation, this would sync with cloud storage, etc.
        try:
            sync_result = {
                "added": 0,
                "updated": 0,
                "deleted": 0,
                "errors": [],
                "sync_time": datetime.now().isoformat()
            }

            # Mock sync implementation
            logger.info("Performing knowledge base synchronization")
            self.updated_at = datetime.now()

            if self.auto_save:
                self.save()

            return sync_result

        except Exception as e:
            logger.error(f"Error during sync: {e}")
            return {
                "added": 0,
                "updated": 0,
                "deleted": 0,
                "errors": [str(e)],
                "sync_time": datetime.now().isoformat()
            }

    def save(self) -> bool:
        """Save knowledge base to disk"""
        try:
            # Save vector store
            vector_store_success = self.vector_store.save()

            # Save statistics
            stats = self.get_statistics()
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)

            # Save configuration
            config = {
                "embedding_dimension": self.embedding_dimension,
                "auto_save": self.auto_save,
                "max_vector_size": self.max_vector_size,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info("Saved knowledge base")
            return vector_store_success

        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            return False

    def load(self) -> bool:
        """Load knowledge base from disk"""
        try:
            # Load vector store
            vector_store_success = self.vector_store.load()

            # Load configuration
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.embedding_dimension = config.get("embedding_dimension", 768)
                    self.auto_save = config.get("auto_save", True)
                    self.max_vector_size = config.get("max_vector_size", 10000)
                    self.created_at = datetime.fromisoformat(config.get("created_at", datetime.now().isoformat()))
                    self.updated_at = datetime.fromisoformat(config.get("updated_at", datetime.now().isoformat()))

            logger.info("Loaded knowledge base")
            return vector_store_success

        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return False

    def clear(self) -> None:
        """Clear all documents from knowledge base"""
        self.vector_store.clear()
        self.updated_at = datetime.now()
        if self.auto_save:
            self.save()
        logger.info("Cleared knowledge base")

    def __len__(self) -> int:
        """Get number of documents"""
        return len(self.vector_store)

    def __str__(self) -> str:
        """String representation"""
        return f"KnowledgeManager({len(self.vector_store)} docs, {self.data_dir})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"KnowledgeManager(documents={len(self.vector_store)}, "
                f"data_dir='{self.data_dir}', dimension={self.embedding_dimension})")