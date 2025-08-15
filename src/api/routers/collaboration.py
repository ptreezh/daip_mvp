import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_collaboration_service
from src.core_services.collaboration_service import CollaborationService
from src.models import Task, TaskBase, WikiEntryRequest

router = APIRouter(
    prefix="/collaboration",
    tags=["Collaboration & Wiki"],
)

logger = logging.getLogger(__name__)


@router.get("/wiki/content")
async def get_wiki_content(entry: str, collab_service: CollaborationService = Depends(get_collaboration_service)):
    """Get the content of a wiki entry."""
    content = collab_service.get_wiki_content(entry)
    return {"entry": entry, "content": content}


@router.post("/wiki/save")
async def save_wiki_version(req: WikiEntryRequest, collab_service: CollaborationService = Depends(get_collaboration_service)):
    """Save a new version of a wiki entry."""
    try:
        collab_service.save_wiki_version(req)
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to save wiki entry '{req.entry}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save wiki entry.")


@router.post("/tasks/create", response_model=Task)
async def create_task(task_base: TaskBase, collab_service: CollaborationService = Depends(get_collaboration_service)):
    """Create a new collaborative task."""
    try:
        new_task = collab_service.create_task(task_base)
        return new_task
    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create task.")


@router.get("/tasks/list", response_model=list[Task])
async def list_all_tasks(
    stage: Optional[str] = None,
    assigned_to: Optional[str] = None,
    status: Optional[str] = None,
    collab_service: CollaborationService = Depends(get_collaboration_service),
):
    """List and filter all collaborative tasks."""
    tasks = collab_service.list_tasks(stage, assigned_to, status)
    return tasks


@router.patch("/tasks/{task_id}/update", response_model=Task)
async def update_task(
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    comment: Optional[str] = None,
    collab_service: CollaborationService = Depends(get_collaboration_service),
):
    """Update a task's status, progress, or add a comment."""
    try:
        task = collab_service.update_task(task_id, status, progress, comment)
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update task.")


@router.get("/users")
async def get_collaboration_users(collab_service: CollaborationService = Depends(get_collaboration_service)):
    """Get the list of collaboration users (mock data)."""
    users = collab_service.get_collaboration_users()
    return {"users": users}


@router.get("/projects")
async def get_collaboration_projects(collab_service: CollaborationService = Depends(get_collaboration_service)):
    """Get the list of collaboration projects (mock data)."""
    projects = collab_service.get_collaboration_projects()
    return {"projects": projects}