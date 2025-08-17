#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降级管理器 (Fallback Manager)

处理算法失败场景，提供多级降级策略和智能重试机制。
确保系统在算法失败时能够优雅降级到可用算法。

核心功能：
1. 多级降级策略管理
2. 优先级链和降级顺序
3. 降级事件记录和分析
4. 智能重试机制
5. 熔断器模式实现

设计原则：
- 优雅降级：算法失败时自动切换到备选方案
- 智能重试：基于失败类型的智能重试策略
- 事件记录：完整的降级事件记录和分析
- 熔断保护：防止级联失败的熔断器机制
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Callable
from collections import defaultdict, deque

from consensus_models import (
    ConsensusRequest, ConsensusResponse, ConsensusResult, FailureContext,
    AlgorithmSelection
)
from consensus_algorithm_interface import ConsensusAlgorithm, ConsensusContext
from algorithm_registry import AlgorithmRegistry
from algorithm_selector import AlgorithmSelector


logger = logging.getLogger(__name__)


class FallbackStrategy(str, Enum):
    """降级策略枚举"""
    SIMPLE_FALLBACK = "simple_fallback"  # 简单降级
    PRIORITY_CHAIN = "priority_chain"    # 优先级链
    SIMILARITY_BASED = "similarity_based"  # 相似性降级
    LOAD_AWARE = "load_aware"           # 负载感知降级
    ADAPTIVE = "adaptive"               # 自适应降级


class RetryStrategy(str, Enum):
    """重试策略枚举"""
    NO_RETRY = "no_retry"
    FIXED_RETRY = "fixed_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE_RETRY = "adaptive_retry"


