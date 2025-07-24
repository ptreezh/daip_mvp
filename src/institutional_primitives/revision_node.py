# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-23 13:00:00
@Author  : DAIP-LIVE Team
@File    : revision_node.py
@Description:
    Implementation of RevisionNode for the Critical Review Workflow.
    Sends low-credibility content back for evidence-based revision.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from .base import InstitutionalPrimitive, ExecutionContext

logger = logging.getLogger(__name__)


class RevisionNode(InstitutionalPrimitive):
    """
    修订节点 - Sends low-credibility content back for evidence-based revision.
    
    Sends content with low credibility scores back to the original creator role
    with evidence-based revision requirements for correction.
    """
    
    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.revision_role = config.get("revision_role", "创作者") if config else "创作者"
        self.max_revision_attempts = config.get("max_revision_attempts", 3) if config else 3
        self.provide_evidence_details = config.get("provide_evidence_details", True) if config else True
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute content revision based on consensus results.
        
        Args:
            inputs: Should contain 'facts_needing_revision' and other consensus data
            context: Execution context
            
        Returns:
            Revised content or indication that no revision was needed
        """
        context.mark_started()
        
        try:
            # Get revision inputs
            facts_needing_revision = inputs.get("facts_needing_revision") or context.state.get("facts_needing_revision", [])
            credibility_scores = inputs.get("credibility_scores") or context.state.get("credibility_scores", {})
            consensus_details = inputs.get("consensus_details") or context.state.get("consensus_details", {})
            
            # Get original content and extracted facts
            original_content = context.state.get("original_content", "")
            extracted_facts_data = context.state.get("extracted_facts", [])
            
            # Check if revision is needed
            if not facts_needing_revision:
                context.mark_completed()
                return {
                    "revised_content": original_content,
                    "revision_needed": False,
                    "revision_summary": "No revision needed - all facts passed validation",
                    "success": True
                }
            
            # Prepare revision instructions
            revision_instructions = self._prepare_revision_instructions(
                facts_needing_revision,
                credibility_scores,
                consensus_details,
                extracted_facts_data
            )
            
            # Get LLM interface
            llm_interface = context.services.get("llm_interface")
            if not llm_interface:
                raise ValueError("LLM interface not available")
            
            # Generate revised content
            prompt = f"""作为{self.revision_role}，请根据以下审查反馈修改原始内容。

原始内容：
{original_content}

审查反馈：
{revision_instructions}

请提供修订后的完整内容，确保修正所有被指出的问题，同时保持内容的连贯性和完整性。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = await llm_interface.generate(messages)
            
            revised_content = response.get("content", "")
            
            # Store in workflow state
            context.state["revised_content"] = revised_content
            context.state["revision_instructions"] = revision_instructions
            
            context.mark_completed()
            
            return {
                "revised_content": revised_content,
                "revision_needed": True,
                "revision_summary": f"Revised {len(facts_needing_revision)} facts with low credibility",
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"RevisionNode execution failed: {e}")
            return {
                "revised_content": "",
                "revision_needed": False,
                "revision_summary": f"Revision failed: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _prepare_revision_instructions(
        self,
        facts_needing_revision: List[str],
        credibility_scores: Dict[str, float],
        consensus_details: Dict[str, Dict],
        extracted_facts: List[Dict]
    ) -> str:
        """
        Prepare detailed revision instructions based on consensus results.
        
        Args:
            facts_needing_revision: List of fact IDs needing revision
            credibility_scores: Credibility scores for each fact
            consensus_details: Detailed consensus information
            extracted_facts: List of extracted facts
            
        Returns:
            Formatted revision instructions
        """
        if not facts_needing_revision:
            return "所有内容均已通过事实验证，无需修改。"
        
        # Create a mapping of fact IDs to content
        fact_content_map = {fact.get("id"): fact.get("content") for fact in extracted_facts}
        
        instructions = "以下内容需要修订，因为它们的可信度较低：\n\n"
        
        for i, fact_id in enumerate(facts_needing_revision):
            fact_content = fact_content_map.get(fact_id, "未知内容")
            credibility = credibility_scores.get(fact_id, 0.0)
            details = consensus_details.get(fact_id, {})
            
            instructions += f"{i+1}. 内容：\"{fact_content}\"\n"
            instructions += f"   可信度评分：{credibility:.2f}\n"
            
            if self.provide_evidence_details and details:
                method = details.get("method", "unknown")
                if method == "weighted_average":
                    instructions += f"   评估方法：加权平均\n"
                    instructions += f"   支持性证据强度：{details.get('supporting_score', 0):.2f}\n"
                    instructions += f"   质疑性证据强度：{details.get('challenging_score', 0):.2f}\n"
                elif method == "majority_vote":
                    instructions += f"   评估方法：多数投票\n"
                    instructions += f"   支持票数：{details.get('supporting_votes', 0)}\n"
                    instructions += f"   质疑票数：{details.get('challenging_votes', 0)}\n"
                elif method == "synthesis":
                    instructions += f"   评估方法：综合分析\n"
                    if "reasoning" in details:
                        instructions += f"   分析理由：{details.get('reasoning', '')[:200]}...\n"
            
            instructions += "\n"
        
        instructions += "\n请修正上述内容中的不准确信息，确保修订后的内容具有更高的准确性和可信度。"
        
        return instructions
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Return input schema for the revision node."""
        return {
            "type": "object",
            "properties": {
                "facts_needing_revision": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of fact IDs that need revision"
                },
                "credibility_scores": {
                    "type": "object",
                    "description": "Credibility scores for each fact"
                },
                "consensus_details": {
                    "type": "object",
                    "description": "Detailed consensus information"
                }
            },
            "required": ["facts_needing_revision"]
        }
    
    def get_output_schema(self) -> Dict[str, Any]:
        """Return output schema for the revision node."""
        return {
            "type": "object",
            "properties": {
                "revised_content": {
                    "type": "string",
                    "description": "Revised content"
                },
                "revision_needed": {
                    "type": "boolean",
                    "description": "Whether revision was needed"
                },
                "revision_summary": {
                    "type": "string",
                    "description": "Summary of revisions made"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether revision was successful"
                }
            },
            "required": ["revised_content", "revision_needed", "success"]
        }