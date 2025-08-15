"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : models.py
@Description:
    Request and response models for FastAPI endpoints.
    Defines the API contract with proper validation and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class EntranceType(str, Enum):
    """入口类型枚举"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"


class IntentType(str, Enum):
    """意图类型枚举"""
    ANALYSIS = "analysis"
    DISCUSSION = "discussion"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"
    COMMENT = "comment"
    EVALUATION = "evaluation"
    SUMMARIZATION = "summarization"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionStatus(str, Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"


class MessageIntent(str, Enum):
    """消息意图枚举"""
    COMMENT = "comment"
    QUESTION = "question"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"


# 用户相关模型
class UserPreference(BaseModel):
    """用户偏好"""
    preferred_entrance: EntranceType = Field(..., description="首选入口类型")
    language: str = Field("zh-CN", description="语言偏好")
    theme: str = Field("light", description="主题偏好")
    notification_enabled: bool = Field(True, description="是否启用通知")
    auto_transparency: bool = Field(False, description="是否自动透明度")
    detail_level: str = Field("comprehensive", description="详细程度")


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$', description="邮箱地址")
    preferred_entrance: EntranceType = Field(..., description="首选入口类型")
    preferences: UserPreference = Field(..., description="用户偏好")


class UserResponse(BaseModel):
    """用户响应"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    preferred_entrance: EntranceType = Field(..., description="首选入口类型")
    preferences: UserPreference = Field(..., description="用户偏好")
    is_active: bool = Field(..., description="是否活跃")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


