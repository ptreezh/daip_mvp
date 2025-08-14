"""@Time    : 2025-07-23 13:00:00
@Author  : DAIP-LIVE Team
@File    : consensus_node.py
@Description:
    Implementation of ConsensusNode for the Critical Review Workflow.
    Calculates credibility scores using synthesis engine or voting algorithms.
"""
import logging
from typing import Any, Dict, Tuple

from .base import ExecutionContext, InstitutionalPrimitive

logger = logging.getLogger(__name__)


class ConsensusNode(InstitutionalPrimitive):
    """共识计算节点 - Calculates credibility scores using synthesis engine or voting algorithms.
    
    Uses SynthesisEngine or voting algorithms to assign credibility scores
    to each factual assertion based on aggregated evidence.
    """

    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.consensus_method = config.get("consensus_method", "weighted_average") if config else "weighted_average"
        self.credibility_threshold = config.get("credibility_threshold", 0.6) if config else 0.6
        self.use_synthesis_engine = config.get("use_synthesis_engine", True) if config else True

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute consensus calculation on aggregated evidence.
        
        Args:
            inputs: Should contain 'aggregated_evidence' from evidence aggregation
            context: Execution context
            
        Returns:
            Final credibility scores and consensus results

        """
        context.mark_started()

        try:
            # Get aggregated evidence from inputs or workflow state
            aggregated_evidence = inputs.get("aggregated_evidence") or context.state.get("aggregated_evidence", {})

            if not aggregated_evidence:
                raise ValueError("Aggregated evidence is required for consensus calculation")

            # Calculate consensus for each fact
            consensus_results = {}
            final_credibility_scores = {}
            facts_needing_revision = []
            consensus_details = {}

            # Get extracted facts for reference
            extracted_facts_data = context.state.get("extracted_facts", [])
            extracted_facts = {fact.get("id"): fact for fact in extracted_facts_data}

            # Process each fact
            for fact_id, evidence_data in aggregated_evidence.items():
                # Choose consensus method
                if self.consensus_method == "weighted_average":
                    credibility, details = self._calculate_weighted_average_consensus(evidence_data)
                elif self.consensus_method == "majority_vote":
                    credibility, details = self._calculate_majority_vote_consensus(evidence_data)
                elif self.consensus_method == "synthesis" and self.use_synthesis_engine:
                    credibility, details = await self._calculate_synthesis_consensus(evidence_data, context)
                else:
                    # Default to weighted average
                    credibility, details = self._calculate_weighted_average_consensus(evidence_data)

                # Store results
                final_credibility_scores[fact_id] = credibility
                consensus_details[fact_id] = details

                # Check if fact needs revision
                if credibility < self.credibility_threshold:
                    facts_needing_revision.append(fact_id)

                # Create consensus result
                consensus_results[fact_id] = {
                    "fact_id": fact_id,
                    "fact_content": extracted_facts.get(fact_id, {}).get("content", "Unknown fact"),
                    "credibility_score": credibility,
                    "consensus_method": self.consensus_method,
                    "needs_revision": credibility < self.credibility_threshold,
                    "evidence_summary": evidence_data.get("evidence_summary", ""),
                    "consensus_details": details
                }

            # Store in workflow state
            context.state["credibility_scores"] = final_credibility_scores
            context.state["facts_needing_revision"] = facts_needing_revision
            context.state["consensus_details"] = consensus_details
            context.state["consensus_results"] = consensus_results

            context.mark_completed()

            return {
                "credibility_scores": final_credibility_scores,
                "facts_needing_revision": facts_needing_revision,
                "consensus_results": consensus_results,
                "success": True
            }

        except Exception as e:
            context.mark_failed()
            logger.error(f"ConsensusNode execution failed: {e}")

            return {
                "consensus_results": {},
                "credibility_scores": {},
                "facts_needing_revision": [],
                "success": False,
                "error": str(e)
            }

    def _calculate_weighted_average_consensus(self, evidence_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Calculate consensus using weighted average of evidence scores.
        
        Args:
            evidence_data: Aggregated evidence data
            
        Returns:
            Tuple of (credibility_score, consensus_details)

        """
        supporting_score = evidence_data.get("supporting_score", 0.0)
        challenging_score = evidence_data.get("challenging_score", 0.0)
        neutral_score = evidence_data.get("neutral_score", 0.0)

        # Calculate weighted credibility
        total_weight = supporting_score + challenging_score + neutral_score
        if total_weight > 0:
            # Supporting evidence increases credibility, challenging decreases it
            weighted_score = (supporting_score - challenging_score) / total_weight
            # Convert to 0-1 scale
            credibility = min(max(0.5 + weighted_score * 0.5, 0.0), 1.0)
        else:
            credibility = 0.5  # Neutral when no evidence

        details = {
            "method": "weighted_average",
            "supporting_score": supporting_score,
            "challenging_score": challenging_score,
            "neutral_score": neutral_score,
            "total_weight": total_weight,
            "weighted_score": weighted_score if total_weight > 0 else 0.0
        }

        return credibility, details

    def _calculate_majority_vote_consensus(self, evidence_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Calculate consensus using majority vote of evidence counts.
        
        Args:
            evidence_data: Aggregated evidence data
            
        Returns:
            Tuple of (credibility_score, consensus_details)

        """
        supporting_count = evidence_data.get("supporting_count", 0)
        challenging_count = evidence_data.get("challenging_count", 0)
        neutral_count = evidence_data.get("neutral_count", 0)

        total_votes = supporting_count + challenging_count + neutral_count

        if total_votes == 0:
            return 0.5, {
                "method": "majority_vote",
                "supporting_votes": supporting_count,
                "challenging_votes": challenging_count,
                "neutral_votes": neutral_count,
                "total_votes": 0,
                "outcome": "no_evidence"
            }

        # Calculate vote percentages
        supporting_percentage = supporting_count / total_votes
        challenging_percentage = challenging_count / total_votes

        # Determine outcome
        if supporting_percentage > challenging_percentage:
            outcome = "supporting"
            # Scale credibility based on margin of victory
            margin = supporting_percentage - challenging_percentage
            credibility = min(0.5 + margin * 0.5, 1.0)
        elif challenging_percentage > supporting_percentage:
            outcome = "challenging"
            # Scale credibility based on margin of victory
            margin = challenging_percentage - supporting_percentage
            credibility = max(0.5 - margin * 0.5, 0.0)
        else:
            outcome = "tie"
            credibility = 0.5

        details = {
            "method": "majority_vote",
            "supporting_votes": supporting_count,
            "challenging_votes": challenging_count,
            "neutral_votes": neutral_count,
            "total_votes": total_votes,
            "supporting_percentage": supporting_percentage,
            "challenging_percentage": challenging_percentage,
            "outcome": outcome
        }

        return credibility, details

    def _calculate_majority_vote(self, evidence_data: Dict[str, Any]) -> float:
        """Calculate credibility score using majority vote method.
        This is a simplified version for testing.
        
        Args:
            evidence_data: Evidence data with vote counts
            
        Returns:
            Credibility score

        """
        supporting = evidence_data.get("supporting_count", 0)
        challenging = evidence_data.get("challenging_count", 0)
        total = supporting + challenging

        if total == 0:
            return 0.5

        # Calculate credibility based on vote ratio
        supporting_ratio = supporting / total
        return min(max(supporting_ratio, 0.0), 1.0)

    def _calculate_weighted_consensus(self, evidence_data: Dict[str, Any]) -> float:
        """Calculate credibility score using weighted average method.
        This is a simplified version for testing.
        
        Args:
            evidence_data: Evidence data with scores
            
        Returns:
            Credibility score

        """
        supporting = evidence_data.get("supporting_score", 0.0)
        challenging = evidence_data.get("challenging_score", 0.0)
        neutral = evidence_data.get("neutral_score", 0.0)

        total_weight = supporting + challenging + neutral
        if total_weight == 0:
            return 0.5

        # Supporting increases credibility, challenging decreases it
        weighted_score = (supporting - challenging) / total_weight
        # Convert to 0-1 scale
        return min(max(0.5 + weighted_score * 0.5, 0.0), 1.0)

    async def _calculate_synthesis_consensus(self, evidence_data: Dict[str, Any], context: ExecutionContext) -> Tuple[float, Dict[str, Any]]:
        """Calculate consensus using synthesis engine for complex evidence analysis.
        
        Args:
            evidence_data: Aggregated evidence data
            context: Execution context
            
        Returns:
            Tuple of (credibility_score, consensus_details)

        """
        # Get synthesis engine
        synthesis_engine = context.services.get("synthesis_engine")
        if not synthesis_engine:
            # Fall back to weighted average if synthesis engine not available
            return self._calculate_weighted_average_consensus(evidence_data)

        # Prepare evidence summary for synthesis
        supporting_evidence = evidence_data.get("supporting_count", 0)
        challenging_evidence = evidence_data.get("challenging_count", 0)

        evidence_summary = f"""
Fact: {evidence_data.get('fact_content', 'Unknown fact')}

Evidence Summary:
- Supporting Evidence: {supporting_evidence} items
- Challenging Evidence: {challenging_evidence} items
- Evidence Details: {evidence_data.get('evidence_summary', 'No details available')}

Please analyze this evidence and determine a credibility score between 0.0 (completely unreliable) 
and 1.0 (completely reliable) for this fact. Provide your reasoning.
"""

        # Use synthesis engine to analyze evidence
        try:
            synthesis_result = await synthesis_engine.synthesize_opinions(
                topic="Fact Credibility Analysis",
                history=[{"round": 1, "role_id": "evidence_analyzer", "opinion": evidence_summary}]
            )

            # Extract credibility score from synthesis result
            # This is a simplified implementation - in practice would use more sophisticated parsing
            credibility = 0.5  # Default
            reasoning = synthesis_result

            # Simple regex-free parsing
            if "credibility score:" in synthesis_result.lower():
                parts = synthesis_result.lower().split("credibility score:")
                if len(parts) > 1:
                    score_text = parts[1].strip().split()[0]
                    try:
                        credibility = float(score_text)
                        credibility = min(max(credibility, 0.0), 1.0)  # Ensure in range 0-1
                    except ValueError:
                        pass

            details = {
                "method": "synthesis",
                "reasoning": reasoning[:500] + "..." if len(reasoning) > 500 else reasoning,
                "supporting_count": supporting_evidence,
                "challenging_count": challenging_evidence
            }

            return credibility, details

        except Exception as e:
            logger.error(f"Synthesis consensus calculation failed: {e}")
            # Fall back to weighted average
            return self._calculate_weighted_average_consensus(evidence_data)

    def get_input_schema(self) -> Dict[str, Any]:
        """Return input schema for the consensus node."""
        return {
            "type": "object",
            "properties": {
                "aggregated_evidence": {
                    "type": "object",
                    "description": "Aggregated evidence for each fact"
                }
            },
            "required": ["aggregated_evidence"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        """Return output schema for the consensus node."""
        return {
            "type": "object",
            "properties": {
                "credibility_scores": {
                    "type": "object",
                    "description": "Credibility scores for each fact"
                },
                "facts_needing_revision": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of fact IDs that need revision"
                },
                "consensus_results": {
                    "type": "object",
                    "description": "Detailed consensus results for each fact"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether consensus calculation was successful"
                }
            },
            "required": ["credibility_scores", "facts_needing_revision", "success"]
        }
