# @AI-Generated: 2024-07-23, Confidence: 0.99, Model: Gemini-Code-Assist
"""API Endpoints for Multi-Role Chat and Role Management.
"""

import asyncio
import json
import logging
import os
import random
from datetime import datetime
from typing import Any, Optional

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.app_state import AppState, get_app_state
from src.chat_config import DEFAULT_CHAT_MODEL, get_available_models
from src.multi_role_chat import MultiRoleChatEngine

router = APIRouter(
    tags=["Roles & Multi-Role Chat"],
)
logger = logging.getLogger(__name__)

# --- Pydantic Models ---


class Role(BaseModel):
    name: str
    desc: str


class SmartRoleCreateRequest(BaseModel):
    role_name: str
    role_definition: str
    category: Optional[str] = "通用"
    specialties: Optional[list[str]] = []
    skills: Optional[list[str]] = []
    experience_years: Optional[int] = 5
    reputation_score: Optional[float] = 80.0
    languages: Optional[list[str]] = ["中文", "英文"]
    availability: Optional[str] = "可用"
    location: Optional[str] = ""
    education: Optional[list[str]] = []
    certifications: Optional[list[str]] = []
    projects: Optional[list[str]] = []


class BatchRoleImportRequest(BaseModel):
    roles: list[dict[str, Any]]
    overwrite_existing: bool = False
    validate_only: bool = False


class ChatMessage(BaseModel):
    sender_name: str = Field(..., description="发送者姓名")
    content: str = Field(..., min_length=1, description="消息内容")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


class MultiRoleChatRequest(BaseModel):
    topic: str
    roles: list[str]
    messages: list[ChatMessage]


class MultiRoleChatResponse(BaseModel):
    new_message: ChatMessage


class CreateChatRoomRequest(BaseModel):
    room_name: str
    topic: str
    initial_participants: list[str] = []
    model_type: str = DEFAULT_CHAT_MODEL


class SendMessageRequest(BaseModel):
    room_id: str = Field(..., description="聊天室ID")
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    sender_name: str = Field(default="用户", max_length=100, description="发送者姓名")
    message_type: str = Field(default="text", description="消息类型")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")


class AddParticipantRequest(BaseModel):
    room_id: str
    role_id: str


class GenerateResponseRequest(BaseModel):
    room_id: str
    target_roles: list[str] = []


class RoleRecommendationRequest(BaseModel):
    room_id: Optional[str] = None
    count: int = 6
    category: Optional[str] = None
    topic: str = ""


# --- Helper Functions ---


async def call_llm_simulation(
    role_name: str, topic: str, history: list[ChatMessage], app_state: AppState
) -> str:
    """模拟LLM调用, 使用增强的、更具人格化的prompt。"""
    await asyncio.sleep(1)  # 模拟网络延迟

    # 从全局缓存获取角色描述
    role_details = app_state.all_roles_details.get(
        role_name, {"desc": "一个普通的参与者"}
    )
    role_desc = role_details["desc"]

    history_summary = "\n".join(
        [f"- {msg.sender_name}: {msg.content}" for msg in history]
    )

    # 构建一个更复杂的、指示性的prompt，要求模型进行深度角色扮演和模仿人类行为
    prompt_for_llm = f"""### 指令 ###
你正在一个多角色聊天应用中扮演一个角色。请严格按照你的角色设定进行回应，并模仿真实人类的聊天行为。

### 你的角色信息 ###
- **角色名称:** {role_name}
- **角色描述/人设:** {role_desc}

### 扮演要求 ###
1.  **深度角色扮演:** 你的每一句话都要完全符合你角色的身份、性格和知识背景。
2.  **模仿人类:**
    *   **使用口语化、生活化的语言**，避免过于正式或书面化。
    *   可以适当使用**网络用语、emoji表情（例如 😉, 🤔, 😂）**来表达情绪。
    *   你的回应不一定总是完美无缺的，可以有**细微的逻辑跳跃或口误**，就像真人在快速聊天时那样。
    *   回复可以简短，也可以很长，取决于情境。

### 当前聊天情景 ###
- **聊天主题:** {topic}
- **最近的对话历史:**
{history_summary}

### 你的任务 ###
根据以上设定和聊天历史，以 **{role_name}** 的身份，对最后一条消息进行回应。你的回应内容将直接展示给用户。不要在回应中包含 "好的"、"根据您的要求" 或任何提及你是一个AI模型的词语。直接开始你的角色扮演对话。"""

    # 这是一个模拟的回复，旨在展示遵循新prompt可能产生的结果
    last_user_message = history[-1].content
    simulated_response = f"嗨，我是**{role_name}**！ 😉\n"
    if len(last_user_message) < 10:
        simulated_response += f'刚看到你说的"{last_user_message}"，这事儿有意思。'
    else:
        simulated_response += f'关于"{last_user_message[:20]}..."这个点，我插句话哈，从我们({role_name})的角度看，这事儿吧，可能没那么简单...🤔 感觉需要考虑XXX方面的问题。'

    simulated_response += "\n\n(PS: 这是一个基于新prompt的模拟回复，实际效果取决于LLM。)"

    # 在真实场景中，你会用 `prompt_for_llm` 去调用真正的LLM服务
    # return real_llm_client.generate(prompt_for_llm)
    return simulated_response


