#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 18:15:00
@Author  : DAIP-LIVE Team
@File    : cqs_bus_implementation.py
@Description:
    CQS总线的具体实现
    
    提供CQS模式的核心协调功能：
    - 查询和命令的路由分发
    - 性能监控和指标收集
    - 缓存管理和优化
    - 错误处理和降级
"""

import asyncio
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Type
from datetime import datetime, timedelta
from collections import defaultdict
import weakref

from .cqs_interfaces import (
    ICQSBus, IQueryHandler, ICommandHandler, IQueryCache, ICQSMetrics,
    QuerySpec, CommandSpec, QueryResult, CommandResult,
    QueryResultStatus, CommandResultStatus, CQSConfiguration,
    CQSViolationError, CQSValidator
)

logger = logging.getLogger(__name__)

class CQSMetricsCollector:
    """CQS指标收集器"""
    
    def __init__(self):
        self.query_metrics = defaultdict(list)
        self.command_metrics = defaultdict(list)
        self.cache_metrics = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        self.error_counts = defaultdict(int)
        self.performance_history = []
        self.start_time = datetime.now()
    
    async def record_query_execution(self, query_type: str, execution_time_ms: float, cache_hit: bool):
        """记录查询执行指标"""
        self.query_metrics[query_type].append({
            "execution_time_ms": execution_time_ms,
            "cache_hit": cache_hit,
            "timestamp": datetime.now()
        })
        
        # 更新缓存指标
        self.cache_metrics["total_requests"] += 1
        if cache_hit:
            self.cache_metrics["hits"] += 1
        else:
            self.cache_metrics["misses"] += 1
        
        # 保持历史记录大小
        if len(self.query_metrics[query_type]) > 1000:
            self.query_metrics[query_type] = self.query_metrics[query_type][-500:]
    
    async def record_command_execution(self, command_type: str, execution_time_ms: float, success: bool):
        """记录命令执行指标"""
        self.command_metrics[command_type].append({
            "execution_time_ms": execution_time_ms,
            "success": success,
            "timestamp": datetime.now()
        })
        
        if not success:
            self.error_counts[command_type] += 1
        
        # 保持历史记录大小
        if len(self.command_metrics[command_type]) > 1000:
            self.command_metrics[command_type] = self.command_metrics[command_type][-500:]
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        query_stats = {}
        for query_type, metrics in self.query_metrics.items():
            if metrics:
                execution_times = [m["execution_time_ms"] for m in metrics]
                cache_hits = sum(1 for m in metrics if m["cache_hit"])
                
                query_stats[query_type] = {
                    "total_executions": len(metrics),
                    "avg_execution_time_ms": sum(execution_times) / len(execution_times),
                    "min_execution_time_ms": min(execution_times),
                    "max_execution_time_ms": max(execution_times),
                    "cache_hit_rate": cache_hits / len(metrics),
                    "recent_executions": len([m for m in metrics if (datetime.now() - m["timestamp"]).seconds < 3600])
                }
        
        command_stats = {}
        for command_type, metrics in self.command_metrics.items():
            if metrics:
                execution_times = [m["execution_time_ms"] for m in metrics]
                successes = sum(1 for m in metrics if m["success"])
                
                command_stats[command_type] = {
                    "total_executions": len(metrics),
                    "avg_execution_time_ms": sum(execution_times) / len(execution_times),
                    "min_execution_time_ms": min(execution_times),
                    "max_execution_time_ms": max(execution_times),
                    "success_rate": successes / len(metrics),
                    "error_count": self.error_counts[command_type]
                }
        
        return {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "query_statistics": query_stats,
            "command_statistics": command_stats,
            "cache_statistics": {
                **self.cache_metrics,
                "hit_rate": self.cache_metrics["hits"] / max(self.cache_metrics["total_requests"], 1)
            },
            "total_errors": sum(self.error_counts.values())
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        metrics = await self.get_performance_metrics()
        
        # 健康评分计算
        health_score = 100
        
        # 检查错误率
        total_operations = sum(len(metrics) for metrics in self.query_metrics.values()) + \
                          sum(len(metrics) for metrics in self.command_metrics.values())
        if total_operations > 0:
            error_rate = metrics["total_errors"] / total_operations
            if error_rate > 0.05:  # 5%错误率
                health_score -= 30
            elif error_rate > 0.01:  # 1%错误率
                health_score -= 10
        
        # 检查性能
        avg_query_time = 0
        query_count = 0
        for stats in metrics["query_statistics"].values():
            avg_query_time += stats["avg_execution_time_ms"]
            query_count += 1
        
        if query_count > 0:
            avg_query_time /= query_count
            if avg_query_time > 1000:  # 1秒
                health_score -= 20
            elif avg_query_time > 500:  # 0.5秒
                health_score -= 10
        
        # 检查缓存命中率
        cache_hit_rate = metrics["cache_statistics"]["hit_rate"]
        if cache_hit_rate < 0.3:  # 30%
            health_score -= 15
        elif cache_hit_rate < 0.5:  # 50%
            health_score -= 5
        
        health_status = "healthy"
        if health_score < 50:
            health_status = "unhealthy"
        elif health_score < 80:
            health_status = "degraded"
        
        return {
            "status": health_status,
            "health_score": max(0, health_score),
            "uptime_seconds": metrics["uptime_seconds"],
            "last_check": datetime.now().isoformat(),
            "issues": self._identify_health_issues(metrics)
        }
    
    def _identify_health_issues(self, metrics: Dict[str, Any]) -> List[str]:
        """识别健康问题"""
        issues = []
        
        if metrics["total_errors"] > 10:
            issues.append(f"高错误率: {metrics['total_errors']} 个错误")
        
        cache_hit_rate = metrics["cache_statistics"]["hit_rate"]
        if cache_hit_rate < 0.3:
            issues.append(f"低缓存命中率: {cache_hit_rate:.1%}")
        
        for query_type, stats in metrics["query_statistics"].items():
            if stats["avg_execution_time_ms"] > 500:
                issues.append(f"查询性能问题: {query_type} 平均耗时 {stats['avg_execution_time_ms']:.1f}ms")
        
        for command_type, stats in metrics["command_statistics"].items():
            if stats["success_rate"] < 0.95:
                issues.append(f"命令成功率低: {command_type} 成功率 {stats['success_rate']:.1%}")
        
        return issues

class InMemoryQueryCache:
    """内存查询缓存实现"""
    
    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.cache = {}
        self.expiry_times = {}
        self.access_times = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def get(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        async with self._lock:
            now = time.time()
            
            # 检查是否过期
            if cache_key in self.expiry_times:
                if now > self.expiry_times[cache_key]:
                    await self._remove_expired_entry(cache_key)
                    return None
            
            if cache_key in self.cache:
                self.access_times[cache_key] = now
                return self.cache[cache_key]
            
            return None
    
    async def set(self, cache_key: str, value: Any, ttl_seconds: int = None):
        """设置缓存数据"""
        async with self._lock:
            ttl = ttl_seconds or self.default_ttl
            now = time.time()
            
            # 如果缓存已满，删除最久未访问的条目
            if len(self.cache) >= self.max_size and cache_key not in self.cache:
                await self._evict_lru_entry()
            
            self.cache[cache_key] = value
            self.expiry_times[cache_key] = now + ttl
            self.access_times[cache_key] = now
    
    async def invalidate(self, cache_key: str):
        """使缓存失效"""
        async with self._lock:
            await self._remove_expired_entry(cache_key)
    
    async def invalidate_pattern(self, pattern: str):
        """根据模式批量使缓存失效"""
        async with self._lock:
            keys_to_remove = []
            for key in self.cache.keys():
                if pattern in key:  # 简单的包含匹配
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                await self._remove_expired_entry(key)
    
    async def _remove_expired_entry(self, cache_key: str):
        """移除过期条目"""
        self.cache.pop(cache_key, None)
        self.expiry_times.pop(cache_key, None)
        self.access_times.pop(cache_key, None)
    
    async def _evict_lru_entry(self):
        """驱逐最久未访问的条目"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        await self._remove_expired_entry(lru_key)

