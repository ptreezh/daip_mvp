#!/usr/bin/env python3
"""
@Time    : 2025-08-18 10:30:00
@Author  : DAIP-LIVE Team
@File    : debate_stream.py
@Description:
    DebateStream辩论流组件 - 实现辩论过程的实时显示和管理
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from lona.html import Widget, Div, HTML, Button, Span, H3, P, Pre
from lona.html import TextInput as LonaInput

from ..services.forum_websocket_integration import forum_websocket_integration
from .rich_text_renderer import rich_text_renderer

# 配置日志
logger = logging.getLogger(__name__)


class DebateStreamStatus(Enum):
    """辩论流状态枚举"""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class DebateMessageType(Enum):
    """辩论消息类型枚举"""
    AGENT_ARGUMENT = "agent_argument"
    USER_INTERVENTION = "user_intervention"
    CONSENSUS_UPDATE = "consensus_update"
    STATUS_CHANGE = "status_change"
    SYSTEM_MESSAGE = "system_message"


class DebateMessage:
    """辩论消息数据类"""
    
    def __init__(self, message_type: DebateMessageType, content: str, 
                 sender: str = "", timestamp: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = f"debate_msg_{datetime.now().timestamp()}"
        self.message_type = message_type
        self.content = content
        self.sender = sender
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}


class DebateStream(Widget):
    """辩论流组件 - 实时显示辩论过程"""
    
    def __init__(self, session_id: str, topic: str):
        super().__init__()
        
        self.session_id = session_id
        self.topic = topic
        self.status = DebateStreamStatus.IDLE
        self.messages: List[DebateMessage] = []
        self.current_round = 0
        self.is_paused = False
        
        # 回调函数
        self.on_pause_toggle = None
        self.on_message_add = None
        
        # 创建UI元素
        self.create_ui()
        
        # 设置WebSocket处理
        self.setup_websocket_handlers()
        
        logger.info(f"DebateStream初始化完成，会话ID: {session_id}")
    
    def create_ui(self):
        """创建UI元素"""
        # 辩论流头部
        self.stream_header = Div(
            H3("🎯 辩论流", _class="debate-stream-title"),
            Div(
                Span(f"话题: {self.topic}", _class="debate-topic"),
                Span(f"状态: {self.get_status_text()}", _class="debate-status"),
                Span(f"轮次: {self.current_round}", _class="debate-round"),
                _class="debate-stream-info"
            ),
            _class="debate-stream-header"
        )
        
        # 控制按钮
        self.control_panel = Div(
            Button(
                "⏸️ 暂停",
                _class="btn btn-warning debate-pause-btn",
                disabled=self.status != DebateStreamStatus.ACTIVE
            ),
            Button(
                "📊 共识",
                _class="btn btn-info debate-consensus-btn",
                disabled=False
            ),
            Button(
                "🗑️ 清空",
                _class="btn btn-secondary debate-clear-btn",
                disabled=False
            ),
            _class="debate-control-panel"
        )
        
        # 消息显示区域
        self.message_container = Div(
            Div(
                P("等待辩论开始...", _class="debate-placeholder"),
                _class="debate-messages"
            ),
            _class="debate-message-container"
        )
        
        # 消息输入区域
        self.input_area = Div(
            LonaInput(
                placeholder="输入您的观点或问题...",
                _class="debate-input"
            ),
            Button(
                "💬 发送",
                _class="btn btn-primary debate-send-btn"
            ),
            _class="debate-input-area"
        )
        
        # 绑定事件
        self.control_panel.nodes[0].handle_click = self.handle_pause_click
        self.control_panel.nodes[1].handle_click = self.handle_consensus_click
        self.control_panel.nodes[2].handle_click = self.handle_clear_click
        self.input_area.nodes[1].handle_click = self.handle_send_click
    
    def setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        forum_websocket_integration.register_handler(
            f"debate_stream_{self.session_id}",
            self.handle_websocket_message
        )
    
    async def handle_websocket_message(self, message_type: str, data: Dict[str, Any]):
        """处理WebSocket消息"""
        try:
            if message_type == "agent_argument":
                await self.add_agent_argument(
                    content=data.get("content", ""),
                    sender=data.get("sender", "Agent"),
                    agent_id=data.get("agent_id", "")
                )
            elif message_type == "consensus_update":
                await self.update_consensus(data.get("consensus_level", 0.0))
            elif message_type == "status_change":
                await self.update_status(data.get("status", "active"))
            elif message_type == "system_message":
                await self.add_system_message(data.get("content", ""))
                
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
    
    def handle_pause_click(self, event):
        """处理暂停/恢复点击"""
        if self.on_pause_toggle:
            self.on_pause_toggle(self.is_paused)
    
    def handle_consensus_click(self, event):
        """处理共识按钮点击"""
        # 触发共识计算
        asyncio.create_task(self.trigger_consensus())
    
    def handle_clear_click(self, event):
        """处理清空按钮点击"""
        self.clear_messages()
    
    def handle_send_click(self, event):
        """处理发送按钮点击"""
        user_input = self.input_area.nodes[0].value.strip()
        if user_input:
            asyncio.create_task(self.send_user_message(user_input))
            self.input_area.nodes[0].value = ""
    
    async def start_debate(self, agents: List[str]):
        """开始辩论"""
        try:
            self.status = DebateStreamStatus.ACTIVE
            self.current_round = 1
            self.is_paused = False
            
            # 添加开始消息
            start_msg = DebateMessage(
                message_type=DebateMessageType.SYSTEM_MESSAGE,
                content=f"🚀 辩论开始\n\n**话题**: {self.topic}\n**参与者**: {', '.join(agents)}",
                sender="System"
            )
            self.add_message(start_msg)
            
            # 更新UI
            self.update_ui()
            
            # 通知WebSocket集成
            await forum_websocket_integration.start_debate(
                session_id=self.session_id,
                topic=self.topic,
                agents=agents
            )
            
            logger.info(f"辩论已开始: {self.session_id}")
            
        except Exception as e:
            logger.error(f"开始辩论失败: {e}")
            self.status = DebateStreamStatus.ERROR
            self.update_ui()
    
    async def pause_debate(self):
        """暂停辩论"""
        self.is_paused = True
        self.status = DebateStreamStatus.PAUSED
        
        pause_msg = DebateMessage(
            message_type=DebateMessageType.SYSTEM_MESSAGE,
            content="⏸️ 辩论已暂停",
            sender="System"
        )
        self.add_message(pause_msg)
        self.update_ui()
        
        logger.info(f"辩论已暂停: {self.session_id}")
    
    async def resume_debate(self):
        """恢复辩论"""
        self.is_paused = False
        self.status = DebateStreamStatus.ACTIVE
        
        resume_msg = DebateMessage(
            message_type=DebateMessageType.SYSTEM_MESSAGE,
            content="▶️ 辩论已恢复",
            sender="System"
        )
        self.add_message(resume_msg)
        self.update_ui()
        
        logger.info(f"辩论已恢复: {self.session_id}")
    
    async def end_debate(self):
        """结束辩论"""
        self.status = DebateStreamStatus.COMPLETED
        
        end_msg = DebateMessage(
            message_type=DebateMessageType.SYSTEM_MESSAGE,
            content=f"🏁 辩论结束\n\n**总轮次**: {self.current_round}\n**消息数量**: {len(self.messages)}",
            sender="System"
        )
        self.add_message(end_msg)
        self.update_ui()
        
        logger.info(f"辩论已结束: {self.session_id}")
    
    async def add_agent_argument(self, content: str, sender: str, agent_id: str):
        """添加Agent论点"""
        if self.is_paused:
            return
            
        argument_msg = DebateMessage(
            message_type=DebateMessageType.AGENT_ARGUMENT,
            content=content,
            sender=sender,
            metadata={"agent_id": agent_id, "round": self.current_round}
        )
        self.add_message(argument_msg)
        self.update_ui()
    
    async def send_user_message(self, content: str):
        """发送用户消息"""
        user_msg = DebateMessage(
            message_type=DebateMessageType.USER_INTERVENTION,
            content=content,
            sender="User"
        )
        self.add_message(user_msg)
        
        # 发送到WebSocket
        await forum_websocket_integration.send_user_intervention(
            session_id=self.session_id,
            content=content
        )
        
        self.update_ui()
    
    async def add_system_message(self, content: str):
        """添加系统消息"""
        system_msg = DebateMessage(
            message_type=DebateMessageType.SYSTEM_MESSAGE,
            content=content,
            sender="System"
        )
        self.add_message(system_msg)
        self.update_ui()
    
    async def update_consensus(self, consensus_level: float):
        """更新共识度"""
        consensus_msg = DebateMessage(
            message_type=DebateMessageType.CONSENSUS_UPDATE,
            content=f"📊 当前共识度: {consensus_level:.1%}",
            sender="System",
            metadata={"consensus_level": consensus_level}
        )
        self.add_message(consensus_msg)
        self.update_ui()
    
    async def update_status(self, status: str):
        """更新状态"""
        status_msg = DebateMessage(
            message_type=DebateMessageType.STATUS_CHANGE,
            content=f"🔄 状态更新: {status}",
            sender="System"
        )
        self.add_message(status_msg)
        self.update_ui()
    
    async def trigger_consensus(self):
        """触发共识计算"""
        try:
            await forum_websocket_integration.trigger_consensus(
                session_id=self.session_id
            )
            
            # 显示触发消息
            trigger_msg = DebateMessage(
                message_type=DebateMessageType.SYSTEM_MESSAGE,
                content="🔄 正在计算共识...",
                sender="System"
            )
            self.add_message(trigger_msg)
            self.update_ui()
            
        except Exception as e:
            logger.error(f"触发共识计算失败: {e}")
    
    def add_message(self, message: DebateMessage):
        """添加消息到辩论流"""
        self.messages.append(message)
        
        # 限制消息数量，保持性能
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]
    
    def clear_messages(self):
        """清空消息"""
        self.messages.clear()
        
        placeholder_msg = DebateMessage(
            message_type=DebateMessageType.SYSTEM_MESSAGE,
            content="🧹 消息已清空",
            sender="System"
        )
        self.add_message(placeholder_msg)
        self.update_ui()
    
    def update_ui(self):
        """更新UI显示"""
        # 更新头部信息
        self.stream_header.nodes = [
            H3("🎯 辩论流", _class="debate-stream-title"),
            Div(
                Span(f"话题: {self.topic}", _class="debate-topic"),
                Span(f"状态: {self.get_status_text()}", _class="debate-status"),
                Span(f"轮次: {self.current_round}", _class="debate-round"),
                _class="debate-stream-info"
            )
        ]
        
        # 更新控制按钮
        pause_button = self.control_panel.nodes[0]
        pause_button.disabled = self.status != DebateStreamStatus.ACTIVE
        pause_button.nodes[0] = "▶️ 恢复" if self.is_paused else "⏸️ 暂停"
        
        # 更新消息显示
        if self.messages:
            message_elements = []
            for msg in self.messages:
                message_elements.append(self.render_message(msg))
            self.message_container.nodes[0] = Div(*message_elements, _class="debate-messages")
        else:
            self.message_container.nodes[0] = Div(
                P("等待辩论开始...", _class="debate-placeholder"),
                _class="debate-messages"
            )
    
    def render_message(self, message: DebateMessage) -> Div:
        """渲染单条消息"""
        # 根据消息类型设置样式
        if message.message_type == DebateMessageType.AGENT_ARGUMENT:
            message_class = "debate-message agent-message"
            icon = "🤖"
        elif message.message_type == DebateMessageType.USER_INTERVENTION:
            message_class = "debate-message user-message"
            icon = "👤"
        elif message.message_type == DebateMessageType.CONSENSUS_UPDATE:
            message_class = "debate-message consensus-message"
            icon = "📊"
        elif message.message_type == DebateMessageType.STATUS_CHANGE:
            message_class = "debate-message status-message"
            icon = "🔄"
        else:
            message_class = "debate-message system-message"
            icon = "📢"
        
        # 渲染消息内容
        content_html = rich_text_renderer.render(message.content, "debate_message")
        
        return Div(
            Div(
                Span(f"{icon} {message.sender}", _class="debate-message-sender"),
                Span(message.timestamp.strftime("%H:%M:%S"), _class="debate-message-time"),
                _class="debate-message-header"
            ),
            Div(content_html, _class="debate-message-content"),
            _class=message_class
        )
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        status_map = {
            DebateStreamStatus.IDLE: "空闲",
            DebateStreamStatus.ACTIVE: "活跃",
            DebateStreamStatus.PAUSED: "暂停",
            DebateStreamStatus.COMPLETED: "已完成",
            DebateStreamStatus.ERROR: "错误"
        }
        return status_map.get(self.status, "未知")
    
    def get_debate_summary(self) -> Dict[str, Any]:
        """获取辩论摘要"""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "status": self.status.value,
            "current_round": self.current_round,
            "total_messages": len(self.messages),
            "is_paused": self.is_paused,
            "agent_messages": len([m for m in self.messages if m.message_type == DebateMessageType.AGENT_ARGUMENT]),
            "user_messages": len([m for m in self.messages if m.message_type == DebateMessageType.USER_INTERVENTION])
        }
    
    def render(self) -> HTML:
        """渲染辩论流组件"""
        return Div(
            self.stream_header,
            self.control_panel,
            self.message_container,
            self.input_area,
            _class="debate-stream-widget"
        )