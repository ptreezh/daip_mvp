#!/usr/bin/env python3
"""智能算法选择器 (Algorithm Selector)

基于输入特征和算法能力智能选择最优的共识算法。
提供多种选择策略和决策可解释性。

核心功能：
1. 基于输入特征的算法适配性评分
2. 多种选择策略支持
3. 自适应选择规则引擎
4. 决策过程可解释性
5. 性能和准确性权衡

设计原则：
- 智能选择：基于多维度评分选择最优算法
- 策略可配置：支持不同的选择策略
- 决策透明：提供详细的选择理由
- 性能优化：快速的选择决策过程
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from algorithm_registry import AlgorithmInfo, AlgorithmRegistry
from consensus_models import (
    AlgorithmSelection,
    ConsensusRequest,
    QualityPriority,
)

logger = logging.getLogger(__name__)


class SelectionStrategy(str, Enum):
    """选择策略枚举"""
    BEST_FIT = "best_fit"  # 最佳匹配
    PERFORMANCE_FIRST = "performance_first"  # 性能优先
    ACCURACY_FIRST = "accuracy_first"  # 准确性优先
    BALANCED = "balanced"  # 平衡策略
    LOAD_BALANCED = "load_balanced"  # 负载均衡
    CUSTOM = "custom"  # 自定义策略


@dataclass
class SelectionCriteria:
    """选择标准"""
    performance_weight: float = 0.3
    accuracy_weight: float = 0.4
    availability_weight: float = 0.2
    compatibility_weight: float = 0.1
    load_balance_factor: float = 0.0
    min_confidence_threshold: float = 0.5
    prefer_simple_algorithms: bool = False
    avoid_experimental: bool = True


@dataclass
class AlgorithmScore:
    """算法评分"""
    algorithm_id: str
    total_score: float
    performance_score: float
    accuracy_score: float
    availability_score: float
    compatibility_score: float
    load_score: float
    reasoning: dict[str, Any] = field(default_factory=dict)


class SelectionRule(ABC):
    """选择规则抽象基类"""
    
    @abstractmethod
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估算法对请求的适合程度
        
        Args:
            request: 共识请求
            algorithm_info: 算法信息
            context: 评估上下文
            
        Returns:
            评分 (0.0-1.0)
        """
        pass
        
    @abstractmethod
    def get_reasoning(self) -> str:
        """获取评估理由"""
        pass


class InputCompatibilityRule(SelectionRule):
    """输入兼容性规则"""
    
    def __init__(self):
        self.last_reasoning = ""
        
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估输入兼容性"""
        capabilities = algorithm_info.capabilities
        
        # 检查输入类型兼容性
        input_types = set()
        for inp in request.inputs:
            input_types.add(type(inp.position).__name__)
            
        supported_types = capabilities.supported_input_types
        compatibility_ratio = len(input_types & supported_types) / len(input_types)
        
        # 检查参与者数量
        participant_count = len(request.inputs)
        if participant_count < capabilities.min_participants:
            participant_score = 0.0
        elif capabilities.max_participants and participant_count > capabilities.max_participants:
            participant_score = 0.0
        else:
            participant_score = 1.0
            
        # 检查特殊要求
        requirements_score = 1.0
        if capabilities.requires_reasoning:
            has_reasoning = all(inp.reasoning for inp in request.inputs)
            if not has_reasoning:
                requirements_score *= 0.5
                
        if capabilities.requires_evidence:
            has_evidence = all(inp.evidence for inp in request.inputs)
            if not has_evidence:
                requirements_score *= 0.5
                
        total_score = compatibility_ratio * participant_score * requirements_score
        
        self.last_reasoning = f"输入兼容性: {compatibility_ratio:.2f}, 参与者匹配: {participant_score:.2f}, 要求满足: {requirements_score:.2f}"
        
        return total_score
        
    def get_reasoning(self) -> str:
        return self.last_reasoning


class PerformanceRule(SelectionRule):
    """性能规则"""
    
    def __init__(self):
        self.last_reasoning = ""
        
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估性能"""
        metadata = algorithm_info.metadata
        
        # 性能等级评分
        performance_scores = {
            "fast": 1.0,
            "medium": 0.7,
            "slow": 0.4
        }
        
        performance_score = performance_scores.get(metadata.performance, 0.5)
        
        # 复杂度评分（简单算法在某些情况下更好）
        complexity_scores = {
            "low": 0.9,
            "medium": 0.7,
            "high": 0.5
        }
        
        complexity_score = complexity_scores.get(metadata.complexity, 0.5)
        
        # 考虑输入规模
        input_count = len(request.inputs)
        if input_count > 100:  # 大规模输入
            if metadata.performance == "fast":
                scale_bonus = 0.2
            else:
                scale_bonus = 0.0
        else:
            scale_bonus = 0.0
            
        total_score = min((performance_score + complexity_score) / 2 + scale_bonus, 1.0)
        
        self.last_reasoning = f"性能等级: {metadata.performance} ({performance_score:.2f}), 复杂度: {metadata.complexity} ({complexity_score:.2f}), 规模奖励: {scale_bonus:.2f}"
        
        return total_score
        
    def get_reasoning(self) -> str:
        return self.last_reasoning


