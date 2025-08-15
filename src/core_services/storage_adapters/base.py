"""Base classes for storage adapters.

This module defines the abstract base class for all storage adapters
and the manager class that coordinates them.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

try:
    from src.core_services.enhanced_sskg_manager import (
        EnhancedSSKGManager,
        KnowledgeNode,
        KnowledgeRelation,
        NodeType,
        RelationType,
    )
except ImportError:
    # For testing purposes
    from datetime import datetime
    from enum import Enum

    from pydantic import BaseModel, Field
    
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
    
    class KnowledgeNode(BaseModel):
        """Base model for all knowledge nodes in the SSKG."""
        id: str
        node_type: NodeType
        content: str
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)
        confidence: float = 1.0
        metadata: dict[str, Any] = {}
        version: int = 1
    
    class KnowledgeRelation(BaseModel):
        """Model for relationships between knowledge nodes."""
        source_id: str
        target_id: str
        relation_type: RelationType
        confidence: float = 1.0
        metadata: dict[str, Any] = {}
        created_at: datetime = Field(default_factory=datetime.now)


class StorageAdapter(ABC):
    """Abstract base class for all storage adapters.
    
    Storage adapters provide a consistent interface for mapping domain-specific
    data structures to SSKG representations while maintaining semantic integrity.
    """
    
    def __init__(self, sskg_manager: 'EnhancedSSKGManager'):
        """Initialize the storage adapter.
        
        Args:
            sskg_manager: The SSKG manager to use for storage operations
        """
        self.sskg_manager = sskg_manager
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def store(self, data: Any, **kwargs) -> str:
        """Store data in the SSKG.
        
        Args:
            data: The data to store
            **kwargs: Additional parameters for storage
            
        Returns:
            ID of the stored node
        """
        pass
    
    @abstractmethod
    def retrieve(self, identifier: str, **kwargs) -> Optional[Any]:
        """Retrieve data from the SSKG.
        
        Args:
            identifier: The identifier of the data to retrieve
            **kwargs: Additional parameters for retrieval
            
        Returns:
            Retrieved data or None if not found
        """
        pass
    
    @abstractmethod
    def update(self, identifier: str, data: Any, **kwargs) -> bool:
        """Update data in the SSKG.
        
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
        """Delete data from the SSKG.
        
        Args:
            identifier: The identifier of the data to delete
            **kwargs: Additional parameters for deletion
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_all(self, **kwargs) -> list[str]:
        """List all identifiers of data stored by this adapter.
        
        Args:
            **kwargs: Additional parameters for listing
            
        Returns:
            List of identifiers
        """
        pass
    
    def _create_node(self, node_type: NodeType, content: str, 
                    confidence: float = 1.0, metadata: dict[str, Any] = None) -> str:
        """Create a node in the SSKG.
        
        Args:
            node_type: Type of the node
            content: Content of the node
            confidence: Confidence score of the node
            metadata: Additional metadata for the node
            
        Returns:
            ID of the created node
        """
        node = KnowledgeNode(
            id="",  # Will be assigned by SSKG manager
            node_type=node_type,
            content=content,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return self.sskg_manager.add_node(node)
    
    def _create_relation(self, source_id: str, target_id: str, 
                        relation_type: RelationType, 
                        confidence: float = 1.0,
                        metadata: dict[str, Any] = None) -> bool:
        """Create a relation between two nodes in the SSKG.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of the relation
            confidence: Confidence score of the relation
            metadata: Additional metadata for the relation
            
        Returns:
            True if the relation was created successfully, False otherwise
        """
        relation = KnowledgeRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        return self.sskg_manager.add_relation(relation)


class StorageAdapterManager:
    """Manager for all storage adapters.
    
    This class provides a unified interface for accessing different storage adapters
    and managing their lifecycle.
    """
    
    def __init__(self, sskg_manager: 'EnhancedSSKGManager'):
        """Initialize the storage adapter manager.
        
        Args:
            sskg_manager: The SSKG manager to use for storage operations
        """
        self.sskg_manager = sskg_manager
        self.adapters = {}
        self.logger = logging.getLogger(__name__)
        
        # Register default adapters
        from .memory_bank_adapter import MemoryBankAdapter
        from .project_adapter import ProjectAdapter
        from .role_adapter import RoleMemoryAdapter
        from .session_adapter import SessionAdapter
        from .wiki_adapter import WikiAdapter
        
        self.register_adapter("role_memory", RoleMemoryAdapter(sskg_manager))
        self.register_adapter("wiki", WikiAdapter(sskg_manager))
        self.register_adapter("session", SessionAdapter(sskg_manager))
        self.register_adapter("project", ProjectAdapter(sskg_manager))
        self.register_adapter("memory_bank", MemoryBankAdapter(sskg_manager))
    
    def get_adapter(self, adapter_type: str) -> Optional[StorageAdapter]:
        """Get a storage adapter by type.
        
        Args:
            adapter_type: Type of the adapter
            
        Returns:
            Storage adapter or None if not found
        """
        return self.adapters.get(adapter_type)
    
    def register_adapter(self, adapter_type: str, adapter: StorageAdapter):
        """Register a new storage adapter.
        
        Args:
            adapter_type: Type of the adapter
            adapter: Storage adapter instance
        """
        self.adapters[adapter_type] = adapter
        self.logger.info(f"Registered storage adapter: {adapter_type}")
    
    def list_adapters(self) -> list[str]:
        """List all registered adapter types.
        
        Returns:
            List of adapter types
        """
        return list(self.adapters.keys())