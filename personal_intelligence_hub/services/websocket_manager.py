#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - WebSocket Manager

实时通信管理器，处理WebSocket连接和实时状态更新
"""

import logging
import asyncio
import json
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket消息类型"""
    CHAT_MESSAGE = "chat_message"
    SYSTEM_STATUS = "system_status"
    AGENT_STATUS = "agent_status"
    WORKFLOW_UPDATE = "workflow_update"
    WIKI_UPDATE = "wiki_update"
    TASK_UPDATE = "task_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class WebSocketMessage:
    """WebSocket消息结构"""
    type: MessageType
    data: Dict[str, Any]
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
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class WebSocketConnection:
    """WebSocket连接封装"""
    
    def __init__(self, websocket, session_id: str, user_id: str = "default"):
        self.websocket = websocket
        self.session_id = session_id
        self.user_id = user_id
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.subscriptions: Set[str] = set()
    
    async def send_message(self, message: WebSocketMessage):
        """发送消息到客户端"""
        try:
            await self.websocket.send_text(message.to_json())
            logger.debug(f"Sent message to {self.session_id}: {message.type.value}")
        except Exception as e:
            logger.error(f"Failed to send message to {self.session_id}: {e}")
            raise
    
    async def send_error(self, error_message: str, error_code: str = "GENERAL_ERROR"):
        """发送错误消息"""
        error_msg = WebSocketMessage(
            type=MessageType.ERROR,
            data={
                "error_code": error_code,
                "message": error_message
            }
        )
        await self.send_message(error_msg)
    
    def subscribe(self, channel: str):
        """订阅频道"""
        self.subscriptions.add(channel)
        logger.debug(f"Session {self.session_id} subscribed to {channel}")
    
    def unsubscribe(self, channel: str):
        """取消订阅频道"""
        self.subscriptions.discard(channel)
        logger.debug(f"Session {self.session_id} unsubscribed from {channel}")
    
    def is_subscribed(self, channel: str) -> bool:
        """检查是否订阅了频道"""
        return channel in self.subscriptions


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.channels: Dict[str, Set[str]] = {}  # channel -> session_ids
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.heartbeat_task: Optional[asyncio.Task] = None
        logger.info("WebSocket Manager initialized")
    
    async def connect(self, websocket, session_id: str, user_id: str = "default") -> WebSocketConnection:
        """建立WebSocket连接"""
        connection = WebSocketConnection(websocket, session_id, user_id)
        self.connections[session_id] = connection
        
        # 自动订阅基础频道
        await self._auto_subscribe(connection)
        
        # 启动心跳检测
        if self.heartbeat_task is None:
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info(f"WebSocket connected: {session_id} (user: {user_id})")
        
        # 发送连接确认消息
        welcome_msg = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data={
                "status": "connected",
                "session_id": session_id,
                "server_time": datetime.now().isoformat()
            }
        )
        await connection.send_message(welcome_msg)
        
        return connection
    
    async def disconnect(self, session_id: str):
        """断开WebSocket连接"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            
            # 从所有频道中移除
            for channel in list(connection.subscriptions):
                await self._unsubscribe_from_channel(session_id, channel)
            
            del self.connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
            
            # 如果没有连接了，停止心跳
            if not self.connections and self.heartbeat_task:
                self.heartbeat_task.cancel()
                self.heartbeat_task = None
    
    async def _auto_subscribe(self, connection: WebSocketConnection):
        """自动订阅基础频道"""
        basic_channels = [
            "system_status",
            "chat_updates", 
            f"user_{connection.user_id}",
            f"session_{connection.session_id}"
        ]
        
        for channel in basic_channels:
            await self._subscribe_to_channel(connection.session_id, channel)
    
    async def _subscribe_to_channel(self, session_id: str, channel: str):
        """订阅频道"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.subscribe(channel)
            
            if channel not in self.channels:
                self.channels[channel] = set()
            self.channels[channel].add(session_id)
    
    async def _unsubscribe_from_channel(self, session_id: str, channel: str):
        """取消订阅频道"""
        if session_id in self.connections:
            connection = self.connections[session_id]
            connection.unsubscribe(channel)
            
            if channel in self.channels:
                self.channels[channel].discard(session_id)
                if not self.channels[channel]:
                    del self.channels[channel]
    
    async def broadcast_to_channel(self, channel: str, message: WebSocketMessage):
        """向频道广播消息"""
        if channel in self.channels:
            disconnected_sessions = []
            
            for session_id in self.channels[channel]:
                if session_id in self.connections:
                    try:
                        await self.connections[session_id].send_message(message)
                    except Exception as e:
                        logger.error(f"Failed to send to {session_id}: {e}")
                        disconnected_sessions.append(session_id)
                else:
                    disconnected_sessions.append(session_id)
            
            # 清理断开的连接
            for session_id in disconnected_sessions:
                await self.disconnect(session_id)
    
    async def send_to_session(self, session_id: str, message: WebSocketMessage):
        """向特定会话发送消息"""
        if session_id in self.connections:
            try:
                await self.connections[session_id].send_message(message)
            except Exception as e:
                logger.error(f"Failed to send to session {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def broadcast_system_status(self, status_data: Dict[str, Any]):
        """广播系统状态更新"""
        message = WebSocketMessage(
            type=MessageType.SYSTEM_STATUS,
            data=status_data
        )
        await self.broadcast_to_channel("system_status", message)
    
    async def broadcast_agent_status(self, agent_data: Dict[str, Any]):
        """广播代理状态更新"""
        message = WebSocketMessage(
            type=MessageType.AGENT_STATUS,
            data=agent_data
        )
        await self.broadcast_to_channel("system_status", message)
    
    async def broadcast_workflow_update(self, workflow_data: Dict[str, Any]):
        """广播工作流更新"""
        message = WebSocketMessage(
            type=MessageType.WORKFLOW_UPDATE,
            data=workflow_data
        )
        await self.broadcast_to_channel("system_status", message)
    
    async def _heartbeat_loop(self):
        """心跳检测循环"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                current_time = datetime.now()
                disconnected_sessions = []
                
                for session_id, connection in self.connections.items():
                    try:
                        # 发送心跳
                        heartbeat_msg = WebSocketMessage(
                            type=MessageType.HEARTBEAT,
                            data={"server_time": current_time.isoformat()}
                        )
                        await connection.send_message(heartbeat_msg)
                        connection.last_heartbeat = current_time
                        
                    except Exception as e:
                        logger.warning(f"Heartbeat failed for {session_id}: {e}")
                        disconnected_sessions.append(session_id)
                
                # 清理失效连接
                for session_id in disconnected_sessions:
                    await self.disconnect(session_id)
                    
            except asyncio.CancelledError:
                logger.info("Heartbeat loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        return {
            "total_connections": len(self.connections),
            "total_channels": len(self.channels),
            "connections_by_user": {},
            "channels_info": {
                channel: len(sessions) 
                for channel, sessions in self.channels.items()
            }
        }


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()