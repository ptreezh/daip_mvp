#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 14:00:00
@Author  : DAIP-LIVE Team
@File    : forum_api.py
@Description:
    Forum模式API端点 - 处理会话管理、用户干预和多智能体协作的HTTP接口
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..app_state import app_state
from ..core.exceptions import ForumServiceError
from ..core_services.forum_service import forum_service

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
forum_router = APIRouter(prefix="/api/forum", tags=["forum"])


# Pydantic模型
class ForumSessionRequest(BaseModel):
    """Forum会话请求模型"""
    topic: str = Field(..., description="讨论话题")
    user_id: str = Field(default="default_user", description="用户ID")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="会话设置")


class UserInterventionRequest(BaseModel):
    """用户干预请求模型"""
    session_id: str = Field(..., description="会话ID")
    message: Dict[str, Any] = Field(..., description="用户消息")
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
    active_agents: List[str]
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
    active_agents: List[str]
    key_arguments: List[Dict[str, Any]]
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


@forum_router.post("/session", response_model=ForumSessionResponse)
async def create_forum_session(request: ForumSessionRequest):
    """创建Forum会话"""
    try:
        logger.info(f"创建Forum会话: {request.topic}")
        
        # 启动Forum会话
        session = await forum_service.start_forum_session(
            topic=request.topic,
            user_id=request.user_id
        )
        
        response = ForumSessionResponse(
            session_id=session.session_id,
            topic=session.topic,
            status=session.status,
            start_time=session.start_time.isoformat(),
            active_agents=session.active_agents,
            message_count=len(session.messages),
            user_intervention_count=len(session.user_interventions),
            consensus_level=session.consensus_level,
            duration=(datetime.now() - session.start_time).total_seconds()
        )
        
        logger.info(f"Forum会话创建成功: {session.session_id}")
        return response
        
    except ForumServiceError as e:
        logger.error(f"Forum服务错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建Forum会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.get("/session/{session_id}", response_model=SessionContextResponse)
async def get_session_context(session_id: str):
    """获取会话上下文"""
    try:
        context = await forum_service.get_session_context(session_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")
        
        response = SessionContextResponse(**context)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话上下文失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.post("/intervention", response_model=UserInterventionResponse)
async def handle_user_intervention(request: UserInterventionRequest):
    """处理用户干预"""
    try:
        logger.info(f"处理用户干预: {request.session_id}")
        
        result = await forum_service.handle_user_intervention(
            session_id=request.session_id,
            user_message=request.message
        )
        
        response = UserInterventionResponse(
            status=result["status"],
            optimized_input=result["optimized_input"],
            session_id=result["session_id"],
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"用户干预处理成功: {request.session_id}")
        return response
        
    except ForumServiceError as e:
        logger.error(f"Forum服务错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理用户干预失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.post("/control")
async def control_session(request: SessionControlRequest):
    """控制会话"""
    try:
        logger.info(f"控制会话: {request.session_id} - {request.action}")
        
        success = False
        
        if request.action == "pause":
            success = await forum_service.pause_session(request.session_id)
        elif request.action == "resume":
            success = await forum_service.resume_session(request.session_id)
        elif request.action == "end":
            result = await forum_service.end_session(request.session_id)
            if result:
                success = True
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "success",
            "action": request.action,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"控制会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.get("/sessions")
async def get_active_sessions():
    """获取所有活跃会话"""
    try:
        sessions = forum_service.get_active_sessions()
        return {
            "sessions": sessions,
            "count": len(sessions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取活跃会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.get("/statistics", response_model=ForumStatisticsResponse)
async def get_forum_statistics():
    """获取Forum统计信息"""
    try:
        stats = forum_service.get_session_statistics()
        return ForumStatisticsResponse(**stats)
        
    except Exception as e:
        logger.error(f"获取Forum统计失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        result = await forum_service.end_session(session_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "status": "deleted",
            "session_id": session_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.get("/health")
async def forum_health_check():
    """Forum健康检查"""
    try:
        active_sessions = forum_service.get_active_sessions()
        stats = forum_service.get_session_statistics()
        
        return {
            "status": "healthy",
            "service": "forum",
            "active_sessions": len(active_sessions),
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Forum健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "forum",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@forum_router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str):
    """获取会话消息历史"""
    try:
        # 从Forum服务获取会话消息
        context = await forum_service.get_session_context(session_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 这里应该从消息存储中获取实际的消息历史
        # 简化实现，返回基本结构
        return {
            "session_id": session_id,
            "messages": [],  # 实际实现中应该从消息存储中获取
            "message_count": context["message_count"],
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话消息失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@forum_router.post("/session/{session_id}/optimize")
async def optimize_user_input(session_id: str, input_data: Dict[str, Any]):
    """优化用户输入"""
    try:
        user_input = input_data.get("input", "")
        intent = input_data.get("intent", "comment")
        
        if not user_input:
            raise HTTPException(status_code=400, detail="Input is required")
        
        # 获取会话上下文以获取话题
        context = await forum_service.get_session_context(session_id)
        
        if not context:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # 使用Forum服务的用户干预管理器优化输入
        optimized_input = await forum_service.user_intervention_manager.optimize_input(
            user_input, intent, context["topic"]
        )
        
        return {
            "original_input": user_input,
            "optimized_input": optimized_input,
            "intent": intent,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"优化用户输入失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# 错误处理
@forum_router.exception_handler(ForumServiceError)
async def forum_service_error_handler(request, exc: ForumServiceError):
    """Forum服务错误处理器"""
    return {
        "error": "Forum service error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }


@forum_router.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """数值错误处理器"""
    return {
        "error": "Validation error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat()
    }


# 包含路由器的函数
def include_forum_router(app):
    """包含Forum路由器"""
    app.include_router(forum_router)
    logger.info("Forum API路由器已注册")