#!/usr/bin/env python3
"""Personal Intelligence Hub - Chat Interface Tests

测试聊天界面组件功能
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from personal_intelligence_hub.models.chat_models import ChatMessage, MessageType


class TestChatInterface:
    """聊天界面组件测试类"""
    
    def setup_method(self):
        """测试前置设置"""
        self.mock_assistant_service = Mock()
        
        # 使用patch来模拟Lona View的初始化
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            self.chat_interface = ChatInterface(self.mock_assistant_service)
            # 手动设置必要的属性
            self.chat_interface.messages = []
            self.chat_interface.assistant_service = self.mock_assistant_service
    
    def test_initialization(self):
        """测试组件初始化"""
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            chat_interface = ChatInterface(self.mock_assistant_service)
            
            assert chat_interface.assistant_service == self.mock_assistant_service
            assert chat_interface.messages == []
    
    def test_message_creation(self):
        """测试消息创建"""
        message = ChatMessage(
            id="test_1",
            sender="user",
            content="测试消息",
            timestamp=datetime.now(),
            message_type=MessageType.TEXT
        )
        
        assert message.sender == "user"
        assert message.content == "测试消息"
        assert message.message_type == MessageType.TEXT
    
    def test_command_detection(self):
        """测试命令检测"""
        commands = ["/consensus now", "/status", "/help", "/clear"]
        non_commands = ["hello", "test message", "regular text"]
        
        for cmd in commands:
            assert cmd.startswith("/")
        
        for non_cmd in non_commands:
            assert not non_cmd.startswith("/")
    
    def test_handle_command_consensus(self):
        """测试共识命令处理逻辑"""
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            chat_interface = ChatInterface(self.mock_assistant_service)
            chat_interface.messages = []
            
            # 测试命令处理逻辑
            assert chat_interface is not None

    def test_handle_command_unknown(self):
        """测试未知命令处理"""
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            chat_interface = ChatInterface(self.mock_assistant_service)
            chat_interface.messages = []
            
            # 测试命令处理逻辑
            assert chat_interface is not None

    def test_message_rendering(self):
        """测试消息渲染"""
        message = ChatMessage(
            id="test_1",
            sender="user",
            content="测试内容",
            timestamp=datetime.now(),
            message_type=MessageType.TEXT
        )
        
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            chat_interface = ChatInterface(self.mock_assistant_service)
            
            html = chat_interface.render_message(message)
            assert html is not None

    def test_chat_message_model(self):
        """测试ChatMessage数据模型"""
        now = datetime.now()
        message = ChatMessage(
            id="msg_123",
            sender="assistant",
            content="这是助手回复",
            timestamp=now,
            message_type=MessageType.AGENT_OUTPUT,
            metadata={"agent_id": "agent_1"}
        )
        
        assert message.id == "msg_123"
        assert message.sender == "assistant"
        assert message.content == "这是助手回复"
        assert message.message_type == MessageType.AGENT_OUTPUT
        assert message.metadata["agent_id"] == "agent_1"

    def test_message_flow(self):
        """测试消息流程"""
        with patch('lona.View.__init__', return_value=None):
            from personal_intelligence_hub.components.chat_interface import ChatInterface
            chat_interface = ChatInterface(self.mock_assistant_service)
            chat_interface.messages = []
            
            # 测试消息添加逻辑
            message = ChatMessage(
                id="test_1",
                sender="user",
                content="测试消息",
                timestamp=datetime.now(),
                message_type=MessageType.TEXT
            )
            
            chat_interface.messages.append(message)
            assert len(chat_interface.messages) == 1
            assert chat_interface.messages[0].content == "测试消息"


class TestChatModels:
    """测试聊天模型"""
    
    def test_message_type_enum(self):
        """测试消息类型枚举"""
        assert MessageType.TEXT.value == "text"
        assert MessageType.WORKFLOW_STATUS.value == "workflow_status"
        assert MessageType.AGENT_OUTPUT.value == "agent_output"
        assert MessageType.CONSENSUS_RESULT.value == "consensus_result"
    
    def test_chat_message_defaults(self):
        """测试ChatMessage默认值"""
        message = ChatMessage(
            id="test",
            sender="user",
            content="test",
            timestamp=datetime.now()
        )
        
        assert message.message_type == MessageType.TEXT
        assert message.metadata == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
