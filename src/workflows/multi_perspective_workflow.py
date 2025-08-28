# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 15:00:00
@Author  : DAIP-LIVE Team
@File    : multi_perspective_workflow.py
@Description:
    Implementation of the Multi-perspective Synthesis Workflow that orchestrates
    all institutional primitive nodes for comprehensive knowledge synthesis.
"""
import logging
from typing import Any, Dict, List

from src.institutional_primitives.multi_perspective import (
    TaskDecompositionNode,
    ParallelExplorationNode,
    ViewpointCollectionNode,
    EnhancedSynthesisNode,
    IterativeRefinementNode
)
from src.institutional_primitives.base import ExecutionContext

logger = logging.getLogger(__name__)


class MultiPerspectiveSynthesisWorkflow:
    """
    多视角综合工作流 - Orchestrates the complete Multi-perspective Synthesis Workflow.
    
    Implements a comprehensive framework to overcome single-LLM perspective limitations
    by orchestrating diverse expert viewpoints with true cognitive independence
    into synthesized knowledge.
    """
    
    def __init__(self, workflow_id: str, config: Dict[str, Any] = None):
        """
        Initialize the Multi-perspective Synthesis Workflow.
        
        Args:
            workflow_id: Unique identifier for this workflow instance
            config: Configuration parameters for the workflow
        """
        self.workflow_id = workflow_id
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "task_decomposition": {
                "planner_role": "规划者",
                "default_perspectives": ["经济", "社会", "技术", "伦理"],
                "max_sub_problems": 5
            },
            "parallel_exploration": {
                "max_parallel_experts": 5,
                "expert_roles": {},
                "default_expert_role": "专家",
                "use_tools": True
            },
            "viewpoint_collection": {
                "min_viewpoints": 2,
                "conflict_threshold": 0.3,
                "consensus_threshold": 0.7,
                "analyze_coverage": True
            },
            "enhanced_synthesis": {
                "synthesis_method": "dialectical",
                "min_confidence_threshold": 0.6,
                "include_expert_attribution": True,
                "quality_threshold": 0.7
            },
            "iterative_refinement": {
                "max_iterations": 3,
                "quality_threshold": 0.7,
                "improvement_threshold": 0.1,
                "refinement_strategies": ["depth", "breadth", "insight"]
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
        self.task_decomposition_node = TaskDecompositionNode(
            f"{workflow_id}_task_decomposition",
            self.config["task_decomposition"]
        )
        
        self.parallel_exploration_node = ParallelExplorationNode(
            f"{workflow_id}_parallel_exploration",
            self.config["parallel_exploration"]
        )
        
        self.viewpoint_collection_node = ViewpointCollectionNode(
            f"{workflow_id}_viewpoint_collection",
            self.config["viewpoint_collection"]
        )
        
        self.enhanced_synthesis_node = EnhancedSynthesisNode(
            f"{workflow_id}_enhanced_synthesis",
            self.config["enhanced_synthesis"]
        )
        
        self.iterative_refinement_node = IterativeRefinementNode(
            f"{workflow_id}_iterative_refinement",
            self.config["iterative_refinement"]
        )
    
    async def execute(
        self,
        topic: str,
        perspectives: List[str] = None,
        services: Dict[str, Any] = None,
        execution_id: str = None
    ) -> Dict[str, Any]:
        """
        Execute the complete Multi-perspective Synthesis Workflow.
        
        Args:
            topic: The complex topic to analyze
            perspectives: Optional list of perspectives to consider
            services: Dictionary of services to use in the workflow
            execution_id: Optional execution ID for tracking
            
        Returns:
            Complete workflow results including all intermediate outputs
        """
        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id or f"multi_persp_{self.workflow_id}_{id(self)}",
            workflow_id=self.workflow_id,
            node_id="workflow_root",
            services=services or {},
            state={}
        )
        
        try:
            logger.info(f"Starting Multi-perspective Synthesis Workflow: {context.execution_id}")
            
            # Step 1: Task decomposition
            decomposition_inputs = {
                "topic": topic,
                "perspectives": perspectives or []
            }
            decomposition_result = await self.task_decomposition_node.execute(decomposition_inputs, context)
            
            if not decomposition_result["success"]:
                logger.error(f"Task decomposition failed: {decomposition_result.get('error')}")
                return self._create_error_result("Task decomposition failed", decomposition_result)
            
            # Step 2: Parallel exploration
            exploration_result = await self.parallel_exploration_node.execute({}, context)
            
            if not exploration_result["success"]:
                logger.error(f"Parallel exploration failed: {exploration_result.get('error')}")
                return self._create_error_result("Parallel exploration failed", exploration_result)
            
            # Step 3: Viewpoint collection and analysis
            collection_result = await self.viewpoint_collection_node.execute({}, context)
            
            if not collection_result["success"]:
                logger.error(f"Viewpoint collection failed: {collection_result.get('error')}")
                return self._create_error_result("Viewpoint collection failed", collection_result)
            
            # Step 4: Enhanced synthesis
            synthesis_result = await self.enhanced_synthesis_node.execute({}, context)
            
            if not synthesis_result["success"]:
                logger.error(f"Enhanced synthesis failed: {synthesis_result.get('error')}")
                return self._create_error_result("Enhanced synthesis failed", synthesis_result)
            
            # Step 5: Iterative refinement (if needed)
            refinement_result = synthesis_result  # Default to original synthesis
            if synthesis_result.get("needs_refinement", False):
                logger.info("Synthesis needs refinement, applying iterative improvement...")
                refinement_result = await self.iterative_refinement_node.execute({}, context)
                
                if not refinement_result["success"]:
                    logger.warning(f"Iterative refinement failed: {refinement_result.get('error')}")
                    # Continue with original synthesis if refinement fails
                    refinement_result = synthesis_result
            
            # Prepare final result
            logger.info(f"Multi-perspective Synthesis Workflow completed: {context.execution_id}")
            
            # Use refined result if available, otherwise use original synthesis
            final_synthesis = refinement_result.get("refined_synthesis", {}) if refinement_result.get("refinement_applied", False) else synthesis_result
            
            return {
                "success": True,
                "topic": topic,
                "perspectives": perspectives or self.config["task_decomposition"]["default_perspectives"],
                "synthesis": final_synthesis.get("synthesis", synthesis_result["synthesis"]),
                "key_insights": final_synthesis.get("key_insights", synthesis_result["key_insights"]),
                "expert_contributions": final_synthesis.get("expert_contributions", synthesis_result["expert_contributions"]),
                "confidence": final_synthesis.get("confidence", synthesis_result["confidence"]),
                "quality_score": final_synthesis.get("quality_assessment", {}).get("overall_score", 0.0) if isinstance(final_synthesis.get("quality_assessment"), dict) else 0.0,
                "refinement_applied": refinement_result.get("refinement_applied", False),
                "refinement_iterations": refinement_result.get("iterations_performed", 0),
                "sub_problems": decomposition_result["sub_problems"],
                "viewpoints": exploration_result["viewpoints"],
                "viewpoint_analysis": collection_result["collection"],
                "execution_id": context.execution_id,
                "execution_details": {
                    "task_decomposition": decomposition_result,
                    "parallel_exploration": exploration_result,
                    "viewpoint_collection": collection_result,
                    "enhanced_synthesis": synthesis_result,
                    "iterative_refinement": refinement_result if refinement_result != synthesis_result else None
                }
            }
            
        except Exception as e:
            logger.exception(f"Multi-perspective Synthesis Workflow failed with exception: {e}")
            return {
                "success": False,
                "error": f"Workflow execution failed: {str(e)}",
                "execution_id": context.execution_id
            }
    
    def _create_error_result(self, error_message: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            "success": False,
            "error": error_message,
            "error_details": step_result.get("error", "Unknown error"),
            "execution_id": step_result.get("execution_id", "unknown")
        }
    
    @classmethod
    async def execute_multi_perspective_synthesis(
        cls,
        topic: str,
        perspectives: List[str] = None,
        services: Dict[str, Any] = None,
        workflow_config: Dict[str, Any] = None,
        workflow_id: str = "multi_perspective"
    ) -> Dict[str, Any]:
        """
        Convenience method to execute a Multi-perspective Synthesis Workflow.
        
        Args:
            topic: The complex topic to analyze
            perspectives: Optional list of perspectives to consider
            services: Dictionary of services to use in the workflow
            workflow_config: Configuration for the workflow
            workflow_id: Identifier for the workflow
            
        Returns:
            Workflow results
        """
        workflow = cls(workflow_id, workflow_config)
        return await workflow.execute(topic, perspectives, services)