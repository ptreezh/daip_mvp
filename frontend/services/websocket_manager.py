#!/usr/bin/env python3
"""WebSocket管理器

基于Lona框架的WebSocket实时通信管理
支持与后端服务的实时数据同步和事件处理
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

# 配置日志
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket消息类型"""
    CHAT_MESSAGE = "chat_message"
    AGENT_STATUS = "agent_status"
    WORKFLOW_UPDATE = "workflow_update"
    WIKI_UPDATE = "wiki_update"
    TASK_UPDATE = "task_update"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


@dataclass
class WebSocketMessage:
    """WebSocket消息数据结构"""
    type: MessageType
    payload: dict[str, Any]
    timestamp: datetime = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'WebSocketMessage':
        """从字典创建消息对象"""
        return cls(
            type=MessageType(data["type"]),
            payload=data["payload"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data.get("session_id")
        )


class WebSocketEventHandler:
    """WebSocket事件处理器基类"""
    
    def __init__(self):
        self.handlers: dict[MessageType, list[Callable]] = {}
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """注册消息处理器"""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
        logger.info(f"注册处理器: {message_type.value}")
    
    async def handle_message(self, message: WebSocketMessage):
        """处理接收到的消息"""
        if message.type in self.handlers:
            for handler in self.handlers[message.type]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"处理消息失败 {message.type.value}: {e}")
        else:
            logger.warning(f"未找到处理器: {message.type.value}")


