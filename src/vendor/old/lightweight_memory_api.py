"""轻量级记忆服务API
高性能、低延迟的记忆管理API接口
"""

import logging
from datetime import datetime
from typing import Any, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.lightweight_memory_service import (
    LightweightMemoryService,
    MemoryPriority,
)
from src.service_container import get_lightweight_memory_service

# 创建FastAPI应用
app = FastAPI(title="轻量级记忆服务API", description="高性能、低延迟的记忆管理服务", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求模型
class LightweightMemoryRequest(BaseModel):
    role_id: str
    content: str
    memory_type: str
    importance: float = 0.5
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, CRITICAL
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    ttl: Optional[int] = None  # 生存时间（秒）


class MemoryQueryRequest(BaseModel):
    role_id: str
    limit: int = 10
    min_importance: float = 0.0
    project_id: Optional[str] = None
    session_id: Optional[str] = None


class ContextRequest(BaseModel):
    role_id: str
    current_question: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: Optional[list[dict[str, str]]] = None
    target_model: str = "ollama"


# 响应模型
class LightweightMemoryResponse(BaseModel):
    memory_id: str
    role_id: str
    content: str
    memory_type: str
    importance: float
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str]
    metadata: dict[str, Any]
    priority: str
    ttl: Optional[int] = None


class ContextResponse(BaseModel):
    role_id: str
    relevant_memories: list[LightweightMemoryResponse]
    role_identity: Optional[dict[str, Any]] = None
    conversation_summary: Optional[str] = None
    project_context: Optional[dict[str, Any]] = None
    model_adaptation: Optional[dict[str, Any]] = None


class PerformanceMetricsResponse(BaseModel):
    memory_operations: int
    cache_hits: int
    cache_misses: int
    db_operations: int
    average_response_time: float
    cache_hit_rate: float
    task_queue_size: int
    circuit_breaker_state: str


# 依赖注入
def get_memory_service() -> LightweightMemoryService:
    """获取轻量级记忆服务"""
    try:
        return get_lightweight_memory_service()
    except Exception as e:
        logging.error(f"获取轻量级记忆服务失败: {e}")
        raise HTTPException(status_code=500, detail="记忆服务不可用")


# API端点
@app.post("/memory/add", response_model=LightweightMemoryResponse)
async def add_memory(
    request: LightweightMemoryRequest,
    background_tasks: BackgroundTasks,
    memory_service: LightweightMemoryService = Depends(get_memory_service),
):
    """添加记忆"""
    try:
        # 转换优先级
        priority = MemoryPriority[request.priority.upper()]

        # 添加记忆
        memory_id = await memory_service.add_memory(
            role_id=request.role_id,
            content=request.content,
            memory_type=request.memory_type,
            importance=request.importance,
            priority=priority,
            project_id=request.project_id,
            session_id=request.session_id,
            tags=request.tags,
            metadata=request.metadata,
            ttl=request.ttl,
        )

        # 获取添加的记忆
        memories = await memory_service.get_memories(role_id=request.role_id, limit=1)

        if not memories:
            raise HTTPException(status_code=500, detail="记忆添加失败")

        memory = memories[0]

        return LightweightMemoryResponse(
            memory_id=memory.id,
            role_id=memory.role_id,
            content=memory.content,
            memory_type=memory.memory_type,
            importance=memory.importance,
            timestamp=memory.timestamp,
            project_id=memory.project_id,
            session_id=memory.session_id,
            tags=memory.tags,
            metadata=memory.metadata,
            priority=memory.priority.name,
            ttl=memory.ttl,
        )

    except Exception as e:
        logging.error(f"添加记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加记忆失败: {e!s}")


@app.post("/memory/query", response_model=list[LightweightMemoryResponse])
async def query_memories(
    request: MemoryQueryRequest,
    memory_service: LightweightMemoryService = Depends(get_memory_service),
):
    """查询记忆"""
    try:
        # 查询记忆
        memories = await memory_service.get_memories(
            role_id=request.role_id,
            limit=request.limit,
            min_importance=request.min_importance,
        )

        # 转换为响应格式
        response_memories = []
        for memory in memories:
            response_memories.append(
                LightweightMemoryResponse(
                    memory_id=memory.id,
                    role_id=memory.role_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    timestamp=memory.timestamp,
                    project_id=memory.project_id,
                    session_id=memory.session_id,
                    tags=memory.tags,
                    metadata=memory.metadata,
                    priority=memory.priority.name,
                    ttl=memory.ttl,
                ),
            )

        return response_memories

    except Exception as e:
        logging.error(f"查询记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询记忆失败: {e!s}")


@app.post("/context/build", response_model=ContextResponse)
async def build_context(
    request: ContextRequest,
    memory_service: LightweightMemoryService = Depends(get_memory_service),
):
    """构建对话上下文"""
    try:
        # 构建上下文
        context = await memory_service.build_context_for_conversation(
            role_id=request.role_id,
            current_question=request.current_question,
            project_id=request.project_id,
            session_id=request.session_id,
            conversation_history=request.conversation_history,
            target_model=request.target_model,
        )

        # 转换记忆格式
        relevant_memories = []
        for memory in context.relevant_memories:
            relevant_memories.append(
                LightweightMemoryResponse(
                    memory_id=memory.id,
                    role_id=memory.role_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    timestamp=memory.timestamp,
                    project_id=memory.project_id,
                    session_id=memory.session_id,
                    tags=memory.tags,
                    metadata=memory.metadata,
                    priority=memory.priority.name,
                    ttl=memory.ttl,
                ),
            )

        return ContextResponse(
            role_id=context.role_id,
            relevant_memories=relevant_memories,
            role_identity=context.role_identity,
            conversation_summary=context.conversation_summary,
            project_context=context.project_context,
            model_adaptation=context.model_adaptation,
        )

    except Exception as e:
        logging.error(f"构建上下文失败: {e}")
        raise HTTPException(status_code=500, detail=f"构建上下文失败: {e!s}")


@app.get("/performance/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    memory_service: LightweightMemoryService = Depends(get_memory_service),
):
    """获取性能指标"""
    try:
        metrics = memory_service.get_performance_metrics()
        return PerformanceMetricsResponse(**metrics)

    except Exception as e:
        logging.error(f"获取性能指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能指标失败: {e!s}")


@app.post("/cache/clear")
async def clear_cache(
    memory_service: LightweightMemoryService = Depends(get_memory_service),
):
    """清空缓存"""
    try:
        memory_service.clear_cache()
        return {"message": "缓存已清空"}

    except Exception as e:
        logging.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {e!s}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "lightweight_memory_service",
        "timestamp": datetime.now().isoformat(),
    }


# 启动函数
def start_lightweight_memory_api(host: str = "0.0.0.0", port: int = 8001):
    """启动轻量级记忆服务API"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_lightweight_memory_api()
