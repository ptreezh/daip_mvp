#!/usr/bin/env python3
"""降级管理器工具模块

包含FallbackManager的工具方法和统计功能。
文件长度限制: <400行
"""

import logging
from collections import defaultdict
<<<<<<< HEAD
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
=======
from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from fallback_manager_core import CircuitBreakerState, FallbackManager, FallbackStrategy

logger = logging.getLogger(__name__)


class FallbackManagerUtils:
    """降级管理器工具类"""
<<<<<<< HEAD

    def __init__(self, fallback_manager: FallbackManager):
        self.fallback_manager = fallback_manager

=======
    
    def __init__(self, fallback_manager: FallbackManager):
        self.fallback_manager = fallback_manager
        
>>>>>>> feature/core-services-refactor
    def update_fallback_strategy(self,
                                strategy: FallbackStrategy,
                                config: Optional[Any] = None) -> bool:
        """更新降级策略
        
        Args:
            strategy: 新的降级策略
            config: 新的配置（可选）
            
        Returns:
            是否更新成功
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            if config:
                self.fallback_manager.config = config
            else:
                self.fallback_manager.config.strategy = strategy
<<<<<<< HEAD

            logger.info(f"Fallback strategy updated to: {strategy}")
            return True

        except Exception as e:
            logger.error(f"Failed to update fallback strategy: {str(e)}")
            return False

    def add_event_listener(self, listener: Callable):
        """添加事件监听器"""
        self.fallback_manager.event_listeners.append(listener)

=======
                
            logger.info(f"Fallback strategy updated to: {strategy}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update fallback strategy: {str(e)}")
            return False
            
    def add_event_listener(self, listener: Callable):
        """添加事件监听器"""
        self.fallback_manager.event_listeners.append(listener)
        
>>>>>>> feature/core-services-refactor
    def remove_event_listener(self, listener: Callable):
        """移除事件监听器"""
        if listener in self.fallback_manager.event_listeners:
            self.fallback_manager.event_listeners.remove(listener)
<<<<<<< HEAD

    def get_fallback_stats(self) -> Dict[str, Any]:
=======
            
    def get_fallback_stats(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取降级统计信息
        
        Returns:
            统计信息字典
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        # 计算成功率
        total = self.fallback_manager.stats["total_fallbacks"]
        success_rate = (self.fallback_manager.stats["successful_fallbacks"] / total) if total > 0 else 0.0
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 统计熔断器状态
        circuit_breaker_stats = {}
        for algo_id, breaker in self.fallback_manager.circuit_breakers.items():
            circuit_breaker_stats[algo_id] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None,
                "last_success": breaker.last_success_time.isoformat() if breaker.last_success_time else None
            }
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        # 统计最近事件
        recent_events = list(self.fallback_manager.fallback_events)[-10:]
        event_summary = []
        for event in recent_events:
            event_summary.append({
                "timestamp": event.timestamp.isoformat(),
                "original_algorithm": event.original_algorithm,
                "fallback_algorithm": event.fallback_algorithm,
                "success": event.success,
                "depth": event.fallback_depth
            })
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
        return {
            "total_fallbacks": total,
            "successful_fallbacks": self.fallback_manager.stats["successful_fallbacks"],
            "failed_fallbacks": self.fallback_manager.stats["failed_fallbacks"],
            "success_rate": success_rate,
            "circuit_breaker_trips": self.fallback_manager.stats["circuit_breaker_trips"],
            "circuit_breakers": circuit_breaker_stats,
            "recent_events": event_summary,
            "config": {
                "strategy": self.fallback_manager.config.strategy.value,
                "max_fallback_depth": self.fallback_manager.config.max_fallback_depth,
                "retry_strategy": self.fallback_manager.config.retry_strategy.value,
                "max_retry_count": self.fallback_manager.config.max_retry_count,
                "circuit_breaker_enabled": self.fallback_manager.config.circuit_breaker_enabled,
                "failure_threshold": self.fallback_manager.config.failure_threshold
            }
        }
<<<<<<< HEAD

    def get_algorithm_reliability(self, algorithm_id: str) -> Dict[str, Any]:
=======
        
    def get_algorithm_reliability(self, algorithm_id: str) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """获取算法可靠性信息
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            可靠性信息
<<<<<<< HEAD

        """
        breaker = self.fallback_manager.circuit_breakers[algorithm_id]

=======
        """
        breaker = self.fallback_manager.circuit_breakers[algorithm_id]
        
