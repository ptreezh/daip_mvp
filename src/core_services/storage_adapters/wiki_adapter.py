"""Wiki Adapter for the SSKG.

This module implements the storage adapter for wiki content and structured documentation.
"""

from datetime import datetime
from typing import Any, Optional

try:
    from src.core_services.enhanced_sskg_manager import KnowledgeQuery, NodeType, RelationType
except ImportError:
    # For testing purposes
    from enum import Enum

    class NodeType(str, Enum):
        WIKI = "wiki"

    class RelationType(str, Enum):
        REFERENCES = "references"

    class KnowledgeQuery:
        pass

from .base import StorageAdapter


class WikiAdapter(StorageAdapter):
    """Storage adapter for wiki content and structured documentation.
    
    This adapter manages the storage and retrieval of wiki pages,
    documentation, and structured knowledge articles.
    """
<<<<<<< HEAD

    def store(self, wiki_data: Dict[str, Any], **kwargs) -> str:
=======
    
    def store(self, wiki_data: dict[str, Any], **kwargs) -> str:
>>>>>>> feature/core-services-refactor
        """Store wiki content in the SSKG.
        
        Args:
            wiki_data: Dictionary containing wiki information
                - page_id: Unique identifier for the page
                - title: Title of the page
                - content: Content of the page
                - tags: List of tags
                - references: List of references
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored wiki node

        """
        page_id = wiki_data.get("page_id")
        if not page_id:
            raise ValueError("page_id is required for wiki storage")

        # Create wiki node
        wiki_content = wiki_data.get("content", "")
        wiki_metadata = {
            "page_id": page_id,
            "title": wiki_data.get("title", page_id),
            "tags": wiki_data.get("tags", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "adapter_type": "wiki"
        }

        # Check if page already exists
        existing_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id, "adapter_type": "wiki"},
            limit=1
        ))

        if existing_nodes:
            # Update existing node
            existing_node = existing_nodes[0]
            updated_metadata = dict(existing_node.metadata)
            updated_metadata["title"] = wiki_data.get("title", page_id)
            updated_metadata["tags"] = wiki_data.get("tags", [])
            updated_metadata["updated_at"] = datetime.now().isoformat()
            updated_metadata["version"] = updated_metadata.get("version", 1) + 1

            self.sskg_manager.update_node(existing_node.id, {
                "content": wiki_content,
                "metadata": updated_metadata
            })

            wiki_node_id = existing_node.id
        else:
            # Create new node
            wiki_node_id = self._create_node(
                node_type=NodeType.WIKI,
                content=wiki_content,
                confidence=1.0,
                metadata=wiki_metadata
            )

        # Store references
        references = wiki_data.get("references", [])
        for reference in references:
            if isinstance(reference, str):
                # Simple string reference
                ref_node_id = self._create_node(
                    node_type=NodeType.WIKI,
                    content=f"Reference: {reference}",
                    confidence=0.8,
                    metadata={
                        "reference_url": reference,
                        "adapter_type": "wiki"
                    }
                )

                self._create_relation(
                    source_id=wiki_node_id,
                    target_id=ref_node_id,
                    relation_type=RelationType.REFERENCES
                )
            elif isinstance(reference, dict) and "url" in reference:
                # Detailed reference
                ref_node_id = self._create_node(
                    node_type=NodeType.WIKI,
                    content=f"Reference: {reference.get('title', reference['url'])}",
                    confidence=0.8,
                    metadata={
                        "reference_url": reference["url"],
                        "reference_title": reference.get("title", ""),
                        "reference_description": reference.get("description", ""),
                        "adapter_type": "wiki"
                    }
                )

                self._create_relation(
                    source_id=wiki_node_id,
                    target_id=ref_node_id,
                    relation_type=RelationType.REFERENCES
                )

        self.logger.info(f"Stored wiki page {page_id} with {len(references)} references")
        return wiki_node_id
<<<<<<< HEAD

    def retrieve(self, page_id: str, **kwargs) -> Optional[Dict[str, Any]]:
=======
    
    def retrieve(self, page_id: str, **kwargs) -> Optional[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Retrieve wiki content from the SSKG.
        
        Args:
            page_id: ID of the page to retrieve
            **kwargs: Additional parameters
                - include_references: Whether to include references (default: True)
            
        Returns:
            Wiki data dictionary or None if not found

        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id, "adapter_type": "wiki"},
            limit=1
        ))

        if not wiki_nodes:
            return None

        wiki_node = wiki_nodes[0]
        wiki_data = {
            "page_id": page_id,
            "title": wiki_node.metadata.get("title", page_id),
            "content": wiki_node.content,
            "tags": wiki_node.metadata.get("tags", []),
            "created_at": wiki_node.metadata.get("created_at", ""),
            "updated_at": wiki_node.metadata.get("updated_at", ""),
            "version": wiki_node.metadata.get("version", 1)
        }

        # Include references if requested
        include_references = kwargs.get("include_references", True)
        if include_references:
            wiki_data["references"] = self._retrieve_references(wiki_node.id)

        return wiki_data
<<<<<<< HEAD

    def _retrieve_references(self, wiki_node_id: str) -> List[Dict[str, Any]]:
