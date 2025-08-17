#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共识质量评估器

评估共识形成过程的质量和有效性
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class ConsensusQualityEvaluator:
    """共识质量评估器"""
    
    def __init__(self):
        """初始化共识质量评估器"""
        self.quality_metrics = [
            "consensus_score",
            "coherence_score", 
            "participant_satisfaction",
            "convergence_rate",
            "stability_index",
            "diversity_preservation"
        ]
        self.evaluation_history = []
        self.quality_thresholds = {
            "consensus_score": {"excellent": 0.9, "good": 0.7, "fair": 0.5},
            "coherence_score": {"excellent": 0.85, "good": 0.65, "fair": 0.45},
            "participant_satisfaction": {"excellent": 0.8, "good": 0.6, "fair": 0.4}
        }
    
    def evaluate_consensus_quality(
        self,
        consensus_data: Dict[str, Any],
        participants_data: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """评估共识质量"""
        try:
            evaluation_result = {
                "evaluation_id": f"quality_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "overall_quality": 0.0,
                "metrics": {},
                "quality_grade": "unknown",
                "recommendations": []
            }
            
            # 计算各项质量指标
            evaluation_result["metrics"]["consensus_score"] = self._calculate_consensus_score(consensus_data)
            evaluation_result["metrics"]["coherence_score"] = self.calculate_coherence_score(consensus_data)
            evaluation_result["metrics"]["participant_satisfaction"] = self.assess_participant_satisfaction(participants_data or [])
            evaluation_result["metrics"]["convergence_rate"] = self._calculate_convergence_rate(consensus_data)
            evaluation_result["metrics"]["stability_index"] = self._calculate_stability_index(consensus_data)
            evaluation_result["metrics"]["diversity_preservation"] = self._calculate_diversity_preservation(consensus_data)
            
            # 计算总体质量分数
            metric_weights = {
                "consensus_score": 0.25,
                "coherence_score": 0.20,
                "participant_satisfaction": 0.20,
                "convergence_rate": 0.15,
                "stability_index": 0.10,
                "diversity_preservation": 0.10
            }
            
            weighted_sum = sum(
                evaluation_result["metrics"][metric] * weight
                for metric, weight in metric_weights.items()
                if metric in evaluation_result["metrics"]
            )
            
            evaluation_result["overall_quality"] = weighted_sum
            evaluation_result["quality_grade"] = self._determine_quality_grade(weighted_sum)
            evaluation_result["recommendations"] = self._generate_improvement_recommendations(evaluation_result["metrics"])
            
            # 保存评估历史
            self.evaluation_history.append(evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"评估共识质量失败: {e}")
            return {"error": str(e)}
    
    def calculate_coherence_score(self, consensus_data: Dict[str, Any]) -> float:
        """计算一致性分数"""
        try:
            # 获取参与者立场
            positions = consensus_data.get("participant_positions", [])
            if not positions:
                return 0.0
            
            # 计算立场间的相似度
            similarity_scores = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    similarity = self._calculate_position_similarity(positions[i], positions[j])
                    similarity_scores.append(similarity)
            
            if not similarity_scores:
                return 0.0
            
            # 返回平均相似度作为一致性分数
            coherence_score = statistics.mean(similarity_scores)
            return min(max(coherence_score, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"计算一致性分数失败: {e}")
            return 0.0
    
    def assess_participant_satisfaction(self, participants_data: List[Dict[str, Any]]) -> float:
        """评估参与者满意度"""
        try:
            if not participants_data:
                return 0.0
            
            satisfaction_scores = []
            
            for participant in participants_data:
                # 基于多个因素计算满意度
                factors = {
                    "agreement_with_consensus": participant.get("agreement_level", 0.5),
                    "participation_level": participant.get("participation_score", 0.5),
                    "influence_on_outcome": participant.get("influence_score", 0.5),
                    "process_fairness": participant.get("fairness_perception", 0.5)
                }
                
                # 加权平均计算个人满意度
                weights = {
                    "agreement_with_consensus": 0.3,
                    "participation_level": 0.25,
                    "influence_on_outcome": 0.25,
                    "process_fairness": 0.2
                }
                
                personal_satisfaction = sum(
                    factors[factor] * weights[factor]
                    for factor in factors
                    if factor in weights
                )
                
                satisfaction_scores.append(personal_satisfaction)
            
            # 返回平均满意度
            if satisfaction_scores:
                return statistics.mean(satisfaction_scores)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"评估参与者满意度失败: {e}")
            return 0.0
    
    def _calculate_consensus_score(self, consensus_data: Dict[str, Any]) -> float:
        """计算共识分数"""
        try:
            # 从共识数据中提取分数
            if "consensus_score" in consensus_data:
                return float(consensus_data["consensus_score"])
            
            # 如果没有直接的共识分数，基于其他数据计算
            agreement_levels = consensus_data.get("agreement_levels", [])
            if agreement_levels:
                return statistics.mean(agreement_levels)
            
            return 0.5  # 默认中等共识
            
        except Exception as e:
            logger.error(f"计算共识分数失败: {e}")
            return 0.0
    
    def _calculate_convergence_rate(self, consensus_data: Dict[str, Any]) -> float:
        """计算收敛速度"""
        try:
            convergence_history = consensus_data.get("convergence_history", [])
            if len(convergence_history) < 2:
                return 0.0
            
            # 计算收敛速度（分数变化率）
            initial_score = convergence_history[0].get("score", 0.0)
            final_score = convergence_history[-1].get("score", 0.0)
            time_steps = len(convergence_history)
            
            if time_steps > 1:
                convergence_rate = (final_score - initial_score) / (time_steps - 1)
                return min(max(convergence_rate, 0.0), 1.0)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"计算收敛速度失败: {e}")
            return 0.0
    
    def _calculate_stability_index(self, consensus_data: Dict[str, Any]) -> float:
        """计算稳定性指数"""
        try:
            stability_data = consensus_data.get("stability_measurements", [])
            if not stability_data:
                return 0.5  # 默认中等稳定性
            
            # 计算分数变化的标准差（越小越稳定）
            scores = [measurement.get("score", 0.0) for measurement in stability_data]
            if len(scores) > 1:
                score_variance = statistics.variance(scores)
                # 将方差转换为稳定性指数（0-1范围）
                stability_index = 1.0 / (1.0 + score_variance)
                return min(max(stability_index, 0.0), 1.0)
            
            return 0.5
            
        except Exception as e:
            logger.error(f"计算稳定性指数失败: {e}")
            return 0.0
    
    def _calculate_diversity_preservation(self, consensus_data: Dict[str, Any]) -> float:
        """计算多样性保持度"""
        try:
            initial_diversity = consensus_data.get("initial_diversity", 0.0)
            final_diversity = consensus_data.get("final_diversity", 0.0)
            
            if initial_diversity > 0:
                preservation_ratio = final_diversity / initial_diversity
                return min(max(preservation_ratio, 0.0), 1.0)
            
            return 0.5  # 默认中等多样性保持
            
        except Exception as e:
            logger.error(f"计算多样性保持度失败: {e}")
            return 0.0
    
    def _calculate_position_similarity(self, position1: Dict[str, Any], position2: Dict[str, Any]) -> float:
        """计算立场相似度"""
        try:
            # 简单的文本相似度计算（实际应用中可以使用更复杂的NLP方法）
            text1 = str(position1.get("content", ""))
            text2 = str(position2.get("content", ""))
            
            if not text1 or not text2:
                return 0.0
            
            # 简单的词汇重叠计算
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            logger.error(f"计算立场相似度失败: {e}")
            return 0.0
    
    def _determine_quality_grade(self, overall_quality: float) -> str:
        """确定质量等级"""
        if overall_quality >= 0.9:
            return "excellent"
        elif overall_quality >= 0.7:
            return "good"
        elif overall_quality >= 0.5:
            return "fair"
        elif overall_quality >= 0.3:
            return "poor"
        else:
            return "very_poor"
    
    def _generate_improvement_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if metrics.get("consensus_score", 0.0) < 0.6:
            recommendations.append("增加讨论轮次以提高共识水平")
        
        if metrics.get("coherence_score", 0.0) < 0.5:
            recommendations.append("引入更多结构化讨论来提高观点一致性")
        
        if metrics.get("participant_satisfaction", 0.0) < 0.6:
            recommendations.append("改进参与机制以提高参与者满意度")
        
        if metrics.get("convergence_rate", 0.0) < 0.3:
            recommendations.append("优化讨论流程以加快共识收敛")
        
        if metrics.get("stability_index", 0.0) < 0.4:
            recommendations.append("增强共识稳定性措施")
        
        if metrics.get("diversity_preservation", 0.0) < 0.3:
            recommendations.append("平衡共识形成与观点多样性保持")
        
        if not recommendations:
            recommendations.append("当前共识质量良好，继续保持现有流程")
        
        return recommendations
    
    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """获取评估历史"""
        return self.evaluation_history.copy()
    
    def get_quality_trends(self) -> Dict[str, Any]:
        """获取质量趋势分析"""
        if len(self.evaluation_history) < 2:
            return {"message": "需要至少两次评估才能分析趋势"}
        
        trends = {}
        for metric in self.quality_metrics:
            values = [eval_result["metrics"].get(metric, 0.0) for eval_result in self.evaluation_history]
            if len(values) >= 2:
                trend = "improving" if values[-1] > values[0] else "declining" if values[-1] < values[0] else "stable"
                trends[metric] = {
                    "trend": trend,
                    "change": values[-1] - values[0],
                    "current_value": values[-1]
                }
        
        return trends