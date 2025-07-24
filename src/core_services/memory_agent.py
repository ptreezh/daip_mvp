# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-22 16:00:00
@Author  : DAIP-LIVE Team
@File    : memory_agent.py
@Description:
    Implementation of MemAgent based on ByteDance/Tsinghua research paper:
    "MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent"
    
    This implementation provides intelligent memory management for long-context
    interactions across multiple conversations using reinforcement learning techniques.
"""
import logging
import json
import random
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, KnowledgeQuery, NodeType

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Types of memories in the MemAgent system."""
    EPISODIC = "episodic"  # Specific conversations and events
    SEMANTIC = "semantic"   # Facts, concepts, and knowledge
    PROCEDURAL = "procedural"  # Processes, methods, and approaches
    META = "meta"  # Insights about memory usage patterns


class Memory(BaseModel):
    """Model for memories in the MemAgent system."""
    id: Optional[str] = None
    content: str
    memory_type: MemoryType
    source_id: str  # Role ID, user ID, or session ID
    importance: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    related_memories: List[str] = []
    metadata: Dict[str, Any] = {}


class MemoryQuery(BaseModel):
    """Model for querying memories."""
    content: str
    memory_types: Optional[List[MemoryType]] = None
    source_id: Optional[str] = None
    min_importance: float = 0.0
    min_recency: float = 0.0
    limit: int = 5


class TrainingExample(BaseModel):
    """Model for RL training examples."""
    context: str
    candidate_memories: List[Memory]
    selected_memories: List[str]
    reward: float


