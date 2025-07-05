"""统一消息模型定义
"""

from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class UnifiedMessageRequest(BaseModel):
    """统一消息发送请求模型"""

    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")

    @validator("content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("消息内容不能为空")
        return v.strip()
