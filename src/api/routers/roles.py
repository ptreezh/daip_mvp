import logging
import os
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import AppStateDep, get_expert_service
from src.models import (
    BatchRoleImportRequest,
    Role,
    SmartRoleCreateRequest,
)
from src.core_services.expert_service import ExpertService

try:
    from src.role_utils import analyze_role_definition, standardize_role_dict
    ROLE_UTILS_AVAILABLE = True
except ImportError:
    ROLE_UTILS_AVAILABLE = False

router = APIRouter(
    prefix="/roles",
    tags=["Role & Expert Management"],
)

logger = logging.getLogger(__name__)


@router.get("/", response_model=dict[str, list[str]])
async def get_roles(expert_service: ExpertService = Depends(get_expert_service)):
    """Get a list of all available roles."""
    all_experts = expert_service.get_all_experts()
    return {"roles": sorted([expert.name for expert in all_experts])}


@router.post("/create", response_model=Role)
async def create_role(role: Role, expert_service: ExpertService = Depends(get_expert_service)):
    """Create and save a new role."""
    if not ROLE_UTILS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Role utils are not available.")

    try:
        standardized_role = standardize_role_dict(role.dict())
        # The service handles checking for existing roles.
        new_expert = expert_service.create_expert(standardized_role)
        return Role(**new_expert.to_dict())
    except ValueError as e:
        # Handle specific error for existing role
        logger.warning(f"Attempted to create an existing role: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while creating role.")

@router.post("/create_smart", response_model=dict[str, Any])
async def create_smart_role(
    request: SmartRoleCreateRequest,
    expert_service: ExpertService = Depends(get_expert_service),
):
    """Intelligently create and standardize a role from a definition."""
    if not ROLE_UTILS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Role utils are not available.")

    try:
        analysis_result = analyze_role_definition(request.role_name, request.role_definition)

        role_data = {
            "name": request.role_name,
            "description": request.role_definition,
            "category": request.category,
            "specialties": request.specialties or analysis_result.get("specialties", []),
            "skills": request.skills or analysis_result.get("skills", []),
            # other fields...
        }

        standardized_role_data = standardize_role_dict(role_data)

        # Use the expert_service to create the role, which handles existence checks and saving.
        new_expert = expert_service.create_expert(standardized_role_data)

        return {
            "success": True,
            "role": new_expert.to_dict(),
            "analysis": analysis_result,
            "message": f"Role '{new_expert.name}' created successfully.",
        }
    except ValueError as e:
        # Handle specific error for existing role from the service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to smart-create role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to smart-create role: {str(e)}")

@router.post("/batch_import", response_model=dict[str, Any])
async def batch_import_roles(
    request: BatchRoleImportRequest, expert_service: ExpertService = Depends(get_expert_service)
):
    """Batch import roles using the ExpertService."""
    if not ROLE_UTILS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Role utils are not available.")

    try:
        # The entire logic is now delegated to the service layer.
        results = expert_service.batch_import_experts(
            roles_data=request.roles,
            overwrite=request.overwrite_existing,
            validate_only=request.validate_only,
        )
        return results
    except Exception as e:
        logger.error(f"Batch import failed at the router level: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred during batch import: {str(e)}"
        )

@router.post("/search_embedding")
async def search_roles_by_embedding(
    query: str, top_k: int = 5, expert_service: ExpertService = Depends(get_expert_service)
):
    """Intelligently search for roles using vector embeddings."""
    try:
        # Logic is now delegated to the service layer
        results = expert_service.search_experts_by_embedding(query, top_k)
        return {"roles": results}
    except Exception as e:
        logger.error(f"Embedding search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Embedding search failed.")