class CQSBusImplementation(ICQSBus):
    """CQS总线实现"""
    
    def __init__(self, config: CQSConfiguration):
        self.config = config
        self.query_handlers: Dict[str, IQueryHandler] = {}
        self.command_handlers: Dict[str, ICommandHandler] = {}
        
        # 组件初始化
        self.query_cache = InMemoryQueryCache() if config.query_cache_enabled else None
        self.metrics = CQSMetricsCollector()
        
        # 并发控制
        self.query_semaphore = asyncio.Semaphore(config.max_concurrent_queries)
        self.command_semaphore = asyncio.Semaphore(config.max_concurrent_commands)
        
        # 断路器状态
        self.circuit_breakers = defaultdict(lambda: {"failures": 0, "last_failure": None, "state": "closed"})
        
        logger.info("CQS总线初始化完成")
    
    async def execute_query(self, query_spec: QuerySpec) -> QueryResult[Any]:
        """执行查询"""
        start_time = time.time()
        cache_hit = False
        
        try:
            # 并发控制
            async with self.query_semaphore:
                
                # CQS验证
                CQSValidator.validate_cqs_compliance("query", False)
                
                # 缓存检查
                cache_key = None
                if self.query_cache and query_spec.cache_policy != "none":
                    cache_key = self._generate_cache_key(query_spec)
                    cached_result = await self.query_cache.get(cache_key)
                    
                    if cached_result is not None:
                        cache_hit = True
                        execution_time_ms = (time.time() - start_time) * 1000
                        await self.metrics.record_query_execution(
                            query_spec.query_type, execution_time_ms, cache_hit
                        )
                        return cached_result
                
                # 断路器检查
                if not self._is_circuit_open(f"query_{query_spec.query_type}"):
                    
                    # 查找处理器
                    handler = self.query_handlers.get(query_spec.query_type)
                    if not handler:
                        return QueryResult(
                            status=QueryResultStatus.ERROR,
                            error_message=f"未找到查询处理器: {query_spec.query_type}"
                        )
                    
                    # 执行查询
                    result = await handler.handle_query(query_spec)
                    
                    # 更新断路器状态
                    if result.status == QueryResultStatus.SUCCESS:
                        self._reset_circuit_breaker(f"query_{query_spec.query_type}")
                    else:
                        self._record_circuit_failure(f"query_{query_spec.query_type}")
                    
                    # 缓存结果
                    if (self.query_cache and cache_key and 
                        result.status == QueryResultStatus.SUCCESS and
                        query_spec.cache_policy != "none"):
                        
                        ttl = self.config.query_cache_ttl_seconds
                        if query_spec.cache_policy == "aggressive":
                            ttl *= 3
                        
                        await self.query_cache.set(cache_key, result, ttl)
                    
                else:
                    result = QueryResult(
                        status=QueryResultStatus.ERROR,
                        error_message=f"断路器开启: {query_spec.query_type}"
                    )
                
        except Exception as e:
            logger.error(f"查询执行错误: {e}")
            self._record_circuit_failure(f"query_{query_spec.query_type}")
            result = QueryResult(
                status=QueryResultStatus.ERROR,
                error_message=str(e)
            )
        
        # 记录指标
        execution_time_ms = (time.time() - start_time) * 1000
        result.execution_time_ms = execution_time_ms
        result.cache_hit = cache_hit
        
        await self.metrics.record_query_execution(
            query_spec.query_type, execution_time_ms, cache_hit
        )
        
        return result
    
    async def execute_command(self, command_spec: CommandSpec) -> CommandResult:
        """执行命令"""
        start_time = time.time()
        
        try:
            # 并发控制
            async with self.command_semaphore:
                
                # CQS验证
                CQSValidator.validate_cqs_compliance("command", True)
                
                # 超时控制
                timeout_task = asyncio.create_task(asyncio.sleep(command_spec.timeout_ms / 1000))
                
                # 断路器检查
                if not self._is_circuit_open(f"command_{command_spec.command_type}"):
                    
                    # 查找处理器
                    handler = self.command_handlers.get(command_spec.command_type)
                    if not handler:
                        return CommandResult(
                            status=CommandResultStatus.FAILED,
                            command_id=command_spec.command_id,
                            error_message=f"未找到命令处理器: {command_spec.command_type}"
                        )
                    
                    # 验证命令
                    validation_errors = await handler.validate_command(command_spec)
                    if validation_errors:
                        return CommandResult(
                            status=CommandResultStatus.VALIDATION_ERROR,
                            command_id=command_spec.command_id,
                            error_message="; ".join(validation_errors)
                        )
                    
                    # 执行命令（带超时）
                    command_task = asyncio.create_task(handler.handle_command(command_spec))
                    
                    done, pending = await asyncio.wait(
                        [command_task, timeout_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    # 取消未完成的任务
                    for task in pending:
                        task.cancel()
                    
                    if command_task in done:
                        result = await command_task
                        
                        # 更新断路器状态
                        if result.status == CommandResultStatus.SUCCESS:
                            self._reset_circuit_breaker(f"command_{command_spec.command_type}")
                        else:
                            self._record_circuit_failure(f"command_{command_spec.command_type}")
                    else:
                        result = CommandResult(
                            status=CommandResultStatus.TIMEOUT,
                            command_id=command_spec.command_id,
                            error_message=f"命令执行超时: {command_spec.timeout_ms}ms"
                        )
                        self._record_circuit_failure(f"command_{command_spec.command_type}")
                
                else:
                    result = CommandResult(
                        status=CommandResultStatus.FAILED,
                        command_id=command_spec.command_id,
                        error_message=f"断路器开启: {command_spec.command_type}"
                    )
                
        except Exception as e:
            logger.error(f"命令执行错误: {e}")
            self._record_circuit_failure(f"command_{command_spec.command_type}")
            result = CommandResult(
                status=CommandResultStatus.FAILED,
                command_id=command_spec.command_id,
                error_message=str(e)
            )
        
        # 记录指标
        execution_time_ms = (time.time() - start_time) * 1000
        result.execution_time_ms = execution_time_ms
        
        await self.metrics.record_command_execution(
            command_spec.command_type, 
            execution_time_ms,
            result.status == CommandResultStatus.SUCCESS
        )
        
        return result
    
    def register_query_handler(self, query_type: str, handler: IQueryHandler):
        """注册查询处理器"""
        CQSValidator.validate_query_handler(handler)
        self.query_handlers[query_type] = handler
        logger.info(f"注册查询处理器: {query_type}")
    
    def register_command_handler(self, command_type: str, handler: ICommandHandler):
        """注册命令处理器"""
        CQSValidator.validate_command_handler(handler)
        self.command_handlers[command_type] = handler
        logger.info(f"注册命令处理器: {command_type}")
    
    def _generate_cache_key(self, query_spec: QuerySpec) -> str:
        """生成缓存键"""
        import hashlib
        import json
        
        # 创建一个包含查询关键信息的字典
        cache_data = {
            "query_type": query_spec.query_type,
            "parameters": query_spec.parameters,
            "filters": query_spec.filters,
            "sort_criteria": query_spec.sort_criteria,
            "pagination": query_spec.pagination
        }
        
        # 生成哈希
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"query_{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _is_circuit_open(self, circuit_name: str) -> bool:
        """检查断路器是否开启"""
        circuit = self.circuit_breakers[circuit_name]
        
        if circuit["state"] == "open":
            # 检查是否应该进入半开状态
            if (circuit["last_failure"] and 
                datetime.now() - circuit["last_failure"] > timedelta(seconds=60)):
                circuit["state"] = "half_open"
                return False
            return True
        
        return False
    
    def _record_circuit_failure(self, circuit_name: str):
        """记录断路器失败"""
        circuit = self.circuit_breakers[circuit_name]
        circuit["failures"] += 1
        circuit["last_failure"] = datetime.now()
        
        # 失败次数达到阈值时开启断路器
        if circuit["failures"] >= 5:
            circuit["state"] = "open"
    
    def _reset_circuit_breaker(self, circuit_name: str):
        """重置断路器"""
        circuit = self.circuit_breakers[circuit_name]
        circuit["failures"] = 0
        circuit["last_failure"] = None
        circuit["state"] = "closed"
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return await self.metrics.get_performance_metrics()
    
    async def get_health(self) -> Dict[str, Any]:
        """获取健康状态"""
        return await self.metrics.get_health_status()

# 工厂函数
def create_cqs_bus(config: CQSConfiguration = None) -> CQSBusImplementation:
    """创建CQS总线实例"""
    if config is None:
        config = CQSConfiguration()
    
    return CQSBusImplementation(config)