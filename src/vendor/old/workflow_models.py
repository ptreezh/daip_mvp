"""增强的工作流API模型
提供完整的参数验证和错误处理
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class WorkflowStatus(str, Enum):
    """工作流状态枚举"""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowType(str, Enum):
    """工作流类型枚举"""

    BRAINSTORM = "brainstorm"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    REPORT = "report"
    COLLABORATION = "collaboration"


class WorkflowAction(str, Enum):
    """工作流动作枚举"""

    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    ADVANCE = "advance"
    MESSAGE = "message"


class BaseWorkflowRequest(BaseModel):
    """基础工作流请求模型"""

    session_id: Optional[str] = Field(None, description="会话ID")

    @validator("session_id")
    def validate_session_id(cls, v):
        if v is not None and not v.strip():
            raise ValueError("会话ID不能为空")
        return v


class WorkflowCreateRequest(BaseWorkflowRequest):
    """创建工作流请求模型"""

    workflow_type: WorkflowType = Field(..., description="工作流类型")
    title: str = Field(..., min_length=1, max_length=200, description="工作流标题")
    description: Optional[str] = Field(None, max_length=1000, description="工作流描述")
    parameters: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="工作流参数",
    )

    @validator("title")
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("标题不能为空")
        return v.strip()


class WorkflowExecuteRequest(BaseWorkflowRequest):
    """执行工作流请求模型"""

    session_id: str = Field(..., description="会话ID")
    action: WorkflowAction = Field(..., description="执行动作")
    message: Optional[str] = Field(None, max_length=5000, description="消息内容")
    parameters: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="执行参数",
    )

    @validator("message")
    def validate_message(cls, v):
        if v is not None and not v.strip():
            return None
        return v


class WorkflowMessageRequest(BaseWorkflowRequest):
    """发送工作流消息请求模型"""

    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    role: Optional[str] = Field(None, max_length=100, description="角色")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")

    @validator("message")
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("消息内容不能为空")
        return v.strip()


class WorkflowAdvanceRequest(BaseWorkflowRequest):
    """推进工作流阶段请求模型"""

    session_id: str = Field(..., description="会话ID")
    target_stage: Optional[str] = Field(None, max_length=100, description="目标阶段")
    parameters: Optional[dict[str, Any]] = Field(
        default_factory=dict,
        description="推进参数",
    )


class WorkflowResponse(BaseModel):
    """工作流响应模型"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict[str, Any]] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


def create_workflow_response(
    success: bool,
    message: str,
    data: Optional[dict[str, Any]] = None,
    error_code: Optional[str] = None,
) -> WorkflowResponse:
    """创建工作流响应"""
    return WorkflowResponse(
        success=success,
        message=message,
        data=data,
        error_code=error_code,
    )