>>>>>>> feature/core-services-refactor
        # 统计该算法相关的降级事件
        algorithm_events = [
            event for event in self.fallback_manager.fallback_events
            if event.original_algorithm == algorithm_id or event.fallback_algorithm == algorithm_id
        ]
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 作为原始算法的失败次数
        original_failures = len([
            event for event in algorithm_events
            if event.original_algorithm == algorithm_id
        ])
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 作为降级算法的成功次数
        fallback_successes = len([
            event for event in algorithm_events
            if event.fallback_algorithm == algorithm_id and event.success
        ])
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 作为降级算法的失败次数
        fallback_failures = len([
            event for event in algorithm_events
            if event.fallback_algorithm == algorithm_id and not event.success
        ])
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        # 计算可靠性评分
        total_uses = original_failures + fallback_successes + fallback_failures
        if total_uses > 0:
            reliability_score = (fallback_successes) / total_uses
        else:
            reliability_score = 1.0
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    def reset_circuit_breaker(self, algorithm_id: str) -> bool:
        """重置算法的熔断器
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            是否重置成功
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            if algorithm_id in self.fallback_manager.circuit_breakers:
                breaker = self.fallback_manager.circuit_breakers[algorithm_id]
                breaker.state = CircuitBreakerState.CLOSED
                breaker.failure_count = 0
                breaker.open_time = None
                logger.info(f"Circuit breaker for {algorithm_id} has been reset")
                return True
            else:
                logger.warning(f"No circuit breaker found for {algorithm_id}")
                return False
<<<<<<< HEAD

        except Exception as e:
            logger.error(f"Failed to reset circuit breaker for {algorithm_id}: {str(e)}")
            return False

=======
                
        except Exception as e:
            logger.error(f"Failed to reset circuit breaker for {algorithm_id}: {str(e)}")
            return False
            
>>>>>>> feature/core-services-refactor
    def clear_event_history(self):
        """清空事件历史"""
        self.fallback_manager.fallback_events.clear()
        logger.info("Fallback event history cleared")
<<<<<<< HEAD

    def export_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
=======
        
    def export_events(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """导出降级事件
        
        Args:
            limit: 导出数量限制
            
        Returns:
            事件列表
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        events = list(self.fallback_manager.fallback_events)
        if limit:
            events = events[-limit:]
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
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
<<<<<<< HEAD

        return exported_events

    def analyze_failure_patterns(self) -> Dict[str, Any]:
=======
            
        return exported_events
        
    def analyze_failure_patterns(self) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """分析失败模式
        
        Returns:
            失败模式分析结果
<<<<<<< HEAD

        """
        if not self.fallback_manager.fallback_events:
            return {"message": "No events to analyze"}

=======
        """
        if not self.fallback_manager.fallback_events:
            return {"message": "No events to analyze"}
            
>>>>>>> feature/core-services-refactor
        # 统计各算法的失败频率
        algorithm_failures = defaultdict(int)
        error_types = defaultdict(int)
        failure_times = []
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        for event in self.fallback_manager.fallback_events:
            if not event.success:
                algorithm_failures[event.fallback_algorithm] += 1
                error_types[event.failure_context.error_type] += 1
                failure_times.append(event.timestamp)
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        # 分析失败时间模式
        if failure_times:
            failure_times.sort()
            time_intervals = []
            for i in range(1, len(failure_times)):
                interval = (failure_times[i] - failure_times[i-1]).total_seconds()
                time_intervals.append(interval)
<<<<<<< HEAD

            avg_interval = sum(time_intervals) / len(time_intervals) if time_intervals else 0
        else:
            avg_interval = 0

        # 找出最不可靠的算法
        most_unreliable = max(algorithm_failures.items(), key=lambda x: x[1]) if algorithm_failures else None

        # 找出最常见的错误类型
        most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else None

=======
                
            avg_interval = sum(time_intervals) / len(time_intervals) if time_intervals else 0
        else:
            avg_interval = 0
            
        # 找出最不可靠的算法
        most_unreliable = max(algorithm_failures.items(), key=lambda x: x[1]) if algorithm_failures else None
        
        # 找出最常见的错误类型
        most_common_error = max(error_types.items(), key=lambda x: x[1]) if error_types else None
        
>>>>>>> feature/core-services-refactor
        return {
            "total_events": len(self.fallback_manager.fallback_events),
            "algorithm_failures": dict(algorithm_failures),
            "error_types": dict(error_types),
            "most_unreliable_algorithm": most_unreliable[0] if most_unreliable else None,
            "most_common_error_type": most_common_error[0] if most_common_error else None,
            "average_failure_interval_seconds": avg_interval,
            "analysis_timestamp": datetime.now().isoformat()
<<<<<<< HEAD
        }
=======
        }
>>>>>>> feature/core-services-refactor
