#!/usr/bin/env python3
"""冲突解决策略

提供多种冲突解决策略
"""

import logging
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class ConflictResolutionStrategies:
    """冲突解决策略"""

    def __init__(self):
        """初始化冲突解决策略"""
        self.available_strategies = [
            "evidence_weighting",
            "source_credibility",
            "synthesis",
            "temporal_priority",
            "stakeholder_consensus"
        ]
        self.strategy_effectiveness = {
            "evidence_weighting": 0.85,
            "source_credibility": 0.80,
            "synthesis": 0.75,
            "temporal_priority": 0.70,
            "stakeholder_consensus": 0.65
        }
<<<<<<< HEAD

    def select_strategy(self, conflict_context: Dict[str, Any]) -> Dict[str, Any]:
=======
    
    def select_strategy(self, conflict_context: dict[str, Any]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """选择策略"""
        try:
            conflict_type = conflict_context.get("conflict_type", "unknown")
            severity = conflict_context.get("severity", "medium")

            # 基于上下文选择最佳策略
            if conflict_type == "contradictory_claims" and severity == "high":
                selected = "evidence_weighting"
                rationale = "高严重性矛盾声明需要基于证据权重解决"
            elif conflict_context.get("evidence_quality") == "high":
                selected = "evidence_weighting"
                rationale = "高质量证据支持证据权重策略"
            else:
                selected = "synthesis"
                rationale = "综合策略适用于大多数冲突情况"

            return {
                "strategy_name": selected,
                "confidence": self.strategy_effectiveness.get(selected, 0.5),
                "rationale": rationale,
                "alternatives": [s for s in self.available_strategies if s != selected][:2]
            }

        except Exception as e:
            logger.error(f"选择策略失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def apply_synthesis_strategy(self, conflicting_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def apply_synthesis_strategy(self, conflicting_claims: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """应用综合策略"""
        try:
            if not conflicting_claims:
                return {"error": "没有冲突声明"}

            # 提取所有声明
            claims = [claim.get("claim", "") for claim in conflicting_claims]

            # 简单的综合逻辑
            synthesized_position = f"综合分析{len(claims)}个观点后认为："

            # 寻找共同点
            common_themes = self._find_common_elements(claims)
            if common_themes:
                synthesized_position += f"各方都认同{common_themes}。"

            # 处理分歧
            synthesized_position += "同时需要平衡不同观点的合理性。"

            # 计算综合置信度
            confidences = [claim.get("evidence_strength", 0.5) for claim in conflicting_claims]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            return {
                "synthesized_position": synthesized_position,
                "confidence_level": avg_confidence * 0.8,  # 综合后略降
                "supporting_evidence": [f"整合了{len(claims)}个观点"],
                "synthesis_method": "balanced_integration"
            }

        except Exception as e:
            logger.error(f"应用综合策略失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def apply_evidence_weighting(self, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def apply_evidence_weighting(self, evidence_items: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """应用证据权重策略"""
        try:
            if not evidence_items:
                return {"error": "没有证据项"}

            # 计算每个证据项的权重
            weighted_items = []
            for item in evidence_items:
                weight = (
                    item.get("evidence_strength", 0.5) * 0.4 +
                    item.get("source_credibility", 0.5) * 0.6
                )
                weighted_items.append({
                    "item": item,
                    "weight": weight
                })

            # 选择权重最高的项
            best_item = max(weighted_items, key=lambda x: x["weight"])

            return {
                "selected_evidence": best_item["item"],
                "confidence_level": best_item["weight"],
                "weighting_rationale": "基于证据强度和来源可信度的综合评估",
                "all_weights": [item["weight"] for item in weighted_items]
            }

        except Exception as e:
            logger.error(f"应用证据权重策略失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _find_common_elements(self, claims: List[str]) -> str:
=======
    
    def _find_common_elements(self, claims: list[str]) -> str:
>>>>>>> feature/core-services-refactor
        """寻找共同元素"""
        try:
            if len(claims) < 2:
                return ""

            # 简单的关键词重叠检测
            all_words = []
            for claim in claims:
                words = claim.split()
                all_words.extend([w for w in words if len(w) > 2])

            word_count = {}
            for word in all_words:
                word_count[word] = word_count.get(word, 0) + 1

            common_words = [word for word, count in word_count.items() if count > 1]

            if common_words:
                return "、".join(common_words[:3])
            else:
                return "某些基本概念"

        except Exception as e:
            logger.error(f"寻找共同元素失败: {e}")
            return ""
