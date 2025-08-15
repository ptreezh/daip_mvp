#!/usr/bin/env python3
"""Personal Intelligence Hub - Monitoring Integration Service

V0.2.2 - 透明度监控系统集成
将PersonalAssistantService与透明度监控系统集成
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from personal_intelligence_hub.services.backend_integration import get_backend_service
from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService, WorkflowType

logger = logging.getLogger(__name__)


@dataclass
class MonitoringEvent:
    """监控事件数据结构"""
    event_id: str
    event_type: str
    timestamp: datetime
    source: str
    data: dict[str, Any]
    session_id: Optional[str] = None


class PersonalAssistantMonitoringWrapper:
    """PersonalAssistant监控包装器"""
    
    def __init__(self, personal_assistant: PersonalAssistantService):
        self.personal_assistant = personal_assistant
        self.monitoring_callbacks: list[Callable] = []
        self.session_contexts: dict[str, dict[str, Any]] = {}
        
        # 监控统计
        self.stats = {
            "intent_analyses": 0,
            "team_assemblies": 0,
            "message_processes": 0,
            "command_executions": 0,
            "total_response_time": 0.0,
            "error_count": 0,
            "start_time": datetime.now()
        }
        
        logger.info("PersonalAssistant monitoring wrapper initialized")
    
    def add_monitoring_callback(self, callback: Callable):
        """添加监控回调"""
        self.monitoring_callbacks.append(callback)
        logger.info(f"Added monitoring callback: {callback.__name__}")
    
    async def _emit_monitoring_event(self, event_type: str, data: dict[str, Any], session_id: Optional[str] = None):
        """发送监控事件"""
        try:
            event = MonitoringEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                timestamp=datetime.now(),
                source="PersonalAssistant",
                data=data,
                session_id=session_id
            )
            
            # 调用所有监控回调
            for callback in self.monitoring_callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Monitoring callback error: {e}")
        
        except Exception as e:
            logger.error(f"Error emitting monitoring event: {e}")
    
    async def analyze_intent(self, user_input: str, context: Optional[dict] = None) -> Any:
        """监控包装的意图分析"""
        start_time = datetime.now()
        session_id = context.get("session_id") if context else None
        
        try:
            # 发送开始事件
            await self._emit_monitoring_event("intent_analysis_start", {
                "user_input": user_input[:100],  # 限制长度
                "context_size": len(context) if context else 0
            }, session_id)
            
            # 调用原始方法
            result = await self.personal_assistant.analyze_intent(user_input, context)
            
            # 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计
            self.stats["intent_analyses"] += 1
            self.stats["total_response_time"] += response_time
            
            # 发送完成事件
            await self._emit_monitoring_event("intent_analysis_complete", {
                "workflow_type": result.workflowType.value,
                "confidence": result.confidence,
                "response_time": response_time,
                "topic": result.topic
            }, session_id)
            
            return result
            
        except Exception as e:
            # 更新错误统计
            self.stats["error_count"] += 1
            
            # 发送错误事件
            await self._emit_monitoring_event("intent_analysis_error", {
                "error": str(e),
                "user_input": user_input[:100]
            }, session_id)
            
            raise
    
    async def assemble_team(self, topic: str, workflow_type: WorkflowType) -> Any:
        """监控包装的团队组建"""
        start_time = datetime.now()
        
        try:
            # 发送开始事件
            await self._emit_monitoring_event("team_assembly_start", {
                "topic": topic,
                "workflow_type": workflow_type.value
            })
            
            # 调用原始方法
            result = await self.personal_assistant.assemble_team(topic, workflow_type)
            
            # 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计
            self.stats["team_assemblies"] += 1
            self.stats["total_response_time"] += response_time
            
            # 发送完成事件
            await self._emit_monitoring_event("team_assembly_complete", {
                "agents": result.agents,
                "diversity_score": result.diversity_score,
                "response_time": response_time
            })
            
            return result
            
        except Exception as e:
            # 更新错误统计
            self.stats["error_count"] += 1
            
            # 发送错误事件
            await self._emit_monitoring_event("team_assembly_error", {
                "error": str(e),
                "topic": topic,
                "workflow_type": workflow_type.value
            })
            
            raise
    
    async def process_message(self, user_input: str, session_id: str) -> str:
        """监控包装的消息处理"""
        start_time = datetime.now()
        
        try:
            # 更新会话上下文
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = {
                    "created_at": datetime.now(),
                    "message_count": 0,
                    "total_response_time": 0.0
                }
            
            session_context = self.session_contexts[session_id]
            session_context["message_count"] += 1
            
            # 发送开始事件
            await self._emit_monitoring_event("message_process_start", {
                "user_input": user_input[:100],
                "session_message_count": session_context["message_count"]
            }, session_id)
            
            # 调用原始方法
            result = await self.personal_assistant.process_message(user_input, session_id)
            
            # 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计
            self.stats["message_processes"] += 1
            self.stats["total_response_time"] += response_time
            session_context["total_response_time"] += response_time
            
            # 发送完成事件
            await self._emit_monitoring_event("message_process_complete", {
                "response_length": len(result),
                "response_time": response_time,
                "session_avg_response_time": session_context["total_response_time"] / session_context["message_count"]
            }, session_id)
            
            return result
            
        except Exception as e:
            # 更新错误统计
            self.stats["error_count"] += 1
            
            # 发送错误事件
            await self._emit_monitoring_event("message_process_error", {
                "error": str(e),
                "user_input": user_input[:100]
            }, session_id)
            
            raise
    
    async def execute_command(self, command: str, session_id: str) -> str:
        """监控包装的命令执行"""
        start_time = datetime.now()
        
        try:
            # 发送开始事件
            await self._emit_monitoring_event("command_execution_start", {
                "command": command[:100]
            }, session_id)
            
            # 调用原始方法
            result = await self.personal_assistant.execute_command(command, session_id)
            
            # 计算响应时间
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 更新统计
            self.stats["command_executions"] += 1
            self.stats["total_response_time"] += response_time
            
            # 发送完成事件
            await self._emit_monitoring_event("command_execution_complete", {
                "result_length": len(result),
                "response_time": response_time
            }, session_id)
            
            return result
            
        except Exception as e:
            # 更新错误统计
            self.stats["error_count"] += 1
            
            # 发送错误事件
            await self._emit_monitoring_event("command_execution_error", {
                "error": str(e),
                "command": command[:100]
            }, session_id)
            
            raise
    
    def get_monitoring_statistics(self) -> dict[str, Any]:
        """获取监控统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        total_operations = (
            self.stats["intent_analyses"] + 
            self.stats["team_assemblies"] + 
            self.stats["message_processes"] + 
            self.stats["command_executions"]
        )
        
        return {
            "uptime_seconds": uptime,
            "total_operations": total_operations,
            "operations_per_minute": (total_operations / (uptime / 60)) if uptime > 0 else 0,
            "average_response_time": (
                self.stats["total_response_time"] / total_operations
            ) if total_operations > 0 else 0,
            "error_rate": (
                self.stats["error_count"] / total_operations * 100
            ) if total_operations > 0 else 0,
            "active_sessions": len(self.session_contexts),
            "operations_breakdown": {
                "intent_analyses": self.stats["intent_analyses"],
                "team_assemblies": self.stats["team_assemblies"],
                "message_processes": self.stats["message_processes"],
                "command_executions": self.stats["command_executions"]
            }
        }


