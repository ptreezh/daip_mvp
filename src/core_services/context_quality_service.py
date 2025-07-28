#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文质量评估服务

提供上下文质量评估和建议功能
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)


class ContextQualityService:
    """上下文质量评估服务"""
    
    def __init__(self):
        """初始化上下文质量评估服务"""
        self.quality_metrics = {
            "readability": ReadabilityAnalyzer(),
            "completeness": CompletenessAnalyzer(),
            "coherence": CoherenceAnalyzer(),
            "specificity": SpecificityAnalyzer(),
            "actionability": ActionabilityAnalyzer()
        }
        
        self.quality_thresholds = {
            "excellent": 0.9,
            "good": 0.8,
            "fair": 0.7,
            "poor": 0.6
        }
        
        logger.info("上下文质量评估服务初始化完成")
    
    def evaluate_context_quality(
        self,
        context: str,
        context_type: str = "general",
        evaluation_criteria: List[str] = None
    ) -> Dict[str, Any]:
        """评估上下文质量"""
        try:
            # 选择评估标准
            criteria_to_evaluate = evaluation_criteria or list(self.quality_metrics.keys())
            
            # 执行各项评估
            metric_scores = {}
            detailed_analysis = {}
            
            for criterion in criteria_to_evaluate:
                if criterion in self.quality_metrics:
                    analyzer = self.quality_metrics[criterion]
                    score, analysis = analyzer.analyze(context, context_type)
                    metric_scores[criterion] = score
                    detailed_analysis[criterion] = analysis
            
            # 计算综合质量分数
            overall_score = self._calculate_overall_score(metric_scores, context_type)
            
            # 确定质量等级
            quality_level = self._determine_quality_level(overall_score)
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(
                metric_scores, detailed_analysis, context_type
            )
            
            # 生成质量报告
            quality_report = {
                "context_type": context_type,
                "overall_score": overall_score,
                "quality_level": quality_level,
                "metric_scores": metric_scores,
                "detailed_analysis": detailed_analysis,
                "improvement_suggestions": improvement_suggestions,
                "evaluation_timestamp": datetime.now().isoformat(),
                "context_length": len(context),
                "word_count": len(context.split())
            }
            
            logger.info(f"上下文质量评估完成: 总分 {overall_score:.3f}, 等级 {quality_level}")
            return quality_report
            
        except Exception as e:
            logger.error(f"评估上下文质量失败: {e}")
            return {
                "error": str(e),
                "overall_score": 0.0,
                "quality_level": "error"
            }
    
    def get_quality_suggestions(
        self,
        context: str,
        target_quality_level: str = "good",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """获取质量改进建议"""
        try:
            # 当前质量评估
            current_quality = self.evaluate_context_quality(context)
            current_score = current_quality["overall_score"]
            target_score = self.quality_thresholds.get(target_quality_level, 0.8)
            
            # 如果已达到目标质量，返回维持建议
            if current_score >= target_score:
                return {
                    "status": "target_achieved",
                    "current_score": current_score,
                    "target_score": target_score,
                    "suggestions": ["当前质量已达到目标水平，建议保持现有水准"],
                    "priority_areas": []
                }
            
            # 识别需要改进的关键领域
            priority_areas = self._identify_priority_areas(
                current_quality["metric_scores"],
                target_score,
                focus_areas
            )
            
            # 生成针对性建议
            targeted_suggestions = self._generate_targeted_suggestions(
                context,
                priority_areas,
                current_quality["detailed_analysis"]
            )
            
            # 估算改进潜力
            improvement_potential = self._estimate_improvement_potential(
                current_quality["metric_scores"],
                targeted_suggestions
            )
            
            result = {
                "status": "improvement_needed",
                "current_score": current_score,
                "target_score": target_score,
                "improvement_gap": target_score - current_score,
                "priority_areas": priority_areas,
                "targeted_suggestions": targeted_suggestions,
                "improvement_potential": improvement_potential,
                "estimated_effort": self._estimate_improvement_effort(priority_areas)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取质量建议失败: {e}")
            return {"error": str(e)}
    
    def compare_context_versions(
        self,
        original_context: str,
        modified_context: str,
        comparison_focus: List[str] = None
    ) -> Dict[str, Any]:
        """比较上下文版本"""
        try:
            # 评估两个版本的质量
            original_quality = self.evaluate_context_quality(original_context)
            modified_quality = self.evaluate_context_quality(modified_context)
            
            # 计算改进情况
            improvements = {}
            regressions = {}
            
            for metric in original_quality["metric_scores"]:
                original_score = original_quality["metric_scores"][metric]
                modified_score = modified_quality["metric_scores"][metric]
                change = modified_score - original_score
                
                if change > 0.05:  # 显著改进
                    improvements[metric] = {
                        "original_score": original_score,
                        "modified_score": modified_score,
                        "improvement": change
                    }
                elif change < -0.05:  # 显著退步
                    regressions[metric] = {
                        "original_score": original_score,
                        "modified_score": modified_score,
                        "regression": abs(change)
                    }
            
            # 计算整体变化
            overall_change = modified_quality["overall_score"] - original_quality["overall_score"]
            
            # 生成比较摘要
            comparison_summary = self._generate_comparison_summary(
                improvements, regressions, overall_change
            )
            
            result = {
                "original_quality": original_quality,
                "modified_quality": modified_quality,
                "overall_change": overall_change,
                "improvements": improvements,
                "regressions": regressions,
                "comparison_summary": comparison_summary,
                "recommendation": self._generate_version_recommendation(
                    overall_change, improvements, regressions
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"比较上下文版本失败: {e}")
            return {"error": str(e)}
    
    def _calculate_overall_score(
        self,
        metric_scores: Dict[str, float],
        context_type: str
    ) -> float:
        """计算综合质量分数"""
        # 根据上下文类型调整权重
        weights = self._get_metric_weights(context_type)
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, score in metric_scores.items():
            weight = weights.get(metric, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_metric_weights(self, context_type: str) -> Dict[str, float]:
        """获取指标权重"""
        weight_configs = {
            "prompt": {
                "readability": 0.2,
                "completeness": 0.3,
                "coherence": 0.2,
                "specificity": 0.2,
                "actionability": 0.1
            },
            "documentation": {
                "readability": 0.3,
                "completeness": 0.3,
                "coherence": 0.2,
                "specificity": 0.1,
                "actionability": 0.1
            },
            "general": {
                "readability": 0.25,
                "completeness": 0.25,
                "coherence": 0.2,
                "specificity": 0.15,
                "actionability": 0.15
            }
        }
        
        return weight_configs.get(context_type, weight_configs["general"])
    
    def _determine_quality_level(self, overall_score: float) -> str:
        """确定质量等级"""
        for level, threshold in self.quality_thresholds.items():
            if overall_score >= threshold:
                return level
        return "poor"
    
    def _generate_improvement_suggestions(
        self,
        metric_scores: Dict[str, float],
        detailed_analysis: Dict[str, Any],
        context_type: str
    ) -> List[Dict[str, Any]]:
        """生成改进建议"""
        suggestions = []
        
        # 找出得分最低的指标
        sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1])
        
        for metric, score in sorted_metrics:
            if score < 0.7:  # 需要改进的阈值
                analysis = detailed_analysis.get(metric, {})
                suggestion = {
                    "metric": metric,
                    "current_score": score,
                    "priority": "high" if score < 0.5 else "medium",
                    "suggestions": analysis.get("suggestions", []),
                    "expected_improvement": self._estimate_metric_improvement_potential(metric, score)
                }
                suggestions.append(suggestion)
        
        return suggestions
    
    def _identify_priority_areas(
        self,
        metric_scores: Dict[str, float],
        target_score: float,
        focus_areas: List[str] = None
    ) -> List[str]:
        """识别优先改进领域"""
        priority_areas = []
        
        # 如果指定了关注领域，优先考虑
        if focus_areas:
            for area in focus_areas:
                if area in metric_scores and metric_scores[area] < target_score:
                    priority_areas.append(area)
        
        # 否则按分数排序选择最需要改进的领域
        if not priority_areas:
            sorted_metrics = sorted(metric_scores.items(), key=lambda x: x[1])
            for metric, score in sorted_metrics:
                if score < target_score and len(priority_areas) < 3:
                    priority_areas.append(metric)
        
        return priority_areas
    
    def _generate_targeted_suggestions(
        self,
        context: str,
        priority_areas: List[str],
        detailed_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成针对性建议"""
        targeted_suggestions = []
        
        for area in priority_areas:
            analysis = detailed_analysis.get(area, {})
            
            suggestion = {
                "area": area,
                "current_issues": analysis.get("issues", []),
                "specific_suggestions": analysis.get("suggestions", []),
                "examples": self._generate_improvement_examples(area, context),
                "difficulty": analysis.get("difficulty", "medium"),
                "estimated_impact": analysis.get("impact", "medium")
            }
            
            targeted_suggestions.append(suggestion)
        
        return targeted_suggestions
    
    def _generate_improvement_examples(self, area: str, context: str) -> List[str]:
        """生成改进示例"""
        examples = []
        
        if area == "readability":
            examples = [
                "将长句分解为多个短句",
                "使用更简单的词汇",
                "添加段落分隔"
            ]
        elif area == "completeness":
            examples = [
                "添加背景信息",
                "补充具体要求",
                "包含预期结果"
            ]
        elif area == "coherence":
            examples = [
                "使用逻辑连接词",
                "重新组织段落顺序",
                "确保主题一致性"
            ]
        elif area == "specificity":
            examples = [
                "添加具体数据和指标",
                "提供详细示例",
                "明确时间和地点"
            ]
        elif area == "actionability":
            examples = [
                "使用动作导向的语言",
                "提供明确的步骤",
                "设定可衡量的目标"
            ]
        
        return examples
    
    def _estimate_improvement_potential(
        self,
        metric_scores: Dict[str, float],
        targeted_suggestions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """估算改进潜力"""
        potential = {}
        
        for suggestion in targeted_suggestions:
            area = suggestion["area"]
            current_score = metric_scores.get(area, 0.0)
            
            # 基于建议数量和难度估算改进潜力
            suggestion_count = len(suggestion.get("specific_suggestions", []))
            difficulty = suggestion.get("difficulty", "medium")
            
            base_improvement = suggestion_count * 0.1
            
            # 根据难度调整
            difficulty_multiplier = {
                "easy": 1.2,
                "medium": 1.0,
                "hard": 0.8
            }.get(difficulty, 1.0)
            
            estimated_improvement = base_improvement * difficulty_multiplier
            potential_score = min(1.0, current_score + estimated_improvement)
            
            potential[area] = potential_score
        
        return potential
    
    def _estimate_improvement_effort(self, priority_areas: List[str]) -> str:
        """估算改进工作量"""
        if len(priority_areas) <= 1:
            return "low"
        elif len(priority_areas) <= 2:
            return "medium"
        else:
            return "high"
    
    def _generate_comparison_summary(
        self,
        improvements: Dict[str, Any],
        regressions: Dict[str, Any],
        overall_change: float
    ) -> str:
        """生成比较摘要"""
        summary_parts = []
        
        if overall_change > 0.05:
            summary_parts.append(f"整体质量提升了{overall_change:.2f}分")
        elif overall_change < -0.05:
            summary_parts.append(f"整体质量下降了{abs(overall_change):.2f}分")
        else:
            summary_parts.append("整体质量基本保持稳定")
        
        if improvements:
            improved_areas = list(improvements.keys())
            summary_parts.append(f"在{', '.join(improved_areas)}方面有显著改进")
        
        if regressions:
            regressed_areas = list(regressions.keys())
            summary_parts.append(f"在{', '.join(regressed_areas)}方面有所退步")
        
        return "；".join(summary_parts) + "。"
    
    def _generate_version_recommendation(
        self,
        overall_change: float,
        improvements: Dict[str, Any],
        regressions: Dict[str, Any]
    ) -> str:
        """生成版本推荐"""
        if overall_change > 0.1:
            return "建议采用修改后的版本，质量有显著提升"
        elif overall_change > 0:
            return "建议采用修改后的版本，质量有所改善"
        elif overall_change > -0.05:
            return "两个版本质量相近，可根据其他因素选择"
        else:
            return "建议保留原版本，修改后质量有所下降"
    
    def _estimate_metric_improvement_potential(self, metric: str, current_score: float) -> float:
        """估算指标改进潜力"""
        # 简化的改进潜力估算
        max_improvement = 1.0 - current_score
        
        # 根据指标类型调整改进潜力
        improvement_factors = {
            "readability": 0.8,
            "completeness": 0.9,
            "coherence": 0.7,
            "specificity": 0.8,
            "actionability": 0.6
        }
        
        factor = improvement_factors.get(metric, 0.7)
        return max_improvement * factor


class ReadabilityAnalyzer:
    """可读性分析器"""
    
    def analyze(self, context: str, context_type: str) -> tuple[float, Dict[str, Any]]:
        """分析可读性"""
        score = 0.5
        analysis = {"issues": [], "suggestions": []}
        
        # 句子长度分析
        sentences = re.split(r'[.!?。！？]', context)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_length <= 15:
                score += 0.2
            elif avg_length > 25:
                score -= 0.1
                analysis["issues"].append("句子平均长度过长")
                analysis["suggestions"].append("将长句分解为多个短句")
        
        # 词汇复杂度分析
        words = context.split()
        complex_words = [w for w in words if len(w) > 8]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        if complexity_ratio < 0.2:
            score += 0.2
        elif complexity_ratio > 0.4:
            score -= 0.1
            analysis["issues"].append("使用了过多复杂词汇")
            analysis["suggestions"].append("使用更简单易懂的词汇")
        
        # 段落结构分析
        paragraphs = [p.strip() for p in context.split('\n') if p.strip()]
        if len(paragraphs) > 1:
            score += 0.1
        else:
            analysis["suggestions"].append("考虑将内容分成多个段落")
        
        return min(1.0, max(0.0, score)), analysis


class CompletenessAnalyzer:
    """完整性分析器"""
    
    def analyze(self, context: str, context_type: str) -> tuple[float, Dict[str, Any]]:
        """分析完整性"""
        score = 0.5
        analysis = {"issues": [], "suggestions": []}
        
        # 长度分析
        word_count = len(context.split())
        
        if context_type == "prompt":
            if word_count >= 30:
                score += 0.2
            elif word_count < 15:
                score -= 0.2
                analysis["issues"].append("内容过于简短")
                analysis["suggestions"].append("添加更多详细信息")
        else:
            if word_count >= 50:
                score += 0.2
            elif word_count < 25:
                score -= 0.2
                analysis["issues"].append("内容不够充实")
                analysis["suggestions"].append("补充更多相关信息")
        
        # 结构元素检查
        has_background = any(keyword in context for keyword in ["背景", "context", "背景信息"])
        has_objective = any(keyword in context for keyword in ["目标", "目的", "objective", "goal"])
        has_requirements = any(keyword in context for keyword in ["要求", "需要", "requirement"])
        
        structure_elements = sum([has_background, has_objective, has_requirements])
        score += structure_elements * 0.1
        
        if not has_background:
            analysis["suggestions"].append("添加相关背景信息")
        if not has_objective:
            analysis["suggestions"].append("明确目标或目的")
        if not has_requirements:
            analysis["suggestions"].append("说明具体要求")
        
        return min(1.0, max(0.0, score)), analysis


class CoherenceAnalyzer:
    """连贯性分析器"""
    
    def analyze(self, context: str, context_type: str) -> tuple[float, Dict[str, Any]]:
        """分析连贯性"""
        score = 0.5
        analysis = {"issues": [], "suggestions": []}
        
        # 逻辑连接词检查
        connectors = ["因此", "所以", "但是", "然而", "首先", "其次", "最后", "另外", "此外"]
        connector_count = sum(1 for conn in connectors if conn in context)
        
        if connector_count > 0:
            score += min(0.2, connector_count * 0.05)
        else:
            analysis["suggestions"].append("使用逻辑连接词增强连贯性")
        
        # 主题一致性检查（简化实现）
        sentences = re.split(r'[.!?。！？]', context)
        if len(sentences) > 3:
            # 检查是否有明显的主题跳跃
            score += 0.1  # 简化处理
        
        # 代词使用检查
        pronouns = ["这", "那", "它", "他们", "我们"]
        pronoun_count = sum(1 for pronoun in pronouns if pronoun in context)
        
        if pronoun_count > 0:
            score += 0.1
        else:
            analysis["suggestions"].append("适当使用代词增强文本连贯性")
        
        return min(1.0, max(0.0, score)), analysis


class SpecificityAnalyzer:
    """具体性分析器"""
    
    def analyze(self, context: str, context_type: str) -> tuple[float, Dict[str, Any]]:
        """分析具体性"""
        score = 0.5
        analysis = {"issues": [], "suggestions": []}
        
        # 数字和数据检查
        numbers = re.findall(r'\d+', context)
        if len(numbers) > 0:
            score += min(0.3, len(numbers) * 0.1)
        else:
            analysis["suggestions"].append("添加具体的数据和指标")
        
        # 示例检查
        example_indicators = ["例如", "比如", "举例", "示例", "案例"]
        examples = sum(1 for indicator in example_indicators if indicator in context)
        
        if examples > 0:
            score += min(0.2, examples * 0.1)
        else:
            analysis["suggestions"].append("提供具体示例说明")
        
        # 模糊词汇检查
        vague_words = ["一些", "很多", "大量", "少量", "可能", "也许", "大概"]
        vague_count = sum(1 for word in vague_words if word in context)
        
        if vague_count > 3:
            score -= 0.1
            analysis["issues"].append("使用了过多模糊表达")
            analysis["suggestions"].append("用具体的描述替换模糊词汇")
        
        # 时间和地点具体性
        time_indicators = ["时间", "日期", "年", "月", "日", "小时"]
        place_indicators = ["地点", "位置", "地址", "场所"]
        
        has_time_specificity = any(indicator in context for indicator in time_indicators)
        has_place_specificity = any(indicator in context for indicator in place_indicators)
        
        if has_time_specificity:
            score += 0.1
        if has_place_specificity:
            score += 0.1
        
        return min(1.0, max(0.0, score)), analysis


class ActionabilityAnalyzer:
    """可操作性分析器"""
    
    def analyze(self, context: str, context_type: str) -> tuple[float, Dict[str, Any]]:
        """分析可操作性"""
        score = 0.5
        analysis = {"issues": [], "suggestions": []}
        
        # 动作词检查
        action_words = ["创建", "生成", "分析", "评估", "实现", "开发", "设计", "优化", "改进"]
        action_count = sum(1 for word in action_words if word in context)
        
        if action_count > 0:
            score += min(0.3, action_count * 0.1)
        else:
            analysis["suggestions"].append("使用更多动作导向的语言")
        
        # 步骤指示检查
        step_indicators = ["步骤", "首先", "然后", "接下来", "最后", "第一", "第二"]
        steps = sum(1 for indicator in step_indicators if indicator in context)
        
        if steps > 0:
            score += min(0.2, steps * 0.05)
        else:
            analysis["suggestions"].append("提供明确的操作步骤")
        
        # 可衡量性检查
        measurable_words = ["测量", "评估", "指标", "标准", "目标", "结果"]
        measurable_count = sum(1 for word in measurable_words if word in context)
        
        if measurable_count > 0:
            score += 0.1
        else:
            analysis["suggestions"].append("设定可衡量的目标和标准")
        
        return min(1.0, max(0.0, score)), analysis