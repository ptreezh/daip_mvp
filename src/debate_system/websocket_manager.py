#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket管理器

为多轮辩论系统提供实时通信支持。
处理客户端-服务器之间的双向通信，支持实时状态更新。

核心功能：
- WebSocket连接管理
- 消息路由和分发
- 实时状态同步
- 错误处理和重连
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket消息类型"""
    # 系统消息
    SYSTEM_STATUS = "system_status"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    
    # 辩论相关
    DEBATE_STARTED = "debate_started"
    DEBATE_ENDED = "debate_ended"
    DEBATE_STATUS = "debate_status"
    
    # 角色和对话
    AGENT_STATUS = "agent_status"
    AGENT_MESSAGE = "agent_message"
    DIALOGUE_UPDATE = "dialogue_update"
    
    # 工作流
    WORKFLOW_STATUS = "workflow_status"
    WORKFLOW_RESULT = "workflow_result"
    
    # 用户交互
    USER_MESSAGE = "user_message"
    USER_COMMAND = "user_command"
    
    # 监控数据
    MONITORING_DATA = "monitoring_data"
    PERFORMANCE_METRICS = "performance_metrics"


@dataclass
class WebSocketMessage:
    """WebSocket消息数据结构"""
    type: MessageType
    payload: Dict[str, Any]
    session_id: Optional[str] = None
    timestamp: datetime = None
    message_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "type": self.type.value,
            "payload": self.payload,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """从字典创建消息"""
        return cls(
            type=MessageType(data["type"]),
            payload=data["payload"],
            session_id=data.get("session_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            message_id=data.get("message_id")
        )


class WebSocketConnection:
    """WebSocket连接封装"""
    
    def __init__(self, websocket, session_id: str = None):
        self.websocket = websocket
        self.session_id = session_id or str(uuid.uuid4())
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.subscriptions: Set[MessageType] = set()
        self.metadata: Dict[str, Any] = {}
        self.message_count = 0
        self.is_active = True
    
    async def send_message(self, message: WebSocketMessage) -> bool:
        """发送消息"""
        try:
            if not self.is_active:
                return False
            
            message_data = json.dumps(message.to_dict())
            await self.websocket.send(message_data)
            self.message_count += 1
            return True
        
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
            self.is_active = False
            return False
    
    async def receive_message(self) -> Optional[WebSocketMessage]:
        """接收消息"""
        try:
            if not self.is_active:
                return None
            
            raw_message = await self.websocket.recv()
            message_data = json.loads(raw_message)
            return WebSocketMessage.from_dict(message_data)
        
        except Exception as e:
            logger.error(f"接收WebSocket消息失败: {e}")
            self.is_active = False
            return None
    
    def subscribe(self, message_type: MessageType):
        """订阅消息类型"""
        self.subscriptions.add(message_type)
    
    def unsubscribe(self, message_type: MessageType):
        """取消订阅消息类型"""
        self.subscriptions.discard(message_type)
    
    def is_subscribed(self, message_type: MessageType) -> bool:
        """检查是否订阅了消息类型"""
        return message_type in self.subscriptions
    
    def update_heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.now()
    
    def get_connection_info(self) -> Dict[str, Any]:
        """获取连接信息"""
        return {
            "session_id": self.session_id,
            "connected_at": self.connected_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "message_count": self.message_count,
            "subscriptions": [sub.value for sub in self.subscriptions],
            "is_active": self.is_active,
            "metadata": self.metadata
        }


class DebateWebSocketManager:
    """辩论系统WebSocket管理器"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.session_connections: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        
        # 消息队列
        self.outgoing_queue: asyncio.Queue = asyncio.Queue()
        self.incoming_queue: asyncio.Queue = asyncio.Queue()
        
        # 统计信息
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0
        self.start_time = datetime.now()
        
        # 后台任务
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.message_processor_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        
        # 配置
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.connection_timeout = 300  # 连接超时（秒）
        self.max_connections = 1000   # 最大连接数
        
        logger.info("辩论WebSocket管理器初始化完成")
    
    async def start(self):
        """启动WebSocket管理器"""
        try:
            # 启动后台任务
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self.message_processor_task = asyncio.create_task(self._message_processor_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            
            logger.info("WebSocket管理器已启动")
        except Exception as e:
            logger.error(f"启动WebSocket管理器失败: {e}")
    
    async def stop(self):
        """停止WebSocket管理器"""
        try:
            # 取消后台任务
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
            if self.message_processor_task:
                self.message_processor_task.cancel()
            if self.cleanup_task:
                self.cleanup_task.cancel()
            
            # 关闭所有连接
            for connection in list(self.connections.values()):
                await self._disconnect_client(connection.session_id)
            
            logger.info("WebSocket管理器已停止")
        except Exception as e:
            logger.error(f"停止WebSocket管理器失败: {e}")
    
    async def add_connection(self, websocket, session_id: str = None) -> str:
        """添加新连接"""
        try:
            if len(self.connections) >= self.max_connections:
                raise Exception("连接数已达上限")
            
            connection = WebSocketConnection(websocket, session_id)
            self.connections[connection.session_id] = connection
            self.total_connections += 1
            
            # 发送欢迎消息
            welcome_message = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                payload={
                    "status": "connected",
                    "session_id": connection.session_id,
                    "server_time": datetime.now().isoformat()
                },
                session_id=connection.session_id
            )
            await connection.send_message(welcome_message)
            
            logger.info(f"新WebSocket连接已建立: {connection.session_id}")
            return connection.session_id
        
        except Exception as e:
            logger.error(f"添加WebSocket连接失败: {e}")
            raise
    
    async def remove_connection(self, session_id: str):
        """移除连接"""
        await self._disconnect_client(session_id)
    
    async def _disconnect_client(self, session_id: str):
        """断开客户端连接"""
        try:
            if session_id in self.connections:
                connection = self.connections[session_id]
                connection.is_active = False
                
                # 从会话连接映射中移除
                for sess_id, conn_ids in self.session_connections.items():
                    conn_ids.discard(session_id)
                
                # 移除连接
                del self.connections[session_id]
                
                logger.info(f"WebSocket连接已断开: {session_id}")
        
        except Exception as e:
            logger.error(f"断开连接失败: {e}")
    
    async def send_message(self, message: WebSocketMessage, target_session: str = None):
        """发送消息"""
        try:
            if target_session:
                # 发送给特定会话
                if target_session in self.connections:
                    connection = self.connections[target_session]
                    success = await connection.send_message(message)
                    if success:
                        self.total_messages_sent += 1
            else:
                # 广播消息
                await self.broadcast_message(message)
        
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
    
    async def broadcast_message(self, message: WebSocketMessage, message_type_filter: MessageType = None):
        """广播消息"""
        try:
            sent_count = 0
            failed_connections = []
            
            for session_id, connection in self.connections.items():
                try:
                    # 检查订阅过滤
                    if message_type_filter and not connection.is_subscribed(message_type_filter):
                        continue
                    
                    success = await connection.send_message(message)
                    if success:
                        sent_count += 1
                    else:
                        failed_connections.append(session_id)
                
                except Exception as e:
                    logger.error(f"向连接 {session_id} 发送消息失败: {e}")
                    failed_connections.append(session_id)
            
            # 清理失败的连接
            for session_id in failed_connections:
                await self._disconnect_client(session_id)
            
            self.total_messages_sent += sent_count
            logger.debug(f"广播消息完成: 成功 {sent_count}, 失败 {len(failed_connections)}")
        
        except Exception as e:
            logger.error(f"广播消息失败: {e}")
    
    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """注册消息处理器"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logger.debug(f"已注册消息处理器: {message_type.value}")
    
    def unregister_message_handler(self, message_type: MessageType, handler: Callable):
        """取消注册消息处理器"""
        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type].remove(handler)
                logger.debug(f"已取消注册消息处理器: {message_type.value}")
            except ValueError:
                pass
    
    async def handle_incoming_message(self, session_id: str, message: WebSocketMessage):
        """处理接收到的消息"""
        try:
            self.total_messages_received += 1
            
            # 更新连接心跳
            if session_id in self.connections:
                self.connections[session_id].update_heartbeat()
            
            # 处理特殊消息类型
            if message.type == MessageType.HEARTBEAT:
                await self._handle_heartbeat(session_id, message)
                return
            
            # 调用注册的处理器
            handlers = self.message_handlers.get(message.type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(session_id, message)
                    else:
                        handler(session_id, message)
                except Exception as e:
                    logger.error(f"消息处理器执行失败: {e}")
        
        except Exception as e:
            logger.error(f"处理接收消息失败: {e}")
    
    async def _handle_heartbeat(self, session_id: str, message: WebSocketMessage):
        """处理心跳消息"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.update_heartbeat()
            
            # 回复心跳
            pong_message = WebSocketMessage(
                type=MessageType.HEARTBEAT,
                payload={"type": "pong", "timestamp": datetime.now().isoformat()},
                session_id=session_id
            )
            await connection.send_message(pong_message)
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while True:
            try:
                # 发送心跳给所有连接
                heartbeat_message = WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    payload={"type": "ping", "timestamp": datetime.now().isoformat()}
                )
                
                await self.broadcast_message(heartbeat_message)
                await asyncio.sleep(self.heartbeat_interval)
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"心跳循环错误: {e}")
                await asyncio.sleep(5)
    
    async def _message_processor_loop(self):
        """消息处理循环"""
        while True:
            try:
                # 处理传入消息队列
                if not self.incoming_queue.empty():
                    session_id, message = await self.incoming_queue.get()
                    await self.handle_incoming_message(session_id, message)
                
                # 处理传出消息队列
                if not self.outgoing_queue.empty():
                    message, target_session = await self.outgoing_queue.get()
                    await self.send_message(message, target_session)
                
                await asyncio.sleep(0.01)  # 避免CPU占用过高
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"消息处理循环错误: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                current_time = datetime.now()
                timeout_connections = []
                
                # 检查超时连接
                for session_id, connection in self.connections.items():
                    time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
                    if time_since_heartbeat > self.connection_timeout:
                        timeout_connections.append(session_id)
                
                # 清理超时连接
                for session_id in timeout_connections:
                    await self._disconnect_client(session_id)
                    logger.info(f"清理超时连接: {session_id}")
                
                await asyncio.sleep(60)  # 每分钟清理一次
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")
                await asyncio.sleep(30)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        current_time = datetime.now()
        uptime = (current_time - self.start_time).total_seconds()
        
        return {
            "total_connections": self.total_connections,
            "active_connections": len(self.connections),
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "uptime_seconds": uptime,
            "average_messages_per_second": (self.total_messages_sent + self.total_messages_received) / max(uptime, 1),
            "connections": [conn.get_connection_info() for conn in self.connections.values()]
        }
    
    async def send_debate_status_update(self, session_id: str, status_data: Dict[str, Any]):
        """发送辩论状态更新"""
        message = WebSocketMessage(
            type=MessageType.DEBATE_STATUS,
            payload=status_data,
            session_id=session_id
        )
        await self.send_message(message)
    
    async def send_agent_status_update(self, agent_data: Dict[str, Any]):
        """发送代理状态更新"""
        message = WebSocketMessage(
            type=MessageType.AGENT_STATUS,
            payload=agent_data
        )
        await self.broadcast_message(message, MessageType.AGENT_STATUS)
    
    async def send_workflow_status_update(self, workflow_data: Dict[str, Any]):
        """发送工作流状态更新"""
        message = WebSocketMessage(
            type=MessageType.WORKFLOW_STATUS,
            payload=workflow_data
        )
        await self.broadcast_message(message, MessageType.WORKFLOW_STATUS)
    
    async def send_monitoring_data(self, monitoring_data: Dict[str, Any]):
        """发送监控数据"""
        message = WebSocketMessage(
            type=MessageType.MONITORING_DATA,
            payload=monitoring_data
        )
        await self.broadcast_message(message, MessageType.MONITORING_DATA)


# 全局WebSocket管理器实例
debate_websocket_manager = DebateWebSocketManager()


# 使用示例和测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_websocket_manager():
        """测试WebSocket管理器"""
        print("🧪 测试WebSocket管理器...")
        
        # 启动管理器
        await debate_websocket_manager.start()
        
        # 模拟消息处理
        def handle_user_message(session_id: str, message: WebSocketMessage):
            print(f"收到用户消息: {session_id} -> {message.payload}")
        
        debate_websocket_manager.register_message_handler(
            MessageType.USER_MESSAGE, handle_user_message
        )
        
        # 获取状态
        status = debate_websocket_manager.get_connection_status()
        print(f"连接状态: {status}")
        
        print("✅ WebSocket管理器测试完成")
        
        # 停止管理器
        await debate_websocket_manager.stop()
    
    # 运行测试
    asyncio.run(test_websocket_manager())