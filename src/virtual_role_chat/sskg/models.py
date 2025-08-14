"""Data models for the Semantic Structured Knowledge Graph (SSKG).

This module defines the core data models used by the SSKG system,
including knowledge facts, relations, queries, and various memory types.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

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

    id: Optional[str] = None
    relation_type: RelationType
    target_fact_id: str
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this relationship")
    evidence: List[str] = Field(default_factory=list, description="Evidence supporting this relationship")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None  # Agent or user ID


class KnowledgeFact(BaseModel):
    """Represents a single fact in the knowledge graph.
    """

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
    keywords: List[str] = Field(default_factory=list)

    # Relationships
    relations: List[KnowledgeRelation] = Field(default_factory=list)

    # Provenance and validation
    validation_status: str = Field(default="unvalidated", description="Validation status")
    validation_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Access and usage tracking
    access_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

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

    content: Optional[str] = None
    source: Optional[str] = None
    domain: Optional[str] = None
    topic: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)

    # Confidence and validation filters
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    max_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_status: Optional[str] = None

    # Relationship filters
    relation_filter: Optional[Dict[str, Any]] = None
    related_to_fact_id: Optional[str] = None
    relation_types: List[RelationType] = Field(default_factory=list)

    # Temporal filters
    time_range: Optional[Tuple[datetime, datetime]] = None
    updated_since: Optional[datetime] = None

    # Metadata filters
    metadata_filter: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)

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

    resolved_fact: KnowledgeFact
    conflicting_facts: List[KnowledgeFact]
    resolution_strategy: ConflictResolutionStrategy
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    evidence: List[str] = Field(default_factory=list)
    resolved_at: datetime = Field(default_factory=datetime.now)
    resolved_by: Optional[str] = None  # Agent or user ID
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Memory(BaseModel):
    """Represents a memory item in the system.
    """

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
    related_memories: List[str] = Field(default_factory=list, description="IDs of related memories")
    associated_facts: List[str] = Field(default_factory=list, description="IDs of associated knowledge facts")

    # Context and metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    def mark_accessed(self) -> None:
        """Mark this memory as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class MemoryQuery(BaseModel):
    """Query specification for searching memories.
    """

    content: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    owner_id: Optional[str] = None

    # Importance and relevance filters
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    relevance_context: Optional[str] = None

    # Temporal filters
    time_range: Optional[Tuple[datetime, datetime]] = None
    accessed_since: Optional[datetime] = None

    # Relationship filters
    related_to_memory: Optional[str] = None
    associated_with_fact: Optional[str] = None

    # Metadata filters
    metadata_filter: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)

    # Result options
    limit: int = Field(default=10, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="relevance")  # relevance, importance, timestamp, access_count
    sort_order: str = Field(default="desc")  # asc, desc


class WikiPage(BaseModel):
    """Represents a wiki page in the system.
    """

    id: str
    title: str
    content: str
    version: int = Field(default=1)

    # Authorship and editing
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    contributors: List[str] = Field(default_factory=list)

    # Organization
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Relationships
    linked_pages: List[str] = Field(default_factory=list, description="IDs of linked wiki pages")
    associated_facts: List[str] = Field(default_factory=list, description="IDs of associated knowledge facts")

    # Access tracking
    view_count: int = Field(default=0)
    last_viewed: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_viewed(self) -> None:
        """Mark this page as viewed."""
        self.view_count += 1
        self.last_viewed = datetime.now()


class SessionState(BaseModel):
    """Represents session state information.
    """

    session_id: str
    user_id: Optional[str] = None

    # Session data
    state_data: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)

    # Temporal information
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Associated entities
    active_roles: List[str] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectState(BaseModel):
    """Represents project state and configuration.
    """

    project_id: str
    name: str
    description: Optional[str] = None

    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)

    # Temporal information
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Associated entities
    participants: List[str] = Field(default_factory=list)
    associated_sessions: List[str] = Field(default_factory=list)

    # Resources and artifacts
    resources: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Represents a search result from the SSKG.
    """

    item: Union[KnowledgeFact, Memory, WikiPage]
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_type: str  # exact, semantic, related, etc.
    match_details: Dict[str, Any] = Field(default_factory=dict)

    # Context information
    context_snippet: Optional[str] = None
    highlighted_terms: List[str] = Field(default_factory=list)

    # Relationship information (if applicable)
    relationship_path: List[str] = Field(default_factory=list)
    relationship_strength: Optional[float] = None


class SSKGStats(BaseModel):
    """Statistics about the SSKG system.
    """

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
    facts_by_domain: Dict[str, int] = Field(default_factory=dict)
    memories_by_type: Dict[str, int] = Field(default_factory=dict)
    queries_by_type: Dict[str, int] = Field(default_factory=dict)