class MonitoringIntegrationService:
    """监控集成服务"""
    
    def __init__(self):
        self.personal_assistant_wrapper: Optional[PersonalAssistantMonitoringWrapper] = None
        self.backend_service = None
        self.monitoring_active = False
        
        # 事件处理器
        self.event_handlers: dict[str, list[Callable]] = {}
        
        # 监控数据缓存
        self.recent_events: list[MonitoringEvent] = []
        self.max_events = 1000
        
        logger.info("Monitoring Integration Service initialized")
    
    async def initialize(self, personal_assistant: PersonalAssistantService):
        """初始化监控集成服务"""
        try:
            # 创建PersonalAssistant监控包装器
            self.personal_assistant_wrapper = PersonalAssistantMonitoringWrapper(personal_assistant)
            
            # 添加事件处理回调
            self.personal_assistant_wrapper.add_monitoring_callback(self._handle_monitoring_event)
            
            # 获取后端服务
            self.backend_service = await get_backend_service()
            
            # 启动监控
            self.monitoring_active = True
            
            logger.info("Monitoring Integration Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Integration Service: {e}")
            raise
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type}")
    
    async def _handle_monitoring_event(self, event: MonitoringEvent):
        """处理监控事件"""
        try:
            # 添加到事件缓存
            self.recent_events.append(event)
            
            # 保持缓存大小
            if len(self.recent_events) > self.max_events:
                self.recent_events = self.recent_events[-self.max_events:]
            
            # 调用注册的事件处理器
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
            
            # 记录关键事件
            if event.event_type.endswith("_error"):
                logger.warning(f"Error event: {event.event_type} - {event.data.get('error', 'Unknown error')}")
            elif event.event_type.endswith("_complete"):
                response_time = event.data.get("response_time", 0)
                if response_time > 10:  # 响应时间超过10秒
                    logger.warning(f"Slow operation: {event.event_type} - {response_time:.2f}s")
        
        except Exception as e:
            logger.error(f"Error handling monitoring event: {e}")
    
    async def get_transparency_data(self) -> dict[str, Any]:
        """获取透明度数据"""
        try:
            transparency_data = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.monitoring_active,
                "personal_assistant_stats": {},
                "recent_events": [],
                "system_health": {}
            }
            
            # 获取PersonalAssistant统计
            if self.personal_assistant_wrapper:
                transparency_data["personal_assistant_stats"] = self.personal_assistant_wrapper.get_monitoring_statistics()
            
            # 获取最近事件
            transparency_data["recent_events"] = [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "source": event.source,
                    "session_id": event.session_id,
                    "data": event.data
                }
                for event in self.recent_events[-20:]  # 最近20个事件
            ]
            
            # 获取系统健康状态
            if self.backend_service:
                health_status = await self.backend_service.check_backend_health()
                transparency_data["system_health"] = {
                    service_name: {
                        "status": status.status.value,
                        "response_time": status.response_time,
                        "last_check": status.last_check.isoformat(),
                        "details": status.details
                    }
                    for service_name, status in health_status.items()
                }
            
            return transparency_data
            
        except Exception as e:
            logger.error(f"Error getting transparency data: {e}")
            return {"error": str(e)}
    
    async def log_llm_call(self, call_data: dict[str, Any]):
        """记录LLM调用（供外部调用）"""
        try:
            event = MonitoringEvent(
                event_id=str(uuid.uuid4()),
                event_type="llm_call",
                timestamp=datetime.now(),
                source="External",
                data=call_data
            )
            
            await self._handle_monitoring_event(event)
            
        except Exception as e:
            logger.error(f"Error logging LLM call: {e}")
    
    async def log_workflow_event(self, workflow_data: dict[str, Any]):
        """记录工作流事件（供外部调用）"""
        try:
            event = MonitoringEvent(
                event_id=str(uuid.uuid4()),
                event_type="workflow_event",
                timestamp=datetime.now(),
                source="External",
                data=workflow_data
            )
            
            await self._handle_monitoring_event(event)
            
        except Exception as e:
            logger.error(f"Error logging workflow event: {e}")
    
    def get_wrapped_personal_assistant(self) -> Optional[PersonalAssistantMonitoringWrapper]:
        """获取监控包装的PersonalAssistant"""
        return self.personal_assistant_wrapper
    
    async def shutdown(self):
        """关闭监控集成服务"""
        try:
            self.monitoring_active = False
            
            if self.backend_service:
                await self.backend_service.close()
            
            logger.info("Monitoring Integration Service shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# 全局监控集成服务实例
_monitoring_integration_service: Optional[MonitoringIntegrationService] = None


async def get_monitoring_integration_service() -> MonitoringIntegrationService:
    """获取监控集成服务实例"""
    global _monitoring_integration_service
    
    if _monitoring_integration_service is None:
        _monitoring_integration_service = MonitoringIntegrationService()
    
    return _monitoring_integration_service


async def initialize_monitoring_integration(personal_assistant: PersonalAssistantService) -> MonitoringIntegrationService:
    """初始化监控集成"""
    service = await get_monitoring_integration_service()
    await service.initialize(personal_assistant)
    return service


async def cleanup_monitoring_integration():
    """清理监控集成服务"""
    global _monitoring_integration_service
    
    if _monitoring_integration_service:
        await _monitoring_integration_service.shutdown()
        _monitoring_integration_service = None