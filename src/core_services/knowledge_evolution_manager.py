"""@Time    : 2025-07-25 00:00:00
@Author  : DAIP-LIVE Team
@File    : knowledge_evolution_manager.py
@Description:
    Knowledge Evolution Manager for tracking and managing knowledge lifecycle,
    versioning, deprecation, and continuous improvement.
"""
import logging
from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, KnowledgeQuery, NodeType, RelationType
from .knowledge_retrieval_service import KnowledgeRetrievalService

logger = logging.getLogger(__name__)


class EvolutionStrategy(str, Enum):
    """Strategies for knowledge evolution."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"


class KnowledgeLifecycleStage(str, Enum):
    """Stages in knowledge lifecycle."""

    DRAFT = "draft"
    VALIDATED = "validated"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class EvolutionTrigger(str, Enum):
    """Triggers for knowledge evolution."""

    QUALITY_DECLINE = "quality_decline"
    CONFLICT_DETECTED = "conflict_detected"
    NEW_EVIDENCE = "new_evidence"
    TIME_BASED = "time_based"
    USER_FEEDBACK = "user_feedback"
    USAGE_PATTERN = "usage_pattern"


class KnowledgeEvolutionManager:
    """Manager for knowledge evolution, versioning, and lifecycle management.
    
    This service implements requirements 6.5, 6.6, and 6.7:
    - Knowledge versioning, deprecation, and evolution with audit trails
    - Continuous knowledge base improvement
    - Quality assessment and lifecycle management
    """

    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        retrieval_service: KnowledgeRetrievalService,
        evolution_strategy: EvolutionStrategy = EvolutionStrategy.HYBRID
    ):
        """Initialize the knowledge evolution manager.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            retrieval_service: Knowledge retrieval service
            evolution_strategy: Strategy for knowledge evolution

        """
        self.sskg_manager = sskg_manager
        self.retrieval_service = retrieval_service
        self.evolution_strategy = evolution_strategy

        # Configuration
        self.quality_threshold = 0.6
        self.deprecation_age_days = 365
        self.auto_evolution_enabled = True

        logger.info(f"KnowledgeEvolutionManager initialized with {evolution_strategy} strategy")

    async def evolve_knowledge_node(
        self,
        node_id: str,
        trigger: EvolutionTrigger,
        new_content: Optional[str] = None,
        metadata_updates: dict[str, Any] = None,
        reason: str = ""
    ) -> Optional[str]:
        """Evolve a knowledge node by creating a new version.
        
        Args:
            node_id: ID of the node to evolve
            trigger: What triggered the evolution
            new_content: New content for the node (if applicable)
            metadata_updates: Updates to metadata
            reason: Reason for evolution
            
        Returns:
            ID of the new evolved node, or None if evolution failed

        """
        logger.info(f"Evolving knowledge node {node_id} (trigger: {trigger})")

        try:
            # Get the original node
            original_node = self.sskg_manager.get_node(node_id)
            if not original_node:
                logger.error(f"Node {node_id} not found")
                return None

            # Create evolved node
            evolved_metadata = original_node.metadata.copy()
            evolved_metadata.update(metadata_updates or {})
            evolved_metadata.update({
                "evolution_trigger": trigger.value,
                "evolution_reason": reason,
                "evolved_from": node_id,
                "evolution_timestamp": datetime.now().isoformat(),
                "version": evolved_metadata.get("version", 1) + 1
            })

            evolved_node = KnowledgeNode(
                id=f"{node_id}_v{evolved_metadata['version']}",
                node_type=original_node.node_type,
                content=new_content or original_node.content,
                confidence=original_node.confidence,
                metadata=evolved_metadata
            )

            # Add evolved node to SSKG
            evolved_id = self.sskg_manager.add_node(evolved_node)

            # Create evolution relation
            from .enhanced_sskg_manager import KnowledgeRelation
            self.sskg_manager.add_relation(KnowledgeRelation(
                source_id=evolved_id,
                target_id=node_id,
                relation_type=RelationType.DERIVED_FROM,
                metadata={
                    "evolution_trigger": trigger.value,
                    "evolution_timestamp": datetime.now().isoformat()
                }
            ))

            # Update original node lifecycle stage
            self.sskg_manager.update_node(node_id, {
                "metadata": {
                    **original_node.metadata,
                    "lifecycle_stage": KnowledgeLifecycleStage.DEPRECATED.value,
                    "deprecated_by": evolved_id,
                    "deprecation_timestamp": datetime.now().isoformat()
                }
            })

            # Track evolution event
            self.retrieval_service.track_knowledge_evolution(
                node_id=evolved_id,
                event_type="evolved",
                description=f"Node evolved from {node_id} due to {trigger.value}: {reason}",
                metadata={
                    "original_node": node_id,
                    "trigger": trigger.value,
                    "evolution_strategy": self.evolution_strategy.value
                }
            )

            logger.info(f"Successfully evolved node {node_id} to {evolved_id}")
            return evolved_id

        except Exception as e:
            logger.error(f"Error evolving knowledge node {node_id}: {e}")
            return None

    async def deprecate_knowledge_node(
        self,
        node_id: str,
        reason: str,
        replacement_id: Optional[str] = None
    ) -> bool:
        """Deprecate a knowledge node.
        
        Args:
            node_id: ID of the node to deprecate
            reason: Reason for deprecation
            replacement_id: Optional ID of replacement node
            
        Returns:
            True if deprecation was successful

        """
        logger.info(f"Deprecating knowledge node {node_id}")

        try:
            # Get the node
            node = self.sskg_manager.get_node(node_id)
            if not node:
                logger.error(f"Node {node_id} not found")
                return False

            # Update node metadata
            deprecation_metadata = {
                **node.metadata,
                "lifecycle_stage": KnowledgeLifecycleStage.DEPRECATED.value,
                "deprecation_reason": reason,
                "deprecation_timestamp": datetime.now().isoformat()
            }

            if replacement_id:
                deprecation_metadata["replaced_by"] = replacement_id

            # Update node
            success = self.sskg_manager.update_node(node_id, {
                "metadata": deprecation_metadata
            })

            if success:
                # Track deprecation event
                self.retrieval_service.track_knowledge_evolution(
                    node_id=node_id,
                    event_type="deprecated",
                    description=f"Node deprecated: {reason}",
                    metadata={
                        "replacement_id": replacement_id,
                        "deprecation_reason": reason
                    }
                )

                # Create relation to replacement if provided
                if replacement_id:
                    from .enhanced_sskg_manager import KnowledgeRelation
                    self.sskg_manager.add_relation(KnowledgeRelation(
                        source_id=replacement_id,
                        target_id=node_id,
                        relation_type=RelationType.DERIVED_FROM,
                        metadata={"replacement_type": "deprecation_replacement"}
                    ))

                logger.info(f"Successfully deprecated node {node_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deprecating knowledge node {node_id}: {e}")
            return False

    async def archive_knowledge_node(
        self,
        node_id: str,
        reason: str = "Automatic archival due to age"
    ) -> bool:
        """Archive a knowledge node.
        
        Args:
            node_id: ID of the node to archive
            reason: Reason for archival
            
        Returns:
            True if archival was successful

        """
        logger.info(f"Archiving knowledge node {node_id}")

        try:
            # Get the node
            node = self.sskg_manager.get_node(node_id)
            if not node:
                logger.error(f"Node {node_id} not found")
                return False

            # Update node metadata
            archival_metadata = {
                **node.metadata,
                "lifecycle_stage": KnowledgeLifecycleStage.ARCHIVED.value,
                "archival_reason": reason,
                "archival_timestamp": datetime.now().isoformat()
            }

            # Update node
            success = self.sskg_manager.update_node(node_id, {
                "metadata": archival_metadata
            })

            if success:
                # Track archival event
                self.retrieval_service.track_knowledge_evolution(
                    node_id=node_id,
                    event_type="archived",
                    description=f"Node archived: {reason}",
                    metadata={"archival_reason": reason}
                )

                logger.info(f"Successfully archived node {node_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error archiving knowledge node {node_id}: {e}")
            return False
<<<<<<< HEAD

    async def run_evolution_cycle(self) -> Dict[str, Any]:
=======
    
    async def run_evolution_cycle(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Run an evolution cycle to identify and process nodes that need evolution.
        
        Returns:
            Summary of evolution cycle results

        """
        logger.info("Running knowledge evolution cycle")

        cycle_results = {
            "cycle_timestamp": datetime.now().isoformat(),
            "nodes_evaluated": 0,
            "nodes_evolved": 0,
            "nodes_deprecated": 0,
            "nodes_archived": 0,
            "evolution_triggers": {},
            "errors": []
        }

        try:
            # Get all active knowledge nodes
            active_nodes = self.sskg_manager.query(KnowledgeQuery(
                node_types=[NodeType.FACT, NodeType.CONCEPT],
                limit=1000
            ))

            cycle_results["nodes_evaluated"] = len(active_nodes)

            for node in active_nodes:
                try:
                    # Skip already deprecated or archived nodes
                    lifecycle_stage = node.metadata.get("lifecycle_stage", KnowledgeLifecycleStage.ACTIVE.value)
                    if lifecycle_stage in [KnowledgeLifecycleStage.DEPRECATED.value, KnowledgeLifecycleStage.ARCHIVED.value]:
                        continue

                    # Check for evolution triggers
                    triggers = await self._check_evolution_triggers(node)

                    for trigger in triggers:
                        trigger_name = trigger["trigger"].value
                        cycle_results["evolution_triggers"][trigger_name] = cycle_results["evolution_triggers"].get(trigger_name, 0) + 1

                        # Process trigger based on strategy
                        if self.evolution_strategy == EvolutionStrategy.AUTOMATIC or (
                            self.evolution_strategy == EvolutionStrategy.HYBRID and trigger["auto_processable"]
                        ):
                            success = await self._process_evolution_trigger(node, trigger)
                            if success:
                                if trigger["action"] == "evolve":
                                    cycle_results["nodes_evolved"] += 1
                                elif trigger["action"] == "deprecate":
                                    cycle_results["nodes_deprecated"] += 1
                                elif trigger["action"] == "archive":
                                    cycle_results["nodes_archived"] += 1

                except Exception as e:
                    error_msg = f"Error processing node {node.id}: {str(e)}"
                    logger.error(error_msg)
                    cycle_results["errors"].append(error_msg)

            logger.info(f"Evolution cycle completed: {cycle_results['nodes_evolved']} evolved, "
                       f"{cycle_results['nodes_deprecated']} deprecated, {cycle_results['nodes_archived']} archived")

        except Exception as e:
            error_msg = f"Error in evolution cycle: {str(e)}"
            logger.error(error_msg)
            cycle_results["errors"].append(error_msg)

        return cycle_results
