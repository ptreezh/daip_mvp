"""统一消息模型定义
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """统一聊天消息模型"""

    role_name: str = Field(..., description="角色姓名")
    content: str = Field(..., min_length=1, description="消息内容")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


class MultiRoleChatRequest(BaseModel):
    """多角色聊天请求模型"""

    topic: str = Field(..., description="聊天主题")
    roles: list[str] = Field(..., description="参与角色列表")
    messages: list[ChatMessage] = Field(..., description="消息列表")


class MultiRoleChatResponse(BaseModel):
    """多角色聊天响应模型"""

    new_message: ChatMessage = Field(..., description="新生成的消息")