class AccuracyRule(SelectionRule):
    """准确性规则"""
    
    def __init__(self):
        self.last_reasoning = ""
        
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估准确性"""
        metadata = algorithm_info.metadata
        accuracy_score = metadata.accuracy
        
        # 根据质量要求调整
        quality_req = request.quality_requirements
        if quality_req and quality_req.priority == QualityPriority.ACCURACY:
            if accuracy_score >= 0.8:
                bonus = 0.1
            else:
                bonus = -0.1
        else:
            bonus = 0.0
            
        total_score = min(accuracy_score + bonus, 1.0)
        
        self.last_reasoning = f"基础准确性: {accuracy_score:.2f}, 质量要求奖励: {bonus:.2f}"
        
        return total_score
        
    def get_reasoning(self) -> str:
        return self.last_reasoning


class AvailabilityRule(SelectionRule):
    """可用性规则"""
    
    def __init__(self):
        self.last_reasoning = ""
        
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估可用性"""
        # 健康状态评分
        health_scores = {
            "healthy": 1.0,
            "unhealthy": 0.0,
            "unknown": 0.5
        }
        
        health_score = health_scores.get(algorithm_info.health_status, 0.5)
        
        # 使用频率评分（适度使用的算法更可靠）
        usage_count = algorithm_info.usage_count
        if usage_count == 0:
            usage_score = 0.7  # 未使用过，可能不稳定
        elif usage_count < 10:
            usage_score = 0.8
        elif usage_count < 100:
            usage_score = 1.0  # 适度使用
        else:
            usage_score = 0.9  # 高频使用，可能有负载问题
            
        # 最近使用时间
        if algorithm_info.last_used:
            time_since_use = (datetime.now() - algorithm_info.last_used).total_seconds()
            if time_since_use < 3600:  # 1小时内
                recency_score = 1.0
            elif time_since_use < 86400:  # 24小时内
                recency_score = 0.8
            else:
                recency_score = 0.6
        else:
            recency_score = 0.7
            
        total_score = (health_score * 0.5 + usage_score * 0.3 + recency_score * 0.2)
        
        self.last_reasoning = f"健康状态: {algorithm_info.health_status} ({health_score:.2f}), 使用频率: {usage_count} ({usage_score:.2f}), 最近使用: ({recency_score:.2f})"
        
        return total_score
        
    def get_reasoning(self) -> str:
        return self.last_reasoning


class LoadBalanceRule(SelectionRule):
    """负载均衡规则"""
    
    def __init__(self):
        self.last_reasoning = ""
        
    def evaluate(self, 
                 request: ConsensusRequest,
                 algorithm_info: AlgorithmInfo,
                 context: dict[str, Any]) -> float:
        """评估负载均衡"""
        # 获取所有算法的使用统计
        all_usage = context.get("all_algorithm_usage", {})
        
        if not all_usage:
            return 1.0  # 没有统计信息时不影响评分
            
        current_usage = algorithm_info.usage_count
        avg_usage = sum(all_usage.values()) / len(all_usage)
        
        # 使用率低于平均值的算法得到更高评分
        if avg_usage == 0:
            load_score = 1.0
        else:
            usage_ratio = current_usage / avg_usage
            if usage_ratio < 0.5:
                load_score = 1.0  # 使用率很低
            elif usage_ratio < 1.0:
                load_score = 0.8  # 使用率低于平均
            elif usage_ratio < 1.5:
                load_score = 0.6  # 使用率略高于平均
            else:
                load_score = 0.4  # 使用率很高
                
        self.last_reasoning = f"当前使用: {current_usage}, 平均使用: {avg_usage:.1f}, 负载评分: {load_score:.2f}"
        
        return load_score
        
    def get_reasoning(self) -> str:
        return self.last_reasoning


