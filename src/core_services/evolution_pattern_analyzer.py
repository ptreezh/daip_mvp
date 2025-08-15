#!/usr/bin/env python3
"""演化模式分析器

分析知识演化的模式和趋势
"""

import logging
<<<<<<< HEAD
from typing import Any, Dict, List
=======
from typing import Any
>>>>>>> feature/core-services-refactor

logger = logging.getLogger(__name__)


class EvolutionPatternAnalyzer:
    """演化模式分析器"""

    def __init__(self):
        """初始化演化模式分析器"""
        self.pattern_templates = {
            "incremental_growth": "渐进式增长",
            "rapid_expansion": "快速扩展",
            "refinement_cycle": "优化循环",
            "knowledge_merge": "知识合并",
            "paradigm_shift": "范式转换"
        }
        self.analysis_history = []
<<<<<<< HEAD

    def identify_evolution_patterns(self, evolution_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
=======
    
    def identify_evolution_patterns(self, evolution_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """识别演化模式"""
        try:
            patterns = []

            if len(evolution_data) < 2:
                return patterns

            # 分析变化类型序列
            change_types = [event.get("change_type", "") for event in evolution_data]

            # 检测渐进式增长模式
            if self._detect_incremental_growth(change_types):
                patterns.append({
                    "pattern_type": "incremental_growth",
                    "confidence": 0.8,
                    "description": "知识呈现渐进式增长模式",
                    "evidence": "连续的增强和优化操作"
                })

            # 检测快速扩展模式
            if self._detect_rapid_expansion(evolution_data):
                patterns.append({
                    "pattern_type": "rapid_expansion",
                    "confidence": 0.7,
                    "description": "知识在短时间内快速扩展",
                    "evidence": "高频率的扩展操作"
                })

            # 检测优化循环模式
            if self._detect_refinement_cycle(change_types):
                patterns.append({
                    "pattern_type": "refinement_cycle",
                    "confidence": 0.6,
                    "description": "知识经历多轮优化循环",
                    "evidence": "重复的优化和修正操作"
                })

            return patterns

        except Exception as e:
            logger.error(f"识别演化模式失败: {e}")
            return []
<<<<<<< HEAD

    def predict_evolution_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def predict_evolution_trends(self, historical_data: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """预测演化趋势"""
        try:
            if not historical_data:
                return {"prediction": "insufficient_data"}

            # 简单的趋势预测
            recent_changes = historical_data[-3:] if len(historical_data) >= 3 else historical_data
            change_types = [event.get("change_type", "") for event in recent_changes]

            prediction = {
                "next_likely_change": self._predict_next_change(change_types),
                "confidence": 0.6,
                "reasoning": "基于最近的变化模式预测",
                "timeline": "1-2周内"
            }

            return prediction

        except Exception as e:
            logger.error(f"预测演化趋势失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def analyze_knowledge_lifecycle(self, evolution_data: List[Dict[str, Any]]) -> Dict[str, Any]:
=======
    
    def analyze_knowledge_lifecycle(self, evolution_data: list[dict[str, Any]]) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析知识生命周期"""
        try:
            if not evolution_data:
                return {"stage": "unknown"}

            change_types = [event.get("change_type", "") for event in evolution_data]

            # 简单的生命周期判断
            if "creation" in change_types and len(change_types) <= 2:
                stage = "birth"
            elif any(ct in change_types for ct in ["enhancement", "expansion"]):
                stage = "growth"
            elif any(ct in change_types for ct in ["refinement", "correction"]):
                stage = "maturity"
            elif "deprecation" in change_types:
                stage = "decline"
            else:
                stage = "maintenance"

            lifecycle_analysis = {
                "current_stage": stage,
                "stage_duration": len(evolution_data),
                "maturity_indicators": self._assess_maturity(change_types),
                "health_score": self._calculate_health_score(evolution_data)
            }

            return lifecycle_analysis

        except Exception as e:
            logger.error(f"分析知识生命周期失败: {e}")
            return {"error": str(e)}
<<<<<<< HEAD

    def _detect_incremental_growth(self, change_types: List[str]) -> bool:
=======
    
    def _detect_incremental_growth(self, change_types: list[str]) -> bool:
>>>>>>> feature/core-services-refactor
        """检测渐进式增长"""
        growth_types = ["enhancement", "refinement", "expansion"]
        growth_count = sum(1 for ct in change_types if ct in growth_types)
        return growth_count >= len(change_types) * 0.6
<<<<<<< HEAD

    def _detect_rapid_expansion(self, evolution_data: List[Dict[str, Any]]) -> bool:
=======
    
    def _detect_rapid_expansion(self, evolution_data: list[dict[str, Any]]) -> bool:
>>>>>>> feature/core-services-refactor
        """检测快速扩展"""
        if len(evolution_data) < 3:
            return False

        # 检查时间密度
        timestamps = [event.get("timestamp", "") for event in evolution_data]
        expansion_count = sum(1 for event in evolution_data if event.get("change_type") == "expansion")

        return expansion_count >= 2 and len(evolution_data) >= 3
<<<<<<< HEAD

    def _detect_refinement_cycle(self, change_types: List[str]) -> bool:
=======
    
    def _detect_refinement_cycle(self, change_types: list[str]) -> bool:
>>>>>>> feature/core-services-refactor
        """检测优化循环"""
        refinement_types = ["refinement", "correction"]
        refinement_count = sum(1 for ct in change_types if ct in refinement_types)
        return refinement_count >= 2
<<<<<<< HEAD

    def _predict_next_change(self, recent_changes: List[str]) -> str:
=======
    
    def _predict_next_change(self, recent_changes: list[str]) -> str:
>>>>>>> feature/core-services-refactor
        """预测下一个变化"""
        if not recent_changes:
            return "enhancement"

        last_change = recent_changes[-1]

        # 简单的预测逻辑
        prediction_map = {
            "creation": "enhancement",
            "enhancement": "refinement",
            "refinement": "expansion",
            "expansion": "refinement",
            "correction": "enhancement"
        }

        return prediction_map.get(last_change, "enhancement")
<<<<<<< HEAD

    def _assess_maturity(self, change_types: List[str]) -> List[str]:
=======
    
    def _assess_maturity(self, change_types: list[str]) -> list[str]:
>>>>>>> feature/core-services-refactor
        """评估成熟度指标"""
        indicators = []

        if "refinement" in change_types:
            indicators.append("经历优化阶段")

        if change_types.count("correction") >= 2:
            indicators.append("多次错误修正")

        if len(set(change_types)) >= 4:
            indicators.append("变化类型多样")

        return indicators
<<<<<<< HEAD

    def _calculate_health_score(self, evolution_data: List[Dict[str, Any]]) -> float:
=======
    
    def _calculate_health_score(self, evolution_data: list[dict[str, Any]]) -> float:
>>>>>>> feature/core-services-refactor
        """计算健康分数"""
        if not evolution_data:
            return 0.0

        # 基于变化频率和类型计算健康分数
        positive_changes = ["enhancement", "expansion", "refinement"]
        negative_changes = ["correction", "deprecation"]

        positive_count = sum(1 for event in evolution_data if event.get("change_type") in positive_changes)
        negative_count = sum(1 for event in evolution_data if event.get("change_type") in negative_changes)

        if len(evolution_data) == 0:
            return 0.0

        health_score = (positive_count - negative_count * 0.5) / len(evolution_data)
        return max(0.0, min(1.0, health_score + 0.5))  # 归一化到0-1
