#!/usr/bin/env python3
"""聊天界面组件 - 修复版本

基于Lona框架的正确实现，面向真正的工程可用性
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from lona.html import HTML, Button, Div, Span, TextInput
from lona.html.widget import Widget
from services.personal_assistant import PersonalAssistantService
from services.websocket_manager import MessageType, WebSocketMessage, websocket_manager

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
                 metadata: Optional[dict[str, Any]] = None):
        self.id = f"msg_{datetime.now().timestamp()}"
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.timestamp = datetime.now()
        self.metadata = metadata or {}


class ChatInterface(Widget):
    """聊天界面组件 - 工程可用版本"""
    
    def __init__(self, assistant_service: PersonalAssistantService, session_id: Optional[str] = None):
        super().__init__()
        
        self.assistant_service = assistant_service
        self.messages: list[ChatMessage] = []
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"
        self.is_processing = False
        
        # 集成演示相关属性
        self.current_scenario = None
        self.demo_active = False
        self.context_data = {}
        self.current_task = None
        
        # 回调函数（供外部组件注册）
        self.on_message_sent = None
        self.on_workflow_triggered = None
        self.on_context_updated = None
        
        # 创建UI元素
        self.message_input = TextInput(
            placeholder="输入您的消息或问题...",
            _class="message-input-field"
        )
        self.send_button = Button(
            "发送",
            _class="btn btn-primary send-button"
        )
        
        # 绑定事件
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
            content="🎭 欢迎使用 DAIP-LIVE 演示系统！\n\n我是您的智能助手，可以帮您：\n" +
                   "• 🔍 进行深度分析和批判性审查\n" +
                   "• 🎯 组织多视角讨论和辩论\n" +
                   "• 📚 管理知识库和任务\n" +
                   "• 🤖 创建自定义工作流\n\n" +
                   "请告诉我您想要分析或讨论的话题！",
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(welcome_msg)
    
    def _setup_websocket_handlers(self):
        """设置WebSocket消息处理器"""
        try:
            websocket_manager.register_chat_handler(self._handle_websocket_message)
        except Exception as e:
            logger.warning(f"WebSocket处理器注册失败: {e}")
    
    async def _handle_websocket_message(self, message: WebSocketMessage):
        """处理WebSocket消息"""
        try:
            if message.type == MessageType.AGENT_OUTPUT:
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
                # Lona会自动更新UI，无需手动refresh
                
            elif message.type == MessageType.WORKFLOW_STATUS:
                status_msg = ChatMessage(
                    sender="system",
                    content=f"🔄 工作流状态更新: {message.payload.get('status', 'unknown')}",
                    message_type=MessageType.WORKFLOW_STATUS,
                    metadata=message.payload
                )
                self.messages.append(status_msg)
                
            elif message.type == MessageType.CONSENSUS_RESULT:
                consensus_msg = ChatMessage(
                    sender="system",
                    content=f"🎯 共识结果: {message.payload.get('result', 'No consensus')}\n" +
                           f"置信度: {message.payload.get('confidence', 0):.2f}",
                    message_type=MessageType.CONSENSUS_RESULT,
                    metadata=message.payload
                )
                self.messages.append(consensus_msg)
                
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
    
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
            
            # 清空输入框
            self.message_input.value = ""
            
            # 触发外部回调（用于组件间通信）
            if self.on_message_sent:
                try:
                    await self.on_message_sent(user_message)
                except Exception as e:
                    logger.error(f"消息发送回调失败: {e}")
            
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
            
        finally:
            self.is_processing = False
            self.send_button.disabled = False
            self.message_input.disabled = False
    
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
                content=f"❌ 未知命令: {command}\n输入 `/help` 查看可用命令",
                message_type=MessageType.ERROR
            )
            self.messages.append(error_msg)
    
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
    
    # 集成演示相关方法
    async def set_demo_scenario(self, scenario_key: str, scenario_data: dict[str, Any]):
        """设置演示场景"""
        self.current_scenario = scenario_key
        self.demo_active = True
        
        scenario_msg = ChatMessage(
            sender="system",
            content=f"🎭 演示场景已启动: {scenario_data['name']}\n\n"
                   f"📝 描述: {scenario_data['description']}\n"
                   f"⏱️ 预计时长: {scenario_data['duration']}\n"
                   f"👥 参与角色: {', '.join(scenario_data['roles'])}\n"
                   f"🔄 工作流: {', '.join(scenario_data['workflows'])}\n\n"
                   f"请输入您想要分析或讨论的具体问题。",
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(scenario_msg)
    
    async def add_context(self, context_data: dict[str, Any]):
        """添加上下文信息"""
        self.context_data.update(context_data)
        
        context_msg = ChatMessage(
            sender="system",
            content=f"📚 已添加上下文信息: {context_data.get('title', '未知')}\n"
                   f"类型: {context_data.get('type', '知识')}\n"
                   f"相关性: {context_data.get('relevance', 'N/A')}",
            message_type=MessageType.SYSTEM_INFO
        )
        self.messages.append(context_msg)
        
        # 触发上下文更新回调
        if self.on_context_updated:
            try:
                await self.on_context_updated(self.context_data)
            except Exception as e:
                logger.error(f"上下文更新回调失败: {e}")
    
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
        else:
            message_class = "message"
        
        # 处理消息内容
        content_text = message.content.replace('\n', '<br>')
        
        # 添加时间戳
        timestamp = Span(
            message.timestamp.strftime("%H:%M:%S"),
            _class="message-timestamp"
        )
        
        return Div(
            Div(
                HTML(content_text),
                _class="message-content"
            ),
            timestamp,
            _class=message_class
        )
    
    def get_demo_context(self) -> dict[str, Any]:
        """获取演示上下文"""
        return {
            "session_id": self.session_id,
            "current_scenario": self.current_scenario,
            "demo_active": self.demo_active,
            "context_data": self.context_data,
            "current_task": self.current_task,
            "message_count": len(self.messages)
        }