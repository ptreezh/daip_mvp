"""@Time    : 2025-07-24 10:00:00
@Author  : DAIP-LIVE Team
@File    : critical_review_workflow.py
@Description:
    Implementation of the Critical Review Workflow that orchestrates
    all institutional primitive nodes for systematic fact validation.
"""
import logging
<<<<<<< HEAD
from typing import Any, Dict
=======
from typing import Any
>>>>>>> feature/core-services-refactor

from src.institutional_primitives.base import ExecutionContext
from src.institutional_primitives.consensus_node import ConsensusNode
from src.institutional_primitives.critical_review_nodes import (
    EvidenceAggregationNode,
    FactExtractionNode,
    GenerationNode,
    ParallelReviewNode,
)
from src.institutional_primitives.revision_node import RevisionNode

logger = logging.getLogger(__name__)


class CriticalReviewWorkflow:
    """批判性审查工作流 - Orchestrates the complete Critical Review Workflow.
    
    Implements a systematic approach to combat LLM hallucinations through
    multi-role fact validation, epistemological verification, and
    evidence-based revision processes.
    """
<<<<<<< HEAD

    def __init__(self, workflow_id: str, config: Dict[str, Any] = None):
=======
    
    def __init__(self, workflow_id: str, config: dict[str, Any] = None):
