"""简化的FastAPI应用 - 集成云端聊天模型
"""
import logging
from typing import Optional

import uvicorn

# 导入云端聊天管理器
from cloud_chat_manager import get_cloud_chat_manager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="DAIP Insight Engine - 云端模型版",
    description="智能洞察引擎 - 使用云端大模型进行对话",
    version="1.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 数据模型
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    session_id: str = "default_session"


class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    message: str = ""
    model_used: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str


# 全局变量
chat_history = []
cloud_manager = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化云端聊天管理器"""
    global cloud_manager
    try:
        cloud_manager = get_cloud_chat_manager()
        logger.info("云端聊天管理器初始化成功")
    except Exception as e:
        logger.error(f"云端聊天管理器初始化失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {"message": "DAIP Insight Engine 云端模型版运行中"}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(status="healthy", message="服务正常运行", version="1.0.0")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """使用云端模型的聊天接口"""
    try:
        global cloud_manager

        # 记录聊天历史
        chat_history.append(
            {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "message": request.message,
                "timestamp": "2024-01-01T00:00:00Z",
            }
        )

        # 使用云端模型进行对话
        if cloud_manager:
            response = await cloud_manager.chat(request.message, request.user_id)
            # 获取当前使用的模型信息
            status = cloud_manager.get_status()
            current_model = (
                status.get("available_models", [])[status.get("current_model_index", 0)]
                if status.get("available_models")
                else None
            )

            return ChatResponse(
                response=response,
                status="success",
                message="云端模型对话成功",
                model_used=current_model,
            )
        else:
            # 回退到简单回复
            response = "云端模型管理器未初始化，使用简单回复模式。"
            return ChatResponse(
                response=response,
                status="fallback",
                message="使用简单回复模式",
                model_used="fallback",
            )

    except Exception as e:
        logger.error(f"聊天处理错误: {e}")
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")


@app.get("/chat/history")
async def get_chat_history(user_id: str = "default_user", limit: int = 10):
    """获取聊天历史"""
    try:
        user_history = [msg for msg in chat_history if msg["user_id"] == user_id]
        return {
            "status": "success",
            "history": user_history[-limit:],
            "total": len(user_history),
        }
    except Exception as e:
        logger.error(f"获取聊天历史错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取聊天历史失败: {str(e)}")


@app.get("/experts")
async def get_experts():
    """获取专家列表（简化版）"""
    try:
        # 返回一些示例专家
        experts = [
            {
                "id": "expert_001",
                "name": "技术专家",
                "category": "技术",
                "description": "专注于技术方案设计",
                "status": "available",
            },
            {
                "id": "expert_002",
                "name": "业务专家",
                "category": "业务",
                "description": "专注于业务分析",
                "status": "available",
            },
        ]

        return {"status": "success", "experts": experts, "total": len(experts)}

    except Exception as e:
        logger.error(f"获取专家列表错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取专家列表失败: {str(e)}")


@app.get("/status")
async def get_status():
    """获取系统状态"""
    global cloud_manager

    cloud_status = {}
    if cloud_manager:
        cloud_status = cloud_manager.get_status()

    return {
        "status": "running",
        "version": "1.0.0",
        "mode": "cloud_models",
        "features": {
            "chat": "cloud_models",
            "experts": "simplified",
            "vector_db": "disabled",
            "role_loading": "disabled",
            "embedding": "local_nomic",
        },
        "cloud_models": cloud_status,
        "message": "云端模型版本运行中，使用本地嵌入模型和云端对话模型",
    }


@app.get("/models")
async def get_models():
    """获取可用模型列表"""
    global cloud_manager

    if cloud_manager:
        status = cloud_manager.get_status()
        return {
            "status": "success",
            "available_models": status.get("available_models", []),
            "model_rotation": status.get("model_rotation", False),
            "auto_fallback": status.get("auto_fallback", False),
            "total_models": status.get("total_models", 0),
        }
    else:
        return {"status": "error", "message": "云端模型管理器未初始化"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
