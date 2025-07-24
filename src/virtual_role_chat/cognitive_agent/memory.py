"""
Implementation of the AgentMemory class.

This module defines the AgentMemory class, which encapsulates the
memory capabilities of a cognitive agent, including storage, retrieval,
and organization of memories.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """
    Individual memory item stored by an agent.
    """
    id: str
    content: Any
    memory_type: str  # "episodic", "semantic", "procedural"
    creation_time: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = Field(ge=0.0, le=1.0)
    source: str
    related_memories: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryCategory(BaseModel):
    """
    Category for organizing related memories.
    """
    id: str
    name: str
    description: str
    parent_category: Optional[str] = None
    subcategories: List[str] = Field(default_factory=list)
    memory_ids: List[str] = Field(default_factory=list)


class AgentMemory:
    """
    System that encapsulates the memory capabilities of a cognitive agent.
    
    The AgentMemory system enables the agent to store, retrieve, and organize
    memories of different types (episodic, semantic, procedural), supporting
    the agent's cognitive processes and maintaining its unique perspective.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize an agent memory system.
        
        Args:
            agent_id: ID of the agent this memory belongs to
        """
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"cognitive_agent.{agent_id}.memory")
        
        # Initialize memory components
        self.memories: Dict[str, MemoryItem] = {}
        self.categories: Dict[str, MemoryCategory] = self._initialize_categories()
        self.memory_index: Dict[str, Set[str]] = {}  # Maps keywords to memory IDs
        
        self.logger.info(f"Initialized memory system for agent {agent_id}")
    
    def _initialize_categories(self) -> Dict[str, MemoryCategory]:
        """
        Initialize basic memory categories.
        
        Returns:
            Dictionary mapping category IDs to MemoryCategory objects
        """
        categories = {}
        
        # Create root categories for different memory types
        categories["episodic"] = MemoryCategory(
            id="episodic",
            name="Episodic Memories",
            description="Memories of specific events and experiences"
        )
        
        categories["semantic"] = MemoryCategory(
            id="semantic",
            name="Semantic Memories",
            description="Memories of facts, concepts, and general knowledge"
        )
        
        categories["procedural"] = MemoryCategory(
            id="procedural",
            name="Procedural Memories",
            description="Memories of skills, methods, and procedures"
        )
        
        # Create some common subcategories
        categories["conversations"] = MemoryCategory(
            id="conversations",
            name="Conversations",
            description="Memories of conversations and dialogues",
            parent_category="episodic"
        )
        categories["episodic"].subcategories.append("conversations")
        
        categories["domain_knowledge"] = MemoryCategory(
            id="domain_knowledge",
            name="Domain Knowledge",
            description="Specialized knowledge in specific domains",
            parent_category="semantic"
        )
        categories["semantic"].subcategories.append("domain_knowledge")
        
        categories["problem_solving"] = MemoryCategory(
            id="problem_solving",
            name="Problem Solving",
            description="Methods and approaches for solving problems",
            parent_category="procedural"
        )
        categories["procedural"].subcategories.append("problem_solving")
        
        return categories
    
    def store(
        self,
        key: str,
        content: Any,
        memory_type: str = "semantic",
        importance: float = 0.5,
        source: str = "agent",
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a new memory item.
        
        Args:
            key: Key or identifier for the memory
            content: Content of the memory
            memory_type: Type of memory ("episodic", "semantic", "procedural")
            importance: Importance of the memory (0.0-1.0)
            source: Source of the memory
            metadata: Additional metadata for the memory
            
        Returns:
            ID of the stored memory
        """
        # Generate memory ID
        memory_id = f"{self.agent_id}_{memory_type}_{key}"
        
        # Create memory item
        memory = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            importance=importance,
            source=source,
            metadata=metadata or {}
        )
        
        # Store memory
        self.memories[memory_id] = memory
        
        # Update category
        if memory_type in self.categories:
            self.categories[memory_type].memory_ids.append(memory_id)
        
        # Update index
        self._index_memory(memory)
        
        self.logger.debug(f"Stored memory {memory_id} of type {memory_type}")
        
        return memory_id
    
    def _index_memory(self, memory: MemoryItem) -> None:
        """
        Index a memory for faster retrieval.
        
        Args:
            memory: Memory to index
        """
        # In a real implementation, this would extract keywords from the memory
        # content and add them to the index
        
        # For now, we'll just use a simple approach for demonstration
        if isinstance(memory.content, str):
            # Extract words from content
            words = set(memory.content.lower().split())
            
            # Add to index
            for word in words:
                if word not in self.memory_index:
                    self.memory_index[word] = set()
                self.memory_index[word].add(memory.id)
    
    async def retrieve(self, memory_id: str) -> Optional[MemoryItem]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Retrieved memory, or None if not found
        """
        if memory_id not in self.memories:
            self.logger.warning(f"Memory {memory_id} not found")
            return None
        
        # Update access information
        memory = self.memories[memory_id]
        memory.last_accessed = datetime.now()
        memory.access_count += 1
        
        self.logger.debug(f"Retrieved memory {memory_id}")
        
        return memory
    
    async def retrieve_by_key(self, key: str, memory_type: str = None) -> List[MemoryItem]:
        """
        Retrieve memories by key.
        
        Args:
            key: Key to search for
            memory_type: Optional type filter
            
        Returns:
            List of matching memories
        """
        # Generate potential memory IDs
        potential_ids = []
        if memory_type:
            potential_ids.append(f"{self.agent_id}_{memory_type}_{key}")
        else:
            for type_name in ["episodic", "semantic", "procedural"]:
                potential_ids.append(f"{self.agent_id}_{type_name}_{key}")
        
        # Retrieve matching memories
        memories = []
        for memory_id in potential_ids:
            memory = await self.retrieve(memory_id)
            if memory:
                memories.append(memory)
        
        return memories
    
    async def search(
        self,
        query: str,
        memory_type: str = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """
        Search for memories matching a query.
        
        Args:
            query: Search query
            memory_type: Optional type filter
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        # In a real implementation, this would use more sophisticated search
        # techniques like vector embeddings and semantic similarity
        
        # For now, we'll use a simple keyword-based approach
        query_words = set(query.lower().split())
        matching_ids = set()
        
        # Find memories that match any query word
        for word in query_words:
            if word in self.memory_index:
                matching_ids.update(self.memory_index[word])
        
        # Filter by memory type if specified
        if memory_type:
            matching_ids = {
                memory_id for memory_id in matching_ids
                if memory_id.split("_")[1] == memory_type
            }
        
        # Retrieve matching memories
        memories = []
        for memory_id in list(matching_ids)[:limit]:
            memory = await self.retrieve(memory_id)
            if memory:
                memories.append(memory)
        
        self.logger.debug(f"Search for '{query}' returned {len(memories)} results")
        
        return memories
    
    async def retrieve_relevant(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve memories relevant to a specific task.
        
        Args:
            task: Task information
            
        Returns:
            Dictionary of relevant memories organized by category
        """
        self.logger.info(f"Retrieving memories relevant to task type: {task.get('type', 'unknown')}")
        
        # Extract query from task
        query = task.get("description", "")
        if not query and "name" in task:
            query = task["name"]
        
        # Search for relevant memories
        relevant_memories = await self.search(query, limit=20)
        self.logger.debug(f"Found {len(relevant_memories)} potentially relevant memories")
        
        # Organize by category
        organized_memories = {}
        for memory in relevant_memories:
            memory_type = memory.memory_type
            if memory_type not in organized_memories:
                organized_memories[memory_type] = []
            organized_memories[memory_type].append(memory.dict())
        
        return organized_memories
    
    async def update(self, task: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Update memory based on task execution results.
        
        Args:
            task: Task information
            result: Task execution results
        """
        self.logger.info(f"Updating memory based on task execution")
        
        # Store task execution as episodic memory
        task_memory_id = self.store(
            key=f"task_{datetime.now().isoformat()}",
            content={
                "task": task,
                "result": result
            },
            memory_type="episodic",
            importance=0.7,
            source="task_execution",
            metadata={"task_type": task.get("type", "unknown")}
        )
        
        # Extract and store semantic knowledge from results
        if "conclusions" in result:
            for i, conclusion in enumerate(result["conclusions"]):
                if isinstance(conclusion, dict) and "content" in conclusion:
                    self.store(
                        key=f"conclusion_{datetime.now().isoformat()}_{i}",
                        content=conclusion["content"],
                        memory_type="semantic",
                        importance=conclusion.get("confidence", 0.5),
                        source="task_conclusion",
                        metadata={"task_id": task_memory_id}
                    )
        
        # Extract and store procedural knowledge if applicable
        if "strategies" in result:
            for i, strategy in enumerate(result.get("strategies", [])):
                if isinstance(strategy, dict) and "steps" in strategy:
                    self.store(
                        key=f"strategy_{datetime.now().isoformat()}_{i}",
                        content=strategy,
                        memory_type="procedural",
                        importance=strategy.get("effectiveness", 0.5),
                        source="task_strategy",
                        metadata={"task_id": task_memory_id}
                    )
    
    def create_category(
        self,
        category_id: str,
        name: str,
        description: str,
        parent_category: str = None
    ) -> bool:
        """
        Create a new memory category.
        
        Args:
            category_id: ID for the new category
            name: Name of the category
            description: Description of the category
            parent_category: Optional parent category ID
            
        Returns:
            True if category was created, False if it already exists
        """
        if category_id in self.categories:
            self.logger.warning(f"Category {category_id} already exists")
            return False
        
        # Create category
        self.categories[category_id] = MemoryCategory(
            id=category_id,
            name=name,
            description=description,
            parent_category=parent_category
        )
        
        # Update parent category if specified
        if parent_category and parent_category in self.categories:
            self.categories[parent_category].subcategories.append(category_id)
        
        self.logger.debug(f"Created category {category_id}")
        
        return True
    
    def categorize_memory(self, memory_id: str, category_id: str) -> bool:
        """
        Add a memory to a category.
        
        Args:
            memory_id: ID of the memory to categorize
            category_id: ID of the category
            
        Returns:
            True if memory was categorized, False otherwise
        """
        if memory_id not in self.memories:
            self.logger.warning(f"Memory {memory_id} not found")
            return False
        
        if category_id not in self.categories:
            self.logger.warning(f"Category {category_id} not found")
            return False
        
        # Add memory to category
        if memory_id not in self.categories[category_id].memory_ids:
            self.categories[category_id].memory_ids.append(memory_id)
            self.logger.debug(f"Added memory {memory_id} to category {category_id}")
        
        return True
    
    def relate_memories(self, memory_id1: str, memory_id2: str) -> bool:
        """
        Create a relationship between two memories.
        
        Args:
            memory_id1: ID of the first memory
            memory_id2: ID of the second memory
            
        Returns:
            True if relationship was created, False otherwise
        """
        if memory_id1 not in self.memories:
            self.logger.warning(f"Memory {memory_id1} not found")
            return False
        
        if memory_id2 not in self.memories:
            self.logger.warning(f"Memory {memory_id2} not found")
            return False
        
        # Add relationship
        if memory_id2 not in self.memories[memory_id1].related_memories:
            self.memories[memory_id1].related_memories.append(memory_id2)
        
        if memory_id1 not in self.memories[memory_id2].related_memories:
            self.memories[memory_id2].related_memories.append(memory_id1)
        
        self.logger.debug(f"Created relationship between memories {memory_id1} and {memory_id2}")
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the agent's memory.
        
        Returns:
            Dictionary containing memory statistics
        """
        # Count memories by type
        type_counts = {}
        for memory in self.memories.values():
            memory_type = memory.memory_type
            if memory_type not in type_counts:
                type_counts[memory_type] = 0
            type_counts[memory_type] += 1
        
        # Calculate average importance
        avg_importance = sum(memory.importance for memory in self.memories.values()) / len(self.memories) if self.memories else 0
        
        # Calculate average access count
        avg_access_count = sum(memory.access_count for memory in self.memories.values()) / len(self.memories) if self.memories else 0
        
        return {
            "total_memories": len(self.memories),
            "memory_types": type_counts,
            "category_count": len(self.categories),
            "avg_importance": avg_importance,
            "avg_access_count": avg_access_count,
            "index_size": len(self.memory_index)
        }