#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天界面组件

提供用户与Personal Assistant交互的主要界面
支持消息发送、接收、历史记录和特殊命令处理
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from lona.html.widget import Widget
from lona.html import HTML, Div, TextInput, Button, P, Span, H3, Pre, Code

from services.personal_assistant import PersonalAssistantService, ConversationContext
from services.websocket_manager import websocket_manager, MessageType, WebSocketMessage
from components.rich_text_renderer import rich_text_renderer

# 配置日志
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    WORKFLOW_STATUS = "workflow_status"
    AGENT_OUTPUT = "agent_output"
    CONSENSUS_RESULT = "consensus_result"
    SYSTEM_INFO = "system_info"
    ERROR = "error"
    COMMAND = "command"


class ChatMessage:
    """聊天消息数据类"""
    
    def __init__(self, sender: str, content: str, message_type: MessageType = MessageType.TEXT, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = f"msg_{datetime.now().timestamp()}"
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.metadata = metadata or {}


class ChatInterface(Widget):
    """聊天界面组件"""
    
    def __init__(self, assistant_service: PersonalAssistantService):
        super().__init__()
        
        self.assistant_service = assistant_service
        self.messages: List[ChatMessage] = []
        self.session_id = f"session_{datetime.now().timestamp()}"
        self.is_processing = False
        
        # 创建UI元素
        self.message_input = TextInput(
            placeholder="输入您的消息或问题...",
            _class="message-input-field"
        )
        self.send_button = Button(
            "发送",
            _class="btn btn-primary send-button"
        )
        
        # 绑定事件 - 使用Lona的正确事件处理方式
        self.send_button.handle_click = self.handle_send_click
        
        # 添加欢迎消息
        self._add_welcome_message()
        
        # 注册WebSocket消息处理
        self._setup_websocket_handlers()
        
        logger.info(f"聊天界面初始化完成，会话ID: {self.session_id}")
    
    def _add_welcome_message(self):
        """添加欢迎消息"""
        welcome_msg = ChatMessage(
            sender="assistant",
            content="🎭 欢迎使用 Personal Intelligence Hub！\\n\\n我是您的智能助手，可以帮您：\\n" +
                   "• 🔍 进行深度分析和批判性审查\\n" +
                   "• 🎯 组织多视角讨论和辩论\\n" +
                   "• 📚 管理知识库和任务\\n" +
                   "• 🤖 创建自定义工作流\\n\\n" +
                   "请告诉我您想要分析或讨论的话题！\\n\\n" +
                   "💡 **特殊命令**：\\n" +
                   "• `/consensus now` - 触发当前辩论的共识计算\\n" +
                   "• `/status` - 查看系统状态\\n" +
                   "• `/help` - 显示帮助信息",
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(welcome_msg)
    
    def _setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        websocket_manager.register_chat_handler(self._handle_websocket_message)
    
    async def _handle_websocket_message(self, message: WebSocketMessage):
        """处理WebSocket消息"""
        try:
            if message.type == MessageType.AGENT_OUTPUT:
                # 代理输出消息
                agent_msg = ChatMessage(
                    sender=message.payload.get("agent_name", "Agent"),
                    content=message.payload.get("content", ""),
                    message_type=MessageType.AGENT_OUTPUT,
                    metadata={
                        "agent_id": message.payload.get("agent_id"),
                        "reasoning_framework": message.payload.get("reasoning_framework")
                    }
                )
                self.messages.append(agent_msg)
                await self.refresh()
                
            elif message.type == MessageType.WORKFLOW_STATUS:
                # 工作流状态更新
                status_msg = ChatMessage(
                    sender="system",
                    content=f"🔄 工作流状态更新: {message.payload.get('status', 'unknown')}",
                    message_type=MessageType.WORKFLOW_STATUS,
                    metadata=message.payload
                )
                self.messages.append(status_msg)
                await self.refresh()
                
            elif message.type == MessageType.CONSENSUS_RESULT:
                # 共识结果
                consensus_msg = ChatMessage(
                    sender="system",
                    content=f"🎯 共识结果: {message.payload.get('result', 'No consensus')}\\n" +
                           f"置信度: {message.payload.get('confidence', 0):.2f}",
                    message_type=MessageType.CONSENSUS_RESULT,
                    metadata=message.payload
                )
                self.messages.append(consensus_msg)
                await self.refresh()
                
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
    
    # Lona的TextInput不支持keydown事件，移除此方法
    
    async def handle_send_click(self, event):
        """处理发送按钮点击"""
        await self.send_message()
    
    async def send_message(self):
        """发送消息"""
        if self.is_processing:
            return
        
        user_input = self.message_input.value.strip()
        if not user_input:
            return
        
        try:
            self.is_processing = True
            self.send_button.disabled = True
            self.message_input.disabled = True
            
            # 添加用户消息
            user_message = ChatMessage(
                sender="user",
                content=user_input,
                message_type=MessageType.TEXT
            )
            self.messages.append(user_message)
            
            # 更新对话上下文
            self.assistant_service.update_conversation_context(
                self.session_id,
                {
                    "sender": "user",
                    "content": user_input,
                    "type": "text"
                }
            )
            
            # 清空输入框并刷新界面
            self.message_input.value = ""
            await self.refresh()
            
            # 检查是否是特殊命令
            if user_input.startswith('/'):
                await self._handle_command(user_input)
            else:
                # 处理普通消息
                await self._process_user_message(user_input)
                
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            error_msg = ChatMessage(
                sender="system",
                content=f"❌ 发送消息时出现错误: {str(e)}",
                message_type=MessageType.ERROR
            )
            self.messages.append(error_msg)
            await self.refresh()
            
        finally:
            self.is_processing = False
            self.send_button.disabled = False
            self.message_input.disabled = False
            await self.refresh()
    
    async def _handle_command(self, command: str):
        """处理特殊命令"""
        command = command.lower().strip()
        
        if command == '/consensus now':
            await self._trigger_consensus()
        elif command == '/status':
            await self._show_system_status()
        elif command == '/help':
            await self._show_help()
        elif command == '/clear':
            await self._clear_chat()
        else:
            error_msg = ChatMessage(
                sender="system",
                content=f"❌ 未知命令: {command}\\n输入 `/help` 查看可用命令",
                message_type=MessageType.ERROR
            )
            self.messages.append(error_msg)
    
    async def _trigger_consensus(self):
        """触发共识计算"""
        try:
            # 发送共识触发消息到WebSocket
            consensus_message = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                payload={
                    "action": "trigger_consensus",
                    "session_id": self.session_id
                }
            )
            await websocket_manager.send_message(consensus_message)
            
            # 添加系统消息
            system_msg = ChatMessage(
                sender="system",
                content="🎯 正在计算当前辩论的共识结果...",
                message_type=MessageType.SYSTEM_INFO
            )
            self.messages.append(system_msg)
            
        except Exception as e:
            logger.error(f"触发共识失败: {e}")
    
    async def _show_system_status(self):
        """显示系统状态"""
        try:
            # 获取WebSocket连接状态
            ws_status = websocket_manager.get_connection_status()
            
            status_content = f"""📊 **系统状态报告**
            
🔌 **连接状态**: {'✅ 已连接' if ws_status['connected'] else '❌ 未连接'}
🌐 **后端地址**: {ws_status['backend_url']}
🔄 **重试次数**: {ws_status['retry_count']}
👥 **活跃会话**: {ws_status['active_sessions']}
📤 **发送队列**: {ws_status['outgoing_queue_size']} 条消息
📥 **接收队列**: {ws_status['incoming_queue_size']} 条消息
💬 **当前会话**: {self.session_id}
📝 **消息历史**: {len(self.messages)} 条消息
"""
            
            status_msg = ChatMessage(
                sender="system",
                content=status_content,
                message_type=MessageType.SYSTEM_INFO
            )
            self.messages.append(status_msg)
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
    
    async def _show_help(self):
        """显示帮助信息"""
        help_content = """🆘 **Personal Intelligence Hub 帮助**

**基本功能**:
• 输入任何话题进行智能分析和讨论
• 系统会自动组建专家团队进行多角度分析
• 支持批判性审查和多视角综合分析

**特殊命令**:
• `/consensus now` - 触发当前辩论的共识计算
• `/status` - 查看系统连接和运行状态
• `/help` - 显示此帮助信息
• `/clear` - 清空聊天历史

**使用示例**:
• "分析人工智能的发展趋势"
• "讨论气候变化的解决方案"
• "评估新技术的伦理影响"

**快捷键**:
• Enter - 发送消息
• Shift+Enter - 换行

💡 **提示**: 您可以随时输入新话题，系统会智能识别并启动相应的分析流程。
"""
        
        help_msg = ChatMessage(
            sender="system",
            content=help_content,
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(help_msg)
    
    async def _clear_chat(self):
        """清空聊天历史"""
        self.messages.clear()
        self._add_welcome_message()
        
        clear_msg = ChatMessage(
            sender="system",
            content="🧹 聊天历史已清空",
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(clear_msg)
    
    async def _process_user_message(self, user_input: str):
        """处理用户消息"""
        try:
            # 显示处理中状态
            processing_msg = ChatMessage(
                sender="assistant",
                content="🤔 正在分析您的请求...",
                message_type=MessageType.SYSTEM_INFO
            )
            self.messages.append(processing_msg)
            await self.refresh()
            
            # 调用个人助手服务处理消息
            response = await self.assistant_service.process_message(user_input, self.session_id)
            
            # 移除处理中消息
            self.messages.remove(processing_msg)
            
            # 添加助手回复
            assistant_msg = ChatMessage(
                sender="assistant",
                content=response,
                message_type=MessageType.TEXT
            )
            self.messages.append(assistant_msg)
            
            # 更新对话上下文
            self.assistant_service.update_conversation_context(
                self.session_id,
                {
                    "sender": "assistant",
                    "content": response,
                    "type": "text"
                }
            )
            
        except Exception as e:
            logger.error(f"处理用户消息失败: {e}")
            
            # 移除处理中消息（如果存在）
            try:
                self.messages.remove(processing_msg)
            except:
                pass
            
            error_msg = ChatMessage(
                sender="system",
                content=f"❌ 处理消息时出现错误: {str(e)}",
                message_type=MessageType.ERROR
            )
            self.messages.append(error_msg)
    
    def _render_message(self, message: ChatMessage) -> HTML:
        """渲染单条消息"""
        # 确定消息样式类
        if message.sender == "user":
            message_class = "message user"
        elif message.sender == "assistant":
            message_class = "message assistant"
        elif message.message_type == MessageType.AGENT_OUTPUT:
            message_class = "message agent"
        elif message.message_type == MessageType.SYSTEM_INFO:
            message_class = "message system-info"
        elif message.message_type == MessageType.ERROR:
            message_class = "message error"
        elif message.message_type == MessageType.WORKFLOW_STATUS:
            message_class = "message workflow-status"
        elif message.message_type == MessageType.CONSENSUS_RESULT:
            message_class = "message consensus-result"
        else:
            message_class = "message"
        
        # 处理消息内容
        content_elements = []
        
        # 添加发送者标识（对于代理消息）
        if message.message_type == MessageType.AGENT_OUTPUT:
            agent_name = message.metadata.get("agent_name", message.sender)
            reasoning_framework = message.metadata.get("reasoning_framework", "")
            
            sender_info = Div(
                Span(f"🤖 {agent_name}", _class="agent-name"),
                Span(f"推理框架: {reasoning_framework}", _class="agent-framework") if reasoning_framework else Span(),
                _class="message-sender-info"
            )
            content_elements.append(sender_info)
        
        # 使用富文本渲染器处理内容
        try:
            # 根据消息类型选择渲染方式
            if message.message_type == MessageType.AGENT_OUTPUT:
                rendered_content = rich_text_renderer.render(message.content, "agent_output")
            elif message.message_type == MessageType.WORKFLOW_STATUS:
                rendered_content = rich_text_renderer.render(message.metadata, "workflow_status")
            elif message.content.startswith('```') and message.content.endswith('```'):
                # 代码块
                rendered_content = rich_text_renderer.render(message.content, "code")
            elif '**' in message.content or '*' in message.content or '#' in message.content:
                # 可能包含Markdown
                rendered_content = rich_text_renderer.render(message.content, "markdown")
            else:
                # 普通文本
                rendered_content = rich_text_renderer.render(message.content, "text")
            
            content_elements.append(rendered_content)
            
        except Exception as e:
            logger.error(f"富文本渲染失败: {e}")
            # 回退到简单文本渲染
            content_text = message.content.replace('\\n', '\n')
            lines = content_text.split('\n')
            for i, line in enumerate(lines):
                content_elements.append(line)
                if i < len(lines) - 1:
                    content_elements.append(HTML('<br>'))
        
        # 添加时间戳
        timestamp = Span(
            message.timestamp.strftime("%H:%M:%S"),
            _class="message-timestamp"
        )
        
        return Div(
            Div(
                *content_elements,
                _class="message-content"
            ),
            timestamp,
            _class=message_class
        )
    
    def render(self) -> HTML:
        """渲染聊天界面"""
        return Div(
            # 消息历史显示区域
            Div(
                *[self._render_message(msg) for msg in self.messages],
                _class="message-history",
                id="message-history"
            ),
            
            # 输入区域
            Div(
                self.message_input,
                self.send_button,
                _class="message-input"
            ),
            
            _class="chat-interface"
        )
    
    async def scroll_to_bottom(self):
        """滚动到底部（显示最新消息）"""
        # 这里可以添加JavaScript代码来滚动到底部
        # Lona框架支持执行客户端JavaScript
        pass
    
    async def add_agent_message(self, agent_name: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """添加代理消息（供外部调用）"""
        agent_msg = ChatMessage(
            sender=agent_name,
            content=content,
            message_type=MessageType.AGENT_OUTPUT,
            metadata=metadata or {}
        )
        self.messages.append(agent_msg)
        await self.refresh()
        await self.scroll_to_bottom()
    
    async def add_system_message(self, content: str, message_type: MessageType = MessageType.SYSTEM_INFO):
        """添加系统消息（供外部调用）"""
        system_msg = ChatMessage(
            sender="system",
            content=content,
            message_type=message_type
        )
        self.messages.append(system_msg)
        await self.refresh()
        await self.scroll_to_bottom()
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """获取消息历史（供外部调用）"""
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "type": msg.message_type.value,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in self.messages
        ]
    
    def clear_messages(self):
        """清空消息历史（供外部调用）"""
        self.messages.clear()
        self._add_welcome_message()
