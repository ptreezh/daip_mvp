"""智能聊天室API接口
提供RESTful API支持多角色聊天功能
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# 请求模型
class CreateSessionRequest(BaseModel):
    user_id: str
    session_name: Optional[str] = None
    participants: Optional[list[str]] = None


class CreateChatRoomRequest(BaseModel):
    room_name: str = Field(..., min_length=1, max_length=100, description="聊天室名称")
    topic: str = Field(..., min_length=1, max_length=200, description="聊天主题")
    participants: list[str] = Field(default_factory=list, description="参与者列表")


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


# 响应模型
class ChatroomResponse(BaseModel):
    success: bool
    room_id: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None


# 创建路由器
chatroom_router = APIRouter(prefix="/chatroom", tags=["chatroom"])

# 模拟聊天室存储
chatrooms = {}
messages = {}


@chatroom_router.post("/create_session")
async def create_session(request: CreateSessionRequest):
    """创建新的智能聊天室会话"""
    try:
        session_id = str(uuid.uuid4())

        # 模拟会话创建
        chatrooms[session_id] = {
            "session_id": session_id,
            "user_id": request.user_id,
            "session_name": request.session_name or f"会话_{session_id[:8]}",
            "participants": request.participants or [],
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }

        messages[session_id] = []

        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.post("/create")
async def create_chatroom(request: CreateChatRoomRequest):
    """创建聊天室 - 兼容性端点"""
    try:
        room_id = str(uuid.uuid4())

        # 创建聊天室
        chatrooms[room_id] = {
            "room_id": room_id,
            "room_name": request.room_name,
            "topic": request.topic,
            "participants": request.participants,
            "created_at": datetime.now().isoformat(),
            "status": "active",
        }

        messages[room_id] = []

        # 如果有初始消息，添加到消息列表
        if request.topic:
            initial_msg = {
                "message_id": str(uuid.uuid4()),
                "content": request.topic,
                "sender_name": "系统",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text",
            }
            messages[room_id].append(initial_msg)

        return {"room_id": room_id, "success": True}
    except Exception as e:
        logging.error(f"创建聊天室失败: {e!s}")
        return {"success": False, "error": str(e)}


@chatroom_router.post("/{room_id}/messages")
async def send_message(room_id: str, request: SendMessageRequest):
    """发送消息到聊天室"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        message_id = str(uuid.uuid4())
        message_data = {
            "message_id": message_id,
            "content": request.content,
            "sender_name": request.sender_name,
            "timestamp": datetime.now().isoformat(),
            "message_type": request.message_type,
            "metadata": request.metadata or {},
        }

        messages[room_id].append(message_data)

        # 模拟AI回复
        ai_response = await _generate_ai_response(request.content, room_id)
        if ai_response:
            ai_message = {
                "message_id": str(uuid.uuid4()),
                "content": ai_response,
                "sender_name": "AI助手",
                "timestamp": datetime.now().isoformat(),
                "message_type": "text",
            }
            messages[room_id].append(ai_message)

        return {"success": True, "message_id": message_id, "ai_response": ai_response}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"发送消息失败: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.get("/{room_id}/messages")
