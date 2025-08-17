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
        node = KnowledgeNode(
            id=None,  # Will be generated
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
            True if relation was created successfully
        """
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
                - include_memories: Whether to include role memories
                
        Returns:
            Role data dictionary or None if not found
        """
        # Find role node
        role_nodes = self.sskg_manager.query({
            "node_types": [NodeType.ROLE],
            "metadata_filters": {"role_id": role_id},
            "limit": 1
        })
        
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
        
        # Include memories if requested
        if kwargs.get("include_memories", True):
            memory_nodes = self.sskg_manager.query({
                "node_types": [NodeType.MEMORY],
                "metadata_filters": {"role_id": role_id},
                "limit": 100
            })
            
            for memory_node in memory_nodes:
                role_data["memories"].append({
                    "content": memory_node.content,
                    "type": memory_node.metadata.get("memory_type", "episodic"),
                    "importance": memory_node.metadata.get("importance", 0.5),
                    "context": memory_node.metadata.get("context", {}),
                    "timestamp": memory_node.metadata.get("timestamp", ""),
                    "confidence": memory_node.confidence
                })
        
        return role_data    

    def update(self, role_id: str, role_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update role data in the SSKG.
        
        Args:
            role_id: ID of the role to update
            role_data: Updated role data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful
        """
        # Find role node
        role_nodes = self.sskg_manager.query({
            "node_types": [NodeType.ROLE],
            "metadata_filters": {"role_id": role_id},
            "limit": 1
        })
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Update role metadata
        updated_metadata = {
            **role_node.metadata,
            "name": role_data.get("name", role_node.metadata.get("name", "")),
            "personality": role_data.get("personality", role_node.metadata.get("personality", {})),
            "cognitive_framework": role_data.get("cognitive_framework", role_node.metadata.get("cognitive_framework", {})),
            "updated_at": datetime.now().isoformat()
        }
        
        return self.sskg_manager.update_node(role_node.id, {
            "content": f"Role: {role_data.get('name', role_id)}",
            "metadata": updated_metadata
        })
    
    def delete(self, role_id: str, **kwargs) -> bool:
        """
        Delete role data from the SSKG.
        
        Args:
            role_id: ID of the role to delete
            **kwargs: Additional parameters
                - delete_memories: Whether to delete associated memories
                
        Returns:
            True if deletion was successful
        """
        # Find role node
        role_nodes = self.sskg_manager.query({
            "node_types": [NodeType.ROLE],
            "metadata_filters": {"role_id": role_id},
            "limit": 1
        })
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Delete associated memories if requested
        if kwargs.get("delete_memories", True):
            memory_nodes = self.sskg_manager.query({
                "node_types": [NodeType.MEMORY],
                "metadata_filters": {"role_id": role_id},
                "limit": 1000
            })
            
            for memory_node in memory_nodes:
                self.sskg_manager.delete_node(memory_node.id)
        
        # Delete role node
        return self.sskg_manager.delete_node(role_node.id)
class WikiAdapter(StorageAdapter):
    """
    Storage adapter for wiki content and structured documentation.
    
    This adapter manages the storage and retrieval of wiki pages,
    documentation, and structured knowledge content.
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
                - author: Author of the page
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored wiki node
        """
        page_id = wiki_data.get("page_id")
        if not page_id:
            raise ValueError("page_id is required for wiki storage")
        
        # Create wiki metadata
        wiki_metadata = {
            "page_id": page_id,
            "title": wiki_data.get("title", ""),
            "tags": wiki_data.get("tags", []),
            "category": wiki_data.get("category", ""),
            "author": wiki_data.get("author", ""),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "wiki"
        }
        
        # Create wiki node
        wiki_node_id = self._create_node(
            node_type=NodeType.WIKI,
            content=wiki_data.get("content", ""),
            confidence=1.0,
            metadata=wiki_metadata
        )
        
        # Create category relation if specified
        category = wiki_data.get("category")
        if category:
            category_node_id = self._get_or_create_category(category)
            self._create_relation(
                source_id=wiki_node_id,
                target_id=category_node_id,
                relation_type=RelationType.PART_OF
            )
        
        # Create tag relations
        tags = wiki_data.get("tags", [])
        for tag in tags:
            tag_node_id = self._get_or_create_tag(tag)
            self._create_relation(
                source_id=wiki_node_id,
                target_id=tag_node_id,
                relation_type=RelationType.RELATED_TO
            )
        
        self.logger.info(f"Stored wiki page {page_id}")
        return wiki_node_id
    
    def _get_or_create_category(self, category: str) -> str:
        """
        Get or create a category node.
        
        Args:
            category: Category name
            
        Returns:
            ID of the category node
        """
        # Check if category already exists
        category_nodes = self.sskg_manager.query({
            "node_types": [NodeType.CONCEPT],
            "metadata_filters": {"concept_type": "category", "name": category},
            "limit": 1
        })
        
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
    
    def _get_or_create_tag(self, tag: str) -> str:
        """
        Get or create a tag node.
        
        Args:
            tag: Tag name
            
        Returns:
            ID of the tag node
        """
        # Check if tag already exists
        tag_nodes = self.sskg_manager.query({
            "node_types": [NodeType.CONCEPT],
            "metadata_filters": {"concept_type": "tag", "name": tag},
            "limit": 1
        })
        
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
            
        Returns:
            Wiki data dictionary or None if not found
        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query({
            "node_types": [NodeType.WIKI],
            "metadata_filters": {"page_id": page_id},
            "limit": 1
        })
        
        if not wiki_nodes:
            return None
        
        wiki_node = wiki_nodes[0]
        return {
            "page_id": page_id,
            "title": wiki_node.metadata.get("title", ""),
            "content": wiki_node.content,
            "tags": wiki_node.metadata.get("tags", []),
            "category": wiki_node.metadata.get("category", ""),
            "author": wiki_node.metadata.get("author", ""),
            "created_at": wiki_node.metadata.get("created_at", ""),
            "updated_at": wiki_node.metadata.get("updated_at", "")
        }    

    def update(self, page_id: str, wiki_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update wiki content in the SSKG.
        
        Args:
            page_id: ID of the wiki page to update
            wiki_data: Updated wiki data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful
        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query({
            "node_types": [NodeType.WIKI],
            "metadata_filters": {"page_id": page_id},
            "limit": 1
        })
        
        if not wiki_nodes:
            return False
        
        wiki_node = wiki_nodes[0]
        
        # Update wiki metadata
        updated_metadata = {
            **wiki_node.metadata,
            "title": wiki_data.get("title", wiki_node.metadata.get("title", "")),
            "tags": wiki_data.get("tags", wiki_node.metadata.get("tags", [])),
            "category": wiki_data.get("category", wiki_node.metadata.get("category", "")),
            "updated_at": datetime.now().isoformat()
        }
        
        return self.sskg_manager.update_node(wiki_node.id, {
            "content": wiki_data.get("content", wiki_node.content),
            "metadata": updated_metadata
        })
    
    def delete(self, page_id: str, **kwargs) -> bool:
        """
        Delete wiki content from the SSKG.
        
        Args:
            page_id: ID of the wiki page to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful
        """
        # Find wiki node
        wiki_nodes = self.sskg_manager.query({
            "node_types": [NodeType.WIKI],
            "metadata_filters": {"page_id": page_id},
            "limit": 1
        })
        
        if not wiki_nodes:
            return False
        
        wiki_node = wiki_nodes[0]
        return self.sskg_manager.delete_node(wiki_node.id)


class SessionAdapter(StorageAdapter):
    """
    Storage adapter for conversation states and session data.
    
    This adapter manages the storage and retrieval of session states,
    conversation history, and user interaction data.
    """
    
    def store(self, session_data: Dict[str, Any], **kwargs) -> str:
        """
        Store session data in the SSKG.
        
        Args:
            session_data: Dictionary containing session information
                - session_id: Unique identifier for the session
                - user_id: ID of the user
                - state: Session state data
                - conversation_history: List of conversation messages
                - context: Additional context data
            **kwargs: Additional parameters
            
        Returns:
            ID of the stored session node
        """
        session_id = session_data.get("session_id")
        if not session_id:
            raise ValueError("session_id is required for session storage")
        
        # Create session metadata
        session_metadata = {
            "session_id": session_id,
            "user_id": session_data.get("user_id", ""),
            "created_at": datetime.now().isoformat(),
            "adapter_type": "session"
        }
        
        # Prepare session content
        session_content = {
            "state": session_data.get("state", {}),
            "conversation_history": session_data.get("conversation_history", []),
            "context": session_data.get("context", {})
        }
        
        # Create session node
        session_node_id = self._create_node(
            node_type=NodeType.SESSION,
            content=json.dumps(session_content),
            confidence=1.0,
            metadata=session_metadata
        )
        
        self.logger.info(f"Stored session {session_id}")
        return session_node_id    

    def retrieve(self, session_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data from the SSKG.
        
        Args:
            session_id: ID of the session to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Session data dictionary or None if not found
        """
        # Find session node
        session_nodes = self.sskg_manager.query({
            "node_types": [NodeType.SESSION],
            "metadata_filters": {"session_id": session_id},
            "limit": 1
        })
        
        if not session_nodes:
            return None
        
        session_node = session_nodes[0]
        
        try:
            session_content = json.loads(session_node.content)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse session content for session {session_id}")
            return None
        
        return {
            "session_id": session_id,
            "user_id": session_node.metadata.get("user_id", ""),
            "state": session_content.get("state", {}),
            "conversation_history": session_content.get("conversation_history", []),
            "context": session_content.get("context", {}),
            "created_at": session_node.metadata.get("created_at", ""),
            "updated_at": session_node.metadata.get("updated_at", "")
        }
    
    def update(self, session_id: str, session_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update session data in the SSKG.
        
        Args:
            session_id: ID of the session to update
            session_data: Updated session data
            **kwargs: Additional parameters
            
        Returns:
            True if update was successful
        """
        # Find session node
        session_nodes = self.sskg_manager.query({
            "node_types": [NodeType.SESSION],
            "metadata_filters": {"session_id": session_id},
            "limit": 1
        })
        
        if not session_nodes:
            return False
        
        session_node = session_nodes[0]
        
        # Prepare updated session content
        session_content = {
            "state": session_data.get("state", {}),
            "conversation_history": session_data.get("conversation_history", []),
            "context": session_data.get("context", {})
        }
        
        # Update session metadata
        updated_metadata = {
            **session_node.metadata,
            "updated_at": datetime.now().isoformat()
        }
        
        return self.sskg_manager.update_node(session_node.id, {
            "content": json.dumps(session_content),
            "metadata": updated_metadata
        })
    
    def delete(self, session_id: str, **kwargs) -> bool:
        """
        Delete session data from the SSKG.
        
        Args:
            session_id: ID of the session to delete
            **kwargs: Additional parameters
            
        Returns:
            True if deletion was successful
        """
        # Find session node
        session_nodes = self.sskg_manager.query({
            "node_types": [NodeType.SESSION],
            "metadata_filters": {"session_id": session_id},
            "limit": 1
        })
        
        if not session_nodes:
            return False
        
        session_node = session_nodes[0]
        return self.sskg_manager.delete_node(session_node.id)


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
            "session": SessionAdapter(sskg_manager)
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
    
    def store_data(self, adapter_type: str, data: Any, **kwargs) -> Optional[str]:
        """
        Store data using the specified adapter.
        
        Args:
            adapter_type: Type of adapter to use
            data: Data to store
            **kwargs: Additional parameters
            
        Returns:
            ID of stored data or None if failed
        """
        adapter = self.get_adapter(adapter_type)
        if not adapter:
            self.logger.error(f"Unknown adapter type: {adapter_type}")
            return None
        
        try:
            return adapter.store(data, **kwargs)
        except Exception as e:
            self.logger.error(f"Error storing data with {adapter_type} adapter: {e}")
            return None
    
    def retrieve_data(self, adapter_type: str, identifier: str, **kwargs) -> Optional[Any]:
        """
        Retrieve data using the specified adapter.
        
        Args:
            adapter_type: Type of adapter to use
            identifier: Identifier of data to retrieve
            **kwargs: Additional parameters
            
        Returns:
            Retrieved data or None if not found
        """
        adapter = self.get_adapter(adapter_type)
        if not adapter:
            self.logger.error(f"Unknown adapter type: {adapter_type}")
            return None
        
        try:
            return adapter.retrieve(identifier, **kwargs)
        except Exception as e:
            self.logger.error(f"Error retrieving data with {adapter_type} adapter: {e}")
            return None