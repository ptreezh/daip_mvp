#!/usr/bin/env python3
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : forum_chat_interface.py
@Description:
    Forum模式聊天界面组件 - 实现多智能体协作和用户深度参与
"""

import asyncio
import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from lona.html.widget import Widget
from lona.html import HTML, Div, TextInput, Button, P, Span, H3, Select, Option, Pre, Code

from ..services.dual_entrance_websocket_manager import dual_entrance_websocket_manager
from ..services.forum_websocket_integration import forum_websocket_integration, ForumWebSocketEventType
from ..services.personal_assistant import PersonalAssistantService
from .rich_text_renderer import rich_text_renderer
from .forum_user_input_panel import ForumUserInputPanel
from .forum_context_panel import ForumContextPanel

# 配置日志
logger = logging.getLogger(__name__)


class ForumMessageType(Enum):
    """Forum消息类型枚举"""
    AGENT_MESSAGE = "agent_message"
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    CONTEXT_UPDATE = "context_update"
    CONSENSUS_UPDATE = "consensus_update"
    DEBATE_STATUS = "debate_status"


class ForumMessage:
    """Forum消息数据类"""
    
    def __init__(self, message_type: ForumMessageType, content: str, 
                 sender: str = "", agent_id: str = "", timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = f"forum_msg_{datetime.now().timestamp()}"
        self.message_type = message_type
        self.content = content
        self.sender = sender
        self.agent_id = agent_id
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}


class ForumChatInterface(Widget):
    """Forum聊天界面组件"""
    
    def __init__(self, assistant_service: PersonalAssistantService, session_id: Optional[str] = None):
        super().__init__()
        
        self.assistant_service = assistant_service
        self.session_id = session_id or f"forum_session_{uuid.uuid4()}"
        self.messages: List[ForumMessage] = []
        self.is_active = True
        self.current_topic = ""
        self.consensus_level = 0.0
        self.active_agents = []
        
        # 用户输入相关
        self.user_input = ""
        self.selected_intent = "comment"
        self.optimized_preview = ""
        
        # 回调函数
        self.on_user_intervention = None
        self.on_context_update = None
        
        # 创建子组件
        self.user_input_panel = ForumUserInputPanel(self.session_id)
        self.context_panel = ForumContextPanel(self.session_id)
        
        # 设置回调
        self.user_input_panel.on_user_intervention = self.handle_user_intervention
        self.on_context_update = self.context_panel.update_context
        
        # 创建UI元素
        self.pause_button = Button(
            "⏸️ 暂停",
            _class="btn btn-secondary forum-pause-button"
        )
        
        # 绑定事件
        self.pause_button.handle_click = self.handle_pause_click
        
        # 添加欢迎消息
        self._add_welcome_message()
        
        # 设置WebSocket处理
        self._setup_websocket_handlers()
        self._setup_forum_integration()
        
        logger.info(f"Forum聊天界面初始化完成，会话ID: {self.session_id}")
    
    def _add_welcome_message(self):
        """添加Forum欢迎消息"""
        welcome_msg = ForumMessage(
            message_type=ForumMessageType.SYSTEM_MESSAGE,
            content="""🏛️ 欢迎来到 **The Forum** - 智能协作空间

这里是多智能体协作和深度讨论的专门场所。

**核心功能**:
• 🤖 **多智能体协作**: 131+专家AI实时协作讨论
• 🎯 **用户参与**: 您可以随时参与讨论、引导方向
• 📊 **共识追踪**: 实时显示讨论进展和共识形成
• 💡 **智能优化**: 您的输入会被智能优化并集成到讨论中

**使用指南**:
1. 选择输入意图类型（评论、提问、建议、纠正）
2. 输入您的观点或问题
3. 观察AI专家们的实时讨论
4. 随时通过优化后的输入参与讨论

