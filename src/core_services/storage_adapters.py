"""
Unified Storage Adapters for the Semantic Structured Knowledge Graph (SSKG).

This module implements domain-specific adapters that map different memory types
to SSKG representations while maintaining semantic integrity and consistent access patterns.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field

try:
    from src.core_services.enhanced_sskg_manager import (
        EnhancedSSKGManager,
        KnowledgeNode,
        KnowledgeRelation,
        NodeType,
        RelationType
    )
except ImportError:
    # For testing purposes
    from typing import Literal
    
    class NodeType(str, Enum):
        """Types of nodes in the SSKG."""
        FACT = "fact"
        MEMORY = "memory"
        WIKI = "wiki"
        SESSION = "session"
        PROJECT = "project"
        ROLE = "role"
        USER = "user"
        CONCEPT = "concept"
        EVENT = "event"
    
    class RelationType(str, Enum):
        """Types of relationships in the SSKG."""
        IS_A = "is_a"
        PART_OF = "part_of"
        RELATED_TO = "related_to"
        SUPPORTS = "supports"
        CONTRADICTS = "contradicts"
        ELABORATES = "elaborates"
        PRECEDES = "precedes"
        FOLLOWS = "follows"
        CAUSES = "causes"
        CREATED_BY = "created_by"
        OWNED_BY = "owned_by"
        REFERENCES = "references"
        INSTANCE_OF = "instance_of"
        DERIVED_FROM = "derived_from"

logger = logging.getLogger(__name__)

class StorageAdapter(ABC):
    """
    Abstract base class for all storage adapters.
    
    Storage adapters provide a consistent interface for mapping domain-specific
    data structures to SSKG representations while maintaining semantic integrity.
    """
    
    def __init__(self, sskg_manager: 'EnhancedSSKGManager'):
        """
        Initialize the storage adapter.
        
        Args:
            sskg_manager: The SSKG manager to use for storage operations
        """
        self.sskg_manager = sskg_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def store(self, data: Any, **kwargs) -> str:
        """
        Store data in the SSKG.
        
        Args:
            data: The data to store
            **kwargs: Additional parameters for storage
            
        Returns:
            ID of the stored node
        """
        pass
    
    @abstractmethod
    def retrieve(self, identifier: str, **kwargs) -> Optional[Any]:
        """
        Retrieve data from the SSKG.
        
        Args:
            identifier: The identifier of the data to retrieve
            **kwargs: Additional parameters for retrieval
            
        Returns:
            Retrieved data or None if not found
        """
        pass
    
    @abstractmethod
    def update(self, identifier: str, data: Any, **kwargs) -> bool:
        """
        Update data in the SSKG.
        
        Args:
            identifier: The identifier of the data to update
            data: The updated data
            **kwargs: Additional parameters for update
            
        Returns:
            True if update was successful, False otherwise
        """
        pass    
    
    @abstractmethod
    def delete(self, identifier: str, **kwargs) -> bool:
        """
        Delete data from the SSKG.
        
        Args:
            identifier: The identifier of the data to delete
            **kwargs: Additional parameters for deletion
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list(self, **kwargs) -> List[str]:
        """
        List all data identifiers of this type.
        
        Args:
            **kwargs: Additional parameters for listing
            
        Returns:
            List of data identifiers
        """
        pass
    
    def _create_node(self, node_type: NodeType, content: str, 
                    confidence: float = 1.0, metadata: Dict[str, Any] = None) -> str:
        """
        Helper method to create a node in the SSKG.
        
        Args:
            node_type: Type of the node
            content: Content of the node
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            ID of the created node
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeNode
        
        node = KnowledgeNode(
            node_type=node_type,
            content=content,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return self.sskg_manager.add_node(node)
    
    def _create_relation(self, source_id: str, target_id: str, 
                        relation_type: RelationType, confidence: float = 1.0,
                        metadata: Dict[str, Any] = None) -> bool:
        """
        Helper method to create a relation in the SSKG.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of the relation
            confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            True if relation was created successfully, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeRelation
        
        relation = KnowledgeRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return self.sskg_manager.add_relation(relation)

