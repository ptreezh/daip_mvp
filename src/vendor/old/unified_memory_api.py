"""统一记忆服务API接口
提供RESTful API接口，整合两套记忆系统
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.multi_model_adapter import MultiModelManager
from src.opinion_collision_engine import (
    OpinionCollisionEngine,
)
from src.role_memory_bank import RoleMemoryBank
from src.unified_memory_service import (
    MemoryValidationLevel,
    UnifiedMemoryService,
)


# Pydantic模型定义
class MemoryRequest(BaseModel):
    """记忆请求"""

    role_id: str
    content: str
    memory_type: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    validation_level: str = "basic"
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class MemoryResponse(BaseModel):
    """记忆响应"""

    memory_id: str
    role_id: str
    content: str
    memory_type: str
    importance: float
    confidence: float
    validation_level: str
    system_type: str
    timestamp: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}
    cross_model_validation: Optional[dict[str, Any]] = None
    consensus_data: Optional[dict[str, Any]] = None


class ContextRequest(BaseModel):
    """上下文请求"""

    role_id: str
    current_question: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    target_model: str = "ollama"
    conversation_history: Optional[list[dict[str, str]]] = None


class ContextResponse(BaseModel):
    """上下文响应"""

    role_identity: Optional[dict[str, Any]] = None
    relevant_memories: list[dict[str, Any]] = []
    project_context: Optional[dict[str, Any]] = None
    conversation_summary: str = ""
    prompt: str = ""
    model_adaptation: dict[str, Any] = {}


class CrossModelValidationRequest(BaseModel):
    """跨模型验证请求"""

    content: str
    models: Optional[list[str]] = None
    validation_type: str = "comprehensive"


class CrossModelValidationResponse(BaseModel):
    """跨模型验证响应"""

    validation_id: str
    content: str
    models_used: list[str]
    agreement_scores: dict[str, float]
    confidence_distribution: dict[str, float]
    uncertainty_metrics: dict[str, float]
    hallucination_detection: dict[str, bool]
    consensus_result: str
    timestamp: str
    metadata: dict[str, Any] = {}


class OpinionCollisionRequest(BaseModel):
    """观点碰撞请求"""

    content: str
    participants: list[str]
    opinions: dict[str, str]
    confidence_scores: dict[str, float]
    evidence_sources: Optional[dict[str, list[str]]] = None


class OpinionCollisionResponse(BaseModel):
    """观点碰撞响应"""

    collision_id: str
    content: str
    participants: list[str]
    collision_type: str
    conflicting_opinions: dict[str, str]
    confidence_scores: dict[str, float]
    evidence_sources: dict[str, list[str]]
    timestamp: str
    resolution_strategy: str
    resolution_result: Optional[str] = None
    consensus_score: Optional[float] = None
    metadata: dict[str, Any] = {}


class CrossModelAnalysisRequest(BaseModel):
    """跨模型分析请求"""

    content: str
    models: Optional[list[str]] = None
    analysis_depth: str = "standard"


class CrossModelAnalysisResponse(BaseModel):
    """跨模型分析响应"""

    analysis_id: str
    content: str
    models_used: list[str]
    model_opinions: dict[str, str]
    agreement_matrix: list[list[float]]
    disagreement_points: list[str]
    consensus_confidence: float
    uncertainty_metrics: dict[str, float]
    analysis_timestamp: str
    metadata: dict[str, Any] = {}


class ConsensusRequest(BaseModel):
    """共识请求"""

    collision_id: str
    resolution_preferences: Optional[dict[str, Any]] = None


class ConsensusResponse(BaseModel):
    """共识响应"""

    consensus_id: str
    collision_id: str
    final_opinion: str
    agreement_score: float
    participant_weights: dict[str, float]
    evidence_strength: float
    blockchain_verified: bool
    consensus_timestamp: str
    resolution_details: dict[str, Any] = {}


class MemoryQueryRequest(BaseModel):
    """记忆查询请求"""

    role_id: str
    memory_type: Optional[str] = None
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    validation_level: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)


class MemoryStatisticsResponse(BaseModel):
    """记忆统计响应"""

    total_memories: int
    resolved_collisions: int
    collision_types: dict[str, int]
    resolution_strategies: dict[str, int]
    average_consensus_score: float
    total_analyses: int
    total_consensus: int
    system_performance: dict[str, Any] = {}


# 全局服务实例
memory_service: Optional[UnifiedMemoryService] = None
collision_engine: Optional[OpinionCollisionEngine] = None
model_manager: Optional[MultiModelManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global memory_service, collision_engine, model_manager

    # 启动时初始化服务
    try:
        # 初始化角色记忆银行
        role_memory_bank = RoleMemoryBank("data/unified_memory/role_memory")

        # 初始化多模型管理器
        model_manager = MultiModelManager(role_memory_bank)

        # 设置默认模型
        try:
            model_manager.setup_ollama(is_default=True)
        except Exception as e:
            logging.warning(f"Ollama设置失败: {e}")

        # 初始化统一记忆服务
        memory_service = UnifiedMemoryService("data/unified_memory")

        # 初始化观点碰撞引擎
        collision_engine = OpinionCollisionEngine(memory_service, model_manager)

        logging.info("统一记忆服务API初始化完成")

    except Exception as e:
        logging.error(f"统一记忆服务API初始化失败: {e}")
        raise

    yield

    # 关闭时清理资源
    try:
        if memory_service:
            memory_service.close()
        logging.info("统一记忆服务API已关闭")
    except Exception as e:
        logging.error(f"统一记忆服务API关闭失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="统一记忆服务API",
    description="整合两套记忆系统，实现跨模型记忆适配和多模型交叉验证",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 依赖注入
def get_memory_service() -> UnifiedMemoryService:
    if not memory_service:
        raise HTTPException(status_code=503, detail="记忆服务未初始化")
    return memory_service


def get_collision_engine() -> OpinionCollisionEngine:
    if not collision_engine:
        raise HTTPException(status_code=503, detail="碰撞引擎未初始化")
    return collision_engine


def get_model_manager() -> MultiModelManager:
    if not model_manager:
        raise HTTPException(status_code=503, detail="模型管理器未初始化")
    return model_manager


# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "统一记忆服务API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查服务状态
        services_status = {
            "memory_service": memory_service is not None,
            "collision_engine": collision_engine is not None,
            "model_manager": model_manager is not None,
        }

        # 检查可用模型
        available_models = []
        if model_manager:
            available_models = model_manager.get_available_models()

        return {
            "status": "healthy",
            "services": services_status,
            "available_models": available_models,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"健康检查失败: {e!s}")


@app.post("/memory/add", response_model=MemoryResponse)
async def add_memory(
    request: MemoryRequest,
    background_tasks: BackgroundTasks,
    memory_service: UnifiedMemoryService = Depends(get_memory_service),
):
    """添加记忆"""
    try:
        # 转换验证级别
        validation_level = MemoryValidationLevel(request.validation_level)

        # 添加记忆
        memory_id = await memory_service.add_memory(
            role_id=request.role_id,
            content=request.content,
            memory_type=request.memory_type,
            importance=request.importance,
            confidence=request.confidence,
            validation_level=validation_level,
            project_id=request.project_id,
            session_id=request.session_id,
            tags=request.tags,
            metadata=request.metadata,
        )

        # 获取添加的记忆
        memories = await memory_service.get_memories(role_id=request.role_id, limit=1)

        if not memories:
            raise HTTPException(status_code=500, detail="记忆添加失败")

        memory = memories[0]

        # 后台任务：跨模型验证
        if validation_level in [
            MemoryValidationLevel.CROSS_MODEL,
            MemoryValidationLevel.CONSENSUS,
        ]:
            background_tasks.add_task(
                memory_service.cross_model_validate,
                request.content,
                None,
            )

        return MemoryResponse(
            memory_id=memory.id,
            role_id=memory.role_id,
            content=memory.content,
            memory_type=memory.memory_type,
            importance=memory.importance,
            confidence=memory.confidence,
            validation_level=memory.validation_level.value,
            system_type=memory.system_type.value,
            timestamp=memory.timestamp,
            project_id=memory.project_id,
            session_id=memory.session_id,
            tags=memory.tags,
            metadata=memory.metadata,
            cross_model_validation=memory.cross_model_validation,
            consensus_data=memory.consensus_data,
        )

    except Exception as e:
        logging.error(f"添加记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加记忆失败: {e!s}")


@app.post("/memory/query", response_model=list[MemoryResponse])
async def query_memories(
    request: MemoryQueryRequest,
    memory_service: UnifiedMemoryService = Depends(get_memory_service),
):
    """查询记忆"""
    try:
        # 转换验证级别
        validation_level = None
        if request.validation_level:
            validation_level = MemoryValidationLevel(request.validation_level)

        # 查询记忆
        memories = await memory_service.get_memories(
            role_id=request.role_id,
            memory_type=request.memory_type,
            project_id=request.project_id,
            session_id=request.session_id,
            validation_level=validation_level,
            limit=request.limit,
            min_importance=request.min_importance,
        )

        # 转换为响应格式
        response_memories = []
        for memory in memories:
            response_memories.append(
                MemoryResponse(
                    memory_id=memory.id,
                    role_id=memory.role_id,
                    content=memory.content,
                    memory_type=memory.memory_type,
                    importance=memory.importance,
                    confidence=memory.confidence,
                    validation_level=memory.validation_level.value,
                    system_type=memory.system_type.value,
                    timestamp=memory.timestamp,
                    project_id=memory.project_id,
                    session_id=memory.session_id,
                    tags=memory.tags,
                    metadata=memory.metadata,
                    cross_model_validation=memory.cross_model_validation,
                    consensus_data=memory.consensus_data,
                ),
            )

        return response_memories

    except Exception as e:
        logging.error(f"查询记忆失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询记忆失败: {e!s}")


@app.post("/context/build", response_model=ContextResponse)
async def build_context(
    request: ContextRequest,
    memory_service: UnifiedMemoryService = Depends(get_memory_service),
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

        return ContextResponse(
            role_identity=context.get("role_identity"),
            relevant_memories=context.get("relevant_memories", []),
            project_context=context.get("project_context"),
            conversation_summary=context.get("conversation_summary", ""),
            prompt=context.get("prompt", ""),
            model_adaptation=context.get("model_adaptation", {}),
        )

    except Exception as e:
        logging.error(f"构建上下文失败: {e}")
        raise HTTPException(status_code=500, detail=f"构建上下文失败: {e!s}")


@app.post("/validation/cross-model", response_model=CrossModelValidationResponse)
async def cross_model_validation(
    request: CrossModelValidationRequest,
    memory_service: UnifiedMemoryService = Depends(get_memory_service),
):
    """跨模型验证"""
    try:
        # 执行跨模型验证
        validation_result = await memory_service.cross_model_validate(
            content=request.content,
            models=request.models,
        )

        return CrossModelValidationResponse(
            validation_id=validation_result.validation_id,
            content=validation_result.content,
            models_used=validation_result.models_used,
            agreement_scores=validation_result.agreement_scores,
            confidence_distribution=validation_result.confidence_distribution,
            uncertainty_metrics=validation_result.uncertainty_metrics,
            hallucination_detection=validation_result.hallucination_detection,
            consensus_result=validation_result.consensus_result,
            timestamp=validation_result.timestamp,
            metadata=validation_result.metadata or {},
        )

    except Exception as e:
        logging.error(f"跨模型验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"跨模型验证失败: {e!s}")


@app.post("/collision/detect", response_model=OpinionCollisionResponse)
async def detect_collision(
    request: OpinionCollisionRequest,
    collision_engine: OpinionCollisionEngine = Depends(get_collision_engine),
):
    """检测观点碰撞"""
    try:
        # 检测碰撞
        collision = await collision_engine.detect_collision(
            content=request.content,
            participants=request.participants,
            opinions=request.opinions,
            confidence_scores=request.confidence_scores,
            evidence_sources=request.evidence_sources,
        )

        if not collision:
            raise HTTPException(status_code=404, detail="未检测到观点碰撞")

        return OpinionCollisionResponse(
            collision_id=collision.collision_id,
            content=collision.content,
            participants=collision.participants,
            collision_type=collision.collision_type.value,
            conflicting_opinions=collision.conflicting_opinions,
            confidence_scores=collision.confidence_scores,
            evidence_sources=collision.evidence_sources,
            timestamp=collision.timestamp,
            resolution_strategy=collision.resolution_strategy.value,
            resolution_result=collision.resolution_result,
            consensus_score=collision.consensus_score,
            metadata=collision.metadata or {},
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"检测观点碰撞失败: {e}")
        raise HTTPException(status_code=500, detail=f"检测观点碰撞失败: {e!s}")


@app.post("/analysis/cross-model", response_model=CrossModelAnalysisResponse)
async def cross_model_analysis(
    request: CrossModelAnalysisRequest,
    collision_engine: OpinionCollisionEngine = Depends(get_collision_engine),
):
    """跨模型分析"""
    try:
        # 执行跨模型分析
        analysis_result = await collision_engine.cross_model_analyze(
            content=request.content,
            models=request.models,
        )

        return CrossModelAnalysisResponse(
            analysis_id=analysis_result.analysis_id,
            content=analysis_result.content,
            models_used=analysis_result.models_used,
            model_opinions=analysis_result.model_opinions,
            agreement_matrix=analysis_result.agreement_matrix,
            disagreement_points=analysis_result.disagreement_points,
            consensus_confidence=analysis_result.consensus_confidence,
            uncertainty_metrics=analysis_result.uncertainty_metrics,
            analysis_timestamp=analysis_result.analysis_timestamp,
            metadata=analysis_result.metadata or {},
        )

    except Exception as e:
        logging.error(f"跨模型分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"跨模型分析失败: {e!s}")


@app.post("/consensus/resolve", response_model=ConsensusResponse)
async def resolve_consensus(
    request: ConsensusRequest,
    collision_engine: OpinionCollisionEngine = Depends(get_collision_engine),
):
    """解决共识"""
    try:
        # 获取碰撞
        collision = collision_engine.collision_cache.get(request.collision_id)
        if not collision:
            raise HTTPException(status_code=404, detail="碰撞不存在")

        # 解决碰撞
        consensus_result = await collision_engine.resolve_collision(collision)

        return ConsensusResponse(
            consensus_id=consensus_result.consensus_id,
            collision_id=consensus_result.collision_id,
            final_opinion=consensus_result.final_opinion,
            agreement_score=consensus_result.agreement_score,
            participant_weights=consensus_result.participant_weights,
            evidence_strength=consensus_result.evidence_strength,
            blockchain_verified=consensus_result.blockchain_verified,
            consensus_timestamp=consensus_result.consensus_timestamp,
            resolution_details=consensus_result.resolution_details or {},
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"解决共识失败: {e}")
        raise HTTPException(status_code=500, detail=f"解决共识失败: {e!s}")


@app.get("/statistics", response_model=MemoryStatisticsResponse)
async def get_statistics(
    collision_engine: OpinionCollisionEngine = Depends(get_collision_engine),
):
    """获取统计信息"""
    try:
        stats = collision_engine.get_collision_statistics()

        return MemoryStatisticsResponse(
            total_memories=stats.get("total_memories", 0),
            resolved_collisions=stats.get("resolved_collisions", 0),
            collision_types=stats.get("collision_types", {}),
            resolution_strategies=stats.get("resolution_strategies", {}),
            average_consensus_score=stats.get("average_consensus_score", 0.0),
            total_analyses=stats.get("total_analyses", 0),
            total_consensus=stats.get("total_consensus", 0),
            system_performance={
                "uptime": "running",
                "last_update": datetime.now().isoformat(),
            },
        )

    except Exception as e:
        logging.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {e!s}")


@app.get("/models/available")
async def get_available_models(
    model_manager: MultiModelManager = Depends(get_model_manager),
):
    """获取可用模型"""
    try:
        available_models = model_manager.get_available_models()
        working_models = model_manager.get_working_models()
        adapter_status = model_manager.get_adapter_status()

        return {
            "available_models": available_models,
            "working_models": working_models,
            "adapter_status": adapter_status,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logging.error(f"获取可用模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取可用模型失败: {e!s}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
