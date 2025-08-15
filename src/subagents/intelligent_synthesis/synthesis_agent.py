"""@Time    : 2025-08-04 10:00:00
@Author  : DAIP-LIVE Team
@File    : synthesis_agent.py
@Description:
    Intelligent Synthesis Agent for advanced multi-perspective analysis.
"""

import logging
import statistics
from datetime import datetime
from typing import Any

from ...core_services.consensus_quality_evaluator import ConsensusQualityEvaluator
from ...kernel.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class IntelligentSynthesisAgent:
    """智能综合代理 - Advanced multi-perspective synthesis with cognitive intelligence.
    
    Implements intelligent synthesis algorithms that go beyond simple text combination
    to create truly insightful, cognitively-aware consensus with conflict resolution.
    """
    
    def __init__(self, llm_interface: LLMInterface, config: dict[str, Any] = None):
        """Initialize the Intelligent Synthesis Agent.
        
        Args:
            llm_interface: LLM interface for synthesis operations
            config: Configuration parameters
        """
        self.llm_interface = llm_interface
        self.config = config or {}
        
        # Synthesis strategies
        self.synthesis_strategies = {
            "dialectical": self._dialectical_synthesis,
            "integrative": self._integrative_synthesis,
            "hierarchical": self._hierarchical_synthesis,
            "adaptive": self._adaptive_synthesis
        }
        
        # Cognitive enhancement parameters
        self.cognitive_params = {
            "depth_threshold": self.config.get("depth_threshold", 0.7),
            "breadth_threshold": self.config.get("breadth_threshold", 0.8),
            "insight_threshold": self.config.get("insight_threshold", 0.6),
            "coherence_threshold": self.config.get("coherence_threshold", 0.7),
            "conflict_resolution_weight": self.config.get("conflict_resolution_weight", 0.3),
            "consensus_enhancement_weight": self.config.get("consensus_enhancement_weight", 0.4)
        }
        
        # Quality evaluator
        self.quality_evaluator = ConsensusQualityEvaluator()
        
        # Synthesis history for learning
        self.synthesis_history = []
        
    async def synthesize_intelligently(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None,
        synthesis_strategy: str = "adaptive"
    ) -> dict[str, Any]:
        """Perform intelligent multi-perspective synthesis.
        
        Args:
            topic: The topic being analyzed
            viewpoints: List of expert viewpoints
            conflicts: List of identified conflicts
            consensus_areas: List of consensus areas
            synthesis_strategy: Strategy to use for synthesis
            
        Returns:
            Intelligent synthesis result with quality assessment
        """
        try:
            logger.info(f"Starting intelligent synthesis for topic: {topic}")
            
            # Pre-process viewpoints
            processed_viewpoints = await self._preprocess_viewpoints(viewpoints)
            
            # Analyze cognitive patterns
            cognitive_analysis = await self._analyze_cognitive_patterns(processed_viewpoints)
            
            # Select optimal synthesis strategy
            if synthesis_strategy == "adaptive":
                synthesis_strategy = await self._select_optimal_strategy(
                    processed_viewpoints, cognitive_analysis
                )
            
            # Perform synthesis
            synthesis_result = await self._perform_synthesis(
                topic, processed_viewpoints, conflicts, consensus_areas, synthesis_strategy
            )
            
            # Enhance synthesis with cognitive insights
            enhanced_synthesis = await self._enhance_synthesis(
                synthesis_result, cognitive_analysis
            )
            
            # Quality assessment
            quality_assessment = await self._assess_synthesis_quality(
                enhanced_synthesis, processed_viewpoints
            )
            
            # Generate meta-insights
            meta_insights = await self._generate_meta_insights(
                enhanced_synthesis, cognitive_analysis, quality_assessment
            )
            
            # Store in history
            synthesis_record = {
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "strategy": synthesis_strategy,
                "viewpoint_count": len(viewpoints),
                "quality_score": quality_assessment.get("overall_quality", 0.0),
                "cognitive_analysis": cognitive_analysis,
                "synthesis_result": enhanced_synthesis
            }
            self.synthesis_history.append(synthesis_record)
            
            return {
                "success": True,
                "synthesis": enhanced_synthesis["synthesis"],
                "cognitive_analysis": cognitive_analysis,
                "quality_assessment": quality_assessment,
                "meta_insights": meta_insights,
                "synthesis_strategy": synthesis_strategy,
                "confidence": enhanced_synthesis.get("confidence", 0.0),
                "processing_metadata": {
                    "viewpoints_processed": len(processed_viewpoints),
                    "cognitive_patterns_identified": len(cognitive_analysis.get("patterns", [])),
                    "synthesis_iterations": enhanced_synthesis.get("iterations", 1),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Intelligent synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "synthesis": "",
                "quality_assessment": {"overall_quality": 0.0},
                "confidence": 0.0
            }
    
    async def _preprocess_viewpoints(self, viewpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Pre-process viewpoints for cognitive analysis."""
        processed = []
        
        for viewpoint in viewpoints:
            # Extract cognitive features
            cognitive_features = await self._extract_cognitive_features(viewpoint)
            
            # Calculate viewpoint quality
            quality_score = await self._calculate_viewpoint_quality(viewpoint, cognitive_features)
            
            processed_viewpoint = {
                **viewpoint,
                "cognitive_features": cognitive_features,
                "quality_score": quality_score,
                "processed_at": datetime.now().isoformat()
            }
            processed.append(processed_viewpoint)
        
        return processed
    
    async def _extract_cognitive_features(self, viewpoint: dict[str, Any]) -> dict[str, Any]:
        """Extract cognitive features from viewpoint."""
        content = viewpoint.get("viewpoint", viewpoint.get("content", ""))
        
        features = {
            "analytical_depth": self._calculate_analytical_depth(content),
            "reasoning_complexity": self._calculate_reasoning_complexity(content),
            "evidence_strength": self._calculate_evidence_strength(viewpoint),
            "perspective_novelty": self._calculate_perspective_novelty(content),
            "logical_coherence": self._calculate_logical_coherence(content),
            "insight_generation": self._calculate_insight_generation(content)
        }
        
        return features
    
    def _calculate_analytical_depth(self, content: str) -> float:
        """Calculate analytical depth of content."""
        depth_indicators = [
            "机制", "原理", "根本", "深层", "本质", "核心", "关键", "重要",
            "分析", "研究", "探讨", "考察", "解释", "阐述", "论证"
        ]
        
        indicator_count = sum(1 for indicator in depth_indicators if indicator in content)
        content_length = len(content)
        
        # Normalize by content length
        depth_score = min(indicator_count / max(content_length / 100, 1), 1.0)
        return depth_score
    
    def _calculate_reasoning_complexity(self, content: str) -> float:
        """Calculate reasoning complexity."""
        complexity_indicators = [
            "因为", "所以", "由于", "因此", "然而", "但是", "虽然", "尽管",
            "首先", "其次", "然后", "最后", "总之", "综上", "综上所述"
        ]
        
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in content)
        complexity_score = min(indicator_count / 10, 1.0)  # Normalize to 0-1
        return complexity_score
    
    def _calculate_evidence_strength(self, viewpoint: dict[str, Any]) -> float:
        """Calculate evidence strength."""
        evidence = viewpoint.get("supporting_evidence", [])
        
        if not evidence:
            return 0.0
        
        # Score based on evidence count and quality
        evidence_count = len(evidence)
        quality_indicators = ["数据", "统计", "研究", "实验", "调查", "分析", "证明"]
        
        quality_score = sum(1 for item in evidence 
                          for indicator in quality_indicators 
                          if indicator in item) / max(evidence_count, 1)
        
        return min((evidence_count * 0.3 + quality_score * 0.7), 1.0)
    
    def _calculate_perspective_novelty(self, content: str) -> float:
        """Calculate perspective novelty."""
        # This is a simplified version - in practice would use NLP techniques
        novelty_indicators = ["新", "创新", "独特", "不同", "另类", "突破", "革命性"]
        
        novelty_score = sum(1 for indicator in novelty_indicators if indicator in content)
        return min(novelty_score / 3, 1.0)
    
    def _calculate_logical_coherence(self, content: str) -> float:
        """Calculate logical coherence."""
        coherence_indicators = [
            "逻辑", "一致", "连贯", "系统", "条理", "清晰", "明确", "结构"
        ]
        
        coherence_score = sum(1 for indicator in coherence_indicators if indicator in content)
        return min(coherence_score / 4, 1.0)
    
    def _calculate_insight_generation(self, content: str) -> float:
        """Calculate insight generation capability."""
        insight_indicators = [
            "洞察", "发现", "揭示", "表明", "说明", "证明", "显示", "反映",
            "关键", "重要", "显著", "值得注意"
        ]
        
        insight_score = sum(1 for indicator in insight_indicators if indicator in content)
        return min(insight_score / 5, 1.0)
    
    async def _calculate_viewpoint_quality(self, viewpoint: dict[str, Any], cognitive_features: dict[str, Any]) -> float:
        """Calculate overall viewpoint quality."""
        # Weight different features
        weights = {
            "analytical_depth": 0.25,
            "reasoning_complexity": 0.20,
            "evidence_strength": 0.25,
            "perspective_novelty": 0.15,
            "logical_coherence": 0.10,
            "insight_generation": 0.05
        }
        
        weighted_score = sum(
            cognitive_features.get(feature, 0.0) * weight
            for feature, weight in weights.items()
        )
        
        return min(weighted_score, 1.0)
    
    async def _analyze_cognitive_patterns(self, viewpoints: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze cognitive patterns across viewpoints."""
        if not viewpoints:
            return {"patterns": [], "diversity_score": 0.0, "convergence_score": 0.0}
        
        # Extract features from all viewpoints
        all_features = [vp["cognitive_features"] for vp in viewpoints]
        
        # Calculate diversity metrics
        diversity_metrics = self._calculate_cognitive_diversity(all_features)
        
        # Identify convergence patterns
        convergence_patterns = self._identify_convergence_patterns(viewpoints)
        
        # Detect cognitive biases
        bias_patterns = self._detect_cognitive_biases(viewpoints)
        
        return {
            "patterns": {
                "diversity": diversity_metrics,
                "convergence": convergence_patterns,
                "biases": bias_patterns
            },
            "diversity_score": diversity_metrics.get("overall_diversity", 0.0),
            "convergence_score": convergence_patterns.get("convergence_strength", 0.0),
            "bias_risk_score": bias_patterns.get("overall_bias_risk", 0.0)
        }
    
    def _calculate_cognitive_diversity(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate cognitive diversity metrics."""
        if not features:
            return {"overall_diversity": 0.0}
        
        # Calculate variance for each cognitive feature
        feature_vars = {}
        for feature_name in features[0].keys():
            values = [f.get(feature_name, 0.0) for f in features]
            if len(values) > 1:
                feature_vars[feature_name] = statistics.variance(values)
            else:
                feature_vars[feature_name] = 0.0
        
        # Calculate overall diversity (higher variance = more diversity)
        overall_diversity = sum(feature_vars.values()) / len(feature_vars)
        overall_diversity = min(overall_diversity, 1.0)  # Normalize to 0-1
        
        return {
            "overall_diversity": overall_diversity,
            "feature_variances": feature_vars,
            "most_diverse_features": sorted(
                feature_vars.items(), key=lambda x: x[1], reverse=True
            )[:3]
        }
    
    def _identify_convergence_patterns(self, viewpoints: list[dict[str, Any]]) -> dict[str, Any]:
        """Identify convergence patterns in viewpoints."""
        convergence_areas = []
        convergence_strength = 0.0
        
        # Simple text-based convergence detection
        # In practice, would use more sophisticated NLP techniques
        all_texts = [vp.get("viewpoint", vp.get("content", "")) for vp in viewpoints]
        
        # Look for common keywords or phrases
        common_keywords = self._find_common_keywords(all_texts)
        
        # Calculate convergence strength based on common elements
        if common_keywords:
            convergence_strength = min(len(common_keywords) / len(all_texts), 1.0)
            convergence_areas = [f"Common focus on: {', '.join(common_keywords[:5])}"]
        
        return {
            "convergence_strength": convergence_strength,
            "convergence_areas": convergence_areas,
            "common_keywords": common_keywords
        }
    
    def _find_common_keywords(self, texts: list[str]) -> list[str]:
        """Find common keywords across texts."""
        if not texts:
            return []
        
        # Simple keyword extraction
        all_words = []
        for text in texts:
            words = text.split()
            all_words.extend([word.strip(".,!?;:()[]{}\"'") for word in words])
        
        # Count word frequencies
        word_counts = {}
        for word in all_words:
            if len(word) > 2:  # Ignore very short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find words that appear in multiple texts
        common_words = [word for word, count in word_counts.items() if count >= len(texts) * 0.5]
        
        return common_words[:10]  # Return top 10 common words
    
    def _detect_cognitive_biases(self, viewpoints: list[dict[str, Any]]) -> dict[str, Any]:
        """Detect potential cognitive biases."""
        bias_patterns = {
            "confirmation_bias": 0.0,
            "groupthink": 0.0,
            "authority_bias": 0.0,
            "availability_bias": 0.0
        }
        
        # Simple bias detection based on content analysis
        all_texts = [vp.get("viewpoint", vp.get("content", "")) for vp in viewpoints]
        
        # Confirmation bias - looking for selective evidence
        confirmation_indicators = ["证明", "证实", "确实", "显然", "毫无疑问"]
        confirmation_score = sum(1 for text in all_texts 
                               for indicator in confirmation_indicators 
                               if indicator in text) / len(all_texts)
        bias_patterns["confirmation_bias"] = min(confirmation_score / 3, 1.0)
        
        # Groupthink - lack of dissent
        dissent_indicators = ["但是", "然而", "不同意", "反对", "质疑"]
        dissent_score = sum(1 for text in all_texts 
                          for indicator in dissent_indicators 
                          if indicator in text) / len(all_texts)
        bias_patterns["groupthink"] = max(0.0, 1.0 - dissent_score)
        
        # Calculate overall bias risk
        overall_bias = sum(bias_patterns.values()) / len(bias_patterns)
        
        return {
            "bias_patterns": bias_patterns,
            "overall_bias_risk": overall_bias,
            "recommendations": self._generate_bias_recommendations(bias_patterns)
        }
    
    def _generate_bias_recommendations(self, bias_patterns: dict[str, Any]) -> list[str]:
        """Generate recommendations for addressing cognitive biases."""
        recommendations = []
        
        if bias_patterns.get("confirmation_bias", 0.0) > 0.6:
            recommendations.append("考虑引入更多反面证据和替代观点")
        
        if bias_patterns.get("groupthink", 0.0) > 0.7:
            recommendations.append("鼓励更多批判性思考和不同意见")
        
        if bias_patterns.get("authority_bias", 0.0) > 0.5:
            recommendations.append("减少对权威观点的过度依赖")
        
        if bias_patterns.get("availability_bias", 0.0) > 0.5:
            recommendations.append("考虑更全面的信息来源")
        
        return recommendations
    
    async def _select_optimal_strategy(self, viewpoints: list[dict[str, Any]], cognitive_analysis: dict[str, Any]) -> str:
        """Select optimal synthesis strategy based on analysis."""
        diversity_score = cognitive_analysis.get("diversity_score", 0.0)
        convergence_score = cognitive_analysis.get("convergence_score", 0.0)
        bias_risk = cognitive_analysis.get("bias_risk_score", 0.0)
        
        # Strategy selection logic
        if diversity_score > 0.7 and convergence_score < 0.3:
            return "integrative"  # High diversity needs integration
        elif convergence_score > 0.7:
            return "hierarchical"  # High convergence needs structured synthesis
        elif bias_risk > 0.6:
            return "dialectical"  # High bias needs critical analysis
        else:
            return "adaptive"  # Default to adaptive
    
    async def _perform_synthesis(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None,
        strategy: str = "adaptive"
    ) -> dict[str, Any]:
        """Perform synthesis using selected strategy."""
        if strategy in self.synthesis_strategies:
            return await self.synthesis_strategies[strategy](
                topic, viewpoints, conflicts, consensus_areas
            )
        else:
            # Default to adaptive synthesis
            return await self._adaptive_synthesis(topic, viewpoints, conflicts, consensus_areas)
    
    async def _adaptive_synthesis(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None
    ) -> dict[str, Any]:
        """Adaptive synthesis that combines multiple strategies."""
        # Prepare synthesis input
        synthesis_input = self._prepare_synthesis_input(topic, viewpoints, conflicts, consensus_areas)
        
        # Create synthesis prompt
        synthesis_prompt = self._create_adaptive_synthesis_prompt(synthesis_input)
        
        # Generate synthesis
        response = await self.llm_interface.generate(
            messages=[{"role": "system", "content": synthesis_prompt}],
            participant_id="intelligent_synthesis_agent"
        )
        
        synthesis_content = response.get("content", "")
        
        return {
            "synthesis": synthesis_content,
            "strategy": "adaptive",
            "iterations": 1,
            "confidence": self._calculate_synthesis_confidence(viewpoints)
        }
    
    def _prepare_synthesis_input(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None
    ) -> dict[str, Any]:
        """Prepare synthesis input data."""
        return {
            "topic": topic,
            "viewpoints": viewpoints,
            "conflicts": conflicts or [],
            "consensus_areas": consensus_areas or [],
            "viewpoint_count": len(viewpoints),
            "cognitive_features": [vp.get("cognitive_features", {}) for vp in viewpoints]
        }
    
    def _create_adaptive_synthesis_prompt(self, synthesis_input: dict[str, Any]) -> str:
        """Create adaptive synthesis prompt."""
        prompt = f"""你是一个智能综合专家，需要综合多位专家的观点来产生深度洞察。

主题：{synthesis_input['topic']}

专家观点（{synthesis_input['viewpoint_count']}位）：
"""
        
        for i, viewpoint in enumerate(synthesis_input['viewpoints']):
            expert_name = viewpoint.get("expert_name", f"专家{i+1}")
            perspective = viewpoint.get("perspective", "未知视角")
            content = viewpoint.get("viewpoint", viewpoint.get("content", ""))
            quality_score = viewpoint.get("quality_score", 0.5)
            
            prompt += f"""
【{expert_name} - {perspective}视角】
质量评分：{quality_score:.2f}
观点：{content}
"""
            
            if viewpoint.get("supporting_evidence"):
                prompt += f"支持证据：{', '.join(viewpoint['supporting_evidence'])}\n"
        
        if synthesis_input['consensus_areas']:
            prompt += f"\n共识领域：{', '.join(synthesis_input['consensus_areas'])}\n"
        
        if synthesis_input['conflicts']:
            prompt += f"\n冲突点：{len(synthesis_input['conflicts'])}个主要冲突\n"
        
        prompt += """
请进行智能综合，要求：

1. **认知深度**：超越表面现象，揭示深层机制和原理
2. **多维度整合**：有机整合不同视角，创造新的理解层次
3. **冲突解决**：理性调和不同观点，找出建设性解决方案
4. **洞察生成**：提供独特的、有价值的见解和发现
5. **逻辑结构**：保持清晰的逻辑框架和论证结构
6. **实用价值**：提供具有实际指导意义的结论

综合分析应包含：
- 核心洞察和关键发现
- 多维度分析框架
- 冲突分析和解决方案
- 基于证据的结论
- 前瞻性思考和建议

请开始你的综合分析：
"""
        
        return prompt
    
    def _calculate_synthesis_confidence(self, viewpoints: list[dict[str, Any]]) -> float:
        """Calculate confidence in synthesis."""
        if not viewpoints:
            return 0.0
        
        quality_scores = [vp.get("quality_score", 0.5) for vp in viewpoints]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        return min(avg_quality, 1.0)
    
    async def _dialectical_synthesis(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None
    ) -> dict[str, Any]:
        """Dialectical synthesis focusing on conflict resolution."""
        # Placeholder for dialectical synthesis implementation
        return await self._adaptive_synthesis(topic, viewpoints, conflicts, consensus_areas)
    
    async def _integrative_synthesis(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None
    ) -> dict[str, Any]:
        """Integrative synthesis focusing on perspective integration."""
        # Placeholder for integrative synthesis implementation
        return await self._adaptive_synthesis(topic, viewpoints, conflicts, consensus_areas)
    
    async def _hierarchical_synthesis(
        self,
        topic: str,
        viewpoints: list[dict[str, Any]],
        conflicts: list[dict[str, Any]] = None,
        consensus_areas: list[str] = None
    ) -> dict[str, Any]:
        """Hierarchical synthesis focusing on structured organization."""
        # Placeholder for hierarchical synthesis implementation
        return await self._adaptive_synthesis(topic, viewpoints, conflicts, consensus_areas)
    
    async def _enhance_synthesis(
        self,
        synthesis_result: dict[str, Any],
        cognitive_analysis: dict[str, Any]
    ) -> dict[str, Any]:
        """Enhance synthesis with cognitive insights."""
        enhanced_synthesis = synthesis_result.copy()
        
        # Add cognitive insights to synthesis
        cognitive_insights = self._generate_cognitive_insights(cognitive_analysis)
        
        # Enhance synthesis content
        enhanced_content = f"""
{synthesis_result.get('synthesis', '')}

**认知分析洞察**：
{cognitive_insights}
"""
        
        enhanced_synthesis["synthesis"] = enhanced_content
        enhanced_synthesis["cognitive_enhancement"] = True
        
        return enhanced_synthesis
    
    def _generate_cognitive_insights(self, cognitive_analysis: dict[str, Any]) -> str:
        """Generate cognitive insights from analysis."""
        insights = []
        
        diversity_score = cognitive_analysis.get("diversity_score", 0.0)
        convergence_score = cognitive_analysis.get("convergence_score", 0.0)
        bias_risk = cognitive_analysis.get("bias_risk_score", 0.0)
        
        if diversity_score > 0.7:
            insights.append("• 高认知多样性：专家团队展现了丰富的思维视角和认知模式")
        
        if convergence_score > 0.6:
            insights.append("• 强收敛模式：在关键问题上存在较高的一致性")
        
        if bias_risk > 0.5:
            insights.append("• 偏见风险提醒：需注意可能的认知偏见影响")
        
        if not insights:
            insights.append("• 认知模式平衡：展现了良好的思维多样性")
        
        return "\n".join(insights)
    
    async def _assess_synthesis_quality(
        self,
        synthesis_result: dict[str, Any],
        viewpoints: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Assess synthesis quality."""
        # Prepare consensus data for quality evaluation
        consensus_data = {
            "consensus_score": synthesis_result.get("confidence", 0.0),
            "participant_positions": [
                {
                    "content": vp.get("viewpoint", vp.get("content", "")),
                    "agreement_level": vp.get("quality_score", 0.5)
                }
                for vp in viewpoints
            ]
        }
        
        # Use quality evaluator
        quality_assessment = self.quality_evaluator.evaluate_consensus_quality(
            consensus_data, viewpoints
        )
        
        return quality_assessment
    
    async def _generate_meta_insights(
        self,
        synthesis_result: dict[str, Any],
        cognitive_analysis: dict[str, Any],
        quality_assessment: dict[str, Any]
    ) -> list[str]:
        """Generate meta-insights about the synthesis process."""
        meta_insights = []
        
        # Process insights
        quality_score = quality_assessment.get("overall_quality", 0.0)
        diversity_score = cognitive_analysis.get("diversity_score", 0.0)
        
        if quality_score > 0.8:
            meta_insights.append("高质量综合：达到了优秀的认知整合水平")
        
        if diversity_score > 0.7 and quality_score > 0.7:
            meta_insights.append("有效整合：成功整合了多样化的专家观点")
        
        if len(synthesis_result.get("synthesis", "")) > 2000:
            meta_insights.append("深度分析：提供了详尽的综合分析")
        
        return meta_insights
    
    def get_synthesis_history(self) -> list[dict[str, Any]]:
        """Get synthesis history."""
        return self.synthesis_history.copy()
    
    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        if not self.synthesis_history:
            return {"message": "No synthesis history available"}
        
        # Calculate average quality scores
        quality_scores = [record.get("quality_score", 0.0) for record in self.synthesis_history]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Strategy usage statistics
        strategy_counts = {}
        for record in self.synthesis_history:
            strategy = record.get("strategy", "unknown")
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "total_syntheses": len(self.synthesis_history),
            "average_quality": avg_quality,
            "strategy_usage": strategy_counts,
            "quality_trend": "improving" if len(quality_scores) > 1 and quality_scores[-1] > quality_scores[0] else "stable"
        }