"""区块链共识系统API接口
提供RESTful API支持区块链共识功能
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from src.blockchain_consensus import ConsensusAlgorithm
from src.consensus_role_integration import ConsensusRoleIntegration


# 请求模型
class CreateConsensusSessionRequest(BaseModel):
    topic: str
    description: str
    algorithm: str = "proof_of_authority"
    required_expertise: list[str] = []
    max_participants: int = 10


class SubmitOpinionRequest(BaseModel):
    session_id: str
    expert_id: str
    content: str
    confidence: float
    supporting_evidence: list[str] = []


class RunConsensusRequest(BaseModel):
    session_id: str


class RegisterExpertRequest(BaseModel):
    session_id: str
    expert_id: str
    name: str
    category: str
    reputation_score: float
    stake_weight: float
    authority_level: int
    specialties: list[str] = []


# 响应模型
class ConsensusSessionResponse(BaseModel):
    session_id: str
    topic: str
    description: str
    algorithm: str
    status: str
    participants: list[dict[str, Any]]
    total_participants: int
    submitted_opinions: int
    created_at: str
    completed_at: Optional[str] = None
    consensus_result: Optional[dict[str, Any]] = None


class ExpertHistoryResponse(BaseModel):
    session_id: str
    topic: str
    status: str
    created_at: str
    completed_at: Optional[str]
    algorithm: str
    consensus_achieved: bool


# 创建路由器
consensus_router = APIRouter(prefix="/consensus", tags=["blockchain-consensus"])

# 全局共识集成实例
consensus_integration = ConsensusRoleIntegration()


@consensus_router.post("/sessions", response_model=dict[str, str])
async def create_consensus_session(request: CreateConsensusSessionRequest):
    """创建共识会话"""
    try:
        # 转换算法枚举
        algorithm_map = {
            "proof_of_authority": ConsensusAlgorithm.PROOF_OF_AUTHORITY,
            "proof_of_stake": ConsensusAlgorithm.PROOF_OF_STAKE,
            "delegated_proof_of_stake": ConsensusAlgorithm.DELEGATED_PROOF_OF_STAKE,
            "pbft": ConsensusAlgorithm.PRACTICAL_BYZANTINE_FAULT_TOLERANCE,
        }

        algorithm = algorithm_map.get(
            request.algorithm,
            ConsensusAlgorithm.PROOF_OF_AUTHORITY,
        )

        session_id = consensus_integration.create_consensus_session(
            topic=request.topic,
            description=request.description,
            algorithm=algorithm,
            required_expertise=request.required_expertise,
            max_participants=request.max_participants,
        )

        return {"session_id": session_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@consensus_router.get("/sessions/{session_id}", response_model=ConsensusSessionResponse)
async def get_consensus_session(session_id: str):
    """获取共识会话详情"""
    session_info = consensus_integration.get_session_status(session_id)

    if session_info.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Consensus session not found")

    return ConsensusSessionResponse(**session_info)


@consensus_router.post("/register_expert")
async def register_expert(request: RegisterExpertRequest):
    """注册专家到共识系统"""
    try:
        consensus_integration.register_expert_to_session(
            session_id=request.session_id,
            expert_id=request.expert_id,
            name=request.name,
            category=request.category,
            reputation_score=request.reputation_score,
            stake_weight=request.stake_weight,
            authority_level=request.authority_level,
            specialties=request.specialties or [],
        )
        return {"status": "success", "message": "Expert registered successfully"}
    except ValueError as ve:
        msg = str(ve)
        if "Session not found" in msg:
            return {
                "status": "error",
                "code": "SESSION_NOT_FOUND",
                "message": msg,
            }, status.HTTP_404_NOT_FOUND
        if "Expert already registered" in msg:
            return {
                "status": "error",
                "code": "EXPERT_ALREADY_REGISTERED",
                "message": msg,
            }, status.HTTP_409_CONFLICT
        return {
            "status": "error",
            "code": "REGISTER_FAILED",
            "message": msg,
        }, status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return {
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": str(e),
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


@consensus_router.post("/submit_opinion")
async def submit_opinion_v2(request: SubmitOpinionRequest):
    """提交专家意见（推荐新路径）"""
    try:
        success = consensus_integration.submit_expert_opinion(
            session_id=request.session_id,
            expert_id=request.expert_id,
            content=request.content,
            confidence=request.confidence,
            supporting_evidence=request.supporting_evidence,
        )
        if not success:
            return {
                "status": "error",
                "code": "SUBMIT_FAILED",
                "message": "Failed to submit opinion",
            }, status.HTTP_400_BAD_REQUEST
        return {"status": "success", "message": "Opinion submitted successfully"}
    except Exception as e:
        return {
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": str(e),
        }, status.HTTP_500_INTERNAL_SERVER_ERROR


# 兼容旧路径
@consensus_router.post("/opinions")
async def submit_opinion_legacy(request: SubmitOpinionRequest):
    return await submit_opinion_v2(request)


@consensus_router.post("/sessions/{session_id}/run")
async def run_consensus(session_id: str):
    """运行共识算法"""
    result = consensus_integration.run_consensus(session_id)

    if result.get("status") == "error":
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Consensus failed"),
        )

    return result


@consensus_router.get(
    "/experts/{expert_id}/history",
    response_model=list[ExpertHistoryResponse],
)
async def get_expert_consensus_history(expert_id: str):
    """获取专家的共识参与历史"""
    history = consensus_integration.get_expert_consensus_history(expert_id)

    return [
        ExpertHistoryResponse(
            session_id=item["session_id"],
            topic=item["topic"],
            status=item["status"],
            created_at=item["created_at"],
            completed_at=item["completed_at"],
            algorithm=item["algorithm"],
            consensus_achieved=item["consensus_achieved"],
        )
        for item in history
    ]


@consensus_router.get("/sessions")
async def list_consensus_sessions(
    status: Optional[str] = Query(None),
    algorithm: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """列出共识会话"""
    # 获取所有活跃会话
    sessions = []
    for session in consensus_integration.active_sessions.values():
        # 应用过滤条件
        if status and session.status != status:
            continue
        if algorithm and session.algorithm.value != algorithm:
            continue

        sessions.append(
            {
                "session_id": session.session_id,
                "topic": session.topic,
                "description": session.description,
                "algorithm": session.algorithm.value,
                "status": session.status,
                "participants_count": len(session.participants),
                "created_at": session.created_at,
                "completed_at": session.completed_at,
            },
        )

    # 分页
    total = len(sessions)
    sessions = sessions[offset : offset + limit]

    return {"sessions": sessions, "total": total, "limit": limit, "offset": offset}


@consensus_router.get("/statistics")
async def get_consensus_statistics():
    """获取共识统计信息"""
    stats = consensus_integration.get_consensus_statistics()
    return stats


@consensus_router.get("/algorithms")
async def get_available_algorithms():
    """获取可用的共识算法"""
    return {
        "algorithms": [
            {
                "value": "proof_of_authority",
                "name": "权威证明 (PoA)",
                "description": "基于专家权威等级和声誉分数的共识算法",
            },
            {
                "value": "proof_of_stake",
                "name": "权益证明 (PoS)",
                "description": "基于专家权益权重的投票共识算法",
            },
            {
                "value": "delegated_proof_of_stake",
                "name": "委托权益证明 (DPoS)",
                "description": "选择权益最高的专家作为代表的共识算法",
            },
            {
                "value": "pbft",
                "name": "实用拜占庭容错 (PBFT)",
                "description": "能够容忍1/3恶意节点的强一致性算法",
            },
        ],
    }


@consensus_router.post("/sessions/{session_id}/cancel")
async def cancel_consensus_session(session_id: str):
    """取消共识会话"""
    if session_id not in consensus_integration.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = consensus_integration.active_sessions[session_id]
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Session is not active")

    session.status = "cancelled"
    consensus_integration._save_session(session)

    return {"status": "success", "message": "Session cancelled successfully"}


@consensus_router.get("/sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """获取会话参与者详情"""
    session_info = consensus_integration.get_session_status(session_id)

    if session_info.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "participants": session_info["participants"],
        "total_participants": session_info["total_participants"],
        "submitted_opinions": session_info["submitted_opinions"],
    }


@consensus_router.post("/sync-experts")
async def sync_experts():
    """手动同步专家库到区块链系统"""
    try:
        consensus_integration._sync_experts_to_blockchain()
        return {"status": "success", "message": "Experts synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync experts: {e!s}")


@consensus_router.get("/blockchain/status")
async def get_blockchain_status():
    """获取区块链状态"""
    blockchain = consensus_integration.consensus_engine.blockchain

    return {
        "total_blocks": len(blockchain),
        "latest_block_hash": blockchain[-1].hash if blockchain else None,
        "registered_experts": len(consensus_integration.consensus_engine.experts),
        "pending_opinions": len(
            consensus_integration.consensus_engine.pending_opinions,
        ),
        "consensus_threshold": consensus_integration.consensus_engine.consensus_threshold,
        "min_validators": consensus_integration.consensus_engine.min_validators,
    }


@consensus_router.post("/rooms")
def create_consensus_room():
    return {"success": True, "room_id": "mock_consensus_room_id"}
