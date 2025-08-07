# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : websocket_manager.py
@Description:
    WebSocket Manager - Real-time communication management for DAIP backend.
    Handles WebSocket connections, broadcasting, and real-time updates.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Set, Callable
from datetime import datetime
from uuid import uuid4
import logging

try:
    from websockets.server import WebSocketServerProtocol
    from websockets.exceptions import ConnectionClosed, WebSocketException
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    # 创建虚拟类用于类型提示
    class WebSocketServerProtocol:
        pass

from ..domain.entities import User, Session, Message
from ..domain.value_objects import EntranceType, SessionStatus, MessageIntent


class WebSocketConnection:
    """WebSocket连接封装类"""
    
    def __init__(self, websocket: WebSocketServerProtocol, connection_id: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.entrance_type: Optional[EntranceType] = None
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
        self.is_authenticated = False
        self.subscriptions: Set[str] = set()
    
    async def send_json(self, data: Dict[str, Any]):
        """发送JSON数据"""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        try:
            message = json.dumps(data, ensure_ascii=False)
            await self.websocket.send(message)
            self.last_activity = datetime.now()
        except (ConnectionClosed, WebSocketException) as e:
            logging.warning(f"Failed to send message to {self.connection_id}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error sending message to {self.connection_id}: {e}")
            raise
    
    async def close(self):
        """关闭连接"""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        try:
            await self.websocket.close()
        except Exception as e:
            logging.warning(f"Error closing connection {self.connection_id}: {e}")
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """检查连接是否活跃"""
        inactive_time = (datetime.now() - self.last_activity).total_seconds()
        return inactive_time < (timeout_minutes * 60)
    
    def add_subscription(self, channel: str):
        """添加订阅"""
        self.subscriptions.add(channel)
    
    def remove_subscription(self, channel: str):
        """移除订阅"""
        self.subscriptions.discard(channel)
    
    def is_subscribed(self, channel: str) -> bool:
        """检查是否订阅了特定频道"""
        return channel in self.subscriptions


class WebSocketManager:
    """WebSocket管理器 - 实时通信管理"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.session_connections: Dict[str, Set[str]] = {}
        self.user_connections: Dict[str, Set[str]] = {}
        self.channel_subscribers: Dict[str, Set[str]] = {}
        
        # 事件处理器
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "start_time": datetime.now()
        }
        
        # 配置
        self.config = {
            "connection_timeout_minutes": 30,
            "ping_interval_seconds": 30,
            "max_connections_per_user": 5,
            "max_connections_per_session": 10,
            "enable_broadcasting": True,
            "enable_authentication": True
        }
        
        # 后台任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start(self):
        """启动WebSocket管理器"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # 启动后台任务
        self._cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
        self._ping_task = asyncio.create_task(self._ping_connections())
        
        logging.info("WebSocket Manager started")
    
    async def stop(self):
        """停止WebSocket管理器"""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # 取消后台任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        if self._ping_task:
            self._ping_task.cancel()
        
        # 关闭所有连接
        for connection in self.connections.values():
            try:
                await connection.close()
            except Exception as e:
                logging.warning(f"Error closing connection {connection.connection_id}: {e}")
        
        # 清空连接
        self.connections.clear()
        self.session_connections.clear()
        self.user_connections.clear()
        self.channel_subscribers.clear()
        
        logging.info("WebSocket Manager stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """处理新的WebSocket连接"""
        if not WEBSOCKETS_AVAILABLE:
            return
            
        connection_id = str(uuid4())
        connection = WebSocketConnection(websocket, connection_id)
        
        # 添加连接
        self.connections[connection_id] = connection
        self.stats["total_connections"] += 1
        self.stats["active_connections"] += 1
        
        logging.info(f"New WebSocket connection: {connection_id}")
        
        try:
            # 发送连接确认
            await connection.send_json({
                "type": "connection_established",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat(),
                "message": "WebSocket连接已建立"
            })
            
            # 处理消息
            async for message in websocket:
                await self._handle_message(connection, message)
                
        except ConnectionClosed:
            logging.info(f"Connection closed: {connection_id}")
        except WebSocketException as e:
            logging.warning(f"WebSocket error for {connection_id}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error for {connection_id}: {e}")
        finally:
            # 清理连接
            await self._cleanup_connection(connection_id)
    
    async def _handle_message(self, connection: WebSocketConnection, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            self.stats["messages_received"] += 1
            
            message_type = data.get("type")
            if not message_type:
                await connection.send_json({
                    "type": "error",
                    "message": "Message type is required",
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            # 更新活动时间
            connection.update_activity()
            
            # 根据消息类型处理
            handler = self._get_message_handler(message_type)
            if handler:
                await handler(connection, data)
            else:
                await connection.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
                
        except json.JSONDecodeError:
            await connection.send_json({
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logging.error(f"Error handling message from {connection.connection_id}: {e}")
            await connection.send_json({
                "type": "error",
                "message": "Internal server error",
                "timestamp": datetime.now().isoformat()
            })
    
    def _get_message_handler(self, message_type: str) -> Optional[Callable]:
        """获取消息处理器"""
        handlers = {
            "authenticate": self._handle_authenticate,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "join_session": self._handle_join_session,
            "leave_session": self._handle_leave_session,
            "send_message": self._handle_send_message,
            "ping": self._handle_ping,
            "get_status": self._handle_get_status
        }
        return handlers.get(message_type)
    
    async def _handle_authenticate(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理认证请求"""
        user_id = data.get("user_id")
        token = data.get("token")
        
        if not user_id or not token:
            await connection.send_json({
                "type": "authentication_error",
                "message": "User ID and token are required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # 简化的认证逻辑
        # 在实际应用中，这里应该验证token的有效性
        connection.user_id = user_id
        connection.is_authenticated = True
        
        # 添加到用户连接映射
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection.connection_id)
        
        await connection.send_json({
            "type": "authentication_success",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "message": "认证成功"
        })
        
        # 触发认证事件
        await self._trigger_event("user_authenticated", {
            "user_id": user_id,
            "connection_id": connection.connection_id
        })
    
    async def _handle_subscribe(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理订阅请求"""
        if not connection.is_authenticated:
            await connection.send_json({
                "type": "error",
                "message": "Authentication required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        channel = data.get("channel")
        if not channel:
            await connection.send_json({
                "type": "error",
                "message": "Channel is required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        connection.add_subscription(channel)
        
        # 添加到频道订阅者
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
        self.channel_subscribers[channel].add(connection.connection_id)
        
        await connection.send_json({
            "type": "subscription_success",
            "channel": channel,
            "timestamp": datetime.now().isoformat(),
            "message": f"已订阅频道: {channel}"
        })
    
    async def _handle_unsubscribe(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理取消订阅请求"""
        channel = data.get("channel")
        if not channel:
            await connection.send_json({
                "type": "error",
                "message": "Channel is required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        connection.remove_subscription(channel)
        
        # 从频道订阅者中移除
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(connection.connection_id)
        
        await connection.send_json({
            "type": "unsubscription_success",
            "channel": channel,
            "timestamp": datetime.now().isoformat(),
            "message": f"已取消订阅频道: {channel}"
        })
    
    async def _handle_join_session(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理加入会话请求"""
        if not connection.is_authenticated:
            await connection.send_json({
                "type": "error",
                "message": "Authentication required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        session_id = data.get("session_id")
        entrance_type = data.get("entrance_type")
        
        if not session_id:
            await connection.send_json({
                "type": "error",
                "message": "Session ID is required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # 检查用户连接数限制
        user_id = connection.user_id
        if user_id in self.user_connections:
            user_session_connections = [
                conn_id for conn_id in self.user_connections[user_id]
                if conn_id in self.connections and self.connections[conn_id].session_id
            ]
            
            if len(user_session_connections) >= self.config["max_connections_per_user"]:
                await connection.send_json({
                    "type": "error",
                    "message": "Maximum connections per user exceeded",
                    "timestamp": datetime.now().isoformat()
                })
                return
        
        # 检查会话连接数限制
        if session_id in self.session_connections:
            if len(self.session_connections[session_id]) >= self.config["max_connections_per_session"]:
                await connection.send_json({
                    "type": "error",
                    "message": "Maximum connections per session exceeded",
                    "timestamp": datetime.now().isoformat()
                })
                return
        
        # 加入会话
        connection.session_id = session_id
        if entrance_type:
            try:
                connection.entrance_type = EntranceType(entrance_type)
            except ValueError:
                await connection.send_json({
                    "type": "error",
                    "message": f"Invalid entrance type: {entrance_type}",
                    "timestamp": datetime.now().isoformat()
                })
                return
        
        # 添加到会话连接映射
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection.connection_id)
        
        # 订阅会话频道
        session_channel = f"session_{session_id}"
        connection.add_subscription(session_channel)
        
        if session_channel not in self.channel_subscribers:
            self.channel_subscribers[session_channel] = set()
        self.channel_subscribers[session_channel].add(connection.connection_id)
        
        await connection.send_json({
            "type": "session_joined",
            "session_id": session_id,
            "entrance_type": entrance_type,
            "timestamp": datetime.now().isoformat(),
            "message": f"已加入会话: {session_id}"
        })
        
        # 触发加入会话事件
        await self._trigger_event("user_joined_session", {
            "user_id": user_id,
            "session_id": session_id,
            "connection_id": connection.connection_id
        })
    
    async def _handle_leave_session(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理离开会话请求"""
        session_id = connection.session_id
        if not session_id:
            await connection.send_json({
                "type": "error",
                "message": "Not in any session",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # 离开会话
        connection.session_id = None
        connection.entrance_type = None
        
        # 从会话连接映射中移除
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection.connection_id)
        
        # 取消订阅会话频道
        session_channel = f"session_{session_id}"
        connection.remove_subscription(session_channel)
        
        if session_channel in self.channel_subscribers:
            self.channel_subscribers[session_channel].discard(connection.connection_id)
        
        await connection.send_json({
            "type": "session_left",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "message": f"已离开会话: {session_id}"
        })
        
        # 触发离开会话事件
        if connection.user_id:
            await self._trigger_event("user_left_session", {
                "user_id": connection.user_id,
                "session_id": session_id,
                "connection_id": connection.connection_id
            })
    
    async def _handle_send_message(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理发送消息请求"""
        if not connection.is_authenticated:
            await connection.send_json({
                "type": "error",
                "message": "Authentication required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        if not connection.session_id:
            await connection.send_json({
                "type": "error",
                "message": "Not in any session",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        message_content = data.get("message")
        if not message_content:
            await connection.send_json({
                "type": "error",
                "message": "Message content is required",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        # 创建消息对象
        message_data = {
            "message_id": str(uuid4()),
            "session_id": connection.session_id,
            "sender": connection.user_id,
            "content": message_content,
            "timestamp": datetime.now().isoformat(),
            "type": "user"
        }
        
        # 广播消息到会话中的所有连接
        await self.broadcast_to_session(connection.session_id, {
            "type": "message",
            "data": message_data,
            "timestamp": datetime.now().isoformat()
        })
        
        # 触发消息事件
        await self._trigger_event("message_sent", {
            "user_id": connection.user_id,
            "session_id": connection.session_id,
            "message": message_data
        })
    
    async def _handle_ping(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理ping请求"""
        await connection.send_json({
            "type": "pong",
            "timestamp": datetime.now().isoformat(),
            "message": "Pong"
        })
    
    async def _handle_get_status(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """处理获取状态请求"""
        status_data = {
            "type": "status",
            "connection_id": connection.connection_id,
            "is_authenticated": connection.is_authenticated,
            "user_id": connection.user_id,
            "session_id": connection.session_id,
            "entrance_type": connection.entrance_type.value if connection.entrance_type else None,
            "subscriptions": list(connection.subscriptions),
            "connected_at": connection.connected_at.isoformat(),
            "last_activity": connection.last_activity.isoformat(),
            "server_stats": self.get_stats()
        }
        
        await connection.send_json(status_data)
    
    async def _cleanup_connection(self, connection_id: str):
        """清理连接"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # 从用户连接映射中移除
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection_id)
        
        # 从会话连接映射中移除
        if connection.session_id and connection.session_id in self.session_connections:
            self.session_connections[connection.session_id].discard(connection_id)
        
        # 从频道订阅者中移除
        for channel in connection.subscriptions:
            if channel in self.channel_subscribers:
                self.channel_subscribers[channel].discard(connection_id)
        
        # 从连接列表中移除
        del self.connections[connection_id]
        self.stats["active_connections"] -= 1
        
        # 触发断开连接事件
        if connection.user_id:
            await self._trigger_event("user_disconnected", {
                "user_id": connection.user_id,
                "connection_id": connection_id,
                "session_id": connection.session_id
            })
        
        logging.info(f"Connection cleaned up: {connection_id}")
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        """向会话中的所有连接广播消息"""
        if not self.config["enable_broadcasting"]:
            return
        
        session_channel = f"session_{session_id}"
        await self.broadcast_to_channel(session_channel, message)
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """向用户的所有连接广播消息"""
        if not self.config["enable_broadcasting"]:
            return
        
        if user_id not in self.user_connections:
            return
        
        user_channel = f"user_{user_id}"
        await self.broadcast_to_channel(user_channel, message)
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """向频道的所有订阅者广播消息"""
        if not self.config["enable_broadcasting"]:
            return
        
        if channel not in self.channel_subscribers:
            return
        
        failed_connections = []
        
        for connection_id in self.channel_subscribers[channel].copy():
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                try:
                    await connection.send_json(message)
                    self.stats["messages_sent"] += 1
                except Exception as e:
                    logging.warning(f"Failed to broadcast to {connection_id}: {e}")
                    failed_connections.append(connection_id)
        
        # 清理失败的连接
        for connection_id in failed_connections:
            await self._cleanup_connection(connection_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """向所有连接广播消息"""
        if not self.config["enable_broadcasting"]:
            return
        
        failed_connections = []
        
        for connection_id, connection in self.connections.items():
            try:
                await connection.send_json(message)
                self.stats["messages_sent"] += 1
            except Exception as e:
                logging.warning(f"Failed to broadcast to {connection_id}: {e}")
                failed_connections.append(connection_id)
        
        # 清理失败的连接
        for connection_id in failed_connections:
            await self._cleanup_connection(connection_id)
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """添加事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logging.error(f"Error in event handler for {event_type}: {e}")
    
    async def _cleanup_inactive_connections(self):
        """清理不活跃的连接"""
        while self._is_running:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                inactive_connections = []
                timeout_minutes = self.config["connection_timeout_minutes"]
                
                for connection_id, connection in self.connections.items():
                    if not connection.is_active(timeout_minutes):
                        inactive_connections.append(connection_id)
                
                for connection_id in inactive_connections:
                    await self._cleanup_connection(connection_id)
                
                if inactive_connections:
                    logging.info(f"Cleaned up {len(inactive_connections)} inactive connections")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in cleanup task: {e}")
    
    async def _ping_connections(self):
        """定期ping连接"""
        while self._is_running:
            try:
                await asyncio.sleep(self.config["ping_interval_seconds"])
                
                ping_message = {
                    "type": "ping",
                    "timestamp": datetime.now().isoformat()
                }
                
                failed_connections = []
                
                for connection_id, connection in self.connections.items():
                    try:
                        await connection.send_json(ping_message)
                        self.stats["messages_sent"] += 1
                    except Exception as e:
                        logging.warning(f"Failed to ping {connection_id}: {e}")
                        failed_connections.append(connection_id)
                
                # 清理失败的连接
                for connection_id in failed_connections:
                    await self._cleanup_connection(connection_id)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in ping task: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            "total_connections": self.stats["total_connections"],
            "active_connections": self.stats["active_connections"],
            "messages_sent": self.stats["messages_sent"],
            "messages_received": self.stats["messages_received"],
            "uptime_seconds": uptime,
            "channels": len(self.channel_subscribers),
            "active_sessions": len(self.session_connections),
            "active_users": len(self.user_connections),
            "is_running": self._is_running
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """获取连接信息"""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            "connection_id": connection_id,
            "user_id": connection.user_id,
            "session_id": connection.session_id,
            "entrance_type": connection.entrance_type.value if connection.entrance_type else None,
            "is_authenticated": connection.is_authenticated,
            "connected_at": connection.connected_at.isoformat(),
            "last_activity": connection.last_activity.isoformat(),
            "subscriptions": list(connection.subscriptions),
            "is_active": connection.is_active()
        }
    
    def get_session_connections(self, session_id: str) -> List[Dict[str, Any]]:
        """获取会话的所有连接"""
        if session_id not in self.session_connections:
            return []
        
        connections_info = []
        for connection_id in self.session_connections[session_id]:
            connection_info = self.get_connection_info(connection_id)
            if connection_info:
                connections_info.append(connection_info)
        
        return connections_info
    
    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户的所有连接"""
        if user_id not in self.user_connections:
            return []
        
        connections_info = []
        for connection_id in self.user_connections[user_id]:
            connection_info = self.get_connection_info(connection_id)
            if connection_info:
                connections_info.append(connection_info)
        
        return connections_info