=======
    
    def _retrieve_references(self, wiki_node_id: str) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Retrieve references for a wiki page.
        
        Args:
            wiki_node_id: ID of the wiki node
            
        Returns:
            List of reference dictionaries

        """
        # Get related nodes with REFERENCES relation
        related_nodes = self.sskg_manager.get_related_nodes(
            node_id=wiki_node_id,
            relation_types=[RelationType.REFERENCES],
            direction="outgoing"
        )

        references = []
        for node, _ in related_nodes:
            if "reference_url" in node.metadata:
                reference = {
                    "url": node.metadata["reference_url"]
                }

                if "reference_title" in node.metadata:
                    reference["title"] = node.metadata["reference_title"]

                if "reference_description" in node.metadata:
                    reference["description"] = node.metadata["reference_description"]

                references.append(reference)

        return references
<<<<<<< HEAD

    def update(self, page_id: str, wiki_data: Dict[str, Any], **kwargs) -> bool:
=======
    
    def update(self, page_id: str, wiki_data: dict[str, Any], **kwargs) -> bool:
>>>>>>> feature/core-services-refactor
        """Update wiki content in the SSKG.
        
        Args:
            page_id: ID of the page to update
            wiki_data: Updated wiki data
            **kwargs: Additional parameters
                - update_references: Whether to update references (default: False)
            
        Returns:
            True if update was successful, False otherwise

        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id, "adapter_type": "wiki"},
            limit=1
        ))

        if not wiki_nodes:
            return False

        wiki_node = wiki_nodes[0]

        # Update wiki metadata
        updated_metadata = dict(wiki_node.metadata)
        if "title" in wiki_data:
            updated_metadata["title"] = wiki_data["title"]
        if "tags" in wiki_data:
            updated_metadata["tags"] = wiki_data["tags"]

        updated_metadata["updated_at"] = datetime.now().isoformat()
        updated_metadata["version"] = updated_metadata.get("version", 1) + 1

        # Update content if provided
        updated_content = wiki_data.get("content", wiki_node.content)

        # Update wiki node
        success = self.sskg_manager.update_node(wiki_node.id, {
            "content": updated_content,
            "metadata": updated_metadata
        })

        # Update references if requested
        update_references = kwargs.get("update_references", False)
        if update_references and "references" in wiki_data:
            # Delete existing references
            related_nodes = self.sskg_manager.get_related_nodes(
                node_id=wiki_node.id,
                relation_types=[RelationType.REFERENCES],
                direction="outgoing"
            )

            for node, _ in related_nodes:
                self.sskg_manager.delete_node(node.id)

            # Add new references
            references = wiki_data["references"]
            for reference in references:
                if isinstance(reference, str):
                    # Simple string reference
                    ref_node_id = self._create_node(
                        node_type=NodeType.WIKI,
                        content=f"Reference: {reference}",
                        confidence=0.8,
                        metadata={
                            "reference_url": reference,
                            "adapter_type": "wiki"
                        }
                    )

                    self._create_relation(
                        source_id=wiki_node.id,
                        target_id=ref_node_id,
                        relation_type=RelationType.REFERENCES
                    )
                elif isinstance(reference, dict) and "url" in reference:
                    # Detailed reference
                    ref_node_id = self._create_node(
                        node_type=NodeType.WIKI,
                        content=f"Reference: {reference.get('title', reference['url'])}",
                        confidence=0.8,
                        metadata={
                            "reference_url": reference["url"],
                            "reference_title": reference.get("title", ""),
                            "reference_description": reference.get("description", ""),
                            "adapter_type": "wiki"
                        }
                    )

                    self._create_relation(
                        source_id=wiki_node.id,
                        target_id=ref_node_id,
                        relation_type=RelationType.REFERENCES
                    )

        if success:
            self.logger.info(f"Updated wiki page {page_id}")

        return success

    def delete(self, page_id: str, **kwargs) -> bool:
        """Delete wiki content from the SSKG.
        
        Args:
            page_id: ID of the page to delete
            **kwargs: Additional parameters
                - delete_references: Whether to delete references (default: True)
            
        Returns:
            True if deletion was successful, False otherwise

        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id, "adapter_type": "wiki"},
            limit=1
        ))

        if not wiki_nodes:
            return False

        wiki_node = wiki_nodes[0]

        # Delete references if requested
        delete_references = kwargs.get("delete_references", True)
        if delete_references:
            related_nodes = self.sskg_manager.get_related_nodes(
                node_id=wiki_node.id,
                relation_types=[RelationType.REFERENCES],
                direction="outgoing"
            )

            for node, _ in related_nodes:
                self.sskg_manager.delete_node(node.id)

        # Delete wiki node
        success = self.sskg_manager.delete_node(wiki_node.id)

        if success:
            self.logger.info(f"Deleted wiki page {page_id}")

        return success
<<<<<<< HEAD

    def list_all(self, **kwargs) -> List[str]:
=======
    
    def list_all(self, **kwargs) -> list[str]:
>>>>>>> feature/core-services-refactor
        """List all page IDs.
        
        Args:
            **kwargs: Additional parameters
                - tag: Filter by tag
            
        Returns:
            List of page IDs

        """
        # Build metadata filters
        metadata_filters = {"adapter_type": "wiki"}

        # Filter by tag if provided
        tag = kwargs.get("tag")
        if tag:
            metadata_filters["tags"] = tag

        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters=metadata_filters,
            limit=1000
        ))

        return [node.metadata.get("page_id", "") for node in wiki_nodes if node.metadata.get("page_id")]
