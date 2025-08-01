#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
透明度监控组件 - 实时状态监控增强版本

实时显示系统内部运作过程，提供完全透明度
支持真实LLM调用监控、工作流状态跟踪和性能指标
集成WebSocket实时通信，支持系统状态实时更新
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from lona.html.widget import Widget
from lona.html import HTML, Div, H3, P, Span, Pre, Code, Button

logger = logging.getLogger(__name__)


class TransparencyMonitor(Widget):
    """透明度监控组件 - 实时状态监控增强版本"""
    
    def __init__(self, websocket_manager=None, realtime_manager=None):
        super().__init__()
        
        # WebSocket和实时管理器
        self.websocket_manager = websocket_manager
        self.realtime_manager = realtime_manager
        
        # 真实数据存储
        self.active_agents = []
        self.llm_calls = []
        self.workflow_executions = []
        self.system_status = {
            "backend_connected": False,
            "llm_services": {},
            "role_library_status": "unknown",
            "workflow_engine_status": "unknown"
        }
        self.system_metrics = {
            "total_tokens": 0,
            "total_cost": 0.0,
            "active_sessions": 0,
            "error_count": 0,
            "uptime": datetime.now(),
            "performance_metrics": {
                "avg_response_time": 0.0,
                "success_rate": 100.0,
                "throughput": 0.0
            }
        }
        
        # 实时监控状态
        self.monitoring_active = False
        self.auto_refresh_enabled = True
        self.refresh_interval = 2  # 2秒刷新间隔
        self.monitoring_task = None
        
        # 回调函数
        self.on_agent_update = None
        self.on_llm_call_logged = None
        self.on_workflow_update = None
        self.on_system_status_change = None
        
        # 初始化示例数据
        self._initialize_demo_data()
        
        # 设置WebSocket回调
        self._setup_websocket_callbacks()
    
    def _setup_websocket_callbacks(self):
        """设置WebSocket回调"""
        if self.realtime_manager:
            self.realtime_manager.register_component_callback("agent_status", self.update_agent_status)
            self.realtime_manager.register_component_callback("workflow", self.update_workflow_status)
            self.realtime_manager.register_component_callback("system_status", self.update_system_status)
            logger.info("WebSocket回调已设置")
    
    def _initialize_demo_data(self):
        """初始化演示数据"""
        self.active_agents = [
            {
                "id": "agent_1",
                "name": "Dr. 理性分析师",
                "status": "idle",
                "framework": "科学推理",
                "last_activity": datetime.now(),
                "confidence": 0.87,
                "current_task": "待命中",
                "processing_time": 0.0
            },
            {
                "id": "agent_2", 
                "name": "创意直觉师",
                "status": "thinking",
                "framework": "直觉洞察",
                "last_activity": datetime.now(),
                "confidence": 0.92,
                "current_task": "分析用户输入",
                "processing_time": 15.2
            }
        ]
        
        self.llm_calls = [
            {
                "id": "call_1",
                "model": "llama3:instruct",
                "input_tokens": 152,
                "output_tokens": 287,
                "response_time": 2.3,
                "cost": 0.0023,
                "timestamp": datetime.now(),
                "success": True,
                "provider": "ollama"
            },
            {
                "id": "call_2",
                "model": "gpt-4",
                "input_tokens": 89,
                "output_tokens": 156,
                "response_time": 1.8,
                "cost": 0.0156,
                "timestamp": datetime.now(),
                "success": True,
                "provider": "openai"
            }
        ]
        
        # 初始化系统状态
        self.system_status = {
            "backend_connected": True,
            "llm_services": {
                "ollama": {"status": "healthy", "response_time": 1.2},
                "openai": {"status": "healthy", "response_time": 0.8}
            },
            "role_library_status": "loaded",
            "workflow_engine_status": "ready"
        }
    
    async def start_monitoring(self):
        """启动实时监控"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("实时监控已启动")
    
    async def stop_monitoring(self):
        """停止实时监控"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
        logger.info("实时监控已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.monitoring_active:
            try:
                await self._update_system_metrics()
                await self._check_system_health()
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(5)
    
    async def _update_system_metrics(self):
        """更新系统指标"""
        try:
            # 计算性能指标
            if self.llm_calls:
                recent_calls = [
                    call for call in self.llm_calls
                    if (datetime.now() - call["timestamp"]).total_seconds() <= 300  # 最近5分钟
                ]
                
                if recent_calls:
                    avg_response_time = sum(call["response_time"] for call in recent_calls) / len(recent_calls)
                    success_rate = (sum(1 for call in recent_calls if call["success"]) / len(recent_calls)) * 100
                    throughput = len(recent_calls) / 5.0  # 每分钟调用数
                    
                    self.system_metrics["performance_metrics"] = {
                        "avg_response_time": avg_response_time,
                        "success_rate": success_rate,
                        "throughput": throughput
                    }
                else:
                    # 如果没有最近的调用，使用所有调用计算
                    avg_response_time = sum(call["response_time"] for call in self.llm_calls) / len(self.llm_calls)
                    success_rate = (sum(1 for call in self.llm_calls if call["success"]) / len(self.llm_calls)) * 100
                    throughput = len(self.llm_calls) / 5.0  # 每分钟调用数
                    
                    self.system_metrics["performance_metrics"] = {
                        "avg_response_time": avg_response_time,
                        "success_rate": success_rate,
                        "throughput": throughput
                    }
            
            # 更新代理处理时间
            for agent in self.active_agents:
                if agent["status"] in ["thinking", "processing"]:
                    agent["processing_time"] = (datetime.now() - agent["last_activity"]).total_seconds()
        
        except Exception as e:
            logger.error(f"更新系统指标失败: {e}")
    
    async def _check_system_health(self):
        """检查系统健康状态"""
        try:
            # 检查后端连接
            if self.websocket_manager:
                connection_status = self.websocket_manager.get_connection_status()
                self.system_status["backend_connected"] = connection_status.get("connected", False)
            
            # 检查LLM服务状态（模拟）
            for service in self.system_status["llm_services"]:
                # 这里应该是真实的健康检查
                # 现在使用模拟数据
                pass
        
        except Exception as e:
            logger.error(f"系统健康检查失败: {e}")
    
    async def update_agent_status(self, data):
        """更新代理状态（WebSocket回调）"""
        try:
            agent_id = data.get("agent_id")
            status = data.get("status")
            framework = data.get("framework")
            confidence = data.get("confidence", 0.0)
            current_task = data.get("current_task", "")
            
            # 查找并更新对应代理
            agent_found = False
            for agent in self.active_agents:
                if agent.get("id") == agent_id or agent["name"] == data.get("name"):
                    agent["status"] = status
                    agent["last_activity"] = datetime.now()
                    agent["processing_time"] = 0.0  # 重置处理时间
                    if framework:
                        agent["framework"] = framework
                    if confidence:
                        agent["confidence"] = confidence
                    if current_task:
                        agent["current_task"] = current_task
                    agent_found = True
                    break
            
            if not agent_found:
                # 添加新代理
                self.active_agents.append({
                    "id": agent_id or f"agent_{len(self.active_agents) + 1}",
                    "name": data.get("name", f"Agent-{agent_id}"),
                    "status": status,
                    "framework": framework or "未知",
                    "last_activity": datetime.now(),
                    "confidence": confidence,
                    "current_task": current_task or "待命中",
                    "processing_time": 0.0
                })
            
            # 触发代理更新回调
            if self.on_agent_update:
                try:
                    await self.on_agent_update(data)
                except Exception as e:
                    logger.error(f"代理更新回调失败: {e}")
            
            logger.info(f"代理状态已更新: {agent_id} -> {status}")
        except Exception as e:
            logger.error(f"更新代理状态失败: {e}")
    
    async def update_system_status(self, data):
        """更新系统状态（WebSocket回调）"""
        try:
            status_type = data.get("type")
            status_data = data.get("data", {})
            
            if status_type == "backend_connection":
                self.system_status["backend_connected"] = status_data.get("connected", False)
            elif status_type == "llm_service":
                service_name = status_data.get("service")
                if service_name:
                    self.system_status["llm_services"][service_name] = {
                        "status": status_data.get("status", "unknown"),
                        "response_time": status_data.get("response_time", 0.0)
                    }
            elif status_type == "role_library":
                self.system_status["role_library_status"] = status_data.get("status", "unknown")
            elif status_type == "workflow_engine":
                self.system_status["workflow_engine_status"] = status_data.get("status", "unknown")
            
            # 触发系统状态变更回调
            if self.on_system_status_change:
                try:
                    await self.on_system_status_change(self.system_status)
                except Exception as e:
                    logger.error(f"系统状态变更回调失败: {e}")
            
            logger.info(f"系统状态已更新: {status_type}")
        except Exception as e:
            logger.error(f"更新系统状态失败: {e}")
    
    async def log_llm_call(self, call_data: Dict[str, Any]):
        """记录LLM调用"""
        try:
            call_record = {
                "id": call_data.get("id", f"call_{len(self.llm_calls) + 1}"),
                "model": call_data.get("model", "unknown"),
                "input_tokens": call_data.get("input_tokens", 0),
                "output_tokens": call_data.get("output_tokens", 0),
                "response_time": call_data.get("response_time", 0.0),
                "cost": call_data.get("cost", 0.0),
                "timestamp": datetime.now(),
                "success": call_data.get("success", True),
                "error_message": call_data.get("error_message")
            }
            
            self.llm_calls.append(call_record)
            
            # 更新系统指标
            self.system_metrics["total_tokens"] += call_record["input_tokens"] + call_record["output_tokens"]
            self.system_metrics["total_cost"] += call_record["cost"]
            if not call_record["success"]:
                self.system_metrics["error_count"] += 1
            
            # 保持最近50条记录
            if len(self.llm_calls) > 50:
                self.llm_calls = self.llm_calls[-50:]
            
            # 触发LLM调用记录回调
            if self.on_llm_call_logged:
                try:
                    await self.on_llm_call_logged(call_record)
                except Exception as e:
                    logger.error(f"LLM调用记录回调失败: {e}")
        except Exception as e:
            logger.error(f"记录LLM调用失败: {e}")
    
    async def log_workflow_start(self, workflows: List[str], roles: List[str]):
        """记录工作流开始"""
        try:
            workflow_record = {
                "id": f"workflow_{len(self.workflow_executions) + 1}",
                "workflows": workflows,
                "roles": roles,
                "status": "started",
                "start_time": datetime.now(),
                "steps": []
            }
            
            self.workflow_executions.append(workflow_record)
        except Exception as e:
            logger.error(f"记录工作流开始失败: {e}")
    
    async def update_workflow_status(self, workflow_data: Dict[str, Any]):
        """更新工作流状态（WebSocket回调）"""
        try:
            workflow_id = workflow_data.get("workflow_id")
            status = workflow_data.get("status")
            workflow_type = workflow_data.get("type")
            progress = workflow_data.get("progress", 0)
            
            # 查找现有工作流或创建新的
            workflow_found = False
            for workflow in self.workflow_executions:
                if workflow.get("id") == workflow_id:
                    workflow["status"] = status
                    workflow["progress"] = progress
                    workflow["last_update"] = datetime.now()
                    if status == "completed":
                        workflow["end_time"] = datetime.now()
                        workflow["result"] = workflow_data.get("result", {})
                    workflow_found = True
                    break
            
            if not workflow_found and status == "started":
                # 创建新的工作流记录
                new_workflow = {
                    "id": workflow_id or f"workflow_{len(self.workflow_executions) + 1}",
                    "type": workflow_type or "unknown",
                    "workflows": workflow_data.get("workflows", []),
                    "roles": workflow_data.get("roles", []),
                    "status": status,
                    "progress": progress,
                    "start_time": datetime.now(),
                    "last_update": datetime.now(),
                    "steps": workflow_data.get("steps", [])
                }
                self.workflow_executions.append(new_workflow)
            
            # 触发工作流更新回调
            if self.on_workflow_update:
                try:
                    await self.on_workflow_update(workflow_data)
                except Exception as e:
                    logger.error(f"工作流更新回调失败: {e}")
            
            logger.info(f"工作流状态已更新: {workflow_id} -> {status}")
        except Exception as e:
            logger.error(f"更新工作流状态失败: {e}")
    
    async def log_user_interaction(self, message):
        """记录用户交互"""
        try:
            # 更新活跃会话数
            self.system_metrics["active_sessions"] = 1  # 简化版本
        except Exception as e:
            logger.error(f"记录用户交互失败: {e}")
    
    async def log_error(self, error_message: str):
        """记录错误"""
        try:
            self.system_metrics["error_count"] += 1
            
            # 添加错误记录到LLM调用中（作为失败的调用）
            error_record = {
                "id": f"error_{datetime.now().timestamp()}",
                "model": "system",
                "input_tokens": 0,
                "output_tokens": 0,
                "response_time": 0.0,
                "cost": 0.0,
                "timestamp": datetime.now(),
                "success": False,
                "error_message": error_message
            }
            
            self.llm_calls.append(error_record)
        except Exception as e:
            logger.error(f"记录错误失败: {e}")
    
    def _render_agent_status_badge(self, status: str) -> str:
        """渲染代理状态徽章样式"""
        status_styles = {
            "idle": "background: #6c757d; color: white;",
            "thinking": "background: #ffc107; color: black;",
            "processing": "background: #17a2b8; color: white;",
            "completed": "background: #28a745; color: white;",
            "error": "background: #dc3545; color: white;"
        }
        return status_styles.get(status, "background: #6c757d; color: white;")
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """格式化时间戳"""
        return timestamp.strftime("%H:%M:%S")
    
    def _calculate_uptime(self) -> str:
        """计算系统运行时间"""
        uptime_delta = datetime.now() - self.system_metrics["uptime"]
        hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _render_system_health_indicator(self) -> HTML:
        """渲染系统健康指示器"""
        backend_status = "🟢 已连接" if self.system_status["backend_connected"] else "🔴 断开"
        
        llm_status_indicators = []
        for service, info in self.system_status["llm_services"].items():
            status_icon = "🟢" if info["status"] == "healthy" else "🟡" if info["status"] == "degraded" else "🔴"
            llm_status_indicators.append(
                Span(f"{status_icon} {service.upper()}", style="margin-right: 10px; font-size: 0.8rem;")
            )
        
        return Div(
            P("🏥 系统健康状态", style="font-weight: 600; margin-bottom: 8px; color: #2f3542;"),
            Div(
                Span(f"后端: {backend_status}", style="margin-right: 15px; font-size: 0.85rem;"),
                *llm_status_indicators,
                style="margin-bottom: 5px;"
            ),
            Div(
                Span(f"角色库: {self.system_status['role_library_status']}", style="margin-right: 15px; font-size: 0.85rem;"),
                Span(f"工作流引擎: {self.system_status['workflow_engine_status']}", style="font-size: 0.85rem;"),
                style="margin-bottom: 10px;"
            ),
            style="padding: 10px; background: #f8f9fa; border-radius: 6px; margin-bottom: 15px;"
        )
    
    def _render_performance_metrics(self) -> HTML:
        """渲染性能指标"""
        metrics = self.system_metrics["performance_metrics"]
        
        return Div(
            P("⚡ 性能指标", style="font-weight: 600; margin-bottom: 8px; color: #2f3542;"),
            Div(
                Span(f"平均响应时间: {metrics['avg_response_time']:.2f}s", style="margin-right: 15px; font-size: 0.85rem;"),
                Span(f"成功率: {metrics['success_rate']:.1f}%", style="margin-right: 15px; font-size: 0.85rem;"),
                Span(f"吞吐量: {metrics['throughput']:.1f}/min", style="font-size: 0.85rem;"),
                style="display: flex; flex-wrap: wrap;"
            ),
            style="padding: 8px; background: #e8f5e8; border-radius: 6px; margin-bottom: 15px;"
        )
    
    def _render_monitoring_controls(self) -> HTML:
        """渲染监控控制按钮"""
        monitoring_status = "🟢 监控中" if self.monitoring_active else "⏸️ 已暂停"
        auto_refresh_status = "🔄 自动刷新" if self.auto_refresh_enabled else "⏹️ 手动刷新"
        
        return Div(
            P("🎛️ 监控控制", style="font-weight: 600; margin-bottom: 8px; color: #2f3542;"),
            Div(
                Span(monitoring_status, style="margin-right: 15px; font-size: 0.85rem;"),
                Span(auto_refresh_status, style="margin-right: 15px; font-size: 0.85rem;"),
                Span(f"刷新间隔: {self.refresh_interval}s", style="font-size: 0.85rem;"),
                style="margin-bottom: 8px;"
            ),
            style="padding: 8px; background: #fff3cd; border-radius: 6px; margin-bottom: 15px;"
        )

    def render(self) -> HTML:
        return Div(
            # 监控控制面板
            self._render_monitoring_controls(),
            
            # 系统健康状态
            self._render_system_health_indicator(),
            
            # 性能指标
            self._render_performance_metrics(),
            
            # 系统状态概览
            Div(
                P("📊 系统状态", style="font-weight: 600; margin-bottom: 10px; color: #2f3542;"),
                Div(
                    Span(f"运行时间: {self._calculate_uptime()}", style="font-size: 0.85rem; margin-right: 15px;"),
                    Span(f"活跃会话: {self.system_metrics['active_sessions']}", style="font-size: 0.85rem; margin-right: 15px;"),
                    Span(f"错误: {self.system_metrics['error_count']}", style="font-size: 0.85rem;"),
                    style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 15px;"
                )
            ),
            
            # 活跃代理状态
            Div(
                P("🤖 活跃代理", style="font-weight: 600; margin-bottom: 10px; color: #2f3542;"),
                *[
                    Div(
                        Div(
                            Span(agent["name"], style="font-weight: 500; display: block;"),
                            Span(
                                agent["status"], 
                                style=f"padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; {self._render_agent_status_badge(agent['status'])}"
                            ),
                            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;"
                        ),
                        P(f"框架: {agent['framework']}", style="font-size: 0.8rem; color: #6c757d; margin: 0;"),
                        P(f"当前任务: {agent.get('current_task', '待命中')}", style="font-size: 0.8rem; color: #495057; margin: 2px 0;"),
                        P(f"置信度: {agent.get('confidence', 0):.2f} | 处理时间: {agent.get('processing_time', 0):.1f}s", 
                          style="font-size: 0.75rem; color: #6c757d; margin: 2px 0;"),
                        P(f"最后活动: {self._format_timestamp(agent.get('last_activity', datetime.now()))}", 
                          style="font-size: 0.75rem; color: #6c757d; margin: 2px 0 0 0;"),
                        style="padding: 10px; border: 1px solid #e9ecef; border-radius: 8px; margin-bottom: 8px; background: white;"
                    )
                    for agent in self.active_agents
                ] if self.active_agents else [
                    P("暂无活跃代理", style="color: #6c757d; font-style: italic; text-align: center; padding: 20px;")
                ],
                style="margin-bottom: 20px;"
            ),
            
            # LLM调用监控
            Div(
                P("📡 LLM调用监控", style="font-weight: 600; margin-bottom: 10px; color: #2f3542;"),
                Div(
                    *[
                        Div(
                            Div(
                                Span(f"[{self._format_timestamp(call['timestamp'])}]", style="font-family: monospace; color: #6c757d; font-size: 0.8rem;"),
                                Span(call['model'], style="font-weight: 500; margin-left: 10px;"),
                                Span("✅" if call['success'] else "❌", style="margin-left: 10px;"),
                                style="margin-bottom: 3px;"
                            ),
                            P(f"输入: {call['input_tokens']} tokens | 输出: {call['output_tokens']} tokens", 
                              style="font-size: 0.8rem; color: #495057; margin: 0;"),
                            P(f"响应时间: {call['response_time']:.1f}s | 成本: ${call['cost']:.4f}", 
                              style="font-size: 0.8rem; color: #495057; margin: 0;"),
                            style="padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 6px;"
                        )
                        for call in self.llm_calls[-5:]  # 显示最近5条记录
                    ] if self.llm_calls else [
                        P("暂无LLM调用记录", style="color: #6c757d; font-style: italic; text-align: center; padding: 20px;")
                    ],
                    style="max-height: 200px; overflow-y: auto;"
                ),
                style="margin-bottom: 20px;"
            ),
            
            # 工作流执行状态
            Div(
                P("🔄 工作流执行", style="font-weight: 600; margin-bottom: 10px; color: #2f3542;"),
                *[
                    Div(
                        Div(
                            Span(f"工作流: {workflow.get('type', 'unknown')}", style="font-weight: 500;"),
                            Span(f"{workflow.get('progress', 0)}%", style="font-size: 0.8rem; color: #667eea; margin-left: 10px;"),
                            style="display: flex; justify-content: space-between; margin-bottom: 3px;"
                        ),
                        P(f"角色: {', '.join(workflow.get('roles', []))}", style="font-size: 0.85rem; color: #6c757d; margin: 2px 0;"),
                        P(f"状态: {workflow['status']} | 开始: {self._format_timestamp(workflow['start_time'])}", 
                          style="font-size: 0.8rem; color: #495057; margin: 0;"),
                        # 进度条
                        Div(
                            Div(
                                style=f"width: {workflow.get('progress', 0)}%; height: 4px; background: #667eea; border-radius: 2px; transition: width 0.3s;"
                            ),
                            style="width: 100%; height: 4px; background: #e9ecef; border-radius: 2px; margin-top: 5px;"
                        ),
                        style="padding: 8px; border-left: 4px solid #667eea; background: #f8f9fa; border-radius: 0 6px 6px 0; margin-bottom: 6px;"
                    )
                    for workflow in self.workflow_executions[-3:]  # 显示最近3个工作流
                ] if self.workflow_executions else [
                    P("暂无工作流执行记录", style="color: #6c757d; font-style: italic; text-align: center; padding: 20px;")
                ],
                style="margin-bottom: 20px;"
            ),
            
            # 统计汇总
            Div(
                P("📈 统计汇总", style="color: white; font-weight: 600; margin: 0 0 8px 0;"),
                Div(
                    Span(f"总Token: {self.system_metrics['total_tokens']:,}", style="color: white; font-size: 0.9rem; margin-right: 15px;"),
                    Span(f"总成本: ${self.system_metrics['total_cost']:.4f}", style="color: white; font-size: 0.9rem; margin-right: 15px;"),
                    style="display: flex; flex-wrap: wrap;"
                ),
                Div(
                    Span(f"调用次数: {len(self.llm_calls)}", style="color: white; font-size: 0.9rem; margin-right: 15px;"),
                    Span(f"成功率: {((len([c for c in self.llm_calls if c['success']]) / len(self.llm_calls)) * 100) if self.llm_calls else 100:.1f}%", 
                         style="color: white; font-size: 0.9rem;"),
                    style="display: flex; flex-wrap: wrap; margin-top: 5px;"
                ),
                style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px;"
            ),
            
            _class="transparency-monitor"
        )