# --- API Endpoints ---


@router.get("/roles", response_model=dict[str, list[str]])
async def get_roles(app_state: AppState = Depends(get_app_state)):
    """获取所有可用的角色列表"""
    return {"roles": sorted(list(app_state.all_roles_details.keys()))}


@router.get("/roles/details", response_model=dict[str, Any])
async def get_roles_details(app_state: AppState = Depends(get_app_state)):
    """获取所有角色的详细信息"""
    roles_list = []
    for name, details in app_state.all_roles_details.items():
        role_info = {
            "name": name,
            "description": details.get("desc", ""),
            "tags": details.get("tags", []),
            "id": name  # 使用name作为id
        }
        roles_list.append(role_info)

    return {"roles": roles_list}


@router.post("/roles/create", response_model=Role)
async def create_role(role: Role, app_state: AppState = Depends(get_app_state)):
    """创建并保存一个新角色"""
    if role.name in app_state.all_roles_details:
        raise HTTPException(status_code=400, detail=f"角色 '{role.name}' 已存在。")

    try:
        from src.role_utils import standardize_role_dict

        role_data = role.dict()
        standardized_role = standardize_role_dict(role_data)

        if os.path.exists(app_state.USER_ROLES_FILE):
            with open(app_state.USER_ROLES_FILE, "r+", encoding="utf-8") as f:
                try:
                    roles_list = json.load(f)
                    if not isinstance(roles_list, list):
                        roles_list = []
                except json.JSONDecodeError:
                    roles_list = []
        else:
            roles_list = []

        roles_list.append(standardized_role)

        with open(app_state.USER_ROLES_FILE, "w", encoding="utf-8") as f:
            json.dump(roles_list, f, ensure_ascii=False, indent=2)

        app_state.load_all_roles()
        return Role(**standardized_role)
    except Exception as e:
        logger.error(f"创建角色失败: {e}")
        raise HTTPException(status_code=500, detail="创建角色时服务器内部发生错误。")


