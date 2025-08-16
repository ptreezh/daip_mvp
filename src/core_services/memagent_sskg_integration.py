"""@Time    : 2025-07-23 12:00:00
@Author  : DAIP-LIVE Team
@File    : memagent_sskg_integration.py
@Description:
    Integration service between MemAgent and SSKG that provides unified memory
    retrieval interface, memory-to-knowledge transformation pipeline, and
    cross-referencing between memory systems.
"""
import logging
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel

from src.core_services.enhanced_sskg_manager import (
    EnhancedSSKGManager,
    KnowledgeNode,
    KnowledgeQuery,
    KnowledgeRelation,
    NodeType,
    RelationType,
)
from src.core_services.memory_agent import MemAgent, Memory, MemoryQuery, MemoryType

logger = logging.getLogger(__name__)


class MemoryKnowledgeMapping(BaseModel):
    """Mapping between memory and knowledge representations."""

    memory_id: str
    knowledge_node_id: str
    mapping_type: str  # "direct", "derived", "consolidated"
    confidence: float
    created_at: datetime
    metadata: dict[str, Any] = {}


class UnifiedMemoryInterface:
    """Unified interface for memory retrieval across MemAgent and SSKG systems.
    
    Provides seamless access to memories stored in both systems with
    automatic cross-referencing and knowledge transformation.
    """

    def __init__(self, mem_agent: MemAgent, sskg_manager: EnhancedSSKGManager):
        """Initialize the unified memory interface.
        
        Args:
            mem_agent: The MemAgent instance
            sskg_manager: The Enhanced SSKG Manager instance

        """
        self.mem_agent = mem_agent
        self.sskg_manager = sskg_manager

        # Mapping between memories and knowledge nodes
<<<<<<< HEAD
        self.memory_knowledge_mappings: Dict[str, MemoryKnowledgeMapping] = {}

=======
        self.memory_knowledge_mappings: dict[str, MemoryKnowledgeMapping] = {}
        
>>>>>>> feature/core-services-refactor
        # Statistics
        self.integration_stats = {
            "memories_transformed": 0,
            "knowledge_nodes_created": 0,
            "cross_references_created": 0,
            "unified_queries": 0
        }

        logger.info("UnifiedMemoryInterface initialized")

    def unified_memory_retrieval(
        self,
        context: str,
        memory_types: Optional[list[MemoryType]] = None,
        source_id: Optional[str] = None,
        min_importance: float = 0.0,
        include_knowledge: bool = True,
        limit: int = 10
<<<<<<< HEAD
    ) -> List[Memory]:
=======
    ) -> list[Memory]:
