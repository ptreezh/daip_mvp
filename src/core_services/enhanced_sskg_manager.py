"""@Time    : 2025-07-22 14:00:00
@Author  : DAIP-LIVE Team
@File    : enhanced_sskg_manager.py
@Description:
    Enhanced Semantic Structured Knowledge Graph (SSKG) Manager that serves as a unified
    storage interface for all system memory types including role memories, wiki content,
    user memories, session states, project states, and memory banks.
"""
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import networkx as nx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


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


class KnowledgeQuery(BaseModel):
    """Model for querying the SSKG."""
    node_types: Optional[list[NodeType]] = None
    content_query: Optional[str] = None
    relation_types: Optional[list[RelationType]] = None
    min_confidence: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata_filters: dict[str, Any] = {}
    limit: int = 10
    include_relations: bool = False


class EnhancedSSKGManager:
    """Enhanced Semantic Structured Knowledge Graph Manager that provides a unified
    storage interface for all system memory types.
    """

    def __init__(
        self,
        graph_path: Optional[Path] = None,
        vector_store_path: Optional[Path] = None,
        enable_vector_search: bool = True
    ):
        """Initialize the Enhanced SSKG Manager.
        
        Args:
            graph_path: Path to the graph file for persistence
            vector_store_path: Path to the vector store for semantic search
            enable_vector_search: Whether to enable vector-based semantic search

        """
        self.graph_path = graph_path
        self.vector_store_path = vector_store_path
        self.enable_vector_search = enable_vector_search

        # Initialize the graph
        self.graph = self._load_graph()

        # Initialize vector store if enabled
        self.vector_store = None
        if self.enable_vector_search:
            self._initialize_vector_store()

        logger.info(
            "EnhancedSSKGManager initialized with %d nodes and %d edges.",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )
    def _load_graph(self) -> nx.MultiDiGraph:
        """Load the graph from the specified path, or create a new one."""
        if self.graph_path and self.graph_path.exists():
            try:
                logger.info(f"Loading knowledge graph from {self.graph_path}")
                # Load the graph from file
                loaded_graph = nx.read_graphml(self.graph_path)
                return nx.MultiDiGraph(loaded_graph)
            except Exception as e:
                logger.error(f"Failed to load graph from {self.graph_path}: {e}. Creating new graph.")
        return nx.MultiDiGraph()

    def _initialize_vector_store(self):
        """Initialize the vector store for semantic search."""
        try:
            import chromadb
            from chromadb.config import Settings

            # Create a persistent client
            client = chromadb.PersistentClient(
                path=str(self.vector_store_path) if self.vector_store_path else "./data/vector_store",
                settings=Settings(anonymized_telemetry=False)
            )

            # Create or get the collection
            self.vector_store = client.get_or_create_collection(
                name="sskg_vectors",
                metadata={"description": "Vector embeddings for SSKG nodes"}
            )

            logger.info("Vector store initialized successfully")
        except ImportError:
            logger.warning("chromadb not installed. Vector search disabled.")
            self.enable_vector_search = False
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.enable_vector_search = False

    def save_graph(self):
        """Save the current graph to the specified path."""
        if self.graph_path:
            try:
                # Ensure parent directory exists
                self.graph_path.parent.mkdir(parents=True, exist_ok=True)

                logger.info(f"Saving knowledge graph to {self.graph_path}")
                nx.write_graphml(self.graph, self.graph_path)
            except Exception as e:
                logger.error(f"Failed to save graph to {self.graph_path}: {e}")

    def add_node(self, node: KnowledgeNode) -> str:
        """Add a node to the SSKG.
        
        Args:
            node: The node to add
            
        Returns:
            The ID of the added node

        """
        # Generate ID if not provided
        if not node.id:
            node.id = str(uuid.uuid4())

        # Add node to graph
        self.graph.add_node(
            node.id,
            node_type=node.node_type.value,
            content=node.content,
            created_at=node.created_at.isoformat(),
            updated_at=node.updated_at.isoformat(),
            confidence=node.confidence,
            metadata=json.dumps(node.metadata),
            version=node.version
        )

        # Add to vector store if enabled
        if self.enable_vector_search and self.vector_store:
            try:
                from sentence_transformers import SentenceTransformer

                # Get or create embeddings model
                if not hasattr(self, 'embeddings_model'):
                    self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

                # Generate embedding
                embedding = self.embeddings_model.encode(node.content).tolist()

                # Add to vector store
                self.vector_store.add(
                    ids=[node.id],
                    embeddings=[embedding],
                    metadatas=[{
                        "node_type": node.node_type.value,
                        "confidence": node.confidence,
                        "created_at": node.created_at.isoformat(),
                        **node.metadata
                    }],
                    documents=[node.content]
                )
            except Exception as e:
                logger.error(f"Failed to add node to vector store: {e}")

        logger.debug(f"Added node: {node.id} ({node.node_type})")
        return node.id

    def add_relation(self, relation: KnowledgeRelation) -> bool:
        """Add a relation between two nodes in the SSKG.
        
        Args:
            relation: The relation to add
            
        Returns:
            True if the relation was added successfully, False otherwise

        """
        # Check if nodes exist
        if not self.graph.has_node(relation.source_id) or not self.graph.has_node(relation.target_id):
            logger.error("Cannot add relation: one or both nodes do not exist")
            return False

        # Add edge to graph
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            key=relation.relation_type.value,
            confidence=relation.confidence,
            metadata=json.dumps(relation.metadata),
            created_at=relation.created_at.isoformat()
        )

        logger.debug(f"Added relation: {relation.source_id} --[{relation.relation_type}]--> {relation.target_id}")
        return True

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node from the SSKG by ID.
        
        Args:
            node_id: The ID of the node to get
            
        Returns:
            The node if found, None otherwise

        """
        if not self.graph.has_node(node_id):
            return None

        node_data = self.graph.nodes[node_id]

        try:
            return KnowledgeNode(
                id=node_id,
                node_type=NodeType(node_data.get('node_type', 'fact')),
                content=node_data.get('content', ''),
                created_at=datetime.fromisoformat(node_data.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(node_data.get('updated_at', datetime.now().isoformat())),
                confidence=float(node_data.get('confidence', 1.0)),
                metadata=json.loads(node_data.get('metadata', '{}')),
                version=int(node_data.get('version', 1))
            )
        except Exception as e:
            logger.error(f"Error parsing node data: {e}")
            return None
    
    def update_node(self, node_id: str, updates: dict[str, Any]) -> bool:
        """Update a node in the SSKG.
        
        Args:
            node_id: The ID of the node to update
            updates: Dictionary of attributes to update
            
        Returns:
            True if the node was updated successfully, False otherwise

        """
        if not self.graph.has_node(node_id):
            logger.error(f"Cannot update node: node {node_id} does not exist")
            return False

        # Get current node data
        node = self.get_node(node_id)
        if not node:
            return False

        # Update version
        updates['version'] = node.version + 1
        updates['updated_at'] = datetime.now()

        # Update node attributes
        for key, value in updates.items():
            if key == 'metadata':
                self.graph.nodes[node_id][key] = json.dumps(value)
            elif key in ['created_at', 'updated_at']:
                self.graph.nodes[node_id][key] = value.isoformat()
            else:
                self.graph.nodes[node_id][key] = value

        # Update vector store if content was updated and vector search is enabled
        if 'content' in updates and self.enable_vector_search and self.vector_store:
            try:
                from sentence_transformers import SentenceTransformer

                # Get or create embeddings model
                if not hasattr(self, 'embeddings_model'):
                    self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

                # Generate new embedding
                embedding = self.embeddings_model.encode(updates['content']).tolist()

                # Update in vector store
                self.vector_store.update(
                    ids=[node_id],
                    embeddings=[embedding],
                    metadatas=[{
                        "node_type": node.node_type.value,
                        "confidence": updates.get('confidence', node.confidence),
                        "updated_at": updates['updated_at'].isoformat(),
                        **updates.get('metadata', node.metadata)
                    }],
                    documents=[updates['content']]
                )
            except Exception as e:
                logger.error(f"Failed to update node in vector store: {e}")

        logger.debug(f"Updated node: {node_id}")
        return True

    def delete_node(self, node_id: str) -> bool:
        """Delete a node from the SSKG.
        
        Args:
            node_id: The ID of the node to delete
            
        Returns:
            True if the node was deleted successfully, False otherwise

        """
        if not self.graph.has_node(node_id):
            logger.error(f"Cannot delete node: node {node_id} does not exist")
            return False

        # Remove from vector store if enabled
        if self.enable_vector_search and self.vector_store:
            try:
                self.vector_store.delete(ids=[node_id])
            except Exception as e:
                logger.error(f"Failed to delete node from vector store: {e}")

        # Remove node from graph (this also removes all connected edges)
        self.graph.remove_node(node_id)

        logger.debug(f"Deleted node: {node_id}")
        return True    
    def query(self, query: KnowledgeQuery) -> list[KnowledgeNode]:
        """Query the SSKG for nodes matching the given criteria.
        
        Args:
            query: The query parameters
            
        Returns:
            List of matching nodes

        """
        results = []

        # Use vector search if enabled and content query is provided
        if self.enable_vector_search and self.vector_store and query.content_query:
            try:
                from sentence_transformers import SentenceTransformer

                # Get or create embeddings model
                if not hasattr(self, 'embeddings_model'):
                    self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

                # Generate query embedding
                query_embedding = self.embeddings_model.encode(query.content_query).tolist()

                # Build metadata filter
                where_clause = {}

                # Filter by node type
                if query.node_types:
                    where_clause["node_type"] = {"$in": [nt.value for nt in query.node_types]}

                # Filter by confidence
                if query.min_confidence > 0:
                    where_clause["confidence"] = {"$gte": query.min_confidence}

                # Filter by time range
                if query.start_time:
                    where_clause["created_at"] = {"$gte": query.start_time.isoformat()}
                if query.end_time:
                    if "created_at" in where_clause:
                        where_clause["created_at"]["$lte"] = query.end_time.isoformat()
                    else:
                        where_clause["created_at"] = {"$lte": query.end_time.isoformat()}

                # Add custom metadata filters
                for key, value in query.metadata_filters.items():
                    where_clause[key] = value

                # Execute vector search
                vector_results = self.vector_store.query(
                    query_embeddings=[query_embedding],
                    n_results=query.limit,
                    where=where_clause if where_clause else None
                )

                # Convert results to KnowledgeNode objects
                for i, node_id in enumerate(vector_results['ids'][0]):
                    node = self.get_node(node_id)
                    if node:
                        results.append(node)

                return results

            except Exception as e:
                logger.error(f"Vector search failed: {e}. Falling back to graph search.")

        # Fall back to graph search
        for node_id, node_data in self.graph.nodes(data=True):
            # Skip if node type doesn't match
            if query.node_types and NodeType(node_data.get('node_type', 'fact')) not in query.node_types:
                continue

            # Skip if confidence is too low
            if float(node_data.get('confidence', 1.0)) < query.min_confidence:
                continue

            # Skip if outside time range
            if query.start_time:
                created_at = datetime.fromisoformat(node_data.get('created_at', datetime.now().isoformat()))
                if created_at < query.start_time:
                    continue

            if query.end_time:
                created_at = datetime.fromisoformat(node_data.get('created_at', datetime.now().isoformat()))
                if created_at > query.end_time:
                    continue

            # Skip if metadata doesn't match
            metadata = json.loads(node_data.get('metadata', '{}'))
            if not all(metadata.get(k) == v for k, v in query.metadata_filters.items()):
                continue

            # Skip if content doesn't match
            if query.content_query and query.content_query.lower() not in node_data.get('content', '').lower():
                continue

            # Add to results
            node = self.get_node(node_id)
            if node:
                results.append(node)

            # Stop if we have enough results
            if len(results) >= query.limit:
                break
        
        return results   
    def get_related_nodes(self, node_id: str, relation_types: Optional[list[RelationType]] = None, 
                      direction: str = "outgoing", limit: int = 10) -> list[tuple[KnowledgeNode, RelationType]]:
        """Get nodes related to the given node.
        
        Args:
            node_id: The ID of the node to get related nodes for
            relation_types: Optional list of relation types to filter by
            direction: Direction of relations to consider ("outgoing", "incoming", or "both")
            limit: Maximum number of related nodes to return
            
        Returns:
            List of tuples containing related nodes and their relation types

        """
        if not self.graph.has_node(node_id):
            logger.error(f"Cannot get related nodes: node {node_id} does not exist")
            return []

        results = []

        # Get outgoing relations
        if direction in ["outgoing", "both"]:
            for _, target_id, key, edge_data in self.graph.out_edges(node_id, data=True, keys=True):
                # Skip if relation type doesn't match
                if relation_types and RelationType(key) not in relation_types:
                    continue

                # Get target node
                target_node = self.get_node(target_id)
                if target_node:
                    results.append((target_node, RelationType(key)))

                # Stop if we have enough results
                if len(results) >= limit:
                    break

        # Get incoming relations
        if direction in ["incoming", "both"] and len(results) < limit:
            for source_id, _, key, edge_data in self.graph.in_edges(node_id, data=True, keys=True):
                # Skip if relation type doesn't match
                if relation_types and RelationType(key) not in relation_types:
                    continue

                # Get source node
                source_node = self.get_node(source_id)
                if source_node:
                    results.append((source_node, RelationType(key)))

                # Stop if we have enough results
                if len(results) >= limit:
                    break

        return results
    
    def resolve_conflicts(self, node_ids: list[str]) -> Optional[KnowledgeNode]:
        """Resolve conflicts between multiple nodes.
        
        Args:
            node_ids: List of conflicting node IDs
            
        Returns:
            Resolved node if successful, None otherwise

        """
        if len(node_ids) < 2:
            logger.error("Cannot resolve conflicts: need at least 2 nodes")
            return None

        # Get nodes
        nodes = [self.get_node(node_id) for node_id in node_ids]
        nodes = [node for node in nodes if node]  # Filter out None values

        if len(nodes) < 2:
            logger.error("Cannot resolve conflicts: not enough valid nodes")
            return None

        # Simple resolution strategy: choose the node with highest confidence
        resolved_node = max(nodes, key=lambda node: node.confidence)

        # Create a new node with combined metadata
        combined_metadata = {}
        for node in nodes:
            combined_metadata.update(node.metadata)

        combined_metadata["conflict_resolution"] = {
            "strategy": "highest_confidence",
            "resolved_from": node_ids,
            "resolution_time": datetime.now().isoformat()
        }

        # Create new node
        new_node = KnowledgeNode(
            id=str(uuid.uuid4()),
            node_type=resolved_node.node_type,
            content=resolved_node.content,
            confidence=resolved_node.confidence,
            metadata=combined_metadata,
            version=1
        )

        # Add to graph
        new_node_id = self.add_node(new_node)

        # Add relations to original nodes
        for node_id in node_ids:
            self.add_relation(KnowledgeRelation(
                source_id=new_node_id,
                target_id=node_id,
                relation_type=RelationType.DERIVED_FROM
            ))

        return new_node
# Domain-specific adapter methods
    
    def store_memory(self, content: str, memory_type: str, owner_id: str, 
                    importance: float = 0.5, metadata: dict[str, Any] = None) -> str:
        """Store a memory in the SSKG.
        
        Args:
            content: The memory content
            memory_type: Type of memory (episodic, semantic, procedural)
            owner_id: ID of the memory owner (role or user)
            importance: Importance score of the memory
            metadata: Additional metadata for the memory
            
        Returns:
            ID of the created memory node

        """
        # Create memory node
        memory_node = KnowledgeNode(
            id=str(uuid.uuid4()),
            node_type=NodeType.MEMORY,
            content=content,
            confidence=importance,
            metadata={
                "memory_type": memory_type,
                "owner_id": owner_id,
                **(metadata or {})
            }
        )

        # Add to graph
        memory_id = self.add_node(memory_node)

        # Add relation to owner
        if self.graph.has_node(owner_id):
            self.add_relation(KnowledgeRelation(
                source_id=memory_id,
                target_id=owner_id,
                relation_type=RelationType.OWNED_BY
            ))

        return memory_id

    def retrieve_memories(self, owner_id: Optional[str] = None, memory_type: Optional[str] = None,
                         content_query: Optional[str] = None, min_importance: float = 0.0,
                         limit: int = 10) -> list[KnowledgeNode]:
        """Retrieve memories from the SSKG.
        
        Args:
            owner_id: Optional ID of the memory owner
            memory_type: Optional type of memories to retrieve
            content_query: Optional content to search for
            min_importance: Minimum importance score
            limit: Maximum number of memories to return
            
        Returns:
            List of matching memory nodes

        """
        # Build query
        metadata_filters = {}
        if memory_type:
            metadata_filters["memory_type"] = memory_type
        if owner_id:
            metadata_filters["owner_id"] = owner_id

        query = KnowledgeQuery(
            node_types=[NodeType.MEMORY],
            content_query=content_query,
            min_confidence=min_importance,
            metadata_filters=metadata_filters,
            limit=limit
        )

        # Execute query
        return self.query(query)
    
    def store_wiki_content(self, page_id: str, content: str, metadata: dict[str, Any] = None) -> str:
        """Store wiki content in the SSKG.
        
        Args:
            page_id: ID of the wiki page
            content: The wiki content
            metadata: Additional metadata for the wiki page
            
        Returns:
            ID of the created wiki node

        """
        # Check if page already exists
        existing_nodes = self.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id},
            limit=1
        ))

        if existing_nodes:
            # Update existing node
            existing_node = existing_nodes[0]
            self.update_node(existing_node.id, {
                "content": content,
                "metadata": {**existing_node.metadata, **(metadata or {})}
            })
            return existing_node.id
        else:
            # Create new node
            wiki_node = KnowledgeNode(
                id=str(uuid.uuid4()),
                node_type=NodeType.WIKI,
                content=content,
                metadata={
                    "page_id": page_id,
                    **(metadata or {})
                }
            )

            # Add to graph
            return self.add_node(wiki_node)

    def retrieve_wiki_content(self, page_id: str) -> Optional[KnowledgeNode]:
        """Retrieve wiki content from the SSKG.
        
        Args:
            page_id: ID of the wiki page
            
        Returns:
            Wiki node if found, None otherwise

        """
        results = self.query(KnowledgeQuery(
            node_types=[NodeType.WIKI],
            metadata_filters={"page_id": page_id},
            limit=1
        ))
        
        return results[0] if results else None    
    def store_session_state(self, session_id: str, state: dict[str, Any]) -> str:
        """Store session state in the SSKG.
        
        Args:
            session_id: ID of the session
            state: Session state to store
            
        Returns:
            ID of the created session node

        """
        # Check if session already exists
        existing_nodes = self.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id},
            limit=1
        ))

        if existing_nodes:
            # Update existing node
            existing_node = existing_nodes[0]
            self.update_node(existing_node.id, {
                "content": json.dumps(state),
                "metadata": {
                    **existing_node.metadata,
                    "last_updated": datetime.now().isoformat()
                }
            })
            return existing_node.id
        else:
            # Create new node
            session_node = KnowledgeNode(
                id=str(uuid.uuid4()),
                node_type=NodeType.SESSION,
                content=json.dumps(state),
                metadata={
                    "session_id": session_id,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            )

            # Add to graph
            return self.add_node(session_node)
    
    def retrieve_session_state(self, session_id: str) -> Optional[dict[str, Any]]:
        """Retrieve session state from the SSKG.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session state if found, None otherwise

        """
        results = self.query(KnowledgeQuery(
            node_types=[NodeType.SESSION],
            metadata_filters={"session_id": session_id},
            limit=1
        ))

        if not results:
            return None

        try:
            return json.loads(results[0].content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse session state for session {session_id}")
            return None
    
    def store_project_state(self, project_id: str, state: dict[str, Any]) -> str:
        """Store project state in the SSKG.
        
        Args:
            project_id: ID of the project
            state: Project state to store
            
        Returns:
            ID of the created project node

        """
        # Check if project already exists
        existing_nodes = self.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"project_id": project_id},
            limit=1
        ))

        if existing_nodes:
            # Update existing node
            existing_node = existing_nodes[0]
            self.update_node(existing_node.id, {
                "content": json.dumps(state),
                "metadata": {
                    **existing_node.metadata,
                    "last_updated": datetime.now().isoformat()
                }
            })
            return existing_node.id
        else:
            # Create new node
            project_node = KnowledgeNode(
                id=str(uuid.uuid4()),
                node_type=NodeType.PROJECT,
                content=json.dumps(state),
                metadata={
                    "project_id": project_id,
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            )

            # Add to graph
            return self.add_node(project_node)
    
    def retrieve_project_state(self, project_id: str) -> Optional[dict[str, Any]]:
        """Retrieve project state from the SSKG.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Project state if found, None otherwise

        """
        results = self.query(KnowledgeQuery(
            node_types=[NodeType.PROJECT],
            metadata_filters={"project_id": project_id},
            limit=1
        ))

        if not results:
            return None

        try:
            return json.loads(results[0].content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse project state for project {project_id}")
            return None
