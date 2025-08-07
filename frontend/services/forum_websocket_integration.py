#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 12:00:00
@Author  : DAIP-LIVE Team
@File    : forum_websocket_integration.py
@Description:
    Forum WebSocket集成服务 - 处理Forum模式的实时通信和状态同步
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum

from ..services.dual_entrance_websocket_manager import dual_entrance_websocket_manager, MessageType, EntranceType

# 配置日志
logger = logging.getLogger(__name__)


class ForumWebSocketEventType(Enum):
    """Forum WebSocket事件类型枚举"""
    SESSION_START = "session_start"
    AGENT_MESSAGE = "agent_message"
    USER_INTERVENTION = "user_intervention"
    CONTEXT_UPDATE = "context_update"
    CONSENSUS_UPDATE = "consensus_update"
    DEBATE_STATUS = "debate_status"
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"
    SESSION_END = "session_end"
    ERROR = "error"


class ForumWebSocketIntegration:
    """Forum WebSocket集成服务"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[ForumWebSocketEventType, List[Callable]] = {}
        self.connection_status = "disconnected"
        self.message_queue = asyncio.Queue()
        self.is_processing = False
        
        # 统计信息
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "sessions_created": 0,
            "errors": 0,
            "last_activity": None
        }
        
        logger.info("Forum WebSocket集成服务初始化完成")
    
    async def initialize(self):
        """初始化WebSocket连接"""
        try:
            # 注册Forum处理器
            dual_entrance_websocket_manager.register_forum_handler(self.handle_forum_message)
            
            # 连接WebSocket
            self.connection_status = "connecting"
            connected = await dual_entrance_websocket_manager.connect()
            
            if connected:
                self.connection_status = "connected"
                logger.info("Forum WebSocket连接成功")
                
                # 启动消息处理器
                self.is_processing = True
                asyncio.create_task(self._process_messages())
                
            else:
                self.connection_status = "disconnected"
                logger.error("Forum WebSocket连接失败")
                
        except Exception as e:
            self.connection_status = "disconnected"
            logger.error(f"Forum WebSocket初始化失败: {e}")
    
    async def handle_forum_message(self, message_data: Dict[str, Any]):
        """处理Forum消息"""
        try:
            self.stats["messages_received"] += 1
            self.stats["last_activity"] = datetime.now()
            
            message_type = message_data.get("type")
            session_id = message_data.get("session_id")
            
            logger.debug(f"收到Forum消息: {message_type} (会话: {session_id})")
            
            # 根据消息类型分发处理
            if message_type == "agent_message":
                await self._handle_agent_message(message_data)
            elif message_type == "context_update":
                await self._handle_context_update(message_data)
            elif message_type == "consensus_update":
                await self._handle_consensus_update(message_data)
            elif message_type == "debate_status":
                await self._handle_debate_status(message_data)
            elif message_type == "error":
                await self._handle_error_message(message_data)
            else:
                logger.warning(f"未知的Forum消息类型: {message_type}")
                
        except Exception as e:
            logger.error(f"处理Forum消息失败: {e}")
            self.stats["errors"] += 1
    
    async def _handle_agent_message(self, message_data: Dict[str, Any]):
        """处理Agent消息"""
        event = {
            "type": ForumWebSocketEventType.AGENT_MESSAGE,
            "session_id": message_data.get("session_id"),
            "agent_name": message_data.get("agent_name"),
            "agent_id": message_data.get("agent_id"),
            "content": message_data.get("content"),
            "timestamp": message_data.get("timestamp"),
            "metadata": message_data.get("metadata", {})
        }
        
        await self._trigger_event_handlers(event)
    
    async def _handle_context_update(self, message_data: Dict[str, Any]):
        """处理上下文更新"""
        event = {
            "type": ForumWebSocketEventType.CONTEXT_UPDATE,
            "session_id": message_data.get("session_id"),
            "context_data": message_data.get("data", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新本地会话状态
        session_id = event["session_id"]
        if session_id in self.active_sessions:
            self.active_sessions[session_id].update(event["context_data"])
        
        await self._trigger_event_handlers(event)
    
    async def _handle_consensus_update(self, message_data: Dict[str, Any]):
        """处理共识更新"""
        event = {
            "type": ForumWebSocketEventType.CONSENSUS_UPDATE,
            "session_id": message_data.get("session_id"),
            "consensus_level": message_data.get("consensus_level", 0.0),
            "timestamp": datetime.now().isoformat()
        }
        
        await self._trigger_event_handlers(event)
    
    async def _handle_debate_status(self, message_data: Dict[str, Any]):
        """处理辩论状态更新"""
        event = {
            "type": ForumWebSocketEventType.DEBATE_STATUS,
            "session_id": message_data.get("session_id"),
            "status": message_data.get("status"),
            "message": message_data.get("message"),
            "timestamp": datetime.now().isoformat()
        }
        
        await self._trigger_event_handlers(event)
    
    async def _handle_error_message(self, message_data: Dict[str, Any]):
        """处理错误消息"""
        event = {
            "type": ForumWebSocketEventType.ERROR,
            "session_id": message_data.get("session_id"),
            "error_message": message_data.get("message"),
            "error_code": message_data.get("code"),
            "timestamp": datetime.now().isoformat()
        }
        
        await self._trigger_event_handlers(event)
    
    async def _trigger_event_handlers(self, event: Dict[str, Any]):
        """触发事件处理器"""
        event_type = event["type"]
        
        if event_type in self.message_handlers:
            for handler in self.message_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"事件处理器执行失败 {event_type.value}: {e}")
    
    async def start_forum_session(self, topic: str, user_id: str = "default_user") -> str:
        """启动Forum会话"""
        try:
            session_id = f"forum_{uuid.uuid4().hex[:8]}"
            
            # 创建会话记录
            session_data = {
                "session_id": session_id,
                "topic": topic,
                "user_id": user_id,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "messages": [],
                "consensus_level": 0.0,
                "active_agents": [],
                "user_interventions": 0
            }
            
            self.active_sessions[session_id] = session_data
            self.stats["sessions_created"] += 1
            
            # 发送会话开始消息
            session_message = {
                "type": "forum_session_start",
                "session_id": session_id,
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            }
            
            await dual_entrance_websocket_manager.send_dict_message(session_message)
            
            logger.info(f"Forum会话已启动: {session_id}")
            
            # 触发会话开始事件
            event = {
                "type": ForumWebSocketEventType.SESSION_START,
                "session_id": session_id,
                "topic": topic,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
            await self._trigger_event_handlers(event)
            
            return session_id
            
        except Exception as e:
            logger.error(f"启动Forum会话失败: {e}")
            self.stats["errors"] += 1
            raise
    
    async def send_user_intervention(self, session_id: str, message: str, 
                                   intent: str = "comment") -> bool:
        """发送用户干预"""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"会话不存在: {session_id}")
                return False
            
            intervention_message = {
                "type": "forum_user_intervention",
                "session_id": session_id,
                "message": {
                    "content": message,
                    "intent": intent,
                    "timestamp": datetime.now().isoformat()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            success = await dual_entrance_websocket_manager.send_dict_message(intervention_message)
            
            if success:
                # 更新会话统计
                self.active_sessions[session_id]["user_interventions"] += 1
                self.stats["messages_sent"] += 1
                
                # 触发用户干预事件
                event = {
                    "type": ForumWebSocketEventType.USER_INTERVENTION,
                    "session_id": session_id,
                    "message": message,
                    "intent": intent,
                    "timestamp": datetime.now().isoformat()
                }
                await self._trigger_event_handlers(event)
            
            return success
            
        except Exception as e:
            logger.error(f"发送用户干预失败: {e}")
            self.stats["errors"] += 1
            return False
    
    async def send_session_control(self, session_id: str, action: str) -> bool:
        """发送会话控制消息"""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"会话不存在: {session_id}")
                return False
            
            control_message = {
                "type": "forum_control",
                "session_id": session_id,
                "action": action,
                "timestamp": datetime.now().isoformat()
            }
            
            success = await dual_entrance_websocket_manager.send_dict_message(control_message)
            
            if success:
                # 更新会话状态
                if action == "pause":
                    self.active_sessions[session_id]["status"] = "paused"
                    event_type = ForumWebSocketEventType.SESSION_PAUSE
                elif action == "resume":
                    self.active_sessions[session_id]["status"] = "active"
                    event_type = ForumWebSocketEventType.SESSION_RESUME
                elif action == "end":
                    self.active_sessions[session_id]["status"] = "completed"
                    event_type = ForumWebSocketEventType.SESSION_END
                else:
                    event_type = None
                
                if event_type:
                    event = {
                        "type": event_type,
                        "session_id": session_id,
                        "action": action,
                        "timestamp": datetime.now().isoformat()
                    }
                    await self._trigger_event_handlers(event)
                
                self.stats["messages_sent"] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"发送会话控制失败: {e}")
            self.stats["errors"] += 1
            return False
    
    async def request_context_update(self, session_id: str) -> bool:
        """请求上下文更新"""
        try:
            if session_id not in self.active_sessions:
                logger.error(f"会话不存在: {session_id}")
                return False
            
            request_message = {
                "type": "forum_context_request",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            return await dual_entrance_websocket_manager.send_dict_message(request_message)
            
        except Exception as e:
            logger.error(f"请求上下文更新失败: {e}")
            return False
    
    def register_event_handler(self, event_type: ForumWebSocketEventType, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.message_handlers:
            self.message_handlers[event_type] = []
        
        self.message_handlers[event_type].append(handler)
        logger.info(f"注册事件处理器: {event_type.value}")
    
    def unregister_event_handler(self, event_type: ForumWebSocketEventType, handler: Callable):
        """取消注册事件处理器"""
        if event_type in self.message_handlers:
            try:
                self.message_handlers[event_type].remove(handler)
                logger.info(f"取消注册事件处理器: {event_type.value}")
            except ValueError:
                logger.warning(f"事件处理器未找到: {event_type.value}")
    
    async def _process_messages(self):
        """处理消息队列"""
        while self.is_processing:
            try:
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self.handle_forum_message(message)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"消息处理错误: {e}")
                await asyncio.sleep(1)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        return self.active_sessions.get(session_id)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """获取所有活跃会话"""
        return list(self.active_sessions.values())
    
    def get_connection_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        return {
            "status": self.connection_status,
            "active_sessions": len(self.active_sessions),
            "stats": self.stats,
            "websocket_status": dual_entrance_websocket_manager.get_connection_status()
        }
    
    async def disconnect(self):
        """断开连接"""
        try:
            self.is_processing = False
            self.connection_status = "disconnected"
            
            # 清理会话
            for session_id in list(self.active_sessions.keys()):
                await self.send_session_control(session_id, "end")
            
            self.active_sessions.clear()
            
            logger.info("Forum WebSocket集成服务已断开")
            
        except Exception as e:
            logger.error(f"断开Forum WebSocket失败: {e}")


# 全局Forum WebSocket集成服务实例
forum_websocket_integration = ForumWebSocketIntegration()