class RoleMemoryAdapter(StorageAdapter):
    """
    Storage adapter for virtual role memories and identities.
    
    This adapter manages the storage and retrieval of role-specific memories,
    personality traits, and cognitive frameworks.
    """
    
    def store(self, role_data: Dict[str, Any], **kwargs) -> str:
        """
        Store role memory data in the SSKG.
        
        Args:
            role_data: Dictionary containing role information
                - role_id: Unique identifier for the role
                - name: Name of the role
                - personality: Personality traits
                - memories: List of role memories
                - cognitive_framework: Cognitive framework data
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored role node
        """
        role_id = role_data.get("role_id")
        if not role_id:
            raise ValueError("role_id is required for role storage")
        
        # Create main role node
        role_content = f"Role: {role_data.get('name', role_id)}"
        role_metadata = {
            "role_id": role_id,
            "name": role_data.get("name", ""),
            "personality": role_data.get("personality", {}),
            "cognitive_framework": role_data.get("cognitive_framework", {}),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "role_memory"
        }
        
        role_node_id = self._create_node(
            node_type=NodeType.ROLE,
            content=role_content,
            confidence=1.0,
            metadata=role_metadata
        )
        
        # Store individual memories
        memories = role_data.get("memories", [])
        for memory in memories:
            memory_node_id = self._store_role_memory(memory, role_id)
            if memory_node_id:
                # Create relation between role and memory
                self._create_relation(
                    source_id=memory_node_id,
                    target_id=role_node_id,
                    relation_type=RelationType.OWNED_BY
                )
        
        self.logger.info(f"Stored role {role_id} with {len(memories)} memories")
        return role_node_id
    
    def _store_role_memory(self, memory_data: Dict[str, Any], role_id: str) -> Optional[str]:
        """
        Store a single role memory.
        
        Args:
            memory_data: Memory data dictionary
            role_id: ID of the role that owns this memory
            
        Returns:
            ID of the stored memory node or None if failed
        """
        if not memory_data.get("content"):
            return None
        
        memory_metadata = {
            "role_id": role_id,
            "memory_type": memory_data.get("type", "episodic"),
            "importance": memory_data.get("importance", 0.5),
            "context": memory_data.get("context", {}),
            "timestamp": memory_data.get("timestamp", datetime.now().isoformat()),
            "adapter_type": "role_memory"
        }
        
        return self._create_node(
            node_type=NodeType.MEMORY,
            content=memory_data["content"],
            confidence=memory_data.get("confidence", 0.8),
            metadata=memory_metadata
        )
    
    def retrieve(self, role_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve role data from the SSKG.
        
        Args:
            role_id: ID of the role to retrieve
            **kwargs: Additional parameters
                - include_memories: Whether to include role memories (default: True)
            
        Returns:
            Role data dictionary or None if not found
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id},
            limit=1
        ))
        
        if not role_nodes:
            return None
        
        role_node = role_nodes[0]
        role_data = {
            "role_id": role_id,
            "name": role_node.metadata.get("name", ""),
            "personality": role_node.metadata.get("personality", {}),
            "cognitive_framework": role_node.metadata.get("cognitive_framework", {}),
            "created_at": role_node.metadata.get("created_at", ""),
            "memories": []
        }
        
        # Retrieve memories if requested
        if kwargs.get("include_memories", True):
            memory_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.MEMORY],
                metadata_filters={"role_id": role_id},
                limit=100
            ))
            
            for memory_node in memory_nodes:
                memory_data = {
                    "content": memory_node.content,
                    "type": memory_node.metadata.get("memory_type", "episodic"),
                    "importance": memory_node.metadata.get("importance", 0.5),
                    "confidence": memory_node.confidence,
                    "context": memory_node.metadata.get("context", {}),
                    "timestamp": memory_node.metadata.get("timestamp", "")
                }
                role_data["memories"].append(memory_data)
        
        return role_data
    
    def update(self, role_id: str, role_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update role data in the SSKG.
        
        Args:
            role_id: ID of the role to update
            role_data: Updated role data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find existing role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id},
            limit=1
        ))
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Update role metadata
        updated_metadata = role_node.metadata.copy()
        updated_metadata.update({
            "name": role_data.get("name", updated_metadata.get("name", "")),
            "personality": role_data.get("personality", updated_metadata.get("personality", {})),
            "cognitive_framework": role_data.get("cognitive_framework", updated_metadata.get("cognitive_framework", {})),
            "updated_at": datetime.now().isoformat()
        })
        
        # Update the node
        success = self.sskg_manager.update_node(role_node.id, {
            "content": f"Role: {updated_metadata['name']}",
            "metadata": updated_metadata
        })
        
        if success:
            self.logger.info(f"Updated role {role_id}")
        
        return success    
    
    def delete(self, role_id: str, **kwargs) -> bool:
        """
        Delete role data from the SSKG.
        
        Args:
            role_id: ID of the role to delete
            **kwargs: Additional parameters
                - delete_memories: Whether to delete associated memories (default: True)
            
        Returns:
            True if deletion was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id},
            limit=1
        ))
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Delete associated memories if requested
        if kwargs.get("delete_memories", True):
            memory_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.MEMORY],
                metadata_filters={"role_id": role_id},
                limit=1000
            ))
            
            for memory_node in memory_nodes:
                self.sskg_manager.delete_node(memory_node.id)
        
        # Delete role node
        success = self.sskg_manager.delete_node(role_node.id)
        
        if success:
            self.logger.info(f"Deleted role {role_id}")
        
        return success
    
    def list(self, **kwargs) -> List[str]:
        """
        List all role IDs.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            List of role IDs
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"adapter_type": "role_memory"},
            limit=1000
        ))
        
        return [node.metadata.get("role_id", "") for node in role_nodes if node.metadata.get("role_id")]