>>>>>>> feature/core-services-refactor
        """Unified memory retrieval that searches both MemAgent and SSKG.
        
        Args:
            context: The context to search for
            memory_types: Optional list of memory types to filter
            source_id: Optional source ID to filter
            min_importance: Minimum importance threshold
            include_knowledge: Whether to include knowledge nodes as memories
            limit: Maximum number of memories to return
            
        Returns:
            List of unified memories from both systems

        """
        self.integration_stats["unified_queries"] += 1

        # Retrieve memories from MemAgent
        mem_query = MemoryQuery(
            content=context,
            memory_types=memory_types,
            source_id=source_id,
            min_importance=min_importance,
            limit=limit
        )

        mem_agent_memories = self.mem_agent.retrieve_memories(context, mem_query)

        # Retrieve related knowledge from SSKG if requested
        sskg_memories = []
        if include_knowledge:
            sskg_memories = self._retrieve_knowledge_as_memories(
                context, memory_types, source_id, min_importance, limit
            )

        # Combine and deduplicate results
        all_memories = mem_agent_memories + sskg_memories

        # Remove duplicates based on content similarity
        unique_memories = self._deduplicate_memories(all_memories)

        # Sort by relevance and importance
        unique_memories.sort(
            key=lambda m: (m.importance + m.recency) / 2,
            reverse=True
        )

        return unique_memories[:limit]

    def _retrieve_knowledge_as_memories(
        self,
        context: str,
        memory_types: Optional[list[MemoryType]],
        source_id: Optional[str],
        min_importance: float,
        limit: int
    ) -> list[Memory]:
        """Retrieve knowledge nodes from SSKG and convert to Memory objects."""
        # Build SSKG query
        node_types = [NodeType.MEMORY, NodeType.FACT, NodeType.CONCEPT]

        metadata_filters = {}
        if source_id:
            metadata_filters["owner_id"] = source_id

        sskg_query = KnowledgeQuery(
            node_types=node_types,
            content_query=context,
            min_confidence=min_importance,
            metadata_filters=metadata_filters,
            limit=limit
        )

        # Query SSKG
        knowledge_nodes = self.sskg_manager.query(sskg_query)

        # Convert knowledge nodes to Memory objects
        memories = []
        for node in knowledge_nodes:
            try:
                # Determine memory type from node metadata or type
                memory_type = self._infer_memory_type_from_node(node)

                # Filter by memory type if specified
                if memory_types and memory_type not in memory_types:
                    continue

                # Create Memory object
                memory = Memory(
                    id=f"sskg_{node.id}",
                    content=node.content,
                    memory_type=memory_type,
                    source_id=node.metadata.get("owner_id", "sskg"),
                    importance=node.confidence,
                    recency=self._calculate_recency_from_node(node),
                    created_at=node.created_at,
                    metadata={
                        **node.metadata,
                        "source_system": "sskg",
                        "original_node_id": node.id,
                        "node_type": node.node_type.value
                    }
                )

                memories.append(memory)

            except Exception as e:
                logger.error(f"Error converting knowledge node to memory: {e}")

        return memories

    def _infer_memory_type_from_node(self, node: KnowledgeNode) -> MemoryType:
        """Infer memory type from knowledge node."""
        # Check metadata first
        if "memory_type" in node.metadata:
            try:
                return MemoryType(node.metadata["memory_type"])
            except ValueError:
                pass

        # Infer from node type
        if node.node_type == NodeType.MEMORY:
            return MemoryType.EPISODIC  # Default for memory nodes
        elif node.node_type == NodeType.FACT or node.node_type == NodeType.CONCEPT:
            return MemoryType.SEMANTIC
        elif node.node_type == NodeType.EVENT:
            return MemoryType.EPISODIC
        else:
            return MemoryType.SEMANTIC  # Default fallback

    def _calculate_recency_from_node(self, node: KnowledgeNode) -> float:
        """Calculate recency score from knowledge node."""
        # Simple recency calculation based on update time
        now = datetime.now()
        time_diff = now - node.updated_at

        # Convert to days
        days_old = time_diff.total_seconds() / (24 * 3600)

        # Calculate recency score (1.0 for very recent, approaching 0 for old)
        if days_old <= 1:
            return 1.0
        elif days_old <= 7:
            return 0.8
        elif days_old <= 30:
            return 0.6
        elif days_old <= 90:
            return 0.4
        else:
            return 0.2
<<<<<<< HEAD

    def _deduplicate_memories(self, memories: List[Memory]) -> List[Memory]:
=======
    
    def _deduplicate_memories(self, memories: list[Memory]) -> list[Memory]:
