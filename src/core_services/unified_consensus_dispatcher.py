#!/usr/bin/env python3
"""统一共识调度器核心模块

提供统一的共识计算调度入口，集成算法注册表、选择器和降级管理器。
实现异步共识计算的核心流程，支持请求路由和负载均衡。

文件长度限制: <400行
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from algorithm_registry import AlgorithmRegistry
from algorithm_selector import AlgorithmSelector, SelectionStrategy
from consensus_models import AlgorithmSelection, ConsensusRequest, ConsensusResponse, FailureContext
from fallback_manager_core import FallbackConfig, FallbackManager

logger = logging.getLogger(__name__)


@dataclass
class DispatcherConfig:
    """调度器配置"""
    default_timeout: float = 30.0
    max_concurrent_requests: int = 100
    enable_load_balancing: bool = True
    enable_metrics_collection: bool = True
    enable_request_logging: bool = True
    fallback_enabled: bool = True
    selection_strategy: SelectionStrategy = SelectionStrategy.BALANCED


@dataclass
class DispatcherMetrics:
    """调度器指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    fallback_requests: int = 0
    average_response_time: float = 0.0
    active_requests: int = 0
    algorithm_usage: dict[str, int] = field(default_factory=dict)
    error_counts: dict[str, int] = field(default_factory=dict)


class RequestContext:
    """请求上下文"""
    
    def __init__(self, request_id: str, request: ConsensusRequest):
        self.request_id = request_id
        self.request = request
        self.start_time = time.time()
        self.selected_algorithm = None
        self.fallback_used = False
        self.attempts = []
        self.metadata = {}


