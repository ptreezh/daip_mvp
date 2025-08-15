"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : refinement_node.py
@Description:
    IterativeRefinementNode for Multi-perspective Synthesis Workflow.
"""
import logging
from datetime import datetime
from typing import Any

from ..base import ExecutionContext, InstitutionalPrimitive
from .models import SynthesisQuality, SynthesisResult

logger = logging.getLogger(__name__)


class IterativeRefinementNode(InstitutionalPrimitive):
    """迭代优化节点 - Iteratively refines synthesis quality through additional expert input.
    
    Implements iterative refinement by requesting additional expert input or deeper analysis
    on specific aspects when synthesis quality is insufficient.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.max_iterations = config.get("max_iterations", 3) if config else 3
        self.quality_threshold = config.get("quality_threshold", 0.7) if config else 0.7
        self.improvement_threshold = config.get("improvement_threshold", 0.1) if config else 0.1
        self.refinement_strategies = config.get("refinement_strategies", ["depth", "breadth", "insight"]) if config else ["depth", "breadth", "insight"]
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute iterative refinement of synthesis.
        
        Args:
            inputs: Should contain 'synthesis_result' to refine
            context: Execution context
            
        Returns:
            Refined synthesis result
        """
        context.mark_started()
        
        try:
            # Get synthesis result from inputs or workflow state
            synthesis_data = inputs.get("synthesis_result") or context.state.get("synthesis_result", {})
            
            if not synthesis_data:
                raise ValueError("Synthesis result is required for refinement")
            
            # Convert to SynthesisResult object
            synthesis_result = SynthesisResult(**synthesis_data)
            
            # Check if refinement is needed
            if not synthesis_result.quality_assessment:
                logger.warning("No quality assessment available, skipping refinement")
                context.mark_completed()
                return {
                    "refined_synthesis": synthesis_result.model_dump(),
                    "refinement_applied": False,
                    "iterations_performed": 0,
                    "final_quality_score": 0.0,
                    "success": True
                }
            
            current_quality = synthesis_result.quality_assessment.overall_score
            
            if current_quality >= self.quality_threshold:
                logger.info(f"Synthesis quality ({current_quality:.2f}) already meets threshold ({self.quality_threshold})")
                context.mark_completed()
                return {
                    "refined_synthesis": synthesis_result.model_dump(),
                    "refinement_applied": False,
                    "iterations_performed": 0,
                    "final_quality_score": current_quality,
                    "success": True
                }
            
            # Get services
            llm_interface = context.services.get("llm_interface")
            synthesis_engine = context.services.get("synthesis_engine")
            
            if not llm_interface or not synthesis_engine:
                raise ValueError("LLM interface and synthesis engine are required for refinement")
            
            # Perform iterative refinement
            refined_result = synthesis_result
            iterations_performed = 0
            
            for iteration in range(self.max_iterations):
                logger.info(f"Starting refinement iteration {iteration + 1}")
                
                # Identify areas for improvement
                improvement_areas = self._identify_improvement_areas(refined_result.quality_assessment)
                
                if not improvement_areas:
                    logger.info("No specific improvement areas identified")
                    break
                
                # Generate refinement requests
                refinement_requests = await self._generate_refinement_requests(
                    refined_result, 
                    improvement_areas, 
                    llm_interface
                )
                
                # Apply refinements
                new_synthesis = await self._apply_refinements(
                    refined_result,
                    refinement_requests,
                    synthesis_engine
                )
                
                # Assess new quality
                new_quality_assessment = self._assess_refined_quality(new_synthesis, refined_result)
                
                # Check for improvement
                quality_improvement = new_quality_assessment.overall_score - refined_result.quality_assessment.overall_score
                
                if quality_improvement >= self.improvement_threshold:
                    # Update synthesis result
                    refined_result = SynthesisResult(
                        topic=refined_result.topic,
                        perspectives=refined_result.perspectives,
                        synthesis=new_synthesis,
                        key_insights=self._extract_key_insights(new_synthesis),
                        expert_contributions=refined_result.expert_contributions,
                        confidence=min(refined_result.confidence + quality_improvement * 0.1, 1.0),
                        quality_assessment=new_quality_assessment,
                        refinement_iterations=iteration + 1,
                        metadata={
                            **refined_result.metadata,
                            "last_refinement_timestamp": datetime.now().isoformat(),
                            "refinement_history": refined_result.metadata.get("refinement_history", []) + [
                                {
                                    "iteration": iteration + 1,
                                    "improvement_areas": improvement_areas,
                                    "quality_improvement": quality_improvement,
                                    "timestamp": datetime.now().isoformat()
                                }
                            ]
                        }
                    )
                    iterations_performed = iteration + 1
                    
                    # Check if quality threshold is met
                    if new_quality_assessment.overall_score >= self.quality_threshold:
                        logger.info(f"Quality threshold reached after {iterations_performed} iterations")
                        break
                else:
                    logger.info(f"Insufficient improvement ({quality_improvement:.3f}) in iteration {iteration + 1}")
                    break
            
            # Store refined result in workflow state
            context.state["refined_synthesis_result"] = refined_result.model_dump()
            
            context.mark_completed()
            
            return {
                "refined_synthesis": refined_result.model_dump(),
                "refinement_applied": iterations_performed > 0,
                "iterations_performed": iterations_performed,
                "final_quality_score": refined_result.quality_assessment.overall_score,
                "quality_improvement": refined_result.quality_assessment.overall_score - current_quality,
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"IterativeRefinementNode execution failed: {e}")
            return {
                "refined_synthesis": {},
                "refinement_applied": False,
                "iterations_performed": 0,
                "final_quality_score": 0.0,
                "quality_improvement": 0.0,
                "success": False,
                "error": str(e)
            }
    
    def _identify_improvement_areas(self, quality_assessment: SynthesisQuality) -> list[str]:
        """Identify specific areas that need improvement."""
        improvement_areas = []
        
        # Check each quality dimension
        if quality_assessment.depth_score < 0.6:
            improvement_areas.append("depth")
        
        if quality_assessment.breadth_score < 0.6:
            improvement_areas.append("breadth")
        
        if quality_assessment.insight_score < 0.6:
            improvement_areas.append("insight")
        
        if quality_assessment.coherence_score < 0.6:
            improvement_areas.append("coherence")
        
        # Use improvement suggestions if available
        if quality_assessment.improvement_suggestions:
            improvement_areas.extend(quality_assessment.improvement_suggestions[:2])  # Limit to top 2
        
        return improvement_areas[:3]  # Limit to top 3 areas
    
    async def _generate_refinement_requests(
        self,
        synthesis_result: SynthesisResult,
        improvement_areas: list[str],
        llm_interface
    ) -> list[str]:
        """Generate specific refinement requests based on improvement areas."""
        refinement_requests = []
        
        for area in improvement_areas:
            if area == "depth":
                request = f"""请对以下综合分析进行深度改进：