class LonaWebSocketManager:
    """Lona WebSocket管理器"""
    
    def __init__(self, backend_url: str = "ws://localhost:8000/ws"):
        self.backend_url = backend_url
        self.websocket = None
        self.is_connected = False
        self.event_handler = WebSocketEventHandler()
        self.connection_retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5  # 秒
        
        # 消息队列
        self.outgoing_queue = asyncio.Queue()
        self.incoming_queue = asyncio.Queue()
        
        # 会话管理
        self.active_sessions: dict[str, dict[str, Any]] = {}
        
        logger.info(f"WebSocket管理器初始化: {backend_url}")
    
    async def connect(self) -> bool:
        """建立WebSocket连接"""
        try:
            # 注意：这里使用模拟连接，实际项目中需要使用真实的WebSocket库
            # 如 websockets 或 Lona内置的WebSocket支持
            
            logger.info(f"尝试连接到: {self.backend_url}")
            
            # 模拟连接成功
            self.is_connected = True
            self.connection_retry_count = 0
            
            logger.info("WebSocket连接成功")
            
            # 启动消息处理任务
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._heartbeat())
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            self.is_connected = False
            
            # 重试连接
            if self.connection_retry_count < self.max_retries:
                self.connection_retry_count += 1
                logger.info(f"将在{self.retry_delay}秒后重试连接 ({self.connection_retry_count}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
                return await self.connect()
            
            return False
    
    async def disconnect(self):
        """断开WebSocket连接"""
        try:
            if self.websocket:
                # await self.websocket.close()
                pass
            
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
            # 将消息加入发送队列
            await self.outgoing_queue.put(message)
            logger.debug(f"消息已加入发送队列: {message.type.value}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    async def _message_processor(self):
        """消息处理器任务"""
        while True:
            try:
                # 处理发送队列
                if not self.outgoing_queue.empty():
                    message = await self.outgoing_queue.get()
                    await self._send_to_backend(message)
                
                # 处理接收队列
                if not self.incoming_queue.empty():
                    message = await self.incoming_queue.get()
                    await self.event_handler.handle_message(message)
                
                await asyncio.sleep(0.1)  # 避免CPU占用过高
                
            except Exception as e:
                logger.error(f"消息处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _send_to_backend(self, message: WebSocketMessage):
        """发送消息到后端"""
        try:
            # 模拟发送到后端
            logger.debug(f"发送到后端: {message.type.value}")
            
            # 这里应该是实际的WebSocket发送逻辑
            # await self.websocket.send(json.dumps(message.to_dict()))
            
        except Exception as e:
            logger.error(f"发送到后端失败: {e}")
    
    async def _heartbeat(self):
        """心跳检测"""
        while self.is_connected:
            try:
                # 发送心跳消息
                heartbeat_message = WebSocketMessage(
                    type=MessageType.SYSTEM_STATUS,
                    payload={"action": "heartbeat", "timestamp": datetime.now().isoformat()}
                )
                await self.send_message(heartbeat_message)
                
                await asyncio.sleep(30)  # 每30秒发送一次心跳
                
            except Exception as e:
                logger.error(f"心跳检测错误: {e}")
                await asyncio.sleep(5)
    
    def register_chat_handler(self, handler: Callable):
        """注册聊天消息处理器"""
        self.event_handler.register_handler(MessageType.CHAT_MESSAGE, handler)
    
    def register_agent_status_handler(self, handler: Callable):
        """注册代理状态处理器"""
        self.event_handler.register_handler(MessageType.AGENT_STATUS, handler)
    
    def register_workflow_handler(self, handler: Callable):
        """注册工作流更新处理器"""
        self.event_handler.register_handler(MessageType.WORKFLOW_UPDATE, handler)
    
    def register_wiki_handler(self, handler: Callable):
        """注册Wiki更新处理器"""
        self.event_handler.register_handler(MessageType.WIKI_UPDATE, handler)
    
    def register_task_handler(self, handler: Callable):
        """注册任务更新处理器"""
        self.event_handler.register_handler(MessageType.TASK_UPDATE, handler)
    
    async def simulate_incoming_message(self, message_type: MessageType, payload: dict[str, Any]):
        """模拟接收消息（用于测试）"""
        message = WebSocketMessage(
            type=message_type,
            payload=payload
        )
        await self.incoming_queue.put(message)
    
    def get_connection_status(self) -> dict[str, Any]:
        """获取连接状态"""
        return {
            "connected": self.is_connected,
            "backend_url": self.backend_url,
            "retry_count": self.connection_retry_count,
            "active_sessions": len(self.active_sessions),
            "outgoing_queue_size": self.outgoing_queue.qsize(),
            "incoming_queue_size": self.incoming_queue.qsize()
        }


class RealtimeUpdateManager:
    """实时更新管理器"""
    
    def __init__(self, websocket_manager: LonaWebSocketManager):
        self.ws_manager = websocket_manager
        self.component_callbacks: dict[str, list[Callable]] = {}
        
        # 注册各种消息处理器
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置消息处理器"""
        self.ws_manager.register_agent_status_handler(self._handle_agent_status)
        self.ws_manager.register_workflow_handler(self._handle_workflow_update)
        self.ws_manager.register_wiki_handler(self._handle_wiki_update)
        self.ws_manager.register_task_handler(self._handle_task_update)
    
    async def _handle_agent_status(self, message: WebSocketMessage):
        """处理代理状态更新"""
        logger.info(f"代理状态更新: {message.payload}")
        await self._notify_components("agent_status", message.payload)
    
    async def _handle_workflow_update(self, message: WebSocketMessage):
        """处理工作流更新"""
        logger.info(f"工作流更新: {message.payload}")
        await self._notify_components("workflow", message.payload)
    
    async def _handle_wiki_update(self, message: WebSocketMessage):
        """处理Wiki更新"""
        logger.info(f"Wiki更新: {message.payload}")
        await self._notify_components("wiki", message.payload)
    
    async def _handle_task_update(self, message: WebSocketMessage):
        """处理任务更新"""
        logger.info(f"任务更新: {message.payload}")
        await self._notify_components("task", message.payload)
    
    def register_component_callback(self, component_type: str, callback: Callable):
        """注册组件回调"""
        if component_type not in self.component_callbacks:
            self.component_callbacks[component_type] = []
        self.component_callbacks[component_type].append(callback)
    
    async def _notify_components(self, component_type: str, data: dict[str, Any]):
        """通知相关组件"""
        if component_type in self.component_callbacks:
            for callback in self.component_callbacks[component_type]:
                try:
                    await callback(data)
                except Exception as e:
                    logger.error(f"组件回调执行失败 {component_type}: {e}")


# 全局WebSocket管理器实例
websocket_manager = LonaWebSocketManager()
realtime_manager = RealtimeUpdateManager(websocket_manager)