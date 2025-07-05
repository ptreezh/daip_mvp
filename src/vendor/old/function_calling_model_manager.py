"""Function Calling专用模型管理器
专门处理工具调用相关的模型选择和优化
"""

import logging
from dataclasses import dataclass
from typing import Any

from src.constants import *

from .config import FUNCTION_CALLING_MODEL


@dataclass
class ModelCapability:
    """模型能力评估"""

    function_calling_score: float  # 工具调用能力评分 (0-1)
    reasoning_score: float  # 推理能力评分 (0-1)
    speed_score: float  # 响应速度评分 (0-1)
    reliability_score: float  # 可靠性评分 (0-1)
    overall_score: float  # 综合评分 (0-1)


class FunctionCallingModelManager:
    """Function Calling专用模型管理器

    功能：
    1. 评估模型的工具调用能力
    2. 根据任务复杂度选择最适合的模型
    3. 管理模型的性能统计和优化
    4. 提供模型切换和回退机制
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_capabilities = self._initialize_model_capabilities()
        self.performance_stats = {}
        self.current_model = FUNCTION_CALLING_MODEL

    def _initialize_model_capabilities(self) -> dict[str, ModelCapability]:
        """初始化模型能力评估"""
        capabilities = {}

        # 基于模型特性的预设评分
        model_ratings = {
            "atlas/intersync-gemma-7b-instruct-function-calling:latest": {
                "function_calling_score": 0.95,  # 专门为function calling优化
                "reasoning_score": 0.8,
                "speed_score": 0.85,
                "reliability_score": 0.9,
            },
            "llama3-groq-tool-use:latest": {
                "function_calling_score": 0.9,  # Groq优化的工具使用
                "reasoning_score": 0.85,
                "speed_score": 0.9,
                "reliability_score": 0.85,
            },
            "qwen3:30b-a3b": {
                "function_calling_score": 0.85,  # 大模型，通用能力强
                "reasoning_score": 0.95,
                "speed_score": 0.6,
                "reliability_score": 0.9,
            },
            "deepseek-r1:8b": {
                "function_calling_score": 0.8,
                "reasoning_score": 0.9,
                "speed_score": 0.8,
                "reliability_score": 0.85,
            },
            "qwen3:8b": {
                "function_calling_score": 0.75,
                "reasoning_score": 0.8,
                "speed_score": 0.85,
                "reliability_score": 0.8,
            },
        }

        for model_name, ratings in model_ratings.items():
            # 计算综合评分
            overall_score = (
                ratings["function_calling_score"] * 0.4
                + ratings["reasoning_score"] * 0.3  # 工具调用权重最高
                + ratings["speed_score"] * 0.2
                + ratings["reliability_score"] * 0.1
            )

            capabilities[model_name] = ModelCapability(
                function_calling_score=ratings["function_calling_score"],
                reasoning_score=ratings["reasoning_score"],
                speed_score=ratings["speed_score"],
                reliability_score=ratings["reliability_score"],
                overall_score=overall_score,
            )

        return capabilities

    def get_best_model_for_task(
        self,
        task_complexity: str = "medium",
        priority: str = "accuracy",
    ) -> str:
        """根据任务复杂度和优先级选择最佳模型

        Args:
        ----
            task_complexity: 任务复杂度 ("simple", "medium", "complex")
            priority: 优先级 ("accuracy", "speed", "balanced")

        Returns:
        -------
            最适合的模型名称

        """
        if not self.model_capabilities:
            return self.current_model

        # 根据优先级调整权重
        if priority == "accuracy":
            weights = {
                "function_calling": 0.5,
                "reasoning": 0.3,
                "speed": 0.1,
                "reliability": 0.1,
            }
        elif priority == "speed":
            weights = {
                "function_calling": 0.3,
                "reasoning": 0.2,
                "speed": 0.4,
                "reliability": 0.1,
            }
        else:  # balanced
            weights = {
                "function_calling": 0.4,
                "reasoning": 0.25,
                "speed": 0.25,
                "reliability": 0.1,
            }

        # 根据任务复杂度筛选模型
        suitable_models = {}
        for model_name, capability in self.model_capabilities.items():
            if task_complexity == "simple" and capability.speed_score >= 0.7:
                suitable_models[model_name] = capability
            elif task_complexity == "complex" and capability.reasoning_score >= 0.8:
                suitable_models[model_name] = capability
            else:  # medium or fallback
                suitable_models[model_name] = capability

        if not suitable_models:
            suitable_models = self.model_capabilities

        # 计算加权评分
        best_model = None
        best_score = 0

        for model_name, capability in suitable_models.items():
            weighted_score = (
                capability.function_calling_score * weights["function_calling"]
                + capability.reasoning_score * weights["reasoning"]
                + capability.speed_score * weights["speed"]
                + capability.reliability_score * weights["reliability"]
            )

            if weighted_score > best_score:
                best_score = weighted_score
                best_model = model_name

        self.logger.info(
            f"为任务复杂度'{task_complexity}'和优先级'{priority}'选择模型: {best_model} (评分: {best_score:.3f})",
        )
        return best_model or self.current_model

    def update_model_performance(
        self,
        model_name: str,
        success: bool,
        response_time: float,
        tool_calls_count: int = 0,
    ):
        """更新模型性能统计"""
        if model_name not in self.performance_stats:
            self.performance_stats[model_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_response_time": 0,
                "tool_calls_count": 0,
                "success_rate": 0,
                "avg_response_time": 0,
            }

        stats = self.performance_stats[model_name]
        stats["total_calls"] += 1
        if success:
            stats["successful_calls"] += 1
        stats["total_response_time"] += response_time
        stats["tool_calls_count"] += tool_calls_count

        # 更新计算指标
        stats["success_rate"] = stats["successful_calls"] / stats["total_calls"]
        stats["avg_response_time"] = stats["total_response_time"] / stats["total_calls"]

        # 动态调整模型能力评分
        if model_name in self.model_capabilities:
            capability = self.model_capabilities[model_name]
            # 基于实际性能调整评分
            performance_factor = (
                stats["success_rate"] * 0.8
                + (1 - min(stats["avg_response_time"] / 10, 1)) * 0.2
            )
            capability.reliability_score = min(
                capability.reliability_score * 0.9 + performance_factor * 0.1,
                1.0,
            )

    def get_model_recommendations(self, user_input: str) -> list[dict[str, Any]]:
        """根据用户输入推荐模型

        Args:
        ----
            user_input: 用户输入文本

        Returns:
        -------
            推荐模型列表，按优先级排序

        """
        # 分析输入复杂度
        complexity = self._analyze_input_complexity(user_input)

        # 获取推荐模型
        recommendations = []

        for priority in ["accuracy", "balanced", "speed"]:
            model = self.get_best_model_for_task(complexity, priority)
            if model in self.model_capabilities:
                capability = self.model_capabilities[model]
                recommendations.append(
                    {
                        "model_name": model,
                        "priority": priority,
                        "complexity": complexity,
                        "overall_score": capability.overall_score,
                        "function_calling_score": capability.function_calling_score,
                        "reasoning": f"最适合{complexity}复杂度任务，优先考虑{priority}",
                    },
                )

        # 去重并按评分排序
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["model_name"] not in seen:
                seen.add(rec["model_name"])
                unique_recommendations.append(rec)

        unique_recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
        return unique_recommendations[:3]  # 返回前3个推荐

    def _analyze_input_complexity(self, user_input: str) -> str:
        """分析输入复杂度"""
        text_length = len(user_input)

        # 复杂度指标
        complexity_indicators = {
            "multiple_tasks": len(
                [word for word in ["和", "以及", "同时", "然后", "接着"] if word in user_input],
            ),
            "technical_terms": len(
                [word for word in ["算法", "协议", "验证", "分析", "计算"] if word in user_input],
            ),
            "conditional_logic": len(
                [word for word in ["如果", "当", "假设", "条件"] if word in user_input],
            ),
        }

        complexity_score = (
            min(text_length / 100, 1) * 0.3
            + min(complexity_indicators["multiple_tasks"] / 3, 1) * 0.3
            + min(complexity_indicators["technical_terms"] / 3, 1) * 0.2
            + min(complexity_indicators["conditional_logic"] / 2, 1) * 0.2
        )

        if complexity_score >= 0.7:
            return "complex"
        elif complexity_score >= 0.4:
            return "medium"
        else:
            return "simple"

    def get_performance_report(self) -> dict[str, Any]:
        """获取性能报告"""
        return {
            "current_model": self.current_model,
            "model_capabilities": {
                name: {
                    "function_calling_score": cap.function_calling_score,
                    "reasoning_score": cap.reasoning_score,
                    "speed_score": cap.speed_score,
                    "reliability_score": cap.reliability_score,
                    "overall_score": cap.overall_score,
                }
                for name, cap in self.model_capabilities.items()
            },
            "performance_stats": self.performance_stats,
        }
