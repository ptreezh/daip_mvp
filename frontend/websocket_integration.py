#!/usr/bin/env python3
"""Personal Intelligence Hub - WebSocket实时通信集成

为双入口界面提供实时通信能力
支持多智能体辩论、状态监控、用户干预等功能
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from lona.html import Button, Div, Span, Widget

# 配置日志
logger = logging.getLogger(__name__)

# ============================================================================
# 消息类型定义
# ============================================================================

class WebSocketMessageType(Enum):
    """WebSocket消息类型"""
    # 基础通信
    CONNECTION = "connection"
    DISCONNECTION = "disconnection"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    
    # 聊天消息
    CHAT_MESSAGE = "chat_message"
    AGENT_MESSAGE = "agent_message"
    SYSTEM_MESSAGE = "system_message"
    
    # 状态更新
    STATUS_UPDATE = "status_update"
    AGENT_STATUS = "agent_status"
    WORKFLOW_STATUS = "workflow_status"
    
    # Forum相关
    DEBATE_START = "debate_start"
    DEBATE_MESSAGE = "debate_message"
    DEBATE_END = "debate_end"
    CONSENSUS_UPDATE = "consensus_update"
    CONSENSUS_RESULT = "consensus_result"
    
    # Secretariat相关
    TASK_SUBMIT = "task_submit"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    
    # 用户交互
    USER_INTERVENTION = "user_intervention"
    USER_ACTION = "user_action"
    
    # 知识管理
    KNOWLEDGE_UPDATE = "knowledge_update"
    WIKI_UPDATE = "wiki_update"
    
    # 性能监控
    PERFORMANCE_METRICS = "performance_metrics"
    TOKEN_USAGE = "token_usage"
    MEMORY_USAGE = "memory_usage"

# ============================================================================
# 消息数据结构
# ============================================================================

@dataclass
class WebSocketMessage:
    """WebSocket消息数据结构"""
    message_id: str
    message_type: WebSocketMessageType
    payload: dict[str, Any]
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.message_id is None:
            self.message_id = f"msg_{uuid.uuid4().hex[:8]}"
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'WebSocketMessage':
        """从字典创建消息对象"""
        return cls(
            message_id=data["message_id"],
            message_type=WebSocketMessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
            user_id=data.get("user_id"),
            correlation_id=data.get("correlation_id")
        )

# ============================================================================
# WebSocket管理器
# ============================================================================

class LonaWebSocketManager:
    """Lona WebSocket管理器"""
    
    def __init__(self, backend_url: str = "ws://localhost:8000/ws"):
        self.backend_url = backend_url
        self.websocket = None
        self.is_connected = False
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.user_id = None
        
        # 消息处理器
        self.message_handlers: dict[WebSocketMessageType, list[Callable]] = {}
        
        # 消息队列
        self.outgoing_queue = asyncio.Queue()
        self.incoming_queue = asyncio.Queue()
        
        # 连接管理
        self.connection_retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5
        
        # 性能统计
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "connection_time": None,
            "last_heartbeat": None
        }
        
        logger.info(f"WebSocket管理器初始化完成: {backend_url}")
    
    async def connect(self, user_id: Optional[str] = None) -> bool:
        """建立WebSocket连接"""
        try:
            self.user_id = user_id
            
            logger.info(f"尝试连接到WebSocket服务器: {self.backend_url}")
            
            # 模拟连接成功（实际项目中需要使用真实的WebSocket库）
            await asyncio.sleep(0.5)
            self.is_connected = True
            self.connection_retry_count = 0
            self.stats["connection_time"] = datetime.now()
            
            logger.info("WebSocket连接成功")
            
            # 发送连接消息
            await self.send_message(WebSocketMessage(
                message_id=f"conn_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.CONNECTION,
                payload={
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                    "client_info": {
                        "user_agent": "Lona Web Client",
                        "version": "1.0.0"
                    }
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.user_id
            ))
            
            # 启动后台任务
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._heartbeat_sender())
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self.is_connected = False
            
            # 重试连接
            if self.connection_retry_count < self.max_retries:
                self.connection_retry_count += 1
                logger.info(f"将在{self.retry_delay}秒后重试连接 ({self.connection_retry_count}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.connect(user_id)
            
            return False
    
    async def disconnect(self):
        """断开WebSocket连接"""
        try:
            if self.is_connected:
                # 发送断开连接消息
                await self.send_message(WebSocketMessage(
                    message_id=f"disc_{uuid.uuid4().hex[:8]}",
                    message_type=WebSocketMessageType.DISCONNECTION,
                    payload={
                        "reason": "user_disconnect"
                    },
                    timestamp=datetime.now(),
                    session_id=self.session_id,
                    user_id=self.user_id
                ))
            
            self.is_connected = False
            logger.info("WebSocket连接已断开")
            
        except Exception as e:
            logger.error(f"断开连接时出错: {e}")
    
    async def send_message(self, message: WebSocketMessage) -> bool:
        """发送消息"""
        if not self.is_connected:
            logger.warning("WebSocket未连接，消息加入队列")
            await self.outgoing_queue.put(message)
            return False
        
        try:
            await self.outgoing_queue.put(message)
            self.stats["messages_sent"] += 1
            logger.debug(f"消息已加入发送队列: {message.message_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    def register_handler(self, message_type: WebSocketMessageType, handler: Callable):
        """注册消息处理器"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logger.info(f"注册消息处理器: {message_type.value}")
    
    async def _message_processor(self):
        """消息处理器任务"""
        while self.is_connected:
            try:
                # 处理发送队列
                if not self.outgoing_queue.empty():
                    message = await self.outgoing_queue.get()
                    await self._send_to_backend(message)
                
                # 处理接收队列
                if not self.incoming_queue.empty():
                    message = await self.incoming_queue.get()
                    await self._process_message(message)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"消息处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _send_to_backend(self, message: WebSocketMessage):
        """发送消息到后端（模拟）"""
        try:
            # 模拟网络延迟
            await asyncio.sleep(0.1)
            
            # 这里应该是实际的WebSocket发送逻辑
            # await self.websocket.send(json.dumps(message.to_dict()))
            
            logger.debug(f"消息发送到后端: {message.message_type.value}")
            
        except Exception as e:
            logger.error(f"发送到后端失败: {e}")
    
    async def _process_message(self, message: WebSocketMessage):
        """处理接收到的消息"""
        try:
            self.stats["messages_received"] += 1
            
            # 调用相应的处理器
            if message.message_type in self.message_handlers:
                for handler in self.message_handlers[message.message_type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"消息处理器执行失败 {message.message_type.value}: {e}")
            else:
                logger.warning(f"未找到处理器: {message.message_type.value}")
                
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    async def _heartbeat_sender(self):
        """心跳发送器"""
        while self.is_connected:
            try:
                await asyncio.sleep(30)  # 每30秒发送一次心跳
                
                heartbeat_message = WebSocketMessage(
                    message_id=f"hb_{uuid.uuid4().hex[:8]}",
                    message_type=WebSocketMessageType.HEARTBEAT,
                    payload={
                        "timestamp": datetime.now().isoformat(),
                        "stats": self.stats
                    },
                    timestamp=datetime.now(),
                    session_id=self.session_id,
                    user_id=self.user_id
                )
                
                await self.send_message(heartbeat_message)
                self.stats["last_heartbeat"] = datetime.now()
                
            except Exception as e:
                logger.error(f"心跳发送错误: {e}")
                await asyncio.sleep(5)
    
    def get_connection_status(self) -> dict[str, Any]:
        """获取连接状态"""
        return {
            "connected": self.is_connected,
            "backend_url": self.backend_url,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "retry_count": self.connection_retry_count,
            "stats": self.stats,
            "queue_sizes": {
                "outgoing": self.outgoing_queue.qsize(),
                "incoming": self.incoming_queue.qsize()
            }
        }
    
    async def simulate_incoming_message(self, message_type: WebSocketMessageType, payload: dict[str, Any]):
        """模拟接收消息（用于测试）"""
        message = WebSocketMessage(
            message_id=f"sim_{uuid.uuid4().hex[:8]}",
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(),
            session_id=self.session_id,
            user_id=self.user_id
        )
        await self.incoming_queue.put(message)