原始分析：
{synthesis_result.synthesis[:500]}...

改进要求：
1. 深入探讨根本机制和原理
2. 分析深层次的因果关系
3. 揭示隐含的影响因素
4. 提供更深入的理论支撑

请提供改进建议和具体的深度分析内容。"""
            
            elif area == "breadth":
                missing_perspectives = self._identify_missing_perspectives(synthesis_result)
                request = f"""请对以下综合分析进行广度改进：

原始分析：
{synthesis_result.synthesis[:500]}...

改进要求：
1. 补充遗漏的视角：{', '.join(missing_perspectives)}
2. 确保所有重要方面都得到覆盖
3. 平衡不同视角的权重
4. 增加跨领域的关联分析

请提供改进建议和补充内容。"""
            
            elif area == "insight":
                request = f"""请对以下综合分析进行洞察力改进：

原始分析：
{synthesis_result.synthesis[:500]}...

改进要求：
1. 提供独特的见解和发现
2. 识别非显而易见的模式和趋势
3. 预测未来发展方向
4. 提出创新性的观点或解决方案

请提供改进建议和新的洞察内容。"""
            
            elif area == "coherence":
                request = f"""请对以下综合分析进行逻辑结构改进：

原始分析：
{synthesis_result.synthesis[:500]}...

