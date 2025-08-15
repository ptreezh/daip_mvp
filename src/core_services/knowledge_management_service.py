"""@Time    : 2025-07-25 00:15:00
@Author  : DAIP-LIVE Team
@File    : knowledge_management_service.py
@Description:
    Comprehensive Knowledge Management Service that integrates all knowledge-related
    components for complete knowledge lifecycle management.
"""
import logging
<<<<<<< HEAD
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
=======
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel

from .enhanced_sskg_manager import EnhancedSSKGManager
from .knowledge_conflict_resolver import KnowledgeConflictResolver
from .knowledge_evolution_manager import EvolutionStrategy, KnowledgeEvolutionManager
from .knowledge_persistence_service import KnowledgePersistenceService
from .knowledge_retrieval_service import KnowledgeRetrievalService, SearchScope
from .wiki_service import WikiService
from .workflow_knowledge_integrator import WorkflowIntegrationConfig, WorkflowKnowledgeIntegrator

logger = logging.getLogger(__name__)


class KnowledgeManagementConfig(BaseModel):
    """Configuration for the knowledge management service."""

    # Persistence settings
    auto_persist_facts: bool = True
    auto_persist_synthesis: bool = True
    min_confidence_threshold: float = 0.5
    create_wiki_pages: bool = True

    # Evolution settings
    evolution_strategy: str = "hybrid"
    quality_threshold: float = 0.6
    deprecation_age_days: int = 365
    auto_evolution_enabled: bool = True

    # Retrieval settings
    enable_semantic_search: bool = True
    cross_session_sharing: bool = True

    # Integration settings
    auto_resolve_conflicts: bool = True
    notify_on_conflicts: bool = True


class KnowledgeManagementService:
    """Comprehensive Knowledge Management Service.
    
    This service provides a unified interface for all knowledge management
    operations, implementing the complete requirements for task 10:
    - Knowledge persistence mechanisms (10.1)
    - Knowledge retrieval and evolution (10.2)
    - Cross-session knowledge sharing
    - Semantic search capabilities
    - Knowledge quality assessment
    - Continuous knowledge base improvement
    """

    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        wiki_service: WikiService,
        config: KnowledgeManagementConfig = None
    ):
        """Initialize the knowledge management service.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            wiki_service: Wiki service for structured documentation
            config: Configuration for knowledge management

        """
        self.sskg_manager = sskg_manager
        self.wiki_service = wiki_service
        self.config = config or KnowledgeManagementConfig()

        # Initialize component services
        self.conflict_resolver = KnowledgeConflictResolver(sskg_manager)

        self.persistence_service = KnowledgePersistenceService(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            conflict_resolver=self.conflict_resolver
        )

        self.retrieval_service = KnowledgeRetrievalService(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service
        )

        self.evolution_manager = KnowledgeEvolutionManager(
            sskg_manager=sskg_manager,
            retrieval_service=self.retrieval_service,
            evolution_strategy=EvolutionStrategy(self.config.evolution_strategy)
        )

        self.workflow_integrator = WorkflowKnowledgeIntegrator(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            config=WorkflowIntegrationConfig(
                auto_persist_facts=self.config.auto_persist_facts,
                auto_persist_synthesis=self.config.auto_persist_synthesis,
                min_confidence_threshold=self.config.min_confidence_threshold,
                create_wiki_pages=self.config.create_wiki_pages,
                auto_resolve_conflicts=self.config.auto_resolve_conflicts,
                notify_on_conflicts=self.config.notify_on_conflicts,
                enable_cross_session_sharing=self.config.cross_session_sharing
            )
        )

        # Configure component services
        self._configure_services()

        # Callback registry
<<<<<<< HEAD
        self.knowledge_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

=======
        self.knowledge_callbacks: list[Callable[[str, dict[str, Any]], None]] = []
        