class MemAgent:
    """
    Implementation of MemAgent based on ByteDance/Tsinghua research.
    
    Provides intelligent memory management for long-context interactions
    across multiple conversations using reinforcement learning techniques.
    """
    
    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        model_path: Optional[Path] = None,
        enable_rl: bool = True
    ):
        """
        Initialize the MemAgent.
        
        Args:
            sskg_manager: Enhanced SSKG manager for memory storage
            model_path: Path to the RL model file
            enable_rl: Whether to enable reinforcement learning
        """
        self.sskg_manager = sskg_manager
        self.model_path = model_path
        self.enable_rl = enable_rl
        
        # Initialize RL model if enabled
        self.rl_model = None
        if self.enable_rl:
            self._initialize_rl_model()
        
        logger.info("MemAgent initialized")
    
    def _initialize_rl_model(self):
        """Initialize the reinforcement learning model."""
        try:
            # In a real implementation, this would load a trained RL model
            # For this example, we'll use a simple placeholder
            
            # Define a simple model structure
            self.rl_model = {
                "weights": {
                    "importance": 0.3,
                    "recency": 0.3,
                    "relevance": 0.4
                },
                "version": "0.1",
                "training_examples": 0
            }
            
            # Load model from file if available
            if self.model_path and self.model_path.exists():
                try:
                    with open(self.model_path, 'r') as f:
                        self.rl_model = json.load(f)
                    logger.info(f"Loaded RL model from {self.model_path}")
                except Exception as e:
                    logger.error(f"Failed to load RL model: {e}")
            
            logger.info("RL model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RL model: {e}")
            self.enable_rl = False
    
    def store_memory(self, memory: Memory) -> str:
        """
        Store a memory in the SSKG.
        
        Args:
            memory: The memory to store
            
        Returns:
            ID of the stored memory
        """
        # Generate ID if not provided
        if not memory.id:
            memory.id = f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Store in SSKG
        node_id = self.sskg_manager.store_memory(
            content=memory.content,
            memory_type=memory.memory_type.value,
            owner_id=memory.source_id,
            importance=memory.importance,
            metadata={
                "memory_id": memory.id,
                "recency": memory.recency,
                "created_at": memory.created_at.isoformat(),
                "last_accessed": memory.last_accessed.isoformat(),
                "access_count": memory.access_count,
                "related_memories": memory.related_memories,
                **memory.metadata
            }
        )
        
        logger.debug(f"Stored memory {memory.id} in SSKG as node {node_id}")
        return memory.id
    
    def retrieve_memories(self, context: str, query: Optional[MemoryQuery] = None, limit: int = 5) -> List[Memory]:
        """
        Retrieve memories relevant to the given context.
        
        Args:
            context: The context to retrieve memories for
            query: Optional additional query parameters
            limit: Maximum number of memories to return
            
        Returns:
            List of relevant memories
        """
        # Create default query if not provided
        if not query:
            query = MemoryQuery(
                content=context,
                limit=limit
            )
        
        # Use RL model for memory selection if enabled
        if self.enable_rl and self.rl_model:
            return self._retrieve_memories_with_rl(context, query)
        else:
            return self._retrieve_memories_simple(context, query)
    
    def _retrieve_memories_simple(self, context: str, query: MemoryQuery) -> List[Memory]:
        """
        Simple memory retrieval without RL.
        
        Args:
            context: The context to retrieve memories for
            query: Query parameters
            
        Returns:
            List of relevant memories
        """
        # Build SSKG query
        metadata_filters = {}
        if query.source_id:
            metadata_filters["owner_id"] = query.source_id
        
        sskg_query = KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            content_query=query.content,
            metadata_filters=metadata_filters,
            limit=query.limit * 2  # Get more candidates for filtering
        )
        
        # Query SSKG
        nodes = self.sskg_manager.query(sskg_query)
        
        # Convert to Memory objects and filter
        memories = []
        for node in nodes:
            try:
                metadata = node.metadata
                
                # Skip if memory type doesn't match
                memory_type = metadata.get("memory_type", "episodic")
                if query.memory_types and MemoryType(memory_type) not in query.memory_types:
                    continue
                
                # Skip if importance is too low
                importance = float(node.confidence)
                if importance < query.min_importance:
                    continue
                
                # Skip if recency is too low
                recency = float(metadata.get("recency", 0.0))
                if recency < query.min_recency:
                    continue
                
                # Create Memory object
                memory = Memory(
                    id=metadata.get("memory_id", node.id),
                    content=node.content,
                    memory_type=MemoryType(memory_type),
                    source_id=metadata.get("owner_id", "unknown"),
                    importance=importance,
                    recency=recency,
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    last_accessed=datetime.fromisoformat(metadata.get("last_accessed", datetime.now().isoformat())),
                    access_count=int(metadata.get("access_count", 0)),
                    related_memories=metadata.get("related_memories", []),
                    metadata={k: v for k, v in metadata.items() if k not in [
                        "memory_id", "memory_type", "owner_id", "recency", "created_at", 
                        "last_accessed", "access_count", "related_memories"
                    ]}
                )
                
                memories.append(memory)
                
                # Update access count and last accessed time
                self.sskg_manager.update_node(node.id, {
                    "metadata": {
                        **metadata,
                        "access_count": memory.access_count + 1,
                        "last_accessed": datetime.now().isoformat()
                    }
                })
            except Exception as e:
                logger.error(f"Error converting node to memory: {e}")
        
        # Sort by importance and recency
        memories.sort(key=lambda m: (m.importance + m.recency) / 2, reverse=True)
        
        # Return limited results
        return memories[:query.limit]
    
    def _retrieve_memories_with_rl(self, context: str, query: MemoryQuery) -> List[Memory]:
        """
        RL-based memory retrieval as described in the ByteDance/Tsinghua paper.
        
        Args:
            context: The context to retrieve memories for
            query: Query parameters
            
        Returns:
            List of relevant memories
        """
        # Get candidate memories (more than we need)
        candidates = self._retrieve_memories_simple(context, MemoryQuery(
            content=query.content,
            memory_types=query.memory_types,
            source_id=query.source_id,
            min_importance=0.0,  # No filtering by importance
            min_recency=0.0,     # No filtering by recency
            limit=query.limit * 3
        ))
        
        if not candidates:
            return []
        
        # Calculate features for each candidate
        candidate_features = []
        for memory in candidates:
            # Calculate relevance score (simple keyword matching for this example)
            # In a real implementation, this would use embeddings or more sophisticated matching
            relevance = self._calculate_relevance(context, memory.content)
            
            features = {
                "importance": memory.importance,
                "recency": memory.recency,
                "relevance": relevance,
                "access_count_norm": min(memory.access_count / 10, 1.0),  # Normalized access count
                "memory_type_factor": {
                    MemoryType.EPISODIC: 0.7,
                    MemoryType.SEMANTIC: 0.9,
                    MemoryType.PROCEDURAL: 0.8,
                    MemoryType.META: 0.6
                }.get(memory.memory_type, 0.7)
            }
            
            candidate_features.append((memory, features))
        
        # Score candidates using RL model
        scored_candidates = []
        for memory, features in candidate_features:
            # Apply RL model weights
            score = (
                features["importance"] * self.rl_model["weights"]["importance"] +
                features["recency"] * self.rl_model["weights"]["recency"] +
                features["relevance"] * self.rl_model["weights"]["relevance"]
            )
            
            # Apply additional factors
            score *= features["memory_type_factor"]
            score *= (1 + 0.1 * features["access_count_norm"])  # Slight boost for frequently accessed memories
            
            scored_candidates.append((memory, score))
        
        # Sort by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Return top memories
        return [memory for memory, _ in scored_candidates[:query.limit]]
    
    def _calculate_relevance(self, context: str, memory_content: str) -> float:
        """
        Calculate relevance between context and memory content.
        
        Args:
            context: The context
            memory_content: The memory content
            
        Returns:
            Relevance score between 0 and 1
        """
        # Simple keyword matching for this example
        # In a real implementation, this would use embeddings or more sophisticated matching
        context_words = set(context.lower().split())
        memory_words = set(memory_content.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(context_words.intersection(memory_words))
        union = len(context_words.union(memory_words))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def consolidate_memories(self, source_id: str, memory_type: Optional[MemoryType] = None) -> List[Memory]:
        """
        Consolidate memories for a source.
        
        Args:
            source_id: ID of the memory source
            memory_type: Optional type of memories to consolidate
            
        Returns:
            List of consolidated memories
        """
        # Build query to get memories to consolidate
        metadata_filters = {"owner_id": source_id}
        if memory_type:
            metadata_filters["memory_type"] = memory_type.value
        
        sskg_query = KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters=metadata_filters,
            limit=100  # Get a large batch for consolidation
        )
        
        # Query SSKG
        nodes = self.sskg_manager.query(sskg_query)
        
        # Convert to Memory objects
        memories = []
        for node in nodes:
            try:
                metadata = node.metadata
                
                memory = Memory(
                    id=metadata.get("memory_id", node.id),
                    content=node.content,
                    memory_type=MemoryType(metadata.get("memory_type", "episodic")),
                    source_id=metadata.get("owner_id", source_id),
                    importance=float(node.confidence),
                    recency=float(metadata.get("recency", 0.0)),
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    last_accessed=datetime.fromisoformat(metadata.get("last_accessed", datetime.now().isoformat())),
                    access_count=int(metadata.get("access_count", 0)),
                    related_memories=metadata.get("related_memories", []),
                    metadata={k: v for k, v in metadata.items() if k not in [
                        "memory_id", "memory_type", "owner_id", "recency", "created_at", 
                        "last_accessed", "access_count", "related_memories"
                    ]}
                )
                
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error converting node to memory: {e}")
        
        # Group memories by type
        memories_by_type = {}
        for memory in memories:
            if memory.memory_type not in memories_by_type:
                memories_by_type[memory.memory_type] = []
            memories_by_type[memory.memory_type].append(memory)
        
        # Consolidate each type
        consolidated_memories = []
        for mem_type, type_memories in memories_by_type.items():
            # Skip if too few memories
            if len(type_memories) < 3:
                continue
            
            # Sort by importance
            type_memories.sort(key=lambda m: m.importance, reverse=True)
            
            # For this example, we'll use a simple consolidation strategy
            # In a real implementation, this would use more sophisticated techniques
            if mem_type == MemoryType.EPISODIC:
                # For episodic memories, group by recency
                recent = [m for m in type_memories if m.recency > 0.7]
                if recent:
                    consolidated = self._consolidate_memory_group(
                        recent, 
                        f"Recent experiences of {source_id}",
                        MemoryType.EPISODIC
                    )
                    consolidated_memories.append(consolidated)
            
            elif mem_type == MemoryType.SEMANTIC:
                # For semantic memories, take the most important ones
                important = type_memories[:5]
                if important:
                    consolidated = self._consolidate_memory_group(
                        important, 
                        f"Key knowledge of {source_id}",
                        MemoryType.SEMANTIC
                    )
                    consolidated_memories.append(consolidated)
            
            elif mem_type == MemoryType.PROCEDURAL:
                # For procedural memories, take the most accessed ones
                accessed = sorted(type_memories, key=lambda m: m.access_count, reverse=True)[:5]
                if accessed:
                    consolidated = self._consolidate_memory_group(
                        accessed, 
                        f"Common procedures used by {source_id}",
                        MemoryType.PROCEDURAL
                    )
                    consolidated_memories.append(consolidated)
        
        # Store consolidated memories
        for memory in consolidated_memories:
            self.store_memory(memory)
        
        return consolidated_memories
    
    def _consolidate_memory_group(self, memories: List[Memory], title: str, memory_type: MemoryType) -> Memory:
        """
        Consolidate a group of memories into a single memory.
        
        Args:
            memories: List of memories to consolidate
            title: Title for the consolidated memory
            memory_type: Type of the consolidated memory
            
        Returns:
            Consolidated memory
        """
        # Extract content from memories
        contents = [m.content for m in memories]
        
        # Create consolidated content
        consolidated_content = f"{title}:\n\n"
        consolidated_content += "\n\n".join([f"- {content}" for content in contents])
        
        # Calculate average importance
        avg_importance = sum(m.importance for m in memories) / len(memories)
        
        # Create consolidated memory
        consolidated = Memory(
            content=consolidated_content,
            memory_type=memory_type,
            source_id=memories[0].source_id,
            importance=avg_importance,
            recency=max(m.recency for m in memories),
            related_memories=[m.id for m in memories],
            metadata={
                "consolidated": True,
                "source_memories": [m.id for m in memories],
                "consolidation_time": datetime.now().isoformat()
            }
        )
        
        return consolidated
    
    def train_memory_selector(self, training_examples: List[TrainingExample]) -> Dict[str, Any]:
        """
        Train the RL model for memory selection.
        
        Args:
            training_examples: List of training examples
            
        Returns:
            Training results
        """
        if not self.enable_rl:
            logger.warning("RL is disabled. Cannot train memory selector.")
            return {"success": False, "reason": "RL disabled"}
        
        # In a real implementation, this would use proper RL training
        # For this example, we'll use a simple update rule
        
        # Initialize weight updates
        weight_updates = {
            "importance": 0.0,
            "recency": 0.0,
            "relevance": 0.0
        }
        
        # Process each training example
        for example in training_examples:
            # Skip examples with no selected memories
            if not example.selected_memories:
                continue
            
            # Get selected and non-selected memories
            selected = [m for m in example.candidate_memories if m.id in example.selected_memories]
            non_selected = [m for m in example.candidate_memories if m.id not in example.selected_memories]
            
            # Skip if no contrast
            if not selected or not non_selected:
                continue
            
            # Calculate average features for selected and non-selected
            selected_features = {
                "importance": sum(m.importance for m in selected) / len(selected),
                "recency": sum(m.recency for m in selected) / len(selected),
                "relevance": sum(self._calculate_relevance(example.context, m.content) for m in selected) / len(selected)
            }
            
            non_selected_features = {
                "importance": sum(m.importance for m in non_selected) / len(non_selected),
                "recency": sum(m.recency for m in non_selected) / len(non_selected),
                "relevance": sum(self._calculate_relevance(example.context, m.content) for m in non_selected) / len(non_selected)
            }
            
            # Update weights based on feature differences
            for feature in weight_updates:
                diff = selected_features[feature] - non_selected_features[feature]
                # Apply reward as learning rate
                weight_updates[feature] += diff * example.reward * 0.01
        
        # Apply updates to model weights
        for feature, update in weight_updates.items():
            self.rl_model["weights"][feature] += update
            
            # Ensure weights stay positive
            self.rl_model["weights"][feature] = max(0.1, self.rl_model["weights"][feature])
        
        # Normalize weights to sum to 1
        total = sum(self.rl_model["weights"].values())
        for feature in self.rl_model["weights"]:
            self.rl_model["weights"][feature] /= total
        
        # Update training count
        self.rl_model["training_examples"] += len(training_examples)
        
        # Save model
        if self.model_path:
            try:
                # Ensure parent directory exists
                self.model_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.model_path, 'w') as f:
                    json.dump(self.rl_model, f)
                logger.info(f"Saved RL model to {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to save RL model: {e}")
        
        return {
            "success": True,
            "weights": self.rl_model["weights"],
            "training_examples": self.rl_model["training_examples"]
        }
    
    def get_memory_importance(self, memory_content: str, context: str) -> float:
        """
        Calculate the importance of a memory in the given context.
        
        Args:
            memory_content: The memory content
            context: The context
            
        Returns:
            Importance score between 0 and 1
        """
        # Calculate relevance
        relevance = self._calculate_relevance(context, memory_content)
        
        # In a real implementation, this would use more sophisticated techniques
        # For this example, we'll use a simple heuristic
        
        # Longer memories might be more important
        length_factor = min(len(memory_content) / 500, 1.0)
        
        # Memories with specific keywords might be important
        important_keywords = ["critical", "important", "key", "essential", "remember", "note"]
        keyword_factor = 0.0
        for keyword in important_keywords:
            if keyword in memory_content.lower():
                keyword_factor += 0.1
        keyword_factor = min(keyword_factor, 0.5)
        
        # Calculate final importance
        importance = 0.3 + (relevance * 0.4) + (length_factor * 0.2) + keyword_factor
        
        return min(importance, 1.0)
    
    def organize_memories(self, memories: List[Memory]) -> Dict[str, List[Memory]]:
        """
        Organize memories into categories.
        
        Args:
            memories: List of memories to organize
            
        Returns:
            Dictionary of categorized memories
        """
        # Organize by memory type
        by_type = {}
        for memory in memories:
            if memory.memory_type not in by_type:
                by_type[memory.memory_type] = []
            by_type[memory.memory_type].append(memory)
        
        # Sort each category
        for mem_type in by_type:
            if mem_type == MemoryType.EPISODIC:
                # Sort episodic memories by recency
                by_type[mem_type].sort(key=lambda m: m.recency, reverse=True)
            elif mem_type == MemoryType.SEMANTIC:
                # Sort semantic memories by importance
                by_type[mem_type].sort(key=lambda m: m.importance, reverse=True)
            elif mem_type == MemoryType.PROCEDURAL:
                # Sort procedural memories by access count
                by_type[mem_type].sort(key=lambda m: m.access_count, reverse=True)
            else:
                # Sort other memories by importance
                by_type[mem_type].sort(key=lambda m: m.importance, reverse=True)
        
        return by_type
    
    def share_memories(self, source_id: str, target_id: str, memory_ids: List[str]) -> bool:
        """
        Share memories from one source to another.
        
        Args:
            source_id: ID of the memory source
            target_id: ID of the memory target
            memory_ids: List of memory IDs to share
            
        Returns:
            True if successful, False otherwise
        """
        # Build query to get memories to share
        metadata_filters = {
            "owner_id": source_id,
            "memory_id": {"$in": memory_ids}
        }
        
        sskg_query = KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            metadata_filters=metadata_filters,
            limit=len(memory_ids)
        )
        
        # Query SSKG
        nodes = self.sskg_manager.query(sskg_query)
        
        # Convert to Memory objects
        memories = []
        for node in nodes:
            try:
                metadata = node.metadata
                
                memory = Memory(
                    id=metadata.get("memory_id", node.id),
                    content=node.content,
                    memory_type=MemoryType(metadata.get("memory_type", "episodic")),
                    source_id=source_id,
                    importance=float(node.confidence),
                    recency=float(metadata.get("recency", 0.0)),
                    created_at=datetime.fromisoformat(metadata.get("created_at", datetime.now().isoformat())),
                    last_accessed=datetime.fromisoformat(metadata.get("last_accessed", datetime.now().isoformat())),
                    access_count=int(metadata.get("access_count", 0)),
                    related_memories=metadata.get("related_memories", []),
                    metadata={k: v for k, v in metadata.items() if k not in [
                        "memory_id", "memory_type", "owner_id", "recency", "created_at", 
                        "last_accessed", "access_count", "related_memories"
                    ]}
                )
                
                memories.append(memory)
            except Exception as e:
                logger.error(f"Error converting node to memory: {e}")
        
        # Create shared copies
        for memory in memories:
            # Create new memory with shared attribution
            shared_memory = Memory(
                content=f"Shared from {source_id}: {memory.content}",
                memory_type=memory.memory_type,
                source_id=target_id,
                importance=memory.importance * 0.9,  # Slightly lower importance for shared memories
                recency=1.0,  # High recency since it's newly shared
                metadata={
                    **memory.metadata,
                    "shared_from": source_id,
                    "original_memory_id": memory.id,
                    "shared_at": datetime.now().isoformat()
                }
            )
            
            # Store shared memory
            self.store_memory(shared_memory)
        
        return True
    
    def optimize_context(self, context: str, task: str, max_tokens: int) -> Dict[str, Any]:
        """
        Optimize context for a specific task using MemAgent.
        
        Args:
            context: The current context
            task: The current task
            max_tokens: Maximum tokens for the optimized context
            
        Returns:
            Optimized context
        """
        # Extract task requirements
        task_keywords = self._extract_keywords(task)
        
        # Retrieve relevant memories
        memories = self.retrieve_memories(
            context=f"{task}\n\n{context}",
            query=MemoryQuery(
                content=task,
                limit=5
            )
        )
        
        # Calculate token counts (simplified)
        token_counts = {
            "context": len(context.split()),
            "memories": sum(len(m.content.split()) for m in memories)
        }
        
        # Check if we need to compress
        total_tokens = token_counts["context"] + token_counts["memories"]
        if total_tokens <= max_tokens:
            # No compression needed
            optimized_context = context
            for memory in memories:
                optimized_context += f"\n\nRelevant memory: {memory.content}"
            
            return {
                "optimized_context": optimized_context,
                "included_memories": [m.id for m in memories],
                "excluded_memories": [],
                "compression_applied": False
            }
        else:
            # Compression needed
            # In a real implementation, this would use more sophisticated techniques
            # For this example, we'll use a simple approach
            
            # Sort memories by relevance to task
            memories.sort(key=lambda m: self._calculate_relevance(task, m.content), reverse=True)
            
            # Calculate available tokens for memories
            available_tokens = max_tokens - min(token_counts["context"], max_tokens * 0.7)
            
            # Select memories to include
            included_memories = []
            excluded_memories = []
            memory_tokens = 0
            
            for memory in memories:
                mem_tokens = len(memory.content.split())
                if memory_tokens + mem_tokens <= available_tokens:
                    included_memories.append(memory)
                    memory_tokens += mem_tokens
                else:
                    excluded_memories.append(memory)
            
            # Compress context if needed
            if token_counts["context"] > max_tokens * 0.7:
                # Simple compression: keep first and last parts
                words = context.split()
                keep_words = int(max_tokens * 0.7)
                first_part = int(keep_words * 0.7)
                last_part = keep_words - first_part
                
                compressed_context = " ".join(words[:first_part]) + "\n\n[...]\n\n" + " ".join(words[-last_part:])
            else:
                compressed_context = context
            
            # Build optimized context
            optimized_context = compressed_context
            for memory in included_memories:
                optimized_context += f"\n\nRelevant memory: {memory.content}"
            
            return {
                "optimized_context": optimized_context,
                "included_memories": [m.id for m in included_memories],
                "excluded_memories": [m.id for m in excluded_memories],
                "compression_applied": token_counts["context"] > max_tokens * 0.7
            }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: The text to extract keywords from
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # In a real implementation, this would use more sophisticated techniques
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of", "is", "are"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return keywords