class WikiAdapter(StorageAdapter):
    """
    Storage adapter for wiki content and structured documentation.
    
    This adapter manages the storage and retrieval of wiki pages,
    documentation, and structured knowledge articles.
    """
    
    def store(self, wiki_data: Dict[str, Any], **kwargs) -> str:
        """
        Store wiki content in the SSKG.
        
        Args:
            wiki_data: Dictionary containing wiki information
                - page_id: Unique identifier for the wiki page
                - title: Title of the wiki page
                - content: Content of the wiki page
                - tags: List of tags
                - category: Category of the page
                - contributors: List of contributors
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored wiki node
        """
        page_id = wiki_data.get("page_id")
        if not page_id:
            raise ValueError("page_id is required for wiki storage")
        
        # Create wiki content
        wiki_content = f"Wiki Page: {wiki_data.get('title', page_id)}\n\n{wiki_data.get('content', '')}"
        
        wiki_metadata = {
            "page_id": page_id,
            "title": wiki_data.get("title", ""),
            "tags": wiki_data.get("tags", []),
            "category": wiki_data.get("category", ""),
            "contributors": wiki_data.get("contributors", []),
            "version": wiki_data.get("version", 1),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "wiki"
        }
        
        wiki_node_id = self._create_node(
            node_type=NodeType.WIKI,
            content=wiki_content,
            confidence=wiki_data.get("confidence", 0.9),
            metadata=wiki_metadata
        )
        
        # Create relations for tags and categories
        self._create_wiki_relations(wiki_node_id, wiki_data)
        
        self.logger.info(f"Stored wiki page {page_id}")
        return wiki_node_id
    
    def _create_wiki_relations(self, wiki_node_id: str, wiki_data: Dict[str, Any]):
        """
        Create relations for wiki page (tags, categories, etc.).
        
        Args:
            wiki_node_id: ID of the wiki node
            wiki_data: Wiki data dictionary
        """
        # Create category relations
        category = wiki_data.get("category")
        if category:
            category_node_id = self._get_or_create_category_node(category)
            self._create_relation(
                source_id=wiki_node_id,
                target_id=category_node_id,
                relation_type=RelationType.PART_OF
            )
        
        # Create tag relations
        tags = wiki_data.get("tags", [])
        for tag in tags:
            tag_node_id = self._get_or_create_tag_node(tag)
            self._create_relation(
                source_id=wiki_node_id,
                target_id=tag_node_id,
                relation_type=RelationType.RELATED_TO
            )
    
    def _get_or_create_category_node(self, category: str) -> str:
        """
        Get or create a category node.
        
        Args:
            category: Category name
            
        Returns:
            ID of the category node
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Check if category node exists
        category_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.CONCEPT],
            metadata_filters={"concept_type": "category", "name": category},
            limit=1
        ))
        
        if category_nodes:
            return category_nodes[0].id
        
        # Create new category node
        return self._create_node(
            node_type=NodeType.CONCEPT,
            content=f"Category: {category}",
            confidence=1.0,
            metadata={
                "concept_type": "category",
                "name": category,
                "adapter_type": "wiki"
            }
        )   
 
    def _get_or_create_tag_node(self, tag: str) -> str:
        """
        Get or create a tag node.
        
        Args:
            tag: Tag name
            
        Returns:
            ID of the tag node
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Check if tag node exists
        tag_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.CONCEPT],
            metadata_filters={"concept_type": "tag", "name": tag},
            limit=1
        ))
        
        if tag_nodes:
            return tag_nodes[0].id
        
        # Create new tag node
        return self._create_node(
            node_type=NodeType.CONCEPT,
            content=f"Tag: {tag}",
            confidence=1.0,
            metadata={
                "concept_type": "tag",
                "name": tag,
                "adapter_type": "wiki"
            }
        )
    
    def retrieve(self, page_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve wiki content from the SSKG.
        
        Args:
            page_id: ID of the wiki page to retrieve
            **kwargs: Additional parameters
                - include_relations: Whether to include related pages (default: False)
            
        Returns:
            Wiki data dictionary or None if not found
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id},
            limit=1
        ))
        
        if not wiki_nodes:
            return None
        
        wiki_node = wiki_nodes[0]
        
        # Extract content (remove title prefix)
        content = wiki_node.content
        if content.startswith("Wiki Page:"):
            lines = content.split("\n", 2)
            if len(lines) >= 3:
                content = lines[2]
        
        wiki_data = {
            "page_id": page_id,
            "title": wiki_node.metadata.get("title", ""),
            "content": content,
            "tags": wiki_node.metadata.get("tags", []),
            "category": wiki_node.metadata.get("category", ""),
            "contributors": wiki_node.metadata.get("contributors", []),
            "version": wiki_node.metadata.get("version", 1),
            "confidence": wiki_node.confidence,
            "created_at": wiki_node.metadata.get("created_at", ""),
            "updated_at": wiki_node.updated_at.isoformat()
        }
        
        # Include related pages if requested
        if kwargs.get("include_relations", False):
            related_pages = self._get_related_pages(wiki_node.id)
            wiki_data["related_pages"] = related_pages
        
        return wiki_data
    
    def _get_related_pages(self, wiki_node_id: str) -> List[Dict[str, Any]]:
        """
        Get pages related to the given wiki page.
        
        Args:
            wiki_node_id: ID of the wiki node
            
        Returns:
            List of related page information
        """
        related_nodes = self.sskg_manager.get_related_nodes(
            node_id=wiki_node_id,
            relation_types=[RelationType.RELATED_TO, RelationType.PART_OF],
            limit=20
        )
        
        related_pages = []
        for related_node, relation_type in related_nodes:
            if related_node.node_type == NodeType.WIKI:
                related_pages.append({
                    "page_id": related_node.metadata.get("page_id", ""),
                    "title": related_node.metadata.get("title", ""),
                    "relation_type": relation_type.value
                })
        
        return related_pages   
 
    def update(self, page_id: str, wiki_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update wiki content in the SSKG.
        
        Args:
            page_id: ID of the wiki page to update
            wiki_data: Updated wiki data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find existing wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id},
            limit=1
        ))
        
        if not wiki_nodes:
            return False
        
        wiki_node = wiki_nodes[0]
        
        # Update wiki content
        new_content = f"Wiki Page: {wiki_data.get('title', page_id)}\n\n{wiki_data.get('content', '')}"
        
        # Update metadata
        updated_metadata = wiki_node.metadata.copy()
        updated_metadata.update({
            "title": wiki_data.get("title", updated_metadata.get("title", "")),
            "tags": wiki_data.get("tags", updated_metadata.get("tags", [])),
            "category": wiki_data.get("category", updated_metadata.get("category", "")),
            "contributors": wiki_data.get("contributors", updated_metadata.get("contributors", [])),
            "version": updated_metadata.get("version", 1) + 1,
            "updated_at": datetime.now().isoformat()
        })
        
        # Update the node
        success = self.sskg_manager.update_node(wiki_node.id, {
            "content": new_content,
            "confidence": wiki_data.get("confidence", wiki_node.confidence),
            "metadata": updated_metadata
        })
        
        if success:
            # Update relations if needed
            self._create_wiki_relations(wiki_node.id, wiki_data)
            self.logger.info(f"Updated wiki page {page_id}")
        
        return success
    
    def delete(self, page_id: str, **kwargs) -> bool:
        """
        Delete wiki content from the SSKG.
        
        Args:
            page_id: ID of the wiki page to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find wiki node
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id},
            limit=1
        ))
        
        if not wiki_nodes:
            return False
        
        wiki_node = wiki_nodes[0]
        
        # Delete wiki node
        success = self.sskg_manager.delete_node(wiki_node.id)
        
        if success:
            self.logger.info(f"Deleted wiki page {page_id}")
        
        return success
    
    def list(self, **kwargs) -> List[str]:
        """
        List all wiki page IDs.
        
        Args:
            **kwargs: Additional parameters
                - category: Filter by category
                - tag: Filter by tag
            
        Returns:
            List of wiki page IDs
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Build metadata filters
        metadata_filters = {"adapter_type": "wiki"}
        
        if kwargs.get("category"):
            metadata_filters["category"] = kwargs["category"]
        
        if kwargs.get("tag"):
            # This is a simplified approach; in practice, you might want to
            # query by relations to tag nodes
            pass
        
        wiki_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters=metadata_filters,
            limit=1000
        ))
        
        return [node.metadata.get("page_id", "") for node in wiki_nodes if node.metadata.get("page_id")]


