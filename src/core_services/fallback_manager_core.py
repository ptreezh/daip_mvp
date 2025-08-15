#!/usr/bin/env python3
"""降级管理器核心模块

按照新的代码生成规则，将FallbackManager拆分为多个模块。
这是核心模块，包含主要的FallbackManager类。

文件长度限制: <400行
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from algorithm_registry import AlgorithmRegistry
from algorithm_selector import AlgorithmSelector
from consensus_algorithm_interface import ConsensusAlgorithm, ConsensusContext
from consensus_models import ConsensusRequest, ConsensusResponse, ConsensusResult, FailureContext

logger = logging.getLogger(__name__)


class FallbackStrategy(str, Enum):
    """降级策略枚举"""
    SIMPLE_FALLBACK = "simple_fallback"
    PRIORITY_CHAIN = "priority_chain"
    SIMILARITY_BASED = "similarity_based"
    LOAD_AWARE = "load_aware"
    ADAPTIVE = "adaptive"


class RetryStrategy(str, Enum):
    """重试策略枚举"""
    NO_RETRY = "no_retry"
    FIXED_RETRY = "fixed_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE_RETRY = "adaptive_retry"


class CircuitBreakerState(str, Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class FallbackConfig:
    """降级配置"""
    
    def __init__(self,
                 strategy: FallbackStrategy = FallbackStrategy.PRIORITY_CHAIN,
                 max_fallback_depth: int = 3,
                 retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 max_retry_count: int = 3,
                 retry_delay_base: float = 1.0,
                 circuit_breaker_enabled: bool = True,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0):
        self.strategy = strategy
        self.max_fallback_depth = max_fallback_depth
        self.retry_strategy = retry_strategy
        self.max_retry_count = max_retry_count
        self.retry_delay_base = retry_delay_base
        self.circuit_breaker_enabled = circuit_breaker_enabled
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout


class CircuitBreakerInfo:
    """熔断器信息"""
    
    def __init__(self):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.open_time = None


class FallbackEvent:
    """降级事件"""
    
    def __init__(self,
                 event_id: str,
                 timestamp: datetime,
                 original_algorithm: str,
                 fallback_algorithm: str,
                 failure_context: FailureContext,
                 fallback_depth: int,
                 success: bool,
                 execution_time: float,
                 metadata: Optional[dict[str, Any]] = None):
        self.event_id = event_id
        self.timestamp = timestamp
        self.original_algorithm = original_algorithm
        self.fallback_algorithm = fallback_algorithm
        self.failure_context = failure_context
        self.fallback_depth = fallback_depth
        self.success = success
        self.execution_time = execution_time
        self.metadata = metadata or {}


class FallbackManager:
    """降级管理器核心类
    
    处理算法失败场景，提供多级降级策略和智能重试机制。
    """
    
    def __init__(self,
                 registry: AlgorithmRegistry,
                 selector: AlgorithmSelector,
                 config: Optional[FallbackConfig] = None):
        self.registry = registry
        self.selector = selector
        self.config = config or FallbackConfig()
        
        # 熔断器状态
        self.circuit_breakers: dict[str, CircuitBreakerInfo] = defaultdict(CircuitBreakerInfo)
        
        # 事件记录
        self.fallback_events: deque = deque(maxlen=1000)
        self.event_listeners: list[Callable[[FallbackEvent], None]] = []
        
        # 统计信息
        self.stats = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "circuit_breaker_trips": 0
        }
        
        logger.info("FallbackManager initialized")
        
    def get_fallback_chain(self,
                          failed_algorithm: str,
                          request: ConsensusRequest,
                          failure_context: Optional[FailureContext] = None) -> list[str]:
        """获取降级链
        
        Args:
            failed_algorithm: 失败的算法ID
            request: 共识请求
            failure_context: 失败上下文
            
        Returns:
            降级算法链
        """
        try:
            # 获取可用算法（排除失败算法）
            available_algorithms = [
                algo_id for algo_id in self.registry.get_healthy_algorithms()
                if algo_id != failed_algorithm
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
                
            # 使用算法选择器获取候选算法
            candidates = self._get_selector_based_candidates(request, available_algorithms)
                
            # 限制降级深度
            return candidates[:self.config.max_fallback_depth]
            
        except Exception as e:
            logger.error(f"Failed to get fallback chain: {str(e)}")
            return []
            
    def _filter_circuit_breaker_algorithms(self, algorithms: list[str]) -> list[str]:
        """过滤熔断器开启的算法"""
        filtered = []
        current_time = datetime.now()
        
        for algo_id in algorithms:
            breaker = self.circuit_breakers[algo_id]
            
            if breaker.state == CircuitBreakerState.CLOSED:
                filtered.append(algo_id)
            elif breaker.state == CircuitBreakerState.HALF_OPEN:
                filtered.append(algo_id)
            elif breaker.state == CircuitBreakerState.OPEN:
                # 检查是否可以转为半开状态
                if (breaker.open_time and 
                    current_time - breaker.open_time >= timedelta(seconds=self.config.recovery_timeout)):
                    breaker.state = CircuitBreakerState.HALF_OPEN
                    filtered.append(algo_id)
                    logger.info(f"Circuit breaker for {algo_id} moved to HALF_OPEN")
                    
        return filtered
        
    def _get_selector_based_candidates(self, request: ConsensusRequest, available_algorithms: list[str]) -> list[str]:
        """基于选择器获取候选算法"""
        try:
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
        """执行降级算法
        
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
                              metadata: Optional[dict[str, Any]] = None):
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