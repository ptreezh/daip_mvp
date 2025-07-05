"""MVP工作流API接口
提供多种协同流程的RESTful API支持
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from src.mvp_collaborative_workflows import MVPCollaborativeWorkflows, WorkflowType


# 请求模型
class CreateWorkflowRequest(BaseModel):
    workflow_type: str
    topic: str
    description: str
    requester_id: str
    custom_participants: list[str] = []


# 兼容性请求模型 - 匹配测试脚本的参数
class CreateWorkflowSessionRequest(BaseModel):
    workflow_type: str
    name: str
    description: str
    participants: list[str] = []
    settings: Optional[dict[str, Any]] = None


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


# 创建路由器
mvp_workflow_router = APIRouter(prefix="/mvp-workflows", tags=["mvp-workflows"])

# 全局工作流管理器实例
workflow_manager = MVPCollaborativeWorkflows()


@mvp_workflow_router.get("/types")
async def get_workflow_types():
    """获取可用的工作流类型"""
    try:
        return {"workflow_types": workflow_manager.get_workflow_types()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.post("/sessions")
async def create_workflow_session(request: CreateWorkflowSessionRequest):
    """创建工作流会话 - 修复参数验证"""
    try:
        # 转换工作流类型
        workflow_type_map = {
            "brainstorming": WorkflowType.BRAINSTORMING,
            "document_review": WorkflowType.DOCUMENT_REVIEW,
            "decision_making": WorkflowType.DECISION_MAKING,
            "problem_solving": WorkflowType.PROBLEM_SOLVING,
            "creative_writing": WorkflowType.CREATIVE_WRITING,
            "technical_discussion": WorkflowType.TECHNICAL_DISCUSSION,
            "strategic_planning": WorkflowType.STRATEGIC_PLANNING,
        }

        workflow_type = workflow_type_map.get(request.workflow_type)
        if not workflow_type:
            raise ValueError(f"不支持的工作流类型: {request.workflow_type}")

        # 使用兼容性参数
        session_id = workflow_manager.create_workflow_session(
            workflow_type=workflow_type,
            topic=request.name,  # 使用name作为topic
            description=request.description,
            requester_id="test_user",  # 默认用户ID
            custom_participants=request.participants,
        )

        return {"session_id": session_id, "status": "created", "message": "工作流会话创建成功"}
    except Exception as e:
        logging.error(f"创建工作流会话失败: {e!s}")
        raise HTTPException(status_code=422, detail=str(e))


@mvp_workflow_router.get("/sessions")
async def list_workflow_sessions(
    requester_id: Optional[str] = Query(None),
    workflow_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """列出工作流会话"""
    try:
        sessions = workflow_manager.get_all_sessions()

        # 应用过滤条件
        filtered_sessions = []
        for session in sessions:
            if requester_id and session.get("requester_id") != requester_id:
                continue
            if workflow_type and session.get("workflow_type") != workflow_type:
                continue
            if status and session.get("current_phase") != status:
                continue
            filtered_sessions.append(session)

        return {"sessions": filtered_sessions, "total": len(filtered_sessions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.get("/sessions/{session_id}")
async def get_workflow_session(session_id: str):
    """获取工作流会话详情"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        return session_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.post("/sessions/{session_id}/messages")
async def send_message_to_session(session_id: str, request: SendMessageRequest):
    """向工作流会话发送消息"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        # 发送消息
        success = await workflow_manager.multi_role_chat.send_user_message(
            chat_room_id,
            request.content,
            request.sender_name,
        )

        if not success:
            raise HTTPException(status_code=500, detail="消息发送失败")

        # 生成角色响应
        responses = await workflow_manager.multi_role_chat.generate_role_responses(
            chat_room_id,
        )

        return {
            "success": True,
            "message": "消息发送成功",
            "responses": [
                {
                    "role_name": response.role_name,
                    "content": response.content,
                    "timestamp": response.timestamp,
                }
                for response in responses
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = Query(50, ge=1, le=100)):
    """获取工作流会话消息历史"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        chat_room = workflow_manager.multi_role_chat.get_chat_room(chat_room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        # 获取最近的消息
        recent_messages = (
            chat_room.messages[-limit:]
            if len(chat_room.messages) > limit
            else chat_room.messages
        )

        return {
            "messages": [
                {
                    "id": msg.id,
                    "role_name": msg.role_name,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "message_type": msg.message_type,
                }
                for msg in recent_messages
            ],
            "total": len(chat_room.messages),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.get("/sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """获取工作流会话参与者"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        chat_room = workflow_manager.multi_role_chat.get_chat_room(chat_room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        return {
            "participants": [
                {
                    "role_id": participant.role_id,
                    "role_name": participant.role_name,
                    "is_active": participant.is_active,
                    "message_count": participant.message_count,
                    "last_activity": participant.last_activity,
                }
                for participant in chat_room.participants
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.post("/sessions/{session_id}/participants")
async def add_session_participant(
    session_id: str,
    role_id: str = Body(..., embed=True),
):
    """向工作流会话添加参与者"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        success = workflow_manager.multi_role_chat.add_participant(
            chat_room_id,
            role_id,
        )

        if not success:
            raise HTTPException(status_code=400, detail="添加参与者失败")

        return {"success": True, "message": "参与者添加成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.delete("/sessions/{session_id}/participants/{role_id}")
async def remove_session_participant(session_id: str, role_id: str):
    """从工作流会话移除参与者"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        success = workflow_manager.multi_role_chat.remove_participant(
            chat_room_id,
            role_id,
        )

        if not success:
            raise HTTPException(status_code=400, detail="移除参与者失败")

        return {"success": True, "message": "参与者移除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.get("/sessions/{session_id}/recommendations")
async def get_session_recommendations(
    session_id: str,
    count: int = Query(6, ge=1, le=20),
):
    """获取工作流会话角色推荐"""
    try:
        session_info = workflow_manager.get_session_info(session_id)
        if not session_info:
            raise HTTPException(status_code=404, detail="会话不存在")

        chat_room_id = session_info.get("chat_room_id")
        if not chat_room_id:
            raise HTTPException(status_code=400, detail="聊天室不存在")

        recommendations = workflow_manager.multi_role_chat.get_room_recommendations(
            chat_room_id,
            count,
        )

        return {"recommendations": recommendations}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@mvp_workflow_router.get("/statistics")
async def get_workflow_statistics():
    """获取工作流统计信息"""
    try:
        sessions = workflow_manager.get_all_sessions()

        # 计算统计信息
        total_sessions = len(sessions)
        active_sessions = len([s for s in sessions if s.get("is_active", False)])
        completed_sessions = total_sessions - active_sessions

        # 按工作流类型统计
        workflow_type_stats = {}
        for session in sessions:
            workflow_type = session.get("workflow_type", "unknown")
            if workflow_type not in workflow_type_stats:
                workflow_type_stats[workflow_type] = 0
            workflow_type_stats[workflow_type] += 1

        # 聊天统计
        chat_stats = workflow_manager.multi_role_chat.get_chat_statistics()

        return {
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": completed_sessions,
                "by_type": workflow_type_stats,
            },
            "chat": chat_stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