class CircuitBreakerState(str, Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 关闭状态，正常工作
    OPEN = "open"          # 开启状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复


@dataclass
class FallbackConfig:
    """降级配置"""
    strategy: FallbackStrategy = FallbackStrategy.PRIORITY_CHAIN
    max_fallback_depth: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retry_count: int = 3
    retry_delay_base: float = 1.0
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    exclude_algorithms: Set[str] = field(default_factory=set)


@dataclass
class CircuitBreakerInfo:
    """熔断器信息"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    open_time: Optional[datetime] = None


@dataclass
class FallbackEvent:
    """降级事件"""
    event_id: str
    timestamp: datetime
    original_algorithm: str
    fallback_algorithm: str
    failure_context: FailureContext
    fallback_depth: int
    success: bool
    execution_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class FallbackRule(ABC):
    """降级规则抽象基类"""
    
    @abstractmethod
    def get_fallback_candidates(self,
                               failed_algorithm: str,
                               request: ConsensusRequest,
                               failure_context: FailureContext,
                               available_algorithms: List[str]) -> List[str]:
        """
        获取降级候选算法
        
        Args:
            failed_algorithm: 失败的算法ID
            request: 共识请求
            failure_context: 失败上下文
            available_algorithms: 可用算法列表
            
        Returns:
            降级候选算法列表（按优先级排序）
        """
        pass


class PriorityChainRule(FallbackRule):
    """优先级链降级规则"""
    
    def __init__(self, priority_chains: Dict[str, List[str]]):
        """
        初始化优先级链规则
        
        Args:
            priority_chains: 算法优先级链映射 {algorithm_id: [fallback1, fallback2, ...]}
        """
        self.priority_chains = priority_chains
        
    def get_fallback_candidates(self,
                               failed_algorithm: str,
                               request: ConsensusRequest,
                               failure_context: FailureContext,
                               available_algorithms: List[str]) -> List[str]:
        """基于预定义优先级链获取候选算法"""
        chain = self.priority_chains.get(failed_algorithm, [])
        
        # 过滤可用算法
        candidates = [algo for algo in chain if algo in available_algorithms]
        
        return candidates


class SimilarityBasedRule(FallbackRule):
    """相似性降级规则"""
    
    def __init__(self, registry: AlgorithmRegistry):
        self.registry = registry
        
    def get_fallback_candidates(self,
                               failed_algorithm: str,
                               request: ConsensusRequest,
                               failure_context: FailureContext,
                               available_algorithms: List[str]) -> List[str]:
        """基于算法相似性获取候选算法"""
        failed_info = self.registry.get_algorithm_info(failed_algorithm)
        if not failed_info:
            return available_algorithms[:3]  # 返回前3个可用算法
            
        failed_metadata = failed_info.metadata
        
        # 计算相似性评分
        similarity_scores = []
        for algo_id in available_algorithms:
            if algo_id == failed_algorithm:
                continue
                
            algo_info = self.registry.get_algorithm_info(algo_id)
            if not algo_info:
                continue
                
            similarity = self._calculate_similarity(failed_metadata, algo_info.metadata)
            similarity_scores.append((algo_id, similarity))
            
        # 按相似性排序
        similarity_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [algo_id for algo_id, _ in similarity_scores[:3]]
        
    def _calculate_similarity(self, metadata1, metadata2) -> float:
        """计算算法元数据相似性"""
        similarity = 0.0
        
        # 算法类型相似性
        if metadata1.algorithm_type == metadata2.algorithm_type:
            similarity += 0.4
            
        # 复杂度相似性
        complexity_scores = {"low": 1, "medium": 2, "high": 3}
        c1 = complexity_scores.get(metadata1.complexity, 2)
        c2 = complexity_scores.get(metadata2.complexity, 2)
        complexity_similarity = 1.0 - abs(c1 - c2) / 2.0
        similarity += complexity_similarity * 0.3
        
        # 准确性相似性
        accuracy_diff = abs(metadata1.accuracy - metadata2.accuracy)
        accuracy_similarity = 1.0 - accuracy_diff
        similarity += accuracy_similarity * 0.3
        
        return similarity


class LoadAwareRule(FallbackRule):
    """负载感知降级规则"""
    
    def __init__(self, registry: AlgorithmRegistry):
        self.registry = registry
        
    def get_fallback_candidates(self,
                               failed_algorithm: str,
                               request: ConsensusRequest,
                               failure_context: FailureContext,
                               available_algorithms: List[str]) -> List[str]:
        """基于负载情况获取候选算法"""
        # 获取算法使用统计
        algorithm_loads = []
        for algo_id in available_algorithms:
            if algo_id == failed_algorithm:
                continue
                
            algo_info = self.registry.get_algorithm_info(algo_id)
            if algo_info:
                # 简单的负载评估：使用次数越少，负载越低
                load_score = algo_info.usage_count
                algorithm_loads.append((algo_id, load_score))
                
        # 按负载排序（负载低的优先）
        algorithm_loads.sort(key=lambda x: x[1])
        
        return [algo_id for algo_id, _ in algorithm_loads[:3]]


class FallbackManager:
    """
    降级管理器
    
    处理算法失败场景，提供多级降级策略和智能重试机制。
    """
    
    def __init__(self,
                 registry: AlgorithmRegistry,
                 selector: AlgorithmSelector,
                 config: Optional[FallbackConfig] = None):
        self.registry = registry
        self.selector = selector
        self.config = config or FallbackConfig()
        
        # 降级规则
        self.rules: Dict[FallbackStrategy, FallbackRule] = {}
        self._initialize_rules()
        
        # 熔断器状态
        self.circuit_breakers: Dict[str, CircuitBreakerInfo] = defaultdict(CircuitBreakerInfo)
        
        # 事件记录
        self.fallback_events: deque = deque(maxlen=1000)
        self.event_listeners: List[Callable[[FallbackEvent], None]] = []
        
        # 统计信息
        self.stats = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "circuit_breaker_trips": 0
        }
        
        logger.info("FallbackManager initialized")
        
    def _initialize_rules(self):
        """初始化降级规则"""
        # 默认优先级链
        default_chains = {
            "accurate_algo": ["balanced_algo", "fast_algo"],
            "balanced_algo": ["fast_algo", "simple_majority"],
            "fast_algo": ["simple_majority"],
            "bayesian_consensus": ["weighted_voting", "simple_majority"],
            "weighted_voting": ["simple_majority"],
            "cognitive_diversity_preserving": ["weighted_voting", "simple_majority"]
        }
        
        self.rules[FallbackStrategy.PRIORITY_CHAIN] = PriorityChainRule(default_chains)
        self.rules[FallbackStrategy.SIMILARITY_BASED] = SimilarityBasedRule(self.registry)
        self.rules[FallbackStrategy.LOAD_AWARE] = LoadAwareRule(self.registry)
        
    def get_fallback_chain(self,
                          failed_algorithm: str,
                          request: ConsensusRequest,
                          failure_context: Optional[FailureContext] = None) -> List[str]:
        """
        获取降级链
        
        Args:
            failed_algorithm: 失败的算法ID
            request: 共识请求
            failure_context: 失败上下文
            
        Returns:
            降级算法链
        """
        try:
            # 获取可用算法（排除失败算法和被排除的算法）
            available_algorithms = [
                algo_id for algo_id in self.registry.get_healthy_algorithms()
                if algo_id != failed_algorithm and algo_id not in self.config.exclude_algorithms
            ]
            
            if not available_algorithms:
                logger.warning("No available algorithms for fallback")
                return []
                
            # 应用熔断器过滤
            if self.config.circuit_breaker_enabled:
                available_algorithms = self._filter_circuit_breaker_algorithms(available_algorithms)
                
            if not available_algorithms:
                logger.warning("All algorithms are circuit broken")
                return []
                
            # 使用降级规则获取候选算法
            rule = self.rules.get(self.config.strategy)
            if rule:
                candidates = rule.get_fallback_candidates(
                    failed_algorithm, request, failure_context or FailureContext(
                        failed_algorithm=failed_algorithm,
                        error_type="unknown",
                        error_message="No failure context provided",
                        execution_time=0.0
                    ), available_algorithms
                )
            else:
                # 默认策略：使用算法选择器
                candidates = self._get_selector_based_candidates(request, available_algorithms)
                
            # 限制降级深度
            return candidates[:self.config.max_fallback_depth]
            
        except Exception as e:
            logger.error(f"Failed to get fallback chain: {str(e)}")
            return []
            
    def _filter_circuit_breaker_algorithms(self, algorithms: List[str]) -> List[str]:
        """过滤熔断器开启的算法"""
        filtered = []
        current_time = datetime.now()
        
        for algo_id in algorithms:
            breaker = self.circuit_breakers[algo_id]
            
            if breaker.state == CircuitBreakerState.CLOSED:
                filtered.append(algo_id)
            elif breaker.state == CircuitBreakerState.HALF_OPEN:
                filtered.append(algo_id)  # 半开状态允许尝试
            elif breaker.state == CircuitBreakerState.OPEN:
                # 检查是否可以转为半开状态
                if (breaker.open_time and 
                    current_time - breaker.open_time >= timedelta(seconds=self.config.recovery_timeout)):
                    breaker.state = CircuitBreakerState.HALF_OPEN
                    filtered.append(algo_id)
                    logger.info(f"Circuit breaker for {algo_id} moved to HALF_OPEN")
                    
        return filtered
        
    def _get_selector_based_candidates(self, request: ConsensusRequest, available_algorithms: List[str]) -> List[str]:
        """基于选择器获取候选算法"""
        try:
            # 获取算法评分
            scores = self.selector.get_algorithm_scores(request, available_algorithms)
            return [score.algorithm_id for score in scores[:self.config.max_fallback_depth]]
        except Exception as e:
            logger.error(f"Selector-based candidate selection failed: {str(e)}")
            return available_algorithms[:self.config.max_fallback_depth]
            
    async def execute_fallback(self,
                              fallback_algorithm: str,
                              request: ConsensusRequest,
                              failure_context: FailureContext,
                              fallback_depth: int = 1) -> ConsensusResponse:
        """
        执行降级算法
        
        Args:
            fallback_algorithm: 降级算法ID
            request: 共识请求
            failure_context: 失败上下文
            fallback_depth: 降级深度
            
        Returns:
            共识响应
        """
        start_time = time.time()
        event_id = f"fallback_{int(time.time() * 1000)}"
        
        try:
            # 检查熔断器状态
            if not self._check_circuit_breaker(fallback_algorithm):
                raise RuntimeError(f"Circuit breaker is OPEN for algorithm {fallback_algorithm}")
                
            # 获取算法实例
            algorithm = self.registry.get_algorithm(fallback_algorithm)
            if not algorithm:
                raise ValueError(f"Fallback algorithm {fallback_algorithm} not found")
                
            # 执行算法（带重试）
            result = await self._execute_with_retry(algorithm, request, fallback_algorithm)
            
            # 记录成功
            self._record_circuit_breaker_success(fallback_algorithm)
            
            # 创建响应
            response = ConsensusResponse(
                success=True,
                result=result,
                algorithm_used=fallback_algorithm,
                execution_time=time.time() - start_time,
                fallback_used=True,
                timestamp=datetime.now()
            )
            
            # 记录降级事件
            self._record_fallback_event(
                event_id=event_id,
                original_algorithm=failure_context.failed_algorithm,
                fallback_algorithm=fallback_algorithm,
                failure_context=failure_context,
                fallback_depth=fallback_depth,
                success=True,
                execution_time=response.execution_time
            )
            
            self.stats["total_fallbacks"] += 1
            self.stats["successful_fallbacks"] += 1
            
            logger.info(f"Fallback successful: {fallback_algorithm} (depth: {fallback_depth})")
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # 记录失败
            self._record_circuit_breaker_failure(fallback_algorithm)
            
            # 记录降级事件
            self._record_fallback_event(
                event_id=event_id,
                original_algorithm=failure_context.failed_algorithm,
                fallback_algorithm=fallback_algorithm,
                failure_context=failure_context,
                fallback_depth=fallback_depth,
                success=False,
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
            
            self.stats["total_fallbacks"] += 1
            self.stats["failed_fallbacks"] += 1
            
            logger.error(f"Fallback failed: {fallback_algorithm} - {str(e)}")
            
            # 创建失败响应
            return ConsensusResponse(
                success=False,
                result=None,
                algorithm_used=fallback_algorithm,
                execution_time=execution_time,
                error=f"Fallback execution failed: {str(e)}",
                fallback_used=True,
                timestamp=datetime.now()
            )
            
    async def _execute_with_retry(self,
                                 algorithm: ConsensusAlgorithm,
                                 request: ConsensusRequest,
                                 algorithm_id: str) -> ConsensusResult:
        """带重试的算法执行"""
        last_exception = None
        
        for attempt in range(self.config.max_retry_count + 1):
            try:
                # 创建执行上下文
                context = ConsensusContext(
                    session_id=f"fallback_{algorithm_id}_{attempt}",
                    services={},
                    configuration={}
                )
                
                # 执行算法
                result = await algorithm.calculate(request.inputs, context)
                
                if attempt > 0:
                    logger.info(f"Algorithm {algorithm_id} succeeded on retry {attempt}")
                    
                return result
                
            except Exception as e:
                last_exception = e
                
                if attempt < self.config.max_retry_count:
                    # 计算重试延迟
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(f"Algorithm {algorithm_id} failed on attempt {attempt + 1}, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Algorithm {algorithm_id} failed after {self.config.max_retry_count + 1} attempts")
                    
        # 所有重试都失败了
        raise last_exception
        
    def _calculate_retry_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        if self.config.retry_strategy == RetryStrategy.NO_RETRY:
            return 0.0
        elif self.config.retry_strategy == RetryStrategy.FIXED_RETRY:
            return self.config.retry_delay_base
        elif self.config.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return self.config.retry_delay_base * (2 ** attempt)
        elif self.config.retry_strategy == RetryStrategy.ADAPTIVE_RETRY:
            # 自适应延迟：基于历史失败率调整
            base_delay = self.config.retry_delay_base * (2 ** attempt)
            # 这里可以添加更复杂的自适应逻辑
            return base_delay
        else:
            return self.config.retry_delay_base
            
    def _check_circuit_breaker(self, algorithm_id: str) -> bool:
        """检查熔断器状态"""
        if not self.config.circuit_breaker_enabled:
            return True
            
        breaker = self.circuit_breakers[algorithm_id]
        return breaker.state != CircuitBreakerState.OPEN
        
    def _record_circuit_breaker_success(self, algorithm_id: str):
        """记录熔断器成功"""
        if not self.config.circuit_breaker_enabled:
            return
            
        breaker = self.circuit_breakers[algorithm_id]
        breaker.last_success_time = datetime.now()
        
        if breaker.state == CircuitBreakerState.HALF_OPEN:
            # 半开状态成功，转为关闭状态
            breaker.state = CircuitBreakerState.CLOSED
            breaker.failure_count = 0
            logger.info(f"Circuit breaker for {algorithm_id} moved to CLOSED")
            
    def _record_circuit_breaker_failure(self, algorithm_id: str):
        """记录熔断器失败"""
        if not self.config.circuit_breaker_enabled:
            return
            
        breaker = self.circuit_breakers[algorithm_id]
        breaker.failure_count += 1
        breaker.last_failure_time = datetime.now()
        
        if breaker.failure_count >= self.config.failure_threshold:
            if breaker.state != CircuitBreakerState.OPEN:
                breaker.state = CircuitBreakerState.OPEN
                breaker.open_time = datetime.now()
                self.stats["circuit_breaker_trips"] += 1
                logger.warning(f"Circuit breaker for {algorithm_id} moved to OPEN")
                
    def _record_fallback_event(self,
                              event_id: str,
                              original_algorithm: str,
                              fallback_algorithm: str,
                              failure_context: FailureContext,
                              fallback_depth: int,
                              success: bool,
                              execution_time: float,
                              metadata: Optional[Dict[str, Any]] = None):
        """记录降级事件"""
        event = FallbackEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            original_algorithm=original_algorithm,
            fallback_algorithm=fallback_algorithm,
            failure_context=failure_context,
            fallback_depth=fallback_depth,
            success=success,
            execution_time=execution_time,
            metadata=metadata or {}
        )
        
        self.fallback_events.append(event)
        
        # 通知监听器
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Event listener failed: {str(e)}")
                
    def update_fallback_strategy(self,
                                strategy: FallbackStrategy,
                                config: Optional[FallbackConfig] = None) -> bool:
        """
        更新降级策略
        
        Args:
            strategy: 新的降级策略
            config: 新的配置（可选）
            
        Returns:
            是否更新成功
        """
        try:
            if config:
                self.config = config
            else:
                self.config.strategy = strategy
                
            logger.info(f"Fallback strategy updated to: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update fallback strategy: {str(e)}")
            return False

    def add_priority_chain(self, algorithm_id: str, fallback_chain: List[str]) -> bool:
        """
        添加算法优先级链
        
        Args:
            algorithm_id: 算法ID
            fallback_chain: 降级链
            
        Returns:
            是否添加成功
        """
        try:
            priority_rule = self.rules.get(FallbackStrategy.PRIORITY_CHAIN)
            if isinstance(priority_rule, PriorityChainRule):
                priority_rule.priority_chains[algorithm_id] = fallback_chain
                logger.info(f"Priority chain added for {algorithm_id}: {fallback_chain}")
                return True
            else:
                logger.error("Priority chain rule not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add priority chain: {str(e)}")
            return False
            
    def add_event_listener(self, listener: Callable[[FallbackEvent], None]):
        """添加事件监听器"""
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[FallbackEvent], None]):
        """移除事件监听器"""
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            
    def get_fallback_stats(self) -> Dict[str, Any]:
        """
        获取降级统计信息
        
        Returns:
            统计信息字典
        """
        # 计算成功率
        total = self.stats["total_fallbacks"]
        success_rate = (self.stats["successful_fallbacks"] / total) if total > 0 else 0.0
        
        # 统计熔断器状态
        circuit_breaker_stats = {}
        for algo_id, breaker in self.circuit_breakers.items():
            circuit_breaker_stats[algo_id] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
                "last_success": breaker.last_success_time.isoformat() if breaker.last_success_time else None
            }
            
        # 统计最近事件
        recent_events = list(self.fallback_events)[-10:]  # 最近10个事件
        event_summary = []
        for event in recent_events:
            event_summary.append({
                "timestamp": event.timestamp.isoformat(),
                "original_algorithm": event.original_algorithm,
                "fallback_algorithm": event.fallback_algorithm,
                "success": event.success,
                "depth": event.fallback_depth
            })
            
        return {
            "total_fallbacks": total,
            "successful_fallbacks": self.stats["successful_fallbacks"],
            "failed_fallbacks": self.stats["failed_fallbacks"],
            "success_rate": success_rate,
            "circuit_breaker_trips": self.stats["circuit_breaker_trips"],
            "circuit_breakers": circuit_breaker_stats,
            "recent_events": event_summary,
            "config": {
                "strategy": self.config.strategy.value,
                "max_fallback_depth": self.config.max_fallback_depth,
                "retry_strategy": self.config.retry_strategy.value,
                "max_retry_count": self.config.max_retry_count,
                "circuit_breaker_enabled": self.config.circuit_breaker_enabled,
                "failure_threshold": self.config.failure_threshold
            }
        }
        
    def get_algorithm_reliability(self, algorithm_id: str) -> Dict[str, Any]:
        """
        获取算法可靠性信息
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            可靠性信息
        """
        breaker = self.circuit_breakers[algorithm_id]
        
        # 统计该算法相关的降级事件
        algorithm_events = [
            event for event in self.fallback_events
            if event.original_algorithm == algorithm_id or event.fallback_algorithm == algorithm_id
        ]
        
        # 作为原始算法的失败次数
        original_failures = len([
            event for event in algorithm_events
            if event.original_algorithm == algorithm_id
        ])
        
        # 作为降级算法的成功次数
        fallback_successes = len([
            event for event in algorithm_events
            if event.fallback_algorithm == algorithm_id and event.success
        ])
        
        # 作为降级算法的失败次数
        fallback_failures = len([
            event for event in algorithm_events
            if event.fallback_algorithm == algorithm_id and not event.success
        ])
        
        # 计算可靠性评分
        total_uses = original_failures + fallback_successes + fallback_failures
        if total_uses > 0:
            reliability_score = (fallback_successes) / total_uses
        else:
            reliability_score = 1.0  # 没有使用记录时默认为可靠
            
        return {
            "algorithm_id": algorithm_id,
            "circuit_breaker_state": breaker.state.value,
            "failure_count": breaker.failure_count,
            "original_failures": original_failures,
            "fallback_successes": fallback_successes,
            "fallback_failures": fallback_failures,
            "reliability_score": reliability_score,
            "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
            "last_success": breaker.last_success_time.isoformat() if breaker.last_success_time else None
        }
        
    def reset_circuit_breaker(self, algorithm_id: str) -> bool:
        """
        重置算法的熔断器
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            是否重置成功
        """
        try:
            if algorithm_id in self.circuit_breakers:
                breaker = self.circuit_breakers[algorithm_id]
                breaker.state = CircuitBreakerState.CLOSED
                breaker.failure_count = 0
                breaker.open_time = None
                logger.info(f"Circuit breaker for {algorithm_id} has been reset")
                return True
            else:
                logger.warning(f"No circuit breaker found for {algorithm_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reset circuit breaker for {algorithm_id}: {str(e)}")
            return False
            
    def clear_event_history(self):
        """清空事件历史"""
        self.fallback_events.clear()
        logger.info("Fallback event history cleared")
        
    def export_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        导出降级事件
        
        Args:
            limit: 导出数量限制
            
        Returns:
            事件列表
        """
        events = list(self.fallback_events)
        if limit:
            events = events[-limit:]
            
        exported_events = []
        for event in events:
            exported_events.append({
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "original_algorithm": event.original_algorithm,
                "fallback_algorithm": event.fallback_algorithm,
                "failure_context": {
                    "failed_algorithm": event.failure_context.failed_algorithm,
                    "error_type": event.failure_context.error_type,
                    "error_message": event.failure_context.error_message,
                    "execution_time": event.failure_context.execution_time,
                    "retry_count": event.failure_context.retry_count
                },
                "fallback_depth": event.fallback_depth,
                "success": event.success,
                "execution_time": event.execution_time,
                "metadata": event.metadata
            })
            
        return exported_events
        
    def analyze_failure_patterns(self) -> Dict[str, Any]:
        """
        分析失败模式
        
        Returns:
            失败模式分析结果
        """
        if not self.fallback_events:
            return {"message": "No events to analyze"}
            
        # 统计各算法的失败频率
        algorithm_failures = defaultdict(int)
        error_types = defaultdict(int)
        failure_times = []
        
        for event in self.fallback_events:
            if not event.success:
                algorithm_failures[event.fallback_algorithm] += 1
                error_types[event.failure_context.error_type] += 1
                failure_times.append(event.timestamp)
                
        # 分析失败时间模式
        if failure_times:
            failure_times.sort()
            time_intervals = []
            for i in range(1, len(failure_times)):
                interval = (failure_times[i] - failure_times[i-1]).total_seconds()
                time_intervals.append(interval)
                
            avg_interval = sum(time_intervals) / len(time_intervals) if time_intervals else 0
        else:
            avg_interval = 0
            
        # 找出最不可靠的算法
        most_unreliable = max(algorithm_failures.items(), key=lambda x: x[1]) if algorithm_failures else None
        
        # 找出最常见的错误类型
        most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else None
        
        return {
            "total_events": len(self.fallback_events),
            "algorithm_failures": dict(algorithm_failures),
            "error_types": dict(error_types),
            "most_unreliable_algorithm": most_unreliable[0] if most_unreliable else None,
            "most_common_error_type": most_common_error[0] if most_common_error else None,
            "average_failure_interval_seconds": avg_interval,
            "analysis_timestamp": datetime.now().isoformat()
        }