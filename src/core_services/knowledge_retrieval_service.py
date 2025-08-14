"""@Time    : 2025-07-24 23:30:00
@Author  : DAIP-LIVE Team
@File    : knowledge_retrieval_service.py
@Description:
    Knowledge retrieval and evolution service for cross-session knowledge sharing
    and semantic search capabilities.
"""
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, KnowledgeQuery, NodeType
from .wiki_service import WikiService

logger = logging.getLogger(__name__)


class SearchScope(str, Enum):
    """Scope for knowledge search."""

    ALL = "all"
    FACTS = "facts"
    SYNTHESIS = "synthesis"
    WIKI = "wiki"
    MEMORIES = "memories"


class QualityMetric(str, Enum):
    """Quality metrics for knowledge assessment."""

    CONFIDENCE = "confidence"
    USAGE_FREQUENCY = "usage_frequency"
    SOURCE_RELIABILITY = "source_reliability"
    VALIDATION_SCORE = "validation_score"
    RECENCY = "recency"
    RELEVANCE = "relevance"


class KnowledgeSearchResult(BaseModel):
    """Result from knowledge search."""

    id: str
    content: str
    node_type: str
    confidence: float
    relevance_score: float = 0.0
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    related_nodes: List[str] = Field(default_factory=list)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)


