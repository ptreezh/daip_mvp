"""
Production-level Memory Management System for Personal Assistant

This module provides comprehensive memory capabilities including:
- Layered memory architecture (short-term, long-term, working memory)
- Semantic memory storage and retrieval with vector embeddings
- Episodic memory with temporal and contextual indexing
- Forgetting curves and memory consolidation
- Memory compression and optimization
- Knowledge graph construction and traversal
- Context-aware memory retrieval
- Memory import/export and backup systems
"""

import asyncio
import uuid
import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
import hashlib
import pickle
import threading
from collections import defaultdict, deque
import faiss
# import sentence_transformers  # Using mock implementation instead
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import spacy
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"      # Working memory, temporary context
    LONG_TERM = "long_term"        # Persistent knowledge
    EPISODIC = "episodic"         # Personal experiences
    SEMANTIC = "semantic"         # General knowledge
    PROCEDURAL = "procedural"     # Skills and procedures
    WORKING = "working"           # Current active processing


class MemoryStrength(Enum):
    """Memory strength levels for forgetting curves"""
    VERY_WEAK = 1
    WEAK = 2
    NORMAL = 3
    STRONG = 4
    VERY_STRONG = 5


class MemoryConsolidationLevel(Enum):
    """Memory consolidation levels"""
    ENCODING = "encoding"         # Initial encoding
    CONSOLIDATION = "consolidation"  # Being consolidated
    STABLE = "stable"            # Stable long-term memory
    REINFORCED = "reinforced"    # Reinforced through recall


@dataclass
class MemoryMetadata:
    """Metadata for memory entries"""
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance_score: float = 0.5
    emotional_weight: float = 0.0
    context_tags: List[str] = field(default_factory=list)
    source: Optional[str] = None
    confidence: float = 1.0
    version: int = 1
    checksum: Optional[str] = None


@dataclass
class MemoryMetrics:
    """Memory access and performance metrics"""
    retrieval_count: int = 0
    retrieval_success_rate: float = 1.0
    average_retrieval_time_ms: float = 0.0
    consolidation_score: float = 0.0
    forgetting_rate: float = 0.0
    last_consolidation: Optional[datetime] = None
    memory_efficiency: float = 1.0


@dataclass
class MemoryFragment:
    """A fragment of memory with rich metadata"""
    id: str
    content: str
    memory_type: MemoryType
    embedding: Optional[np.ndarray] = None
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
    metrics: MemoryMetrics = field(default_factory=MemoryMetrics)
    related_memories: Set[str] = field(default_factory=set)
    strength: MemoryStrength = MemoryStrength.NORMAL
    consolidation_level: MemoryConsolidationLevel = MemoryConsolidationLevel.ENCODING
    context_vector: Optional[Dict[str, float]] = field(default_factory=dict)
    temporal_context: Optional[Dict[str, Any]] = field(default_factory=dict)
    spatial_context: Optional[Dict[str, Any]] = field(default_factory=dict)

    def calculate_relevance_score(self, query_embedding: np.ndarray,
                                 context_weights: Dict[str, float] = None) -> float:
        """Calculate relevance score for retrieval"""
        if self.embedding is None or query_embedding is None:
            return 0.0

        # Semantic similarity
        semantic_similarity = float(np.dot(self.embedding, query_embedding) /
                                   (np.linalg.norm(self.embedding) * np.linalg.norm(query_embedding)))

        # Strength weighting
        strength_weight = self.strength.value / 5.0

        # Recency weighting (time decay)
        time_diff = datetime.now() - self.metadata.last_accessed
        recency_weight = np.exp(-time_diff.days / 365.0)  # 1-year decay

        # Importance weighting
        importance_weight = self.metadata.importance_score

        # Access frequency weighting
        frequency_weight = min(self.metrics.retrieval_count / 10.0, 1.0)

        # Context matching
        context_weight = 1.0
        if context_weights and self.context_vector:
            context_overlap = sum(min(context_weights.get(k, 0), v)
                                for k, v in self.context_vector.items())
            context_weight = min(context_overlap + 0.5, 1.0)

        # Combine weights
        total_score = (
            semantic_similarity * 0.3 +
            strength_weight * 0.2 +
            recency_weight * 0.15 +
            importance_weight * 0.15 +
            frequency_weight * 0.1 +
            context_weight * 0.1
        )

        return float(total_score)

    def update_access(self, importance_adjustment: float = 0.0) -> None:
        """Update access metrics"""
        self.metadata.last_accessed = datetime.now()
        self.metrics.retrieval_count += 1
        self.metadata.importance_score = max(0.0, min(1.0,
            self.metadata.importance_score + importance_adjustment))

        # Potentially strengthen memory
        if self.metrics.retrieval_count % 5 == 0:
            current_strength = self.strength.value
            if current_strength < MemoryStrength.VERY_STRONG.value:
                self.strength = MemoryStrength(current_strength + 1)