class SessionAdapter(StorageAdapter):
    """
    Storage adapter for conversation states and session data.
    
    This adapter manages the storage and retrieval of session states,
    conversation history, and context information.
    """
    
    def store(self, session_data: Dict[str, Any], **kwargs) -> str:
        """
        Store session data in the SSKG.
        
        Args:
            session_data: Dictionary containing session information
                - session_id: Unique identifier for the session
                - state: Session state data
                - context: Conversation context
                - participants: List of participants
                - metadata: Additional session metadata
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored session node
        """
        session_id = session_data.get("session_id")
        if not session_id:
            raise ValueError("session_id is required for session storage")
        
        # Create session content
        session_content = f"Session: {session_id}"
        if session_data.get("context"):
            session_content += f"\nContext: {json.dumps(session_data['context'], indent=2)}"
        
        session_metadata = {
            "session_id": session_id,
            "state": session_data.get("state", {}),
            "context": session_data.get("context", {}),
            "participants": session_data.get("participants", []),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "session"
        }
        
        # Add any additional metadata
        if session_data.get("metadata"):
            session_metadata.update(session_data["metadata"])
        
        session_node_id = self._create_node(
            node_type=NodeType.SESSION,
            content=session_content,
            confidence=1.0,
            metadata=session_metadata
        )
        
        # Create relations to participants
        participants = session_data.get("participants", [])
        for participant_id in participants:
            self._create_participant_relation(session_node_id, participant_id)
        
        self.logger.info(f"Stored session {session_id}")
        return session_node_id
    
    def _create_participant_relation(self, session_node_id: str, participant_id: str):
        """
        Create a relation between session and participant.
        
        Args:
            session_node_id: ID of the session node
            participant_id: ID of the participant
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Try to find participant node (could be role or user)
        participant_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE, NodeType.USER],
            metadata_filters={"role_id": participant_id},
            limit=1
        ))
        
        if not participant_nodes:
            # Try with user_id
            participant_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.USER],
                metadata_filters={"user_id": participant_id},
                limit=1
            ))
        
        if participant_nodes:
            self._create_relation(
                source_id=session_node_id,
                target_id=participant_nodes[0].id,
                relation_type=RelationType.REFERENCES
            )
    
    def retrieve(self, session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from the SSKG.
        
        Args:
            session_id: ID of the session to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Session data dictionary or None if not found
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id},
            limit=1
        ))
        
        if not session_nodes:
            return None
        
        session_node = session_nodes[0]
        
        session_data = {
            "session_id": session_id,
            "state": session_node.metadata.get("state", {}),
            "context": session_node.metadata.get("context", {}),
            "participants": session_node.metadata.get("participants", []),
            "created_at": session_node.metadata.get("created_at", ""),
            "updated_at": session_node.updated_at.isoformat()
        }
        
        # Add any additional metadata (excluding adapter-specific fields)
        for key, value in session_node.metadata.items():
            if key not in ["session_id", "state", "context", "participants", "created_at", "adapter_type"]:
                session_data[key] = value
        
        return session_data   
 
    def update(self, session_id: str, session_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update session data in the SSKG.
        
        Args:
            session_id: ID of the session to update
            session_data: Updated session data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find existing session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id},
            limit=1
        ))
        
        if not session_nodes:
            return False
        
        session_node = session_nodes[0]
        
        # Update session content
        new_content = f"Session: {session_id}"
        if session_data.get("context"):
            new_content += f"\nContext: {json.dumps(session_data['context'], indent=2)}"
        
        # Update metadata
        updated_metadata = session_node.metadata.copy()
        updated_metadata.update({
            "state": session_data.get("state", updated_metadata.get("state", {})),
            "context": session_data.get("context", updated_metadata.get("context", {})),
            "participants": session_data.get("participants", updated_metadata.get("participants", [])),
            "updated_at": datetime.now().isoformat()
        })
        
        # Add any additional metadata
        if session_data.get("metadata"):
            updated_metadata.update(session_data["metadata"])
        
        # Update the node
        success = self.sskg_manager.update_node(session_node.id, {
            "content": new_content,
            "metadata": updated_metadata
        })
        
        if success:
            self.logger.info(f"Updated session {session_id}")
        
        return success
    
    def delete(self, session_id: str, **kwargs) -> bool:
        """
        Delete session data from the SSKG.
        
        Args:
            session_id: ID of the session to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find session node
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id},
            limit=1
        ))
        
        if not session_nodes:
            return False
        
        session_node = session_nodes[0]
        
        # Delete session node
        success = self.sskg_manager.delete_node(session_node.id)
        
        if success:
            self.logger.info(f"Deleted session {session_id}")
        
        return success
    
    def list(self, **kwargs) -> List[str]:
        """
        List all session IDs.
        
        Args:
            **kwargs: Additional parameters
                - participant: Filter by participant ID
            
        Returns:
            List of session IDs
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Build metadata filters
        metadata_filters = {"adapter_type": "session"}
        
        if kwargs.get("participant"):
            # This is a simplified approach; in practice, you might want to
            # query by relations to participant nodes
            pass
        
        session_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters=metadata_filters,
            limit=1000
        ))
        
        return [node.metadata.get("session_id", "") for node in session_nodes if node.metadata.get("session_id")]


class ProjectAdapter(StorageAdapter):
    """
    Storage adapter for project configurations and management data.
    
    This adapter manages the storage and retrieval of project settings,
    configurations, and metadata.
    """
    
    def store(self, project_data: Dict[str, Any], **kwargs) -> str:
        """
        Store project data in the SSKG.
        
        Args:
            project_data: Dictionary containing project information
                - project_id: Unique identifier for the project
                - name: Name of the project
                - description: Project description
                - configuration: Project configuration data
                - settings: Project settings
                - metadata: Additional project metadata
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored project node
        """
        project_id = project_data.get("project_id")
        if not project_id:
            raise ValueError("project_id is required for project storage")
        
        # Create project content
        project_content = f"Project: {project_data.get('name', project_id)}"
        if project_data.get("description"):
            project_content += f"\nDescription: {project_data['description']}"
        
        project_metadata = {
            "project_id": project_id,
            "name": project_data.get("name", ""),
            "description": project_data.get("description", ""),
            "configuration": project_data.get("configuration", {}),
            "settings": project_data.get("settings", {}),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "project"
        }
        
        # Add any additional metadata
        if project_data.get("metadata"):
            project_metadata.update(project_data["metadata"])
        
        project_node_id = self._create_node(
            node_type=NodeType.PROJECT,
            content=project_content,
            confidence=1.0,
            metadata=project_metadata
        )
        
        self.logger.info(f"Stored project {project_id}")
        return project_node_id
    
    def retrieve(self, project_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve project data from the SSKG.
        
        Args:
            project_id: ID of the project to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Project data dictionary or None if not found
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find project node
        project_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"project_id": project_id},
            limit=1
        ))
        
        if not project_nodes:
            return None
        
        project_node = project_nodes[0]
        
        project_data = {
            "project_id": project_id,
            "name": project_node.metadata.get("name", ""),
            "description": project_node.metadata.get("description", ""),
            "configuration": project_node.metadata.get("configuration", {}),
            "settings": project_node.metadata.get("settings", {}),
            "created_at": project_node.metadata.get("created_at", ""),
            "updated_at": project_node.updated_at.isoformat()
        }
        
        # Add any additional metadata (excluding adapter-specific fields)
        for key, value in project_node.metadata.items():
            if key not in ["project_id", "name", "description", "configuration", "settings", "created_at", "adapter_type"]:
                project_data[key] = value
        
        return project_data   
 
    def update(self, project_id: str, project_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update project data in the SSKG.
        
        Args:
            project_id: ID of the project to update
            project_data: Updated project data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find existing project node
        project_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"project_id": project_id},
            limit=1
        ))
        
        if not project_nodes:
            return False
        
        project_node = project_nodes[0]
        
        # Update project content
        new_content = f"Project: {project_data.get('name', project_id)}"
        if project_data.get("description"):
            new_content += f"\nDescription: {project_data['description']}"
        
        # Update metadata
        updated_metadata = project_node.metadata.copy()
        updated_metadata.update({
            "name": project_data.get("name", updated_metadata.get("name", "")),
            "description": project_data.get("description", updated_metadata.get("description", "")),
            "configuration": project_data.get("configuration", updated_metadata.get("configuration", {})),
            "settings": project_data.get("settings", updated_metadata.get("settings", {})),
            "updated_at": datetime.now().isoformat()
        })
        
        # Add any additional metadata
        if project_data.get("metadata"):
            updated_metadata.update(project_data["metadata"])
        
        # Update the node
        success = self.sskg_manager.update_node(project_node.id, {
            "content": new_content,
            "metadata": updated_metadata
        })
        
        if success:
            self.logger.info(f"Updated project {project_id}")
        
        return success
    
    def delete(self, project_id: str, **kwargs) -> bool:
        """
        Delete project data from the SSKG.
        
        Args:
            project_id: ID of the project to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find project node
        project_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"project_id": project_id},
            limit=1
        ))
        
        if not project_nodes:
            return False
        
        project_node = project_nodes[0]
        
        # Delete project node
        success = self.sskg_manager.delete_node(project_node.id)
        
        if success:
            self.logger.info(f"Deleted project {project_id}")
        
        return success
    
    def list(self, **kwargs) -> List[str]:
        """
        List all project IDs.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            List of project IDs
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        project_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"adapter_type": "project"},
            limit=1000
        ))
        
        return [node.metadata.get("project_id", "") for node in project_nodes if node.metadata.get("project_id")]


class MemoryBankAdapter(StorageAdapter):
    """
    Storage adapter for consolidated knowledge and memory banks.
    
    This adapter manages the storage and retrieval of consolidated memories,
    knowledge summaries, and aggregated information.
    """
    
    def store(self, memory_bank_data: Dict[str, Any], **kwargs) -> str:
        """
        Store memory bank data in the SSKG.
        
        Args:
            memory_bank_data: Dictionary containing memory bank information
                - bank_id: Unique identifier for the memory bank
                - name: Name of the memory bank
                - description: Description of the memory bank
                - memories: List of consolidated memories
                - summary: Summary of the memory bank
                - topics: List of topics covered
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored memory bank node
        """
        bank_id = memory_bank_data.get("bank_id")
        if not bank_id:
            raise ValueError("bank_id is required for memory bank storage")
        
        # Create memory bank content
        bank_content = f"Memory Bank: {memory_bank_data.get('name', bank_id)}"
        if memory_bank_data.get("description"):
            bank_content += f"\nDescription: {memory_bank_data['description']}"
        if memory_bank_data.get("summary"):
            bank_content += f"\nSummary: {memory_bank_data['summary']}"
        
        bank_metadata = {
            "bank_id": bank_id,
            "name": memory_bank_data.get("name", ""),
            "description": memory_bank_data.get("description", ""),
            "summary": memory_bank_data.get("summary", ""),
            "topics": memory_bank_data.get("topics", []),
            "memory_count": len(memory_bank_data.get("memories", [])),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "memory_bank"
        }
        
        bank_node_id = self._create_node(
            node_type=NodeType.MEMORY,
            content=bank_content,
            confidence=memory_bank_data.get("confidence", 0.8),
            metadata=bank_metadata
        )
        
        # Store individual memories
        memories = memory_bank_data.get("memories", [])
        for memory in memories:
            memory_node_id = self._store_consolidated_memory(memory, bank_id)
            if memory_node_id:
                # Create relation between memory bank and memory
                self._create_relation(
                    source_id=memory_node_id,
                    target_id=bank_node_id,
                    relation_type=RelationType.PART_OF
                )
        
        self.logger.info(f"Stored memory bank {bank_id} with {len(memories)} memories")
        return bank_node_id
    
    def _store_consolidated_memory(self, memory_data: Dict[str, Any], bank_id: str) -> Optional[str]:
        """
        Store a consolidated memory.
        
        Args:
            memory_data: Memory data dictionary
            bank_id: ID of the memory bank that contains this memory
            
        Returns:
            ID of the stored memory node or None if failed
        """
        if not memory_data.get("content"):
            return None
        
        memory_metadata = {
            "bank_id": bank_id,
            "memory_type": memory_data.get("type", "consolidated"),
            "importance": memory_data.get("importance", 0.7),
            "topics": memory_data.get("topics", []),
            "source_count": memory_data.get("source_count", 1),
            "consolidation_method": memory_data.get("consolidation_method", ""),
            "timestamp": memory_data.get("timestamp", datetime.now().isoformat()),
            "adapter_type": "memory_bank"
        }
        
        return self._create_node(
            node_type=NodeType.MEMORY,
            content=memory_data["content"],
            confidence=memory_data.get("confidence", 0.7),
            metadata=memory_metadata
        )   
 
    def retrieve(self, bank_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve memory bank data from the SSKG.
        
        Args:
            bank_id: ID of the memory bank to retrieve
            **kwargs: Additional parameters
                - include_memories: Whether to include individual memories (default: True)
            
        Returns:
            Memory bank data dictionary or None if not found
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find memory bank node
        bank_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters={"bank_id": bank_id, "adapter_type": "memory_bank"},
            limit=1
        ))
        
        if not bank_nodes:
            return None
        
        bank_node = bank_nodes[0]
        
        bank_data = {
            "bank_id": bank_id,
            "name": bank_node.metadata.get("name", ""),
            "description": bank_node.metadata.get("description", ""),
            "summary": bank_node.metadata.get("summary", ""),
            "topics": bank_node.metadata.get("topics", []),
            "memory_count": bank_node.metadata.get("memory_count", 0),
            "confidence": bank_node.confidence,
            "created_at": bank_node.metadata.get("created_at", ""),
            "updated_at": bank_node.updated_at.isoformat(),
            "memories": []
        }
        
        # Retrieve individual memories if requested
        if kwargs.get("include_memories", True):
            memory_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.MEMORY],
                metadata_filters={"bank_id": bank_id, "memory_type": "consolidated"},
                limit=1000
            ))
            
            for memory_node in memory_nodes:
                memory_data = {
                    "content": memory_node.content,
                    "type": memory_node.metadata.get("memory_type", "consolidated"),
                    "importance": memory_node.metadata.get("importance", 0.7),
                    "confidence": memory_node.confidence,
                    "topics": memory_node.metadata.get("topics", []),
                    "source_count": memory_node.metadata.get("source_count", 1),
                    "consolidation_method": memory_node.metadata.get("consolidation_method", ""),
                    "timestamp": memory_node.metadata.get("timestamp", "")
                }
                bank_data["memories"].append(memory_data)
        
        return bank_data
    
    def update(self, bank_id: str, memory_bank_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update memory bank data in the SSKG.
        
        Args:
            bank_id: ID of the memory bank to update
            memory_bank_data: Updated memory bank data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find existing memory bank node
        bank_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters={"bank_id": bank_id, "adapter_type": "memory_bank"},
            limit=1
        ))
        
        if not bank_nodes:
            return False
        
        bank_node = bank_nodes[0]
        
        # Update memory bank content
        new_content = f"Memory Bank: {memory_bank_data.get('name', bank_id)}"
        if memory_bank_data.get("description"):
            new_content += f"\nDescription: {memory_bank_data['description']}"
        if memory_bank_data.get("summary"):
            new_content += f"\nSummary: {memory_bank_data['summary']}"
        
        # Update metadata
        updated_metadata = bank_node.metadata.copy()
        updated_metadata.update({
            "name": memory_bank_data.get("name", updated_metadata.get("name", "")),
            "description": memory_bank_data.get("description", updated_metadata.get("description", "")),
            "summary": memory_bank_data.get("summary", updated_metadata.get("summary", "")),
            "topics": memory_bank_data.get("topics", updated_metadata.get("topics", [])),
            "memory_count": len(memory_bank_data.get("memories", [])),
            "updated_at": datetime.now().isoformat()
        })
        
        # Update the node
        success = self.sskg_manager.update_node(bank_node.id, {
            "content": new_content,
            "confidence": memory_bank_data.get("confidence", bank_node.confidence),
            "metadata": updated_metadata
        })
        
        if success:
            self.logger.info(f"Updated memory bank {bank_id}")
        
        return success
    
    def delete(self, bank_id: str, **kwargs) -> bool:
        """
        Delete memory bank data from the SSKG.
        
        Args:
            bank_id: ID of the memory bank to delete
            **kwargs: Additional parameters
                - delete_memories: Whether to delete individual memories (default: True)
            
        Returns:
            True if deletion was successful, False otherwise
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Find memory bank node
        bank_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters={"bank_id": bank_id, "adapter_type": "memory_bank"},
            limit=1
        ))
        
        if not bank_nodes:
            return False
        
        bank_node = bank_nodes[0]
        
        # Delete individual memories if requested
        if kwargs.get("delete_memories", True):
            memory_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.MEMORY],
                metadata_filters={"bank_id": bank_id, "memory_type": "consolidated"},
                limit=1000
            ))
            
            for memory_node in memory_nodes:
                self.sskg_manager.delete_node(memory_node.id)
        
        # Delete memory bank node
        success = self.sskg_manager.delete_node(bank_node.id)
        
        if success:
            self.logger.info(f"Deleted memory bank {bank_id}")
        
        return success
    
    def list(self, **kwargs) -> List[str]:
        """
        List all memory bank IDs.
        
        Args:
            **kwargs: Additional parameters
                - topic: Filter by topic
            
        Returns:
            List of memory bank IDs
        """
        from src.core_services.enhanced_sskg_manager import KnowledgeQuery
        
        # Build metadata filters
        metadata_filters = {"adapter_type": "memory_bank"}
        
        if kwargs.get("topic"):
            # This is a simplified approach; in practice, you might want to
            # implement more sophisticated topic filtering
            pass
        
        bank_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters=metadata_filters,
            limit=1000
        ))
        
        return [node.metadata.get("bank_id", "") for node in bank_nodes if node.metadata.get("bank_id")]


