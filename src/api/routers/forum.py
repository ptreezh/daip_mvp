#!/usr/bin/env python3
"""@Time    : 2025-08-06 14:00:00
@Author  : DAIP-LIVE Team
@File    : forum_api.py
@Description:
    Forum模式API端点 - 处理会话管理、用户干预和多智能体协作的HTTP接口
"""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...core.exceptions import ForumServiceError
from ...core_services.forum_service import forum_service

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/forum", tags=["forum"])


# Pydantic模型
class ForumSessionRequest(BaseModel):
    """Forum会话请求模型"""
    topic: str = Field(..., description="讨论话题")
    user_id: str = Field(default="default_user", description="用户ID")
    settings: Optional[dict[str, Any]] = Field(default=None, description="会话设置")


class UserInterventionRequest(BaseModel):
    """用户干预请求模型"""
    session_id: str = Field(..., description="会话ID")
    message: dict[str, Any] = Field(..., description="用户消息")
    intent: str = Field(default="comment", description="干预意图")


class SessionControlRequest(BaseModel):
    """会话控制请求模型"""
    session_id: str = Field(..., description="会话ID")
    action: str = Field(..., description="控制动作: pause, resume, end")


class ForumSessionResponse(BaseModel):
    """Forum会话响应模型"""
    session_id: str
    topic: str
    status: str
    start_time: str
    active_agents: list[str]
    message_count: int
    user_intervention_count: int
    consensus_level: float
    duration: float


class UserInterventionResponse(BaseModel):
    """用户干预响应模型"""
    status: str
    optimized_input: str
    session_id: str
    timestamp: str


class SessionContextResponse(BaseModel):
    """会话上下文响应模型"""
    session_id: str
    topic: str
    status: str
    consensus_level: float
    active_agents: list[str]
    key_arguments: list[dict[str, Any]]
    message_count: int
    user_intervention_count: int
    start_time: str
    duration: float


class ForumStatisticsResponse(BaseModel):
    """Forum统计响应模型"""
    total_sessions: int
    active_sessions: int
    total_messages: int
    total_interventions: int
    average_consensus: float


@router.post("/session", response_model=ForumSessionResponse)
async def create_forum_session(request: ForumSessionRequest):
    """创建Forum会话"""
    try:
        session_id = await forum_service.start_session(request.topic, request.user_id, request.settings or {})
        return ForumSessionResponse(
            session_id=session_id,
            topic=request.topic,
            user_id=request.user_id,
            start_time=datetime.now().isoformat()
        )
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"创建Forum会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}", response_model=SessionContextResponse)
async def get_session_context(session_id: str):
    """获取会话上下文"""
    try:
        context = await forum_service.get_session_context(session_id)
        return SessionContextResponse(**context)
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取会话上下文失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/intervention", response_model=UserInterventionResponse)
async def handle_user_intervention(request: UserInterventionRequest):
    """处理用户干预"""
    try:
        result = await forum_service.handle_user_intervention(
            request.session_id, 
            request.message, 
            request.intent
        )
        return UserInterventionResponse(**result)
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"处理用户干预失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/control")
async def control_session(request: SessionControlRequest):
    """控制会话"""
    try:
        if request.action == "pause":
            await forum_service.pause_session(request.session_id)
        elif request.action == "resume":
            await forum_service.resume_session(request.session_id)
        elif request.action == "end":
            await forum_service.end_session(request.session_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {"message": f"Session {request.session_id} {request.action}d successfully"}
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"控制会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions")
async def list_sessions():
    """列出所有会话"""
    try:
        sessions = await forum_service.list_sessions()
        return sessions
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"列出会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/statistics", response_model=ForumStatisticsResponse)
async def get_forum_statistics():
    """获取Forum统计信息"""
    try:
        stats = await forum_service.get_statistics()
        return ForumStatisticsResponse(**stats)
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        await forum_service.delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully"}
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def forum_health_check():
    """Forum服务健康检查"""
    try:
        health_status = await forum_service.health_check()
        return health_status
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50):
    """获取会话消息"""
    try:
        messages = await forum_service.get_session_messages(session_id, limit)
        return messages
    except ForumServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"获取会话消息失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/session/{session_id}/optimize")
async def optimize_user_input(session_id: str, user_input: str):
    """优化用户输入"""
    try:
        # 这里应该调用一个实际的优化服务
        optimized_input = user_input  # 占位符实现
        return {"optimized_input": optimized_input}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"优化用户输入失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")





