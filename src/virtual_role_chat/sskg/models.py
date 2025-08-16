"""Data models for the Semantic Structured Knowledge Graph (SSKG).

This module defines the core data models used by the SSKG system,
including knowledge facts, relations, queries, and various memory types.
"""

from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import Any, Dict, List, Optional, Tuple, Union
=======
from typing import Any, Optional, Union
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    """Types of relationships between knowledge facts."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    ELABORATES = "elaborates"
    IMPLIES = "implies"
    CAUSED_BY = "caused_by"
    PART_OF = "part_of"
    SIMILAR_TO = "similar_to"
    DEPENDS_ON = "depends_on"
    PRECEDES = "precedes"
    FOLLOWS = "follows"


class MemoryType(str, Enum):
    """Types of memories in the system."""

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    META = "meta"


class ConflictResolutionStrategy(str, Enum):
    """Strategies for resolving knowledge conflicts."""

    TEMPORAL = "temporal"  # Newer information supersedes older
    SOURCE_BASED = "source_based"  # Prioritize more reliable sources
    CONFIDENCE_BASED = "confidence_based"  # Higher confidence prevails
    CONSENSUS_BASED = "consensus_based"  # Majority agreement
    HUMAN_IN_LOOP = "human_in_loop"  # Require human resolution


class KnowledgeRelation(BaseModel):
    """Represents a relationship between two knowledge facts.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    id: Optional[str] = None
    relation_type: RelationType
    target_fact_id: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this relationship")
    evidence: list[str] = Field(default_factory=list, description="Evidence supporting this relationship")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None  # Agent or user ID


class KnowledgeFact(BaseModel):
    """Represents a single fact in the knowledge graph.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    id: Optional[str] = None
    content: str = Field(description="The actual content/statement of the fact")
    source: str = Field(description="Source of this fact")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence level in this fact")
    timestamp: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1, description="Version number for tracking changes")

    # Semantic information
    domain: Optional[str] = None
    topic: Optional[str] = None
<<<<<<< HEAD
    keywords: List[str] = Field(default_factory=list)

    # Relationships
    relations: List[KnowledgeRelation] = Field(default_factory=list)

    # Provenance and validation
    validation_status: str = Field(default="unvalidated", description="Validation status")
    validation_history: List[Dict[str, Any]] = Field(default_factory=list)

=======
    keywords: list[str] = Field(default_factory=list)
    
    # Relationships
    relations: list[KnowledgeRelation] = Field(default_factory=list)
    
    # Provenance and validation
    validation_status: str = Field(default="unvalidated", description="Validation status")
    validation_history: list[dict[str, Any]] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Access and usage tracking
    access_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None

    # Metadata
<<<<<<< HEAD
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

=======
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    def add_relation(self, relation: KnowledgeRelation) -> None:
        """Add a relationship to this fact."""
        self.relations.append(relation)
        self.last_updated = datetime.now()

    def update_confidence(self, new_confidence: float, reason: str = "") -> None:
        """Update the confidence level of this fact."""
        old_confidence = self.confidence
        self.confidence = new_confidence
        self.last_updated = datetime.now()
        self.version += 1

        # Record the change in validation history
        self.validation_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": "confidence_update",
            "old_confidence": old_confidence,
            "new_confidence": new_confidence,
            "reason": reason
        })

    def mark_accessed(self) -> None:
        """Mark this fact as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class KnowledgeQuery(BaseModel):
    """Query specification for searching knowledge facts.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    content: Optional[str] = None
    source: Optional[str] = None
    domain: Optional[str] = None
    topic: Optional[str] = None
<<<<<<< HEAD
    keywords: List[str] = Field(default_factory=list)

=======
    keywords: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Confidence and validation filters
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    max_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_status: Optional[str] = None

    # Relationship filters
    relation_filter: Optional[dict[str, Any]] = None
    related_to_fact_id: Optional[str] = None
<<<<<<< HEAD
    relation_types: List[RelationType] = Field(default_factory=list)

=======
    relation_types: list[RelationType] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Temporal filters
    time_range: Optional[tuple[datetime, datetime]] = None
    updated_since: Optional[datetime] = None

    # Metadata filters
<<<<<<< HEAD
    metadata_filter: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)

=======
    metadata_filter: Optional[dict[str, Any]] = None
    tags: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Result options
    limit: int = Field(default=10, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="relevance")  # relevance, confidence, timestamp, access_count
    sort_order: str = Field(default="desc")  # asc, desc

    # Semantic search options
    semantic_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    include_related: bool = Field(default=False)
    max_relation_depth: int = Field(default=2, ge=1, le=5)


class ConflictResolution(BaseModel):
    """Result of resolving conflicts between knowledge facts.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    resolved_fact: KnowledgeFact
    conflicting_facts: list[KnowledgeFact]
    resolution_strategy: ConflictResolutionStrategy
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    evidence: list[str] = Field(default_factory=list)
    resolved_at: datetime = Field(default_factory=datetime.now)
    resolved_by: Optional[str] = None  # Agent or user ID
    metadata: dict[str, Any] = Field(default_factory=dict)