async def get_messages(room_id: str, limit: int = 50, offset: int = 0):
    """获取聊天室消息"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_messages = messages.get(room_id, [])
        total = len(room_messages)

        # 分页
        paginated_messages = room_messages[offset : offset + limit]

        return {
            "success": True,
            "messages": paginated_messages,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.get("/rooms")
async def get_chatrooms():
    """获取所有聊天室"""
    try:
        room_list = []
        for room_id, room_data in chatrooms.items():
            room_info = {
                "room_id": room_id,
                "room_name": room_data.get("room_name", "未命名聊天室"),
                "participants": room_data.get("participants", []),
                "created_at": room_data.get("created_at"),
                "status": room_data.get("status", "active"),
                "message_count": len(messages.get(room_id, [])),
            }
            room_list.append(room_info)

        return {"success": True, "rooms": room_list, "total": len(room_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.delete("/{room_id}")
async def delete_chatroom(room_id: str):
    """删除聊天室"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        del chatrooms[room_id]
        if room_id in messages:
            del messages[room_id]

        return {"success": True, "message": "聊天室已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_ai_response(message: str, room_id: str) -> Optional[str]:
    """生成AI回复"""
    try:
        # 简单的AI回复逻辑
        message_lower = message.lower()

        if "你好" in message or "hello" in message:
            return "你好！我是AI助手，很高兴为您服务。"

        elif "帮助" in message or "help" in message:
            return "我可以帮助您进行各种分析和讨论。请告诉我您需要什么帮助。"

        elif "分析" in message or "分析" in message:
            return "我可以帮您分析文档、数据或问题。请提供具体的内容。"

        elif "谢谢" in message or "感谢" in message:
            return "不客气！如果还有其他问题，随时可以问我。"

        else:
            # 根据消息内容生成通用回复
            return f'我理解您说的"{message}"。请告诉我更多细节，我会尽力帮助您。'
    except Exception as e:
        logging.error(f"生成AI回复失败: {e!s}")
        return None


@chatroom_router.get("/stats")
async def get_chatroom_stats():
    """获取聊天室统计信息"""
    try:
        total_rooms = len(chatrooms)
        total_messages = sum(len(msgs) for msgs in messages.values())
        active_rooms = sum(
            1 for room in chatrooms.values() if room.get("status") == "active"
        )

        return {
            "success": True,
            "stats": {
                "total_rooms": total_rooms,
                "active_rooms": active_rooms,
                "total_messages": total_messages,
                "average_messages_per_room": total_messages / total_rooms
                if total_rooms > 0
                else 0,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.get("/{room_id}")
async def get_chatroom_info(room_id: str):
    """获取聊天室信息"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_data = chatrooms[room_id]
        room_messages = messages.get(room_id, [])

        return {
            "success": True,
            "room_id": room_id,
            "room_name": room_data.get("room_name", "未命名聊天室"),
            "participants": room_data.get("participants", []),
            "created_at": room_data.get("created_at"),
            "status": room_data.get("status", "active"),
            "message_count": len(room_messages),
            "last_activity": room_messages[-1]["timestamp"] if room_messages else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.get("/")
async def get_chatroom_list():
    """获取聊天室列表 - 兼容性端点"""
    return await get_chatrooms()


@chatroom_router.get("/{room_id}/participants")
async def get_chatroom_participants(room_id: str):
    """获取聊天室参与者列表"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_data = chatrooms[room_id]
        participants = room_data.get("participants", [])

        return {
            "success": True,
            "participants": [
                {
                    "id": participant,
                    "name": participant,
                    "role": "participant",
                    "joined_at": room_data.get("created_at"),
                }
                for participant in participants
            ],
            "total": len(participants),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.post("/{room_id}/participants")
async def add_chatroom_participant(room_id: str, request: dict[str, str]):
    """添加聊天室参与者"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        participant_id = request.get("participant_id")
        if not participant_id:
            raise HTTPException(status_code=400, detail="缺少participant_id")

        room_data = chatrooms[room_id]
        participants = room_data.get("participants", [])

        if participant_id not in participants:
            participants.append(participant_id)
            room_data["participants"] = participants

        return {
            "success": True,
            "message": f"成功添加参与者: {participant_id}",
            "participants": participants,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.post("/{room_id}/generate_responses")
async def generate_ai_responses(room_id: str):
    """生成AI响应"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_messages = messages.get(room_id, [])
        if not room_messages:
            raise HTTPException(status_code=400, detail="聊天室没有消息")

        # 获取最后几条消息作为上下文
        recent_messages = room_messages[-5:]  # 最近5条消息
        context = "\n".join(
            [f"{msg['sender_name']}: {msg['content']}" for msg in recent_messages],
        )

        # 模拟AI响应生成
        ai_responses = []
        participants = chatrooms[room_id].get("participants", [])

        for participant in participants[:3]:  # 最多生成3个AI响应
            ai_response = await _generate_ai_response(context, room_id)
            if ai_response:
                ai_message = {
                    "message_id": str(uuid.uuid4()),
                    "content": ai_response,
                    "sender_name": f"{participant}(AI)",
                    "timestamp": datetime.now().isoformat(),
                    "message_type": "text",
                }
                messages[room_id].append(ai_message)
                ai_responses.append(ai_message)

        return {
            "success": True,
            "responses": ai_responses,
            "generated_count": len(ai_responses),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@chatroom_router.get("/{room_id}/statistics")
async def get_chatroom_statistics(room_id: str):
    """获取聊天室统计信息"""
    try:
        if room_id not in chatrooms:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        room_data = chatrooms[room_id]
        room_messages = messages.get(room_id, [])
        participants = room_data.get("participants", [])

        # 统计消息发送者
        sender_stats = {}
        for msg in room_messages:
            sender = msg.get("sender_name", "未知")
            sender_stats[sender] = sender_stats.get(sender, 0) + 1

        return {
            "success": True,
            "room_id": room_id,
            "room_name": room_data.get("room_name", "未命名聊天室"),
            "message_count": len(room_messages),
            "participant_count": len(participants),
            "created_at": room_data.get("created_at"),
            "last_activity": room_messages[-1]["timestamp"] if room_messages else None,
            "sender_statistics": sender_stats,
            "most_active_sender": max(sender_stats.items(), key=lambda x: x[1])[0]
            if sender_stats
            else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/rooms")
def create_chat_room():
    return {"success": True, "room_id": "mock_room_id"}