改进要求：
1. 改善逻辑结构和论证流程
2. 增强段落间的连贯性
3. 明确观点之间的关系
4. 优化表述的清晰度

请提供改进建议和结构优化方案。"""
            
            else:
                # Handle custom improvement suggestions
                request = f"""请对以下综合分析进行改进：

原始分析：
{synthesis_result.synthesis[:500]}...

具体改进要求：{area}

请提供改进建议和具体的改进内容。"""
            
            # Generate refinement suggestion
            messages = [
                {"role": "system", "content": "你是一位专业的内容改进专家，擅长提升分析报告的质量。"},
                {"role": "user", "content": request}
            ]
            
            try:
                response = await llm_interface.generate(messages)
                refinement_requests.append(response.get("content", ""))
            except Exception as e:
                logger.error(f"Failed to generate refinement request for {area}: {e}")
        
        return refinement_requests
    
    def _identify_missing_perspectives(self, synthesis_result: SynthesisResult) -> list[str]:
        """Identify missing perspectives in the synthesis."""
        expected_perspectives = ["经济", "社会", "技术", "伦理", "政治", "环境", "文化", "法律"]
        covered_perspectives = synthesis_result.perspectives
        
        missing = [p for p in expected_perspectives if p not in covered_perspectives]
        return missing[:3]  # Return at most 3 missing perspectives
    
    async def _apply_refinements(
        self,
        synthesis_result: SynthesisResult,
        refinement_requests: list[str],
        synthesis_engine
    ) -> str:
        """Apply refinement requests to generate improved synthesis."""
        from src.models import DebateTurn
        
        # Prepare refinement input
        refinement_input = []
        
        # Add original synthesis
        refinement_input.append(DebateTurn(
            round=1,
            role_id="original_synthesis",
            opinion=f"原始综合分析：\n{synthesis_result.synthesis}"
        ))
        
        # Add refinement requests
        for i, request in enumerate(refinement_requests):
            refinement_input.append(DebateTurn(
                round=i + 2,
                role_id=f"refinement_expert_{i+1}",
                opinion=request
            ))
        
        # Add final refinement instruction
        refinement_instruction = """基于以上原始分析和改进建议，请生成一个改进后的综合分析，确保：

1. 保持原有分析的优点和核心观点
2. 整合所有改进建议的精华内容
3. 提升分析的深度、广度、洞察力和逻辑性
4. 确保内容的连贯性和可读性
5. 生成比原始分析更高质量的最终版本