# ============================================================================
# Forum辩论实时通信组件
# ============================================================================

class ForumWebSocketIntegration(Widget):
    """Forum辩论WebSocket集成组件"""
    
    def __init__(self, websocket_manager: LonaWebSocketManager, session_id: str):
        super().__init__()
        self.ws_manager = websocket_manager
        self.session_id = session_id
        self.debate_id = None
        self.agents = []
        self.consensus_score = 0.0
        
        # 注册消息处理器
        self._setup_handlers()
        
        # UI组件
        self.status_indicator = Div(_class="connection-status")
        self.agents_list = Div(_class="agents-list")
        self.consensus_display = Div(_class="consensus-display")
        
        self._update_status_display()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        self.ws_manager.register_handler(WebSocketMessageType.AGENT_MESSAGE, self._handle_agent_message)
        self.ws_manager.register_handler(WebSocketMessageType.CONSENSUS_UPDATE, self._handle_consensus_update)
        self.ws_manager.register_handler(WebSocketMessageType.CONSENSUS_RESULT, self._handle_consensus_result)
        self.ws_manager.register_handler(WebSocketMessageType.DEBATE_START, self._handle_debate_start)
        self.ws_manager.register_handler(WebSocketMessageType.DEBATE_END, self._handle_debate_end)
    
    async def _handle_agent_message(self, message: WebSocketMessage):
        """处理代理消息"""
        try:
            payload = message.payload
            agent_name = payload.get("agent_name", "Unknown Agent")
            content = payload.get("content", "")
            
            # 更新代理列表
            if agent_name not in self.agents:
                self.agents.append(agent_name)
            
            # 创建消息UI
            agent_message = Div(
                Div(
                    Span(f"🤖 {agent_name}", _class="agent-name"),
                    Span(content, _class="agent-content"),
                    Span(
                        message.timestamp.strftime("%H:%M:%S"),
                        _class="message-timestamp"
                    ),
                    _class="agent-message"
                ),
                _class="message-container"
            )
            
            # 添加到消息历史（通过事件通知父组件）
            self.fire_event("agent_message_received", {
                "message_element": agent_message,
                "agent_name": agent_name,
                "content": content
            })
            
        except Exception as e:
            logger.error(f"处理代理消息失败: {e}")
    
    async def _handle_consensus_update(self, message: WebSocketMessage):
        """处理共识更新"""
        try:
            payload = message.payload
            self.consensus_score = payload.get("consensus_score", 0.0)
            
            # 更新共识显示
            self._update_consensus_display()
            
            # 通知父组件
            self.fire_event("consensus_updated", {
                "score": self.consensus_score,
                "details": payload
            })
            
        except Exception as e:
            logger.error(f"处理共识更新失败: {e}")
    
    async def _handle_consensus_result(self, message: WebSocketMessage):
        """处理共识结果"""
        try:
            payload = message.payload
            consensus_result = payload.get("result", "")
            confidence = payload.get("confidence", 0.0)
            
            # 创建共识结果UI
            result_element = Div(
                Div(
                    Span("🎯 共识结果", _class="result-title"),
                    Span(consensus_result, _class="result-content"),
                    Span(f"置信度: {confidence:.2f}", _class="confidence-score"),
                    _class="consensus-result-card"
                ),
                _class="message-container"
            )
            
            # 通知父组件
            self.fire_event("consensus_result_received", {
                "result_element": result_element,
                "result": consensus_result,
                "confidence": confidence
            })
            
        except Exception as e:
            logger.error(f"处理共识结果失败: {e}")
    
    async def _handle_debate_start(self, message: WebSocketMessage):
        """处理辩论开始"""
        try:
            payload = message.payload
            self.debate_id = payload.get("debate_id")
            self.agents = payload.get("agents", [])
            
            # 更新代理列表显示
            self._update_agents_list()
            
            # 通知父组件
            self.fire_event("debate_started", {
                "debate_id": self.debate_id,
                "agents": self.agents,
                "topic": payload.get("topic")
            })
            
        except Exception as e:
            logger.error(f"处理辩论开始失败: {e}")
    
    async def _handle_debate_end(self, message: WebSocketMessage):
        """处理辩论结束"""
        try:
            payload = message.payload
            reason = payload.get("reason", "unknown")
            
            # 通知父组件
            self.fire_event("debate_ended", {
                "debate_id": self.debate_id,
                "reason": reason,
                "final_stats": payload.get("stats", {})
            })
            
            # 重置状态
            self.debate_id = None
            self.consensus_score = 0.0
            
        except Exception as e:
            logger.error(f"处理辩论结束失败: {e}")
    
    async def start_debate(self, topic: str, agents: list[str]):
        """开始辩论"""
        try:
            message = WebSocketMessage(
                message_id=f"start_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.DEBATE_START,
                payload={
                    "topic": topic,
                    "agents": agents,
                    "session_id": self.session_id
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.ws_manager.user_id
            )
            
            await self.ws_manager.send_message(message)
            
        except Exception as e:
            logger.error(f"开始辩论失败: {e}")
    
    async def send_user_message(self, content: str):
        """发送用户消息"""
        try:
            message = WebSocketMessage(
                message_id=f"user_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.CHAT_MESSAGE,
                payload={
                    "content": content,
                    "debate_id": self.debate_id,
                    "session_id": self.session_id
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.ws_manager.user_id
            )
            
            await self.ws_manager.send_message(message)
            
        except Exception as e:
            logger.error(f"发送用户消息失败: {e}")
    
    async def request_consensus(self):
        """请求共识计算"""
        try:
            message = WebSocketMessage(
                message_id=f"consensus_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.CONSENSUS_UPDATE,
                payload={
                    "action": "request_consensus",
                    "debate_id": self.debate_id,
                    "session_id": self.session_id
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.ws_manager.user_id
            )
            
            await self.ws_manager.send_message(message)
            
        except Exception as e:
            logger.error(f"请求共识失败: {e}")
    
    def _update_status_display(self):
        """更新状态显示"""
        status = self.ws_manager.get_connection_status()
        
        if status["connected"]:
            self.status_indicator.set_text("🟢 已连接")
            self.status_indicator.set_class("connection-status connected")
        else:
            self.status_indicator.set_text("🔴 未连接")
            self.status_indicator.set_class("connection-status disconnected")
    
    def _update_agents_list(self):
        """更新代理列表显示"""
        self.agents_list.clear()
        
        for agent in self.agents:
            agent_item = Div(
                Span("🤖", _class="agent-icon"),
                Span(agent, _class="agent-name"),
                Span("●", _class="agent-status active"),
                _class="agent-item"
            )
            self.agents_list.append(agent_item)
    
    def _update_consensus_display(self):
        """更新共识显示"""
        self.consensus_display.clear()
        
        consensus_element = Div(
            Div(
                Span("共识度", _class="consensus-label"),
                Span(f"{self.consensus_score:.2f}", _class="consensus-value"),
                _class="consensus-header"
            ),
            Div(
                Div(
                    _class="consensus-bar-fill",
                    style=f"width: {self.consensus_score * 100}%"
                ),
                _class="consensus-bar"
            ),
            _class="consensus-meter"
        )
        
        self.consensus_display.append(consensus_element)
    
    def render(self) -> Div:
        """渲染组件"""
        return Div(
            Div(
                Span("连接状态:", _class="status-label"),
                self.status_indicator,
                _class="connection-status-container"
            ),
            
            Div(
                H4("活跃代理", _class="section-title"),
                self.agents_list,
                _class="agents-section"
            ),
            
            Div(
                H4("共识状态", _class="section-title"),
                self.consensus_display,
                _class="consensus-section"
            ),
            
            _class="forum-websocket-integration"
        )

# ============================================================================
# Secretariat实时通信组件
# ============================================================================

class SecretariatWebSocketIntegration(Widget):
    """Secretariat WebSocket集成组件"""
    
    def __init__(self, websocket_manager: LonaWebSocketManager, session_id: str):
        super().__init__()
        self.ws_manager = websocket_manager
        self.session_id = session_id
        self.current_task = None
        
        # 注册消息处理器
        self._setup_handlers()
        
        # UI组件
        self.task_status = Div(_class="task-status")
        self.progress_indicator = Div(_class="progress-indicator")
        self.notification_area = Div(_class="notification-area")
        
        self._update_status_display()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        self.ws_manager.register_handler(WebSocketMessageType.TASK_UPDATE, self._handle_task_update)
        self.ws_manager.register_handler(WebSocketMessageType.TASK_COMPLETE, self._handle_task_complete)
        self.ws_manager.register_handler(WebSocketMessageType.STATUS_UPDATE, self._handle_status_update)
        self.ws_manager.register_handler(WebSocketMessageType.PERFORMANCE_METRICS, self._handle_performance_metrics)
    
    async def _handle_task_update(self, message: WebSocketMessage):
        """处理任务更新"""
        try:
            payload = message.payload
            task_id = payload.get("task_id")
            status = payload.get("status")
            progress = payload.get("progress", 0)
            
            if task_id == self.current_task:
                self._update_task_status(status, progress)
            
            # 通知父组件
            self.fire_event("task_updated", {
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "details": payload
            })
            
        except Exception as e:
            logger.error(f"处理任务更新失败: {e}")
    
    async def _handle_task_complete(self, message: WebSocketMessage):
        """处理任务完成"""
        try:
            payload = message.payload
            task_id = payload.get("task_id")
            result = payload.get("result", "")
            
            # 创建完成通知
            notification = Div(
                Div(
                    Span("✅ 任务完成", _class="notification-title"),
                    Span(result, _class="notification-content"),
                    Button(
                        "查看详情",
                        _class="btn btn-sm",
                        handle_click=lambda e: self.fire_event("view_task_details", {"task_id": task_id})
                    ),
                    _class="notification-item success"
                ),
                _class="notification-container"
            )
            
            self.notification_area.append(notification)
            
            # 通知父组件
            self.fire_event("task_completed", {
                "task_id": task_id,
                "result": result,
                "details": payload
            })
            
            # 重置当前任务
            self.current_task = None
            self._update_task_status("completed", 100)
            
        except Exception as e:
            logger.error(f"处理任务完成失败: {e}")
    
    async def _handle_status_update(self, message: WebSocketMessage):
        """处理状态更新"""
        try:
            payload = message.payload
            
            # 更新系统状态显示
            self._update_system_status(payload)
            
            # 通知父组件
            self.fire_event("system_status_updated", payload)
            
        except Exception as e:
            logger.error(f"处理状态更新失败: {e}")
    
    async def _handle_performance_metrics(self, message: WebSocketMessage):
        """处理性能指标"""
        try:
            payload = message.payload
            
            # 更新性能显示
            self._update_performance_display(payload)
            
            # 通知父组件
            self.fire_event("performance_metrics_updated", payload)
            
        except Exception as e:
            logger.error(f"处理性能指标失败: {e}")
    
    async def submit_task(self, task_data: dict[str, Any]):
        """提交任务"""
        try:
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            self.current_task = task_id
            
            message = WebSocketMessage(
                message_id=f"submit_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.TASK_SUBMIT,
                payload={
                    "task_id": task_id,
                    "task_data": task_data,
                    "session_id": self.session_id
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.ws_manager.user_id
            )
            
            await self.ws_manager.send_message(message)
            
            # 更新任务状态
            self._update_task_status("submitted", 0)
            
        except Exception as e:
            logger.error(f"提交任务失败: {e}")
    
    async def request_status_update(self):
        """请求状态更新"""
        try:
            message = WebSocketMessage(
                message_id=f"status_{uuid.uuid4().hex[:8]}",
                message_type=WebSocketMessageType.STATUS_UPDATE,
                payload={
                    "action": "request_status",
                    "session_id": self.session_id
                },
                timestamp=datetime.now(),
                session_id=self.session_id,
                user_id=self.ws_manager.user_id
            )
            
            await self.ws_manager.send_message(message)
            
        except Exception as e:
            logger.error(f"请求状态更新失败: {e}")
    
    def _update_status_display(self):
        """更新状态显示"""
        status = self.ws_manager.get_connection_status()
        
        if status["connected"]:
            connection_text = "🟢 已连接"
            connection_class = "connection-status connected"
        else:
            connection_text = "🔴 未连接"
            connection_class = "connection-status disconnected"
        
        self.task_status.clear()
        self.task_status.append(Div(
            Span("连接状态:", _class="status-label"),
            Span(connection_text, _class=connection_class),
            _class="status-row"
        ))
    
    def _update_task_status(self, status: str, progress: int):
        """更新任务状态"""
        self.progress_indicator.clear()
        
        progress_element = Div(
            Div(
                Span("任务进度", _class="progress-label"),
                Span(f"{progress}%", _class="progress-value"),
                _class="progress-header"
            ),
            Div(
                Div(
                    _class="progress-bar-fill",
                    style=f"width: {progress}%"
                ),
                _class="progress-bar"
            ),
            Div(
                Span(f"状态: {status}", _class="task-status-text"),
                _class="task-info"
            ),
            _class="progress-container"
        )
        
        self.progress_indicator.append(progress_element)
    
    def _update_system_status(self, status_data: dict[str, Any]):
        """更新系统状态显示"""
        # 可以在这里添加更多状态显示逻辑
        pass
    
    def _update_performance_display(self, metrics: dict[str, Any]):
        """更新性能显示"""
        # 可以在这里添加性能指标显示逻辑
        pass
    
    def render(self) -> Div:
        """渲染组件"""
        return Div(
            Div(
                H4("任务状态", _class="section-title"),
                self.task_status,
                self.progress_indicator,
                _class="task-section"
            ),
            
            Div(
                H4("通知", _class="section-title"),
                self.notification_area,
                _class="notification-section"
            ),
            
            _class="secretariat-websocket-integration"
        )

# ============================================================================
# 全局WebSocket管理器实例
# ============================================================================

# 创建全局WebSocket管理器实例
global_websocket_manager = LonaWebSocketManager()

# ============================================================================
# 使用示例
# ============================================================================

async def example_usage():
    """使用示例"""
    # 连接WebSocket
    await global_websocket_manager.connect(user_id="example_user")
    
    # 创建Forum集成组件
    forum_integration = ForumWebSocketIntegration(global_websocket_manager, "example_session")
    
    # 创建Secretariat集成组件
    secretariat_integration = SecretariatWebSocketIntegration(global_websocket_manager, "example_session")
    
    # 开始辩论
    await forum_integration.start_debate(
        topic="人工智能的伦理问题",
        agents=["伦理学家", "技术专家", "社会学家"]
    )
    
    # 提交任务
    await secretariat_integration.submit_task({
        "type": "analysis",
        "content": "分析市场趋势",
        "priority": "high"
    })
    
    # 获取连接状态
    status = global_websocket_manager.get_connection_status()
    print(f"连接状态: {status}")

if __name__ == "__main__":
    # 示例用法
    asyncio.run(example_usage())