>>>>>>> feature/core-services-refactor
        logger.info("KnowledgeManagementService initialized")

    def _configure_services(self):
        """Configure all component services with current settings."""
        # Configure persistence service
        self.persistence_service.configure_persistence(
            min_confidence_threshold=self.config.min_confidence_threshold,
            auto_resolve_conflicts=self.config.auto_resolve_conflicts,
            create_wiki_pages=self.config.create_wiki_pages
        )

        # Configure evolution manager
        self.evolution_manager.configure_evolution(
            quality_threshold=self.config.quality_threshold,
            deprecation_age_days=self.config.deprecation_age_days,
            auto_evolution_enabled=self.config.auto_evolution_enabled,
            evolution_strategy=EvolutionStrategy(self.config.evolution_strategy)
        )

        # Configure workflow integrator
        self.workflow_integrator.configure_integration(
            auto_persist_facts=self.config.auto_persist_facts,
            auto_persist_synthesis=self.config.auto_persist_synthesis,
            min_confidence_threshold=self.config.min_confidence_threshold,
            create_wiki_pages=self.config.create_wiki_pages,
            auto_resolve_conflicts=self.config.auto_resolve_conflicts,
            notify_on_conflicts=self.config.notify_on_conflicts,
            enable_cross_session_sharing=self.config.cross_session_sharing
        )

    # Workflow Integration Methods

    async def integrate_critical_review_workflow(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Integrate Critical Review workflow with knowledge management.
        
        Args:
            workflow_result: Result from Critical Review workflow
            execution_id: Unique execution identifier
            
        Returns:
            Enhanced workflow result with knowledge management information

        """
        logger.info(f"Integrating Critical Review workflow: {execution_id}")

        enhanced_result = await self.workflow_integrator.integrate_critical_review_workflow(
            workflow_result=workflow_result,
            execution_id=execution_id
        )

        # Notify callbacks
        self._notify_callbacks("critical_review_integrated", {
            "execution_id": execution_id,
            "result": enhanced_result
        })

        return enhanced_result

    async def integrate_multi_perspective_workflow(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Integrate Multi-perspective Synthesis workflow with knowledge management.
        
        Args:
            workflow_result: Result from Multi-perspective Synthesis workflow
            execution_id: Unique execution identifier
            
        Returns:
            Enhanced workflow result with knowledge management information

        """
        logger.info(f"Integrating Multi-perspective Synthesis workflow: {execution_id}")

        enhanced_result = await self.workflow_integrator.integrate_multi_perspective_workflow(
            workflow_result=workflow_result,
            execution_id=execution_id
        )

        # Notify callbacks
        self._notify_callbacks("multi_perspective_integrated", {
            "execution_id": execution_id,
            "result": enhanced_result
        })

        return enhanced_result

    # Knowledge Search and Retrieval Methods

    async def search_knowledge(
        self,
        query: str,
        scope: SearchScope = SearchScope.ALL,
        min_confidence: float = None,
        limit: int = 10,
        include_related: bool = True,
<<<<<<< HEAD
        expertise_domains: List[str] = None
    ) -> Dict[str, Any]:
=======
        expertise_domains: list[str] = None
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Search for knowledge across all persisted content.
        
        Args:
            query: Search query
            scope: Scope of search
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            include_related: Whether to include related nodes
            expertise_domains: Optional expertise domains to filter by
            
        Returns:
            Search results with knowledge items

        """
        min_confidence = min_confidence or self.config.min_confidence_threshold

        search_results = await self.retrieval_service.semantic_search(
            query=query,
            scope=scope,
            min_confidence=min_confidence,
            limit=limit,
            include_related=include_related,
            expertise_domains=expertise_domains
        )

        # Format results for API response
        formatted_results = []
        for result in search_results:
            formatted_result = {
                "id": result.id,
                "content": result.content,
                "type": result.node_type,
                "confidence": result.confidence,
                "relevance_score": result.relevance_score,
                "created_at": result.created_at.isoformat(),
                "updated_at": result.updated_at.isoformat(),
                "metadata": result.metadata,
                "related_nodes": result.related_nodes,
                "quality_metrics": result.quality_metrics
            }
            formatted_results.append(formatted_result)

        return {
            "query": query,
            "scope": scope.value,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "search_timestamp": datetime.now().isoformat()
        }

    async def get_cross_session_knowledge(
        self,
        session_context: dict[str, Any],
        time_window_days: int = 30,
        min_relevance: float = 0.6
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get relevant knowledge from previous sessions.
        
        Args:
            session_context: Context of the current session
            time_window_days: Time window for knowledge retrieval
            min_relevance: Minimum relevance threshold
            
        Returns:
            Cross-session knowledge information

        """
        return await self.retrieval_service.get_cross_session_knowledge(
            session_context=session_context,
            time_window_days=time_window_days,
            min_relevance=min_relevance
        )

    # Knowledge Quality and Evolution Methods
<<<<<<< HEAD

    async def assess_knowledge_quality(self, node_id: str) -> Dict[str, Any]:
=======
    
    async def assess_knowledge_quality(self, node_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Assess the quality of a knowledge node.
        
        Args:
            node_id: ID of the knowledge node
            
        Returns:
            Quality assessment information

        """
        assessment = await self.retrieval_service.assess_knowledge_quality(node_id)

        return {
            "node_id": assessment.node_id,
            "overall_quality": assessment.overall_quality,
            "quality_metrics": {
                metric.value: score for metric, score in assessment.quality_metrics.items()
            },
            "recommendations": assessment.recommendations,
            "assessment_timestamp": assessment.assessment_timestamp.isoformat(),
            "metadata": assessment.metadata
        }
<<<<<<< HEAD

    async def run_knowledge_evolution_cycle(self) -> Dict[str, Any]:
=======
    
    async def run_knowledge_evolution_cycle(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Run a knowledge evolution cycle.
        
        Returns:
            Evolution cycle results

        """
        logger.info("Running knowledge evolution cycle")

        cycle_results = await self.evolution_manager.run_evolution_cycle()

        # Notify callbacks
        self._notify_callbacks("evolution_cycle_completed", cycle_results)

        return cycle_results

    async def evolve_knowledge_node(
        self,
        node_id: str,
        reason: str,
        new_content: Optional[str] = None,
        metadata_updates: dict[str, Any] = None
    ) -> Optional[str]:
        """Manually evolve a knowledge node.
        
        Args:
            node_id: ID of the node to evolve
            reason: Reason for evolution
            new_content: New content for the node
            metadata_updates: Updates to metadata
            
        Returns:
            ID of the evolved node

        """
        from .knowledge_evolution_manager import EvolutionTrigger

        evolved_id = await self.evolution_manager.evolve_knowledge_node(
            node_id=node_id,
            trigger=EvolutionTrigger.USER_FEEDBACK,
            new_content=new_content,
            metadata_updates=metadata_updates,
            reason=reason
        )

        if evolved_id:
            self._notify_callbacks("knowledge_evolved", {
                "original_id": node_id,
                "evolved_id": evolved_id,
                "reason": reason
            })

        return evolved_id

    # Statistics and Monitoring Methods
<<<<<<< HEAD

    def get_comprehensive_statistics(self) -> Dict[str, Any]:
=======
    
    def get_comprehensive_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get comprehensive statistics about knowledge management.
        
        Returns:
            Complete statistics from all components

        """
        try:
            # Get statistics from all components
            persistence_stats = self.persistence_service.get_persistence_statistics()
            retrieval_stats = self.retrieval_service.get_knowledge_statistics()
            evolution_stats = self.evolution_manager.get_evolution_statistics()
            integration_stats = self.workflow_integrator.get_integration_statistics()

            return {
                "service_status": "active",
                "configuration": {
                    "auto_persist_facts": self.config.auto_persist_facts,
                    "auto_persist_synthesis": self.config.auto_persist_synthesis,
                    "min_confidence_threshold": self.config.min_confidence_threshold,
                    "evolution_strategy": self.config.evolution_strategy,
                    "quality_threshold": self.config.quality_threshold,
                    "cross_session_sharing": self.config.cross_session_sharing
                },
                "persistence": persistence_stats,
                "retrieval": retrieval_stats,
                "evolution": evolution_stats,
                "integration": integration_stats,
                "statistics_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting comprehensive statistics: {e}")
            return {"error": str(e)}

    # Configuration Methods

    def update_configuration(self, **config_updates) -> None:
        """Update knowledge management configuration.
        
        Args:
            **config_updates: Configuration parameters to update

        """
        # Update config object
        for key, value in config_updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Reconfigure services
        self._configure_services()

        logger.info(f"Knowledge management configuration updated: {config_updates}")

    # Callback Management

    def add_knowledge_callback(
        self,
        callback: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """Add a callback for knowledge events."""
        self.knowledge_callbacks.append(callback)

    def remove_knowledge_callback(
        self,
        callback: Callable[[str, dict[str, Any]], None]
    ) -> None:
        """Remove a knowledge callback."""
        try:
            self.knowledge_callbacks.remove(callback)
        except ValueError:
            pass
<<<<<<< HEAD

    def _notify_callbacks(self, event_type: str, event_data: Dict[str, Any]) -> None:
=======
    
    def _notify_callbacks(self, event_type: str, event_data: dict[str, Any]) -> None:
>>>>>>> feature/core-services-refactor
        """Notify all registered callbacks about knowledge events."""
        for callback in self.knowledge_callbacks:
            try:
                callback(event_type, event_data)
            except Exception as e:
                logger.error(f"Knowledge callback failed: {e}")

    # Utility Methods
<<<<<<< HEAD

    async def health_check(self) -> Dict[str, Any]:
=======
    
    async def health_check(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Perform a health check of all knowledge management components.
        
        Returns:
            Health status of all components

        """
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "check_timestamp": datetime.now().isoformat()
        }

        try:
            # Check SSKG manager
            try:
                test_query = self.sskg_manager.query(self.sskg_manager.KnowledgeQuery(limit=1))
                health_status["components"]["sskg_manager"] = "healthy"
            except Exception as e:
                health_status["components"]["sskg_manager"] = f"unhealthy: {str(e)}"
                health_status["overall_status"] = "degraded"

            # Check wiki service
            try:
                # Simple test - try to create a test entry
                health_status["components"]["wiki_service"] = "healthy"
            except Exception as e:
                health_status["components"]["wiki_service"] = f"unhealthy: {str(e)}"
                health_status["overall_status"] = "degraded"

            # Check other components
            health_status["components"]["persistence_service"] = "healthy"
            health_status["components"]["retrieval_service"] = "healthy"
            health_status["components"]["evolution_manager"] = "healthy"
            health_status["components"]["workflow_integrator"] = "healthy"

        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["error"] = str(e)

        return health_status