请直接提供改进后的完整综合分析。"""
        
        refinement_input.append(DebateTurn(
            round=len(refinement_input) + 1,
            role_id="refinement_coordinator",
            opinion=refinement_instruction
        ))
        
        # Generate refined synthesis
        refined_synthesis = await synthesis_engine.synthesize_opinions(
            topic=f"{synthesis_result.topic} - 改进版本",
            history=refinement_input
        )
        
        return refined_synthesis
    
    def _assess_refined_quality(self, refined_synthesis: str, original_result: SynthesisResult) -> SynthesisQuality:
        """Assess the quality of the refined synthesis."""
        # Use similar assessment logic as the original synthesis node
        # This is a simplified version - in practice would use more sophisticated assessment
        
        # Depth score - based on analysis depth indicators
        depth_indicators = ["机制", "原理", "根本", "深层", "本质", "核心", "关键", "重要", "深入", "详细"]
        depth_score = min(sum(1 for indicator in depth_indicators if indicator in refined_synthesis) / len(depth_indicators), 1.0)
        
        # Breadth score - based on perspective coverage
        perspectives = original_result.perspectives
        perspectives_mentioned = sum(1 for perspective in perspectives if perspective in refined_synthesis)
        breadth_score = perspectives_mentioned / len(perspectives) if perspectives else 0
        
        # Insight score - based on insight indicators
        insight_indicators = ["洞察", "发现", "揭示", "表明", "说明", "证明", "显示", "反映", "预测", "趋势"]
        insight_score = min(sum(1 for indicator in insight_indicators if indicator in refined_synthesis) / len(insight_indicators), 1.0)
        
        # Coherence score - based on structure and flow
        structure_indicators = ["首先", "其次", "然后", "最后", "总之", "综上", "因此", "所以", "另外", "此外"]
        coherence_score = min(sum(1 for indicator in structure_indicators if indicator in refined_synthesis) / len(structure_indicators), 1.0)
        
        # Overall score with slight bonus for refinement
        overall_score = (depth_score * 0.3 + breadth_score * 0.3 + insight_score * 0.25 + coherence_score * 0.15) * 1.05
        overall_score = min(overall_score, 1.0)
        
        # Generate improvement suggestions for next iteration
        improvement_suggestions = []
        if depth_score < 0.7:
            improvement_suggestions.append("仍需更深入的分析")
        if breadth_score < 0.8:
            improvement_suggestions.append("需要更全面的视角覆盖")
        if insight_score < 0.7:
            improvement_suggestions.append("需要更多独特洞察")
        if coherence_score < 0.7:
            improvement_suggestions.append("需要改善逻辑结构")
        
        return SynthesisQuality(
            depth_score=depth_score,
            breadth_score=breadth_score,
            insight_score=insight_score,
            coherence_score=coherence_score,
            overall_score=overall_score,
            improvement_suggestions=improvement_suggestions,
            metadata={
                "assessment_timestamp": datetime.now().isoformat(),
                "synthesis_length": len(refined_synthesis),
                "refinement_applied": True
            }
        )
    
    def _extract_key_insights(self, synthesis: str) -> list[str]:
        """Extract key insights from refined synthesis text."""
        import re
        
        insights = []
        
        # Look for numbered lists
        numbered_items = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', synthesis, re.DOTALL)
        if numbered_items:
            insights.extend([item.strip() for item in numbered_items if len(item.strip()) > 20])
        
        # Look for bullet points
        bullet_items = re.findall(r'[•\-\*]\s+(.*?)(?=[•\-\*]|$)', synthesis, re.DOTALL)
        if bullet_items:
            insights.extend([item.strip() for item in bullet_items if len(item.strip()) > 20])
        
        # Look for insight sections
        insight_sections = re.findall(r'(?:洞察|见解|发现|结论|关键点)[：:]\s*(.*?)(?=\n\n|$)', synthesis, re.DOTALL)
        if insight_sections:
            for section in insight_sections:
                items = re.split(r'(?:\n|。)', section)
                insights.extend([item.strip() for item in items if len(item.strip()) > 20])
        
        # Limit and return
        insights = [insight for insight in insights if len(insight) <= 200]
        return insights[:5]
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the iterative refinement node."""
        return {
            "type": "object",
            "properties": {
                "synthesis_result": {
                    "type": "object",
                    "description": "Synthesis result to refine"
                }
            },
            "required": ["synthesis_result"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the iterative refinement node."""
        return {
            "type": "object",
            "properties": {
                "refined_synthesis": {
                    "type": "object",
                    "description": "Refined synthesis result"
                },
                "refinement_applied": {
                    "type": "boolean",
                    "description": "Whether refinement was applied"
                },
                "iterations_performed": {
                    "type": "integer",
                    "description": "Number of refinement iterations performed"
                },
                "final_quality_score": {
                    "type": "number",
                    "description": "Final quality score after refinement"
                },
                "quality_improvement": {
                    "type": "number",
                    "description": "Quality improvement achieved"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether refinement was successful"
                }
            },
            "required": ["refined_synthesis", "refinement_applied", "iterations_performed", "final_quality_score", "success"]
        }