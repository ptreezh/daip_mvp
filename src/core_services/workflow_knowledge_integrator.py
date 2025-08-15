"""@Time    : 2025-07-24 22:30:00
@Author  : DAIP-LIVE Team
@File    : workflow_knowledge_integrator.py
@Description:
    Workflow Knowledge Integrator that automatically integrates knowledge persistence
    into Critical Review and Multi-perspective Synthesis workflows.
"""
import logging
<<<<<<< HEAD
from datetime import datetime
from typing import Any, Callable, Dict, List
=======
from collections.abc import Callable
from datetime import datetime
from typing import Any
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel

from .enhanced_sskg_manager import EnhancedSSKGManager
from .knowledge_conflict_resolver import KnowledgeConflictResolver
from .knowledge_persistence_service import KnowledgePersistenceResult, KnowledgePersistenceService
from .wiki_service import WikiService

logger = logging.getLogger(__name__)


class WorkflowIntegrationConfig(BaseModel):
    """Configuration for workflow knowledge integration."""

    auto_persist_facts: bool = True
    auto_persist_synthesis: bool = True
    min_confidence_threshold: float = 0.5
    create_wiki_pages: bool = True
    auto_resolve_conflicts: bool = True
    notify_on_conflicts: bool = True
    enable_cross_session_sharing: bool = True


class WorkflowKnowledgeIntegrator:
    """Integrates knowledge persistence into workflow execution.
    
    This service implements requirement 6.1 and 6.2 by automatically
    persisting validated facts and synthesis results from workflows.
    """

    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        wiki_service: WikiService,
        config: WorkflowIntegrationConfig = None
    ):
        """Initialize the workflow knowledge integrator.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            wiki_service: Wiki service for structured documentation
            config: Configuration for integration behavior

        """
        self.sskg_manager = sskg_manager
        self.wiki_service = wiki_service
        self.config = config or WorkflowIntegrationConfig()

        # Initialize knowledge persistence service
        conflict_resolver = KnowledgeConflictResolver()
        self.persistence_service = KnowledgePersistenceService(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            conflict_resolver=conflict_resolver
        )

        # Configure persistence service
        self.persistence_service.configure_persistence(
            min_confidence_threshold=self.config.min_confidence_threshold,
            auto_resolve_conflicts=self.config.auto_resolve_conflicts,
            create_wiki_pages=self.config.create_wiki_pages
        )

        # Callback registry for notifications
<<<<<<< HEAD
        self.persistence_callbacks: List[Callable[[str, KnowledgePersistenceResult], None]] = []
        self.conflict_callbacks: List[Callable[[str, List[str]], None]] = []

=======
        self.persistence_callbacks: list[Callable[[str, KnowledgePersistenceResult], None]] = []
        self.conflict_callbacks: list[Callable[[str, list[str]], None]] = []
        
