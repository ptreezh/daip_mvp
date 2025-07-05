"""专家库管理API接口
提供RESTful API支持专家库管理功能
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.enhanced_recommendation_engine import EnhancedRecommendationEngine
from src.expert_library import ExpertLibrary


# 请求模型
class CreateExpertRequest(BaseModel):
    expert_id: str
    name: str
    title: str
    specialties: list[str]
    description: str
    category: str = "general"
    tags: list[str] = []


class UpdateExpertRequest(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    specialties: Optional[list[str]] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None


class ExpertRecommendationRequest(BaseModel):
    task_description: str
    required_skills: list[str]
    max_experts: int = 3
    category: Optional[str] = None


# 创建路由器 - 修复路由前缀
expert_router = APIRouter(prefix="/experts", tags=["experts"])

# 全局专家库实例
expert_library = ExpertLibrary()
# 全局增强推荐引擎实例
recommendation_engine = EnhancedRecommendationEngine(expert_library)


@expert_router.get("/categories")
async def get_categories():
    """获取专家分类"""
    try:
        categories = expert_library.get_categories()
        return {"success": True, "categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.get("/statistics")
async def get_statistics():
    """获取专家库统计信息"""
    try:
        stats = expert_library.get_statistics()
        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.get("/")
async def get_experts(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
):
    """获取专家列表"""
    try:
        # 处理category可能为None的情况
        experts = expert_library.get_all_experts(category=category if category else "")

        # 应用搜索过滤
        if search:
            search_lower = search.lower()
            experts = [
                e
                for e in experts
                if search_lower in e.get("name", "").lower()
                or search_lower in e.get("title", "").lower()
                or search_lower in " ".join(e.get("specialties", [])).lower()
            ]

        # 分页
        total = len(experts)
        experts = experts[offset : offset + limit]

        return {"experts": experts, "total": total, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.post("/recommend")
async def recommend_experts(request: ExpertRecommendationRequest):
    """基于语义分数的智能专家推荐（Ollama本地嵌入式模型）"""
    try:
        # 构建查询文本
        query_text = (
            request.task_description.strip()
            + " "
            + " ".join(request.required_skills or [])
        )
        top_k = request.max_experts if request.max_experts else 5
        # 语义检索
        similar_experts = recommendation_engine.vector_store.find_similar_experts(
            query_text,
            top_k=top_k,
        )
        recommended = []
        for expert_id, semantic_score in similar_experts:
            expert = expert_library.get_expert_by_id(expert_id)
            if expert:
                recommended.append({"expert": expert, "semantic_score": semantic_score})
        return {
            "success": True,
            "recommended_experts": recommended,
            "total_candidates": len(expert_library.experts),
        }
    except Exception as e:
        logging.error(f"专家推荐失败: {e!s}")
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.get("/{expert_id}")
async def get_expert(expert_id: str):
    """获取专家详情"""
    try:
        expert = expert_library.get_expert_by_id(expert_id)
        if not expert:
            raise HTTPException(status_code=404, detail="专家不存在")
        return {"success": True, "expert": expert}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.post("/")
async def create_expert(request: CreateExpertRequest):
    """创建新专家"""
    try:
        expert_data = {
            "expert_id": request.expert_id,
            "name": request.name,
            "title": request.title,
            "specialties": request.specialties,
            "description": request.description,
            "category": request.category,
            "tags": request.tags,
        }

        expert_id = expert_library.add_expert_manually(expert_data)
        if not expert_id:
            raise HTTPException(status_code=400, detail="创建专家失败")

        return {"success": True, "message": "专家创建成功", "expert_id": expert_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.put("/{expert_id}")
async def update_expert(expert_id: str, request: UpdateExpertRequest):
    """更新专家信息"""
    try:
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.title is not None:
            update_data["title"] = request.title
        if request.specialties is not None:
            update_data["specialties"] = request.specialties
        if request.description is not None:
            update_data["description"] = request.description
        if request.category is not None:
            update_data["category"] = request.category
        if request.tags is not None:
            update_data["tags"] = request.tags

        success = expert_library.update_expert(expert_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="专家不存在")

        return {"success": True, "message": "专家信息更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@expert_router.delete("/{expert_id}")
async def delete_expert(expert_id: str):
    """删除专家"""
    try:
        success = expert_library.delete_expert(expert_id)
        if not success:
            raise HTTPException(status_code=404, detail="专家不存在")

        return {"success": True, "message": "专家删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 兼容性路由 - 保持原有的expert_library前缀
expert_library_router = APIRouter(prefix="/expert_library", tags=["expert_library"])


@expert_library_router.get("/experts")
async def get_experts_compat(
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
):
    """兼容性接口：获取专家列表"""
    return await get_experts(category, limit, offset, search)


@expert_library_router.post("/experts/recommend")
async def recommend_experts_compat(request: ExpertRecommendationRequest):
    """兼容性接口：智能专家推荐"""
    return await recommend_experts(request)


@expert_library_router.get("/experts/{expert_id}")
async def get_expert_compat(expert_id: str):
    """兼容性接口：获取专家详情"""
    return await get_expert(expert_id)
