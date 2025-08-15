#!/usr/bin/env python3
"""统一共识计算调度器

负责协调系统中所有共识计算实现，提供统一的调度入口
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from src.protocols.consensus_strategies import ConsensusStrategyFactory, SimpleMajorityVoteStrategy

from .advanced_consensus_algorithms import (
    BayesianConsensus,
    CognitiveDiversityPreservingConsensus,
    ConsensusInput,
    ConsensusResult,
    WeightedVotingConsensus,
)

logger = logging.getLogger(__name__)


class ConsensusMethod(str, Enum):
    """共识计算方法枚举"""
    SIMPLE_MAJORITY = "simple_majority"
    WEIGHTED_VOTING = "weighted_voting"
    BAYESIAN = "bayesian"
    DIVERSITY_PRESERVING = "diversity_preserving"
    AUTO_SELECT = "auto_select"


class UnifiedConsensusDispatcher:
    """统一共识计算调度器"""
    
    def __init__(self):
        """初始化调度器"""
        self.strategy_factory = ConsensusStrategyFactory()
        self.advanced_algorithms = {}
        self._initialize_algorithms()
        logger.info("统一共识调度器初始化完成")
    
    def _initialize_algorithms(self):
        """初始化所有共识算法"""
        # 注册简单策略
        self.strategy_factory.register("simple_majority_vote", SimpleMajorityVoteStrategy)
        
        # 初始化高级算法
        self.advanced_algorithms = {
            ConsensusMethod.WEIGHTED_VOTING: WeightedVotingConsensus(),
            ConsensusMethod.BAYESIAN: BayesianConsensus(),
            ConsensusMethod.DIVERSITY_PRESERVING: CognitiveDiversityPreservingConsensus()
        }
    
    async def calculate_consensus(
        self,
        inputs: list[dict[str, Any]],
        method: ConsensusMethod = ConsensusMethod.AUTO_SELECT,
        context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """统一的共识计算入口
        
        Args:
            inputs: 输入数据列表
            method: 共识计算方法
            context: 上下文信息
            
        Returns:
            统一格式的共识计算结果
        """
        try:
            logger.info(f"开始共识计算，方法: {method}, 输入数量: {len(inputs)}")
            
            # 自动选择最佳方法
            if method == ConsensusMethod.AUTO_SELECT:
                method = self._select_optimal_method(inputs, context)
                logger.info(f"自动选择方法: {method}")
            
            # 执行共识计算
            if method == ConsensusMethod.SIMPLE_MAJORITY:
                result = await self._execute_simple_majority(inputs)
            else:
                result = await self._execute_advanced_consensus(inputs, method, context)
            
            # 统一结果格式
            unified_result = self._unify_result_format(result, method)
            
            logger.info(f"共识计算完成，方法: {method}, 强度: {unified_result.get('consensus_strength', 0):.2f}")
            return unified_result
            
        except Exception as e:
            logger.error(f"共识计算失败: {e}")
            return {
                "error": str(e),
                "method": method,
                "timestamp": datetime.now().isoformat()
            }
    
    def _select_optimal_method(
        self,
        inputs: list[dict[str, Any]],
        context: Optional[dict[str, Any]] = None
    ) -> ConsensusMethod:
        """自动选择最优的共识计算方法"""
        # 基于输入数量选择
        if len(inputs) <= 3:
            return ConsensusMethod.SIMPLE_MAJORITY
        elif len(inputs) <= 10:
            return ConsensusMethod.WEIGHTED_VOTING
        else:
            return ConsensusMethod.DIVERSITY_PRESERVING
    
    async def _execute_simple_majority(self, inputs: list[dict[str, Any]]) -> dict[str, Any]:
        """执行简单多数投票"""
        # 转换为SimpleMajorityVoteStrategy期望的格式
        from src.models import DebateTurn
        
        # 模拟DebateTurn格式
        debate_turns = []
        for i, input_data in enumerate(inputs):
            turn = DebateTurn(
                role_id=input_data.get("agent_id", f"agent_{i}"),
                opinion=input_data.get("position", ""),
                turn_number=i + 1,
                timestamp=datetime.now()
            )
            debate_turns.append(turn)
        
        # 执行简单多数投票
        strategy = SimpleMajorityVoteStrategy()
        result = strategy.execute(debate_turns)
        
        return {
            "algorithm_type": "simple_majority_vote",
            "consensus_strength": self._calculate_strength_from_votes(result.get("votes", {})),
            "summary": f"多数投票结果: {result.get('outcome', 'unknown')}",
            "confidence": 0.75,
            "details": result
        }
    
    async def _execute_advanced_consensus(
        self,
        inputs: list[dict[str, Any]],
        method: ConsensusMethod,
        context: Optional[dict[str, Any]] = None
    ) -> ConsensusResult:
        """执行高级共识算法"""
        # 转换为ConsensusInput格式
        consensus_inputs = []
        for input_data in inputs:
            consensus_input = ConsensusInput(
                agent_id=input_data.get("agent_id", "unknown"),
                position=input_data.get("position", ""),
                confidence=input_data.get("confidence", 0.5),
                reasoning=input_data.get("reasoning", ""),
                timestamp=datetime.now()
            )
            consensus_inputs.append(consensus_input)
        
        # 获取对应的算法
        algorithm = self.advanced_algorithms.get(method)
        if not algorithm:
            raise ValueError(f"不支持的共识方法: {method}")
        
        # 执行算法
        result = algorithm.calculate_consensus(consensus_inputs, context)
        return result
    
    def _unify_result_format(self, result: Union[dict[str, Any], ConsensusResult], method: ConsensusMethod) -> dict[str, Any]:
        """统一结果格式"""
        if isinstance(result, ConsensusResult):
            # 高级算法结果
            return {
                "algorithm_type": result.algorithm_used.value,
                "consensus_strength": result.confidence_level,
                "summary": f"使用{result.algorithm_used.value}算法完成共识计算",
                "confidence": result.confidence_level,
                "consensus_value": result.consensus_value,
                "participant_count": result.participant_count,
                "diversity_score": result.diversity_score,
                "emergent_insights": result.emergent_insights,
                "timestamp": result.timestamp.isoformat(),
                "method_used": method
            }
        else:
            # 简单算法结果
            return {
                **result,
                "method_used": method,
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_strength_from_votes(self, votes: dict[str, int]) -> float:
        """从投票结果计算共识强度"""
        if not votes:
            return 0.0
        
        total_votes = sum(votes.values())
        if total_votes == 0:
            return 0.0
        
        max_votes = max(votes.values())
        return max_votes / total_votes
    
    def get_available_methods(self) -> list[str]:
        """获取可用的共识计算方法"""
        return [method.value for method in ConsensusMethod]
    
    def get_method_info(self, method: ConsensusMethod) -> dict[str, Any]:
        """获取方法信息"""
        method_info = {
            ConsensusMethod.SIMPLE_MAJORITY: {
                "name": "简单多数投票",
                "description": "基于关键词的简单多数投票",
                "best_for": "小规模、简单决策",
                "complexity": "低"
            },
            ConsensusMethod.WEIGHTED_VOTING: {
                "name": "加权投票",
                "description": "考虑专业度和置信度的加权投票",
                "best_for": "中等规模、需要专业权重",
                "complexity": "中"
            },
            ConsensusMethod.BAYESIAN: {
                "name": "贝叶斯共识",
                "description": "基于贝叶斯推理的共识计算",
                "best_for": "不确定性高、需要概率推理",
                "complexity": "高"
            },
            ConsensusMethod.DIVERSITY_PRESERVING: {
                "name": "多样性保持",
                "description": "保持认知多样性的共识算法",
                "best_for": "大规模、需要保持多元观点",
                "complexity": "高"
            }
        }
        
        return method_info.get(method, {"name": "未知方法"})


# 全局单例实例
_consensus_dispatcher = None

def get_consensus_dispatcher() -> UnifiedConsensusDispatcher:
    """获取全局共识调度器实例"""
    global _consensus_dispatcher
    if _consensus_dispatcher is None:
        _consensus_dispatcher = UnifiedConsensusDispatcher()
    return _consensus_dispatcher