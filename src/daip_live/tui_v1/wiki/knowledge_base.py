"""
Knowledge Base for Wiki Knowledge Base System

High-level knowledge base abstraction with advanced features like
categorization, backup/restore, and analytics.
"""

import json
import logging
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .document import Document
from .knowledge_manager import KnowledgeManager
from .vector_store import SearchResult

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Advanced knowledge base with categorization and analytics"""

    def __init__(
        self,
        name: str,
        storage_path: str,
        description: str = "",
        embedding_dimension: int = 768,
        auto_categorize: bool = True,
        enable_analytics: bool = True,
    ):
        self.name = name
        self.description = description
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.auto_categorize = auto_categorize
        self.enable_analytics = enable_analytics

        # Initialize knowledge manager
        self.manager = KnowledgeManager(
            data_dir=str(self.storage_path / "data"),
            embedding_dimension=embedding_dimension,
        )

        # Categories and tags
        self.categories_file = self.storage_path / "categories.json"
        self.tags_file = self.storage_path / "tags.json"
        self.analytics_file = self.storage_path / "analytics.json"

        # Load or initialize categories and tags
        self.categories: dict[str, dict[str, Any]] = self._load_categories()
        self.tags: dict[str, dict[str, Any]] = self._load_tags()

        # Analytics data
        self.analytics: dict[str, Any] = self._load_analytics()

        # Backup settings
        self.backup_dir = self.storage_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.created_at = datetime.now()
        self.updated_at = self.created_at

        logger.info(f"Initialized KnowledgeBase '{name}' at {self.storage_path}")

    def add_document(self, document: Document) -> Optional[str]:
        """Add a document to the knowledge base"""
        try:
            # Auto-categorize if enabled
            if self.auto_categorize:
                self._auto_categorize_document(document)

            # Add to manager
            doc_id = self.manager.add_document(document)

            if doc_id:
                # Update categories and tags
                self._update_document_metadata(document)

                # Update analytics
                if self.enable_analytics:
                    self._record_document_addition(document)

                self.updated_at = datetime.now()
                logger.info(
                    f"Added document '{document.title}' to knowledge base '{self.name}'"
                )

            return doc_id

        except Exception as e:
            logger.error(f"Error adding document to knowledge base: {e}")
            return None

    def add_documents_batch(self, documents: list[Document]) -> list[str]:
        """Add multiple documents in batch"""
        added_ids = []
        for document in documents:
            doc_id = self.add_document(document)
            if doc_id:
                added_ids.append(doc_id)

        logger.info(
            f"Added {len(added_ids)}/{len(documents)} documents to knowledge base '{self.name}'"  # noqa: E501
        )
        return added_ids

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        categories: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        search_type: str = "hybrid",
    ) -> list[SearchResult]:
        """Search the knowledge base with advanced filtering"""
        try:
            # Build filters
            search_filters = filters or {}

            if categories:
                search_filters["categories"] = categories

            if tags:
                search_filters["tags"] = tags

            # Perform search
            results = self.manager.search(query, top_k, search_filters, search_type)

            # Update analytics
            if self.enable_analytics:
                self._record_search(query, len(results), search_filters, search_type)

            return results

        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.manager.get_document(document_id)

    def get_all_documents(self) -> list[Document]:
        """Get all documents in the knowledge base"""
        return self.manager.get_all_documents()

    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the knowledge base"""
        try:
            success = self.manager.delete_document(document_id)
            if success and self.enable_analytics:
                self._record_document_deletion(document_id)
            return success

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

    def update_document(self, document_id: str, updates: dict[str, Any]) -> bool:
        """Update a document"""
        try:
            success = self.manager.update_document(document_id, updates)

            if success:
                # Update categories and tags if changed
                document = self.get_document(document_id)
                if document:
                    self._update_document_metadata(document)

                if self.enable_analytics:
                    self._record_document_update(document_id)

                self.updated_at = datetime.now()

            return success

        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False

    def get_categories(self) -> dict[str, int]:
        """Get all categories and their document counts"""
        return self.manager.get_categories()

    def add_category(
        self,
        name: str,
        description: str = "",
        color: str = "#007acc",
        parent: Optional[str] = None,
    ) -> bool:
        """Add a new category"""
        try:
            if name in self.categories:
                logger.warning(f"Category '{name}' already exists")
                return False

            self.categories[name] = {
                "description": description,
                "color": color,
                "parent": parent,
                "created_at": datetime.now().isoformat(),
                "document_count": 0,
            }

            self._save_categories()
            logger.info(f"Added category '{name}'")
            return True

        except Exception as e:
            logger.error(f"Error adding category: {e}")
            return False

    def remove_category(self, name: str, migrate_to: Optional[str] = None) -> bool:
        """Remove a category"""
        try:
            if name not in self.categories:
                logger.warning(f"Category '{name}' not found")
                return False

            # Migrate documents if specified
            if migrate_to and migrate_to in self.categories:
                documents = self.get_all_documents()
                for document in documents:
                    if document.metadata.get("category") == name:
                        document.update_metadata("category", migrate_to)

            # Remove category
            del self.categories[name]
            self._save_categories()

            logger.info(f"Removed category '{name}'")
            return True

        except Exception as e:
            logger.error(f"Error removing category: {e}")
            return False

    def get_tags(self) -> dict[str, int]:
        """Get all tags and their usage counts"""
        tag_counts = defaultdict(int)
        for document in self.get_all_documents():
            for tag in document.tags:
                tag_counts[tag] += 1

        return dict(tag_counts)

    def add_tag(self, tag: str, description: str = "", color: str = "#28a745") -> bool:
        """Add a new tag"""
        try:
            if tag in self.tags:
                logger.warning(f"Tag '{tag}' already exists")
                return False

            self.tags[tag] = {
                "description": description,
                "color": color,
                "created_at": datetime.now().isoformat(),
                "usage_count": 0,
            }

            self._save_tags()
            logger.info(f"Added tag '{tag}'")
            return True

        except Exception as e:
            logger.error(f"Error adding tag: {e}")
            return False

    def remove_tag(self, tag: str) -> bool:
        """Remove a tag"""
        try:
            if tag not in self.tags:
                logger.warning(f"Tag '{tag}' not found")
                return False

            # Remove tag from all documents
            documents = self.get_all_documents()
            for document in documents:
                if tag in document.tags:
                    document.remove_tag(tag)

            # Remove tag
            del self.tags[tag]
            self._save_tags()

            logger.info(f"Removed tag '{tag}'")
            return True

        except Exception as e:
            logger.error(f"Error removing tag: {e}")
            return False

    def get_analytics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> dict[str, Any]:
        """Get knowledge base analytics"""
        try:
            # Basic statistics
            stats = self.manager.get_statistics()

            # Document trends
            documents = self.get_all_documents()
            doc_trends = self._calculate_document_trends(
                documents, start_date, end_date
            )

            # Category analytics
            category_analytics = self._calculate_category_analytics()

            # Tag analytics
            tag_analytics = self._calculate_tag_analytics()

            # Search analytics
            search_analytics = self.manager.search_engine.get_search_analytics()

            return {
                "knowledge_base": {
                    "name": self.name,
                    "description": self.description,
                    "created_at": self.created_at.isoformat(),
                    "updated_at": self.updated_at.isoformat(),
                },
                "basic_stats": stats,
                "document_trends": doc_trends,
                "category_analytics": category_analytics,
                "tag_analytics": tag_analytics,
                "search_analytics": search_analytics,
            }

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {"error": str(e)}

    def create_backup(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the knowledge base"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = self.backup_dir / f"{self.name}_backup_{timestamp}.zip"

            backup_path = Path(backup_path)

            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add knowledge base data
                for file_path in self.storage_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.startswith("."):
                        arcname = file_path.relative_to(self.storage_path)
                        zipf.write(file_path, arcname)

                # Add metadata
                metadata = {
                    "backup_name": f"{self.name} backup",
                    "created_at": datetime.now().isoformat(),
                    "knowledge_base_name": self.name,
                    "description": self.description,
                    "document_count": len(self.get_all_documents()),
                }

                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2))

            logger.info(f"Created backup at {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False

    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore knowledge base from backup"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # Create backup of current state
            current_backup = (
                self.backup_dir
                / f"{self.name}_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"  # noqa: E501
            )
            self.create_backup(str(current_backup))

            # Clear current data
            self.clear()

            # Extract backup
            with zipfile.ZipFile(backup_path, "r") as zipf:
                zipf.extractall(self.storage_path)

            # Reload data
            self.categories = self._load_categories()
            self.tags = self._load_tags()
            self.analytics = self._load_analytics()
            self.manager.load()

            logger.info(f"Restored knowledge base from {backup_path}")
            return True

        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False

    def clear(self) -> None:
        """Clear all documents from knowledge base"""
        self.manager.clear()
        self.updated_at = datetime.now()
        logger.info(f"Cleared knowledge base '{self.name}'")

    def get_document_count(self) -> int:
        """Get total document count"""
        return len(self.manager)

    def get_recent_documents(self, limit: int = 10) -> list[Document]:
        """Get recently added documents"""
        return self.manager.get_recent_documents(limit)

    def get_similar_documents(
        self, document_id: str, limit: int = 5
    ) -> list[SearchResult]:
        """Get documents similar to a given document"""
        return self.manager.search_engine.get_similar_documents(document_id, limit)

    # Private methods

    def _auto_categorize_document(self, document: Document) -> None:
        """Automatically categorize a document based on content"""
        try:
            content = document.content.lower()
            title = document.title.lower()

            # Simple keyword-based categorization
            category_keywords = {
                "Technical": [
                    "code",
                    "programming",
                    "software",
                    "development",
                    "api",
                    "algorithm",
                ],
                "Research": [
                    "study",
                    "research",
                    "analysis",
                    "findings",
                    "methodology",
                    "results",
                ],
                "Documentation": [
                    "guide",
                    "manual",
                    "documentation",
                    "tutorial",
                    "howto",
                    "instructions",
                ],
                "Business": [
                    "business",
                    "strategy",
                    "market",
                    "revenue",
                    "customer",
                    "product",
                ],
                "Design": ["design", "ui", "ux", "interface", "prototype", "wireframe"],
                "Data": [
                    "data",
                    "database",
                    "analytics",
                    "statistics",
                    "metrics",
                    "report",
                ],
            }

            best_category = "General"
            best_score = 0

            for category, keywords in category_keywords.items():
                score = sum(
                    1 for keyword in keywords if keyword in content or keyword in title
                )
                if score > best_score:
                    best_score = score
                    best_category = category

            if best_score > 0:
                document.update_metadata("category", best_category)
                logger.debug(
                    f"Auto-categorized document '{document.title}' as '{best_category}'"
                )

        except Exception as e:
            logger.error(f"Error auto-categorizing document: {e}")

    def _update_document_metadata(self, document: Document) -> None:
        """Update categories and tags based on document"""
        try:
            # Update category counts
            category = document.metadata.get("category")
            if category and category in self.categories:
                self.categories[category]["document_count"] = sum(
                    1
                    for doc in self.get_all_documents()
                    if doc.metadata.get("category") == category
                )

            # Update tag counts
            for tag in document.tags:
                if tag in self.tags:
                    self.tags[tag]["usage_count"] = sum(
                        1 for doc in self.get_all_documents() if tag in doc.tags
                    )

            self._save_categories()
            self._save_tags()

        except Exception as e:
            logger.error(f"Error updating document metadata: {e}")

    def _load_categories(self) -> dict[str, dict[str, Any]]:
        """Load categories from file"""
        try:
            if self.categories_file.exists():
                with open(self.categories_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading categories: {e}")

        return {}

    def _save_categories(self) -> None:
        """Save categories to file"""
        try:
            with open(self.categories_file, "w", encoding="utf-8") as f:
                json.dump(self.categories, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving categories: {e}")

    def _load_tags(self) -> dict[str, dict[str, Any]]:
        """Load tags from file"""
        try:
            if self.tags_file.exists():
                with open(self.tags_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tags: {e}")

        return {}

    def _save_tags(self) -> None:
        """Save tags to file"""
        try:
            with open(self.tags_file, "w", encoding="utf-8") as f:
                json.dump(self.tags, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tags: {e}")

    def _load_analytics(self) -> dict[str, Any]:
        """Load analytics from file"""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading analytics: {e}")

        return {
            "documents_added": 0,
            "documents_deleted": 0,
            "searches_performed": 0,
            "created_at": datetime.now().isoformat(),
        }

    def _save_analytics(self) -> None:
        """Save analytics to file"""
        try:
            with open(self.analytics_file, "w", encoding="utf-8") as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def _record_document_addition(self, document: Document) -> None:
        """Record document addition in analytics"""
        self.analytics["documents_added"] += 1
        self.analytics["last_document_added"] = {
            "title": document.title,
            "type": document.document_type.value,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_analytics()

    def _record_document_deletion(self, document_id: str) -> None:
        """Record document deletion in analytics"""
        self.analytics["documents_deleted"] += 1
        self.analytics["last_document_deleted"] = {
            "document_id": document_id,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_analytics()

    def _record_document_update(self, document_id: str) -> None:
        """Record document update in analytics"""
        if "documents_updated" not in self.analytics:
            self.analytics["documents_updated"] = 0
        self.analytics["documents_updated"] += 1
        self._save_analytics()

    def _record_search(
        self, query: str, result_count: int, filters: dict[str, Any], search_type: str
    ) -> None:
        """Record search in analytics"""
        self.analytics["searches_performed"] += 1
        self.analytics["last_search"] = {
            "query": query,
            "result_count": result_count,
            "filters": filters,
            "search_type": search_type,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_analytics()

    def _calculate_document_trends(
        self,
        documents: list[Document],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> dict[str, Any]:
        """Calculate document addition trends"""
        # Group documents by creation date
        daily_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for document in documents:
            # Filter by date range if specified
            if start_date and document.created_at < start_date:
                continue
            if end_date and document.created_at > end_date:
                continue

            date_key = document.created_at.strftime("%Y-%m-%d")
            daily_counts[date_key] += 1
            type_counts[document.document_type.value] += 1

        return {
            "daily_additions": dict(daily_counts),
            "type_distribution": dict(type_counts),
            "total_documents": len(documents),
        }

    def _calculate_category_analytics(self) -> dict[str, Any]:
        """Calculate category analytics"""
        category_stats = {}
        for category_name, category_info in self.categories.items():
            category_docs = [
                doc
                for doc in self.get_all_documents()
                if doc.metadata.get("category") == category_name
            ]

            category_stats[category_name] = {
                "document_count": len(category_docs),
                "description": category_info.get("description", ""),
                "color": category_info.get("color", "#007acc"),
                "created_at": category_info.get("created_at"),
                "total_words": sum(doc.get_word_count() for doc in category_docs),
            }

        return category_stats

    def _calculate_tag_analytics(self) -> dict[str, Any]:
        """Calculate tag analytics"""
        tag_stats = {}
        for tag_name, tag_info in self.tags.items():
            tag_docs = [doc for doc in self.get_all_documents() if tag_name in doc.tags]

            tag_stats[tag_name] = {
                "usage_count": len(tag_docs),
                "description": tag_info.get("description", ""),
                "color": tag_info.get("color", "#28a745"),
                "created_at": tag_info.get("created_at"),
            }

        return tag_stats

    @property
    def document_count(self) -> int:
        """Get document count property"""
        return len(self.manager)

    def __len__(self) -> int:
        """Get document count"""
        return len(self.manager)

    def __str__(self) -> str:
        """String representation"""
        return f"KnowledgeBase('{self.name}', {len(self.manager)} docs)"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"KnowledgeBase(name='{self.name}', documents={len(self.manager)}, "
            f"storage_path='{self.storage_path}')"
        )
