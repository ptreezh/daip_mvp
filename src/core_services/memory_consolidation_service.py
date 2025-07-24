# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-23 11:00:00
@Author  : DAIP-LIVE Team
@File    : memory_consolidation_service.py
@Description:
    Enhanced memory consolidation and sharing service for MemAgent.
    Implements background consolidation processes, conflict resolution,
    and controlled memory sharing mechanisms.
"""
import logging
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

from src.core_services.memory_agent import MemAgent, Memory, MemoryType, MemoryQuery

logger = logging.getLogger(__name__)


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving memory conflicts."""
    TEMPORAL = "temporal"
    SOURCE_BASED = "source_based"
    CONFIDENCE_BASED = "confidence_based"
    CONSENSUS_BASED = "consensus_based"


class MemoryConflict(BaseModel):
    """Model for memory conflicts."""
    conflicting_memories: List[Memory]
    conflict_type: str
    severity: float = Field(ge=0.0, le=1.0)
    description: str
    suggested_resolution: Optional[str] = None


class SharingPolicy(BaseModel):
    """Policy for memory sharing between sources."""
    source_id: str
    target_id: str
    allowed_memory_types: List[MemoryType]
    importance_threshold: float = 0.7
    max_memories_per_share: int = 10
    trust_level: float = Field(ge=0.0, le=1.0, default=0.5)


class MemoryConsolidationService:
    """Enhanced memory consolidation and sharing service."""
    
    def __init__(self, mem_agent: MemAgent):
        """Initialize the consolidation service."""
        self.mem_agent = mem_agent
        self.sharing_policies: List[SharingPolicy] = []
        self.consolidation_stats = {
            "total_consolidations": 0,
            "conflicts_resolved": 0,
            "memories_shared": 0
        }
        logger.info("MemoryConsolidationService initialized")
    
    def consolidate_memories_advanced(self, source_id: str) -> List[Memory]:
        """Advanced memory consolidation."""
        consolidated_memories = []
        
        # Get memories for consolidation
        query = MemoryQuery(content="", source_id=source_id, limit=50)
        memories = self.mem_agent.retrieve_memories("", query)
        
        if len(memories) < 3:
            return consolidated_memories
        
        # Group by memory type
        type_groups = {}
        for memory in memories:
            if memory.memory_type not in type_groups:
                type_groups[memory.memory_type] = []
            type_groups[memory.memory_type].append(memory)
        
        # Consolidate each type
        for memory_type, group_memories in type_groups.items():
            if len(group_memories) >= 3:
                consolidated = self._create_consolidated_memory(
                    group_memories[:5],  # Take top 5
                    f"Consolidated {memory_type.value} memories for {source_id}",
                    memory_type,
                    source_id
                )
                consolidated_memories.append(consolidated)
                self.mem_agent.store_memory(consolidated)
        
        self.consolidation_stats["total_consolidations"] += len(consolidated_memories)
        return consolidated_memories
    
    def _create_consolidated_memory(
        self, memories: List[Memory], title: str, memory_type: MemoryType, source_id: str
    ) -> Memory:
        """Create a consolidated memory."""
        contents = [m.content for m in memories]
        consolidated_content = f"{title}:\n\n" + "\n\n".join([f"- {content}" for content in contents])
        
        avg_importance = sum(m.importance for m in memories) / len(memories)
        max_recency = max(m.recency for m in memories)
        
        return Memory(
            content=consolidated_content,
            memory_type=memory_type,
            source_id=source_id,
            importance=min(avg_importance * 1.1, 1.0),
            recency=max_recency,
            metadata={
                "consolidated": True,
                "source_memories": [m.id for m in memories if m.id],
                "consolidation_time": datetime.now().isoformat()
            }
        )
    
    def detect_memory_conflicts(self, source_id: str) -> List[MemoryConflict]:
        """Detect conflicts between memories."""
        conflicts = []
        
        query = MemoryQuery(content="", source_id=source_id, limit=50)
        memories = self.mem_agent.retrieve_memories("", query)
        
        # Check for duplications
        for i, memory1 in enumerate(memories):
            for j, memory2 in enumerate(memories[i+1:], i+1):
                similarity = self._calculate_similarity(memory1.content, memory2.content)
                if similarity > 0.8:
                    conflict = MemoryConflict(
                        conflicting_memories=[memory1, memory2],
                        conflict_type="duplication",
                        severity=0.6,
                        description=f"Duplicate memories detected (similarity: {similarity:.2f})",
                        suggested_resolution="Merge duplicate memories"
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate Jaccard similarity between two content strings."""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def resolve_memory_conflict(
        self, conflict: MemoryConflict, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.CONFIDENCE_BASED
    ) -> Optional[Memory]:
        """Resolve a memory conflict."""
        if not conflict.conflicting_memories:
            return None
        
        if strategy == ConflictResolutionStrategy.CONFIDENCE_BASED:
            best_memory = max(conflict.conflicting_memories, key=lambda m: m.importance)
        elif strategy == ConflictResolutionStrategy.TEMPORAL:
            best_memory = max(conflict.conflicting_memories, key=lambda m: m.created_at)
        else:
            best_memory = conflict.conflicting_memories[0]
        
        resolved = Memory(
            content=best_memory.content,
            memory_type=best_memory.memory_type,
            source_id=best_memory.source_id,
            importance=best_memory.importance,
            recency=best_memory.recency,
            metadata={
                **best_memory.metadata,
                "conflict_resolved": True,
                "resolution_strategy": strategy.value,
                "resolution_time": datetime.now().isoformat()
            }
        )
        
        self.mem_agent.store_memory(resolved)
        self.consolidation_stats["conflicts_resolved"] += 1
        return resolved
    
    def add_sharing_policy(self, policy: SharingPolicy):
        """Add a memory sharing policy."""
        self.sharing_policies.append(policy)
        logger.info(f"Added sharing policy: {policy.source_id} -> {policy.target_id}")
    
    def execute_sharing_policy(self, policy: SharingPolicy) -> int:
        """Execute a sharing policy."""
        memories_shared = 0
        
        for memory_type in policy.allowed_memory_types:
            query = MemoryQuery(
                content="",
                memory_types=[memory_type],
                source_id=policy.source_id,
                min_importance=policy.importance_threshold,
                limit=policy.max_memories_per_share
            )
            
            memories = self.mem_agent.retrieve_memories("", query)
            
            if memories:
                memory_ids = [m.id for m in memories if m.id]
                success = self.mem_agent.share_memories(policy.source_id, policy.target_id, memory_ids)
                
                if success:
                    memories_shared += len(memory_ids)
        
        self.consolidation_stats["memories_shared"] += memories_shared
        return memories_shared
    
    def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics."""
        return self.consolidation_stats.copy()