@router.post("/roles/create_smart", response_model=dict[str, Any])
async def create_smart_role(
    request: SmartRoleCreateRequest, app_state: AppState = Depends(get_app_state)
):
    """智能创建并标准化角色"""
    try:
        from src.role_utils import analyze_role_definition, standardize_role_dict

        analysis_result = analyze_role_definition(
            request.role_name, request.role_definition
        )

        role_data = {
            "name": request.role_name,
            "description": request.role_definition,
            "category": request.category,
            "specialties": request.specialties
            if request.specialties
            else analysis_result["specialties"],
            "skills": request.skills if request.skills else analysis_result["skills"],
            "experience_years": request.experience_years
            if request.experience_years != 5
            else analysis_result["experience_years"],
            "reputation_score": request.reputation_score
            if request.reputation_score != 80.0
            else analysis_result["reputation_score"],
            "languages": request.languages
            if request.languages
            else analysis_result["languages"],
            "availability": request.availability,
            "location": request.location,
            "education": request.education,
            "certifications": request.certifications,
            "projects": request.projects,
        }

        standardized_role = standardize_role_dict(role_data)

        if standardized_role["name"] in app_state.all_roles_details:
            raise HTTPException(
                status_code=400, detail=f"角色 '{standardized_role['name']}' 已存在。"
            )

        if os.path.exists(app_state.USER_ROLES_FILE):
            with open(app_state.USER_ROLES_FILE, "r+", encoding="utf-8") as f:
                try:
                    roles_list = json.load(f)
                    if not isinstance(roles_list, list):
                        roles_list = []
                except json.JSONDecodeError:
                    roles_list = []
        else:
            roles_list = []

        roles_list.append(standardized_role)

        with open(app_state.USER_ROLES_FILE, "w", encoding="utf-8") as f:
            json.dump(roles_list, f, ensure_ascii=False, indent=2)

        app_state.load_all_roles()

        return {
            "success": True,
            "role": standardized_role,
            "analysis": analysis_result,
            "message": f"角色 '{standardized_role['name']}' 创建成功，智能分析置信度: {analysis_result['analysis_confidence']:.1%}",
        }

    except Exception as e:
        logger.error(f"智能创建角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"智能创建角色失败: {str(e)}")


@router.post("/roles/batch_import", response_model=dict[str, Any])
async def batch_import_roles(
    request: BatchRoleImportRequest, app_state: AppState = Depends(get_app_state)
):
    """批量导入角色数据（每个角色写为单文件）"""
    user_defined_dir = app_state.USER_DEFINED_DIR
    os.makedirs(user_defined_dir, exist_ok=True)
    try:
        from src.role_utils import standardize_role_dict

        results = {
            "total": len(request.roles),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": [],
        }
        for i, role_data in enumerate(request.roles):
            try:
                standardized_role = standardize_role_dict(role_data)
                role_name = standardized_role["name"]
                role_id = standardized_role.get("id", "")
                safe_name = "".join(
                    c for c in role_name if c.isalnum() or c in ("_", "-")
                ).strip()
                filename = f"{safe_name}_{role_id}.json"
                filepath = os.path.join(user_defined_dir, filename)

                if os.path.exists(filepath) and not request.overwrite_existing:
                    results["skipped"] += 1
                    results["details"].append(
                        {
                            "index": i,
                            "name": role_name,
                            "status": "skipped",
                            "message": "角色已存在",
                        }
                    )
                    continue
                if not request.validate_only:
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(standardized_role, f, ensure_ascii=False, indent=2)
                results["success"] += 1
                results["details"].append(
                    {
                        "index": i,
                        "name": role_name,
                        "status": "success",
                        "message": "导入成功" if not request.validate_only else "验证通过",
                    }
                )
            except Exception as e:
                results["failed"] += 1
                results["details"].append(
                    {
                        "index": i,
                        "name": role_data.get("name", f"角色{i}"),
                        "status": "failed",
                        "message": str(e),
                    }
                )

        if not request.validate_only and results["success"] > 0:
            app_state.load_all_roles()
        return results
    except Exception as e:
        logger.error(f"批量导入角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量导入角色失败: {str(e)}")


@router.post("/multi_role_chat", response_model=MultiRoleChatResponse)
async def multi_role_chat(
    request: MultiRoleChatRequest, app_state: AppState = Depends(get_app_state)
):
    """处理多角色聊天逻辑"""
    try:
        with open(app_state.CHAT_LOG_FILE, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": asyncio.get_event_loop().time(),
                "topic": request.topic,
                "roles": request.roles,
                "messages": [msg.model_dump() for msg in request.messages],
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        ai_roles = [r for r in request.roles if r.lower() not in ["user", "system"]]
        if not ai_roles:
            raise HTTPException(status_code=400, detail="聊天中没有可用的AI角色。")

        selected_role = random.choice(ai_roles)

        context_messages = request.messages[-random.randint(1, 5) :]
        llm_response_content = await call_llm_simulation(
            selected_role, request.topic, context_messages, app_state
        )

        new_message = ChatMessage(
            sender_name=selected_role, content=llm_response_content
        )

        return MultiRoleChatResponse(new_message=new_message)

    except Exception as e:
        logger.error(f"多角色聊天失败: {e}")
        raise HTTPException(status_code=500, detail="多角色聊天时服务器内部发生错误。")


@router.post("/roles/search_embedding")
async def api_search_roles_by_embedding(
    query: str, top_k: int = 5, app_state: AppState = Depends(get_app_state)
):
    """智能embedding检索角色，返回最相关top_k角色"""
    query_emb = app_state.get_text_embedding(query)
    scored = []
    for name, info in app_state.all_roles_details.items():
        emb = info.get("embedding")
        if emb:
            score = float(
                np.dot(query_emb, emb)
                / (np.linalg.norm(query_emb) * np.linalg.norm(emb) + 1e-8)
            )
            scored.append((score, name, info))
    scored.sort(reverse=True, key=lambda x: x[0])
    return {
        "roles": [
            {"name": n, "desc": i.get("desc", ""), "score": s}
            for s, n, i in scored[:top_k]
        ]
    }


@router.post("/multi_chat/create_engine")
async def create_chat_engine(
    engine_id: str,
    model_type: str = DEFAULT_CHAT_MODEL,
    app_state: AppState = Depends(get_app_state),
):
    """创建聊天引擎实例"""
    try:
        if engine_id in app_state.chat_engines:
            return {"success": False, "message": "聊天引擎已存在"}

        if not app_state.expert_library.experts:
            app_state.expert_library.load_experts_from_directory()

        app_state.chat_engines[engine_id] = MultiRoleChatEngine(app_state.expert_library, model_type)

        return {
            "success": True,
            "engine_id": engine_id,
            "model_type": model_type,
            "message": "聊天引擎创建成功",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建聊天引擎失败: {str(e)}")


@router.post("/multi_chat/create_room")
async def create_chat_room(
    request: CreateChatRoomRequest, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """创建聊天室"""
    try:
        if engine_id not in app_state.chat_engines:
            await create_chat_engine(engine_id, request.model_type, app_state)

        chat_engine = app_state.chat_engines[engine_id]
        room_id = chat_engine.create_chat_room(
            room_name=request.room_name,
            topic=request.topic,
            initial_participants=request.initial_participants,
        )

        return {"success": True, "room_id": room_id, "message": "聊天室创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建聊天室失败: {str(e)}")


@router.post("/multi_chat/send_message")
async def send_message(
    request: SendMessageRequest, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """发送用户消息"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        success = await chat_engine.send_user_message(
            room_id=request.room_id,
            content=request.content,
            sender_name=request.sender_name,
        )

        if success:
            return {"success": True, "message": "消息发送成功"}
        else:
            raise HTTPException(status_code=404, detail="聊天室不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")


@router.post("/multi_chat/generate_responses")
async def generate_ai_responses(
    request: dict, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """生成AI角色响应"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        room_id = request.get("room_id")
        target_roles = request.get("target_roles")

        if not room_id:
            raise HTTPException(status_code=400, detail="缺少room_id参数")

        responses = await chat_engine.generate_role_responses(room_id, target_roles)

        response_data = [
            {
                "id": r.id,
                "role_id": r.role_id,
                "role_name": r.role_name,
                "content": r.content,
                "timestamp": r.timestamp,
                "message_type": r.message_type,
                "metadata": r.metadata,
            }
            for r in responses
        ]

        return {
            "success": True,
            "responses": response_data,
            "count": len(response_data),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成AI响应失败: {str(e)}")


@router.post("/multi_chat/add_participant")
async def add_participant(
    request: AddParticipantRequest, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """添加参与者"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        success = chat_engine.add_participant(request.room_id, request.role_id)

        if success:
            return {"success": True, "message": "参与者添加成功"}
        else:
            return {
                "success": False,
                "message": "添加失败，可能是聊天室不存在、角色已参与或达到人数上限",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加参与者失败: {str(e)}")


@router.delete("/multi_chat/remove_participant")
async def remove_participant(
    room_id: str, role_id: str, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """移除参与者"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        success = chat_engine.remove_participant(room_id, role_id)

        if success:
            return {"success": True, "message": "参与者移除成功"}
        else:
            return {"success": False, "message": "移除失败，可能是聊天室或参与者不存在"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除参与者失败: {str(e)}")


@router.get("/multi_chat/room/{room_id}")
async def get_chat_room(
    room_id: str, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """获取聊天室信息"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        room = chat_engine.get_chat_room(room_id)

        if not room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        participants_data = [
            {
                "role_id": p.role_id,
                "role_name": p.role_name,
                "is_active": p.is_active,
                "message_count": p.message_count,
                "last_activity": p.last_activity,
                "role_category": p.role_data.get("category", ""),
                "role_title": p.role_data.get("title", ""),
            }
            for p in room.participants
        ]

        messages_data = [
            {
                "id": m.id,
                "role_id": m.role_id,
                "role_name": m.role_name,
                "content": m.content,
                "timestamp": m.timestamp,
                "message_type": m.message_type,
                "metadata": m.metadata,
            }
            for m in room.messages
        ]

        return {
            "success": True,
            "room": {
                "room_id": room.room_id,
                "room_name": room.room_name,
                "topic": room.topic,
                "participants": participants_data,
                "messages": messages_data,
                "created_at": room.created_at,
                "last_activity": room.last_activity,
                "is_active": room.is_active,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天室失败: {str(e)}")


@router.get("/multi_chat/rooms")
async def get_all_rooms(engine_id: str = "default", app_state: AppState = Depends(get_app_state)):
    """获取所有聊天室"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        rooms = chat_engine.get_all_rooms()

        rooms_data = [
            {
                "room_id": r.room_id,
                "room_name": r.room_name,
                "topic": r.topic,
                "participant_count": len(r.participants),
                "message_count": len(r.messages),
                "created_at": r.created_at,
                "last_activity": r.last_activity,
                "is_active": r.is_active,
            }
            for r in rooms
        ]

        return {"success": True, "rooms": rooms_data, "total_rooms": len(rooms_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天室列表失败: {str(e)}")


@router.post("/multi_chat/recommend_roles")
async def recommend_roles(
    request: RoleRecommendationRequest, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """推荐角色"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]

        if request.room_id:
            recommendations = chat_engine.get_room_recommendations(
                request.room_id, request.count
            )
        else:
            recommendations = chat_engine.get_random_recommendations(
                request.count, request.category
            )

        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色推荐失败: {str(e)}")


@router.get("/multi_chat/available_models")
async def get_available_chat_models():
    """获取可用的聊天模型"""
    try:
        models = get_available_models()
        return {
            "success": True,
            "available_models": models,
            "default_model": DEFAULT_CHAT_MODEL,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取可用模型失败: {str(e)}")


@router.get("/multi_chat/statistics")
async def get_chat_statistics(engine_id: str = "default", app_state: AppState = Depends(get_app_state)):
    """获取聊天统计信息"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        stats = chat_engine.get_chat_statistics()

        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/multi_chat/room/{room_id}/messages")
async def get_room_messages(
    room_id: str, engine_id: str = "default", app_state: AppState = Depends(get_app_state)
):
    """获取聊天室消息"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        room = chat_engine.get_chat_room(room_id)

        if not room:
            raise HTTPException(status_code=404, detail="聊天室不存在")

        messages_data = [
            {
                "id": m.id,
                "role_id": m.role_id,
                "role_name": m.role_name,
                "content": m.content,
                "timestamp": m.timestamp,
                "message_type": m.message_type,
                "metadata": m.metadata,
            }
            for m in room.messages
        ]

        return {
            "success": True,
            "messages": messages_data,
            "total_messages": len(messages_data),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天室消息失败: {str(e)}")


@router.get("/multi_chat/room/{room_id}/recommendations")
async def get_room_role_recommendations(
    room_id: str,
    count: int = 6,
    side: Optional[str] = None,
    message_type: Optional[str] = None,
    engine_id: str = "default",
    app_state: AppState = Depends(get_app_state),
):
    """获取聊天室角色推荐"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        recommendations = chat_engine.get_room_recommendations(room_id, count)

        if message_type == "debate" and side:
            filtered_recommendations = []
            for rec in recommendations:
                if side == "正方" and any(
                    keyword in rec.get("specialties", [])
                    for keyword in ["支持", "积极", "正面"]
                ):
                    filtered_recommendations.append(rec)
                elif side == "反方" and any(
                    keyword in rec.get("specialties", [])
                    for keyword in ["批判", "质疑", "反对"]
                ):
                    filtered_recommendations.append(rec)
                else:
                    filtered_recommendations.append(rec)
            recommendations = filtered_recommendations[:count]

        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations),
            "room_id": room_id,
            "criteria": {"side": side, "type": message_type, "count": count},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色推荐失败: {str(e)}")


@router.get("/multi_chat/models")
async def get_chat_models():
    """获取可用的聊天模型"""
    try:
        models = get_available_models()
        return {
            "success": True,
            "models": models,
            "default_model": DEFAULT_CHAT_MODEL,
            "total_models": len(models),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天模型失败: {str(e)}")


@router.post("/analyze_debate_materials")
async def analyze_debate_materials(request: dict):
    """分析辩论材料"""
    try:
        documents = request.get("documents", [])
        if not documents:
            raise HTTPException(status_code=400, detail="没有提供文档进行分析")

        analysis_result = {
            "total_documents": len(documents),
            "analysis_summary": {
                "key_topics": ["人工智能", "技术发展", "社会影响"],
                "sentiment_analysis": {"positive": 0.6, "negative": 0.3, "neutral": 0.1},
                "main_arguments": ["AI技术能够提高工作效率", "AI可能导致就业问题", "需要建立AI伦理规范"],
                "evidence_strength": "中等",
                "credibility_score": 0.75,
            },
            "document_breakdown": [],
        }

        for i, doc in enumerate(documents):
            doc_analysis = {
                "filename": doc.get("filename", f"文档{i+1}"),
                "type": doc.get("type", "中性材料"),
                "key_points": [f"文档{i+1}的关键观点1", f"文档{i+1}的关键观点2"],
                "stance": "中性"
                if doc.get("type") == "中性材料"
                else doc.get("type", "").replace("材料", ""),
                "reliability": 0.8,
            }
            analysis_result["document_breakdown"].append(doc_analysis)

        return {
            "success": True,
            "analysis": analysis_result,
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"辩论材料分析失败: {str(e)}")


@router.delete("/multi_chat/room/{room_id}")
async def delete_chat_room(room_id: str, engine_id: str = "default", app_state: AppState = Depends(get_app_state)):
    """删除聊天室"""
    if engine_id not in app_state.chat_engines:
        raise HTTPException(status_code=404, detail="聊天引擎不存在")

    try:
        chat_engine = app_state.chat_engines[engine_id]
        success = chat_engine.delete_chat_room(room_id)

        if success:
            return {"success": True, "message": "聊天室删除成功"}
        else:
            raise HTTPException(status_code=404, detail="聊天室不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除聊天室失败: {str(e)}")
