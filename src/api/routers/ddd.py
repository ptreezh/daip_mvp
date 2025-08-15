"""@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : ddd.py
@Description:
    DDD-based API endpoints for the Personal Intelligence Hub.
    These endpoints implement the CQRS pattern with proper separation of concerns.
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

from ...application.commands import (
    CommandDispatcher,
)
from ...application.queries import (
    QueryDispatcher,
)
from ...application.use_cases import UseCaseFactory
from ...domain.domain_services import (
    ConsensusTrackingService,
    EntranceSelectorService,
    UserInterventionService,
    WorkflowOrchestratorService,
)
from ...domain.value_objects import (
    EntranceType,
    IntentType,
    MessageIntent,
    SessionStatus,
    TaskPriority,
    TaskStatus,
)
from ...infrastructure.database import get_database_manager
from ...infrastructure.redis_client import get_redis_manager


# Pydantic models for API requests/responses
class UserCreateRequest(BaseModel):
    """用户创建请求"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    preferred_entrance: str = Field(..., description="首选入口类型")
    preferences: dict[str, Any] = Field(default_factory=dict, description="用户偏好")


class SessionCreateRequest(BaseModel):
    """会话创建请求"""
    user_id: str = Field(..., description="用户ID")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class TaskCreateRequest(BaseModel):
    """任务创建请求"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="任务内容")
    intent_type: str = Field(..., description="意图类型")
    priority: str = Field(default="normal", description="任务优先级")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class MessageProcessRequest(BaseModel):
    """消息处理请求"""
    session_id: str = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    sender: str = Field(..., description="发送者")
    message_intent: str = Field(default="comment", description="消息意图")
    context: dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class DebateStartRequest(BaseModel):
    """辩论开始请求"""
    session_id: str = Field(..., description="会话ID")
    topic: str = Field(..., description="辩论主题")
    participants: list[str] = Field(..., description="参与者列表")


class UserResponse(BaseModel):
    """用户响应"""
    user_id: str
    username: str
    email: str
    preferred_entrance: str
    is_active: bool
    preferences: dict[str, Any]
    created_at: str
    updated_at: str


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    user_id: str
    entrance_type: str
    status: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    session_id: str
    content: str
    intent_type: str
    status: str
    priority: str
    result: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    metadata: dict[str, Any]


class MessageResponse(BaseModel):
    """消息响应"""
    message_id: str
    session_id: str
    content: str
    sender: str
    timestamp: str
    type: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    agent_role: Optional[str] = None


class DebateResponse(BaseModel):
    """辩论响应"""
    debate_id: str
    session_id: str
    topic: str
    participants: list[str]
    status: str
    created_at: str
    consensus_level: float


class SystemStatusResponse(BaseModel):
    """系统状态响应"""
    timestamp: str
    overall_status: str
    services: dict[str, Any]
    statistics: dict[str, Any]


# 全局依赖注入
_command_dispatcher: Optional[CommandDispatcher] = None
_query_dispatcher: Optional[QueryDispatcher] = None
_use_case_factory: Optional[UseCaseFactory] = None


async def get_command_dispatcher() -> CommandDispatcher:
    """获取命令分发器"""
    global _command_dispatcher
    
    if _command_dispatcher is None:
        # 初始化依赖
        db_manager = await get_database_manager()
        redis_client = await get_redis_manager()
        
        # 初始化领域服务
        entrance_selector = EntranceSelectorService()
        workflow_orchestrator = WorkflowOrchestratorService()
        user_intervention = UserInterventionService()
        consensus_tracker = ConsensusTrackingService()
        
        # 初始化用例工厂
        use_case_factory = UseCaseFactory(
            db_manager=db_manager,
            redis_client=redis_client,
            entrance_selector=entrance_selector,
            workflow_orchestrator=workflow_orchestrator,
            user_intervention=user_intervention,
            consensus_tracker=consensus_tracker
        )
        
        # 初始化命令分发器
        _command_dispatcher = CommandDispatcher(
            command_bus=CommandDispatcher.CommandBus(),
            use_case_factory=use_case_factory
        )
    
    return _command_dispatcher


async def get_query_dispatcher() -> QueryDispatcher:
    """获取查询分发器"""
    global _query_dispatcher
    
    if _query_dispatcher is None:
        # 初始化依赖
        db_manager = await get_database_manager()
        redis_client = await get_redis_manager()
        
        # 初始化查询分发器
        _query_dispatcher = QueryDispatcher(
            query_bus=QueryDispatcher.QueryBus(),
            db_manager=db_manager,
            redis_client=redis_client
        )
    
    return _query_dispatcher


# 创建路由器
router = APIRouter(prefix="/api/v1/ddd", tags=["DDD"])


# 用户相关端点
@router.post("/users", response_model=dict[str, Any])
async def create_user(
    request: UserCreateRequest,
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """创建用户"""
    try:
        result = await command_dispatcher.create_user(
            user_id=request.user_id,
            username=request.username,
            email=request.email,
            preferred_entrance=EntranceType(request.preferred_entrance),
            preferences=request.preferences
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str = Path(..., description="用户ID"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取用户信息"""
    try:
        result = await query_dispatcher.get_user(user_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 会话相关端点
@router.post("/sessions", response_model=dict[str, Any])
async def create_session(
    request: SessionCreateRequest,
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """创建会话"""
    try:
        result = await command_dispatcher.create_session(
            user_id=request.user_id,
            context=request.context
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str = Path(..., description="会话ID"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取会话信息"""
    try:
        result = await query_dispatcher.get_session(session_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/sessions", response_model=list[SessionResponse])
async def get_user_sessions(
    user_id: str = Path(..., description="用户ID"),
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取用户的会话列表"""
    try:
        result = await query_dispatcher.get_user_sessions(user_id, limit, offset)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data.get("sessions", [])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 任务相关端点
@router.post("/tasks", response_model=dict[str, Any])
async def create_task(
    request: TaskCreateRequest,
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """创建任务"""
    try:
        result = await command_dispatcher.create_task(
            session_id=request.session_id,
            content=request.content,
            intent_type=IntentType(request.intent_type),
            priority=TaskPriority(request.priority),
            context=request.context
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str = Path(..., description="任务ID"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取任务信息"""
    try:
        result = await query_dispatcher.get_task(task_id)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/tasks", response_model=list[TaskResponse])
async def get_session_tasks(
    session_id: str = Path(..., description="会话ID"),
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取会话的任务列表"""
    try:
        result = await query_dispatcher.get_session_tasks(session_id, limit, offset)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data.get("tasks", [])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/execute", response_model=dict[str, Any])
async def execute_task(
    task_id: str = Path(..., description="任务ID"),
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """执行任务"""
    try:
        result = await command_dispatcher.execute_task(task_id)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 消息相关端点
@router.post("/messages", response_model=dict[str, Any])
async def process_message(
    request: MessageProcessRequest,
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """处理消息"""
    try:
        result = await command_dispatcher.process_message(
            session_id=request.session_id,
            content=request.content,
            sender=request.sender,
            message_intent=MessageIntent(request.message_intent),
            context=request.context
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_session_messages(
    session_id: str = Path(..., description="会话ID"),
    limit: int = Query(50, ge=1, le=100, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取会话的消息列表"""
    try:
        result = await query_dispatcher.get_session_messages(session_id, limit, offset)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data.get("messages", [])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 辩论相关端点
@router.post("/debates", response_model=dict[str, Any])
async def start_debate(
    request: DebateStartRequest,
    command_dispatcher: CommandDispatcher = Depends(get_command_dispatcher)
):
    """开始辩论"""
    try:
        result = await command_dispatcher.start_debate(
            session_id=request.session_id,
            topic=request.topic,
            participants=request.participants
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 系统相关端点
@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取系统状态"""
    try:
        result = await query_dispatcher.get_system_status()
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return result.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 健康检查端点
@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "DDD API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# 统计信息端点
@router.get("/statistics")
async def get_statistics(
    query_dispatcher: QueryDispatcher = Depends(get_query_dispatcher)
):
    """获取统计信息"""
    try:
        result = await query_dispatcher.get_system_status()
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)
        
        return {
            "statistics": result.data.get("statistics", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 配置信息端点
@router.get("/config")
async def get_config():
    """获取配置信息"""
    return {
        "supported_entrance_types": [e.value for e in EntranceType],
        "supported_intent_types": [i.value for i in IntentType],
        "supported_task_statuses": [s.value for s in TaskStatus],
        "supported_session_statuses": [s.value for s in SessionStatus],
        "supported_message_intents": [i.value for i in MessageIntent],
        "supported_task_priorities": ["low", "normal", "high", "urgent"],
        "api_version": "1.0.0",
        "ddd_enabled": True,
        "cqr_enabled": True,
        "event_sourcing_enabled": False,
        "caching_enabled": True
    }