#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强透明度监控系统集成

V0.2.2 - 透明度监控系统集成
将现有TransparencyMonitor与后端服务深度集成，提供实时监控能力
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json

from frontend.components.transparency_monitor import TransparencyMonitor
from frontend.services.websocket_manager import websocket_manager, realtime_manager, MessageType, WebSocketMessage
from personal_intelligence_hub.services.backend_integration import get_backend_service, ServiceStatus

logger = logging.getLogger(__name__)


class MonitoringLevel(Enum):
    """监控级别"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class LLMCallMetrics:
    """LLM调用指标"""
    call_id: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    response_time: float
    cost: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class WorkflowMetrics:
    """工作流执行指标"""
    workflow_id: str
    workflow_type: str
    status: str
    progress: float
    participants: List[str]
    start_time: datetime
    current_step: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    error_count: int = 0


@dataclass
class SystemHealthMetrics:
    """系统健康指标"""
    backend_status: ServiceStatus
    llm_services: Dict[str, Dict[str, Any]]
    active_workflows: int
    total_memory_usage: float
    cpu_usage: float
    response_time_avg: float
    error_rate: float
    uptime: timedelta


class EnhancedTransparencyIntegration:
    """增强透明度监控集成器"""
    
    def __init__(self, transparency_monitor: TransparencyMonitor, monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED):
        self.monitor = transparency_monitor
        self.monitoring_level = monitoring_level
        self.backend_service = None
        
        # 监控状态
        self.is_monitoring = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # 数据缓存
        self.llm_call_cache: List[LLMCallMetrics] = []
        self.workflow_cache: Dict[str, WorkflowMetrics] = {}
        self.system_health_cache: Optional[SystemHealthMetrics] = None
        
        # 配置参数
        self.cache_size = 100
        self.health_check_interval = 10  # 秒
        self.metrics_update_interval = 5  # 秒
        
        # 回调函数
        self.on_llm_call_detected: Optional[Callable] = None
        self.on_workflow_status_change: Optional[Callable] = None
        self.on_system_health_change: Optional[Callable] = None
        
        logger.info(f"Enhanced Transparency Integration initialized with level: {monitoring_level.value}")
    
    async def initialize(self):
        """初始化集成器"""
        try:
            # 获取后端服务
            self.backend_service = await get_backend_service()
            
            # 设置WebSocket回调
            await self._setup_websocket_callbacks()
            
            # 设置监控器回调
            self._setup_monitor_callbacks()
            
            # 启动监控任务
            await self.start_monitoring()
            
            logger.info("Enhanced Transparency Integration initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Transparency Integration: {e}")
            raise
    
    async def _setup_websocket_callbacks(self):
        """设置WebSocket回调"""
        try:
            # 注册LLM调用监控
            websocket_manager.register_handler(MessageType.SYSTEM_STATUS, self._handle_llm_call_update)
            
            # 注册工作流状态监控
            websocket_manager.register_workflow_handler(self._handle_workflow_update)
            
            # 注册代理状态监控
            websocket_manager.register_agent_status_handler(self._handle_agent_status_update)
            
            # 启动WebSocket连接
            if not websocket_manager.is_connected:
                await websocket_manager.connect()
            
            logger.info("WebSocket callbacks configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup WebSocket callbacks: {e}")
    
    def _setup_monitor_callbacks(self):
        """设置监控器回调"""
        try:
            # 设置透明度监控器的回调
            self.monitor.on_llm_call_logged = self._on_monitor_llm_call
            self.monitor.on_workflow_update = self._on_monitor_workflow_update
            self.monitor.on_agent_update = self._on_monitor_agent_update
            self.monitor.on_system_status_change = self._on_monitor_system_status_change
            
            logger.info("Monitor callbacks configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup monitor callbacks: {e}")
    
    async def start_monitoring(self):
        """启动监控"""
        if self.is_monitoring:
            logger.warning("Monitoring is already active")
            return
        
        try:
            self.is_monitoring = True
            
            # 启动透明度监控器
            await self.monitor.start_monitoring()
            
            # 启动各种监控任务
            self.monitoring_tasks = [
                asyncio.create_task(self._system_health_monitor()),
                asyncio.create_task(self._llm_call_monitor()),
                asyncio.create_task(self._workflow_monitor()),
                asyncio.create_task(self._performance_monitor())
            ]
            
            logger.info("Enhanced monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            self.is_monitoring = False
            raise
    
    async def stop_monitoring(self):
        """停止监控"""
        try:
            self.is_monitoring = False
            
            # 停止透明度监控器
            await self.monitor.stop_monitoring()
            
            # 取消监控任务
            for task in self.monitoring_tasks:
                if not task.done():
                    task.cancel()
            
            # 等待任务完成
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            self.monitoring_tasks.clear()
            
            logger.info("Enhanced monitoring stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
    
    async def _system_health_monitor(self):
        """系统健康监控任务"""
        while self.is_monitoring:
            try:
                # 检查后端健康状态
                health_status = await self.backend_service.check_backend_health()
                
                # 更新系统健康缓存
                await self._update_system_health_cache(health_status)
                
                # 通知透明度监控器
                await self._notify_system_status_update(health_status)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"System health monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _llm_call_monitor(self):
        """LLM调用监控任务"""
        while self.is_monitoring:
            try:
                # 这里可以添加主动检测LLM调用的逻辑
                # 目前主要依赖WebSocket事件和回调
                
                # 清理过期的LLM调用缓存
                await self._cleanup_llm_cache()
                
                await asyncio.sleep(self.metrics_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"LLM call monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _workflow_monitor(self):
        """工作流监控任务"""
        while self.is_monitoring:
            try:
                # 检查活跃工作流状态
                for workflow_id, workflow_metrics in self.workflow_cache.items():
                    if workflow_metrics.status in ["running", "processing"]:
                        # 尝试获取最新状态
                        status_update = await self.backend_service.get_workflow_status(workflow_id)
                        if "error" not in status_update:
                            await self._update_workflow_metrics(workflow_id, status_update)
                
                await asyncio.sleep(self.metrics_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Workflow monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _performance_monitor(self):
        """性能监控任务"""
        while self.is_monitoring:
            try:
                # 计算性能指标
                performance_metrics = await self._calculate_performance_metrics()
                
                # 更新透明度监控器的性能数据
                if performance_metrics:
                    self.monitor.system_metrics["performance_metrics"].update(performance_metrics)
                
                await asyncio.sleep(self.metrics_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(5)
    
    async def _handle_llm_call_update(self, message: WebSocketMessage):
        """处理LLM调用更新"""
        try:
            payload = message.payload
            
            if payload.get("type") == "llm_call":
                # 创建LLM调用指标
                llm_metrics = LLMCallMetrics(
                    call_id=payload.get("call_id", f"call_{datetime.now().timestamp()}"),
                    model=payload.get("model", "unknown"),
                    provider=payload.get("provider", "unknown"),
                    input_tokens=payload.get("input_tokens", 0),
                    output_tokens=payload.get("output_tokens", 0),
                    response_time=payload.get("response_time", 0.0),
                    cost=payload.get("cost", 0.0),
                    success=payload.get("success", True),
                    error_message=payload.get("error_message")
                )
                
                # 添加到缓存
                self.llm_call_cache.append(llm_metrics)
                
                # 通知透明度监控器
                await self.monitor.log_llm_call(asdict(llm_metrics))
                
                # 触发回调
                if self.on_llm_call_detected:
                    await self.on_llm_call_detected(llm_metrics)
                
                logger.debug(f"LLM call logged: {llm_metrics.model} - {llm_metrics.response_time:.2f}s")
        
        except Exception as e:
            logger.error(f"Error handling LLM call update: {e}")
    
    async def _handle_workflow_update(self, message: WebSocketMessage):
        """处理工作流更新"""
        try:
            payload = message.payload
            workflow_id = payload.get("workflow_id")
            
            if workflow_id:
                # 更新工作流指标
                await self._update_workflow_metrics(workflow_id, payload)
                
                # 通知透明度监控器
                await self.monitor.update_workflow_status(payload)
                
                # 触发回调
                if self.on_workflow_status_change:
                    workflow_metrics = self.workflow_cache.get(workflow_id)
                    if workflow_metrics:
                        await self.on_workflow_status_change(workflow_metrics)
        
        except Exception as e:
            logger.error(f"Error handling workflow update: {e}")
    
    async def _handle_agent_status_update(self, message: WebSocketMessage):
        """处理代理状态更新"""
        try:
            payload = message.payload
            
            # 通知透明度监控器
            await self.monitor.update_agent_status(payload)
            
            logger.debug(f"Agent status updated: {payload.get('agent_id')} -> {payload.get('status')}")
        
        except Exception as e:
            logger.error(f"Error handling agent status update: {e}")
    
    async def _update_workflow_metrics(self, workflow_id: str, status_data: Dict[str, Any]):
        """更新工作流指标"""
        try:
            if workflow_id not in self.workflow_cache:
                # 创建新的工作流指标
                self.workflow_cache[workflow_id] = WorkflowMetrics(
                    workflow_id=workflow_id,
                    workflow_type=status_data.get("type", "unknown"),
                    status=status_data.get("status", "unknown"),
                    progress=status_data.get("progress", 0.0),
                    participants=status_data.get("participants", []),
                    start_time=datetime.now()
                )
            else:
                # 更新现有指标
                metrics = self.workflow_cache[workflow_id]
                metrics.status = status_data.get("status", metrics.status)
                metrics.progress = status_data.get("progress", metrics.progress)
                metrics.current_step = status_data.get("current_step")
                
                if status_data.get("error"):
                    metrics.error_count += 1
        
        except Exception as e:
            logger.error(f"Error updating workflow metrics: {e}")
    
    async def _update_system_health_cache(self, health_status: Dict[str, Any]):
        """更新系统健康缓存"""
        try:
            backend_status = health_status.get("backend", {})
            
            self.system_health_cache = SystemHealthMetrics(
                backend_status=backend_status.status if hasattr(backend_status, 'status') else ServiceStatus.UNAVAILABLE,
                llm_services=self._extract_llm_services_status(health_status),
                active_workflows=len([w for w in self.workflow_cache.values() if w.status in ["running", "processing"]]),
                total_memory_usage=0.0,  # TODO: 实现内存监控
                cpu_usage=0.0,  # TODO: 实现CPU监控
                response_time_avg=self._calculate_avg_response_time(),
                error_rate=self._calculate_error_rate(),
                uptime=datetime.now() - self.monitor.system_metrics["uptime"]
            )
        
        except Exception as e:
            logger.error(f"Error updating system health cache: {e}")
    
    def _extract_llm_services_status(self, health_status: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """提取LLM服务状态"""
        llm_services = {}
        
        # 从健康状态中提取LLM服务信息
        # 这里可以根据实际的健康检查响应格式进行调整
        if "llm_services" in health_status:
            llm_services = health_status["llm_services"]
        else:
            # 默认服务状态
            llm_services = {
                "ollama": {"status": "unknown", "response_time": 0.0},
                "openai": {"status": "unknown", "response_time": 0.0}
            }
        
        return llm_services
    
    def _calculate_avg_response_time(self) -> float:
        """计算平均响应时间"""
        if not self.llm_call_cache:
            return 0.0
        
        recent_calls = [
            call for call in self.llm_call_cache
            if (datetime.now() - call.timestamp).total_seconds() <= 300  # 最近5分钟
        ]
        
        if not recent_calls:
            return 0.0
        
        return sum(call.response_time for call in recent_calls) / len(recent_calls)
    
    def _calculate_error_rate(self) -> float:
        """计算错误率"""
        if not self.llm_call_cache:
            return 0.0
        
        recent_calls = [
            call for call in self.llm_call_cache
            if (datetime.now() - call.timestamp).total_seconds() <= 300  # 最近5分钟
        ]
        
        if not recent_calls:
            return 0.0
        
        error_count = sum(1 for call in recent_calls if not call.success)
        return (error_count / len(recent_calls)) * 100
    
    async def _calculate_performance_metrics(self) -> Dict[str, float]:
        """计算性能指标"""
        try:
            return {
                "avg_response_time": self._calculate_avg_response_time(),
                "success_rate": 100.0 - self._calculate_error_rate(),
                "throughput": len(self.llm_call_cache) / 5.0 if self.llm_call_cache else 0.0,
                "active_workflows": len([w for w in self.workflow_cache.values() if w.status in ["running", "processing"]])
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    async def _cleanup_llm_cache(self):
        """清理LLM调用缓存"""
        try:
            # 保留最近的调用记录
            if len(self.llm_call_cache) > self.cache_size:
                self.llm_call_cache = self.llm_call_cache[-self.cache_size:]
            
            # 清理过期的工作流缓存
            current_time = datetime.now()
            expired_workflows = [
                wf_id for wf_id, metrics in self.workflow_cache.items()
                if metrics.status in ["completed", "failed", "cancelled"] and
                (current_time - metrics.start_time).total_seconds() > 3600  # 1小时后清理
            ]
            
            for wf_id in expired_workflows:
                del self.workflow_cache[wf_id]
        
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
    
    async def _notify_system_status_update(self, health_status: Dict[str, Any]):
        """通知系统状态更新"""
        try:
            # 构造系统状态更新消息
            status_update = {
                "type": "system_health",
                "data": {
                    "backend_connected": "backend" in health_status and hasattr(health_status["backend"], 'status'),
                    "llm_services": self._extract_llm_services_status(health_status),
                    "active_workflows": len(self.workflow_cache),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # 通知透明度监控器
            await self.monitor.update_system_status(status_update)
            
            # 触发回调
            if self.on_system_health_change and self.system_health_cache:
                await self.on_system_health_change(self.system_health_cache)
        
        except Exception as e:
            logger.error(f"Error notifying system status update: {e}")
    
    # 监控器回调方法
    async def _on_monitor_llm_call(self, call_data: Dict[str, Any]):
        """监控器LLM调用回调"""
        logger.debug(f"Monitor LLM call callback: {call_data.get('model', 'unknown')}")
    
    async def _on_monitor_workflow_update(self, workflow_data: Dict[str, Any]):
        """监控器工作流更新回调"""
        logger.debug(f"Monitor workflow update callback: {workflow_data.get('workflow_id', 'unknown')}")
    
    async def _on_monitor_agent_update(self, agent_data: Dict[str, Any]):
        """监控器代理更新回调"""
        logger.debug(f"Monitor agent update callback: {agent_data.get('agent_id', 'unknown')}")
    
    async def _on_monitor_system_status_change(self, status_data: Dict[str, Any]):
        """监控器系统状态变更回调"""
        logger.debug("Monitor system status change callback triggered")
    
    # 公共接口方法
    async def log_llm_call(self, call_data: Dict[str, Any]):
        """手动记录LLM调用"""
        try:
            llm_metrics = LLMCallMetrics(
                call_id=call_data.get("call_id", f"manual_{datetime.now().timestamp()}"),
                model=call_data.get("model", "unknown"),
                provider=call_data.get("provider", "unknown"),
                input_tokens=call_data.get("input_tokens", 0),
                output_tokens=call_data.get("output_tokens", 0),
                response_time=call_data.get("response_time", 0.0),
                cost=call_data.get("cost", 0.0),
                success=call_data.get("success", True),
                error_message=call_data.get("error_message")
            )
            
            self.llm_call_cache.append(llm_metrics)
            await self.monitor.log_llm_call(asdict(llm_metrics))
            
            if self.on_llm_call_detected:
                await self.on_llm_call_detected(llm_metrics)
        
        except Exception as e:
            logger.error(f"Error logging LLM call: {e}")
    
    async def log_workflow_start(self, workflow_data: Dict[str, Any]):
        """记录工作流开始"""
        try:
            workflow_id = workflow_data.get("workflow_id", f"workflow_{datetime.now().timestamp()}")
            
            # 创建工作流指标
            workflow_metrics = WorkflowMetrics(
                workflow_id=workflow_id,
                workflow_type=workflow_data.get("workflow_type", "unknown"),
                status="started",
                progress=0.0,
                participants=workflow_data.get("participants", []),
                start_time=datetime.now()
            )
            
            self.workflow_cache[workflow_id] = workflow_metrics
            
            # 通知透明度监控器
            await self.monitor.log_workflow_start(
                workflows=[workflow_data.get("workflow_type", "unknown")],
                roles=workflow_data.get("participants", [])
            )
            
            if self.on_workflow_status_change:
                await self.on_workflow_status_change(workflow_metrics)
        
        except Exception as e:
            logger.error(f"Error logging workflow start: {e}")
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """获取监控统计信息"""
        try:
            return {
                "is_monitoring": self.is_monitoring,
                "monitoring_level": self.monitoring_level.value,
                "llm_calls_cached": len(self.llm_call_cache),
                "active_workflows": len([w for w in self.workflow_cache.values() if w.status in ["running", "processing"]]),
                "total_workflows": len(self.workflow_cache),
                "system_health": asdict(self.system_health_cache) if self.system_health_cache else None,
                "cache_size": self.cache_size,
                "monitoring_intervals": {
                    "health_check": self.health_check_interval,
                    "metrics_update": self.metrics_update_interval
                }
            }
        except Exception as e:
            logger.error(f"Error getting monitoring statistics: {e}")
            return {"error": str(e)}


# 全局集成器实例
_enhanced_transparency_integration: Optional[EnhancedTransparencyIntegration] = None


async def get_enhanced_transparency_integration(
    transparency_monitor: TransparencyMonitor,
    monitoring_level: MonitoringLevel = MonitoringLevel.DETAILED
) -> EnhancedTransparencyIntegration:
    """获取增强透明度集成器实例"""
    global _enhanced_transparency_integration
    
    if _enhanced_transparency_integration is None:
        _enhanced_transparency_integration = EnhancedTransparencyIntegration(
            transparency_monitor, monitoring_level
        )
        await _enhanced_transparency_integration.initialize()
    
    return _enhanced_transparency_integration


async def cleanup_enhanced_transparency_integration():
    """清理增强透明度集成器"""
    global _enhanced_transparency_integration
    
    if _enhanced_transparency_integration:
        await _enhanced_transparency_integration.stop_monitoring()
        _enhanced_transparency_integration = None