>>>>>>> feature/core-services-refactor
        """Initialize the Critical Review Workflow.
        
        Args:
            workflow_id: Unique identifier for this workflow instance
            config: Configuration parameters for the workflow

        """
        self.workflow_id = workflow_id
        self.config = config or {}

        # Default configuration
        self.default_config = {
            "generation": {
                "role_name": "创作者",
                "capture_metadata": True
            },
            "fact_extraction": {
                "min_confidence": 0.6,
                "max_facts": 20
            },
            "parallel_review": {
                "reviewer_roles": ["批判者", "验证者"],
                "max_parallel_reviews": 5
            },
            "evidence_aggregation": {
                "min_evidence_threshold": 2,
                "weight_by_credibility": True
            },
            "consensus": {
                "consensus_method": "synthesis",
                "credibility_threshold": 0.7,
                "use_synthesis_engine": True
            },
            "revision": {
                "revision_role": "创作者",
                "max_revision_attempts": 3,
                "provide_evidence_details": True
            }
        }

        # Merge default config with provided config
        for section, defaults in self.default_config.items():
            if section not in self.config:
                self.config[section] = {}
            for key, value in defaults.items():
                if key not in self.config[section]:
                    self.config[section][key] = value

        # Initialize workflow nodes
        self.generation_node = GenerationNode(
            f"{workflow_id}_generation",
            self.config["generation"]
        )

        self.fact_extraction_node = FactExtractionNode(
            f"{workflow_id}_fact_extraction",
            self.config["fact_extraction"]
        )

        self.parallel_review_node = ParallelReviewNode(
            f"{workflow_id}_parallel_review",
            self.config["parallel_review"]
        )

        self.evidence_aggregation_node = EvidenceAggregationNode(
            f"{workflow_id}_evidence_aggregation",
            self.config["evidence_aggregation"]
        )

        self.consensus_node = ConsensusNode(
            f"{workflow_id}_consensus",
            self.config["consensus"]
        )

        self.revision_node = RevisionNode(
            f"{workflow_id}_revision",
            self.config["revision"]
        )

    async def execute(
        self,
        prompt: str,
        role_context: str = "",
        services: dict[str, Any] = None,
        execution_id: str = None
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Execute the complete Critical Review Workflow.
        
        Args:
            prompt: The prompt for content generation
            role_context: Additional context for the creator role
            services: Dictionary of services to use in the workflow
            execution_id: Optional execution ID for tracking
            
        Returns:
            Complete workflow results including all intermediate outputs

        """
        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id or f"crit_review_{self.workflow_id}_{id(self)}",
            workflow_id=self.workflow_id,
            node_id="workflow_root",
            services=services or {},
            state={}
        )

        try:
            logger.info(f"Starting Critical Review Workflow: {context.execution_id}")

            # Step 1: Generate content
            generation_inputs = {
                "prompt": prompt,
                "role_context": role_context
            }
            generation_result = await self.generation_node.execute(generation_inputs, context)

            if not generation_result["success"]:
                logger.error(f"Content generation failed: {generation_result.get('error')}")
                return self._create_error_result("Content generation failed", generation_result)

            # Step 2: Extract facts
            fact_extraction_result = await self.fact_extraction_node.execute({}, context)

            if not fact_extraction_result["success"]:
                logger.error(f"Fact extraction failed: {fact_extraction_result.get('error')}")
                return self._create_error_result("Fact extraction failed", fact_extraction_result)

            # Step 3: Parallel review
            parallel_review_result = await self.parallel_review_node.execute({}, context)

            if not parallel_review_result["success"]:
                logger.error(f"Parallel review failed: {parallel_review_result.get('error')}")
                return self._create_error_result("Parallel review failed", parallel_review_result)

            # Step 4: Evidence aggregation
            evidence_aggregation_result = await self.evidence_aggregation_node.execute({}, context)

            if not evidence_aggregation_result["success"]:
                logger.error(f"Evidence aggregation failed: {evidence_aggregation_result.get('error')}")
                return self._create_error_result("Evidence aggregation failed", evidence_aggregation_result)

            # Step 5: Consensus calculation
            consensus_result = await self.consensus_node.execute({}, context)

            if not consensus_result["success"]:
                logger.error(f"Consensus calculation failed: {consensus_result.get('error')}")
                return self._create_error_result("Consensus calculation failed", consensus_result)

            # Step 6: Revision (if needed)
            revision_result = await self.revision_node.execute({}, context)

            if not revision_result["success"]:
                logger.error(f"Content revision failed: {revision_result.get('error')}")
                return self._create_error_result("Content revision failed", revision_result)

            # Prepare final result
            final_content = revision_result["revised_content"]
            revision_needed = revision_result["revision_needed"]

            logger.info(f"Critical Review Workflow completed: {context.execution_id}")

            return {
                "success": True,
                "original_content": generation_result["content"],
                "final_content": final_content,
                "revision_needed": revision_needed,
                "revision_summary": revision_result["revision_summary"] if revision_needed else "No revision needed",
                "facts_extracted": fact_extraction_result["fact_count"],
                "facts_reviewed": parallel_review_result["review_count"],
                "facts_needing_revision": len(consensus_result.get("facts_needing_revision", [])),
                "credibility_scores": consensus_result.get("credibility_scores", {}),
                "execution_id": context.execution_id,
                "execution_details": {
                    "generation": generation_result,
                    "fact_extraction": fact_extraction_result,
                    "parallel_review": parallel_review_result,
                    "evidence_aggregation": evidence_aggregation_result,
                    "consensus": consensus_result,
                    "revision": revision_result
                }
            }

        except Exception as e:
            logger.exception(f"Critical Review Workflow failed with exception: {e}")
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "execution_id": context.execution_id
            }
<<<<<<< HEAD

    def _create_error_result(self, error_message: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def _create_error_result(self, error_message: str, step_result: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Create a standardized error result."""
        return {
            "success": False,
            "error": error_message,
            "error_details": step_result.get("error", "Unknown error"),
            "execution_id": step_result.get("execution_id", "unknown")
        }

    @classmethod
    async def execute_critical_review(
        cls,
        prompt: str,
        role_context: str = "",
        services: dict[str, Any] = None,
        workflow_config: dict[str, Any] = None,
        workflow_id: str = "critical_review"
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Convenience method to execute a Critical Review Workflow.
        
        Args:
            prompt: The prompt for content generation
            role_context: Additional context for the creator role
            services: Dictionary of services to use in the workflow
            workflow_config: Configuration for the workflow
            workflow_id: Identifier for the workflow
            
        Returns:
            Workflow results

        """
        workflow = cls(workflow_id, workflow_config)
        return await workflow.execute(prompt, role_context, services)
