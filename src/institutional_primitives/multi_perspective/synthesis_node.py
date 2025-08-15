"""@Time    : 2025-07-24 16:30:00
@Author  : DAIP-LIVE Team
@File    : synthesis_node.py
@Description:
    Enhanced SynthesisNode for Multi-perspective Synthesis Workflow.
"""
import logging
import re
from datetime import datetime
from typing import Any

from ..base import ExecutionContext, InstitutionalPrimitive
from .models import SynthesisQuality, SynthesisResult, ViewpointCollection

logger = logging.getLogger(__name__)


class EnhancedSynthesisNode(InstitutionalPrimitive):
    """增强观点综合节点 - Synthesizes diverse expert viewpoints with quality assessment.
    
    Uses SynthesisEngine to merge diverse and potentially conflicting viewpoints
    into a comprehensive, insightful, and nuanced synthesis report with quality assessment.
    """
    
    def __init__(self, primitive_id: str, config: dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.synthesis_method = config.get("synthesis_method", "dialectical") if config else "dialectical"
        self.min_confidence_threshold = config.get("min_confidence_threshold", 0.6) if config else 0.6
        self.include_expert_attribution = config.get("include_expert_attribution", True) if config else True
        self.quality_threshold = config.get("quality_threshold", 0.7) if config else 0.7
        self.max_synthesis_length = config.get("max_synthesis_length", 2000) if config else 2000
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> dict[str, Any]:
        """Execute enhanced synthesis of viewpoint collection.
        
        Args:
            inputs: Should contain 'viewpoint_collection' to synthesize
            context: Execution context
            
        Returns:
            Enhanced synthesis with quality assessment
        """
        context.mark_started()
        
        try:
            # Get viewpoint collection from inputs or workflow state
            collection_data = inputs.get("viewpoint_collection") or context.state.get("viewpoint_collection", {})
            topic = inputs.get("topic") or context.state.get("topic", "Unknown topic")
            
            if not collection_data:
                raise ValueError("Viewpoint collection is required for synthesis")
            
            # Convert to ViewpointCollection object
            collection = ViewpointCollection(**collection_data)
            
            if not collection.viewpoints:
                raise ValueError("No viewpoints available for synthesis")
            
            # Get synthesis engine
            synthesis_engine = context.services.get("synthesis_engine")
            if not synthesis_engine:
                raise ValueError("Synthesis engine not available")
            
            # Prepare synthesis input with conflict and consensus awareness
            synthesis_input = self._prepare_enhanced_synthesis_input(collection)
            
            # Generate synthesis
            synthesis_result = await synthesis_engine.synthesize_opinions(
                topic=topic,
                history=synthesis_input
            )
            
            # Assess synthesis quality
            quality_assessment = self._assess_synthesis_quality(synthesis_result, collection)
            
            # Extract key insights
            key_insights = self._extract_key_insights(synthesis_result)
            
            # Create expert contribution mapping
            expert_contributions = {}
            if self.include_expert_attribution:
                expert_contributions = self._create_expert_contributions(collection.viewpoints)
            
            # Calculate overall confidence
            confidence = self._calculate_synthesis_confidence(collection.viewpoints, quality_assessment)
            
            # Create synthesis result object
            result = SynthesisResult(
                topic=topic,
                perspectives=[vp.metadata.get("perspective", "Unknown") for vp in collection.viewpoints],
                synthesis=synthesis_result,
                key_insights=key_insights,
                expert_contributions=expert_contributions,
                confidence=confidence,
                quality_assessment=quality_assessment,
                refinement_iterations=0,
                metadata={
                    "synthesis_method": self.synthesis_method,
                    "viewpoint_count": len(collection.viewpoints),
                    "conflict_count": len(collection.conflicts),
                    "consensus_count": len(collection.consensus_areas),
                    "synthesis_timestamp": datetime.now().isoformat()
                }
            )
            
            # Store in workflow state
            context.state["synthesis_result"] = result.model_dump()
            
            context.mark_completed()
            
            return {
                "topic": topic,
                "synthesis": synthesis_result,
                "key_insights": key_insights,
                "expert_contributions": expert_contributions,
                "confidence": confidence,
                "quality_assessment": quality_assessment.model_dump(),
                "needs_refinement": quality_assessment.overall_score < self.quality_threshold,
                "success": True
            }
            
        except Exception as e:
            context.mark_failed()
            logger.error(f"EnhancedSynthesisNode execution failed: {e}")
            return {
                "topic": inputs.get("topic", "Unknown topic"),
                "synthesis": "",
                "key_insights": [],
                "expert_contributions": {},
                "confidence": 0.0,
                "quality_assessment": {},
                "needs_refinement": True,
                "success": False,
                "error": str(e)
            }
    
    def _prepare_enhanced_synthesis_input(self, collection: ViewpointCollection) -> list[dict[str, Any]]:
        """Prepare enhanced synthesis input with conflict and consensus awareness."""
        from src.models import DebateTurn
        
        synthesis_input = []
        
        # Add introduction with collection analysis
        intro_text = f"""我们正在讨论主题："{collection.topic}"。

以下是来自{len(collection.viewpoints)}位专家的观点分析：
- 涵盖视角：{', '.join(collection.metadata.get('perspectives', []))}
- 发现{len(collection.conflicts)}个观点冲突
- 识别出{len(collection.consensus_areas)}个共识领域
- 整体质量评分：{collection.quality_score:.2f}

请综合这些观点，特别注意处理冲突和强化共识，提供一个全面、深入、有洞察力的分析。"""
        
        synthesis_input.append(DebateTurn(
            round=1,
            role_id="moderator",
            opinion=intro_text
        ))
        
        # Add consensus areas first
        if collection.consensus_areas:
            consensus_text = "专家共识领域：\n" + "\n".join([f"• {area}" for area in collection.consensus_areas])
            synthesis_input.append(DebateTurn(
                round=2,
                role_id="consensus_analyzer",
                opinion=consensus_text
            ))
        
        # Add each expert viewpoint with perspective context
        for i, viewpoint in enumerate(collection.viewpoints):
            perspective = viewpoint.metadata.get("perspective", "Unknown")
            opinion = f"【{perspective}视角 - {viewpoint.expert_name}】\n\n{viewpoint.viewpoint}\n\n"
            
            if viewpoint.supporting_evidence:
                opinion += "支持证据：\n" + "\n".join([f"- {evidence}" for evidence in viewpoint.supporting_evidence]) + "\n\n"
            
            if viewpoint.reasoning_process:
                opinion += f"推理过程：\n{viewpoint.reasoning_process}\n\n"
            
            opinion += f"信心水平：{viewpoint.confidence:.2f}"
            
            synthesis_input.append(DebateTurn(
                round=i + 3,
                role_id=viewpoint.expert_name,
                opinion=opinion
            ))
        
        # Add conflict analysis
        if collection.conflicts:
            conflict_text = "观点冲突分析：\n"
            for conflict in collection.conflicts[:3]:  # Limit to top 3 conflicts
                conflict_text += f"• {conflict['description']} (冲突程度: {conflict['conflict_score']:.2f})\n"
            
            synthesis_input.append(DebateTurn(
                round=len(collection.viewpoints) + 3,
                role_id="conflict_analyzer",
                opinion=conflict_text
            ))
        
        # Add synthesis request with specific requirements
        synthesis_request = """请基于以上所有专家观点进行综合分析，确保：

1. **深度分析**：超越表面现象，揭示深层机制和原理
2. **广度覆盖**：整合所有重要视角，不遗漏关键方面
3. **洞察生成**：提供新的见解和发现，超越单一专家的认知
4. **冲突处理**：合理解释和调和不同观点的分歧
5. **共识强化**：基于专家共识构建可靠结论
6. **实用价值**：提供具有指导意义的分析和建议

请确保最终综合分析具有：
- 逻辑清晰的结构
- 基于证据的论证
- 平衡不同观点的表述
- 具有前瞻性的洞察
- 可操作的建议或结论"""
        
        synthesis_input.append(DebateTurn(
            round=len(synthesis_input) + 1,
            role_id="synthesis_coordinator",
            opinion=synthesis_request
        ))
        
        return synthesis_input
    
    def _assess_synthesis_quality(self, synthesis: str, collection: ViewpointCollection) -> SynthesisQuality:
        """Assess the quality of the synthesis."""
        # Depth score - based on analysis depth indicators
        depth_indicators = ["机制", "原理", "根本", "深层", "本质", "核心", "关键", "重要"]
        depth_score = min(sum(1 for indicator in depth_indicators if indicator in synthesis) / len(depth_indicators), 1.0)
        
        # Breadth score - based on perspective coverage
        perspectives_mentioned = sum(1 for vp in collection.viewpoints 
                                   if vp.metadata.get("perspective", "") in synthesis)
        breadth_score = perspectives_mentioned / len(collection.viewpoints) if collection.viewpoints else 0
        
        # Insight score - based on insight indicators
        insight_indicators = ["洞察", "发现", "揭示", "表明", "说明", "证明", "显示", "反映"]
        insight_score = min(sum(1 for indicator in insight_indicators if indicator in synthesis) / len(insight_indicators), 1.0)
        
        # Coherence score - based on structure and flow
        structure_indicators = ["首先", "其次", "然后", "最后", "总之", "综上", "因此", "所以"]
        coherence_score = min(sum(1 for indicator in structure_indicators if indicator in synthesis) / len(structure_indicators), 1.0)
        
        # Overall score
        overall_score = (depth_score * 0.3 + breadth_score * 0.3 + insight_score * 0.25 + coherence_score * 0.15)
        
        # Generate improvement suggestions
        improvement_suggestions = []
        if depth_score < 0.5:
            improvement_suggestions.append("需要更深入的分析，探讨根本机制和原理")
        if breadth_score < 0.7:
            improvement_suggestions.append("需要更全面地覆盖所有专家视角")
        if insight_score < 0.5:
            improvement_suggestions.append("需要提供更多独特的洞察和发现")
        if coherence_score < 0.5:
            improvement_suggestions.append("需要改善逻辑结构和表述连贯性")
        
        return SynthesisQuality(
            depth_score=depth_score,
            breadth_score=breadth_score,
            insight_score=insight_score,
            coherence_score=coherence_score,
            overall_score=overall_score,
            improvement_suggestions=improvement_suggestions,
            metadata={
                "assessment_timestamp": datetime.now().isoformat(),
                "synthesis_length": len(synthesis),
                "viewpoint_count": len(collection.viewpoints)
            }
        )
    
    def _extract_key_insights(self, synthesis: str) -> list[str]:
        """Extract key insights from synthesis text."""
        insights = []
        
        # Look for sections that might contain insights
        # Look for numbered lists
        numbered_items = re.findall(r'\d+\.\s+(.*?)(?=\d+\.|$)', synthesis, re.DOTALL)
        if numbered_items:
            insights.extend([item.strip() for item in numbered_items if len(item.strip()) > 20])
        
        # Look for bullet points
        bullet_items = re.findall(r'[•\-\*]\s+(.*?)(?=[•\-\*]|$)', synthesis, re.DOTALL)
        if bullet_items:
            insights.extend([item.strip() for item in bullet_items if len(item.strip()) > 20])
        
        # Look for sections with insight keywords
        insight_sections = re.findall(r'(?:洞察|见解|发现|结论|关键点|重要发现)[：:]\s*(.*?)(?=\n\n|$)', synthesis, re.DOTALL)
        if insight_sections:
            for section in insight_sections:
                # Split by newlines or periods
                items = re.split(r'(?:\n|。)', section)
                insights.extend([item.strip() for item in items if len(item.strip()) > 20])
        
        # If no structured insights found, create some from the text
        if not insights:
            # Split by periods and take sentences that seem insightful
            sentences = re.split(r'。', synthesis)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and any(keyword in sentence for keyword in ["关键", "重要", "显著", "值得注意", "综合", "分析表明", "可以看出"]):
                    insights.append(sentence)
        
        # Limit to reasonable number and length
        insights = [insight for insight in insights if len(insight) <= 200]
        return insights[:5]  # Return at most 5 insights
    
    def _create_expert_contributions(self, viewpoints: list) -> dict[str, list[str]]:
        """Create expert contribution mapping."""
        expert_contributions = {}
        
        for viewpoint in viewpoints:
            expert_name = viewpoint.expert_name
            perspective = viewpoint.metadata.get("perspective", "Unknown")
            
            if expert_name not in expert_contributions:
                expert_contributions[expert_name] = []
            
            # Extract a brief summary of this expert's contribution
            contribution = self._summarize_contribution(viewpoint, perspective)
            expert_contributions[expert_name].append(contribution)
        
        return expert_contributions
    
    def _summarize_contribution(self, viewpoint, perspective: str) -> str:
        """Summarize an expert's contribution."""
        # Extract first sentence or up to 100 characters
        if viewpoint.viewpoint:
            summary = viewpoint.viewpoint.split("。")[0]
            if len(summary) > 100:
                summary = summary[:97] + "..."
            return f"从{perspective}角度提供了观点：{summary}"
        else:
            return f"提供了{perspective}角度的分析"
    
    def _calculate_synthesis_confidence(self, viewpoints: list, quality_assessment: SynthesisQuality) -> float:
        """Calculate overall confidence in the synthesis."""
        if not viewpoints:
            return 0.0
        
        # Calculate weighted average of expert confidences
        total_confidence = 0.0
        total_weight = 0.0
        
        for viewpoint in viewpoints:
            # Higher priority sub-problems get more weight
            weight = 1.0
            if "priority" in viewpoint.metadata:
                priority = viewpoint.metadata["priority"]
                if isinstance(priority, (int, float)):
                    # Convert priority (1-5, 1 is highest) to weight
                    weight = 6 - priority  # So priority 1 gets weight 5, etc.
            
            total_confidence += viewpoint.confidence * weight
            total_weight += weight
        
        # Calculate weighted average
        if total_weight > 0:
            avg_confidence = total_confidence / total_weight
        else:
            avg_confidence = sum(vp.confidence for vp in viewpoints) / len(viewpoints)
        
        # Adjust based on synthesis quality
        quality_factor = quality_assessment.overall_score
        final_confidence = (avg_confidence * 0.7 + quality_factor * 0.3)
        
        # Apply minimum threshold
        if final_confidence < self.min_confidence_threshold:
            return self.min_confidence_threshold
        
        return final_confidence
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return input schema for the enhanced synthesis node."""
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Original topic"
                },
                "viewpoint_collection": {
                    "type": "object",
                    "description": "Analyzed viewpoint collection to synthesize"
                }
            },
            "required": ["viewpoint_collection"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return output schema for the enhanced synthesis node."""
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Original topic"
                },
                "synthesis": {
                    "type": "string",
                    "description": "Synthesized analysis"
                },
                "key_insights": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key insights from the synthesis"
                },
                "expert_contributions": {
                    "type": "object",
                    "description": "Mapping of expert names to their contributions"
                },
                "confidence": {
                    "type": "number",
                    "description": "Overall confidence in the synthesis"
                },
                "quality_assessment": {
                    "type": "object",
                    "description": "Quality assessment of the synthesis"
                },
                "needs_refinement": {
                    "type": "boolean",
                    "description": "Whether the synthesis needs refinement"
                },
                "success": {
                    "type": "boolean",
                    "description": "Whether synthesis was successful"
                }
            },
            "required": ["topic", "synthesis", "key_insights", "confidence", "success"]
        }