**开始讨论**:
请输入您想要探讨的话题，系统会自动组建专家团队开始协作！""",
            sender="Forum"
        )
        self.messages.append(welcome_msg)
    
    def _setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        dual_entrance_websocket_manager.register_forum_handler(self._handle_websocket_message)
    
    def _setup_forum_integration(self):
        """设置Forum集成"""
        # 注册事件处理器
        forum_websocket_integration.register_event_handler(
            ForumWebSocketEventType.AGENT_MESSAGE, self._handle_agent_message_event
        )
        forum_websocket_integration.register_event_handler(
            ForumWebSocketEventType.CONTEXT_UPDATE, self._handle_context_update_event
        )
        forum_websocket_integration.register_event_handler(
            ForumWebSocketEventType.CONSENSUS_UPDATE, self._handle_consensus_update_event
        )
        forum_websocket_integration.register_event_handler(
            ForumWebSocketEventType.DEBATE_STATUS, self._handle_debate_status_event
        )
    
    async def _handle_websocket_message(self, message_data: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            msg_type = message_data.get("type")
            
            if msg_type == "agent_message":
                # Agent消息
                agent_msg = ForumMessage(
                    message_type=ForumMessageType.AGENT_MESSAGE,
                    content=message_data.get("content", ""),
                    sender=message_data.get("agent_name", "Agent"),
                    agent_id=message_data.get("agent_id", ""),
                    metadata=message_data.get("metadata", {})
                )
                self.messages.append(agent_msg)
                
            elif msg_type == "context_update":
                # 上下文更新
                context_data = message_data.get("data", {})
                self.current_topic = context_data.get("topic", "")
                self.consensus_level = context_data.get("consensus_level", 0.0)
                self.active_agents = context_data.get("active_agents", [])
                
                # 触发上下文更新回调
                if self.on_context_update:
                    await self.on_context_update(context_data)
                
            elif msg_type == "consensus_update":
                # 共识更新
                self.consensus_level = message_data.get("consensus_level", 0.0)
                
            elif msg_type == "debate_status":
                # 辩论状态更新
                status_msg = ForumMessage(
                    message_type=ForumMessageType.DEBATE_STATUS,
                    content=message_data.get("message", ""),
                    sender="System",
                    metadata=message_data
                )
                self.messages.append(status_msg)
                
        except Exception as e:
            logger.error(f"处理Forum WebSocket消息失败: {e}")
    
    async def _handle_agent_message_event(self, event: Dict[str, Any]):
        """处理Agent消息事件"""
        try:
            agent_msg = ForumMessage(
                message_type=ForumMessageType.AGENT_MESSAGE,
                content=event.get("content", ""),
                sender=event.get("agent_name", "Agent"),
                agent_id=event.get("agent_id", ""),
                metadata=event.get("metadata", {})
            )
            self.messages.append(agent_msg)
            
        except Exception as e:
            logger.error(f"处理Agent消息事件失败: {e}")
    
    async def _handle_context_update_event(self, event: Dict[str, Any]):
        """处理上下文更新事件"""
        try:
            context_data = event.get("context_data", {})
            self.current_topic = context_data.get("topic", "")
            self.consensus_level = context_data.get("consensus_level", 0.0)
            self.active_agents = context_data.get("active_agents", [])
            
            # 触发上下文更新回调
            if self.on_context_update:
                await self.on_context_update(context_data)
                
        except Exception as e:
            logger.error(f"处理上下文更新事件失败: {e}")
    
    async def _handle_consensus_update_event(self, event: Dict[str, Any]):
        """处理共识更新事件"""
        try:
            self.consensus_level = event.get("consensus_level", 0.0)
            
        except Exception as e:
            logger.error(f"处理共识更新事件失败: {e}")
    
    async def _handle_debate_status_event(self, event: Dict[str, Any]):
        """处理辩论状态事件"""
        try:
            status_msg = ForumMessage(
                message_type=ForumMessageType.DEBATE_STATUS,
                content=event.get("message", ""),
                sender="System",
                metadata=event
            )
            self.messages.append(status_msg)
            
        except Exception as e:
            logger.error(f"处理辩论状态事件失败: {e}")
    
    def handle_intent_change(self, event):
        """处理意图选择变化"""
        self.selected_intent = event.data
    
    async def handle_pause_click(self, event):
        """处理暂停/恢复点击"""
        self.is_active = not self.is_active
        self.pause_button.value = "▶️ 恢复" if not self.is_active else "⏸️ 暂停"
        
        # 使用Forum集成发送控制消息
        action = "pause" if not self.is_active else "resume"
        await forum_websocket_integration.send_session_control(self.session_id, action)
    
    async def handle_send_click(self, event):
        """处理发送按钮点击"""
        await self.send_user_input()
    
    async def send_user_input(self):
        """发送用户输入"""
        try:
            # 添加用户消息到界面
            user_msg = ForumMessage(
                message_type=ForumMessageType.USER_MESSAGE,
                content=self.user_input,
                sender="您",
                metadata={"intent": self.selected_intent}
            )
            self.messages.append(user_msg)
            
            # 使用Forum集成发送用户干预
            success = await forum_websocket_integration.send_user_intervention(
                self.session_id, self.user_input, self.selected_intent
            )
            
            if success:
                # 触发回调
                if self.on_user_intervention:
                    await self.on_user_intervention({
                        "type": "forum_user_intervention",
                        "message": {
                            "content": self.user_input,
                            "intent": self.selected_intent,
                            "timestamp": datetime.now().isoformat()
                        },
                        "session_id": self.session_id
                    })
                
                # 清空输入
                self.user_input = ""
            else:
                raise Exception("发送用户干预失败")
            
        except Exception as e:
            logger.error(f"发送用户输入失败: {e}")
            
            error_msg = ForumMessage(
                message_type=ForumMessageType.SYSTEM_MESSAGE,
                content=f"❌ 发送失败: {str(e)}",
                sender="System"
            )
            self.messages.append(error_msg)
    
    def handle_intent_change(self, event):
        """处理意图选择变化"""
        self.selected_intent = event.data
    
    def _render_agent_message(self, message: ForumMessage) -> HTML:
        """渲染Agent消息"""
        agent_avatar = message.sender[:2].upper() if message.sender else "AI"
        
        return Div(
            Div(
                Div(
                    Span(agent_avatar, _class="forum-agent-avatar"),
                    Div(
                        Span(message.sender, _class="forum-agent-name"),
                        Span(message.timestamp.strftime("%H:%M:%S"), _class="forum-message-time"),
                        _class="forum-agent-header"
                    ),
                    _class="forum-agent-info"
                ),
                Div(
                    rich_text_renderer.render(message.content, "forum_agent"),
                    _class="forum-message-content"
                ),
                _class="forum-agent-message"
            )
        )
    
    def _render_user_message(self, message: ForumMessage) -> HTML:
        """渲染用户消息"""
        intent_emoji = {
            "comment": "💬",
            "question": "❓", 
            "suggestion": "💡",
            "correction": "✏️"
        }.get(message.metadata.get("intent", "comment"), "💬")
        
        return Div(
            Div(
                Div(
                    Span(f"{intent_emoji} {message.sender}", _class="forum-user-header"),
                    Span(message.timestamp.strftime("%H:%M:%S"), _class="forum-message-time"),
                    _class="forum-user-info"
                ),
                Div(
                    rich_text_renderer.render(message.content, "forum_user"),
                    _class="forum-message-content"
                ),
                _class="forum-user-message"
            )
        )
    
    def _render_system_message(self, message: ForumMessage) -> HTML:
        """渲染系统消息"""
        return Div(
            Div(
                Span("📢 系统通知", _class="forum-system-header"),
                Span(message.timestamp.strftime("%H:%M:%S"), _class="forum-message-time"),
                _class="forum-system-info"
            ),
            Div(
                rich_text_renderer.render(message.content, "forum_system"),
                _class="forum-message-content"
            ),
            _class="forum-system-message"
        )
    
    def _render_message(self, message: ForumMessage) -> HTML:
        """渲染单条消息"""
        if message.message_type == ForumMessageType.AGENT_MESSAGE:
            return self._render_agent_message(message)
        elif message.message_type == ForumMessageType.USER_MESSAGE:
            return self._render_user_message(message)
        elif message.message_type == ForumMessageType.SYSTEM_MESSAGE:
            return self._render_system_message(message)
        elif message.message_type == ForumMessageType.DEBATE_STATUS:
            return self._render_system_message(message)
        else:
            # 默认渲染
            return Div(
                Div(
                    rich_text_renderer.render(message.content, "text"),
                    _class="forum-message-content"
                ),
                _class="forum-message"
            )
    
    def render(self) -> HTML:
        """渲染Forum聊天界面"""
        return Div(
            # 主要内容区域
            Div(
                # 辩论流区域
                Div(
                    *[self._render_message(msg) for msg in self.messages],
                    _class="forum-debate-stream",
                    id="forum-debate-stream"
                ),
                
                # 用户输入面板
                Div(
                    self.user_input_panel,
                    self.pause_button,
                    _class="forum-user-input-section"
                ),
                
                _class="forum-main-content"
            ),
            
            # 上下文面板
            Div(
                self.context_panel,
                _class="forum-sidebar"
            ),
            
            _class="forum-chat-interface"
        )
    
    async def start_forum_session(self, topic: str):
        """启动Forum会话"""
        try:
            self.current_topic = topic
            
            start_msg = ForumMessage(
                message_type=ForumMessageType.SYSTEM_MESSAGE,
                content=f"🚀 Forum会话已启动\n\n**讨论话题**: {topic}\n\n正在组建专家团队...",
                sender="Forum"
            )
            self.messages.append(start_msg)
            
            # 更新上下文面板
            self.context_panel.set_topic(topic)
            
            # 使用Forum集成启动会话
            await forum_websocket_integration.start_forum_session(topic)
            
        except Exception as e:
            logger.error(f"启动Forum会话失败: {e}")
            
            error_msg = ForumMessage(
                message_type=ForumMessageType.SYSTEM_MESSAGE,
                content=f"❌ 启动会话失败: {str(e)}",
                sender="System"
            )
            self.messages.append(error_msg)
    
    def get_forum_context(self) -> Dict[str, Any]:
        """获取Forum上下文信息"""
        return {
            "session_id": self.session_id,
            "topic": self.current_topic,
            "consensus_level": self.consensus_level,
            "active_agents": self.active_agents,
            "is_active": self.is_active,
            "message_count": len(self.messages)
        }
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """获取消息历史"""
        return [
            {
                "id": msg.id,
                "type": msg.message_type.value,
                "content": msg.content,
                "sender": msg.sender,
                "agent_id": msg.agent_id,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in self.messages
        ]
    
    def clear_messages(self):
        """清空消息历史"""
        self.messages.clear()
        self._add_welcome_message()
    
    async def add_agent_message(self, agent_name: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加Agent消息（供外部调用）"""
        agent_msg = ForumMessage(
            message_type=ForumMessageType.AGENT_MESSAGE,
            content=content,
            sender=agent_name,
            metadata=metadata or {}
        )
        self.messages.append(agent_msg)
    
    async def add_system_message(self, content: str):
        """添加系统消息（供外部调用）"""
        system_msg = ForumMessage(
            message_type=ForumMessageType.SYSTEM_MESSAGE,
            content=content,
            sender="System"
        )
        self.messages.append(system_msg)
    
    def set_consensus_level(self, level: float):
        """设置共识度"""
        self.consensus_level = level
    
    def update_active_agents(self, agents: List[str]):
        """更新活跃Agent列表"""
        self.active_agents = agents