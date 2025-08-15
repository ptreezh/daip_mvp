"""@Time    : 2025-08-04 10:30:00
@Author  : DAIP-LIVE Team
@File    : quality_evaluator.py
@Description:
    Enhanced Quality Evaluator for intelligent synthesis assessment.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ...core_services.consensus_quality_evaluator import ConsensusQualityEvaluator

logger = logging.getLogger(__name__)


@dataclass
class QualityDimension:
    """Quality dimension with detailed metrics."""
    name: str
    score: float
    weight: float
    confidence: float
    details: dict[str, Any]
    improvement_suggestions: list[str]


class EnhancedQualityEvaluator:
    """增强质量评估器 - Advanced quality evaluation for intelligent synthesis.
    
    Extends the basic consensus quality evaluator with sophisticated metrics
    for cognitive quality, insight generation, and synthesis effectiveness.
    """
    
    def __init__(self, config: dict[str, Any] = None):
        """Initialize the Enhanced Quality Evaluator.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or {}
        
        # Base quality evaluator
        self.base_evaluator = ConsensusQualityEvaluator()
        
        # Enhanced quality dimensions
        self.enhanced_dimensions = {
            "cognitive_depth": {"weight": 0.20, "threshold": 0.7},
            "insight_quality": {"weight": 0.18, "threshold": 0.6},
            "synthesis_coherence": {"weight": 0.15, "threshold": 0.7},
            "perspective_integration": {"weight": 0.12, "threshold": 0.6},
            "conflict_resolution": {"weight": 0.10, "threshold": 0.5},
            "evidence_utilization": {"weight": 0.10, "threshold": 0.6},
            "practical_value": {"weight": 0.08, "threshold": 0.5},
            "innovation_level": {"weight": 0.07, "threshold": 0.4}
        }
        
        # Evaluation history
        self.evaluation_history = []
        
        # Quality benchmarks
        self.quality_benchmarks = {
            "excellent": {"min_score": 0.85, "description": "卓越水平，具有深度洞察"},
            "good": {"min_score": 0.70, "description": "良好水平，达到预期标准"},
            "fair": {"min_score": 0.55, "description": "一般水平，需要改进"},
            "poor": {"min_score": 0.40, "description": "较差水平，需要大幅改进"},
            "very_poor": {"min_score": 0.0, "description": "很差水平，需要重新处理"}
        }
        
    async def evaluate_enhanced_quality(
        self,
        synthesis_result: dict[str, Any],
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Perform enhanced quality evaluation.
        
        Args:
            synthesis_result: The synthesis result to evaluate
            viewpoints: Original expert viewpoints
            cognitive_analysis: Cognitive pattern analysis
            conflicts: Identified conflicts
            
        Returns:
            Enhanced quality evaluation results
        """
        try:
            logger.info("Starting enhanced quality evaluation")
            
            # Extract synthesis content
            synthesis_content = synthesis_result.get("synthesis", "")
            
            # Evaluate each quality dimension
            dimension_results = {}
            for dimension_name, dimension_config in self.enhanced_dimensions.items():
                dimension_result = await self._evaluate_dimension(
                    dimension_name,
                    synthesis_content,
                    viewpoints,
                    cognitive_analysis,
                    conflicts,
                    dimension_config
                )
                dimension_results[dimension_name] = dimension_result
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(dimension_results)
            
            # Generate quality assessment
            quality_assessment = self._generate_quality_assessment(
                overall_score, dimension_results
            )
            
            # Generate improvement recommendations
            recommendations = await self._generate_enhanced_recommendations(
                dimension_results, overall_score
            )
            
            # Create evaluation record
            evaluation_record = {
                "evaluation_id": f"enhanced_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "overall_score": overall_score,
                "quality_grade": quality_assessment["grade"],
                "dimensions": dimension_results,
                "recommendations": recommendations,
                "synthesis_metadata": {
                    "length": len(synthesis_content),
                    "viewpoint_count": len(viewpoints),
                    "conflict_count": len(conflicts or [])
                }
            }
            
            # Store in history
            self.evaluation_history.append(evaluation_record)
            
            return evaluation_record
            
        except Exception as e:
            logger.error(f"Enhanced quality evaluation failed: {e}")
            return {
                "evaluation_id": f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_score": 0.0,
                "quality_grade": "error"
            }
    
    async def _evaluate_dimension(
        self,
        dimension_name: str,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None,
        dimension_config: dict[str, Any] = None
    ) -> QualityDimension:
        """Evaluate a specific quality dimension."""
        if dimension_config is None:
            dimension_config = self.enhanced_dimensions.get(dimension_name, {"weight": 0.1, "threshold": 0.5})
        
        # Select evaluation method based on dimension
        evaluation_methods = {
            "cognitive_depth": self._evaluate_cognitive_depth,
            "insight_quality": self._evaluate_insight_quality,
            "synthesis_coherence": self._evaluate_synthesis_coherence,
            "perspective_integration": self._evaluate_perspective_integration,
            "conflict_resolution": self._evaluate_conflict_resolution,
            "evidence_utilization": self._evaluate_evidence_utilization,
            "practical_value": self._evaluate_practical_value,
            "innovation_level": self._evaluate_innovation_level
        }
        
        if dimension_name in evaluation_methods:
            result = await evaluation_methods[dimension_name](
                synthesis_content, viewpoints, cognitive_analysis, conflicts
            )
        else:
            result = {"score": 0.5, "confidence": 0.5, "details": {}, "suggestions": []}
        
        return QualityDimension(
            name=dimension_name,
            score=result["score"],
            weight=dimension_config["weight"],
            confidence=result["confidence"],
            details=result["details"],
            improvement_suggestions=result["suggestions"]
        )
    
    async def _evaluate_cognitive_depth(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate cognitive depth of synthesis."""
        # Depth indicators
        depth_indicators = {
            "mechanism": ["机制", "原理", "根本", "深层", "本质", "核心"],
            "analysis": ["分析", "研究", "探讨", "考察", "解释", "阐述"],
            "causality": ["因为", "所以", "由于", "因此", "导致", "影响"],
            "system": ["系统", "整体", "全局", "综合", "全面", "完整"],
            "complexity": ["复杂", "多维度", "多层次", "相互作用", "动态"]
        }
        
        # Calculate depth scores
        depth_scores = {}
        for category, indicators in depth_indicators.items():
            score = sum(1 for indicator in indicators if indicator in synthesis_content)
            depth_scores[category] = min(score / 2, 1.0)  # Normalize
        
        # Calculate overall depth score
        overall_depth = sum(depth_scores.values()) / len(depth_scores)
        
        # Confidence based on synthesis length and structure
        confidence = min(len(synthesis_content) / 1000, 1.0) * 0.7 + 0.3
        
        # Suggestions for improvement
        suggestions = []
        if overall_depth < 0.5:
            suggestions.append("增加深层机制分析")
        if depth_scores["causality"] < 0.3:
            suggestions.append("强化因果关系分析")
        if depth_scores["system"] < 0.3:
            suggestions.append("提升系统性思维")
        
        return {
            "score": overall_depth,
            "confidence": confidence,
            "details": {
                "category_scores": depth_scores,
                "strongest_area": max(depth_scores.items(), key=lambda x: x[1])[0],
                "weakest_area": min(depth_scores.items(), key=lambda x: x[1])[0]
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_insight_quality(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate insight quality and generation."""
        # Insight quality indicators
        insight_indicators = {
            "novelty": ["新", "创新", "独特", "突破", "首创", "原创"],
            "clarity": ["清晰", "明确", "准确", "具体", "详细", "精确"],
            "depth": ["深刻", "深入", "透彻", "本质", "深层", "核心"],
            "actionability": ["可行", "实用", "操作", "实施", "执行", "应用"],
            "generativity": ["启发", "激发", "引导", "促进", "推动", "带动"]
        }
        
        # Calculate insight scores
        insight_scores = {}
        for category, indicators in insight_indicators.items():
            score = sum(1 for indicator in indicators if indicator in synthesis_content)
            insight_scores[category] = min(score / 2, 1.0)
        
        # Count explicit insight statements
        insight_statements = synthesis_content.count("洞察") + synthesis_content.count("发现") + synthesis_content.count("揭示")
        insight_density = min(insight_statements / max(len(synthesis_content) / 500, 1), 1.0)
        
        # Overall insight score
        overall_insight = (sum(insight_scores.values()) / len(insight_scores) + insight_density) / 2
        
        # Confidence based on insight diversity
        confidence = min(len([s for s in insight_scores.values() if s > 0.3]) / len(insight_scores), 1.0)
        
        # Suggestions
        suggestions = []
        if overall_insight < 0.4:
            suggestions.append("增加原创性洞察")
        if insight_scores["novelty"] < 0.3:
            suggestions.append("提升观点新颖性")
        if insight_scores["actionability"] < 0.3:
            suggestions.append("增强可操作性")
        
        return {
            "score": overall_insight,
            "confidence": confidence,
            "details": {
                "quality_scores": insight_scores,
                "insight_density": insight_density,
                "explicit_insights": insight_statements
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_synthesis_coherence(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate synthesis coherence and structure."""
        # Structure indicators
        structure_indicators = {
            "logical_flow": ["首先", "其次", "然后", "最后", "总之", "综上", "因此"],
            "transitions": ["然而", "但是", "虽然", "尽管", "另外", "此外", "同时"],
            "conclusion": ["结论", "总结", "总之", "综上", "因此", "所以"],
            "introduction": ["引言", "概述", "介绍", "背景", "首先", "第一"],
            "organization": ["部分", "章节", "方面", "角度", "维度", "层面"]
        }
        
        # Calculate structure scores
        structure_scores = {}
        for category, indicators in structure_indicators.items():
            score = sum(1 for indicator in indicators if indicator in synthesis_content)
            structure_scores[category] = min(score / 2, 1.0)
        
        # Paragraph coherence (simplified)
        paragraphs = synthesis_content.split('\n\n')
        paragraph_coherence = len([p for p in paragraphs if len(p.strip()) > 50]) / max(len(paragraphs), 1)
        
        # Overall coherence score
        overall_coherence = (sum(structure_scores.values()) / len(structure_scores) + paragraph_coherence) / 2
        
        # Confidence based on structural completeness
        structural_completeness = sum(1 for score in structure_scores.values() if score > 0.3) / len(structure_scores)
        confidence = structural_completeness
        
        # Suggestions
        suggestions = []
        if overall_coherence < 0.5:
            suggestions.append("改善逻辑结构和连贯性")
        if structure_scores["logical_flow"] < 0.3:
            suggestions.append("增强逻辑流程标记")
        if paragraph_coherence < 0.6:
            suggestions.append("优化段落组织")
        
        return {
            "score": overall_coherence,
            "confidence": confidence,
            "details": {
                "structure_scores": structure_scores,
                "paragraph_coherence": paragraph_coherence,
                "structural_completeness": structural_completeness
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_perspective_integration(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate perspective integration quality."""
        if not viewpoints:
            return {"score": 0.0, "confidence": 0.0, "details": {}, "suggestions": []}
        
        # Check perspective coverage
        perspectives_mentioned = 0
        perspective_coverage = {}
        
        for viewpoint in viewpoints:
            perspective = viewpoint.get("perspective", viewpoint.get("metadata", {}).get("perspective", "unknown"))
            if perspective in synthesis_content:
                perspectives_mentioned += 1
                perspective_coverage[perspective] = True
            else:
                perspective_coverage[perspective] = False
        
        coverage_score = perspectives_mentioned / len(viewpoints)
        
        # Integration quality indicators
        integration_indicators = [
            "整合", "融合", "结合", "综合", "协调", "统一",
            "多视角", "多维度", "多方面", "多层次", "全方位"
        ]
        
        integration_score = sum(1 for indicator in integration_indicators if indicator in synthesis_content)
        integration_score = min(integration_score / 5, 1.0)
        
        # Overall integration score
        overall_integration = (coverage_score + integration_score) / 2
        
        # Confidence based on coverage completeness
        confidence = coverage_score
        
        # Suggestions
        suggestions = []
        if coverage_score < 0.7:
            suggestions.append("确保覆盖所有专家视角")
        if integration_score < 0.4:
            suggestions.append("增强视角整合的深度")
        
        return {
            "score": overall_integration,
            "confidence": confidence,
            "details": {
                "perspective_coverage": perspective_coverage,
                "coverage_score": coverage_score,
                "integration_score": integration_score,
                "missing_perspectives": [p for p, covered in perspective_coverage.items() if not covered]
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_conflict_resolution(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate conflict resolution quality."""
        if not conflicts:
            return {"score": 1.0, "confidence": 1.0, "details": {"no_conflicts": True}, "suggestions": []}
        
        # Conflict resolution indicators
        resolution_indicators = [
            "调和", "协调", "平衡", "折中", "妥协", "统一",
            "解决", "处理", "应对", "化解", "消除", "克服",
            "尽管", "但是", "然而", "虽然", "不过", "另一方面"
        ]
        
        resolution_score = sum(1 for indicator in resolution_indicators if indicator in synthesis_content)
        resolution_score = min(resolution_score / 5, 1.0)
        
        # Conflict acknowledgment
        conflict_keywords = ["冲突", "矛盾", "分歧", "差异", "争议", "不同意见"]
        conflict_acknowledgment = sum(1 for keyword in conflict_keywords if keyword in synthesis_content)
        conflict_acknowledgment = min(conflict_acknowledgment / 3, 1.0)
        
        # Overall resolution score
        overall_resolution = (resolution_score + conflict_acknowledgment) / 2
        
        # Confidence based on conflict complexity
        confidence = min(len(conflicts) / 5, 1.0)
        
        # Suggestions
        suggestions = []
        if overall_resolution < 0.5:
            suggestions.append("加强冲突分析和解决方案")
        if conflict_acknowledgment < 0.3:
            suggestions.append("明确承认和讨论冲突点")
        
        return {
            "score": overall_resolution,
            "confidence": confidence,
            "details": {
                "resolution_score": resolution_score,
                "conflict_acknowledgment": conflict_acknowledgment,
                "conflict_count": len(conflicts)
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_evidence_utilization(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate evidence utilization in synthesis."""
        # Evidence indicators
        evidence_indicators = [
            "证据", "数据", "事实", "研究", "分析", "统计",
            "表明", "显示", "证明", "证实", "说明", "反映",
            "根据", "基于", "按照", "依据", "参考", "引用"
        ]
        
        evidence_score = sum(1 for indicator in evidence_indicators if indicator in synthesis_content)
        evidence_score = min(evidence_score / 8, 1.0)
        
        # Source diversity (simplified)
        source_indicators = ["研究", "调查", "数据", "统计", "实验", "分析"]
        source_diversity = sum(1 for indicator in source_indicators if indicator in synthesis_content)
        source_diversity = min(source_diversity / 3, 1.0)
        
        # Overall evidence score
        overall_evidence = (evidence_score + source_diversity) / 2
        
        # Confidence based on evidence density
        confidence = min(evidence_score, 1.0)
        
        # Suggestions
        suggestions = []
        if overall_evidence < 0.4:
            suggestions.append("增加证据支持和数据引用")
        if source_diversity < 0.3:
            suggestions.append("丰富证据来源的多样性")
        
        return {
            "score": overall_evidence,
            "confidence": confidence,
            "details": {
                "evidence_score": evidence_score,
                "source_diversity": source_diversity,
                "evidence_density": evidence_score
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_practical_value(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate practical value and applicability."""
        # Practical value indicators
        practical_indicators = [
            "应用", "实践", "实施", "执行", "操作", "运用",
            "建议", "方案", "策略", "方法", "措施", "步骤",
            "可行", "有效", "实用", "有用", "帮助", "促进"
        ]
        
        practical_score = sum(1 for indicator in practical_indicators if indicator in synthesis_content)
        practical_score = min(practical_score / 6, 1.0)
        
        # Action orientation
        action_indicators = ["应该", "需要", "必须", "可以", "能够", "建议"]
        action_orientation = sum(1 for indicator in action_indicators if indicator in synthesis_content)
        action_orientation = min(action_orientation / 4, 1.0)
        
        # Overall practical value
        overall_practical = (practical_score + action_orientation) / 2
        
        # Confidence based on practical content density
        confidence = min(practical_score, 1.0)
        
        # Suggestions
        suggestions = []
        if overall_practical < 0.4:
            suggestions.append("增强实用价值和可操作性")
        if action_orientation < 0.3:
            suggestions.append("增加具体行动建议")
        
        return {
            "score": overall_practical,
            "confidence": confidence,
            "details": {
                "practical_score": practical_score,
                "action_orientation": action_orientation,
                "actionability": overall_practical
            },
            "suggestions": suggestions
        }
    
    async def _evaluate_innovation_level(
        self,
        synthesis_content: str,
        viewpoints: list[dict[str, Any]],
        cognitive_analysis: dict[str, Any] = None,
        conflicts: list[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Evaluate innovation level and creativity."""
        # Innovation indicators
        innovation_indicators = [
            "创新", "突破", "首创", "原创", "新", "独特",
            "前所未有", "开创性", "革命性", "颠覆性", "创造性",
            "发现", "揭示", "洞察", "启发", "灵感", "创意"
        ]
        
        innovation_score = sum(1 for indicator in innovation_indicators if indicator in synthesis_content)
        innovation_score = min(innovation_score / 4, 1.0)
        
        # Novelty of approach (simplified)
        novelty_indicators = ["新方法", "新思路", "新角度", "新框架", "新模型", "新理论"]
        novelty_score = sum(1 for indicator in novelty_indicators if indicator in synthesis_content)
        novelty_score = min(novelty_score / 2, 1.0)
        
        # Overall innovation score
        overall_innovation = (innovation_score + novelty_score) / 2
        
        # Confidence based on innovation consistency
        confidence = min(innovation_score, 1.0)
        
        # Suggestions
        suggestions = []
        if overall_innovation < 0.3:
            suggestions.append("增加创新性和独特见解")
        if novelty_score < 0.2:
            suggestions.append("提供新的思路和方法")
        
        return {
            "score": overall_innovation,
            "confidence": confidence,
            "details": {
                "innovation_score": innovation_score,
                "novelty_score": novelty_score,
                "creativity_level": overall_innovation
            },
            "suggestions": suggestions
        }
    
    def _calculate_overall_score(self, dimension_results: dict[str, QualityDimension]) -> float:
        """Calculate overall quality score."""
        weighted_sum = sum(
            dimension.score * dimension.weight
            for dimension in dimension_results.values()
        )
        
        total_weight = sum(dimension.weight for dimension in dimension_results.values())
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _generate_quality_assessment(self, overall_score: float, dimension_results: dict[str, QualityDimension]) -> dict[str, Any]:
        """Generate quality assessment."""
        # Determine quality grade
        grade = "very_poor"
        for grade_name, benchmark in self.quality_benchmarks.items():
            if overall_score >= benchmark["min_score"]:
                grade = grade_name
                break
        
        # Find strongest and weakest dimensions
        dimensions_sorted = sorted(dimension_results.items(), key=lambda x: x[1].score, reverse=True)
        strongest_dimension = dimensions_sorted[0] if dimensions_sorted else None
        weakest_dimension = dimensions_sorted[-1] if dimensions_sorted else None
        
        return {
            "grade": grade,
            "description": self.quality_benchmarks[grade]["description"],
            "overall_score": overall_score,
            "strongest_dimension": strongest_dimension[0] if strongest_dimension else None,
            "weakest_dimension": weakest_dimension[0] if weakest_dimension else None,
            "score_distribution": {
                name: dim.score for name, dim in dimension_results.items()
            }
        }
    
    async def _generate_enhanced_recommendations(
        self,
        dimension_results: dict[str, QualityDimension],
        overall_score: float
    ) -> list[str]:
        """Generate enhanced improvement recommendations."""
        recommendations = []
        
        # Overall quality recommendations
        if overall_score < 0.4:
            recommendations.append("整体质量较低，建议重新进行综合分析")
        elif overall_score < 0.6:
            recommendations.append("整体质量需要提升，重点关注关键维度")
        elif overall_score < 0.8:
            recommendations.append("整体质量良好，可以进一步提升细节")
        
        # Dimension-specific recommendations
        weak_dimensions = [
            (name, dim) for name, dim in dimension_results.items()
            if dim.score < dim.details.get("threshold", 0.5)
        ]
        
        # Sort by importance (weight * deficit)
        weak_dimensions.sort(key=lambda x: x[1].weight * (0.5 - x[1].score), reverse=True)
        
        for dimension_name, dimension in weak_dimensions[:3]:  # Top 3 recommendations
            recommendations.extend(dimension.improvement_suggestions)
        
        # Remove duplicates and limit
        unique_recommendations = list(set(recommendations))
        return unique_recommendations[:5]
    
    def get_evaluation_history(self) -> list[dict[str, Any]]:
        """Get evaluation history."""
        return self.evaluation_history.copy()
    
    def get_quality_trends(self) -> dict[str, Any]:
        """Get quality trends over time."""
        if len(self.evaluation_history) < 2:
            return {"message": "需要至少两次评估才能分析趋势"}
        
        # Extract overall scores
        scores = [eval_record["overall_score"] for eval_record in self.evaluation_history]
        
        # Calculate trend
        trend = "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable"
        
        # Calculate dimension trends
        dimension_trends = {}
        if self.evaluation_history:
            latest_dimensions = self.evaluation_history[-1].get("dimensions", {})
            for dimension_name in latest_dimensions:
                dimension_scores = [
                    eval_record["dimensions"][dimension_name].score
                    for eval_record in self.evaluation_history
                    if dimension_name in eval_record.get("dimensions", {})
                ]
                if len(dimension_scores) >= 2:
                    dimension_trend = "improving" if dimension_scores[-1] > dimension_scores[0] else "declining"
                    dimension_trends[dimension_name] = {
                        "trend": dimension_trend,
                        "current_score": dimension_scores[-1],
                        "change": dimension_scores[-1] - dimension_scores[0]
                    }
        
        return {
            "overall_trend": trend,
            "overall_change": scores[-1] - scores[0],
            "current_score": scores[-1],
            "dimension_trends": dimension_trends,
            "evaluation_count": len(self.evaluation_history)
        }
    
    def get_quality_benchmarks(self) -> dict[str, Any]:
        """Get quality benchmarks."""
        return self.quality_benchmarks.copy()