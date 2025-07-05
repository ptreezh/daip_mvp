import json
import os
import time
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.config import CHROMA_PATH, DATABASE_PATH
from src.lim import LLMInteractionModule
from src.protocol_dag_utils import (
    build_protocol_dag,
    extract_protocol_steps_with_ollama,
)
from src.protocol_schema_validator import validate_protocol_dag
from src.sskg import SSKG
from src.tool_config import tool_config

# 初始化 SSKG 和 LLMInteractionModule
sskg_instance = SSKG(DATABASE_PATH, CHROMA_PATH)
sskg_instance.init_db()
llm_module = LLMInteractionModule(sskg_instance)

app = FastAPI()


@app.get("/")
async def root():
    """根路径 - 提供API基本信息"""
    return {
        "message": "DAIP Insight Engine API",
        "version": "1.0.0",
        "description": "智能协议生成与多角色聊天系统",
        "endpoints": {
            "health": "/health",
            "models": "/ai/models",
            "ai_execute": "/ai/execute",
            "protocol_dag": "/ai/protocol_dag",
            "chatroom": {
                "rooms": "/multi_chat/rooms",
                "models": "/multi_chat/models",
                "stats": "/chatroom/stats",
                "create_session": "/chatroom/create_session",
            },
        },
        "docs": "/docs",
    }


class ProtocolGenRequest(BaseModel):
    input: str
    tool_definitions: list[dict[str, Any]] = []  # 可选，支持工具调用
    lang: Optional[str] = "zh"
    model: Optional[str] = None


class ProtocolDagRequest(BaseModel):
    input: str
    lang: Optional[str] = "zh"
    model: Optional[str] = None


# 简单文件持久化中间结果
def save_intermediate_result(flow_id: str, dag: dict):
    os.makedirs("data/intermediate", exist_ok=True)
    with open(f"data/intermediate/{flow_id}.json", "w", encoding="utf-8") as f:
        json.dump(dag, f, ensure_ascii=False, indent=2)