<<<<<<< HEAD

    async def _check_evolution_triggers(self, node: KnowledgeNode) -> List[Dict[str, Any]]:
=======
    
    async def _check_evolution_triggers(self, node: KnowledgeNode) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Check if a node has any evolution triggers."""
        triggers = []

        try:
            # Quality-based trigger
            quality_assessment = await self.retrieval_service.assess_knowledge_quality(node.id)
            if quality_assessment.overall_quality < self.quality_threshold:
                triggers.append({
                    "trigger": EvolutionTrigger.QUALITY_DECLINE,
                    "action": "evolve",
                    "auto_processable": True,
                    "details": f"Quality score {quality_assessment.overall_quality:.2f} below threshold {self.quality_threshold}",
                    "recommendations": quality_assessment.recommendations
                })

            # Age-based trigger
            age_days = (datetime.now() - node.created_at).days
            if age_days > self.deprecation_age_days:
                triggers.append({
                    "trigger": EvolutionTrigger.TIME_BASED,
                    "action": "archive",
                    "auto_processable": True,
                    "details": f"Node is {age_days} days old, exceeding threshold of {self.deprecation_age_days} days"
                })

            # Conflict-based trigger
            related_nodes = self.sskg_manager.get_related_nodes(
                node.id,
                relation_types=[RelationType.CONTRADICTS],
                limit=5
            )

            if related_nodes:
                triggers.append({
                    "trigger": EvolutionTrigger.CONFLICT_DETECTED,
                    "action": "evolve",
                    "auto_processable": False,  # Requires manual review
                    "details": f"Found {len(related_nodes)} conflicting nodes",
                    "conflicting_nodes": [rn.id for rn, _ in related_nodes]
                })

        except Exception as e:
            logger.error(f"Error checking evolution triggers for node {node.id}: {e}")

        return triggers
<<<<<<< HEAD

    async def _process_evolution_trigger(self, node: KnowledgeNode, trigger: Dict[str, Any]) -> bool:
=======
    
    async def _process_evolution_trigger(self, node: KnowledgeNode, trigger: dict[str, Any]) -> bool:
>>>>>>> feature/core-services-refactor
        """Process an evolution trigger."""
        try:
            trigger_type = trigger["trigger"]
            action = trigger["action"]

            if action == "evolve":
                # Create evolved version with improvements
                evolved_id = await self.evolve_knowledge_node(
                    node_id=node.id,
                    trigger=trigger_type,
                    reason=trigger["details"]
                )
                return evolved_id is not None

            elif action == "deprecate":
                return await self.deprecate_knowledge_node(
                    node_id=node.id,
                    reason=trigger["details"]
                )

            elif action == "archive":
                return await self.archive_knowledge_node(
                    node_id=node.id,
                    reason=trigger["details"]
                )

        except Exception as e:
            logger.error(f"Error processing evolution trigger: {e}")
            return False

        return False
<<<<<<< HEAD

    def get_evolution_statistics(self) -> Dict[str, Any]:
=======
    
    def get_evolution_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get statistics about knowledge evolution."""
        try:
            # Get evolution events
            evolution_events = self.retrieval_service.get_knowledge_evolution_history(
                time_window_days=30
            )

            # Count events by type
            event_counts = {}
            for event in evolution_events:
                event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1

            # Get lifecycle stage distribution
            all_nodes = self.sskg_manager.query(KnowledgeQuery(limit=1000))
            lifecycle_distribution = {}

            for node in all_nodes:
                stage = node.metadata.get("lifecycle_stage", KnowledgeLifecycleStage.ACTIVE.value)
                lifecycle_distribution[stage] = lifecycle_distribution.get(stage, 0) + 1

            return {
                "evolution_strategy": self.evolution_strategy.value,
                "quality_threshold": self.quality_threshold,
                "deprecation_age_days": self.deprecation_age_days,
                "auto_evolution_enabled": self.auto_evolution_enabled,
                "recent_events": {
                    "total_events": len(evolution_events),
                    "event_counts": event_counts
                },
                "lifecycle_distribution": lifecycle_distribution,
                "statistics_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting evolution statistics: {e}")
            return {"error": str(e)}

    def configure_evolution(
        self,
        quality_threshold: float = None,
        deprecation_age_days: int = None,
        auto_evolution_enabled: bool = None,
        evolution_strategy: EvolutionStrategy = None
    ) -> None:
        """Configure evolution parameters.
        
        Args:
            quality_threshold: Minimum quality threshold for nodes
            deprecation_age_days: Age in days after which nodes are deprecated
            auto_evolution_enabled: Whether automatic evolution is enabled
            evolution_strategy: Strategy for knowledge evolution

        """
        if quality_threshold is not None:
            self.quality_threshold = quality_threshold
        if deprecation_age_days is not None:
            self.deprecation_age_days = deprecation_age_days
        if auto_evolution_enabled is not None:
            self.auto_evolution_enabled = auto_evolution_enabled
        if evolution_strategy is not None:
            self.evolution_strategy = evolution_strategy

        logger.info(f"Evolution configuration updated: threshold={self.quality_threshold}, "
                   f"age_days={self.deprecation_age_days}, auto={self.auto_evolution_enabled}, "
                   f"strategy={self.evolution_strategy}")