class UnifiedConsensusDispatcher:
    """统一共识调度器
    
    提供统一的共识计算入口，协调算法选择、执行和降级。
    """
    
    def __init__(self, 
                 config: Optional[DispatcherConfig] = None):
        self.config = config or DispatcherConfig()
        
        # 核心组件
        self.registry = AlgorithmRegistry()
        self.selector = AlgorithmSelector(self.registry, self.config.selection_strategy)
        
        # 降级管理器（如果启用）
        if self.config.fallback_enabled:
            fallback_config = FallbackConfig()
            self.fallback_manager = FallbackManager(self.registry, self.selector, fallback_config)
        else:
            self.fallback_manager = None
            
        # 指标和状态
        self.metrics = DispatcherMetrics()
        self.active_requests: dict[str, RequestContext] = {}
        self.request_counter = 0
        
        # 并发控制
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        logger.info("UnifiedConsensusDispatcher initialized")
        
    async def calculate_consensus(self, request: ConsensusRequest) -> ConsensusResponse:
        """计算共识 - 主要入口点
        
        Args:
            request: 共识请求
            
        Returns:
            共识响应
        """
        # 生成请求ID
        request_id = f"req_{int(time.time() * 1000)}_{self.request_counter}"
        self.request_counter += 1
        
        # 创建请求上下文
        context = RequestContext(request_id, request)
        
        # 并发控制
        async with self.semaphore:
            try:
                # 记录请求开始
                self._record_request_start(context)
                
                # 执行共识计算
                response = await self._execute_consensus(context)
                
                # 记录请求完成
                self._record_request_completion(context, response)
                
                return response
                
            except Exception as e:
                # 记录请求失败
                error_response = ConsensusResponse(
                    success=False,
                    result=None,
                    algorithm_used="unknown",
                    execution_time=time.time() - context.start_time,
                    error=f"Dispatcher error: {str(e)}",
                    fallback_used=False,
                    timestamp=datetime.now()
                )
                
                self._record_request_completion(context, error_response)
                
                logger.error(f"Request {request_id} failed: {str(e)}")
                return error_response
                
            finally:
                # 清理请求上下文
                if request_id in self.active_requests:
                    del self.active_requests[request_id]
                    
    async def _execute_consensus(self, context: RequestContext) -> ConsensusResponse:
        """执行共识计算的核心逻辑
        
        Args:
            context: 请求上下文
            
        Returns:
            共识响应
        """
        request = context.request
        
        try:
            # 1. 算法选择
            selection = await self._select_algorithm(request)
            context.selected_algorithm = selection.algorithm_id
            context.attempts.append({
                "algorithm": selection.algorithm_id,
                "selection_time": selection.selection_time,
                "confidence": selection.confidence
            })
            
            # 2. 执行算法
            response = await self._execute_algorithm(selection.algorithm_id, request)
            
            if response.success:
                return response
            else:
                # 3. 如果失败且启用降级，尝试降级
                if self.config.fallback_enabled and self.fallback_manager:
                    return await self._handle_algorithm_failure(context, response)
                else:
                    return response
                    
        except Exception as e:
            logger.error(f"Consensus execution failed: {str(e)}")
            
            # 如果启用降级，尝试降级
            if self.config.fallback_enabled and self.fallback_manager:
                failure_context = FailureContext(
                    failed_algorithm=context.selected_algorithm or "unknown",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    execution_time=time.time() - context.start_time
                )
                return await self._handle_algorithm_failure(context, None, failure_context)
            else:
                # 返回错误响应
                return ConsensusResponse(
                    success=False,
                    result=None,
                    algorithm_used=context.selected_algorithm or "unknown",
                    execution_time=time.time() - context.start_time,
                    error=str(e),
                    fallback_used=False,
                    timestamp=datetime.now()
                )
                
    async def _select_algorithm(self, request: ConsensusRequest) -> AlgorithmSelection:
        """选择算法
        
        Args:
            request: 共识请求
            
        Returns:
            算法选择结果
        """
        try:
            # 应用超时控制
            timeout = getattr(request, 'timeout', self.config.default_timeout)
            
            selection = await asyncio.wait_for(
                asyncio.create_task(self._async_select_algorithm(request)),
                timeout=timeout * 0.1  # 选择阶段使用10%的超时时间
            )
            
            return selection
            
        except asyncio.TimeoutError:
            logger.warning("Algorithm selection timed out, using fallback selection")
            # 超时时使用简单选择策略
            available_algorithms = self.registry.get_healthy_algorithms()
            if available_algorithms:
                return AlgorithmSelection(
                    algorithm_id=available_algorithms[0],
                    confidence=0.5,
                    reasoning="Fallback selection due to timeout",
                    alternatives=[],
                    selection_time=timeout * 0.1
                )
            else:
                raise RuntimeError("No available algorithms for selection")
                
    async def _async_select_algorithm(self, request: ConsensusRequest) -> AlgorithmSelection:
        """异步算法选择
        
        Args:
            request: 共识请求
            
        Returns:
            算法选择结果
        """
        # 在线程池中执行选择逻辑（因为selector是同步的）
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.selector.select_algorithm, 
            request
        )
        
    async def _execute_algorithm(self, algorithm_id: str, request: ConsensusRequest) -> ConsensusResponse:
        """执行指定算法
        
        Args:
            algorithm_id: 算法ID
            request: 共识请求
            
        Returns:
            共识响应
        """
        start_time = time.time()
        
        try:
            # 获取算法实例
            algorithm = self.registry.get_algorithm(algorithm_id)
            if not algorithm:
                raise ValueError(f"Algorithm {algorithm_id} not found")
                
            # 创建执行上下文
            from consensus_algorithm_interface import ConsensusContext
            context = ConsensusContext(
                session_id=f"dispatch_{algorithm_id}_{int(time.time())}",
                services={"registry": self.registry, "selector": self.selector},
                configuration={}
            )
            
            # 应用超时控制
            timeout = getattr(request, 'timeout', self.config.default_timeout)
            
            # 执行算法
            result = await asyncio.wait_for(
                algorithm.calculate(request.inputs, context),
                timeout=timeout
            )
            
            # 创建成功响应
            response = ConsensusResponse(
                success=True,
                result=result,
                algorithm_used=algorithm_id,
                execution_time=time.time() - start_time,
                fallback_used=False,
                timestamp=datetime.now()
            )
            
            return response
            
        except asyncio.TimeoutError:
            error_msg = f"Algorithm {algorithm_id} execution timed out"
            logger.warning(error_msg)
            
            return ConsensusResponse(
                success=False,
                result=None,
                algorithm_used=algorithm_id,
                execution_time=time.time() - start_time,
                error=error_msg,
                fallback_used=False,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Algorithm {algorithm_id} execution failed: {str(e)}"
            logger.error(error_msg)
            
            return ConsensusResponse(
                success=False,
                result=None,
                algorithm_used=algorithm_id,
                execution_time=time.time() - start_time,
                error=error_msg,
                fallback_used=False,
                timestamp=datetime.now()
            )
            
    async def _handle_algorithm_failure(self, 
                                       context: RequestContext, 
                                       failed_response: Optional[ConsensusResponse] = None,
                                       failure_context: Optional[FailureContext] = None) -> ConsensusResponse:
        """处理算法失败，尝试降级
        
        Args:
            context: 请求上下文
            failed_response: 失败的响应（可选）
            failure_context: 失败上下文（可选）
            
        Returns:
            共识响应
        """
        if not self.fallback_manager:
            return failed_response or ConsensusResponse(
                success=False,
                result=None,
                algorithm_used=context.selected_algorithm or "unknown",
                execution_time=time.time() - context.start_time,
                error="Fallback not available",
                fallback_used=False,
                timestamp=datetime.now()
            )
            
        try:
            # 创建失败上下文
            if not failure_context:
                failure_context = FailureContext(
                    failed_algorithm=context.selected_algorithm or "unknown",
                    error_type="ExecutionError",
                    error_message=failed_response.error if failed_response else "Unknown error",
                    execution_time=failed_response.execution_time if failed_response else 0.0
                )
                
            # 获取降级链
            fallback_chain = self.fallback_manager.get_fallback_chain(
                failure_context.failed_algorithm,
                context.request,
                failure_context
            )
            
            if not fallback_chain:
                logger.warning("No fallback algorithms available")
                return failed_response or ConsensusResponse(
                    success=False,
                    result=None,
                    algorithm_used=failure_context.failed_algorithm,
                    execution_time=time.time() - context.start_time,
                    error="No fallback algorithms available",
                    fallback_used=False,
                    timestamp=datetime.now()
                )
                
            # 尝试第一个降级算法
            fallback_algorithm = fallback_chain[0]
            context.fallback_used = True
            
            logger.info(f"Attempting fallback to {fallback_algorithm}")
            
            # 执行降级
            fallback_response = await self.fallback_manager.execute_fallback(
                fallback_algorithm,
                context.request,
                failure_context,
                fallback_depth=1
            )
            
            return fallback_response
            
        except Exception as e:
            logger.error(f"Fallback handling failed: {str(e)}")
            
            return ConsensusResponse(
                success=False,
                result=None,
                algorithm_used=context.selected_algorithm or "unknown",
                execution_time=time.time() - context.start_time,
                error=f"Fallback failed: {str(e)}",
                fallback_used=True,
                timestamp=datetime.now()
            )
            
    def _record_request_start(self, context: RequestContext):
        """记录请求开始"""
        self.active_requests[context.request_id] = context
        self.metrics.active_requests = len(self.active_requests)
        
        if self.config.enable_request_logging:
            logger.info(f"Request {context.request_id} started")
            
    def _record_request_completion(self, context: RequestContext, response: ConsensusResponse):
        """记录请求完成"""
        # 更新指标
        self.metrics.total_requests += 1
        
        if response.success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            
            # 记录错误类型
            error_type = "unknown"
            if response.error:
                if "timeout" in response.error.lower():
                    error_type = "timeout"
                elif "not found" in response.error.lower():
                    error_type = "algorithm_not_found"
                elif "circuit breaker" in response.error.lower():
                    error_type = "circuit_breaker"
                else:
                    error_type = "execution_error"
                    
            self.metrics.error_counts[error_type] = self.metrics.error_counts.get(error_type, 0) + 1
            
        if response.fallback_used:
            self.metrics.fallback_requests += 1
            
        # 更新算法使用统计
        algorithm_used = response.algorithm_used
        self.metrics.algorithm_usage[algorithm_used] = self.metrics.algorithm_usage.get(algorithm_used, 0) + 1
        
        # 更新平均响应时间
        if self.metrics.total_requests > 0:
            total_time = (self.metrics.average_response_time * (self.metrics.total_requests - 1) + 
                         response.execution_time)
            self.metrics.average_response_time = total_time / self.metrics.total_requests
            
        # 更新活跃请求数
        self.metrics.active_requests = len(self.active_requests)
        
        if self.config.enable_request_logging:
            status = "SUCCESS" if response.success else "FAILED"
            logger.info(f"Request {context.request_id} completed: {status} "
                       f"(algorithm: {algorithm_used}, time: {response.execution_time:.3f}s)")
                       
    def get_health_status(self) -> dict[str, Any]:
        """获取调度器健康状态
        
        Returns:
            健康状态信息
        """
        registry_stats = self.registry.get_registry_stats()
        
        # 计算健康评分
        health_score = 1.0
        
        # 基于算法可用性
        if registry_stats.total_algorithms == 0:
            health_score = 0.0
        else:
            algorithm_health_ratio = registry_stats.healthy_algorithms / registry_stats.total_algorithms
            health_score *= algorithm_health_ratio
            
        # 基于成功率
        if self.metrics.total_requests > 0:
            success_rate = self.metrics.successful_requests / self.metrics.total_requests
            health_score *= success_rate
            
        # 确定健康状态
        if health_score >= 0.8:
            status = "healthy"
        elif health_score >= 0.5:
            status = "degraded"
        else:
            status = "unhealthy"
            
        return {
            "status": status,
            "health_score": health_score,
            "total_algorithms": registry_stats.total_algorithms,
            "healthy_algorithms": registry_stats.healthy_algorithms,
            "total_requests": self.metrics.total_requests,
            "success_rate": self.metrics.successful_requests / max(self.metrics.total_requests, 1),
            "active_requests": self.metrics.active_requests,
            "fallback_enabled": self.config.fallback_enabled,
            "timestamp": datetime.now().isoformat()
        }
        
    async def shutdown(self):
        """关闭调度器"""
        try:
            # 等待所有活跃请求完成（最多等待30秒）
            if self.active_requests:
                logger.info(f"Waiting for {len(self.active_requests)} active requests to complete...")
                
                for _ in range(30):  # 最多等待30秒
                    if not self.active_requests:
                        break
                    await asyncio.sleep(1)
                    
                if self.active_requests:
                    logger.warning(f"Shutting down with {len(self.active_requests)} active requests")
                    
            # 关闭组件
            if hasattr(self.registry, 'shutdown'):
                self.registry.shutdown()
                
            logger.info("UnifiedConsensusDispatcher shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            
    def __str__(self) -> str:
        return f"UnifiedConsensusDispatcher(algorithms={len(self.registry)}, active_requests={len(self.active_requests)})"
        
    def __repr__(self) -> str:
        return (f"UnifiedConsensusDispatcher(config={self.config}, "
                f"algorithms={len(self.registry)}, "
                f"metrics={self.metrics})")