# 会话相关模型
class SessionCreate(BaseModel):
    """创建会话请求"""
    user_id: str = Field(..., description="用户ID")
    entrance_type: EntranceType = Field(..., description="入口类型")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str = Field(..., description="会话ID")
    user_id: str = Field(..., description="用户ID")
    entrance_type: EntranceType = Field(..., description="入口类型")
    status: SessionStatus = Field(..., description="会话状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    duration: float = Field(..., description="持续时间（秒）")
    task_count: int = Field(..., description="任务数量")
    message_count: int = Field(..., description="消息数量")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


# 任务相关模型
class TaskPriority(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    """创建任务请求"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., min_length=1, description="任务内容")
    intent_type: IntentType = Field(..., description="意图类型")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str = Field(..., description="任务ID")
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="任务内容")
    intent_type: IntentType = Field(..., description="意图类型")
    status: TaskStatus = Field(..., description="任务状态")
    priority: TaskPriority = Field(..., description="任务优先级")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    result: Optional[str] = Field(None, description="任务结果")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


# 消息相关模型
class MessageCreate(BaseModel):
    """创建消息请求"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., min_length=1, description="消息内容")
    intent: MessageIntent = Field(MessageIntent.COMMENT, description="消息意图")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class MessageResponse(BaseModel):
    """消息响应"""
    message_id: str = Field(..., description="消息ID")
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    sender: str = Field(..., description="发送者")
    timestamp: datetime = Field(..., description="时间戳")
    intent: Optional[MessageIntent] = Field(None, description="消息意图")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="置信度")
    agent_role: Optional[str] = Field(None, description="Agent角色")
    message_type: str = Field(..., description="消息类型")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


# 入口选择相关模型
class EntranceSuggestionResponse(BaseModel):
    """入口建议响应"""
    recommended_entrance: EntranceType = Field(..., description="推荐的入口类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    reasoning: list[str] = Field(..., description="推理过程")
    alternative_options: list[dict[str, Any]] = Field(..., description="备选方案")
    context_features: dict[str, Any] = Field(..., description="上下文特征")


# 透明度相关模型
class AgentActivity(BaseModel):
    """Agent活动"""
    agent: str = Field(..., description="Agent名称")
    activity: str = Field(..., description="活动描述")
    duration: float = Field(..., description="持续时间（秒）")
    contribution: str = Field(..., description="贡献描述")


class ResourceUsage(BaseModel):
    """资源使用情况"""
    memory_mb: float = Field(..., ge=0.0, description="内存使用（MB）")
    cpu_percent: float = Field(..., ge=0.0, le=100.0, description="CPU使用率（%）")
    network_mb: float = Field(..., ge=0.0, description="网络使用（MB）")
    tokens_used: int = Field(..., ge=0, description="使用的Token数量")


class TransparencyResponse(BaseModel):
    """透明度响应"""
    session_id: str = Field(..., description="会话ID")
    entrance_type: EntranceType = Field(..., description="入口类型")
    timestamp: datetime = Field(..., description="时间戳")
    system_metrics: dict[str, Any] = Field(..., description="系统指标")
    tasks: list[dict[str, Any]] = Field(..., description="任务信息")
    agent_activities: list[AgentActivity] = Field(..., description="Agent活动")
    resource_usage: ResourceUsage = Field(..., description="资源使用情况")


# 健康检查相关模型
class ServiceHealth(BaseModel):
    """服务健康状态"""
    name: str = Field(..., description="服务名称")
    status: str = Field(..., description="状态")
    is_healthy: bool = Field(..., description="是否健康")
    message: Optional[str] = Field(None, description="状态消息")
    last_check: datetime = Field(..., description="最后检查时间")


class HealthResponse(BaseModel):
    """健康检查响应"""
    overall_status: str = Field(..., description="整体状态")
    services: dict[str, ServiceHealth] = Field(..., description="服务状态")
    uptime: float = Field(..., description="运行时间（秒）")
    version: str = Field(..., description="版本")
    last_check: datetime = Field(..., description="最后检查时间")


# WebSocket相关模型
class WebSocketMessage(BaseModel):
    """WebSocket消息"""
    type: str = Field(..., description="消息类型")
    data: dict[str, Any] = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class WebSocketConnection(BaseModel):
    """WebSocket连接"""
    connection_id: str = Field(..., description="连接ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    entrance_type: Optional[EntranceType] = Field(None, description="入口类型")
    is_authenticated: bool = Field(..., description="是否已认证")
    connected_at: datetime = Field(..., description="连接时间")
    last_activity: datetime = Field(..., description="最后活动时间")


# 错误响应模型
class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


# 通用响应模型
class SuccessResponse(BaseModel):
    """成功响应"""
    message: str = Field(..., description="响应消息")
    data: Optional[dict[str, Any]] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: list[Any] = Field(..., description="数据项")
    total: int = Field(..., description="总数")
    page: int = Field(..., ge=1, description="当前页")
    size: int = Field(..., ge=1, description="每页大小")
    pages: int = Field(..., ge=1, description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


# 统计相关模型
class UserStatistics(BaseModel):
    """用户统计"""
    user_id: str = Field(..., description="用户ID")
    total_sessions: int = Field(..., ge=0, description="总会话数")
    active_sessions: int = Field(..., ge=0, description="活跃会话数")
    completed_sessions: int = Field(..., ge=0, description="已完成会话数")
    total_tasks: int = Field(..., ge=0, description="总任务数")
    completed_tasks: int = Field(..., ge=0, description="已完成任务数")
    task_completion_rate: float = Field(..., ge=0.0, le=1.0, description="任务完成率")
    average_session_duration: float = Field(..., ge=0.0, description="平均会话持续时间（秒）")
    entrance_distribution: dict[str, int] = Field(..., description="入口分布")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")


class SystemStatistics(BaseModel):
    """系统统计"""
    total_users: int = Field(..., ge=0, description="总用户数")
    total_sessions: int = Field(..., ge=0, description="总会话数")
    total_tasks: int = Field(..., ge=0, description="总任务数")
    total_messages: int = Field(..., ge=0, description="总消息数")
    active_sessions: int = Field(..., ge=0, description="活跃会话数")
    running_tasks: int = Field(..., ge=0, description="运行中任务数")
    uptime: float = Field(..., ge=0.0, description="运行时间（秒）")
    entrance_distribution: dict[str, int] = Field(..., description="入口分布")
    task_status_distribution: dict[str, int] = Field(..., description="任务状态分布")


# 配置相关模型
class SystemConfig(BaseModel):
    """系统配置"""
    database_url: str = Field(..., description="数据库URL")
    redis_url: str = Field(..., description="Redis URL")
    vector_store_config: dict[str, Any] = Field(..., description="向量存储配置")
    ollama_config: dict[str, Any] = Field(..., description="Ollama配置")
    session_config: dict[str, Any] = Field(..., description="会话配置")
    task_config: dict[str, Any] = Field(..., description="任务配置")
    websocket_config: dict[str, Any] = Field(..., description="WebSocket配置")


# 验证器
@validator('content')
def validate_content_not_empty(cls, v):
    """验证内容不为空"""
    if not v.strip():
        raise ValueError("Content cannot be empty")
    return v.strip()


@validator('email')
def validate_email_format(cls, v):
    """验证邮箱格式"""
    if '@' not in v:
        raise ValueError("Invalid email format")
    return v


@validator('priority')
def validate_priority_range(cls, v):
    """验证优先级范围"""
    if v not in ["low", "normal", "high", "urgent"]:
        raise ValueError("Priority must be one of: low, normal, high, urgent")
    return v


# 响应模型别名
UserListResponse = PaginatedResponse
SessionListResponse = PaginatedResponse
TaskListResponse = PaginatedResponse
MessageListResponse = PaginatedResponse