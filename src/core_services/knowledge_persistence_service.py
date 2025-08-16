"""@Time    : 2025-07-24 22:00:00
@Author  : DAIP-LIVE Team
@File    : knowledge_persistence_service.py
@Description:
    Knowledge persistence service for automatically storing validated facts and synthesis results
    from Critical Review and Multi-perspective Synthesis workflows.
"""
import logging
import uuid
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel, Field

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, KnowledgeRelation, NodeType, RelationType
from .knowledge_conflict_resolver import KnowledgeConflictResolver
from .wiki_service import WikiService

logger = logging.getLogger(__name__)


class ValidatedFact(BaseModel):
    """Model for a validated fact from Critical Review workflow."""

    id: str
    content: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence_sources: list[str] = Field(default_factory=list)
    validation_timestamp: datetime = Field(default_factory=datetime.now)
    original_content: Optional[str] = None
    revision_applied: bool = False
    credibility_threshold: float = 0.7
    reviewer_roles: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SynthesisResult(BaseModel):
    """Model for synthesis result from Multi-perspective Synthesis workflow."""

    id: str
    topic: str
    synthesis_content: str
    perspectives: list[str] = Field(default_factory=list)
    expert_attributions: dict[str, list[str]] = Field(default_factory=dict)
    supporting_evidence: list[str] = Field(default_factory=list)
    synthesis_rationale: str = ""
    quality_score: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    synthesis_timestamp: datetime = Field(default_factory=datetime.now)
    refinement_iterations: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgePersistenceResult(BaseModel):
    """Result of knowledge persistence operation."""

    success: bool
    persisted_node_id: Optional[str] = None
    wiki_page_id: Optional[str] = None
    conflicts_detected: list[str] = Field(default_factory=list)
    conflicts_resolved: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    persistence_timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgePersistenceService:
    """Service for automatically persisting validated knowledge from workflows.
    
    This service implements requirement 6.1 and 6.2:
    - Automatic fact persistence from Critical Review
    - Synthesis result storage from Multi-perspective Synthesis
    - Confidence scoring and evidence source tracking
    """

    def __init__(
        self,
        sskg_manager: EnhancedSSKGManager,
        wiki_service: WikiService,
        conflict_resolver: Optional[KnowledgeConflictResolver] = None
    ):
        """Initialize the knowledge persistence service.
        
        Args:
            sskg_manager: Enhanced SSKG manager for knowledge storage
            wiki_service: Wiki service for structured documentation
            conflict_resolver: Optional conflict resolver for handling conflicts

        """
        self.sskg_manager = sskg_manager
        self.wiki_service = wiki_service
        self.conflict_resolver = conflict_resolver or KnowledgeConflictResolver(sskg_manager)

        # Configuration
        self.min_confidence_threshold = 0.5
        self.auto_resolve_conflicts = True
        self.create_wiki_pages = True

        logger.info("KnowledgePersistenceService initialized")

    async def persist_critical_review_results(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
<<<<<<< HEAD
    ) -> List[KnowledgePersistenceResult]:
=======
    ) -> list[KnowledgePersistenceResult]:
