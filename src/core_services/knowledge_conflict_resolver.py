"""
Knowledge Conflict Resolution for the Semantic Structured Knowledge Graph (SSKG).

This module implements sophisticated strategies to detect and resolve conflicts
between knowledge facts in the SSKG, ensuring knowledge coherence and consistency.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

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
    
    class KnowledgeNode(BaseModel):
        """Base model for all knowledge nodes in the SSKG."""
        id: str
        node_type: NodeType
        content: str
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)
        confidence: float = 1.0
        metadata: Dict[str, Any] = {}
        version: int = 1
    
    class KnowledgeRelation(BaseModel):
        """Model for relationships between knowledge nodes."""
        source_id: str
        target_id: str
        relation_type: RelationType
        confidence: float = 1.0
        metadata: Dict[str, Any] = {}
        created_at: datetime = Field(default_factory=datetime.now)

logger = logging.getLogger(__name__)


class ConflictType(str, Enum):
    """Types of conflicts that can occur between knowledge facts."""
    DIRECT_CONTRADICTION = "direct_contradiction"  # Facts directly contradict each other
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  # Facts are inconsistent across time
    CONFIDENCE_VARIATION = "confidence_variation"  # Same fact with different confidence levels
    SOURCE_DISAGREEMENT = "source_disagreement"  # Different sources disagree on a fact
    PARTIAL_OVERLAP = "partial_overlap"  # Facts partially overlap with inconsistencies
    SEMANTIC_DRIFT = "semantic_drift"  # Facts have drifted in meaning over time


class ResolutionStrategy(str, Enum):
    """Strategies for resolving conflicts between knowledge facts."""
    HIGHEST_CONFIDENCE = "highest_confidence"  # Choose fact with highest confidence
    MOST_RECENT = "most_recent"  # Choose most recent fact
    SOURCE_RELIABILITY = "source_reliability"  # Choose fact from most reliable source
    MAJORITY_VOTE = "majority_vote"  # Choose fact supported by most sources
    SYNTHESIS = "synthesis"  # Create a new fact that synthesizes conflicting facts
    HUMAN_RESOLUTION = "human_resolution"  # Flag for human review and resolution


class ConflictDetectionResult(BaseModel):
    """Result of conflict detection between knowledge facts."""
    conflict_type: ConflictType
    conflicting_nodes: List[str]  # List of conflicting node IDs
    confidence: float  # Confidence in the conflict detection
    description: str  # Human-readable description of the conflict
    metadata: Dict[str, Any] = {}


class ConflictResolutionResult(BaseModel):
    """Result of conflict resolution between knowledge facts."""
    resolved_node_id: str  # ID of the resolved node
    resolution_strategy: ResolutionStrategy
    conflicting_node_ids: List[str]  # IDs of the original conflicting nodes
    confidence: float  # Confidence in the resolution
    reasoning: str  # Explanation of the resolution process
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}


class KnowledgeConflictResolver:
    """
    Resolver for conflicts between knowledge facts in the SSKG.
    
    This class implements sophisticated strategies to detect and resolve conflicts
    between knowledge facts, ensuring knowledge coherence and consistency.
    """
    
    def __init__(self, sskg_manager: EnhancedSSKGManager):
        """
        Initialize the knowledge conflict resolver.
        
        Args:
            sskg_manager: The SSKG manager to use for knowledge operations
        """
        self.sskg_manager = sskg_manager
        self.logger = logging.getLogger(__name__)
        
        # Register resolution strategies
        self.resolution_strategies = {
            ResolutionStrategy.HIGHEST_CONFIDENCE: self._resolve_by_highest_confidence,
            ResolutionStrategy.MOST_RECENT: self._resolve_by_most_recent,
            ResolutionStrategy.SOURCE_RELIABILITY: self._resolve_by_source_reliability,
            ResolutionStrategy.MAJORITY_VOTE: self._resolve_by_majority_vote,
            ResolutionStrategy.SYNTHESIS: self._resolve_by_synthesis,
        }
        
        # Source reliability rankings (higher is more reliable)
        self.source_reliability = {
            "human_verified": 5.0,
            "expert_consensus": 4.5,
            "primary_source": 4.0,
            "verified_database": 3.5,
            "reputable_publication": 3.0,
            "expert_opinion": 2.5,
            "ai_generated": 2.0,
            "unverified_source": 1.0,
        }
    
    def detect_conflicts(self, node_id: str) -> List[ConflictDetectionResult]:
        """
        Detect conflicts between a knowledge node and existing knowledge.
        
        Args:
            node_id: ID of the node to check for conflicts
            
        Returns:
            List of detected conflicts
        """
        node = self.sskg_manager.get_node(node_id)
        if not node:
            self.logger.error(f"Cannot detect conflicts: node {node_id} does not exist")
            return []
        
        # Only check for conflicts in fact nodes
        if node.node_type != NodeType.FACT:
            return []
        
        conflicts = []
        
        # Check for direct contradictions using semantic similarity
        semantic_conflicts = self._detect_semantic_conflicts(node)
        conflicts.extend(semantic_conflicts)
        
        # Check for temporal inconsistencies
        temporal_conflicts = self._detect_temporal_conflicts(node)
        conflicts.extend(temporal_conflicts)
        
        # Check for source disagreements
        source_conflicts = self._detect_source_conflicts(node)
        conflicts.extend(source_conflicts)
        
        return conflicts
    
    def _detect_semantic_conflicts(self, node: KnowledgeNode) -> List[ConflictDetectionResult]:
        """
        Detect semantic conflicts between a node and existing knowledge.
        
        Args:
            node: The node to check for conflicts
            
        Returns:
            List of detected semantic conflicts
        """
        conflicts = []
        
        # Use vector search to find semantically similar nodes
        similar_nodes = self.sskg_manager.query({
            "node_types": [NodeType.FACT],
            "content_query": node.content,
            "limit": 10
        })
        
        for similar_node in similar_nodes:
            # Skip self
            if similar_node.id == node.id:
                continue
            
            # Check for direct contradictions
            contradiction_score = self._calculate_contradiction_score(node, similar_node)
            if contradiction_score > 0.7:  # Threshold for contradiction
                conflicts.append(ConflictDetectionResult(
                    conflict_type=ConflictType.DIRECT_CONTRADICTION,
                    conflicting_nodes=[node.id, similar_node.id],
                    confidence=contradiction_score,
                    description=f"Direct contradiction detected between facts: '{node.content}' and '{similar_node.content}'",
                    metadata={
                        "similarity_score": contradiction_score,
                        "detection_method": "semantic_similarity"
                    }
                ))
            
            # Check for partial overlaps
            elif contradiction_score > 0.3:  # Threshold for partial overlap
                conflicts.append(ConflictDetectionResult(
                    conflict_type=ConflictType.PARTIAL_OVERLAP,
                    conflicting_nodes=[node.id, similar_node.id],
                    confidence=contradiction_score,
                    description=f"Partial overlap with inconsistencies detected between facts: '{node.content}' and '{similar_node.content}'",
                    metadata={
                        "similarity_score": contradiction_score,
                        "detection_method": "semantic_similarity"
                    }
                ))
        
        return conflicts
    
    def _detect_temporal_conflicts(self, node: KnowledgeNode) -> List[ConflictDetectionResult]:
        """
        Detect temporal inconsistencies between a node and existing knowledge.
        
        Args:
            node: The node to check for conflicts
            
        Returns:
            List of detected temporal conflicts
        """
        conflicts = []
        
        # Extract temporal information from node content and metadata
        node_temporal_info = self._extract_temporal_info(node)
        if not node_temporal_info:
            return []
        
        # Find nodes with overlapping temporal context
        temporal_nodes = self.sskg_manager.query({
            "node_types": [NodeType.FACT],
            "metadata_filters": {
                "temporal_context": {"$exists": True}
            },
            "limit": 20
        })
        
        for temporal_node in temporal_nodes:
            # Skip self
            if temporal_node.id == node.id:
                continue
            
            # Extract temporal information
            other_temporal_info = self._extract_temporal_info(temporal_node)
            if not other_temporal_info:
                continue
            
            # Check for temporal inconsistencies
            if self._has_temporal_conflict(node_temporal_info, other_temporal_info):
                # Check if content is semantically related
                similarity_score = self._calculate_similarity_score(node, temporal_node)
                if similarity_score > 0.5:  # Threshold for semantic relatedness
                    conflicts.append(ConflictDetectionResult(
                        conflict_type=ConflictType.TEMPORAL_INCONSISTENCY,
                        conflicting_nodes=[node.id, temporal_node.id],
                        confidence=similarity_score * 0.8,  # Adjust confidence
                        description=f"Temporal inconsistency detected between facts: '{node.content}' and '{temporal_node.content}'",
                        metadata={
                            "similarity_score": similarity_score,
                            "node_temporal_info": node_temporal_info,
                            "other_temporal_info": other_temporal_info,
                            "detection_method": "temporal_analysis"
                        }
                    ))
        
        return conflicts
    
    def _detect_source_conflicts(self, node: KnowledgeNode) -> List[ConflictDetectionResult]:
        """
        Detect source disagreements between a node and existing knowledge.
        
        Args:
            node: The node to check for conflicts
            
        Returns:
            List of detected source conflicts
        """
        conflicts = []
        
        # Extract source information
        node_source = node.metadata.get("source", "")
        if not node_source:
            return []
        
        # Find semantically similar nodes with different sources
        similar_nodes = self.sskg_manager.query({
            "node_types": [NodeType.FACT],
            "content_query": node.content,
            "limit": 10
        })
        
        for similar_node in similar_nodes:
            # Skip self
            if similar_node.id == node.id:
                continue
            
            # Check if sources are different
            other_source = similar_node.metadata.get("source", "")
            if not other_source or other_source == node_source:
                continue
            
            # Check if content is semantically similar but not identical
            similarity_score = self._calculate_similarity_score(node, similar_node)
            if 0.7 < similarity_score < 0.95:  # Similar but not identical
                conflicts.append(ConflictDetectionResult(
                    conflict_type=ConflictType.SOURCE_DISAGREEMENT,
                    conflicting_nodes=[node.id, similar_node.id],
                    confidence=similarity_score * 0.9,  # Adjust confidence
                    description=f"Source disagreement detected between facts from '{node_source}' and '{other_source}'",
                    metadata={
                        "similarity_score": similarity_score,
                        "node_source": node_source,
                        "other_source": other_source,
                        "detection_method": "source_analysis"
                    }
                ))
        
        return conflicts
    
    def _calculate_contradiction_score(self, node1: KnowledgeNode, node2: KnowledgeNode) -> float:
        """
        Calculate a contradiction score between two nodes.
        
        Args:
            node1: First node
            node2: Second node
            
        Returns:
            Contradiction score between 0 and 1
        """
        # In a real implementation, this would use NLP techniques to detect contradictions
        # For now, we'll use a simple heuristic based on semantic similarity
        
        # Check for explicit contradiction markers
        contradiction_markers = [
            ("is", "is not"),
            ("was", "was not"),
            ("will", "will not"),
            ("can", "cannot"),
            ("should", "should not"),
            ("must", "must not"),
            ("always", "never"),
            ("all", "none"),
            ("true", "false"),
            ("yes", "no")
        ]
        
        content1 = node1.content.lower()
        content2 = node2.content.lower()
        
        # Check for explicit contradictions
        for pos, neg in contradiction_markers:
            if (pos in content1 and neg in content2 and content1.replace(pos, neg) == content2) or \
               (pos in content2 and neg in content1 and content2.replace(pos, neg) == content1):
                return 0.9  # High confidence in contradiction
        
        # Calculate semantic similarity (placeholder)
        similarity = self._calculate_similarity_score(node1, node2)
        
        # Heuristic: if similar content but different confidence levels
        if similarity > 0.8 and abs(node1.confidence - node2.confidence) > 0.3:
            return 0.7  # Moderate confidence in contradiction
        
        # Default: low contradiction score
        return 0.1
    
    def _calculate_similarity_score(self, node1: KnowledgeNode, node2: KnowledgeNode) -> float:
        """
        Calculate a semantic similarity score between two nodes.
        
        Args:
            node1: First node
            node2: Second node
            
        Returns:
            Similarity score between 0 and 1
        """
        # In a real implementation, this would use embeddings or other NLP techniques
        # For now, we'll use a simple heuristic based on word overlap
        
        words1 = set(node1.content.lower().split())
        words2 = set(node2.content.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _extract_temporal_info(self, node: KnowledgeNode) -> Optional[Dict[str, Any]]:
        """
        Extract temporal information from a node.
        
        Args:
            node: The node to extract temporal information from
            
        Returns:
            Dictionary of temporal information, or None if not available
        """
        # Check metadata first
        temporal_context = node.metadata.get("temporal_context")
        if temporal_context:
            return temporal_context
        
        # In a real implementation, this would use NLP to extract temporal information
        # For now, we'll return None
        return None
    
    def _has_temporal_conflict(self, temporal_info1: Dict[str, Any], temporal_info2: Dict[str, Any]) -> bool:
        """
        Check if two temporal contexts conflict.
        
        Args:
            temporal_info1: First temporal context
            temporal_info2: Second temporal context
            
        Returns:
            True if the contexts conflict, False otherwise
        """
        # In a real implementation, this would check for temporal inconsistencies
        # For now, we'll return False
        return False
    
    def resolve_conflicts(self, conflicts: List[ConflictDetectionResult], 
                         strategy: Optional[ResolutionStrategy] = None) -> List[ConflictResolutionResult]:
        """
        Resolve detected conflicts using the specified strategy.
        
        Args:
            conflicts: List of detected conflicts
            strategy: Resolution strategy to use (if None, will select automatically)
            
        Returns:
            List of conflict resolution results
        """
        results = []
        
        for conflict in conflicts:
            # Get conflicting nodes
            node_ids = conflict.conflicting_nodes
            nodes = [self.sskg_manager.get_node(node_id) for node_id in node_ids]
            nodes = [node for node in nodes if node]  # Filter out None values
            
            if len(nodes) < 2:
                self.logger.warning(f"Cannot resolve conflict: not enough valid nodes")
                continue
            
            # Select resolution strategy if not specified
            if strategy is None:
                strategy = self._select_resolution_strategy(conflict, nodes)
            
            # Apply resolution strategy
            resolution_func = self.resolution_strategies.get(strategy)
            if not resolution_func:
                self.logger.error(f"Unknown resolution strategy: {strategy}")
                continue
            
            try:
                result = resolution_func(conflict, nodes)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(f"Error resolving conflict: {e}")
        
        return results
    
    def _select_resolution_strategy(self, conflict: ConflictDetectionResult, 
                                  nodes: List[KnowledgeNode]) -> ResolutionStrategy:
        """
        Select an appropriate resolution strategy for a conflict.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Selected resolution strategy
        """
        conflict_type = conflict.conflict_type
        
        # Select strategy based on conflict type
        if conflict_type == ConflictType.DIRECT_CONTRADICTION:
            # For direct contradictions, use highest confidence
            return ResolutionStrategy.HIGHEST_CONFIDENCE
        
        elif conflict_type == ConflictType.TEMPORAL_INCONSISTENCY:
            # For temporal inconsistencies, use most recent
            return ResolutionStrategy.MOST_RECENT
        
        elif conflict_type == ConflictType.SOURCE_DISAGREEMENT:
            # For source disagreements, use source reliability
            return ResolutionStrategy.SOURCE_RELIABILITY
        
        elif conflict_type == ConflictType.PARTIAL_OVERLAP:
            # For partial overlaps, use synthesis
            return ResolutionStrategy.SYNTHESIS
        
        elif conflict_type == ConflictType.CONFIDENCE_VARIATION:
            # For confidence variations, use highest confidence
            return ResolutionStrategy.HIGHEST_CONFIDENCE
        
        elif conflict_type == ConflictType.SEMANTIC_DRIFT:
            # For semantic drift, use most recent
            return ResolutionStrategy.MOST_RECENT
        
        # Default to highest confidence
        return ResolutionStrategy.HIGHEST_CONFIDENCE
    
    def _resolve_by_highest_confidence(self, conflict: ConflictDetectionResult, 
                                     nodes: List[KnowledgeNode]) -> ConflictResolutionResult:
        """
        Resolve conflict by selecting the node with highest confidence.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Conflict resolution result
        """
        # Select node with highest confidence
        resolved_node = max(nodes, key=lambda node: node.confidence)
        
        # Create resolution result
        return self._create_resolution_result(
            resolved_node=resolved_node,
            conflicting_nodes=nodes,
            strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
            confidence=resolved_node.confidence,
            reasoning=f"Selected fact with highest confidence ({resolved_node.confidence:.2f})"
        )
    
    def _resolve_by_most_recent(self, conflict: ConflictDetectionResult, 
                              nodes: List[KnowledgeNode]) -> ConflictResolutionResult:
        """
        Resolve conflict by selecting the most recent node.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Conflict resolution result
        """
        # Select most recent node
        resolved_node = max(nodes, key=lambda node: node.updated_at)
        
        # Create resolution result
        return self._create_resolution_result(
            resolved_node=resolved_node,
            conflicting_nodes=nodes,
            strategy=ResolutionStrategy.MOST_RECENT,
            confidence=0.8,  # Fixed confidence for temporal resolution
            reasoning=f"Selected most recent fact (updated at {resolved_node.updated_at.isoformat()})"
        )
    
    def _resolve_by_source_reliability(self, conflict: ConflictDetectionResult, 
                                     nodes: List[KnowledgeNode]) -> ConflictResolutionResult:
        """
        Resolve conflict by selecting the node from the most reliable source.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Conflict resolution result
        """
        # Get source reliability for each node
        node_reliability = []
        for node in nodes:
            source = node.metadata.get("source", "")
            reliability = self.source_reliability.get(source, 1.0)
            node_reliability.append((node, reliability))
        
        # Select node from most reliable source
        resolved_node, reliability = max(node_reliability, key=lambda x: x[1])
        
        # Create resolution result
        return self._create_resolution_result(
            resolved_node=resolved_node,
            conflicting_nodes=nodes,
            strategy=ResolutionStrategy.SOURCE_RELIABILITY,
            confidence=min(reliability / 5.0, 1.0),  # Normalize to 0-1
            reasoning=f"Selected fact from most reliable source ({resolved_node.metadata.get('source', 'unknown')})"
        )
    
    def _resolve_by_majority_vote(self, conflict: ConflictDetectionResult, 
                                nodes: List[KnowledgeNode]) -> ConflictResolutionResult:
        """
        Resolve conflict by selecting the node supported by the most sources.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Conflict resolution result
        """
        # Group nodes by content similarity
        content_groups = {}
        for node in nodes:
            content = node.content
            found_group = False
            
            for group_content, group_nodes in content_groups.items():
                if self._calculate_similarity_score(node, group_nodes[0]) > 0.9:
                    group_nodes.append(node)
                    found_group = True
                    break
            
            if not found_group:
                content_groups[content] = [node]
        
        # Find group with most nodes
        largest_group = max(content_groups.values(), key=len)
        
        # Select node with highest confidence from largest group
        resolved_node = max(largest_group, key=lambda node: node.confidence)
        
        # Calculate confidence based on majority size
        majority_confidence = len(largest_group) / len(nodes)
        
        # Create resolution result
        return self._create_resolution_result(
            resolved_node=resolved_node,
            conflicting_nodes=nodes,
            strategy=ResolutionStrategy.MAJORITY_VOTE,
            confidence=majority_confidence,
            reasoning=f"Selected fact supported by {len(largest_group)} out of {len(nodes)} sources"
        )
    
    def _resolve_by_synthesis(self, conflict: ConflictDetectionResult, 
                            nodes: List[KnowledgeNode]) -> ConflictResolutionResult:
        """
        Resolve conflict by synthesizing a new node from conflicting nodes.
        
        Args:
            conflict: The detected conflict
            nodes: The conflicting nodes
            
        Returns:
            Conflict resolution result
        """
        # In a real implementation, this would use NLP to synthesize content
        # For now, we'll use the content from the highest confidence node
        
        # Select node with highest confidence as base
        base_node = max(nodes, key=lambda node: node.confidence)
        
        # Create a new synthesized node
        import uuid
        
        # Combine metadata from all nodes
        combined_metadata = {}
        for node in nodes:
            combined_metadata.update(node.metadata)
        
        # Add synthesis metadata
        combined_metadata["synthesis"] = {
            "source_nodes": [node.id for node in nodes],
            "synthesis_time": datetime.now().isoformat(),
            "synthesis_method": "highest_confidence_base"
        }
        
        # Create new node
        synthesized_node = KnowledgeNode(
            id=str(uuid.uuid4()),
            node_type=base_node.node_type,
            content=base_node.content,
            confidence=base_node.confidence * 0.9,  # Slightly reduce confidence
            metadata=combined_metadata,
            version=1
        )
        
        # Add to graph
        synthesized_node_id = self.sskg_manager.add_node(synthesized_node)
        
        # Add relations to original nodes
        for node in nodes:
            self.sskg_manager.add_relation(KnowledgeRelation(
                source_id=synthesized_node_id,
                target_id=node.id,
                relation_type=RelationType.DERIVED_FROM
            ))
        
        # Create resolution result
        return ConflictResolutionResult(
            resolved_node_id=synthesized_node_id,
            resolution_strategy=ResolutionStrategy.SYNTHESIS,
            conflicting_node_ids=[node.id for node in nodes],
            confidence=base_node.confidence * 0.9,
            reasoning=f"Synthesized new fact from {len(nodes)} conflicting facts",
            metadata={
                "synthesis_method": "highest_confidence_base",
                "base_node_id": base_node.id
            }
        )
    
    def _create_resolution_result(self, resolved_node: KnowledgeNode, 
                                conflicting_nodes: List[KnowledgeNode],
                                strategy: ResolutionStrategy, 
                                confidence: float,
                                reasoning: str) -> ConflictResolutionResult:
        """
        Create a conflict resolution result.
        
        Args:
            resolved_node: The resolved node
            conflicting_nodes: The original conflicting nodes
            strategy: The resolution strategy used
            confidence: Confidence in the resolution
            reasoning: Explanation of the resolution process
            
        Returns:
            Conflict resolution result
        """
        # Add resolution metadata to node
        resolution_metadata = {
            "conflict_resolution": {
                "strategy": strategy.value,
                "conflicting_nodes": [node.id for node in conflicting_nodes],
                "confidence": confidence,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Update node metadata
        self.sskg_manager.update_node(resolved_node.id, {
            "metadata": {**resolved_node.metadata, **resolution_metadata}
        })
        
        # Add relations to conflicting nodes
        for node in conflicting_nodes:
            if node.id != resolved_node.id:
                self.sskg_manager.add_relation(KnowledgeRelation(
                    source_id=resolved_node.id,
                    target_id=node.id,
                    relation_type=RelationType.DERIVED_FROM,
                    metadata={"resolution_strategy": strategy.value}
                ))
        
        # Create resolution result
        return ConflictResolutionResult(
            resolved_node_id=resolved_node.id,
            resolution_strategy=strategy,
            conflicting_node_ids=[node.id for node in conflicting_nodes],
            confidence=confidence,
            reasoning=reasoning,
            metadata=resolution_metadata
        )
    
    def track_knowledge_evolution(self, node_id: str) -> List[Dict[str, Any]]:
        """
        Track the evolution of a knowledge node over time.
        
        Args:
            node_id: ID of the node to track
            
        Returns:
            List of evolution events
        """
        node = self.sskg_manager.get_node(node_id)
        if not node:
            self.logger.error(f"Cannot track evolution: node {node_id} does not exist")
            return []
        
        evolution = []
        
        # Get derived nodes
        derived_relations = self.sskg_manager.get_related_nodes(
            node_id=node_id,
            relation_types=[RelationType.DERIVED_FROM],
            direction="incoming"
        )
        
        for derived_node, relation_type in derived_relations:
            evolution.append({
                "event_type": "derived_from",
                "node_id": derived_node.id,
                "timestamp": derived_node.created_at,
                "description": f"Node {derived_node.id} was derived from this node",
                "confidence_change": derived_node.confidence - node.confidence
            })
        
        # Get source nodes
        source_relations = self.sskg_manager.get_related_nodes(
            node_id=node_id,
            relation_types=[RelationType.DERIVED_FROM],
            direction="outgoing"
        )
        
        for source_node, relation_type in source_relations:
            evolution.append({
                "event_type": "derived_from_source",
                "node_id": source_node.id,
                "timestamp": node.created_at,
                "description": f"This node was derived from node {source_node.id}",
                "confidence_change": node.confidence - source_node.confidence
            })
        
        # Sort by timestamp
        evolution.sort(key=lambda x: x["timestamp"])
        
        return evolution