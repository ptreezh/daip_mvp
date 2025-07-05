"""Wiki协同编辑API接口
提供RESTful API支持Wiki协同编辑功能
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.enhanced_wiki_collaboration import EnhancedWikiCollaboration, WikiPermission


# 请求模型
class CreateWikiEntryRequest(BaseModel):
    name: str
    initial_content: str
    creator_id: str
    category: str = "general"
    tags: list[str] = []


class EditWikiEntryRequest(BaseModel):
    entry_id: str
    new_content: str
    editor_id: str
    edit_summary: str = ""
    tags: list[str] = []


class ReviewEditRequest(BaseModel):
    entry_id: str
    edit_id: str
    reviewer_id: str
    decision: str  # approve, reject
    comments: str = ""


class ExpertRecommendationRequest(BaseModel):
    entry_name: str
    topic: str
    required_skills: list[str] = []
    max_experts: int = 5


class AssignRoleRequest(BaseModel):
    entry_id: str
    expert_id: str
    permissions: list[str]


# 响应模型
class WikiEntryResponse(BaseModel):
    entry_id: str
    name: str
    current_content: str
    current_version: int
    status: str
    tags: list[str]
    category: str
    collaboration_stats: dict[str, Any]


class ExpertRecommendationResponse(BaseModel):
    expert_id: str
    name: str
    title: str
    specialties: list[str]
    relevance_score: float
    reputation_score: float
    recommended_permissions: list[str]
    contribution_potential: float


# 创建路由器
wiki_router = APIRouter(prefix="/wiki", tags=["wiki-collaboration"])

# 全局Wiki协同编辑实例
wiki_collaboration = EnhancedWikiCollaboration()


@wiki_router.post("/entries", response_model=dict[str, str])
async def create_wiki_entry(request: CreateWikiEntryRequest):
    """创建新的Wiki条目"""
    try:
        entry_id = wiki_collaboration.create_wiki_entry(
            name=request.name,
            initial_content=request.initial_content,
            creator_id=request.creator_id,
            category=request.category,
            tags=request.tags,
        )
        return {"entry_id": entry_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@wiki_router.get("/entries/{entry_id}", response_model=WikiEntryResponse)
async def get_wiki_entry(entry_id: str):
    """获取Wiki条目详情"""
    if entry_id not in wiki_collaboration.wiki_entries:
        raise HTTPException(status_code=404, detail="Wiki entry not found")

    entry = wiki_collaboration.wiki_entries[entry_id]
    collaboration_stats = wiki_collaboration.get_collaboration_stats(entry_id)

    return WikiEntryResponse(
        entry_id=entry.entry_id,
        name=entry.name,
        current_content=entry.current_content,
        current_version=entry.current_version,
        status=entry.status,
        tags=entry.tags,
        category=entry.category,
        collaboration_stats=collaboration_stats,
    )


@wiki_router.put("/entries/edit")
async def edit_wiki_entry(request: EditWikiEntryRequest):
    """编辑Wiki条目"""
    success = wiki_collaboration.edit_wiki_entry(
        entry_id=request.entry_id,
        new_content=request.new_content,
        editor_id=request.editor_id,
        edit_summary=request.edit_summary,
        tags=request.tags,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to edit wiki entry")

    return {"status": "success", "message": "Wiki entry edited successfully"}


@wiki_router.post("/entries/review")
async def review_edit(request: ReviewEditRequest):
    """审核编辑"""
    success = wiki_collaboration.review_edit(
        entry_id=request.entry_id,
        edit_id=request.edit_id,
        reviewer_id=request.reviewer_id,
        decision=request.decision,
        comments=request.comments,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to review edit")

    return {"status": "success", "message": "Edit reviewed successfully"}


@wiki_router.get("/entries/{entry_id}/history")
async def get_edit_history(entry_id: str, limit: int = Query(20, ge=1, le=100)):
    """获取编辑历史"""
    history = wiki_collaboration.get_edit_history(entry_id, limit)
    return {"entry_id": entry_id, "edit_history": history}


@wiki_router.get("/entries/{entry_id}/stats")
async def get_collaboration_stats(entry_id: str):
    """获取协作统计信息"""
    stats = wiki_collaboration.get_collaboration_stats(entry_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Wiki entry not found")
    return stats


@wiki_router.post(
    "/recommend-experts",
    response_model=list[ExpertRecommendationResponse],
)
async def recommend_experts(request: ExpertRecommendationRequest):
    """推荐专家"""
    recommendations = wiki_collaboration.recommend_experts_for_entry(
        entry_name=request.entry_name,
        topic=request.topic,
        required_skills=request.required_skills,
        max_experts=request.max_experts,
    )

    return [
        ExpertRecommendationResponse(
            expert_id=rec["expert_id"],
            name=rec["name"],
            title=rec["title"],
            specialties=rec["specialties"],
            relevance_score=rec["relevance_score"],
            reputation_score=rec["reputation_score"],
            recommended_permissions=rec["recommended_permissions"],
            contribution_potential=rec["contribution_potential"],
        )
        for rec in recommendations
    ]


@wiki_router.post("/entries/assign-role")
async def assign_role_to_entry(request: AssignRoleRequest):
    """为条目分配专家角色"""
    # 转换权限字符串为枚举
    try:
        permissions = [WikiPermission(p) for p in request.permissions]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid permission: {e}")

    success = wiki_collaboration.assign_role_to_entry(
        entry_id=request.entry_id,
        expert_id=request.expert_id,
        permissions=permissions,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign role")

    return {"status": "success", "message": "Role assigned successfully"}


@wiki_router.get("/entries/{entry_id}/workflow")
async def get_recommended_workflow(entry_id: str, topic: str = Query(...)):
    """获取推荐的协作工作流"""
    if entry_id not in wiki_collaboration.wiki_entries:
        raise HTTPException(status_code=404, detail="Wiki entry not found")

    entry = wiki_collaboration.wiki_entries[entry_id]
    workflow = wiki_collaboration.get_recommended_workflow(entry.name, topic)

    return workflow


@wiki_router.get("/entries")
async def list_wiki_entries(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """列出Wiki条目"""
    entries = []

    for entry in wiki_collaboration.wiki_entries.values():
        # 应用过滤条件
        if category and entry.category != category:
            continue
        if tag and tag not in entry.tags:
            continue

        entries.append(
            {
                "entry_id": entry.entry_id,
                "name": entry.name,
                "category": entry.category,
                "tags": entry.tags,
                "current_version": entry.current_version,
                "last_modified": entry.last_modified,
                "last_editor": entry.last_editor,
                "status": entry.status,
            },
        )

    # 分页
    total = len(entries)
    entries = entries[offset : offset + limit]

    return {"entries": entries, "total": total, "limit": limit, "offset": offset}


@wiki_router.get("/permissions")
async def get_available_permissions():
    """获取可用的权限列表"""
    return {
        "permissions": [
            {
                "value": perm.value,
                "name": perm.name,
                "description": _get_permission_description(perm),
            }
            for perm in WikiPermission
        ],
    }


def _get_permission_description(permission: WikiPermission) -> str:
    """获取权限描述"""
    descriptions = {
        WikiPermission.READ: "查看Wiki条目内容",
        WikiPermission.COMMENT: "添加评论和讨论",
        WikiPermission.EDIT: "编辑Wiki条目内容",
        WikiPermission.REVIEW: "审核其他用户的编辑",
        WikiPermission.ADMIN: "管理Wiki条目和用户权限",
    }
    return descriptions.get(permission, "未知权限")