>>>>>>> feature/core-services-refactor
        """Remove duplicate memories based on content similarity."""
        unique_memories = []
        seen_contents = set()

        for memory in memories:
            # Simple deduplication based on content hash
            content_hash = hash(memory.content.lower().strip())

            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_memories.append(memory)

        return unique_memories

    def transform_memory_to_knowledge(
        self,
        memory: Memory,
        create_relations: bool = True
    ) -> Optional[str]:
        """Transform a memory into a knowledge node in SSKG.
        
        Args:
            memory: The memory to transform
            create_relations: Whether to create relations to existing knowledge
            
        Returns:
            ID of the created knowledge node, or None if failed

        """
        try:
            # Determine appropriate node type
            node_type = self._memory_type_to_node_type(memory.memory_type)

            # Create knowledge node
            knowledge_node = KnowledgeNode(
                id=f"knowledge_{memory.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                node_type=node_type,
                content=memory.content,
                confidence=memory.importance,
                metadata={
                    **memory.metadata,
                    "source_memory_id": memory.id,
                    "memory_type": memory.memory_type.value,
                    "owner_id": memory.source_id,
                    "recency": memory.recency,
                    "access_count": memory.access_count,
                    "transformation_time": datetime.now().isoformat()
                }
            )

            # Add node to SSKG
            node_id = self.sskg_manager.add_node(knowledge_node)

            # Create mapping
            mapping = MemoryKnowledgeMapping(
                memory_id=memory.id,
                knowledge_node_id=node_id,
                mapping_type="direct",
                confidence=memory.importance,
                created_at=datetime.now()
            )

            self.memory_knowledge_mappings[memory.id] = mapping

            # Create relations to existing knowledge if requested
            if create_relations:
                self._create_knowledge_relations(node_id, memory)

            # Update statistics
            self.integration_stats["memories_transformed"] += 1
            self.integration_stats["knowledge_nodes_created"] += 1

            logger.debug(f"Transformed memory {memory.id} to knowledge node {node_id}")
            return node_id

        except Exception as e:
            logger.error(f"Error transforming memory to knowledge: {e}")
            return None

    def _memory_type_to_node_type(self, memory_type: MemoryType) -> NodeType:
        """Convert memory type to appropriate node type."""
        mapping = {
            MemoryType.EPISODIC: NodeType.EVENT,
            MemoryType.SEMANTIC: NodeType.FACT,
            MemoryType.PROCEDURAL: NodeType.CONCEPT,
            MemoryType.META: NodeType.CONCEPT
        }
        return mapping.get(memory_type, NodeType.FACT)

    def _create_knowledge_relations(self, node_id: str, memory: Memory):
        """Create relations between the new knowledge node and existing knowledge."""
        try:
            # Find related knowledge nodes
            related_query = KnowledgeQuery(
                content_query=memory.content,
                limit=5,
                min_confidence=0.5
            )

            related_nodes = self.sskg_manager.query(related_query)

            # Create relations to related nodes
            for related_node in related_nodes:
                if related_node.id != node_id:  # Don't relate to self
                    # Determine relation type based on content similarity and types
                    relation_type = self._determine_relation_type(memory, related_node)

                    if relation_type:
                        relation = KnowledgeRelation(
                            source_id=node_id,
                            target_id=related_node.id,
                            relation_type=relation_type,
                            confidence=0.7,  # Default confidence for auto-created relations
                            metadata={
                                "auto_created": True,
                                "creation_time": datetime.now().isoformat()
                            }
                        )

                        self.sskg_manager.add_relation(relation)
                        self.integration_stats["cross_references_created"] += 1

        except Exception as e:
            logger.error(f"Error creating knowledge relations: {e}")

    def _determine_relation_type(self, memory: Memory, related_node: KnowledgeNode) -> Optional[RelationType]:
        """Determine the appropriate relation type between memory and related node."""
        # Simple heuristic-based relation type determination
        # In a real implementation, this would use more sophisticated NLP

        memory_content = memory.content.lower()
        node_content = related_node.content.lower()

        # Check for common relation patterns
        if any(word in memory_content for word in ["because", "due to", "caused by"]):
            if any(word in node_content for word in ["result", "effect", "consequence"]):
                return RelationType.CAUSES

        if any(word in memory_content for word in ["part of", "component", "element"]):
            return RelationType.PART_OF

        if any(word in memory_content for word in ["similar", "like", "related"]):
            return RelationType.RELATED_TO

        if any(word in memory_content for word in ["supports", "confirms", "validates"]):
            return RelationType.SUPPORTS

        if any(word in memory_content for word in ["contradicts", "opposes", "disagrees"]):
            return RelationType.CONTRADICTS

        # Default to related_to for similar content
        return RelationType.RELATED_TO
<<<<<<< HEAD

    def create_cross_references(self, memory_id: str, knowledge_node_ids: List[str]):
=======
    
    def create_cross_references(self, memory_id: str, knowledge_node_ids: list[str]):
>>>>>>> feature/core-services-refactor
        """Create explicit cross-references between memory and knowledge nodes."""
        try:
            # Get the memory
            memory_query = MemoryQuery(content="", limit=100)
            memories = self.mem_agent.retrieve_memories("", memory_query)
            target_memory = next((m for m in memories if m.id == memory_id), None)

            if not target_memory:
                logger.warning(f"Memory {memory_id} not found for cross-referencing")
                return

            # Create references to each knowledge node
            for node_id in knowledge_node_ids:
                # Check if node exists
                node_query = KnowledgeQuery(limit=1)
                nodes = self.sskg_manager.query(node_query)
                target_node = next((n for n in nodes if n.id == node_id), None)

                if target_node:
                    # Create bidirectional reference
                    relation = KnowledgeRelation(
                        source_id=f"mem_{memory_id}",
                        target_id=node_id,
                        relation_type=RelationType.REFERENCES,
                        confidence=0.9,
                        metadata={
                            "cross_reference": True,
                            "memory_id": memory_id,
                            "creation_time": datetime.now().isoformat()
                        }
                    )

                    self.sskg_manager.add_relation(relation)
                    self.integration_stats["cross_references_created"] += 1

                    logger.debug(f"Created cross-reference: memory {memory_id} -> node {node_id}")

        except Exception as e:
            logger.error(f"Error creating cross-references: {e}")

    def get_memory_knowledge_mapping(self, memory_id: str) -> Optional[MemoryKnowledgeMapping]:
        """Get the knowledge mapping for a memory."""
        return self.memory_knowledge_mappings.get(memory_id)
