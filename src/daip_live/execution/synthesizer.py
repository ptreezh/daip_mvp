"""
Result synthesis system for combining outputs from multiple Subagents/skills.
"""
from typing import List, Dict, Any
from ..subagents.base import AnalysisResult
from ..skills.base import SkillOutput


class ResultSynthesizer:
    """Synthesizes results from multiple sources."""
    
    def __init__(self):
        pass
    
    def synthesize_subagent_results(self, results: List[AnalysisResult]) -> AnalysisResult:
        """
        Synthesize results from multiple Subagents.
        
        Args:
            results: List of AnalysisResult objects
            
        Returns:
            Synthesized AnalysisResult
        """
        if not results:
            return AnalysisResult(
                content="No results to synthesize",
                metadata={"synthesized": True, "result_count": 0}
            )
        
        if len(results) == 1:
            return results[0]
        
        # Combine the content from all results
        combined_content = "\n\n---\n\n".join([result.content for result in results])
        
        # Calculate average confidence
        avg_confidence = sum([result.confidence for result in results]) / len(results)
        
        # Combine metadata
        combined_metadata = {
            "synthesized": True,
            "result_count": len(results),
            "individual_results": [
                {
                    "subagent": result.subagent_name,
                    "confidence": result.confidence,
                    "metadata": result.metadata
                }
                for result in results
            ],
            "average_confidence": avg_confidence
        }
        
        # Use the name of the first Subagent as the synthesized result name
        synthesized_name = f"Synthesized from {len(results)} Subagents"
        
        return AnalysisResult(
            content=combined_content,
            metadata=combined_metadata,
            confidence=avg_confidence,
            subagent_name=synthesized_name
        )
    
    def synthesize_skill_outputs(self, outputs: List[SkillOutput]) -> SkillOutput:
        """
        Synthesize outputs from multiple skills.
        
        Args:
            outputs: List of SkillOutput objects
            
        Returns:
            Synthesized SkillOutput
        """
        if not outputs:
            return SkillOutput(
                result="No outputs to synthesize",
                metadata={"synthesized": True, "output_count": 0}
            )
        
        if len(outputs) == 1:
            return outputs[0]
        
        # Combine the results from all outputs
        combined_result = "\n\n---\n\n".join([output.result for output in outputs])
        
        # Calculate average confidence
        avg_confidence = sum([output.confidence for output in outputs]) / len(outputs)
        
        # Combine metadata
        combined_metadata = {
            "synthesized": True,
            "output_count": len(outputs),
            "individual_outputs": [
                {
                    "skill": output.metadata.get("skill_name", "Unknown"),
                    "confidence": output.confidence,
                    "execution_time": output.execution_time,
                    "metadata": output.metadata
                }
                for output in outputs
            ],
            "average_confidence": avg_confidence
        }
        
        # Calculate total execution time
        total_execution_time = sum([output.execution_time for output in outputs])
        
        return SkillOutput(
            result=combined_result,
            metadata=combined_metadata,
            confidence=avg_confidence,
            execution_time=total_execution_time
        )
    
    def resolve_conflicts(self, results: List[AnalysisResult]) -> AnalysisResult:
        """
        Resolve conflicts between different results.
        
        Args:
            results: List of AnalysisResult objects with potential conflicts
            
        Returns:
            Conflict-resolved AnalysisResult
        """
        # This is a simplified implementation
        # A full implementation would need more sophisticated conflict resolution logic
        if not results:
            return AnalysisResult(
                content="No results to resolve conflicts for",
                metadata={"conflict_resolution": True, "result_count": 0}
            )
        
        # For now, we'll just return the result with the highest confidence
        best_result = max(results, key=lambda r: r.confidence)
        
        # Add conflict resolution metadata
        resolution_metadata = best_result.metadata.copy()
        resolution_metadata["conflict_resolution"] = {
            "method": "highest_confidence",
            "selected_from": len(results),
            "selected_confidence": best_result.confidence
        }
        
        return AnalysisResult(
            content=best_result.content,
            metadata=resolution_metadata,
            confidence=best_result.confidence,
            subagent_name=best_result.subagent_name
        )