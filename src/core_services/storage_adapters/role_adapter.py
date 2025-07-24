"""
Role Memory Adapter for the SSKG.

This module implements the storage adapter for virtual role memories and identities.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from src.core_services.enhanced_sskg_manager import (
        KnowledgeQuery,
        NodeType,
        RelationType
    )
except ImportError:
    # For testing purposes
    from enum import Enum
    
    class NodeType(str, Enum):
        ROLE = "role"
        MEMORY = "memory"
    
    class RelationType(str, Enum):
        OWNED_BY = "owned_by"
    
    class KnowledgeQuery:
        pass

from .base import StorageAdapter


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
        # Find role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id, "adapter_type": "role_memory"},
            limit=1
        ))
        
        if not role_nodes:
            return None
        
        role_node = role_nodes[0]
        role_data = {
            "role_id": role_id,
            "name": role_node.metadata.get("name", ""),
            "personality": role_node.metadata.get("personality", {}),
            "cognitive_framework": role_node.metadata.get("cognitive_framework", {})
        }
        
        # Include memories if requested
        include_memories = kwargs.get("include_memories", True)
        if include_memories:
            role_data["memories"] = self._retrieve_role_memories(role_id)
        
        return role_data
    
    def _retrieve_role_memories(self, role_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a role.
        
        Args:
            role_id: ID of the role
            
        Returns:
            List of memory dictionaries
        """
        memory_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters={"role_id": role_id, "adapter_type": "role_memory"},
            limit=1000
        ))
        
        memories = []
        for node in memory_nodes:
            memories.append({
                "content": node.content,
                "type": node.metadata.get("memory_type", "episodic"),
                "importance": node.metadata.get("importance", 0.5),
                "context": node.metadata.get("context", {}),
                "timestamp": node.metadata.get("timestamp", ""),
                "confidence": node.confidence
            })
        
        return memories
    
    def update(self, role_id: str, role_data: Dict[str, Any], **kwargs) -> bool:
        """
        Update role data in the SSKG.
        
        Args:
            role_id: ID of the role to update
            role_data: Updated role data
            **kwargs: Additional parameters
                - update_memories: Whether to update role memories (default: False)
            
        Returns:
            True if update was successful, False otherwise
        """
        # Find role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id, "adapter_type": "role_memory"},
            limit=1
        ))
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Update role metadata
        updated_metadata = dict(role_node.metadata)
        if "name" in role_data:
            updated_metadata["name"] = role_data["name"]
        if "personality" in role_data:
            updated_metadata["personality"] = role_data["personality"]
        if "cognitive_framework" in role_data:
            updated_metadata["cognitive_framework"] = role_data["cognitive_framework"]
        
        # Update role content if name changed
        updated_content = role_node.content
        if "name" in role_data:
            updated_content = f"Role: {role_data['name']}"
        
        # Update role node
        success = self.sskg_manager.update_node(role_node.id, {
            "content": updated_content,
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
        # Find role node
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"role_id": role_id, "adapter_type": "role_memory"},
            limit=1
        ))
        
        if not role_nodes:
            return False
        
        role_node = role_nodes[0]
        
        # Delete associated memories if requested
        delete_memories = kwargs.get("delete_memories", True)
        if delete_memories:
            memory_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.MEMORY],
                metadata_filters={"role_id": role_id, "adapter_type": "role_memory"},
                limit=1000
            ))
            
            for memory_node in memory_nodes:
                self.sskg_manager.delete_node(memory_node.id)
        
        # Delete role node
        success = self.sskg_manager.delete_node(role_node.id)
        
        if success:
            self.logger.info(f"Deleted role {role_id}")
        
        return success
    
    def list_all(self, **kwargs) -> List[str]:
        """
        List all role IDs.
        
        Args:
            **kwargs: Additional parameters
            
        Returns:
            List of role IDs
        """
        role_nodes = self.sskg_manager.query(KnowledgeQuery(
            node_types=[NodeType.ROLE],
            metadata_filters={"adapter_type": "role_memory"},
            limit=1000
        ))
        
        return [node.metadata.get("role_id", "") for node in role_nodes if node.metadata.get("role_id")]