<<<<<<< HEAD

    def get_related_knowledge_for_memory(self, memory_id: str) -> List[KnowledgeNode]:
=======
    
    def get_related_knowledge_for_memory(self, memory_id: str) -> list[KnowledgeNode]:
>>>>>>> feature/core-services-refactor
        """Get knowledge nodes related to a specific memory."""
        try:
            # Get the mapping
            mapping = self.get_memory_knowledge_mapping(memory_id)
            if not mapping:
                return []

            # Query for related knowledge nodes
            related_query = KnowledgeQuery(
                limit=10,
                include_relations=True
            )

            all_nodes = self.sskg_manager.query(related_query)

            # Filter for nodes related to the mapped knowledge node
            related_nodes = []
            for node in all_nodes:
                if node.id == mapping.knowledge_node_id:
                    continue  # Skip the directly mapped node

                # Check if there's a relation (simplified check)
                # In a real implementation, this would use the graph structure
                if self._nodes_are_related(mapping.knowledge_node_id, node.id):
                    related_nodes.append(node)

            return related_nodes

        except Exception as e:
            logger.error(f"Error getting related knowledge for memory: {e}")
            return []

    def _nodes_are_related(self, node1_id: str, node2_id: str) -> bool:
        """Check if two nodes are related in the knowledge graph."""
        # Simplified implementation - in reality would check graph structure
        return True  # Placeholder

    def sync_memory_to_knowledge(self, memory_id: str) -> bool:
        """Synchronize a memory with its corresponding knowledge representation."""
        try:
            # Get the memory
            memory_query = MemoryQuery(content="", limit=100)
            memories = self.mem_agent.retrieve_memories("", memory_query)
            target_memory = next((m for m in memories if m.id == memory_id), None)

            if not target_memory:
                logger.warning(f"Memory {memory_id} not found for synchronization")
                return False

            # Get the mapping
            mapping = self.get_memory_knowledge_mapping(memory_id)
            if not mapping:
                # Create new knowledge node if no mapping exists
                node_id = self.transform_memory_to_knowledge(target_memory)
                return node_id is not None

            # Update existing knowledge node
            node_query = KnowledgeQuery(limit=1)
            nodes = self.sskg_manager.query(node_query)
            target_node = next((n for n in nodes if n.id == mapping.knowledge_node_id), None)

            if target_node:
                # Update node with current memory data
                updates = {
                    "content": target_memory.content,
                    "confidence": target_memory.importance,
                    "metadata": {
                        **target_node.metadata,
                        "recency": target_memory.recency,
                        "access_count": target_memory.access_count,
                        "last_sync": datetime.now().isoformat()
                    }
                }

                success = self.sskg_manager.update_node(mapping.knowledge_node_id, updates)

                if success:
                    logger.debug(f"Synchronized memory {memory_id} with knowledge node {mapping.knowledge_node_id}")

                return success

            return False

        except Exception as e:
            logger.error(f"Error synchronizing memory to knowledge: {e}")
            return False
<<<<<<< HEAD

    def get_integration_stats(self) -> Dict[str, Any]:
=======
    
    def get_integration_stats(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get integration statistics."""
        return {
            **self.integration_stats,
            "total_mappings": len(self.memory_knowledge_mappings),
            "mapping_details": {
                mapping_id: {
                    "memory_id": mapping.memory_id,
                    "knowledge_node_id": mapping.knowledge_node_id,
                    "mapping_type": mapping.mapping_type,
                    "confidence": mapping.confidence
                }
                for mapping_id, mapping in self.memory_knowledge_mappings.items()
            }
        }