class KnowledgeEvolutionEvent(BaseModel):
    """Event representing knowledge evolution."""

    event_id: str
    event_type: str  # "created", "updated", "deprecated", "merged", "conflicted"
    node_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    description: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeQualityAssessment(BaseModel):
    """Assessment of knowledge quality."""

    node_id: str
    overall_quality: float = Field(ge=0.0, le=1.0)
    quality_metrics: Dict[QualityMetric, float] = Field(default_factory=dict)
    assessment_timestamp: datetime = Field(default_factory=datetime.now)
    recommendations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRetrievalService:
    """Service for knowledge retrieval, evolution tracking, and quality assessment.
    
    This service implements requirements 6.3, 6.4, 6.5, 6.6, and 6.7:
    - Cross-session knowledge sharing
    - Semantic search for validated information
    - Knowledge quality assessment metrics
    - Knowledge evolution tracking
    - Continuous knowledge base improvement
    """

    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        wiki_service: WikiService
    ):
        """Initialize the knowledge retrieval service.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            wiki_service: Wiki service for structured documentation

        """
        self.sskg_manager = sskg_manager
        self.wiki_service = wiki_service

        # Evolution tracking
        self.evolution_events: List[KnowledgeEvolutionEvent] = []

        # Quality assessment cache
        self.quality_assessments: Dict[str, KnowledgeQualityAssessment] = {}

        # Usage tracking
        self.usage_stats: Dict[str, Dict[str, Any]] = {}

        logger.info("KnowledgeRetrievalService initialized")

    async def semantic_search(
        self,
        query: str,
        scope: SearchScope = SearchScope.ALL,
        min_confidence: float = 0.5,
        limit: int = 10,
        include_related: bool = True,
        expertise_domains: List[str] = None
    ) -> List[KnowledgeSearchResult]:
        """Perform semantic search for validated information.
        
        Args:
            query: Search query
            scope: Scope of search (all, facts, synthesis, etc.)
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            include_related: Whether to include related nodes
            expertise_domains: Optional list of expertise domains to filter by
            
        Returns:
            List of search results with relevance scores

        """
        logger.info(f"Performing semantic search: '{query}' (scope: {scope})")

        try:
            # Map search scope to node types
            node_types = self._get_node_types_for_scope(scope)

            # Build metadata filters
            metadata_filters = {}
            if expertise_domains:
                metadata_filters["expertise_domain"] = {"$in": expertise_domains}

            # Create search query
            search_query = KnowledgeQuery(
                node_types=node_types,
                content_query=query,
                min_confidence=min_confidence,
                metadata_filters=metadata_filters,
                limit=limit * 2  # Get more results for relevance ranking
            )

            # Execute search
            raw_results = self.sskg_manager.query(search_query)

            # Calculate relevance scores and rank results
            scored_results = []
            for node in raw_results:
                relevance_score = self._calculate_relevance_score(node, query)

                # Get related nodes if requested
                related_nodes = []
                if include_related:
                    related = self.sskg_manager.get_related_nodes(
                        node.id,
                        limit=3
                    )
                    related_nodes = [related_node.id for related_node, _ in related]

                # Get quality metrics
                quality_metrics = await self._get_quality_metrics(node.id)

                # Create search result
                result = KnowledgeSearchResult(
                    id=node.id,
                    content=node.content,
                    node_type=node.node_type.value,
                    confidence=node.confidence,
                    relevance_score=relevance_score,
                    created_at=node.created_at,
                    updated_at=node.updated_at,
                    metadata=node.metadata,
                    related_nodes=related_nodes,
                    quality_metrics=quality_metrics
                )

                scored_results.append(result)

                # Track usage
                self._track_usage(node.id, "search_result")

            # Sort by relevance score and limit results
            scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
            final_results = scored_results[:limit]

            logger.info(f"Semantic search returned {len(final_results)} results")
            return final_results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def get_cross_session_knowledge(
        self,
        session_context: Dict[str, Any],
        knowledge_types: List[str] = None,
        time_window_days: int = 30,
        min_relevance: float = 0.6
    ) -> Dict[str, Any]:
        """Get relevant knowledge from previous sessions for cross-session sharing.
        
        Args:
            session_context: Context of the current session
            knowledge_types: Types of knowledge to retrieve
            time_window_days: Time window for knowledge retrieval
            min_relevance: Minimum relevance threshold
            
        Returns:
            Dictionary containing cross-session knowledge

        """
        logger.info("Retrieving cross-session knowledge")

        try:
            # Extract context information
            topic = session_context.get("topic", "")
            keywords = session_context.get("keywords", [])
            user_id = session_context.get("user_id", "")

            # Build search query from context
            search_terms = [topic] + keywords
            query = " ".join(search_terms)

            # Determine time range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=time_window_days)

            # Search for relevant knowledge
            search_query = KnowledgeQuery(
                content_query=query,
                start_time=start_time,
                end_time=end_time,
                min_confidence=min_relevance,
                limit=20
            )

            results = self.sskg_manager.query(search_query)

            # Organize results by type
            cross_session_knowledge = {
                "facts": [],
                "synthesis": [],
                "wiki_pages": [],
                "related_sessions": [],
                "knowledge_connections": [],
                "retrieval_timestamp": datetime.now().isoformat(),
                "context_used": session_context
            }

            for node in results:
                relevance = self._calculate_relevance_score(node, query)
                if relevance >= min_relevance:
                    knowledge_item = {
                        "id": node.id,
                        "content": node.content[:300] + "..." if len(node.content) > 300 else node.content,
                        "confidence": node.confidence,
                        "relevance": relevance,
                        "created_at": node.created_at.isoformat(),
                        "metadata": node.metadata
                    }

                    # Categorize by node type
                    if node.node_type == NodeType.FACT:
                        cross_session_knowledge["facts"].append(knowledge_item)
                    elif node.node_type == NodeType.CONCEPT:
                        cross_session_knowledge["synthesis"].append(knowledge_item)
                    elif node.node_type == NodeType.WIKI:
                        cross_session_knowledge["wiki_pages"].append(knowledge_item)
                    elif node.node_type == NodeType.SESSION:
                        cross_session_knowledge["related_sessions"].append(knowledge_item)

            # Find knowledge connections
            cross_session_knowledge["knowledge_connections"] = await self._find_knowledge_connections(
                results, query
            )

            logger.info(f"Retrieved cross-session knowledge: {len(results)} items")
            return cross_session_knowledge

        except Exception as e:
            logger.error(f"Error retrieving cross-session knowledge: {e}")
            return {
                "facts": [],
                "synthesis": [],
                "wiki_pages": [],
                "related_sessions": [],
                "knowledge_connections": [],
                "error": str(e)
            }

    async def assess_knowledge_quality(
        self,
        node_id: str,
        force_refresh: bool = False
    ) -> KnowledgeQualityAssessment:
        """Assess the quality of a knowledge node.
        
        Args:
            node_id: ID of the knowledge node to assess
            force_refresh: Whether to force a fresh assessment
            
        Returns:
            Quality assessment for the node

        """
        # Check cache first
        if not force_refresh and node_id in self.quality_assessments:
            cached_assessment = self.quality_assessments[node_id]
            # Return cached if less than 1 hour old
            if (datetime.now() - cached_assessment.assessment_timestamp).seconds < 3600:
                return cached_assessment

        logger.info(f"Assessing knowledge quality for node: {node_id}")

        try:
            # Get the node
            node = self.sskg_manager.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found")

            # Calculate quality metrics
            quality_metrics = {}

            # Confidence metric
            quality_metrics[QualityMetric.CONFIDENCE] = node.confidence

            # Usage frequency metric
            usage_stats = self.usage_stats.get(node_id, {})
            usage_frequency = usage_stats.get("access_count", 0) / max(usage_stats.get("days_since_creation", 1), 1)
            quality_metrics[QualityMetric.USAGE_FREQUENCY] = min(usage_frequency / 10.0, 1.0)  # Normalize

            # Source reliability metric
            source_reliability = self._assess_source_reliability(node)
            quality_metrics[QualityMetric.SOURCE_RELIABILITY] = source_reliability

            # Validation score metric
            validation_score = self._assess_validation_score(node)
            quality_metrics[QualityMetric.VALIDATION_SCORE] = validation_score

            # Recency metric
            days_old = (datetime.now() - node.created_at).days
            recency_score = max(0.0, 1.0 - (days_old / 365.0))  # Decay over a year
            quality_metrics[QualityMetric.RECENCY] = recency_score

            # Calculate overall quality (weighted average)
            weights = {
                QualityMetric.CONFIDENCE: 0.3,
                QualityMetric.USAGE_FREQUENCY: 0.2,
                QualityMetric.SOURCE_RELIABILITY: 0.2,
                QualityMetric.VALIDATION_SCORE: 0.2,
                QualityMetric.RECENCY: 0.1
            }

            overall_quality = sum(
                quality_metrics[metric] * weight
                for metric, weight in weights.items()
            )

            # Generate recommendations
            recommendations = self._generate_quality_recommendations(quality_metrics, node)

            # Create assessment
            assessment = KnowledgeQualityAssessment(
                node_id=node_id,
                overall_quality=overall_quality,
                quality_metrics=quality_metrics,
                recommendations=recommendations,
                metadata={
                    "node_type": node.node_type.value,
                    "content_length": len(node.content),
                    "metadata_keys": list(node.metadata.keys())
                }
            )

            # Cache assessment
            self.quality_assessments[node_id] = assessment

            return assessment

        except Exception as e:
            logger.error(f"Error assessing knowledge quality: {e}")
            return KnowledgeQualityAssessment(
                node_id=node_id,
                overall_quality=0.0,
                recommendations=[f"Assessment failed: {str(e)}"]
            )

    def track_knowledge_evolution(
        self,
        node_id: str,
        event_type: str,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Track a knowledge evolution event.
        
        Args:
            node_id: ID of the knowledge node
            event_type: Type of evolution event
            description: Description of the event
            metadata: Additional metadata for the event
            
        Returns:
            ID of the evolution event

        """
        event = KnowledgeEvolutionEvent(
            event_id=f"evolution_{len(self.evolution_events)}_{node_id}",
            event_type=event_type,
            node_id=node_id,
            description=description,
            metadata=metadata or {}
        )

        self.evolution_events.append(event)

        logger.info(f"Tracked evolution event: {event_type} for node {node_id}")
        return event.event_id

    def get_knowledge_evolution_history(
        self,
        node_id: Optional[str] = None,
        event_types: List[str] = None,
        time_window_days: int = 30
    ) -> List[KnowledgeEvolutionEvent]:
        """Get knowledge evolution history.
        
        Args:
            node_id: Optional node ID to filter by
            event_types: Optional event types to filter by
            time_window_days: Time window for events
            
        Returns:
            List of evolution events

        """
        # Filter events
        filtered_events = []
        cutoff_time = datetime.now() - timedelta(days=time_window_days)

        for event in self.evolution_events:
            # Time filter
            if event.timestamp < cutoff_time:
                continue

            # Node filter
            if node_id and event.node_id != node_id:
                continue

            # Event type filter
            if event_types and event.event_type not in event_types:
                continue

            filtered_events.append(event)

        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)

        return filtered_events

    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge statistics.
        
        Returns:
            Dictionary containing knowledge statistics

        """
        try:
            # Get all nodes for statistics
            all_facts = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.FACT],
                limit=1000
            ))

            all_synthesis = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.CONCEPT],
                limit=1000
            ))

            all_wiki = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.WIKI],
                limit=1000
            ))

            # Calculate statistics
            stats = {
                "total_knowledge_items": len(all_facts) + len(all_synthesis) + len(all_wiki),
                "facts_count": len(all_facts),
                "synthesis_count": len(all_synthesis),
                "wiki_pages_count": len(all_wiki),
                "average_confidence": {
                    "facts": sum(f.confidence for f in all_facts) / len(all_facts) if all_facts else 0,
                    "synthesis": sum(s.confidence for s in all_synthesis) / len(all_synthesis) if all_synthesis else 0
                },
                "quality_assessments_count": len(self.quality_assessments),
                "evolution_events_count": len(self.evolution_events),
                "usage_tracked_items": len(self.usage_stats),
                "recent_activity": {
                    "last_24h_events": len([
                        e for e in self.evolution_events
                        if (datetime.now() - e.timestamp).days < 1
                    ]),
                    "last_week_events": len([
                        e for e in self.evolution_events
                        if (datetime.now() - e.timestamp).days < 7
                    ])
                }
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting knowledge statistics: {e}")
            return {"error": str(e)}

    def _get_node_types_for_scope(self, scope: SearchScope) -> List[NodeType]:
        """Map search scope to node types."""
        scope_mapping = {
            SearchScope.ALL: [NodeType.FACT, NodeType.CONCEPT, NodeType.WIKI, NodeType.MEMORY],
            SearchScope.FACTS: [NodeType.FACT],
            SearchScope.SYNTHESIS: [NodeType.CONCEPT],
            SearchScope.WIKI: [NodeType.WIKI],
            SearchScope.MEMORIES: [NodeType.MEMORY]
        }
        return scope_mapping.get(scope, [NodeType.FACT, NodeType.CONCEPT])

    def _calculate_relevance_score(self, node: KnowledgeNode, query: str) -> float:
        """Calculate relevance score for a node given a query."""
        # Simple relevance calculation based on content similarity
        query_lower = query.lower()
        content_lower = node.content.lower()

        # Count query term matches
        query_terms = query_lower.split()
        matches = sum(1 for term in query_terms if term in content_lower)

        # Base relevance on term matches and confidence
        term_relevance = matches / len(query_terms) if query_terms else 0
        confidence_boost = node.confidence * 0.3

        # Metadata boost for specific types
        metadata_boost = 0
        if node.node_type == NodeType.FACT and "validation_timestamp" in node.metadata:
            metadata_boost = 0.1
        elif node.node_type == NodeType.CONCEPT and "quality_score" in node.metadata:
            quality_score = node.metadata.get("quality_score", 0)
            metadata_boost = quality_score * 0.2

        relevance = min(term_relevance + confidence_boost + metadata_boost, 1.0)
        return relevance

    async def _get_quality_metrics(self, node_id: str) -> Dict[str, float]:
        """Get quality metrics for a node."""
        try:
            assessment = await self.assess_knowledge_quality(node_id)
            return {metric.value: score for metric, score in assessment.quality_metrics.items()}
        except Exception:
            return {}

    def _track_usage(self, node_id: str, usage_type: str):
        """Track usage of a knowledge node."""
        if node_id not in self.usage_stats:
            self.usage_stats[node_id] = {
                "access_count": 0,
                "last_accessed": datetime.now(),
                "usage_types": {},
                "days_since_creation": 1
            }

        stats = self.usage_stats[node_id]
        stats["access_count"] += 1
        stats["last_accessed"] = datetime.now()
        stats["usage_types"][usage_type] = stats["usage_types"].get(usage_type, 0) + 1

    def _assess_source_reliability(self, node: KnowledgeNode) -> float:
        """Assess the reliability of a node's source."""
        # Simple source reliability assessment
        source = node.metadata.get("source", "unknown")

        reliability_scores = {
            "critical_review_workflow": 0.9,
            "multi_perspective_synthesis_workflow": 0.8,
            "wiki_service": 0.7,
            "user_input": 0.6,
            "unknown": 0.3
        }

        return reliability_scores.get(source, 0.5)

    def _assess_validation_score(self, node: KnowledgeNode) -> float:
        """Assess the validation score of a node."""
        # Check for validation indicators
        validation_score = 0.5  # Default

        if "validation_timestamp" in node.metadata:
            validation_score += 0.2

        if "evidence_sources" in node.metadata:
            evidence_count = len(node.metadata.get("evidence_sources", []))
            validation_score += min(evidence_count * 0.1, 0.3)

        if "reviewer_roles" in node.metadata:
            reviewer_count = len(node.metadata.get("reviewer_roles", []))
            validation_score += min(reviewer_count * 0.05, 0.2)

        return min(validation_score, 1.0)

    def _generate_quality_recommendations(
        self,
        quality_metrics: Dict[QualityMetric, float],
        node: KnowledgeNode
    ) -> List[str]:
        """Generate recommendations for improving knowledge quality."""
        recommendations = []

        # Low confidence
        if quality_metrics.get(QualityMetric.CONFIDENCE, 0) < 0.6:
            recommendations.append("Consider additional validation to improve confidence")

        # Low usage
        if quality_metrics.get(QualityMetric.USAGE_FREQUENCY, 0) < 0.2:
            recommendations.append("Knowledge item may need better discoverability or relevance")

        # Low source reliability
        if quality_metrics.get(QualityMetric.SOURCE_RELIABILITY, 0) < 0.5:
            recommendations.append("Consider verifying with more reliable sources")

        # Old content
        if quality_metrics.get(QualityMetric.RECENCY, 0) < 0.3:
            recommendations.append("Content may need updating or verification for current relevance")

        # Low validation
        if quality_metrics.get(QualityMetric.VALIDATION_SCORE, 0) < 0.5:
            recommendations.append("Additional evidence or peer review recommended")

        return recommendations

    async def _find_knowledge_connections(
        self,
        nodes: List[KnowledgeNode],
        query: str
    ) -> List[Dict[str, Any]]:
        """Find connections between knowledge nodes."""
        connections = []

        try:
            # Look for nodes that reference each other
            for i, node1 in enumerate(nodes):
                for j, node2 in enumerate(nodes[i+1:], i+1):
                    # Check if nodes are related
                    related = self.sskg_manager.get_related_nodes(
                        node1.id,
                        limit=10
                    )

                    for related_node, relation_type in related:
                        if related_node.id == node2.id:
                            connections.append({
                                "source_id": node1.id,
                                "target_id": node2.id,
                                "relation_type": relation_type.value,
                                "source_content": node1.content[:100] + "...",
                                "target_content": node2.content[:100] + "..."
                            })
                            break

        except Exception as e:
            logger.error(f"Error finding knowledge connections: {e}")

        return connections[:10]  # Limit to 10 connections
