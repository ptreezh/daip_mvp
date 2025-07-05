"""协同文档分析API接口
提供RESTful API支持多角色协同文档分析功能
"""

from typing import Any, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from src.enhanced_collaborative_analysis import (
    AnalysisType,
    EnhancedCollaborativeAnalysis,
)


# 请求模型
class CreateAnalysisTaskRequest(BaseModel):
    document_name: str
    document_content: str
    analysis_type: str
    requester_id: str
    custom_requirements: list[str] = []


class AnalysisTaskResponse(BaseModel):
    task_id: str
    document_name: str
    analysis_type: str
    current_phase: str
    assigned_experts: int
    created_at: str
    estimated_completion: Optional[str]
    actual_completion: Optional[str]
    progress_percentage: float
    quality_metrics: dict[str, Any]
    collaboration_history: list[dict[str, Any]]


# 创建路由器
collaborative_analysis_router = APIRouter(
    prefix="/collaborative-analysis",
    tags=["collaborative-analysis"],
)

# 全局协同分析实例
collaborative_analysis = EnhancedCollaborativeAnalysis()


@collaborative_analysis_router.post("/tasks", response_model=dict[str, str])
async def create_analysis_task(request: CreateAnalysisTaskRequest):
    """创建协同分析任务"""
    try:
        # 转换分析类型
        analysis_type_map = {
            "financial_report": AnalysisType.FINANCIAL_REPORT,
            "legal_document": AnalysisType.LEGAL_DOCUMENT,
            "research_paper": AnalysisType.RESEARCH_PAPER,
            "technical_spec": AnalysisType.TECHNICAL_SPEC,
            "business_plan": AnalysisType.BUSINESS_PLAN,
            "policy_document": AnalysisType.POLICY_DOCUMENT,
            "general_analysis": AnalysisType.GENERAL_ANALYSIS,
        }

        analysis_type = analysis_type_map.get(
            request.analysis_type,
            AnalysisType.GENERAL_ANALYSIS,
        )

        task_id = collaborative_analysis.create_analysis_task(
            document_name=request.document_name,
            document_content=request.document_content,
            analysis_type=analysis_type,
            requester_id=request.requester_id,
            custom_requirements=request.custom_requirements,
        )

        return {"task_id": task_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@collaborative_analysis_router.post("/tasks/upload", response_model=dict[str, str])
async def create_analysis_task_from_file(
    file: UploadFile = File(...),
    analysis_type: str = Query("general_analysis"),
    requester_id: str = Query(...),
    custom_requirements: str = Query(""),
):
    """从上传文件创建协同分析任务"""
    try:
        # 读取文件内容
        file_content = await file.read()
        document_content = file_content.decode("utf-8", errors="ignore")

        # 解析自定义需求
        custom_req_list = [
            req.strip() for req in custom_requirements.split(",") if req.strip()
        ]

        # 转换分析类型
        analysis_type_map = {
            "financial_report": AnalysisType.FINANCIAL_REPORT,
            "legal_document": AnalysisType.LEGAL_DOCUMENT,
            "research_paper": AnalysisType.RESEARCH_PAPER,
            "technical_spec": AnalysisType.TECHNICAL_SPEC,
            "business_plan": AnalysisType.BUSINESS_PLAN,
            "policy_document": AnalysisType.POLICY_DOCUMENT,
            "general_analysis": AnalysisType.GENERAL_ANALYSIS,
        }

        analysis_type_enum = analysis_type_map.get(
            analysis_type,
            AnalysisType.GENERAL_ANALYSIS,
        )

        task_id = collaborative_analysis.create_analysis_task(
            document_name=file.filename or "uploaded_document",
            document_content=document_content,
            analysis_type=analysis_type_enum,
            requester_id=requester_id,
            custom_requirements=custom_req_list,
        )

        return {"task_id": task_id, "status": "created", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@collaborative_analysis_router.get(
    "/tasks/{task_id}",
    response_model=AnalysisTaskResponse,
)
async def get_analysis_task(task_id: str):
    """获取分析任务详情"""
    task_status = collaborative_analysis.get_task_status(task_id)

    if task_status.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Analysis task not found")

    return AnalysisTaskResponse(**task_status)


@collaborative_analysis_router.get("/tasks")
async def list_analysis_tasks(
    requester_id: Optional[str] = Query(None),
    analysis_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """列出分析任务"""
    tasks = []

    for task in collaborative_analysis.active_tasks.values():
        # 应用过滤条件
        if requester_id and task.requester_id != requester_id:
            continue
        if analysis_type and task.analysis_type.value != analysis_type:
            continue
        if status and task.current_phase.value != status:
            continue

        tasks.append(
            {
                "task_id": task.task_id,
                "document_name": task.document_name,
                "analysis_type": task.analysis_type.value,
                "current_phase": task.current_phase.value,
                "requester_id": task.requester_id,
                "assigned_experts": len(task.assigned_experts),
                "created_at": task.created_at,
                "estimated_completion": task.estimated_completion,
                "progress_percentage": collaborative_analysis._calculate_progress_percentage(
                    task,
                ),
            },
        )

    # 按创建时间排序
    tasks.sort(key=lambda x: x["created_at"], reverse=True)

    # 分页
    total = len(tasks)
    tasks = tasks[offset : offset + limit]

    return {"tasks": tasks, "total": total, "limit": limit, "offset": offset}


@collaborative_analysis_router.get("/tasks/{task_id}/results")
async def get_analysis_results(task_id: str):
    """获取分析结果"""
    if task_id not in collaborative_analysis.active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collaborative_analysis.active_tasks[task_id]

    return {
        "task_id": task_id,
        "analysis_results": task.analysis_results,
        "current_phase": task.current_phase.value,
        "completion_status": task.current_phase.value == "completed",
    }


@collaborative_analysis_router.get("/tasks/{task_id}/experts")
async def get_task_experts(task_id: str):
    """获取任务分配的专家"""
    if task_id not in collaborative_analysis.active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collaborative_analysis.active_tasks[task_id]
    assigned_experts = task.analysis_results.get("assigned_experts", [])

    return {
        "task_id": task_id,
        "assigned_experts": assigned_experts,
        "total_experts": len(assigned_experts),
    }


@collaborative_analysis_router.get("/tasks/{task_id}/collaboration-history")
async def get_collaboration_history(task_id: str, limit: int = Query(50, ge=1, le=200)):
    """获取协作历史"""
    if task_id not in collaborative_analysis.active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collaborative_analysis.active_tasks[task_id]

    # 获取最近的协作历史
    history = (
        task.collaboration_history[-limit:]
        if len(task.collaboration_history) > limit
        else task.collaboration_history
    )

    return {
        "task_id": task_id,
        "collaboration_history": history,
        "total_events": len(task.collaboration_history),
    }


@collaborative_analysis_router.get("/analysis-types")
async def get_available_analysis_types():
    """获取可用的分析类型"""
    return {
        "analysis_types": [
            {
                "value": "financial_report",
                "name": "财务报告分析",
                "description": "分析财务报表、投资报告等财务文档",
            },
            {
                "value": "legal_document",
                "name": "法律文档分析",
                "description": "分析合同、法规、法律意见书等法律文档",
            },
            {
                "value": "research_paper",
                "name": "学术论文分析",
                "description": "分析学术论文、研究报告等学术文档",
            },
            {
                "value": "technical_spec",
                "name": "技术规范分析",
                "description": "分析技术文档、系统规范等技术文档",
            },
            {
                "value": "business_plan",
                "name": "商业计划分析",
                "description": "分析商业计划书、市场分析报告等商业文档",
            },
            {
                "value": "policy_document",
                "name": "政策文档分析",
                "description": "分析政策文件、法规草案等政策文档",
            },
            {
                "value": "general_analysis",
                "name": "通用文档分析",
                "description": "适用于各种类型的文档分析",
            },
        ],
    }


@collaborative_analysis_router.get("/statistics")
async def get_analysis_statistics():
    """获取分析统计信息"""
    active_tasks = collaborative_analysis.active_tasks

    # 统计各种指标
    total_tasks = len(active_tasks)
    completed_tasks = len(
        [t for t in active_tasks.values() if t.current_phase.value == "completed"],
    )
    in_progress_tasks = total_tasks - completed_tasks

    # 按分析类型统计
    type_stats = {}
    for task in active_tasks.values():
        task_type = task.analysis_type.value
        type_stats[task_type] = type_stats.get(task_type, 0) + 1

    # 按阶段统计
    phase_stats = {}
    for task in active_tasks.values():
        phase = task.current_phase.value
        phase_stats[phase] = phase_stats.get(phase, 0) + 1

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
        "analysis_type_distribution": type_stats,
        "phase_distribution": phase_stats,
        "total_experts_involved": len(
            set(
                expert_id
                for task in active_tasks.values()
                for expert_id in task.assigned_experts
            ),
        ),
    }


@collaborative_analysis_router.delete("/tasks/{task_id}")
async def cancel_analysis_task(task_id: str):
    """取消分析任务"""
    if task_id not in collaborative_analysis.active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = collaborative_analysis.active_tasks[task_id]

    if task.current_phase.value == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed task")

    # 移除任务
    del collaborative_analysis.active_tasks[task_id]

    return {"status": "success", "message": "Task cancelled successfully"}
