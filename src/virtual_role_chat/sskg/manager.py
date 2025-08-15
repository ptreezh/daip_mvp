"""SSKG Manager - Main interface for the Semantic Structured Knowledge Graph.

This module provides the main interface for interacting with the SSKG system,
including knowledge storage, retrieval, conflict resolution, and semantic search.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from .models import (
    ConflictResolution,
    ConflictResolutionStrategy,
    KnowledgeFact,
    KnowledgeQuery,
    Memory,
    MemoryQuery,
    ProjectState,
    SessionState,
    WikiPage,
)
from .storage import SSKGStorage


class SSKGManager:
    """Main manager class for the Semantic Structured Knowledge Graph.
    
    This class provides a unified interface for all SSKG operations including
    knowledge storage, retrieval, conflict resolution, and semantic search.
    """
    
    def __init__(self, storage: Optional[SSKGStorage] = None):
        """Initialize the SSKG manager.
        
        Args:
            storage: Storage backend (defaults to SQLite storage)
        """
        self.storage = storage or SSKGStorage()
        self.logger = logging.getLogger(__name__)
        
        # Conflict resolution strategies
        self.conflict_resolvers = {
            ConflictResolutionStrategy.TEMPORAL: self._resolve_temporal_conflict,
            ConflictResolutionStrategy.CONFIDENCE_BASED: self._resolve_confidence_conflict,
            ConflictResolutionStrategy.SOURCE_BASED: self._resolve_source_conflict,
        }
    
    # Knowledge Fact Operations
    
    def store_fact(self, fact: KnowledgeFact) -> str:
        """Store a knowledge fact with automatic conflict detection.
        
        Args:
            fact: Knowledge fact to store
            
        Returns:
            ID of the stored fact
        """
        # Check for potential conflicts
        conflicts = self._detect_conflicts(fact)
        
        if conflicts:
            self.logger.info(f"Detected {len(conflicts)} potential conflicts for fact")
            # For now, just log conflicts. In a full implementation,
            # this would trigger conflict resolution
            for conflict in conflicts:
                self.logger.debug(f"Conflict with fact {conflict.id}: {conflict.content}")
        
        return self.storage.store_fact(fact)
    
    def retrieve_facts(self, query: KnowledgeQuery) -> list[KnowledgeFact]:
        """Retrieve knowledge facts based on query criteria.
        
        Args:
            query: Query specification
            
        Returns:
            List of matching knowledge facts
        """
        return self.storage.search_facts(query)
    
    def update_fact(self, fact_id: str, updates: dict[str, Any]) -> bool:
        """Update a knowledge fact.
        
        Args:
            fact_id: ID of the fact to update
            updates: Dictionary of field updates
            
        Returns:
            True if update was successful
        """
        fact = self.storage.retrieve_fact(fact_id)
        if not fact:
            return False
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(fact, field):
                setattr(fact, field, value)
        
        fact.last_updated = datetime.now()
        fact.version += 1
        
        self.storage.store_fact(fact)
        return True
    
    def delete_fact(self, fact_id: str) -> bool:
        """Delete a knowledge fact.
        
        Args:
            fact_id: ID of the fact to delete
            
        Returns:
            True if deletion was successful
        """
        # In a full implementation, this would handle cascading deletes
        # and relationship cleanup
        return self.storage.delete_fact(fact_id)
    
    def search_knowledge(
        self, 
        query: str, 
        filters: dict[str, Any] = None, 
        limit: int = 10
    ) -> list[KnowledgeFact]:
        """Perform semantic search for knowledge.
        
        Args:
            query: Search query string
            filters: Additional filters to apply
            limit: Maximum number of results
            
        Returns:
            List of matching knowledge facts
        """
        # Build knowledge query
        knowledge_query = KnowledgeQuery(
            content=query,
            limit=limit
        )
        
        # Apply filters
        if filters:
            if 'domain' in filters:
                knowledge_query.domain = filters['domain']
            if 'min_confidence' in filters:
                knowledge_query.min_confidence = filters['min_confidence']
            if 'source' in filters:
                knowledge_query.source = filters['source']
        
        return self.retrieve_facts(knowledge_query)
    
    def get_related_facts(
        self, 
        fact_id: str, 
        relation_types: list[str] = None
    ) -> list[KnowledgeFact]:
        """Get facts related to a specific fact.
        
        Args:
            fact_id: ID of the source fact
            relation_types: Types of relations to follow
            
        Returns:
            List of related facts
        """
        fact = self.storage.retrieve_fact(fact_id)
        if not fact:
            return []
        
        related_facts = []
        for relation in fact.relations:
            if not relation_types or relation.relation_type.value in relation_types:
                related_fact = self.storage.retrieve_fact(relation.target_fact_id)
                if related_fact:
                    related_facts.append(related_fact)
        
        return related_facts
    
    def resolve_conflicts(self, conflicting_facts: list[str]) -> ConflictResolution:
        """Resolve conflicts between knowledge facts.
        
        Args:
            conflicting_facts: List of fact IDs that are in conflict
            
        Returns:
            Conflict resolution result
        """
        facts = []
        for fact_id in conflicting_facts:
            fact = self.storage.retrieve_fact(fact_id)
            if fact:
                facts.append(fact)
        
        if len(facts) < 2:
            raise ValueError("Need at least 2 facts to resolve conflicts")
        
        # Use confidence-based resolution as default
        return self._resolve_confidence_conflict(facts)
    
    # Memory Operations
    
    def store_memory(self, memory: Memory, memory_type: str) -> str:
        """Store a memory item.
        
        Args:
            memory: Memory to store
            memory_type: Type of memory (for compatibility)
            
        Returns:
            ID of the stored memory
        """
        return self.storage.store_memory(memory)
    
    def retrieve_memories(self, query: MemoryQuery) -> list[Memory]:
        """Retrieve memories based on query criteria.
        
        Args:
            query: Memory query specification
            
        Returns:
            List of matching memories
        """
        return self.storage.search_memories(query)
    
    # Session and Project State Operations
    
    def store_session_state(self, session_id: str, state: dict[str, Any]) -> bool:
        """Store session state.
        
        Args:
            session_id: Session identifier
            state: State data to store
            
        Returns:
            True if storage was successful
        """
        session_state = SessionState(
            session_id=session_id,
            state_data=state
        )
        return self.storage.store_session_state(session_state)
    
    def retrieve_session_state(self, session_id: str) -> dict[str, Any]:
        """Retrieve session state.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session state data
        """
        session_state = self.storage.retrieve_session_state(session_id)
        return session_state.state_data if session_state else {}
    
    def store_project_state(self, project_id: str, state: dict[str, Any]) -> bool:
        """Store project state.
        
        Args:
            project_id: Project identifier
            state: State data to store
            
        Returns:
            True if storage was successful
        """
        project_state = ProjectState(
            project_id=project_id,
            name=state.get('name', project_id),
            config=state
        )
        return self.storage.store_project_state(project_state)
    
    def retrieve_project_state(self, project_id: str) -> dict[str, Any]:
        """Retrieve project state.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Project state data
        """
        project_state = self.storage.retrieve_project_state(project_id)
        return project_state.config if project_state else {}
    
    # Wiki Operations
    
    def store_wiki_content(
        self, 
        page_id: str, 
        content: str, 
        metadata: dict[str, Any]
    ) -> bool:
        """Store wiki page content.
        
        Args:
            page_id: Page identifier
            content: Page content
            metadata: Page metadata
            
        Returns:
            True if storage was successful
        """
        wiki_page = WikiPage(
            id=page_id,
            title=metadata.get('title', page_id),
            content=content,
            created_by=metadata.get('created_by', 'system'),
            metadata=metadata
        )
        return self.storage.store_wiki_page(wiki_page)
    
    def retrieve_wiki_content(self, page_id: str) -> WikiPage:
        """Retrieve wiki page content.
        
        Args:
            page_id: Page identifier
            
        Returns:
            Wiki page object
        """
        return self.storage.retrieve_wiki_page(page_id)
    
    # Private helper methods
    
    def _detect_conflicts(self, fact: KnowledgeFact) -> list[KnowledgeFact]:
        """Detect potential conflicts with existing facts.
        
        Args:
            fact: Fact to check for conflicts
            
        Returns:
            List of potentially conflicting facts
        """
        # Simple conflict detection based on content similarity
        query = KnowledgeQuery(
            content=fact.content,
            domain=fact.domain,
            limit=5
        )
        
        similar_facts = self.storage.search_facts(query)
        
        # Filter out exact matches and low-confidence facts
        conflicts = []
        for similar_fact in similar_facts:
            if (similar_fact.id != fact.id and 
                similar_fact.confidence > 0.5 and
                self._are_conflicting(fact, similar_fact)):
                conflicts.append(similar_fact)
        
        return conflicts
    
    def _are_conflicting(self, fact1: KnowledgeFact, fact2: KnowledgeFact) -> bool:
        """Determine if two facts are conflicting.
        
        Args:
            fact1: First fact
            fact2: Second fact
            
        Returns:
            True if facts are conflicting
        """
        # Simple heuristic: facts are conflicting if they have similar content
        # but different confidence levels or sources
        # In a real implementation, this would use more sophisticated NLP
        
        content_similarity = self._calculate_content_similarity(fact1.content, fact2.content)
        
        return (content_similarity > 0.7 and 
                abs(fact1.confidence - fact2.confidence) > 0.3)
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings.
        
        Args:
            content1: First content string
            content2: Second content string
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple word-based similarity
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _resolve_confidence_conflict(self, facts: list[KnowledgeFact]) -> ConflictResolution:
        """Resolve conflict by choosing the fact with highest confidence.
        
        Args:
            facts: List of conflicting facts
            
        Returns:
            Conflict resolution result
        """
        resolved_fact = max(facts, key=lambda f: f.confidence)
        
        return ConflictResolution(
            resolved_fact=resolved_fact,
            conflicting_facts=[f for f in facts if f.id != resolved_fact.id],
            resolution_strategy=ConflictResolutionStrategy.CONFIDENCE_BASED,
            confidence=resolved_fact.confidence,
            reasoning=f"Selected fact with highest confidence ({resolved_fact.confidence})"
        )
    
    def _resolve_temporal_conflict(self, facts: list[KnowledgeFact]) -> ConflictResolution:
        """Resolve conflict by choosing the most recent fact.
        
        Args:
            facts: List of conflicting facts
            
        Returns:
            Conflict resolution result
        """
        resolved_fact = max(facts, key=lambda f: f.timestamp)
        
        return ConflictResolution(
            resolved_fact=resolved_fact,
            conflicting_facts=[f for f in facts if f.id != resolved_fact.id],
            resolution_strategy=ConflictResolutionStrategy.TEMPORAL,
            confidence=resolved_fact.confidence,
            reasoning=f"Selected most recent fact (timestamp: {resolved_fact.timestamp})"
        )
    
    def _resolve_source_conflict(self, facts: list[KnowledgeFact]) -> ConflictResolution:
        """Resolve conflict by choosing the fact from the most reliable source.
        
        Args:
            facts: List of conflicting facts
            
        Returns:
            Conflict resolution result
        """
        # Simple source reliability ranking
        source_reliability = {
            'system': 0.9,
            'expert': 0.8,
            'user': 0.6,
            'unknown': 0.3
        }
        
        def get_source_score(fact):
            return source_reliability.get(fact.source, 0.5)
        
        resolved_fact = max(facts, key=get_source_score)
        
        return ConflictResolution(
            resolved_fact=resolved_fact,
            conflicting_facts=[f for f in facts if f.id != resolved_fact.id],
            resolution_strategy=ConflictResolutionStrategy.SOURCE_BASED,
            confidence=resolved_fact.confidence,
            reasoning=f"Selected fact from most reliable source ({resolved_fact.source})"
        )