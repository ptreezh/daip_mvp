"""Personal Intelligence Hub - Chat Models

聊天相关的数据模型
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"
    WORKFLOW_STATUS = "workflow_status"
    AGENT_OUTPUT = "agent_output"
    CONSENSUS_RESULT = "consensus_result"
    SYSTEM_NOTIFICATION = "system_notification"


@dataclass
class ChatMessage:
    """聊天消息数据模型"""
    id: str
    sender: str  # 'user' | 'assistant' | 'system' | 角色ID
    content: str
    timestamp: datetime
    message_type: MessageType = MessageType.TEXT
    metadata: Optional[dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversationContext:
    """对话上下文数据模型"""
    user_id: str
    session_id: str
    message_history: list  # List[ChatMessage]
    current_workflow: Optional[str] = None
    active_agents: list = None  # List[str]
    
    def __post_init__(self):
        if self.active_agents is None:
            self.active_agents = []