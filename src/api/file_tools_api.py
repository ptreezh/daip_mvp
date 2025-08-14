# @AI-Generated: 2024-07-23, Confidence: 0.99, Model: Gemini-Code-Assist
"""API Endpoints for File System Operations.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from tools.file_tools import (
    list_files,
    make_dir,
    make_tree_dirs,
    read_file,
    write_file,
)

router = APIRouter(
    prefix="/tools",
    tags=["File Tools"],
)


class FileOpRequest(BaseModel):
    path: str
    encoding: Optional[str] = "utf-8"
    content: Optional[str] = None
    tree: Optional[dict] = None


@router.post("/read_file")
async def api_read_file(req: FileOpRequest):
    try:
        content = read_file(req.path, req.encoding)
        return {"success": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/write_file")
async def api_write_file(req: FileOpRequest):
    try:
        write_file(req.path, req.content or "", req.encoding)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/list_files")
async def api_list_files(req: FileOpRequest):
    try:
        files = list_files(req.path)
        return {"success": True, "files": files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/make_dir")
async def api_make_dir(req: FileOpRequest):
    try:
        make_dir(req.path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/make_tree_dirs")
async def api_make_tree_dirs(req: FileOpRequest):
    try:
        make_tree_dirs(req.tree or {}, req.path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
