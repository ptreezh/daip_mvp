from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.expert_library import ExpertLibrary
from src.memory_bank_tools import MemoryBankTools
from src.virtual_team_project_engine import VirtualTeamProjectEngine


# 请求模型
def get_engine():
    return VirtualTeamProjectEngine(MemoryBankTools(), ExpertLibrary())


class CreateProjectRequest(BaseModel):
    name: str
    description: str
    creator: str
    initial_roles: list[str] = []
    config: dict[str, Any] = {}


class AssignRoleRequest(BaseModel):
    project_id: str
    role_id: str


class CreateTaskRequest(BaseModel):
    project_id: str
    title: str
    description: str
    assigned_role: str
    priority: str = "medium"
    dependencies: list[str] = []


virtual_team_router = APIRouter(prefix="/virtual_team", tags=["virtual_team"])


@virtual_team_router.post("/create_project")
async def create_project(request: CreateProjectRequest):
    engine = get_engine()
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
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.post("/assign_role")
async def assign_role(request: AssignRoleRequest):
    engine = get_engine()
    try:
        result = await engine.assign_role(request.project_id, request.role_id)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.post("/create_task")
async def create_task(request: CreateTaskRequest):
    engine = get_engine()
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
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.get("/projects")
async def list_projects():
    engine = get_engine()
    try:
        projects = list(engine.projects.values())
        return {"success": True, "projects": [p.__dict__ for p in projects]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.get("/project/{project_id}/status")
async def get_project_status(project_id: str):
    engine = get_engine()
    try:
        status = await engine.get_project_status(project_id)
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.get("/tasks")
async def list_tasks(project_id: str = Query(...)):
    engine = get_engine()
    try:
        project = engine.projects.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        tasks = [
            t.__dict__ for t in engine.tasks.values() if t.project_id == project_id
        ]
        return {"success": True, "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.get("/project/{project_id}/memory")
async def get_project_memory(project_id: str):
    engine = get_engine()
    try:
        memory = await engine.get_memory_bank_content(project_id)
        return {"success": True, "memory": memory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.get("/statistics")
async def get_statistics():
    engine = get_engine()
    try:
        stats = {
            "total_projects": len(engine.projects),
            "total_tasks": len(engine.tasks),
            "total_roles": len(engine.role_contexts),
        }
        return {"success": True, "statistics": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@virtual_team_router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    engine = get_engine()
    try:
        if project_id in engine.projects:
            del engine.projects[project_id]
            return {"success": True}
        else:
            raise HTTPException(status_code=404, detail="项目不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