class MemoryIndex:
    """Efficient memory indexing for fast retrieval"""

    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.faiss_index = None
        self.id_to_index = {}
        self.index_to_id = {}
        self._build_index()

    def _build_index(self) -> None:
        """Build FAISS index for similarity search"""
        self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity

    def add_memory(self, memory_id: str, embedding: np.ndarray) -> None:
        """Add memory to index"""
        if embedding is None:
            return

        # Normalize for cosine similarity
        normalized_embedding = embedding / np.linalg.norm(embedding)

        index = self.faiss_index.ntotal
        self.faiss_index.add(normalized_embedding.reshape(1, -1))
        self.id_to_index[memory_id] = index
        self.index_to_id[index] = memory_id

    def search_similar(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar memories"""
        if self.faiss_index.ntotal == 0 or query_embedding is None:
            return []

        # Normalize query embedding
        normalized_query = query_embedding / np.linalg.norm(query_embedding)

        # Search
        scores, indices = self.faiss_index.search(normalized_query.reshape(1, -1), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx in self.index_to_id:
                memory_id = self.index_to_id[idx]
                results.append((memory_id, float(score)))

        return results

    def remove_memory(self, memory_id: str) -> bool:
        """Remove memory from index (note: FAISS doesn't support efficient removal)"""
        # This is inefficient - would need to rebuild index
        # For production, consider using a different approach
        if memory_id in self.id_to_index:
            del self.id_to_index[memory_id]
            # Note: FAISS removal requires rebuilding index
            return True
        return False


class MemoryConsolidator:
    """Handles memory consolidation and forgetting"""

    def __init__(self):
        self.consolidation_threshold = 0.7
        self.forgetting_rate_base = 0.1
        self.consolidation_interval_hours = 24
        self.consolidation_strategy = "spaced_repetition"

    def calculate_consolidation_need(self, memory: MemoryFragment) -> float:
        """Calculate how much consolidation is needed"""
        factors = {
            'age': self._calculate_age_factor(memory),
            'access_frequency': self._calculate_frequency_factor(memory),
            'importance': memory.metadata.importance_score,
            'strength': memory.strength.value / 5.0,
            'emotional_weight': memory.metadata.emotional_weight
        }

        # Weighted combination
        consolidation_need = (
            factors['age'] * 0.3 +
            factors['access_frequency'] * 0.25 +
            factors['importance'] * 0.2 +
            factors['strength'] * 0.15 +
            factors['emotional_weight'] * 0.1
        )

        return consolidation_need

    def _calculate_age_factor(self, memory: MemoryFragment) -> float:
        """Calculate age-based consolidation factor"""
        age_days = (datetime.now() - memory.metadata.created_at).days
        # Younger memories need more consolidation
        return max(0.0, 1.0 - age_days / 365.0)

    def _calculate_frequency_factor(self, memory: MemoryFragment) -> float:
        """Calculate frequency-based consolidation factor"""
        return min(memory.metrics.retrieval_count / 10.0, 1.0)

    def calculate_forgetting_probability(self, memory: MemoryFragment) -> float:
        """Calculate probability of forgetting using Ebbinghaus forgetting curve"""
        if memory.consolidation_level == MemoryConsolidationLevel.STABLE:
            return 0.01  # Very low forgetting rate for stable memories

        # Base forgetting rate
        time_since_last_access = (datetime.now() - memory.metadata.last_accessed).days
        forgetting_rate = self.forgetting_rate_base * np.exp(-time_since_last_access / 7.0)

        # Adjust by strength and importance
        strength_multiplier = 1.0 - (memory.strength.value / 5.0) * 0.8
        importance_multiplier = 1.0 - memory.metadata.importance_score * 0.5

        forgetting_probability = forgetting_rate * strength_multiplier * importance_multiplier
        return max(0.0, min(1.0, forgetting_probability))

    def should_consolidate(self, memory: MemoryFragment) -> bool:
        """Determine if memory should be consolidated"""
        consolidation_need = self.calculate_consolidation_need(memory)
        return consolidation_need >= self.consolidation_threshold


class MemoryKnowledgeGraph:
    """Knowledge graph for memory relationships"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_index = defaultdict(set)
        self.relation_index = defaultdict(set)

    def add_memory_node(self, memory: MemoryFragment) -> None:
        """Add memory as node in knowledge graph"""
        self.graph.add_node(
            memory.id,
            memory_type=memory.memory_type.value,
            content=memory.content[:100],  # Preview
            importance=memory.metadata.importance_score,
            created_at=memory.metadata.created_at.isoformat(),
            strength=memory.strength.value
        )

    def add_relationship(self, memory1_id: str, memory2_id: str,
                        relation_type: str, weight: float = 1.0) -> None:
        """Add relationship between memories"""
        self.graph.add_edge(memory1_id, memory2_id,
                           type=relation_type, weight=weight)
        self.relation_index[relation_type].add((memory1_id, memory2_id))

    def find_related_memories(self, memory_id: str,
                             max_depth: int = 2) -> List[Tuple[str, float]]:
        """Find related memories using graph traversal"""
        if memory_id not in self.graph:
            return []

        related = []
        visited = set()
        queue = [(memory_id, 0, 1.0)]  # (node_id, depth, weight)

        while queue:
            current_id, depth, weight = queue.pop(0)

            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)

            if current_id != memory_id:
                related.append((current_id, weight))

            # Explore neighbors
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in visited:
                    edge_weight = self.graph[current_id][neighbor].get('weight', 1.0)
                    new_weight = weight * edge_weight * 0.8  # Decay with depth
                    queue.append((neighbor, depth + 1, new_weight))

        return sorted(related, key=lambda x: x[1], reverse=True)

    def get_central_memories(self, top_k: int = 10) -> List[Tuple[str, float]]:
        """Get most central memories in the knowledge graph"""
        centrality_scores = nx.betweenness_centrality(self.graph)
        sorted_memories = sorted(centrality_scores.items(),
                               key=lambda x: x[1], reverse=True)
        return sorted_memories[:top_k]


class MemoryManager:
    """Production-level Memory Manager with comprehensive functionality"""

    def __init__(self, storage_path: Optional[str] = None,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.storage_path = Path(storage_path) if storage_path else Path("data/memory.db")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize components (mock implementation)
        self.embedding_dim = 384  # Default embedding dimension
        # self.embedding_model = sentence_transformers.SentenceTransformer(embedding_model)
        # self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Memory storage
        self.memories: Dict[str, MemoryFragment] = {}
        self.short_term_memory = deque(maxlen=50)  # Recent memories
        self.working_memory = deque(maxlen=20)    # Active context

        # Indexing and search
        self.memory_index = MemoryIndex(self.embedding_dim)
        self.knowledge_graph = MemoryKnowledgeGraph()

        # Consolidation and maintenance
        self.consolidator = MemoryConsolidator()
        self.consolidation_task: Optional[asyncio.Task] = None
        self.maintenance_active = False

        # Performance tracking
        self.access_times = deque(maxlen=1000)
        self.cache_hit_rate = 0.0

        # Threading
        self._lock = threading.RLock()

        # Database initialization
        self._init_database()

        # Load existing memories
        self._load_memories()

    def _init_database(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    embedding BLOB,
                    metadata TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    strength INTEGER NOT NULL,
                    consolidation_level TEXT NOT NULL,
                    context_vector TEXT,
                    temporal_context TEXT,
                    spatial_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_relationships (
                    id TEXT PRIMARY KEY,
                    memory1_id TEXT NOT NULL,
                    memory2_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory1_id) REFERENCES memories (id),
                    FOREIGN KEY (memory2_id) REFERENCES memories (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_access_log (
                    id TEXT PRIMARY KEY,
                    memory_id TEXT NOT NULL,
                    access_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    context TEXT,
                    FOREIGN KEY (memory_id) REFERENCES memories (id)
                )
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories (memory_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_strength ON memories (strength)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_created ON memories (created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_relationships_type ON memory_relationships (relation_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_access_timestamp ON memory_access_log (timestamp)")

            conn.commit()

    def _load_memories(self) -> None:
        """Load memories from database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("""
                    SELECT id, content, memory_type, embedding, metadata, metrics,
                           strength, consolidation_level, context_vector, temporal_context,
                           spatial_context
                    FROM memories
                """)

                for row in cursor.fetchall():
                    try:
                        memory_id = row[0]
                        content = row[1]
                        memory_type = MemoryType(row[2])

                        # Deserialize embedding
                        embedding = None
                        if row[3]:
                            embedding = pickle.loads(row[3])

                        # Deserialize metadata
                        metadata_dict = json.loads(row[4])
                        metadata = MemoryMetadata(
                            created_at=datetime.fromisoformat(metadata_dict['created_at']),
                            last_accessed=datetime.fromisoformat(metadata_dict['last_accessed']),
                            access_count=metadata_dict['access_count'],
                            importance_score=metadata_dict['importance_score'],
                            emotional_weight=metadata_dict['emotional_weight'],
                            context_tags=metadata_dict['context_tags'],
                            source=metadata_dict['source'],
                            confidence=metadata_dict['confidence'],
                            version=metadata_dict['version'],
                            checksum=metadata_dict['checksum']
                        )

                        # Deserialize metrics
                        metrics_dict = json.loads(row[5])
                        metrics = MemoryMetrics(
                            retrieval_count=metrics_dict['retrieval_count'],
                            retrieval_success_rate=metrics_dict['retrieval_success_rate'],
                            average_retrieval_time_ms=metrics_dict['average_retrieval_time_ms'],
                            consolidation_score=metrics_dict['consolidation_score'],
                            forgetting_rate=metrics_dict['forgetting_rate'],
                            last_consolidation=datetime.fromisoformat(metrics_dict['last_consolidation']) if metrics_dict['last_consolidation'] else None,
                            memory_efficiency=metrics_dict['memory_efficiency']
                        )

                        # Deserialize other fields
                        strength = MemoryStrength(row[6])
                        consolidation_level = MemoryConsolidationLevel(row[7])
                        context_vector = json.loads(row[8]) if row[8] else {}
                        temporal_context = json.loads(row[9]) if row[9] else {}
                        spatial_context = json.loads(row[10]) if row[10] else {}

                        # Create memory fragment
                        memory = MemoryFragment(
                            id=memory_id,
                            content=content,
                            memory_type=memory_type,
                            embedding=embedding,
                            metadata=metadata,
                            metrics=metrics,
                            strength=strength,
                            consolidation_level=consolidation_level,
                            context_vector=context_vector,
                            temporal_context=temporal_context,
                            spatial_context=spatial_context
                        )

                        self.memories[memory_id] = memory

                        # Add to index
                        if embedding is not None:
                            self.memory_index.add_memory(memory_id, embedding)

                        # Add to knowledge graph
                        self.knowledge_graph.add_memory_node(memory)

                        # Add to short-term memory if recent
                        if (datetime.now() - metadata.last_accessed).hours < 1:
                            self.short_term_memory.append(memory_id)

                    except Exception as e:
                        logger.error(f"Failed to load memory {row[0]}: {e}")

                # Load relationships
                cursor = conn.execute("""
                    SELECT memory1_id, memory2_id, relation_type, weight
                    FROM memory_relationships
                """)

                for row in cursor.fetchall():
                    self.knowledge_graph.add_relationship(row[0], row[1], row[2], row[3])

            logger.info(f"Loaded {len(self.memories)} memories from database")

        except Exception as e:
            logger.error(f"Failed to load memories: {e}")

    def _save_memory(self, memory: MemoryFragment) -> None:
        """Save memory to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories
                    (id, content, memory_type, embedding, metadata, metrics,
                     strength, consolidation_level, context_vector, temporal_context,
                     spatial_context, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    memory.content,
                    memory.memory_type.value,
                    pickle.dumps(memory.embedding) if memory.embedding is not None else None,
                    json.dumps({
                        'created_at': memory.metadata.created_at.isoformat(),
                        'last_accessed': memory.metadata.last_accessed.isoformat(),
                        'access_count': memory.metadata.access_count,
                        'importance_score': memory.metadata.importance_score,
                        'emotional_weight': memory.metadata.emotional_weight,
                        'context_tags': memory.metadata.context_tags,
                        'source': memory.metadata.source,
                        'confidence': memory.metadata.confidence,
                        'version': memory.metadata.version,
                        'checksum': memory.metadata.checksum
                    }),
                    json.dumps({
                        'retrieval_count': memory.metrics.retrieval_count,
                        'retrieval_success_rate': memory.metrics.retrieval_success_rate,
                        'average_retrieval_time_ms': memory.metrics.average_retrieval_time_ms,
                        'consolidation_score': memory.metrics.consolidation_score,
                        'forgetting_rate': memory.metrics.forgetting_rate,
                        'last_consolidation': memory.metrics.last_consolidation.isoformat() if memory.metrics.last_consolidation else None,
                        'memory_efficiency': memory.metrics.memory_efficiency
                    }),
                    memory.strength.value,
                    memory.consolidation_level.value,
                    json.dumps(memory.context_vector),
                    json.dumps(memory.temporal_context),
                    json.dumps(memory.spatial_context),
                    datetime.now().isoformat()
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to save memory {memory.id}: {e}")

    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.LONG_TERM,
        importance_score: float = 0.5,
        emotional_weight: float = 0.0,
        context_tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        context_vector: Optional[Dict[str, float]] = None,
        temporal_context: Optional[Dict[str, Any]] = None,
        spatial_context: Optional[Dict[str, Any]] = None,
        related_memories: Optional[List[str]] = None
    ) -> str:
        """Store a new memory with comprehensive metadata"""
        start_time = datetime.now()

        # Generate embedding (mock implementation)
        embedding = self._mock_encode(content)

        # Generate content checksum
        checksum = hashlib.md5(content.encode()).hexdigest()

        # Create memory fragment
        memory = MemoryFragment(
            id=str(uuid.uuid4()),
            content=content,
            memory_type=memory_type,
            embedding=embedding,
            metadata=MemoryMetadata(
                importance_score=importance_score,
                emotional_weight=emotional_weight,
                context_tags=context_tags or [],
                source=source,
                checksum=checksum
            ),
            context_vector=context_vector or {},
            temporal_context=temporal_context or {},
            spatial_context=spatial_context or {}
        )

        # Store memory
        with self._lock:
            self.memories[memory.id] = memory

            # Add to appropriate memory stores
            if memory_type == MemoryType.SHORT_TERM:
                self.short_term_memory.append(memory.id)
            elif memory_type == MemoryType.WORKING:
                self.working_memory.append(memory.id)

            # Add to search index
            self.memory_index.add_memory(memory.id, embedding)

            # Add to knowledge graph
            self.knowledge_graph.add_memory_node(memory)

            # Add relationships
            if related_memories:
                for related_id in related_memories:
                    if related_id in self.memories:
                        self.knowledge_graph.add_relationship(
                            memory.id, related_id, "related", 0.8
                        )
                        memory.related_memories.add(related_id)
                        self.memories[related_id].related_memories.add(memory.id)

        # Save to database
        self._save_memory(memory)

        # Log access
        await self._log_memory_access(memory.id, "store")

        # Update performance metrics
        access_time = (datetime.now() - start_time).total_seconds() * 1000
        self.access_times.append(access_time)

        logger.debug(f"Stored memory: {memory.id[:8]}... (type: {memory_type.value})")
        return memory.id

    async def retrieve_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        context_weights: Optional[Dict[str, float]] = None,
        max_results: int = 10,
        min_relevance: float = 0.1,
        include_related: bool = True
    ) -> List[Tuple[MemoryFragment, float]]:
        """Retrieve memories based on semantic similarity and context"""
        start_time = datetime.now()

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search in index
        similar_memories = self.memory_index.search_similar(query_embedding, max_results * 2)

        results = []

        with self._lock:
            for memory_id, similarity_score in similar_memories:
                if memory_id not in self.memories:
                    continue

                memory = self.memories[memory_id]

                # Filter by type if specified
                if memory_type and memory.memory_type != memory_type:
                    continue

                # Calculate comprehensive relevance score
                relevance_score = memory.calculate_relevance_score(query_embedding, context_weights)

                # Filter by minimum relevance
                if relevance_score < min_relevance:
                    continue

                results.append((memory, relevance_score))

                # Include related memories if requested
                if include_related and len(results) < max_results:
                    related_memories = self.knowledge_graph.find_related_memories(
                        memory_id, max_depth=2
                    )
                    for related_id, relation_weight in related_memories:
                        if related_id in self.memories and len(results) < max_results:
                            related_memory = self.memories[related_id]
                            adjusted_score = relevance_score * relation_weight * 0.7

                            if adjusted_score >= min_relevance:
                                results.append((related_memory, adjusted_score))

        # Sort by relevance and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:max_results]

        # Update access metrics for retrieved memories
        for memory, _ in results:
            memory.update_access(0.01)  # Small importance boost
            self._save_memory(memory)
            await self._log_memory_access(memory.id, "retrieve")

        # Update performance metrics
        access_time = (datetime.now() - start_time).total_seconds() * 1000
        self.access_times.append(access_time)

        logger.debug(f"Retrieved {len(results)} memories for query: {query[:50]}...")
        return results

    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryFragment]:
        """Get memory by ID"""
        with self._lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.update_access(0.02)
                self._save_memory(memory)
                await self._log_memory_access(memory_id, "get_by_id")
            return memory

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        importance_score: Optional[float] = None,
        emotional_weight: Optional[float] = None,
        context_tags: Optional[List[str]] = None,
        context_vector: Optional[Dict[str, float]] = None
    ) -> bool:
        """Update existing memory"""
        with self._lock:
            if memory_id not in self.memories:
                return False

            memory = self.memories[memory_id]
            updated = False

            # Update fields
            if content is not None and content != memory.content:
                memory.content = content
                memory.embedding = self.embedding_model.encode([content])[0]
                memory.metadata.version += 1
                memory.metadata.checksum = hashlib.md5(content.encode()).hexdigest()
                updated = True

            if importance_score is not None:
                memory.metadata.importance_score = max(0.0, min(1.0, importance_score))
                updated = True

            if emotional_weight is not None:
                memory.metadata.emotional_weight = max(0.0, min(1.0, emotional_weight))
                updated = True

            if context_tags is not None:
                memory.metadata.context_tags = context_tags
                updated = True

            if context_vector is not None:
                memory.context_vector = context_vector
                updated = True

            if updated:
                memory.metadata.last_accessed = datetime.now()
                self._save_memory(memory)
                await self._log_memory_access(memory_id, "update")

                # Update index if embedding changed
                if content is not None:
                    self.memory_index.add_memory(memory_id, memory.embedding)

            return updated

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete memory"""
        with self._lock:
            if memory_id not in self.memories:
                return False

            memory = self.memories[memory_id]

            # Remove from all data structures
            del self.memories[memory_id]

            # Remove from memory stores
            if memory_id in self.short_term_memory:
                self.short_term_memory.remove(memory_id)
            if memory_id in self.working_memory:
                self.working_memory.remove(memory_id)

            # Remove from index
            self.memory_index.remove_memory(memory_id)

            # Remove from knowledge graph
            if memory_id in self.knowledge_graph.graph:
                self.knowledge_graph.graph.remove_node(memory_id)

            # Remove from database
            try:
                with sqlite3.connect(self.storage_path) as conn:
                    conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                    conn.execute("DELETE FROM memory_relationships WHERE memory1_id = ? OR memory2_id = ?",
                               (memory_id, memory_id))
                    conn.execute("DELETE FROM memory_access_log WHERE memory_id = ?", (memory_id,))
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to delete memory {memory_id} from database: {e}")

            await self._log_memory_access(memory_id, "delete")
            logger.debug(f"Deleted memory: {memory_id}")
            return True

    async def consolidate_memories(self) -> int:
        """Perform memory consolidation"""
        consolidated_count = 0

        with self._lock:
            memories_to_consolidate = []

            for memory in self.memories.values():
                if self.consolidator.should_consolidate(memory):
                    memories_to_consolidate.append(memory)

            for memory in memories_to_consolidate:
                # Increase consolidation level
                if memory.consolidation_level == MemoryConsolidationLevel.ENCODING:
                    memory.consolidation_level = MemoryConsolidationLevel.CONSOLIDATION
                elif memory.consolidation_level == MemoryConsolidationLevel.CONSOLIDATION:
                    # Check if should become stable
                    consolidation_need = self.consolidator.calculate_consolidation_need(memory)
                    if consolidation_need >= 0.8:
                        memory.consolidation_level = MemoryConsolidationLevel.STABLE

                # Potentially strengthen memory
                forgetting_prob = self.consolidator.calculate_forgetting_probability(memory)
                if forgetting_prob < 0.1 and memory.strength.value < MemoryStrength.VERY_STRONG.value:
                    memory.strength = MemoryStrength(memory.strength.value + 1)

                # Update metrics
                memory.metrics.last_consolidation = datetime.now()
                memory.metrics.consolidation_score = self.consolidator.calculate_consolidation_need(memory)
                memory.metrics.forgetting_rate = forgetting_prob

                self._save_memory(memory)
                consolidated_count += 1

        logger.info(f"Consolidated {consolidated_count} memories")
        return consolidated_count

    async def forget_memories(self) -> int:
        """Perform memory forgetting based on forgetting curves"""
        forgotten_count = 0

        with self._lock:
            memories_to_forget = []

            for memory in self.memories.values():
                if memory.consolidation_level != MemoryConsolidationLevel.STABLE:
                    forgetting_prob = self.consolidator.calculate_forgetting_probability(memory)

                    # Probabilistic forgetting
                    if np.random.random() < forgetting_prob:
                        memories_to_forget.append(memory.id)

            # Forget memories
            for memory_id in memories_to_forget:
                await self.delete_memory(memory_id)
                forgotten_count += 1

        logger.info(f"Forgot {forgotten_count} memories")
        return forgotten_count

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        with self._lock:
            total_memories = len(self.memories)

            # Type distribution
            type_counts = defaultdict(int)
            strength_counts = defaultdict(int)
            consolidation_counts = defaultdict(int)

            importance_scores = []
            access_counts = []
            ages = []

            now = datetime.now()

            for memory in self.memories.values():
                type_counts[memory.memory_type.value] += 1
                strength_counts[memory.strength.value] += 1
                consolidation_counts[memory.consolidation_level.value] += 1

                importance_scores.append(memory.metadata.importance_score)
                access_counts.append(memory.metrics.retrieval_count)
                ages.append((now - memory.metadata.created_at).days)

            # Performance metrics
            avg_access_time = np.mean(self.access_times) if self.access_times else 0

            return {
                "total_memories": total_memories,
                "short_term_count": len(self.short_term_memory),
                "working_memory_count": len(self.working_memory),
                "knowledge_graph_nodes": self.knowledge_graph.graph.number_of_nodes(),
                "knowledge_graph_edges": self.knowledge_graph.graph.number_of_edges(),
                "type_distribution": dict(type_counts),
                "strength_distribution": dict(strength_counts),
                "consolidation_distribution": dict(consolidation_counts),
                "average_importance": np.mean(importance_scores) if importance_scores else 0,
                "average_access_count": np.mean(access_counts) if access_counts else 0,
                "average_age_days": np.mean(ages) if ages else 0,
                "average_access_time_ms": avg_access_time,
                "cache_hit_rate": self.cache_hit_rate
            }

    async def search_memories_advanced(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        temporal_range: Optional[Tuple[datetime, datetime]] = None,
        spatial_constraints: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[Tuple[MemoryFragment, float]]:
        """Advanced memory search with multiple filters"""
        # Basic semantic search first
        base_results = await self.retrieve_memory(query, max_results=max_results * 2)

        if not filters and not temporal_range and not spatial_constraints:
            return base_results

        # Apply filters
        filtered_results = []

        for memory, relevance_score in base_results:
            # Type filter
            if filters and 'memory_type' in filters:
                if memory.memory_type != filters['memory_type']:
                    continue

            # Importance filter
            if filters and 'min_importance' in filters:
                if memory.metadata.importance_score < filters['min_importance']:
                    continue

            # Tag filter
            if filters and 'required_tags' in filters:
                if not any(tag in memory.metadata.context_tags
                          for tag in filters['required_tags']):
                    continue

            # Temporal filter
            if temporal_range:
                start_time, end_time = temporal_range
                if not (start_time <= memory.metadata.created_at <= end_time):
                    continue

            # Spatial filter
            if spatial_constraints and memory.spatial_context:
                # Example spatial constraint matching
                if 'location' in spatial_constraints:
                    if memory.spatial_context.get('location') != spatial_constraints['location']:
                        continue

            filtered_results.append((memory, relevance_score))

        return filtered_results[:max_results]

    async def export_memories(
        self,
        file_path: str,
        memory_types: Optional[List[MemoryType]] = None,
        date_range: Optional[Tuple[datetime, datetime]] = None,
        include_embeddings: bool = False
    ) -> int:
        """Export memories to file"""
        exported_count = 0

        try:
            memories_to_export = []

            with self._lock:
                for memory in self.memories.values():
                    # Apply filters
                    if memory_types and memory.memory_type not in memory_types:
                        continue

                    if date_range:
                        start_date, end_date = date_range
                        if not (start_date <= memory.metadata.created_at <= end_date):
                            continue

                    # Prepare export data
                    export_data = {
                        'id': memory.id,
                        'content': memory.content,
                        'memory_type': memory.memory_type.value,
                        'metadata': {
                            'created_at': memory.metadata.created_at.isoformat(),
                            'importance_score': memory.metadata.importance_score,
                            'context_tags': memory.metadata.context_tags,
                            'source': memory.metadata.source
                        },
                        'metrics': {
                            'retrieval_count': memory.metrics.retrieval_count,
                            'consolidation_score': memory.metrics.consolidation_score
                        }
                    }

                    if include_embeddings and memory.embedding is not None:
                        export_data['embedding'] = memory.embedding.tolist()

                    memories_to_export.append(export_data)
                    exported_count += 1

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memories_to_export, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {exported_count} memories to {file_path}")

        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            raise

        return exported_count

    async def import_memories(self, file_path: str, merge_strategy: str = "skip_duplicates") -> int:
        """Import memories from file"""
        imported_count = 0

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                memories_data = json.load(f)

            for memory_data in memories_data:
                # Check for duplicates
                existing_memory = None
                for memory in self.memories.values():
                    if memory.metadata.checksum == hashlib.md5(memory_data['content'].encode()).hexdigest():
                        existing_memory = memory
                        break

                if existing_memory:
                    if merge_strategy == "skip_duplicates":
                        continue
                    elif merge_strategy == "update_existing":
                        # Update existing memory
                        await self.update_memory(
                            existing_memory.id,
                            content=memory_data['content'],
                            importance_score=memory_data['metadata'].get('importance_score'),
                            context_tags=memory_data['metadata'].get('context_tags')
                        )
                        imported_count += 1
                        continue

                # Create new memory
                embedding = None
                if 'embedding' in memory_data:
                    embedding = np.array(memory_data['embedding'])

                memory = MemoryFragment(
                    id=memory_data['id'],
                    content=memory_data['content'],
                    memory_type=MemoryType(memory_data['memory_type']),
                    embedding=embedding,
                    metadata=MemoryMetadata(
                        created_at=datetime.fromisoformat(memory_data['metadata']['created_at']),
                        importance_score=memory_data['metadata'].get('importance_score', 0.5),
                        context_tags=memory_data['metadata'].get('context_tags', []),
                        source=memory_data['metadata'].get('source'),
                        checksum=hashlib.md5(memory_data['content'].encode()).hexdigest()
                    )
                )

                with self._lock:
                    self.memories[memory.id] = memory
                    if memory.embedding is not None:
                        self.memory_index.add_memory(memory.id, memory.embedding)
                    self.knowledge_graph.add_memory_node(memory)
                    self._save_memory(memory)

                imported_count += 1

            logger.info(f"Imported {imported_count} memories from {file_path}")

        except Exception as e:
            logger.error(f"Failed to import memories: {e}")
            raise

        return imported_count

    async def _log_memory_access(self, memory_id: str, access_type: str) -> None:
        """Log memory access for analytics"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT INTO memory_access_log (id, memory_id, access_type) VALUES (?, ?, ?)",
                    (str(uuid.uuid4()), memory_id, access_type)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log memory access: {e}")

    async def start_maintenance(self) -> None:
        """Start background maintenance tasks"""
        if self.maintenance_active:
            return

        self.maintenance_active = True
        self.consolidation_task = asyncio.create_task(self._maintenance_loop())
        logger.info("Memory maintenance started")

    async def stop_maintenance(self) -> None:
        """Stop background maintenance tasks"""
        self.maintenance_active = False
        if self.consolidation_task:
            self.consolidation_task.cancel()
            try:
                await self.consolidation_task
            except asyncio.CancelledError:
                pass
        logger.info("Memory maintenance stopped")

    async def _maintenance_loop(self) -> None:
        """Background maintenance loop"""
        while self.maintenance_active:
            try:
                # Perform consolidation
                await self.consolidate_memories()

                # Perform forgetting
                await self.forget_memories()

                # Sleep for consolidation interval
                await asyncio.sleep(self.consolidator.consolidation_interval_hours * 3600)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Maintenance loop error: {e}")
                await asyncio.sleep(300)  # 5 minutes on error

    async def shutdown(self) -> None:
        """Shutdown memory manager gracefully"""
        logger.info("Shutting down memory manager")

        # Stop maintenance
        await self.stop_maintenance()

        # Save any pending changes
        with self._lock:
            for memory in self.memories.values():
                self._save_memory(memory)

        logger.info("Memory manager shutdown complete")

    def _mock_encode(self, text: str) -> np.ndarray:
        """Mock embedding function for testing"""
        # Simple hash-based mock embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # Convert hash to numpy array of fixed size
        hash_int = int(text_hash, 16)
        # Generate pseudo-random but deterministic embedding
        embedding = np.array([
            (hash_int >> (i * 8) & 0xFF) / 255.0 - 0.5
            for i in range(self.embedding_dim)
        ])
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding