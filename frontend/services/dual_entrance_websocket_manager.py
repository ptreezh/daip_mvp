#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双入口WebSocket通信管理器

支持Secretariat和Forum两种入口模式的实时通信
提供统一的WebSocket接口和消息处理机制
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

# 配置日志
logger = logging.getLogger(__name__)


class EntranceType(Enum):
    """入口类型枚举"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"


class MessageType(Enum):
    """消息类型枚举"""
    # 通用消息
    CHAT_MESSAGE = "chat_message"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"
    
    # Secretariat消息
    SECRETARIAT_TASK = "secretariat_task"
    TASK_STATUS = "task_status"
    SECRETARIAT_RESULT = "secretariat_result"
    REQUEST_TRANSPARENCY = "request_transparency"
    TRANSPARENCY_DATA = "transparency_data"
    
    # Forum消息
    CREATE_FORUM_SESSION = "create_forum_session"
    USER_INTERVENTION = "user_intervention"
    AGENT_MESSAGE = "agent_message"
    CONSENSUS_UPDATE = "consensus_update"
    FORUM_CONTROL = "forum_control"
    FORUM_SESSION_START = "forum_session_start"
    FORUM_CONTEXT_UPDATE = "forum_context_update"
    FORUM_DEBATE_STATUS = "forum_debate_status"
    OPTIMIZE_USER_INPUT = "optimize_user_input"
    FORUM_USER_INTERVENTION = "forum_user_intervention"
    
    # 实时更新
    AGENT_STATUS = "agent_status"
    WORKFLOW_UPDATE = "workflow_update"
    WIKI_UPDATE = "wiki_update"
    TASK_UPDATE = "task_update"


@dataclass
class BaseMessage:
    """基础消息数据结构"""
    message_id: str
    type: MessageType
    session_id: str
    timestamp: datetime
    entrance_type: EntranceType
    payload: Dict[str, Any]
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "message_id": self.message_id,
            "type": self.type.value,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "entrance_type": self.entrance_type.value,
            "payload": self.payload
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMessage':
        """从字典创建消息对象"""
        return cls(
            message_id=data["message_id"],
            type=MessageType(data["type"]),
            session_id=data["session_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            entrance_type=EntranceType(data["entrance_type"]),
            payload=data["payload"]
        )


@dataclass
class SecretariatTaskMessage(BaseMessage):
    """Secretariat任务消息"""
    content: str
    priority: str = "normal"
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.SECRETARIAT_TASK
        self.entrance_type = EntranceType.SECRETARIAT


@dataclass
class ForumSessionMessage(BaseMessage):
    """Forum会话消息"""
    topic: str
    participants: List[str]
    settings: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.CREATE_FORUM_SESSION
        self.entrance_type = EntranceType.FORUM


@dataclass
class UserInterventionMessage(BaseMessage):
    """用户干预消息"""
    message: Dict[str, Any]
    intent: str = "comment"
    target_agent: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.USER_INTERVENTION
        self.entrance_type = EntranceType.FORUM


@dataclass
class ForumSessionStartMessage(BaseMessage):
    """Forum会话开始消息"""
    topic: str
    selected_agents: List[str]
    user_id: str
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.FORUM_SESSION_START
        self.entrance_type = EntranceType.FORUM


@dataclass
class ForumContextUpdateMessage(BaseMessage):
    """Forum上下文更新消息"""
    context_data: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.FORUM_CONTEXT_UPDATE
        self.entrance_type = EntranceType.FORUM


@dataclass
class ForumDebateStatusMessage(BaseMessage):
    """Forum辩论状态消息"""
    debate_status: str
    current_round: int
    active_agents: List[str]
    message_count: int
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.FORUM_DEBATE_STATUS
        self.entrance_type = EntranceType.FORUM


@dataclass
class OptimizeUserInputMessage(BaseMessage):
    """优化用户输入消息"""
    input_text: str
    intent: str
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.OPTIMIZE_USER_INPUT
        self.entrance_type = EntranceType.FORUM


@dataclass
class ForumUserInterventionMessage(BaseMessage):
    """Forum用户干预消息"""
    message: Dict[str, Any]
    
    def __post_init__(self):
        super().__post_init__()
        self.type = MessageType.FORUM_USER_INTERVENTION
        self.entrance_type = EntranceType.FORUM


class DualEntranceWebSocketManager:
    """双入口WebSocket管理器"""
    
    def __init__(self, backend_url: str = "ws://localhost:8000/ws"):
        self.backend_url = backend_url
        self.websocket = None
        self.is_connected = False
        self.connection_retry_count = 0
        self.max_retries = 5
        self.retry_delay = 5
        
        # 会话管理
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_types: Dict[str, EntranceType] = {}
        
        # 消息处理器
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        self.entrance_handlers: Dict[EntranceType, Dict[MessageType, List[Callable]]] = {}
        
        # 消息队列
        self.outgoing_queue = asyncio.Queue()
        self.incoming_queue = asyncio.Queue()
        
        # Forum特定的处理器
        self.forum_handler: Optional[Callable] = None
        
        # 统计信息
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "last_activity": None
        }
        
        logger.info(f"双入口WebSocket管理器初始化: {backend_url}")
    
    async def connect(self) -> bool:
        """建立WebSocket连接"""
        try:
            logger.info(f"尝试连接到: {self.backend_url}")
            
            # 模拟连接成功
            self.is_connected = True
            self.connection_retry_count = 0
            
            logger.info("WebSocket连接成功")
            
            # 启动消息处理任务
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._heartbeat())
            asyncio.create_task(self._connection_monitor())
            
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
    
    async def send_message(self, message: BaseMessage) -> bool:
        """发送消息"""
        if not self.is_connected:
            logger.warning("WebSocket未连接，消息加入队列")
            await self.outgoing_queue.put(message)
            return False
        
        try:
            # 将消息加入发送队列
            await self.outgoing_queue.put(message)
            self.stats["messages_sent"] += 1
            self.stats["last_activity"] = datetime.now()
            
            logger.debug(f"消息已加入发送队列: {message.type.value}")
            return True
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.stats["errors"] += 1
            return False
    
    async def create_session(self, entrance_type: EntranceType, user_id: str, 
                           initial_context: Optional[Dict[str, Any]] = None) -> str:
        """创建会话"""
        session_id = f"{entrance_type.value}_{uuid.uuid4().hex[:8]}"
        
        session_data = {
            "session_id": session_id,
            "entrance_type": entrance_type,
            "user_id": user_id,
            "created_at": datetime.now(),
            "status": "active",
            "context": initial_context or {},
            "message_count": 0
        }
        
        self.active_sessions[session_id] = session_data
        self.session_types[session_id] = entrance_type
        
        logger.info(f"创建会话: {session_id} ({entrance_type.value})")
        
        # 发送会话创建消息
        session_message = BaseMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.SYSTEM_STATUS,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=entrance_type,
            payload={
                "action": "session_created",
                "session_data": session_data
            }
        )
        
        await self.send_message(session_message)
        
        return session_id
    
    async def send_secretariat_task(self, session_id: str, content: str, 
                                  priority: str = "normal",
                                  context: Optional[Dict[str, Any]] = None) -> bool:
        """发送Secretariat任务"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        if self.session_types[session_id] != EntranceType.SECRETARIAT:
            logger.error(f"会话类型不匹配: {session_id}")
            return False
        
        task_message = SecretariatTaskMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.SECRETARIAT_TASK,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.SECRETARIAT,
            payload={},
            content=content,
            priority=priority,
            context=context
        )
        
        return await self.send_message(task_message)
    
    async def create_forum_session(self, user_id: str, topic: str,
                                 participants: List[str],
                                 settings: Optional[Dict[str, Any]] = None) -> str:
        """创建Forum会话"""
        session_id = await self.create_session(
            EntranceType.FORUM, user_id, {"topic": topic}
        )
        
        forum_message = ForumSessionMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.CREATE_FORUM_SESSION,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            topic=topic,
            participants=participants,
            settings=settings
        )
        
        await self.send_message(forum_message)
        
        return session_id
    
    async def send_user_intervention(self, session_id: str, message: Dict[str, Any],
                                   intent: str = "comment",
                                   target_agent: Optional[str] = None) -> bool:
        """发送用户干预"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        if self.session_types[session_id] != EntranceType.FORUM:
            logger.error(f"会话类型不匹配: {session_id}")
            return False
        
        intervention_message = UserInterventionMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.USER_INTERVENTION,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            message=message,
            intent=intent,
            target_agent=target_agent
        )
        
        return await self.send_message(intervention_message)
    
    async def send_forum_session_start(self, session_id: str, topic: str,
                                      selected_agents: List[str],
                                      user_id: str = "default_user") -> bool:
        """发送Forum会话开始消息"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        if self.session_types[session_id] != EntranceType.FORUM:
            logger.error(f"会话类型不匹配: {session_id}")
            return False
        
        session_start_message = ForumSessionStartMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.FORUM_SESSION_START,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            topic=topic,
            selected_agents=selected_agents,
            user_id=user_id
        )
        
        return await self.send_message(session_start_message)
    
    async def send_forum_context_update(self, session_id: str,
                                      context_data: Dict[str, Any]) -> bool:
        """发送Forum上下文更新消息"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        context_update_message = ForumContextUpdateMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.FORUM_CONTEXT_UPDATE,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            context_data=context_data
        )
        
        return await self.send_message(context_update_message)
    
    async def send_forum_debate_status(self, session_id: str,
                                     debate_status: str,
                                     current_round: int,
                                     active_agents: List[str],
                                     message_count: int) -> bool:
        """发送Forum辩论状态消息"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        debate_status_message = ForumDebateStatusMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.FORUM_DEBATE_STATUS,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            debate_status=debate_status,
            current_round=current_round,
            active_agents=active_agents,
            message_count=message_count
        )
        
        return await self.send_message(debate_status_message)
    
    async def send_optimize_user_input(self, session_id: str,
                                      input_text: str,
                                      intent: str,
                                      context: Optional[Dict[str, Any]] = None) -> bool:
        """发送优化用户输入消息"""
        optimize_message = OptimizeUserInputMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.OPTIMIZE_USER_INPUT,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            input_text=input_text,
            intent=intent,
            context=context
        )
        
        return await self.send_message(optimize_message)
    
    async def send_forum_user_intervention(self, session_id: str,
                                         message: Dict[str, Any]) -> bool:
        """发送Forum用户干预消息"""
        if session_id not in self.session_types:
            logger.error(f"会话不存在: {session_id}")
            return False
        
        forum_intervention_message = ForumUserInterventionMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            type=MessageType.FORUM_USER_INTERVENTION,
            session_id=session_id,
            timestamp=datetime.now(),
            entrance_type=EntranceType.FORUM,
            payload={},
            message=message
        )
        
        return await self.send_message(forum_intervention_message)
    
    async def send_dict_message(self, message_data: Dict[str, Any]) -> bool:
        """发送简单字典消息（向后兼容）"""
        try:
            # 创建基础消息
            message_type = message_data.get("type", "system_status")
            session_id = message_data.get("session_id", "default")
            
            # 根据消息类型确定入口类型
            if message_type.startswith("forum_"):
                entrance_type = EntranceType.FORUM
            else:
                entrance_type = EntranceType.SECRETARIAT
            
            base_message = BaseMessage(
                message_id=f"msg_{uuid.uuid4().hex[:8]}",
                type=MessageType(message_type),
                session_id=session_id,
                timestamp=datetime.now(),
                entrance_type=entrance_type,
                payload=message_data
            )
            
            return await self.send_message(base_message)
            
        except Exception as e:
            logger.error(f"发送字典消息失败: {e}")
            return False
    
    def register_forum_handler(self, handler: Callable):
        """注册Forum专用处理器"""
        self.forum_handler = handler
        logger.info("注册Forum专用处理器")
    
    def register_handler(self, message_type: MessageType, handler: Callable,
                         entrance_type: Optional[EntranceType] = None):
        """注册消息处理器"""
        if entrance_type:
            if entrance_type not in self.entrance_handlers:
                self.entrance_handlers[entrance_type] = {}
            if message_type not in self.entrance_handlers[entrance_type]:
                self.entrance_handlers[entrance_type][message_type] = []
            self.entrance_handlers[entrance_type][message_type].append(handler)
        else:
            if message_type not in self.message_handlers:
                self.message_handlers[message_type] = []
            self.message_handlers[message_type].append(handler)
        
        logger.info(f"注册处理器: {message_type.value} ({entrance_type.value if entrance_type else '通用'})")
    
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
                    await self._handle_message(message)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"消息处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _send_to_backend(self, message: BaseMessage):
        """发送消息到后端"""
        try:
            logger.debug(f"发送到后端: {message.type.value}")
            
            # 更新会话统计
            if message.session_id in self.active_sessions:
                self.active_sessions[message.session_id]["message_count"] += 1
            
            # 这里应该是实际的WebSocket发送逻辑
            # await self.websocket.send(json.dumps(message.to_dict()))
            
        except Exception as e:
            logger.error(f"发送到后端失败: {e}")
    
    async def _handle_message(self, message: BaseMessage):
        """处理接收到的消息"""
        try:
            self.stats["messages_received"] += 1
            self.stats["last_activity"] = datetime.now()
            
            # 通用处理器
            if message.type in self.message_handlers:
                for handler in self.message_handlers[message.type]:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"通用处理器执行失败 {message.type.value}: {e}")
            
            # 入口特定处理器
            if message.entrance_type in self.entrance_handlers:
                entrance_handlers = self.entrance_handlers[message.entrance_type]
                if message.type in entrance_handlers:
                    for handler in entrance_handlers[message.type]:
                        try:
                            await handler(message)
                        except Exception as e:
                            logger.error(f"入口处理器执行失败 {message.entrance_type.value}.{message.type.value}: {e}")
            
            # Forum专用处理器
            if message.entrance_type == EntranceType.FORUM and self.forum_handler:
                try:
                    await self.forum_handler(message.payload)
                except Exception as e:
                    logger.error(f"Forum处理器执行失败: {e}")
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            self.stats["errors"] += 1
    
    async def _heartbeat(self):
        """心跳检测"""
        while self.is_connected:
            try:
                # 发送心跳消息
                heartbeat_message = BaseMessage(
                    message_id=f"heartbeat_{uuid.uuid4().hex[:8]}",
                    type=MessageType.SYSTEM_STATUS,
                    session_id="system",
                    timestamp=datetime.now(),
                    entrance_type=EntranceType.SECRETARIAT,
                    payload={
                        "action": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                await self.send_message(heartbeat_message)
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"心跳检测错误: {e}")
                await asyncio.sleep(5)
    
    async def _connection_monitor(self):
        """连接监控"""
        while self.is_connected:
            try:
                # 检查连接状态
                if self.stats["last_activity"]:
                    idle_time = (datetime.now() - self.stats["last_activity"]).total_seconds()
                    if idle_time > 60:  # 60秒无活动
                        logger.warning(f"连接空闲时间过长: {idle_time}秒")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"连接监控错误: {e}")
                await asyncio.sleep(5)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """获取连接状态"""
        return {
            "connected": self.is_connected,
            "backend_url": self.backend_url,
            "retry_count": self.connection_retry_count,
            "active_sessions": len(self.active_sessions),
            "outgoing_queue_size": self.outgoing_queue.qsize(),
            "incoming_queue_size": self.incoming_queue.qsize(),
            "stats": self.stats
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        return self.active_sessions.get(session_id)
    
    def get_entrance_sessions(self, entrance_type: EntranceType) -> List[str]:
        """获取特定入口类型的会话列表"""
        return [
            session_id for session_id, etype in self.session_types.items()
            if etype == entrance_type
        ]


# 全局双入口WebSocket管理器实例
dual_entrance_websocket_manager = DualEntranceWebSocketManager()