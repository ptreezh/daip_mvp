#!/usr/bin/env python3
"""统一共识调度器工具模块

包含调度器的管理方法、指标收集和配置功能。
文件长度限制: <400行
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Optional

from consensus_algorithm_interface import ConsensusAlgorithm
from consensus_models import AlgorithmMetadata
from unified_consensus_dispatcher import DispatcherMetrics, UnifiedConsensusDispatcher

logger = logging.getLogger(__name__)


class DispatcherManager:
    """调度器管理器"""
    
    def __init__(self, dispatcher: UnifiedConsensusDispatcher):
        self.dispatcher = dispatcher
        
    def register_algorithm(self, 
                          algorithm_id: str, 
                          algorithm: ConsensusAlgorithm,
                          metadata: Optional[AlgorithmMetadata] = None) -> bool:
        """注册算法
        
        Args:
            algorithm_id: 算法ID
            algorithm: 算法实例
            metadata: 算法元数据（可选）
            
        Returns:
            是否注册成功
        """
        try:
            success = self.dispatcher.registry.register(algorithm_id, algorithm, metadata)
            
            if success:
                logger.info(f"Algorithm {algorithm_id} registered successfully")
                
                # 更新选择器
                self.dispatcher.selector = self.dispatcher.selector.__class__(
                    self.dispatcher.registry,
                    self.dispatcher.config.selection_strategy
                )
                
                # 更新降级管理器
                if self.dispatcher.fallback_manager:
                    self.dispatcher.fallback_manager.registry = self.dispatcher.registry
                    
            return success
            
        except Exception as e:
            logger.error(f"Failed to register algorithm {algorithm_id}: {str(e)}")
            return False
            
    def unregister_algorithm(self, algorithm_id: str) -> bool:
        """注销算法
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            是否注销成功
        """
        try:
            success = self.dispatcher.registry.unregister(algorithm_id)
            
            if success:
                logger.info(f"Algorithm {algorithm_id} unregistered successfully")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to unregister algorithm {algorithm_id}: {str(e)}")
            return False
            
    def get_available_algorithms(self) -> list[dict[str, Any]]:
        """获取可用算法列表
        
        Returns:
            算法信息列表
        """
        try:
            algorithms = self.dispatcher.registry.list_algorithms()
            
            algorithm_list = []
            for algo_info in algorithms:
                algorithm_list.append({
                    "algorithm_id": algo_info.algorithm_id,
                    "name": algo_info.metadata.name,
                    "version": algo_info.metadata.version,
                    "algorithm_type": algo_info.metadata.algorithm_type.value,
                    "health_status": algo_info.health_status,
                    "usage_count": algo_info.usage_count,
                    "last_used": algo_info.last_used.isoformat() if algo_info.last_used else None,
                    "accuracy": algo_info.metadata.accuracy,
                    "performance": algo_info.metadata.performance,
                    "complexity": algo_info.metadata.complexity
                })
                
            return algorithm_list
            
        except Exception as e:
            logger.error(f"Failed to get available algorithms: {str(e)}")
            return []
            
    def get_algorithm_details(self, algorithm_id: str) -> Optional[dict[str, Any]]:
        """获取算法详细信息
        
        Args:
            algorithm_id: 算法ID
            
        Returns:
            算法详细信息
        """
        try:
            algo_info = self.dispatcher.registry.get_algorithm_info(algorithm_id)
            if not algo_info:
                return None
                
            return {
                "algorithm_id": algo_info.algorithm_id,
                "metadata": {
                    "name": algo_info.metadata.name,
                    "version": algo_info.metadata.version,
                    "description": algo_info.metadata.description,
                    "algorithm_type": algo_info.metadata.algorithm_type.value,
                    "input_types": algo_info.metadata.input_types,
                    "output_types": algo_info.metadata.output_types,
                    "complexity": algo_info.metadata.complexity,
                    "accuracy": algo_info.metadata.accuracy,
                    "performance": algo_info.metadata.performance,
                    "requirements": algo_info.metadata.requirements
                },
                "capabilities": {
                    "supported_input_types": list(algo_info.capabilities.supported_input_types),
                    "supported_output_types": list(algo_info.capabilities.supported_output_types),
                    "requires_reasoning": algo_info.capabilities.requires_reasoning,
                    "requires_evidence": algo_info.capabilities.requires_evidence,
                    "supports_async": algo_info.capabilities.supports_async,
                    "min_participants": algo_info.capabilities.min_participants,
                    "max_participants": algo_info.capabilities.max_participants
                },
                "status": {
                    "health_status": algo_info.health_status,
                    "usage_count": algo_info.usage_count,
                    "last_used": algo_info.last_used.isoformat() if algo_info.last_used else None,
                    "registered_at": algo_info.registered_at.isoformat(),
                    "last_health_check": algo_info.last_health_check.isoformat() if algo_info.last_health_check else None
                },
                "configuration": algo_info.configuration
            }
            
        except Exception as e:
            logger.error(f"Failed to get algorithm details for {algorithm_id}: {str(e)}")
            return None


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, dispatcher: UnifiedConsensusDispatcher):
        self.dispatcher = dispatcher
        
    def get_metrics(self) -> dict[str, Any]:
        """获取调度器指标
        
        Returns:
            指标字典
        """
        metrics = self.dispatcher.metrics
        
        # 计算成功率
        success_rate = 0.0
        if metrics.total_requests > 0:
            success_rate = metrics.successful_requests / metrics.total_requests
            
        # 计算降级率
        fallback_rate = 0.0
        if metrics.total_requests > 0:
            fallback_rate = metrics.fallback_requests / metrics.total_requests
            
        return {
            "summary": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "fallback_requests": metrics.fallback_requests,
                "success_rate": success_rate,
                "fallback_rate": fallback_rate,
                "average_response_time": metrics.average_response_time,
                "active_requests": metrics.active_requests
            },
            "algorithm_usage": dict(metrics.algorithm_usage),
            "error_counts": dict(metrics.error_counts),
            "registry_stats": self.dispatcher.registry.get_registry_stats().__dict__,
            "fallback_stats": self._get_fallback_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
    def _get_fallback_stats(self) -> dict[str, Any]:
        """获取降级统计"""
        if self.dispatcher.fallback_manager:
            from fallback_manager_utils import FallbackManagerUtils
            utils = FallbackManagerUtils(self.dispatcher.fallback_manager)
            return utils.get_fallback_stats()
        else:
            return {"message": "Fallback manager not enabled"}
            
    def reset_metrics(self):
        """重置指标"""
        self.dispatcher.metrics = DispatcherMetrics()
        logger.info("Dispatcher metrics reset")
        
    def get_active_requests(self) -> list[dict[str, Any]]:
        """获取活跃请求信息
        
        Returns:
            活跃请求列表
        """
        active_requests = []
        
        for request_id, context in self.dispatcher.active_requests.items():
            active_requests.append({
                "request_id": request_id,
                "start_time": datetime.fromtimestamp(context.start_time).isoformat(),
                "duration": time.time() - context.start_time,
                "selected_algorithm": context.selected_algorithm,
                "fallback_used": context.fallback_used,
                "attempts": len(context.attempts),
                "participant_count": len(context.request.inputs)
            })
            
        return active_requests


class ConfigurationManager:
    """配置管理器"""
    
    def __init__(self, dispatcher: UnifiedConsensusDispatcher):
        self.dispatcher = dispatcher
        
    def update_config(self, config_updates: dict[str, Any]) -> bool:
        """更新配置
        
        Args:
            config_updates: 配置更新字典
            
        Returns:
            是否更新成功
        """
        try:
            config = self.dispatcher.config
            
            # 更新基本配置
            if "default_timeout" in config_updates:
                config.default_timeout = float(config_updates["default_timeout"])
                
            if "max_concurrent_requests" in config_updates:
                new_limit = int(config_updates["max_concurrent_requests"])
                config.max_concurrent_requests = new_limit
                # 更新信号量
                self.dispatcher.semaphore = asyncio.Semaphore(new_limit)
                
            if "enable_load_balancing" in config_updates:
                config.enable_load_balancing = bool(config_updates["enable_load_balancing"])
                
            if "enable_metrics_collection" in config_updates:
                config.enable_metrics_collection = bool(config_updates["enable_metrics_collection"])
                
            if "enable_request_logging" in config_updates:
                config.enable_request_logging = bool(config_updates["enable_request_logging"])
                
            if "fallback_enabled" in config_updates:
                config.fallback_enabled = bool(config_updates["fallback_enabled"])
                
            if "selection_strategy" in config_updates:
                from algorithm_selector import SelectionStrategy
                strategy_name = config_updates["selection_strategy"]
                if hasattr(SelectionStrategy, strategy_name.upper()):
                    config.selection_strategy = getattr(SelectionStrategy, strategy_name.upper())
                    # 更新选择器策略
                    self.dispatcher.selector.update_selection_strategy(config.selection_strategy)
                    
            logger.info("Dispatcher configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False
            
    def get_config(self) -> dict[str, Any]:
        """获取当前配置
        
        Returns:
            配置字典
        """
        config = self.dispatcher.config
        
        return {
            "default_timeout": config.default_timeout,
            "max_concurrent_requests": config.max_concurrent_requests,
            "enable_load_balancing": config.enable_load_balancing,
            "enable_metrics_collection": config.enable_metrics_collection,
            "enable_request_logging": config.enable_request_logging,
            "fallback_enabled": config.fallback_enabled,
            "selection_strategy": config.selection_strategy.value
        }
        
    def export_config(self) -> str:
        """导出配置为JSON字符串
        
        Returns:
            JSON配置字符串
        """
        import json
        return json.dumps(self.get_config(), indent=2)
        
    def import_config(self, config_json: str) -> bool:
        """从JSON字符串导入配置
        
        Args:
            config_json: JSON配置字符串
            
        Returns:
            是否导入成功
        """
        try:
            import json
            config_dict = json.loads(config_json)
            return self.update_config(config_dict)
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {str(e)}")
            return False