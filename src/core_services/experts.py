from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.core.services.expert_service import ExpertService, get_expert_service

router = APIRouter()


@router.get("/", summary="List all experts with filtering")
async def list_experts(
    category: Optional[str] = Query(None, description="Filter by category"),
    availability: Optional[str] = Query(None, description="Filter by availability"),
    search: Optional[str] = Query(None, description="Search by keyword in name or description"),
    expert_service: ExpertService = Depends(get_expert_service),
):
    """Retrieves a list of experts, with optional filters for category, availability, and a search term.
    """
    experts = expert_service.get_experts(category, availability, search)
    return {
        "experts": experts,
        "total": len(experts),
        "categories": list(expert_service.get_categories().keys()),
    }


@router.get("/{expert_id}", summary="Get expert details")
async def get_expert(
    expert_id: str, expert_service: ExpertService = Depends(get_expert_service)
):
    """Retrieves the detailed information for a specific expert by their ID.
    """
    expert = expert_service.get_expert_by_id(expert_id)
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")
    return expert


@router.get("/categories", summary="Get all expert categories")
async def get_expert_categories(expert_service: ExpertService = Depends(get_expert_service)):
    """Retrieves a list of all available expert categories.
    """
    return {"categories": expert_service.get_categories()}


@router.post("/search", summary="Search for experts by vector similarity")
async def search_experts_by_vector(
    query: str, top_k: int = 5, expert_service: ExpertService = Depends(get_expert_service)
):
    """Performs a semantic search for the most relevant experts based on a query string.
    """
    results = expert_service.search_experts_by_vector(query, top_k)
    return {"query": query, "results": results}