def load_intermediate_result(flow_id: str):
    try:
        with open(f"data/intermediate/{flow_id}.json", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def log_retry_and_error(flow_id: str, attempt: int, error: str):
    os.makedirs("data/intermediate", exist_ok=True)
    with open(f"data/intermediate/{flow_id}.log", "a", encoding="utf-8") as f:
        f.write(f"Attempt {attempt}: {error}\n")


def load_prompt_templates():
    try:
        with open("config/prompt_templates.json", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


# prompt模板集中管理，支持热更新和A/B测试
def get_prompt(lang, ab_test=None):
    templates = load_prompt_templates()
    if templates:
        # 支持A/B测试
        if ab_test and ab_test in templates.get(lang, {}):
            return templates[lang][ab_test]
        return templates.get(lang, {}).get("default")
    # fallback
    PROMPTS = {
        "zh": "请根据以下协议需求，提取每个关键步骤，标明责任角色、节点类型（user_input/auto/approval）、后续步骤。请严格以结构化方式输出，不要遗漏任何步骤。输出请调用extract_protocol_steps函数。",
        "en": "Please extract each key step from the following protocol requirement, specifying the responsible role, node type (user_input/auto/approval), and next steps. Output must be strictly structured. Please call the extract_protocol_steps function.",
    }
    return PROMPTS.get(lang, PROMPTS["zh"])


@app.post("/ai/execute")
async def ai_execute(req: ProtocolGenRequest):
    """接收自然语言输入，调用 LLM 生成协议草案，返回结构化协议内容。"""
    result = await llm_module.get_llm_response(req.input, req.tool_definitions)
    return {"result": result}


@app.post("/ai/protocol_dag")
async def ai_protocol_dag(req: ProtocolDagRequest, ab_test: Optional[str] = None):
    """输入自然语言协议需求，返回结构化DAG数据，自动校验，异常重试，持久化中间结果，支持多语言多模型。"""
    flow_id = str(abs(hash(req.input + (req.lang or "") + (req.model or ""))))
    prompt = get_prompt(req.lang, ab_test)
    max_retries = 3
    last_error = None
    for attempt in range(max_retries):
        try:
            model = req.model or tool_config.model.function_calling_model
            steps = extract_protocol_steps_with_ollama(
                prompt + "\n" + req.input,
                model=model,
            )
            dag = build_protocol_dag(steps)
            valid, err = validate_protocol_dag(dag)
            if not valid:
                log_retry_and_error(flow_id, attempt + 1, f"协议DAG校验失败: {err}")
                return {"success": False, "error": f"协议DAG校验失败: {err}", "dag": dag}
            save_intermediate_result(flow_id, dag)
            return {"success": True, "dag": dag, "flow_id": flow_id}
        except Exception as e:
            last_error = str(e)
            log_retry_and_error(flow_id, attempt + 1, last_error)
            continue
    return {"success": False, "error": f"生成或校验失败: {last_error}"}


@app.get("/ai/protocol_dag/history/{flow_id}")
async def get_protocol_dag_history(flow_id: str):
    dag = load_intermediate_result(flow_id)
    if dag:
        return {"success": True, "dag": dag}
    else:
        return {"success": False, "error": "未找到中间结果"}


# 多模型注册与健康检查接口
def get_registered_models():
    """获取已注册的模型列表"""
    try:
        # 使用统一的tool_config来获取模型信息
        models = []
        # 添加Ollama模型
        if tool_config.model.default_model:
            models.append(
                {
                    "name": tool_config.model.default_model,
                    "type": "ollama",
                    "description": f"Ollama模型: {tool_config.model.default_model}",
                },
            )
        # 添加函数调用模型
        if tool_config.model.function_calling_model:
            models.append(
                {
                    "name": tool_config.model.function_calling_model,
                    "type": "function_calling",
                    "description": f"函数调用模型: {tool_config.model.function_calling_model}",
                },
            )
        return models
    except Exception as e:
        print(f"Error loading model config: {e}")
        return []


@app.get("/ai/models")
async def list_models():
    return {"models": get_registered_models()}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {"database": "connected", "llm": "configured", "api": "running"},
    }


@app.get("/multi_chat/rooms")
async def get_multi_chat_rooms():
    """获取多角色聊天室列表"""
    return {
        "rooms": [
            {
                "room_id": "demo_room_1",
                "room_name": "演示聊天室",
                "topic": "AI技术讨论",
                "participant_count": 3,
                "message_count": 15,
                "created_at": "2024-01-01T10:00:00Z",
            },
        ],
    }


@app.get("/multi_chat/models")
async def get_multi_chat_models():
    """获取多角色聊天可用模型"""
    return {
        "models": [
            {
                "model_id": "qwen3:30b-a3b",
                "name": "Qwen 3 30B A3B",
                "type": "ollama",
                "status": "available",
            },
        ],
    }


@app.get("/chatroom/stats")
async def get_chatroom_stats():
    """获取聊天室统计信息"""
    return {
        "total_rooms": 1,
        "active_rooms": 1,
        "total_messages": 15,
        "total_participants": 3,
    }


@app.post("/chatroom/create_session")
async def create_chatroom_session(request: dict):
    """创建聊天室会话"""
    return {
        "session_id": "session_" + str(int(time.time())),
        "room_id": request.get("room_id", "demo_room_1"),
        "status": "created",
        "created_at": datetime.now().isoformat(),
    }


@app.get("/chatroom/session/{session_id}")
async def get_chatroom_session(session_id: str):
    """获取聊天室会话信息"""
    return {
        "session_id": session_id,
        "room_id": "demo_room_1",
        "status": "active",
        "messages": [
            {
                "message_id": "msg_1",
                "role_id": "user",
                "role_name": "用户",
                "content": "你好，这是一个演示消息",
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "message_id": "msg_2",
                "role_id": "assistant",
                "role_name": "AI助手",
                "content": "你好！我是AI助手，很高兴为您服务。",
                "timestamp": "2024-01-01T10:01:00Z",
            },
        ],
        "participants": [
            {"role_id": "user", "role_name": "用户", "status": "active"},
            {"role_id": "assistant", "role_name": "AI助手", "status": "active"},
        ],
    }


@app.get("/chatroom/history/{session_id}")
async def get_chatroom_history(session_id: str):
    """获取聊天室历史记录"""
    return {
        "session_id": session_id,
        "messages": [
            {
                "message_id": "msg_1",
                "role_id": "user",
                "role_name": "用户",
                "content": "你好，这是一个演示消息",
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "message_id": "msg_2",
                "role_id": "assistant",
                "role_name": "AI助手",
                "content": "你好！我是AI助手，很高兴为您服务。",
                "timestamp": "2024-01-01T10:01:00Z",
            },
        ],
    }


@app.post("/chatroom/send_message")
async def send_chatroom_message(request: dict):
    """发送聊天室消息"""
    return {
        "message_id": f"msg_{int(time.time())}",
        "session_id": request.get("session_id"),
        "role_id": request.get("role_id", "user"),
        "role_name": request.get("role_name", "用户"),
        "content": request.get("content", ""),
        "timestamp": datetime.now().isoformat(),
        "status": "sent",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
