import logging

from fastapi import APIRouter, HTTPException

from src.api.dependencies import AppStateDep
from src.models import (
    CreateVirtualProjectRequest,
    CreateVirtualTaskRequest,
)

router = APIRouter(
    prefix="/virtual_team",
    tags=["Virtual Team Management"],
)

logger = logging.getLogger(__name__)


@router.post("/create_project")
async def create_virtual_project(state: AppStateDep, request: CreateVirtualProjectRequest):
    """Create a new virtual team project."""
    engine = state.virtual_team_engine
    try:
        project_id = await engine.create_project(
            name=request.name,
            description=request.description,
            creator=request.creator,
            initial_roles=request.initial_roles,
            config=request.config,
        )
        return {"success": True, "project_id": project_id}
    except Exception as e:
        logger.error(f"Failed to create virtual project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.post("/create_task")
async def create_virtual_task(state: AppStateDep, request: CreateVirtualTaskRequest):
    """Create a new task within a virtual project."""
    engine = state.virtual_team_engine
    try:
        task_id = await engine.create_task(
            project_id=request.project_id,
            title=request.title,
            description=request.description,
            assigned_role=request.assigned_role,
            priority=request.priority,
            dependencies=request.dependencies,
        )
        return {"success": True, "task_id": task_id}
    except Exception as e:
        logger.error(f"Failed to create virtual task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.post("/execute_task/{task_id}")
async def execute_virtual_task(state: AppStateDep, task_id: str):
    """Execute a specific task in a virtual project."""
    engine = state.virtual_team_engine
    try:
        result = await engine.execute_task(task_id)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Failed to execute virtual task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to execute task: {str(e)}")


@router.get("/project/{project_id}/status")
async def get_project_status(state: AppStateDep, project_id: str):
    """Get the status of a virtual project."""
    engine = state.virtual_team_engine
    try:
        status = await engine.get_project_status(project_id)
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Failed to get project status for {project_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")


@router.get("/projects")
async def list_virtual_projects(state: AppStateDep):
    """List all active virtual projects."""
    engine = state.virtual_team_engine
    projects = [p.dict() for p in engine.projects.values()]
    return {"success": True, "projects": projects}