>>>>>>> feature/core-services-refactor
        logger.info("WorkflowKnowledgeIntegrator initialized")

    async def integrate_critical_review_workflow(
        self,
        workflow_result: dict[str, Any],
        execution_id: str,
        workflow_instance: Any = None
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Integrate knowledge persistence into Critical Review workflow results.
        
        Args:
            workflow_result: Result from Critical Review workflow
            execution_id: Unique execution identifier
            workflow_instance: Optional workflow instance for callbacks
            
        Returns:
            Enhanced workflow result with persistence information

        """
        logger.info(f"Integrating Critical Review workflow knowledge for execution {execution_id}")

        enhanced_result = workflow_result.copy()

        try:
            if self.config.auto_persist_facts and workflow_result.get("success", False):
                # Persist validated facts
                persistence_results = await self.persistence_service.persist_critical_review_results(
                    workflow_result, execution_id
                )

                # Add persistence information to result
                enhanced_result["knowledge_persistence"] = {
                    "facts_persisted": len([r for r in persistence_results if r.success]),
                    "persistence_failures": len([r for r in persistence_results if not r.success]),
                    "conflicts_detected": sum(len(r.conflicts_detected) for r in persistence_results),
                    "conflicts_resolved": sum(len(r.conflicts_resolved) for r in persistence_results),
                    "wiki_pages_created": len([r for r in persistence_results if r.wiki_page_id]),
                    "persistence_timestamp": datetime.now().isoformat(),
                    "persistence_results": [r.model_dump() for r in persistence_results]
                }

                # Notify callbacks
                for result in persistence_results:
                    for callback in self.persistence_callbacks:
                        try:
                            callback(execution_id, result)
                        except Exception as e:
                            logger.error(f"Persistence callback failed: {e}")

                # Handle conflicts if any
                all_conflicts = []
                for result in persistence_results:
                    all_conflicts.extend(result.conflicts_detected)

                if all_conflicts and self.config.notify_on_conflicts:
                    for callback in self.conflict_callbacks:
                        try:
                            callback(execution_id, all_conflicts)
                        except Exception as e:
                            logger.error(f"Conflict callback failed: {e}")

                logger.info(f"Successfully integrated {len(persistence_results)} facts from Critical Review")

            # Enable cross-session knowledge sharing if configured
            if self.config.enable_cross_session_sharing:
                enhanced_result["cross_session_knowledge"] = await self._get_related_knowledge(
                    workflow_result, "critical_review"
                )

        except Exception as e:
            logger.error(f"Error integrating Critical Review workflow knowledge: {e}")
            enhanced_result["knowledge_persistence_error"] = str(e)

        return enhanced_result

    async def integrate_multi_perspective_workflow(
        self,
        workflow_result: dict[str, Any],
        execution_id: str,
        workflow_instance: Any = None
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Integrate knowledge persistence into Multi-perspective Synthesis workflow results.
        
        Args:
            workflow_result: Result from Multi-perspective Synthesis workflow
            execution_id: Unique execution identifier
            workflow_instance: Optional workflow instance for callbacks
            
        Returns:
            Enhanced workflow result with persistence information

        """
        logger.info(f"Integrating Multi-perspective Synthesis workflow knowledge for execution {execution_id}")

        enhanced_result = workflow_result.copy()

        try:
            if self.config.auto_persist_synthesis and workflow_result.get("success", False):
                # Persist synthesis result
                persistence_result = await self.persistence_service.persist_synthesis_results(
                    workflow_result, execution_id
                )

                # Add persistence information to result
                enhanced_result["knowledge_persistence"] = {
                    "synthesis_persisted": persistence_result.success,
                    "conflicts_detected": len(persistence_result.conflicts_detected),
                    "conflicts_resolved": len(persistence_result.conflicts_resolved),
                    "wiki_page_created": bool(persistence_result.wiki_page_id),
                    "persistence_timestamp": persistence_result.persistence_timestamp.isoformat(),
                    "persistence_result": persistence_result.model_dump()
                }

                # Notify callbacks
                for callback in self.persistence_callbacks:
                    try:
                        callback(execution_id, persistence_result)
                    except Exception as e:
                        logger.error(f"Persistence callback failed: {e}")

                # Handle conflicts if any
                if persistence_result.conflicts_detected and self.config.notify_on_conflicts:
                    for callback in self.conflict_callbacks:
                        try:
                            callback(execution_id, persistence_result.conflicts_detected)
                        except Exception as e:
                            logger.error(f"Conflict callback failed: {e}")
<<<<<<< HEAD

                logger.info("Successfully integrated synthesis result from Multi-perspective workflow")

=======
                
                logger.info("Successfully integrated synthesis result from Multi-perspective workflow")
            
>>>>>>> feature/core-services-refactor
            # Enable cross-session knowledge sharing if configured
            if self.config.enable_cross_session_sharing:
                enhanced_result["cross_session_knowledge"] = await self._get_related_knowledge(
                    workflow_result, "multi_perspective"
                )

        except Exception as e:
            logger.error(f"Error integrating Multi-perspective workflow knowledge: {e}")
            enhanced_result["knowledge_persistence_error"] = str(e)

        return enhanced_result

    async def _get_related_knowledge(
        self,
        workflow_result: dict[str, Any],
        workflow_type: str
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get related knowledge from previous sessions for cross-session sharing.
        
        Args:
            workflow_result: Current workflow result
            workflow_type: Type of workflow ("critical_review" or "multi_perspective")
            
        Returns:
            Dictionary containing related knowledge information

        """
        related_knowledge = {
            "related_facts": [],
            "related_synthesis": [],
            "knowledge_connections": [],
            "retrieval_timestamp": datetime.now().isoformat()
        }

        try:
            if workflow_type == "critical_review":
                # Look for related facts based on content similarity
                original_content = workflow_result.get("original_content", "")
                if original_content:
                    # Query for similar facts
                    from .enhanced_sskg_manager import KnowledgeQuery, NodeType

                    related_facts_query = KnowledgeQuery(
                        node_types=[NodeType.FACT],
                        content_query=original_content[:200],  # Use first 200 chars for similarity
                        min_confidence=0.6,
                        limit=5
                    )

                    related_facts = self.sskg_manager.query(related_facts_query)
                    related_knowledge["related_facts"] = [
                        {
                            "id": fact.id,
                            "content": fact.content,
                            "confidence": fact.confidence,
                            "created_at": fact.created_at.isoformat(),
                            "metadata": fact.metadata
                        }
                        for fact in related_facts
                    ]

            elif workflow_type == "multi_perspective":
                # Look for related synthesis results based on topic similarity
                topic = workflow_result.get("topic", "")
                if topic:
                    from .enhanced_sskg_manager import KnowledgeQuery, NodeType

                    related_synthesis_query = KnowledgeQuery(
                        node_types=[NodeType.CONCEPT],
                        content_query=topic,
                        min_confidence=0.6,
                        limit=5
                    )

                    related_synthesis = self.sskg_manager.query(related_synthesis_query)
                    related_knowledge["related_synthesis"] = [
                        {
                            "id": synthesis.id,
                            "content": synthesis.content[:300] + "..." if len(synthesis.content) > 300 else synthesis.content,
                            "confidence": synthesis.confidence,
                            "created_at": synthesis.created_at.isoformat(),
                            "topic": synthesis.metadata.get("topic", "Unknown"),
                            "perspectives": synthesis.metadata.get("perspectives", [])
                        }
                        for synthesis in related_synthesis
                    ]

        except Exception as e:
            logger.error(f"Error retrieving related knowledge: {e}")
            related_knowledge["retrieval_error"] = str(e)

        return related_knowledge

    def add_persistence_callback(
        self,
        callback: Callable[[str, KnowledgePersistenceResult], None]
    ) -> None:
        """Add a callback for persistence events.
        
        Args:
            callback: Function to call when knowledge is persisted

        """
        self.persistence_callbacks.append(callback)

    def add_conflict_callback(
        self,
        callback: Callable[[str, list[str]], None]
    ) -> None:
        """Add a callback for conflict events.
        
        Args:
            callback: Function to call when conflicts are detected

        """
        self.conflict_callbacks.append(callback)

    def remove_persistence_callback(
        self,
        callback: Callable[[str, KnowledgePersistenceResult], None]
    ) -> None:
        """Remove a persistence callback."""
        try:
            self.persistence_callbacks.remove(callback)
        except ValueError:
            pass

    def remove_conflict_callback(
        self,
        callback: Callable[[str, list[str]], None]
    ) -> None:
        """Remove a conflict callback."""
        try:
            self.conflict_callbacks.remove(callback)
        except ValueError:
            pass

    def configure_integration(
        self,
        auto_persist_facts: bool = None,
        auto_persist_synthesis: bool = None,
        min_confidence_threshold: float = None,
        create_wiki_pages: bool = None,
        auto_resolve_conflicts: bool = None,
        notify_on_conflicts: bool = None,
        enable_cross_session_sharing: bool = None
    ) -> None:
        """Configure integration behavior.
        
        Args:
            auto_persist_facts: Whether to automatically persist facts
            auto_persist_synthesis: Whether to automatically persist synthesis
            min_confidence_threshold: Minimum confidence for persistence
            create_wiki_pages: Whether to create wiki pages
            auto_resolve_conflicts: Whether to automatically resolve conflicts
            notify_on_conflicts: Whether to notify on conflicts
            enable_cross_session_sharing: Whether to enable cross-session sharing

        """
        if auto_persist_facts is not None:
            self.config.auto_persist_facts = auto_persist_facts
        if auto_persist_synthesis is not None:
            self.config.auto_persist_synthesis = auto_persist_synthesis
        if min_confidence_threshold is not None:
            self.config.min_confidence_threshold = min_confidence_threshold
            self.persistence_service.configure_persistence(
                min_confidence_threshold=min_confidence_threshold
            )
        if create_wiki_pages is not None:
            self.config.create_wiki_pages = create_wiki_pages
            self.persistence_service.configure_persistence(
                create_wiki_pages=create_wiki_pages
            )
        if auto_resolve_conflicts is not None:
            self.config.auto_resolve_conflicts = auto_resolve_conflicts
            self.persistence_service.configure_persistence(
                auto_resolve_conflicts=auto_resolve_conflicts
            )
        if notify_on_conflicts is not None:
            self.config.notify_on_conflicts = notify_on_conflicts
        if enable_cross_session_sharing is not None:
            self.config.enable_cross_session_sharing = enable_cross_session_sharing

        logger.info("Workflow knowledge integration configuration updated")
<<<<<<< HEAD

    def get_integration_statistics(self) -> Dict[str, Any]:
=======
    
    def get_integration_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get statistics about knowledge integration.
        
        Returns:
            Dictionary containing integration statistics

        """
        try:
            # Get persistence statistics
            persistence_stats = self.persistence_service.get_persistence_statistics()

            # Add integration-specific statistics
            integration_stats = {
                **persistence_stats,
                "integration_config": {
                    "auto_persist_facts": self.config.auto_persist_facts,
                    "auto_persist_synthesis": self.config.auto_persist_synthesis,
                    "min_confidence_threshold": self.config.min_confidence_threshold,
                    "create_wiki_pages": self.config.create_wiki_pages,
                    "auto_resolve_conflicts": self.config.auto_resolve_conflicts,
                    "enable_cross_session_sharing": self.config.enable_cross_session_sharing
                },
                "callback_counts": {
                    "persistence_callbacks": len(self.persistence_callbacks),
                    "conflict_callbacks": len(self.conflict_callbacks)
                }
            }

            return integration_stats

        except Exception as e:
            logger.error(f"Error getting integration statistics: {e}")
            return {"error": str(e)}

    async def search_knowledge(
        self,
        query: str,
        knowledge_types: list[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Search for knowledge across all persisted content.
        
        Args:
            query: Search query
            knowledge_types: Types of knowledge to search (facts, synthesis, etc.)
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            
        Returns:
            Search results with knowledge items

        """
        try:
            from .enhanced_sskg_manager import KnowledgeQuery, NodeType

            # Map knowledge types to node types
            type_mapping = {
                "facts": NodeType.FACT,
                "synthesis": NodeType.CONCEPT,
                "wiki": NodeType.WIKI,
                "memories": NodeType.MEMORY
            }

            # Determine node types to search
            node_types = []
            if knowledge_types:
                for kt in knowledge_types:
                    if kt in type_mapping:
                        node_types.append(type_mapping[kt])
            else:
                # Search all knowledge types by default
                node_types = [NodeType.FACT, NodeType.CONCEPT, NodeType.WIKI]

            # Execute search
            search_query = KnowledgeQuery(
                node_types=node_types,
                content_query=query,
                min_confidence=min_confidence,
                limit=limit
            )

            results = self.sskg_manager.query(search_query)

            # Format results
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "type": result.node_type.value,
                    "content": result.content,
                    "confidence": result.confidence,
                    "created_at": result.created_at.isoformat(),
                    "metadata": result.metadata
                }

                # Add type-specific information
                if result.node_type == NodeType.FACT:
                    formatted_result["source"] = result.metadata.get("source", "unknown")
                    formatted_result["evidence_sources"] = result.metadata.get("evidence_sources", [])
                elif result.node_type == NodeType.CONCEPT:
                    formatted_result["topic"] = result.metadata.get("topic", "Unknown")
                    formatted_result["perspectives"] = result.metadata.get("perspectives", [])

                formatted_results.append(formatted_result)

            return {
                "query": query,
                "results": formatted_results,
                "total_results": len(formatted_results),
                "search_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": str(e)
            }