class StorageAdapterManager:
    """
    Manager for all storage adapters.
    
    This class provides a unified interface for accessing different storage adapters
    and managing their lifecycle.
    """
    
    def __init__(self, sskg_manager: 'EnhancedSSKGManager'):
        """
        Initialize the storage adapter manager.
        
        Args:
            sskg_manager: The SSKG manager to use for storage operations
        """
        self.sskg_manager = sskg_manager
        self.adapters = {
            "role_memory": RoleMemoryAdapter(sskg_manager),
            "wiki": WikiAdapter(sskg_manager),
            "session": SessionAdapter(sskg_manager),
            "project": ProjectAdapter(sskg_manager),
            "memory_bank": MemoryBankAdapter(sskg_manager)
        }
        self.logger = logging.getLogger(__name__)
    
    def get_adapter(self, adapter_type: str) -> Optional[StorageAdapter]:
        """
        Get a storage adapter by type.
        
        Args:
            adapter_type: Type of the adapter
            
        Returns:
            Storage adapter or None if not found
        """
        return self.adapters.get(adapter_type)
    
    def register_adapter(self, adapter_type: str, adapter: StorageAdapter):
        """
        Register a new storage adapter.
        
        Args:
            adapter_type: Type of the adapter
            adapter: Storage adapter instance
        """
        self.adapters[adapter_type] = adapter
        self.logger.info(f"Registered storage adapter: {adapter_type}")
    
    def list_adapters(self) -> List[str]:
        """
        List all registered adapter types.
        
        Returns:
            List of adapter types
        """
        return list(self.adapters.keys())