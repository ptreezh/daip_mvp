# @AI-Generated: 2024-07-23, Confidence: 0.99, Model: Gemini-Code-Assist
"""
API Endpoints for Memory Bank and Memory Management.
This module unifies the old /tools/memory and /memory endpoints into a single
set of services that use the new AppState and RoleMemoryBank.
"""
from dataclasses import asdict
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.app_state import AppState, get_app_state

router = APIRouter(
    tags=["Memory Tools"],
)


class MemoryBankRequest(BaseModel):
    role_name: str
    content: Optional[str] = None


class MemoryEntryRequest(BaseModel):
    agent_id: str
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    embedding: Optional[list[float]] = None
    memory_id: Optional[str] = None
    limit: Optional[int] = 10
    tag: Optional[str] = None
    keyword: Optional[str] = None
    after: Optional[float] = None
    before: Optional[float] = None
    top_k: Optional[int] = 5


@router.post("/tools/create_memory_bank")
async def api_create_memory_bank(
    req: MemoryBankRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        if not app_state.memory_bank.get_role_identity(req.role_name):
            role_data = {
                "id": req.role_name,
                "name": req.role_name,
                "description": "Auto-created role via memory bank.",
            }
            app_state.memory_bank.create_role_identity(role_data)
        return {"success": True, "path": f"memory_bank/{req.role_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tools/write_memory")
async def api_write_memory(
    req: MemoryBankRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memory_id = app_state.memory_bank.add_memory(
            role_id=req.role_name,
            content=req.content or "",
            memory_type="dialogue",
            importance=0.5,
        )
        return {"success": True, "file_path": f"memory/{memory_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tools/read_memory")
async def api_read_memory(
    req: MemoryBankRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memories = app_state.memory_bank.retrieve_memories(
            role_id=req.role_name, limit=1000
        )
        content = "\n".join([m.content for m in memories])
        return {"success": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tools/list_memories")
async def api_list_memories(
    req: MemoryBankRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memories = app_state.memory_bank.retrieve_memories(
            role_id=req.role_name, limit=100
        )
        memory_list = [asdict(m) for m in memories]
        return {"success": True, "memories": memory_list}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/add")
async def api_add_memory(
    req: MemoryEntryRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memory_id = app_state.memory_bank.add_memory(
            role_id=req.agent_id,
            content=req.content or "",
            memory_type="knowledge",
            importance=0.5,
            tags=req.tags,
            metadata={"source": req.source} if req.source else {},
        )
        return {"success": True, "memory_id": memory_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/list")
async def api_list_all_memories(
    req: MemoryEntryRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memories = app_state.memory_bank.retrieve_memories(
            role_id=req.agent_id, query=req.keyword, limit=req.limit or 100
        )
        return {"success": True, "memories": [asdict(m) for m in memories]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/get")
async def api_get_memory(
    req: MemoryEntryRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memory = app_state.memory_bank.get_memory_by_id(req.memory_id)
        if not memory or memory.role_id != req.agent_id:
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"success": True, "memory": asdict(memory)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/delete")
async def api_delete_memory(
    req: MemoryEntryRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memory = app_state.memory_bank.get_memory_by_id(req.memory_id)
        if not memory or memory.role_id != req.agent_id:
            return {"success": True, "message": "Memory not found or not owned."}
        ok = app_state.memory_bank.delete_memory(req.memory_id)
        return {"success": ok}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/search_embedding")
async def api_search_memory_by_embedding(
    req: MemoryEntryRequest, app_state: AppState = Depends(get_app_state)
):
    try:
        memories = app_state.memory_bank.search_by_embedding(
            role_id=req.agent_id, embedding=req.embedding or [], top_k=req.top_k or 5
        )
        return {"success": True, "memories": [asdict(m) for m in memories]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))