class AlgorithmSelector:
    """智能算法选择器
    
    基于多维度评分和可配置策略选择最优的共识算法。
    """
    
    def __init__(self, 
                 registry: AlgorithmRegistry,
                 default_strategy: SelectionStrategy = SelectionStrategy.BALANCED,
                 default_criteria: Optional[SelectionCriteria] = None):
        self.registry = registry
        self.default_strategy = default_strategy
        self.default_criteria = default_criteria or SelectionCriteria()
        
        # 初始化评估规则
        self.rules = {
            "compatibility": InputCompatibilityRule(),
            "performance": PerformanceRule(),
            "accuracy": AccuracyRule(),
            "availability": AvailabilityRule(),
            "load_balance": LoadBalanceRule()
        }
        
        # 策略配置
        self.strategy_configs = {
            SelectionStrategy.BEST_FIT: SelectionCriteria(
                performance_weight=0.2,
                accuracy_weight=0.3,
                availability_weight=0.3,
                compatibility_weight=0.2
            ),
            SelectionStrategy.PERFORMANCE_FIRST: SelectionCriteria(
                performance_weight=0.6,
                accuracy_weight=0.2,
                availability_weight=0.1,
                compatibility_weight=0.1
            ),
            SelectionStrategy.ACCURACY_FIRST: SelectionCriteria(
                performance_weight=0.1,
                accuracy_weight=0.6,
                availability_weight=0.2,
                compatibility_weight=0.1
            ),
            SelectionStrategy.BALANCED: SelectionCriteria(
                performance_weight=0.25,
                accuracy_weight=0.25,
                availability_weight=0.25,
                compatibility_weight=0.25
            ),
            SelectionStrategy.LOAD_BALANCED: SelectionCriteria(
                performance_weight=0.2,
                accuracy_weight=0.2,
                availability_weight=0.2,
                compatibility_weight=0.2,
                load_balance_factor=0.2
            )
        }
        
        logger.info(f"AlgorithmSelector initialized with strategy: {default_strategy}")
        
    def select_algorithm(self,
                        request: ConsensusRequest,
                        available_algorithms: Optional[list[str]] = None,
                        strategy: Optional[SelectionStrategy] = None,
                        criteria: Optional[SelectionCriteria] = None) -> AlgorithmSelection:
        """选择最优算法
        
        Args:
            request: 共识请求
            available_algorithms: 可用算法列表（可选，默认使用所有健康算法）
            strategy: 选择策略（可选）
            criteria: 选择标准（可选）
            
        Returns:
            算法选择结果
        """
        start_time = time.time()
        
        try:
            # 确定选择策略和标准
            strategy = strategy or self.default_strategy
            criteria = criteria or self.strategy_configs.get(strategy, self.default_criteria)
            
            # 获取可用算法
            if available_algorithms is None:
                available_algorithms = self.registry.get_healthy_algorithms()
                
            if not available_algorithms:
                raise ValueError("No available algorithms for selection")
                
            # 过滤算法（基于基本兼容性）
            compatible_algorithms = self._filter_compatible_algorithms(request, available_algorithms)
            
            if not compatible_algorithms:
                raise ValueError("No compatible algorithms found for the request")
                
            # 评分所有兼容算法
            algorithm_scores = self._score_algorithms(request, compatible_algorithms, criteria)
            
            # 选择最佳算法
            best_algorithm = self._select_best_algorithm(algorithm_scores, strategy)
            
            # 生成备选算法列表
            alternatives = [score.algorithm_id for score in algorithm_scores[1:3]]  # 前2个备选
            
            # 生成选择理由
            reasoning = self._generate_reasoning(best_algorithm, algorithm_scores, strategy, criteria)
            
            selection_time = time.time() - start_time
            
            selection = AlgorithmSelection(
                algorithm_id=best_algorithm.algorithm_id,
                confidence=best_algorithm.total_score,
                reasoning=reasoning,
                alternatives=alternatives,
                selection_time=selection_time
            )
            
            logger.info(f"Selected algorithm: {selection.algorithm_id} (confidence: {selection.confidence:.3f}, time: {selection_time:.3f}s)")
            
            return selection
            
        except Exception as e:
            logger.error(f"Algorithm selection failed: {str(e)}")
            
            # 返回默认选择（如果有可用算法）
            if available_algorithms:
                fallback_algorithm = available_algorithms[0]
                return AlgorithmSelection(
                    algorithm_id=fallback_algorithm,
                    confidence=0.1,
                    reasoning=f"Fallback selection due to error: {str(e)}",
                    alternatives=[],
                    selection_time=time.time() - start_time
                )
            else:
                raise ValueError(f"Algorithm selection failed and no fallback available: {str(e)}") from e
                
    def _filter_compatible_algorithms(self, 
                                    request: ConsensusRequest, 
                                    available_algorithms: list[str]) -> list[str]:
        """过滤兼容的算法"""
        compatible = []
        
        for algorithm_id in available_algorithms:
            algorithm_info = self.registry.get_algorithm_info(algorithm_id)
            if not algorithm_info:
                continue
                
            # 基本兼容性检查
            capabilities = algorithm_info.capabilities
            
            # 检查参与者数量
            participant_count = len(request.inputs)
            if participant_count < capabilities.min_participants:
                continue
            if capabilities.max_participants and participant_count > capabilities.max_participants:
                continue
                
            # 检查输入类型
            input_types = {type(inp.position).__name__ for inp in request.inputs}
            if not input_types.issubset(capabilities.supported_input_types):
                continue
                
            compatible.append(algorithm_id)
            
        return compatible
        
    def _score_algorithms(self, 
                         request: ConsensusRequest,
                         algorithm_ids: list[str],
                         criteria: SelectionCriteria) -> list[AlgorithmScore]:
        """为算法评分"""
        scores = []
        
        # 准备评估上下文
        all_usage = {
            algo_id: self.registry.get_algorithm_info(algo_id).usage_count
            for algo_id in algorithm_ids
            if self.registry.get_algorithm_info(algo_id)
        }
        
        context = {
            "all_algorithm_usage": all_usage,
            "request": request,
            "criteria": criteria
        }
        
        for algorithm_id in algorithm_ids:
            algorithm_info = self.registry.get_algorithm_info(algorithm_id)
            if not algorithm_info:
                continue
                
            # 计算各维度评分
            compatibility_score = self.rules["compatibility"].evaluate(request, algorithm_info, context)
            performance_score = self.rules["performance"].evaluate(request, algorithm_info, context)
            accuracy_score = self.rules["accuracy"].evaluate(request, algorithm_info, context)
            availability_score = self.rules["availability"].evaluate(request, algorithm_info, context)
            load_score = self.rules["load_balance"].evaluate(request, algorithm_info, context)
            
            # 计算总分
            total_score = (
                compatibility_score * criteria.compatibility_weight +
                performance_score * criteria.performance_weight +
                accuracy_score * criteria.accuracy_weight +
                availability_score * criteria.availability_weight +
                load_score * criteria.load_balance_factor
            )
            
            # 应用最小置信度阈值
            if total_score < criteria.min_confidence_threshold:
                total_score *= 0.5  # 惩罚低置信度
                
            algorithm_score = AlgorithmScore(
                algorithm_id=algorithm_id,
                total_score=total_score,
                performance_score=performance_score,
                accuracy_score=accuracy_score,
                availability_score=availability_score,
                compatibility_score=compatibility_score,
                load_score=load_score,
                reasoning={
                    "compatibility": self.rules["compatibility"].get_reasoning(),
                    "performance": self.rules["performance"].get_reasoning(),
                    "accuracy": self.rules["accuracy"].get_reasoning(),
                    "availability": self.rules["availability"].get_reasoning(),
                    "load_balance": self.rules["load_balance"].get_reasoning()
                }
            )
            
            scores.append(algorithm_score)
            
        # 按总分排序
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        return scores    
    def _select_best_algorithm(self, 
                              algorithm_scores: list[AlgorithmScore],
                              strategy: SelectionStrategy) -> AlgorithmScore:
        """选择最佳算法"""
        if not algorithm_scores:
            raise ValueError("No algorithm scores available")
            
        if strategy == SelectionStrategy.LOAD_BALANCED:
            # 负载均衡策略：在前几名中选择负载最低的
            top_candidates = algorithm_scores[:min(3, len(algorithm_scores))]
            return max(top_candidates, key=lambda x: x.load_score)
        else:
            # 其他策略：选择总分最高的
            return algorithm_scores[0]
            
    def _generate_reasoning(self, 
                           best_algorithm: AlgorithmScore,
                           all_scores: list[AlgorithmScore],
                           strategy: SelectionStrategy,
                           criteria: SelectionCriteria) -> str:
        """生成选择理由"""
        reasoning_parts = [
            f"选择策略: {strategy.value}",
            f"总评分: {best_algorithm.total_score:.3f}",
            "",
            "详细评分:",
            f"- 兼容性 ({criteria.compatibility_weight:.1%}): {best_algorithm.compatibility_score:.3f}",
            f"- 性能 ({criteria.performance_weight:.1%}): {best_algorithm.performance_score:.3f}",
            f"- 准确性 ({criteria.accuracy_weight:.1%}): {best_algorithm.accuracy_score:.3f}",
            f"- 可用性 ({criteria.availability_weight:.1%}): {best_algorithm.availability_score:.3f}"
        ]
        
        if criteria.load_balance_factor > 0:
            reasoning_parts.append(f"- 负载均衡 ({criteria.load_balance_factor:.1%}): {best_algorithm.load_score:.3f}")
            
        reasoning_parts.extend([
            "",
            "评估详情:",
            f"- 兼容性: {best_algorithm.reasoning.get('compatibility', 'N/A')}",
            f"- 性能: {best_algorithm.reasoning.get('performance', 'N/A')}",
            f"- 准确性: {best_algorithm.reasoning.get('accuracy', 'N/A')}",
            f"- 可用性: {best_algorithm.reasoning.get('availability', 'N/A')}"
        ])
        
        if criteria.load_balance_factor > 0:
            reasoning_parts.append(f"- 负载均衡: {best_algorithm.reasoning.get('load_balance', 'N/A')}")
            
        # 添加竞争对手信息
        if len(all_scores) > 1:
            reasoning_parts.extend([
                "",
                "其他候选算法:",
                f"- {all_scores[1].algorithm_id}: {all_scores[1].total_score:.3f}"
            ])
            
            if len(all_scores) > 2:
                reasoning_parts.append(f"- {all_scores[2].algorithm_id}: {all_scores[2].total_score:.3f}")
                
        return "\n".join(reasoning_parts)
        
    def update_selection_strategy(self, 
                                 strategy: SelectionStrategy,
                                 criteria: Optional[SelectionCriteria] = None) -> bool:
        """更新选择策略
        
        Args:
            strategy: 新的选择策略
            criteria: 自定义选择标准（可选）
            
        Returns:
            是否更新成功
        """
        try:
            self.default_strategy = strategy
            
            if criteria:
                self.strategy_configs[strategy] = criteria
                
            logger.info(f"Selection strategy updated to: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update selection strategy: {str(e)}")
            return False
            
    def add_custom_rule(self, rule_name: str, rule: SelectionRule) -> bool:
        """添加自定义评估规则
        
        Args:
            rule_name: 规则名称
            rule: 规则实例
            
        Returns:
            是否添加成功
        """
        try:
            self.rules[rule_name] = rule
            logger.info(f"Custom rule '{rule_name}' added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom rule '{rule_name}': {str(e)}")
            return False
            
    def get_selection_reasoning(self, selection: AlgorithmSelection) -> str:
        """获取选择推理过程
        
        Args:
            selection: 算法选择结果
            
        Returns:
            详细的推理说明
        """
        return selection.reasoning
        
    def get_algorithm_scores(self, 
                           request: ConsensusRequest,
                           available_algorithms: Optional[list[str]] = None,
                           strategy: Optional[SelectionStrategy] = None,
                           criteria: Optional[SelectionCriteria] = None) -> list[AlgorithmScore]:
        """获取所有算法的详细评分（用于分析和调试）
        
        Args:
            request: 共识请求
            available_algorithms: 可用算法列表
            strategy: 选择策略
            criteria: 选择标准
            
        Returns:
            算法评分列表
        """
        try:
            strategy = strategy or self.default_strategy
            criteria = criteria or self.strategy_configs.get(strategy, self.default_criteria)
            
            if available_algorithms is None:
                available_algorithms = self.registry.get_healthy_algorithms()
                
            compatible_algorithms = self._filter_compatible_algorithms(request, available_algorithms)
            
            return self._score_algorithms(request, compatible_algorithms, criteria)
            
        except Exception as e:
            logger.error(f"Failed to get algorithm scores: {str(e)}")
            return []
            
    def get_selection_stats(self) -> dict[str, Any]:
        """获取选择器统计信息
        
        Returns:
            统计信息字典
        """
        registry_stats = self.registry.get_registry_stats()
        
        return {
            "current_strategy": self.default_strategy.value,
            "available_algorithms": registry_stats.total_algorithms,
            "healthy_algorithms": registry_stats.healthy_algorithms,
            "available_rules": list(self.rules.keys()),
            "strategy_configs": {
                strategy.value: {
                    "performance_weight": config.performance_weight,
                    "accuracy_weight": config.accuracy_weight,
                    "availability_weight": config.availability_weight,
                    "compatibility_weight": config.compatibility_weight,
                    "load_balance_factor": config.load_balance_factor
                }
                for strategy, config in self.strategy_configs.items()
            }
        }
        
    def validate_request_compatibility(self, request: ConsensusRequest) -> dict[str, list[str]]:
        """验证请求与所有算法的兼容性
        
        Args:
            request: 共识请求
            
        Returns:
            兼容性报告
        """
        all_algorithms = self.registry.get_algorithm_ids()
        
        compatible = []
        incompatible = []
        reasons = {}
        
        for algorithm_id in all_algorithms:
            algorithm_info = self.registry.get_algorithm_info(algorithm_id)
            if not algorithm_info:
                incompatible.append(algorithm_id)
                reasons[algorithm_id] = "Algorithm info not found"
                continue
                
            capabilities = algorithm_info.capabilities
            incompatible_reasons = []
            
            # 检查参与者数量
            participant_count = len(request.inputs)
            if participant_count < capabilities.min_participants:
                incompatible_reasons.append(f"需要至少 {capabilities.min_participants} 个参与者，实际 {participant_count}")
            if capabilities.max_participants and participant_count > capabilities.max_participants:
                incompatible_reasons.append(f"最多支持 {capabilities.max_participants} 个参与者，实际 {participant_count}")
                
            # 检查输入类型
            input_types = {type(inp.position).__name__ for inp in request.inputs}
            unsupported_types = input_types - capabilities.supported_input_types
            if unsupported_types:
                incompatible_reasons.append(f"不支持的输入类型: {unsupported_types}")
                
            # 检查特殊要求
            if capabilities.requires_reasoning:
                missing_reasoning = [i for i, inp in enumerate(request.inputs) if not inp.reasoning]
                if missing_reasoning:
                    incompatible_reasons.append(f"缺少推理信息的输入: {missing_reasoning}")
                    
            if capabilities.requires_evidence:
                missing_evidence = [i for i, inp in enumerate(request.inputs) if not inp.evidence]
                if missing_evidence:
                    incompatible_reasons.append(f"缺少证据信息的输入: {missing_evidence}")
                    
            if incompatible_reasons:
                incompatible.append(algorithm_id)
                reasons[algorithm_id] = "; ".join(incompatible_reasons)
            else:
                compatible.append(algorithm_id)
                
        return {
            "compatible": compatible,
            "incompatible": incompatible,
            "reasons": reasons,
            "total_algorithms": len(all_algorithms),
            "compatibility_rate": len(compatible) / len(all_algorithms) if all_algorithms else 0.0
        }