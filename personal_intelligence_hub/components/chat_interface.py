"""Personal Intelligence Hub - Chat Interface Component

核心聊天对话界面组件
"""

import logging
from datetime import datetime

from lona.html import H3, HTML, Button, Div, TextInput

logger = logging.getLogger(__name__)


from personal_intelligence_hub.models.chat_models import ChatMessage, MessageType


class ChatInterface:
    """聊天界面组件"""
    
    def __init__(self, assistant_service, session_id: str = None):
        self.assistant_service = assistant_service
        self.session_id = session_id
        self.messages: list[ChatMessage] = []
        
        # 创建UI元素
        self.message_input = TextInput(
            placeholder="输入消息或命令 (如 /consensus now)...",
            _class="message-input"
        )
        self.send_button = Button("发送", _class="send-button")
        
        # 绑定事件
        self.send_button.onclick = self.handle_send_message
        self.message_input.onkeydown = self.handle_input_keydown
    
    async def handle_send_message(self, event):
        """处理发送消息事件"""
        message_text = self.message_input.value.strip()
        if not message_text:
            return
        
        # 创建用户消息
        user_message = ChatMessage(
            id=f"msg_{len(self.messages)}",
            sender="user",
            content=message_text,
            timestamp=datetime.now(),
            message_type=MessageType.TEXT
        )
        
        # 添加到消息列表
        self.messages.append(user_message)
        
        # 清空输入框
        self.message_input.value = ""
        
        # 刷新界面
        await self.refresh()
        
        # 处理特殊命令
        if message_text.startswith('/'):
            await self.handle_command(message_text)
        else:
            # 发送给Personal Assistant
            await self.send_to_assistant(message_text)
    
    async def handle_input_keydown(self, event):
        """处理输入框按键事件"""
        if event.key == 'Enter' and not event.shift_key:
            await self.handle_send_message(event)
    
    async def handle_command(self, command: str):
        """处理特殊命令"""
        try:
            session_id = self.session_id or "default_session"
            
            # 显示命令执行状态
            executing_message = ChatMessage(
                id=f"msg_{len(self.messages)}_executing",
                sender="system",
                content=f"⚡ 正在执行命令: {command}",
                timestamp=datetime.now(),
                message_type=MessageType.WORKFLOW_STATUS
            )
            self.messages.append(executing_message)
            await self.refresh()
            
            # 执行命令
            command_response_str = await self.assistant_service.execute_command(command, session_id)
            
            # 移除执行状态消息
            self.messages = [msg for msg in self.messages if msg.id != executing_message.id]
            
            # 确定消息类型
            if command == "/consensus now":
                message_type = MessageType.WORKFLOW_STATUS
            elif command in ["/help", "/status"]:
                message_type = MessageType.TEXT
            else:
                message_type = MessageType.TEXT
            
            # 添加命令结果
            response_message = ChatMessage(
                id=f"msg_{len(self.messages)}",
                sender="system",
                content=command_response_str,
                timestamp=datetime.now(),
                message_type=message_type
            )
            self.messages.append(response_message)
            
        except Exception as e:
            logger.error(f"Error handling command '{command}': {e}")
            # 移除执行状态消息（如果存在）
            self.messages = [msg for msg in self.messages if not msg.id.endswith("_executing")]
            
            error_message = ChatMessage(
                id=f"msg_{len(self.messages)}",
                sender="system",
                content=f"❌ 执行命令 '{command}' 时出错: {str(e)}",
                timestamp=datetime.now(),
                message_type=MessageType.TEXT
            )
            self.messages.append(error_message)
            
        finally:
            await self.refresh()
    
    async def send_to_assistant(self, message: str):
        """发送消息给Personal Assistant"""
        try:
            session_id = self.session_id or "default_session"
            
            # 显示"正在思考"状态
            thinking_message = ChatMessage(
                id=f"msg_{len(self.messages)}_thinking",
                sender="assistant",
                content="🤔 正在分析您的请求...",
                timestamp=datetime.now(),
                message_type=MessageType.TEXT
            )
            self.messages.append(thinking_message)
            await self.refresh()
            
            # 调用助手服务
            assistant_response_str = await self.assistant_service.process_message(message, session_id)
            
            # 移除"正在思考"消息
            self.messages = [msg for msg in self.messages if msg.id != thinking_message.id]
            
            # 添加实际响应
            response_message = ChatMessage(
                id=f"msg_{len(self.messages)}",
                sender="assistant",
                content=assistant_response_str,
                timestamp=datetime.now(),
                message_type=MessageType.TEXT
            )
            self.messages.append(response_message)
            
        except Exception as e:
            logger.error(f"Error sending message to assistant: {e}")
            # 移除"正在思考"消息（如果存在）
            self.messages = [msg for msg in self.messages if not msg.id.endswith("_thinking")]
            
            error_message = ChatMessage(
                id=f"msg_{len(self.messages)}",
                sender="system",
                content=f"❌ 与助手通信时出错: {str(e)}",
                timestamp=datetime.now(),
                message_type=MessageType.TEXT
            )
            self.messages.append(error_message)
            
        finally:
            await self.refresh()
    
    async def receive_message(self, message: ChatMessage):
        """接收外部消息"""
        self.messages.append(message)
        await self.refresh()
    
    def render_message(self, message: ChatMessage) -> HTML:
        """渲染单个消息"""
        sender_class = f"message-{message.sender}"
        type_class = f"message-type-{message.message_type.value}"
        
        return Div(
            Div(
                message.sender,
                _class="message-sender"
            ),
            Div(
                message.content,
                _class="message-content"
            ),
            Div(
                message.timestamp.strftime("%H:%M:%S"),
                _class="message-timestamp"
            ),
            _class=f"message {sender_class} {type_class}"
        )
    
    def render(self) -> HTML:
        """渲染聊天界面"""
        return Div(
            H3("💬 对话", _class="chat-title"),
            
            # 消息历史区域
            Div(
                *[self.render_message(msg) for msg in self.messages],
                _class="message-history"
            ),
            
            # 输入区域
            Div(
                self.message_input,
                self.send_button,
                _class="message-input-area"
            ),
            
            _class="chat-interface"
        )