>>>>>>> feature/core-services-refactor
        """Persist validated facts from Critical Review workflow.
        
        Args:
            workflow_result: Result from Critical Review workflow
            execution_id: Unique execution identifier
            
        Returns:
            List of persistence results for each validated fact

        """
        logger.info(f"Persisting Critical Review results for execution {execution_id}")

        results = []

        try:
            # Extract validated facts from workflow result
            validated_facts = self._extract_validated_facts(workflow_result, execution_id)

            # Persist each validated fact
            for fact in validated_facts:
                result = await self._persist_validated_fact(fact, execution_id)
                results.append(result)

            # Create summary wiki page if enabled
            if self.create_wiki_pages and validated_facts:
                await self._create_critical_review_wiki_page(
                    validated_facts, workflow_result, execution_id
                )

            logger.info(f"Successfully persisted {len(validated_facts)} facts from Critical Review")

        except Exception as e:
            logger.error(f"Error persisting Critical Review results: {e}")
            results.append(KnowledgePersistenceResult(
                success=False,
                error_message=str(e),
                metadata={"execution_id": execution_id, "workflow_type": "critical_review"}
            ))

        return results

    async def persist_synthesis_results(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
    ) -> KnowledgePersistenceResult:
        """Persist synthesis results from Multi-perspective Synthesis workflow.
        
        Args:
            workflow_result: Result from Multi-perspective Synthesis workflow
            execution_id: Unique execution identifier
            
        Returns:
            Persistence result for the synthesis

        """
        logger.info(f"Persisting Multi-perspective Synthesis results for execution {execution_id}")

        try:
            # Extract synthesis result from workflow result
            synthesis_result = self._extract_synthesis_result(workflow_result, execution_id)

            # Persist synthesis result
            result = await self._persist_synthesis_result(synthesis_result, execution_id)

            # Create wiki page if enabled
            if self.create_wiki_pages and result.success:
                await self._create_synthesis_wiki_page(
                    synthesis_result, workflow_result, execution_id
                )

            logger.info(f"Successfully persisted synthesis result for topic: {synthesis_result.topic}")
            return result

        except Exception as e:
            logger.error(f"Error persisting synthesis results: {e}")
            return KnowledgePersistenceResult(
                success=False,
                error_message=str(e),
                metadata={"execution_id": execution_id, "workflow_type": "multi_perspective"}
            )

    def _extract_validated_facts(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
    ) -> list[ValidatedFact]:
        """Extract validated facts from Critical Review workflow result."""
        validated_facts = []

        # Get credibility scores
        credibility_scores = workflow_result.get("credibility_scores", {})

        # Get extracted facts
        extracted_facts = workflow_result.get("extracted_facts", [])

        # Get evidence reports
        evidence_reports = workflow_result.get("evidence_reports", [])

        # Get original and revised content
        original_content = workflow_result.get("original_content", "")
        revised_content = workflow_result.get("revised_content") or workflow_result.get("final_content")

        # Process each fact
        for fact_data in extracted_facts:
            if isinstance(fact_data, dict):
                fact_id = fact_data.get("id", str(uuid.uuid4()))
                fact_content = fact_data.get("content", "")
                fact_confidence = fact_data.get("confidence", 0.0)

                # Get credibility score
                credibility_score = credibility_scores.get(fact_id, fact_confidence)

                # Only persist facts above minimum threshold
                if credibility_score >= self.min_confidence_threshold:
                    # Extract evidence sources
                    evidence_sources = []
                    reviewer_roles = []

                    for report in evidence_reports:
                        if isinstance(report, dict) and report.get("fact_id") == fact_id:
                            # Add supporting evidence sources
                            for evidence in report.get("supporting_evidence", []):
                                if isinstance(evidence, dict):
                                    source = evidence.get("source", "")
                                    if source:
                                        evidence_sources.append(source)

                            # Add reviewer role
                            reviewer_id = report.get("reviewer_id", "")
                            if reviewer_id:
                                reviewer_roles.append(reviewer_id)

                    # Create validated fact
                    validated_fact = ValidatedFact(
                        id=fact_id,
                        content=fact_content,
                        confidence_score=credibility_score,
                        evidence_sources=evidence_sources,
                        original_content=original_content,
                        revision_applied=bool(revised_content),
                        reviewer_roles=reviewer_roles,
                        metadata={
                            "execution_id": execution_id,
                            "workflow_type": "critical_review",
                            "fact_type": fact_data.get("fact_type", "general"),
                            "source_location": fact_data.get("source_location", ""),
                            "extraction_method": fact_data.get("metadata", {}).get("extraction_method", "llm")
                        }
                    )

                    validated_facts.append(validated_fact)

        return validated_facts

    def _extract_synthesis_result(
        self,
        workflow_result: dict[str, Any],
        execution_id: str
    ) -> SynthesisResult:
        """Extract synthesis result from Multi-perspective Synthesis workflow result."""
        # Extract basic information
        topic = workflow_result.get("topic", "Unknown Topic")
        synthesis_content = workflow_result.get("synthesis", "")
        perspectives = workflow_result.get("perspectives", [])
        quality_score = workflow_result.get("quality_score", 0.0)
        confidence = workflow_result.get("confidence", 0.0)
        refinement_iterations = workflow_result.get("refinement_iterations", 0)

        # Extract expert attributions
        expert_attributions = workflow_result.get("expert_contributions", {})

        # Extract supporting evidence
        supporting_evidence = []
        key_insights = workflow_result.get("key_insights", [])
        if key_insights:
            supporting_evidence.extend(key_insights)

        # Extract synthesis rationale
        synthesis_rationale = ""
        viewpoint_analysis = workflow_result.get("viewpoint_analysis", {})
        if viewpoint_analysis:
            consensus_areas = viewpoint_analysis.get("consensus_areas", [])
            conflicts = viewpoint_analysis.get("conflicts", [])

            rationale_parts = []
            if consensus_areas:
                rationale_parts.append(f"Consensus areas: {', '.join(consensus_areas)}")
            if conflicts:
                rationale_parts.append(f"Resolved conflicts: {', '.join(conflicts)}")

            synthesis_rationale = "; ".join(rationale_parts)

        # Create synthesis result
        synthesis_result = SynthesisResult(
            id=str(uuid.uuid4()),
            topic=topic,
            synthesis_content=synthesis_content,
            perspectives=perspectives,
            expert_attributions=expert_attributions,
            supporting_evidence=supporting_evidence,
            synthesis_rationale=synthesis_rationale,
            quality_score=quality_score,
            confidence=confidence,
            refinement_iterations=refinement_iterations,
            metadata={
                "execution_id": execution_id,
                "workflow_type": "multi_perspective",
                "sub_problems": workflow_result.get("sub_problems", []),
                "refinement_applied": workflow_result.get("refinement_applied", False)
            }
        )

        return synthesis_result

    async def _persist_validated_fact(
        self,
        fact: ValidatedFact,
        execution_id: str
    ) -> KnowledgePersistenceResult:
        """Persist a single validated fact to the SSKG."""
        try:
            # Create knowledge node
            fact_node = KnowledgeNode(
                id=fact.id,
                node_type=NodeType.FACT,
                content=fact.content,
                confidence=fact.confidence_score,
                metadata={
                    **fact.metadata,
                    "validation_timestamp": fact.validation_timestamp.isoformat(),
                    "evidence_sources": fact.evidence_sources,
                    "reviewer_roles": fact.reviewer_roles,
                    "revision_applied": fact.revision_applied,
                    "original_content": fact.original_content,
                    "source": "critical_review_workflow"
                }
            )

            # Check for conflicts
            conflicts_detected = []
            conflicts_resolved = []

            if self.conflict_resolver:
                # Add node first
                node_id = self.sskg_manager.add_node(fact_node)

                # Detect conflicts
                detected_conflicts = self.conflict_resolver.detect_conflicts(node_id)
                conflicts_detected = [c.description for c in detected_conflicts]

                # Resolve conflicts if enabled
                if self.auto_resolve_conflicts and detected_conflicts:
                    resolution_results = self.conflict_resolver.resolve_conflicts(detected_conflicts)
                    conflicts_resolved = [r.reasoning for r in resolution_results]
            else:
                # Add node without conflict detection
                node_id = self.sskg_manager.add_node(fact_node)

            # Create relations to evidence sources
            for source in fact.evidence_sources:
                # Try to find existing source node
                source_nodes = self.sskg_manager.query({
                    "content_query": source,
                    "node_types": [NodeType.FACT, NodeType.WIKI],
                    "limit": 1
                })

                if source_nodes:
                    # Create relation to existing source
                    self.sskg_manager.add_relation(KnowledgeRelation(
                        source_id=node_id,
                        target_id=source_nodes[0].id,
                        relation_type=RelationType.REFERENCES
                    ))

            return KnowledgePersistenceResult(
                success=True,
                persisted_node_id=node_id,
                conflicts_detected=conflicts_detected,
                conflicts_resolved=conflicts_resolved,
                metadata={
                    "fact_id": fact.id,
                    "confidence_score": fact.confidence_score,
                    "evidence_sources_count": len(fact.evidence_sources)
                }
            )

        except Exception as e:
            logger.error(f"Error persisting validated fact {fact.id}: {e}")
            return KnowledgePersistenceResult(
                success=False,
                error_message=str(e),
                metadata={"fact_id": fact.id}
            )

    async def _persist_synthesis_result(
        self,
        synthesis: SynthesisResult,
        execution_id: str
    ) -> KnowledgePersistenceResult:
        """Persist synthesis result to the SSKG."""
        try:
            # Create knowledge node for synthesis
            synthesis_node = KnowledgeNode(
                id=synthesis.id,
                node_type=NodeType.CONCEPT,  # Use CONCEPT for synthesis results
                content=synthesis.synthesis_content,
                confidence=synthesis.confidence,
                metadata={
                    **synthesis.metadata,
                    "topic": synthesis.topic,
                    "perspectives": synthesis.perspectives,
                    "expert_attributions": synthesis.expert_attributions,
                    "supporting_evidence": synthesis.supporting_evidence,
                    "synthesis_rationale": synthesis.synthesis_rationale,
                    "quality_score": synthesis.quality_score,
                    "refinement_iterations": synthesis.refinement_iterations,
                    "synthesis_timestamp": synthesis.synthesis_timestamp.isoformat(),
                    "source": "multi_perspective_synthesis_workflow"
                }
            )

            # Add node to SSKG
            node_id = self.sskg_manager.add_node(synthesis_node)

            # Create relations to supporting evidence
            for evidence in synthesis.supporting_evidence:
                # Create evidence node if it doesn't exist
                evidence_node = KnowledgeNode(
                    id=str(uuid.uuid4()),
                    node_type=NodeType.FACT,
                    content=evidence,
                    confidence=0.8,  # Default confidence for supporting evidence
                    metadata={
                        "source": "synthesis_supporting_evidence",
                        "parent_synthesis": synthesis.id
                    }
                )

                evidence_node_id = self.sskg_manager.add_node(evidence_node)

                # Create relation
                self.sskg_manager.add_relation(KnowledgeRelation(
                    source_id=node_id,
                    target_id=evidence_node_id,
                    relation_type=RelationType.SUPPORTS
                ))

            # Check for conflicts
            conflicts_detected = []
            conflicts_resolved = []

            if self.conflict_resolver:
                detected_conflicts = self.conflict_resolver.detect_conflicts(node_id)
                conflicts_detected = [c.description for c in detected_conflicts]

                if self.auto_resolve_conflicts and detected_conflicts:
                    resolution_results = self.conflict_resolver.resolve_conflicts(detected_conflicts)
                    conflicts_resolved = [r.reasoning for r in resolution_results]

            return KnowledgePersistenceResult(
                success=True,
                persisted_node_id=node_id,
                conflicts_detected=conflicts_detected,
                conflicts_resolved=conflicts_resolved,
                metadata={
                    "synthesis_id": synthesis.id,
                    "topic": synthesis.topic,
                    "quality_score": synthesis.quality_score,
                    "perspectives_count": len(synthesis.perspectives)
                }
            )

        except Exception as e:
            logger.error(f"Error persisting synthesis result {synthesis.id}: {e}")
            return KnowledgePersistenceResult(
                success=False,
                error_message=str(e),
                metadata={"synthesis_id": synthesis.id}
            )

    async def _create_critical_review_wiki_page(
        self,
        validated_facts: list[ValidatedFact],
        workflow_result: dict[str, Any],
        execution_id: str
    ) -> Optional[str]:
        """Create a wiki page summarizing Critical Review results."""
        try:
            # Generate page name
            page_name = f"critical_review_{execution_id}"

            # Generate content
            content_parts = []
            content_parts.append(f"# Critical Review Results - {execution_id}")
            content_parts.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content_parts.append("**Workflow Type:** Critical Review")
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            # Add original content
            original_content = workflow_result.get("original_content", "")
            if original_content:
                content_parts.append(f"\n## Original Content\n\n{original_content}")

            # Add validated facts
            if validated_facts:
                content_parts.append(f"\n## Validated Facts ({len(validated_facts)} facts)")

                for i, fact in enumerate(validated_facts, 1):
                    content_parts.append(f"\n### Fact {i}")
                    content_parts.append(f"\n**Content:** {fact.content}")
                    content_parts.append(f"**Confidence Score:** {fact.confidence_score:.3f}")

                    if fact.evidence_sources:
                        content_parts.append(f"**Evidence Sources:** {', '.join(fact.evidence_sources)}")

                    if fact.reviewer_roles:
                        content_parts.append(f"**Reviewed by:** {', '.join(fact.reviewer_roles)}")

            # Add revision information
            revised_content = workflow_result.get("revised_content") or workflow_result.get("final_content")
            if revised_content:
                content_parts.append(f"\n## Revised Content\n\n{revised_content}")

            # Add statistics
            content_parts.append("\n## Statistics")
            content_parts.append(f"- **Facts Extracted:** {workflow_result.get('facts_extracted', 0)}")
            content_parts.append(f"- **Facts Reviewed:** {workflow_result.get('facts_reviewed', 0)}")
            content_parts.append(f"- **Facts Validated:** {len(validated_facts)}")
            content_parts.append(f"- **Revision Applied:** {'Yes' if revised_content else 'No'}")

            wiki_content = "\n".join(content_parts)

            # Create wiki page
            wiki_result = self.wiki_service.create_entry(
                entry_name=page_name,
                content=wiki_content,
                author_role="knowledge_persistence_service",
                tags=["critical_review", "fact_validation", "automated"],
                category="workflow_results"
            )

            if wiki_result:
                logger.info(f"Created wiki page for Critical Review: {page_name}")
                return page_name

        except Exception as e:
            logger.error(f"Error creating Critical Review wiki page: {e}")

        return None

    async def _create_synthesis_wiki_page(
        self,
        synthesis: SynthesisResult,
        workflow_result: dict[str, Any],
        execution_id: str
    ) -> Optional[str]:
        """Create a wiki page for Multi-perspective Synthesis results."""
        try:
            # Generate page name
            page_name = f"synthesis_{execution_id}_{synthesis.topic.replace(' ', '_').lower()}"

            # Generate content
            content_parts = []
            content_parts.append(f"# Multi-perspective Synthesis: {synthesis.topic}")
            content_parts.append(f"\n**Generated:** {synthesis.synthesis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            content_parts.append(f"**Execution ID:** {execution_id}")
            content_parts.append(f"**Quality Score:** {synthesis.quality_score:.3f}")
            content_parts.append(f"**Confidence:** {synthesis.confidence:.3f}")

            # Add perspectives
            if synthesis.perspectives:
                content_parts.append("\n## Perspectives Analyzed")
                for perspective in synthesis.perspectives:
                    content_parts.append(f"- {perspective}")

            # Add synthesis content
            content_parts.append(f"\n## Synthesis\n\n{synthesis.synthesis_content}")

            # Add key insights
            if synthesis.supporting_evidence:
                content_parts.append("\n## Key Insights")
                for i, insight in enumerate(synthesis.supporting_evidence, 1):
                    content_parts.append(f"{i}. {insight}")

            # Add expert contributions
            if synthesis.expert_attributions:
                content_parts.append("\n## Expert Contributions")
                for expert, contributions in synthesis.expert_attributions.items():
                    content_parts.append(f"\n### {expert}")
                    for contribution in contributions:
                        content_parts.append(f"- {contribution}")

            # Add synthesis rationale
            if synthesis.synthesis_rationale:
                content_parts.append(f"\n## Synthesis Rationale\n\n{synthesis.synthesis_rationale}")

            # Add metadata
            content_parts.append("\n## Metadata")
            content_parts.append(f"- **Refinement Iterations:** {synthesis.refinement_iterations}")
            content_parts.append(f"- **Perspectives Count:** {len(synthesis.perspectives)}")
            content_parts.append(f"- **Expert Contributions:** {len(synthesis.expert_attributions)}")

            wiki_content = "\n".join(content_parts)

            # Create wiki page
            wiki_result = self.wiki_service.create_entry(
                entry_name=page_name,
                content=wiki_content,
                author_role="knowledge_persistence_service",
                tags=["multi_perspective", "synthesis", "automated", synthesis.topic.lower()],
                category="synthesis_results"
            )

            if wiki_result:
                logger.info(f"Created wiki page for synthesis: {page_name}")
                return page_name

        except Exception as e:
            logger.error(f"Error creating synthesis wiki page: {e}")

        return None

    def configure_persistence(
        self,
        min_confidence_threshold: float = 0.5,
        auto_resolve_conflicts: bool = True,
        create_wiki_pages: bool = True
    ) -> None:
        """Configure persistence behavior.
        
        Args:
            min_confidence_threshold: Minimum confidence score for fact persistence
            auto_resolve_conflicts: Whether to automatically resolve conflicts
            create_wiki_pages: Whether to create wiki pages for results

        """
        self.min_confidence_threshold = min_confidence_threshold
        self.auto_resolve_conflicts = auto_resolve_conflicts
        self.create_wiki_pages = create_wiki_pages

        logger.info(f"Knowledge persistence configured: threshold={min_confidence_threshold}, "
                   f"auto_resolve={auto_resolve_conflicts}, wiki_pages={create_wiki_pages}")
<<<<<<< HEAD

    def get_persistence_statistics(self) -> Dict[str, Any]:
=======
    
    def get_persistence_statistics(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Get statistics about persisted knowledge."""
        try:
            # Query for facts from critical review
            critical_review_facts = self.sskg_manager.query({
                "node_types": [NodeType.FACT],
                "metadata_filters": {"source": "critical_review_workflow"},
                "limit": 1000
            })

            # Query for synthesis results
            synthesis_results = self.sskg_manager.query({
                "node_types": [NodeType.CONCEPT],
                "metadata_filters": {"source": "multi_perspective_synthesis_workflow"},
                "limit": 1000
            })

            # Calculate statistics
            stats = {
                "total_validated_facts": len(critical_review_facts),
                "total_synthesis_results": len(synthesis_results),
                "average_fact_confidence": 0.0,
                "average_synthesis_quality": 0.0,
                "facts_by_confidence": {"high": 0, "medium": 0, "low": 0},
                "synthesis_by_quality": {"high": 0, "medium": 0, "low": 0}
            }

            # Calculate fact statistics
            if critical_review_facts:
                confidences = [fact.confidence for fact in critical_review_facts]
                stats["average_fact_confidence"] = sum(confidences) / len(confidences)

                for confidence in confidences:
                    if confidence >= 0.8:
                        stats["facts_by_confidence"]["high"] += 1
                    elif confidence >= 0.6:
                        stats["facts_by_confidence"]["medium"] += 1
                    else:
                        stats["facts_by_confidence"]["low"] += 1

            # Calculate synthesis statistics
            if synthesis_results:
                qualities = []
                for synthesis in synthesis_results:
                    quality = synthesis.metadata.get("quality_score", 0.0)
                    qualities.append(quality)

                if qualities:
                    stats["average_synthesis_quality"] = sum(qualities) / len(qualities)

                    for quality in qualities:
                        if quality >= 0.8:
                            stats["synthesis_by_quality"]["high"] += 1
                        elif quality >= 0.6:
                            stats["synthesis_by_quality"]["medium"] += 1
                        else:
                            stats["synthesis_by_quality"]["low"] += 1

            return stats

        except Exception as e:
            logger.error(f"Error getting persistence statistics: {e}")
            return {"error": str(e)}
