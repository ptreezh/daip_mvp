"""多角色协作聊天室API接口
提供RESTful API支持多角色协作聊天室功能
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.expert_library import ExpertLibrary
from src.multi_role_chat import MultiRoleChatEngine


# 请求模型
class CreateChatRoomRequest(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=100, description="聊天室名称")
    participants: list[str] = Field(default_factory=list, description="参与者列表")
    initial_message: str = Field(default="", max_length=1000, description="初始消息")


class SendMessageRequest(BaseModel):
    room_id: str = Field(..., description="聊天室ID")
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


class AddParticipantRequest(BaseModel):
    room_id: str
    role_id: str


# 创建路由器
multi_chat_router = APIRouter(prefix="/multi_chat", tags=["multi_chat"])

# 全局实例
multi_role_chat = MultiRoleChatEngine(ExpertLibrary())


@multi_chat_router.post("/create_room")
async def create_chat_room(request: CreateChatRoomRequest):
    """创建多角色协作聊天室"""
    try:
        room_id = multi_role_chat.create_chat_room(
            room_name=request.room_name,
            topic=request.initial_message,
            initial_participants=request.participants,
        )
        return {"success": True, "room_id": room_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.get("/room/{room_id}")
async def get_chat_room_info(room_id: str):
    """获取聊天室信息"""
    try:
        chat_room = multi_role_chat.get_chat_room(room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_info = {
            "room_id": chat_room.room_id,
            "room_name": chat_room.room_name,
            "topic": chat_room.topic,
            "participants": [
                {
                    "role_id": p.role_id,
                    "role_name": p.role_name,
                    "is_active": p.is_active,
                    "message_count": p.message_count,
                }
                for p in chat_room.participants
            ],
            "created_at": chat_room.created_at,
            "last_activity": chat_room.last_activity,
            "is_active": chat_room.is_active,
        }
        return {"success": True, "room": room_info}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.get("/rooms")
async def get_all_chat_rooms():
    """获取所有聊天室"""
    try:
        rooms = multi_role_chat.get_all_rooms()
        room_list = []
        for room in rooms:
            room_info = {
                "room_id": room.room_id,
                "room_name": room.room_name,
                "topic": room.topic,
                "participants_count": len(room.participants),
                "messages_count": len(room.messages),
                "created_at": room.created_at,
                "last_activity": room.last_activity,
                "is_active": room.is_active,
            }
            room_list.append(room_info)

        return {"success": True, "rooms": room_list, "total_rooms": len(room_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.post("/send_message")
async def send_message(request: SendMessageRequest):
    """发送消息到聊天室"""
    try:
        success = await multi_role_chat.send_user_message(
            request.room_id,
            request.content,
            request.sender_name,
        )
        if not success:
            raise HTTPException(status_code=400, detail="消息发送失败")
        return {"success": True, "message": "消息发送成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.get("/room/{room_id}/messages")
async def get_chat_room_messages(room_id: str):
    """获取聊天室消息"""
    try:
        chat_room = multi_role_chat.get_chat_room(room_id)
        if not chat_room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        messages = [
            {
                "id": msg.id,
                "role_id": msg.role_id,
                "role_name": msg.role_name,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "message_type": msg.message_type,
            }
            for msg in chat_room.messages
        ]
        return {"success": True, "messages": messages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.post("/add_participant")
async def add_participant(request: AddParticipantRequest):
    """添加参与者到聊天室"""
    try:
        success = multi_role_chat.add_participant(request.room_id, request.role_id)
        if not success:
            raise HTTPException(status_code=400, detail="添加参与者失败")
        return {"success": True, "message": "参与者添加成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.delete("/remove_participant")
async def remove_participant(room_id: str = Query(...), role_id: str = Query(...)):
    """从聊天室移除参与者"""
    try:
        success = multi_role_chat.remove_participant(room_id, role_id)
        if not success:
            raise HTTPException(status_code=400, detail="移除参与者失败")
        return {"success": True, "message": "参与者移除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.delete("/room/{room_id}")
async def delete_chat_room(room_id: str):
    """删除聊天室"""
    try:
        success = multi_role_chat.delete_chat_room(room_id)
        if not success:
            raise HTTPException(status_code=404, detail="聊天室不存在")
        return {"success": True, "message": "聊天室删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@multi_chat_router.get("/models")
async def get_available_models():
    """获取可用模型"""
    try:
        # 返回默认的模型配置
        models = ["llama3.1:8b", "qweb3:4b", "gemma2:9b"]
        return {
            "success": True,
            "models": models,
            "default_model": models[0] if models else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