class Memory(BaseModel):
    """Represents a memory item in the system.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    id: Optional[str] = None
    content: str
    memory_type: MemoryType
    owner_id: str  # Role ID, user ID, or system ID

    # Importance and relevance
    importance: float = Field(ge=0.0, le=1.0, description="Importance of this memory")
    relevance_context: Optional[str] = None

    # Temporal information
    timestamp: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)

    # Relationships and associations
<<<<<<< HEAD
    related_memories: List[str] = Field(default_factory=list, description="IDs of related memories")
    associated_facts: List[str] = Field(default_factory=list, description="IDs of associated knowledge facts")

    # Context and metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

=======
    related_memories: list[str] = Field(default_factory=list, description="IDs of related memories")
    associated_facts: list[str] = Field(default_factory=list, description="IDs of associated knowledge facts")
    
    # Context and metadata
    context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    def mark_accessed(self) -> None:
        """Mark this memory as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class MemoryQuery(BaseModel):
    """Query specification for searching memories.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    owner_id: Optional[str] = None

    # Importance and relevance filters
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_context: Optional[str] = None

    # Temporal filters
    time_range: Optional[tuple[datetime, datetime]] = None
    accessed_since: Optional[datetime] = None

    # Relationship filters
    related_to_memory: Optional[str] = None
    associated_with_fact: Optional[str] = None

    # Metadata filters
<<<<<<< HEAD
    metadata_filter: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)

=======
    metadata_filter: Optional[dict[str, Any]] = None
    tags: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Result options
    limit: int = Field(default=10, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="relevance")  # relevance, importance, timestamp, access_count
    sort_order: str = Field(default="desc")  # asc, desc


class WikiPage(BaseModel):
    """Represents a wiki page in the system.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    id: str
    title: str
    content: str
    version: int = Field(default=1)

    # Authorship and editing
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
<<<<<<< HEAD
    contributors: List[str] = Field(default_factory=list)

    # Organization
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Relationships
    linked_pages: List[str] = Field(default_factory=list, description="IDs of linked wiki pages")
    associated_facts: List[str] = Field(default_factory=list, description="IDs of associated knowledge facts")

=======
    contributors: list[str] = Field(default_factory=list)
    
    # Organization
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    
    # Relationships
    linked_pages: list[str] = Field(default_factory=list, description="IDs of linked wiki pages")
    associated_facts: list[str] = Field(default_factory=list, description="IDs of associated knowledge facts")
    
>>>>>>> feature/core-services-refactor
    # Access tracking
    view_count: int = Field(default=0)
    last_viewed: Optional[datetime] = None

    # Metadata
<<<<<<< HEAD
    metadata: Dict[str, Any] = Field(default_factory=dict)

=======
    metadata: dict[str, Any] = Field(default_factory=dict)
    
>>>>>>> feature/core-services-refactor
    def mark_viewed(self) -> None:
        """Mark this page as viewed."""
        self.view_count += 1
        self.last_viewed = datetime.now()


class SessionState(BaseModel):
    """Represents session state information.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    session_id: str
    user_id: Optional[str] = None

    # Session data
<<<<<<< HEAD
    state_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

=======
    state_data: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    
>>>>>>> feature/core-services-refactor
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Associated entities
<<<<<<< HEAD
    active_roles: List[str] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

=======
    active_roles: list[str] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectState(BaseModel):
    """Represents project state and configuration.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    project_id: str
    name: str
    description: Optional[str] = None

    # Configuration
<<<<<<< HEAD
    config: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

=======
    config: dict[str, Any] = Field(default_factory=dict)
    settings: dict[str, Any] = Field(default_factory=dict)
    
>>>>>>> feature/core-services-refactor
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Associated entities
<<<<<<< HEAD
    participants: List[str] = Field(default_factory=list)
    associated_sessions: List[str] = Field(default_factory=list)

    # Resources and artifacts
    resources: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)

=======
    participants: list[str] = Field(default_factory=list)
    associated_sessions: list[str] = Field(default_factory=list)
    
    # Resources and artifacts
    resources: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Metadata
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Represents a search result from the SSKG.
    """
<<<<<<< HEAD

    item: Union[KnowledgeFact, Memory, WikiPage]
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_type: str  # exact, semantic, related, etc.
    match_details: Dict[str, Any] = Field(default_factory=dict)

    # Context information
    context_snippet: Optional[str] = None
    highlighted_terms: List[str] = Field(default_factory=list)

=======
    item: Union[KnowledgeFact, Memory, WikiPage]
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_type: str  # exact, semantic, related, etc.
    match_details: dict[str, Any] = Field(default_factory=dict)
    
    # Context information
    context_snippet: Optional[str] = None
    highlighted_terms: list[str] = Field(default_factory=list)
    
>>>>>>> feature/core-services-refactor
    # Relationship information (if applicable)
    relationship_path: list[str] = Field(default_factory=list)
    relationship_strength: Optional[float] = None


class SSKGStats(BaseModel):
    """Statistics about the SSKG system.
    """
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    # Content statistics
    total_facts: int = 0
    total_memories: int = 0
    total_wiki_pages: int = 0
    total_relations: int = 0

    # Quality metrics
    average_fact_confidence: float = 0.0
    validated_facts_percentage: float = 0.0

    # Usage statistics
    total_queries: int = 0
    average_query_response_time: float = 0.0

    # Storage statistics
    storage_size_mb: float = 0.0
    index_size_mb: float = 0.0

    # Temporal information
    last_updated: datetime = Field(default_factory=datetime.now)

    # Breakdown by type/category
<<<<<<< HEAD
    facts_by_domain: Dict[str, int] = Field(default_factory=dict)
    memories_by_type: Dict[str, int] = Field(default_factory=dict)
    queries_by_type: Dict[str, int] = Field(default_factory=dict)
=======
    facts_by_domain: dict[str, int] = Field(default_factory=dict)
    memories_by_type: dict[str, int] = Field(default_factory=dict)
    queries_by_type: dict[str, int] = Field(default_factory=dict)
>>>>>>> feature/core-services-refactor
