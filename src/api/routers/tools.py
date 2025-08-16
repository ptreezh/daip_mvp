import logging

from fastapi import APIRouter, HTTPException

from src.api.dependencies import AppStateDep
from src.models import (
    FileOpRequest,
    MemoryEntryRequest,
    PromptOptimizationRequest,
    PromptOptimizationResponse,
)

router = APIRouter(
    prefix="/tools",
    tags=["Tools & Memory"],
)

logger = logging.getLogger(__name__)


@router.get("/")
async def list_tools(state: AppStateDep):
    """List all available tools from the unified tool manager."""
    tool_defs = state.unified_tool_manager.get_tool_definitions()
    return {
        "total_tools": len(tool_defs),
        "tools": [tool["function"]["name"] for tool in tool_defs],
    }


@router.post("/read_file")
async def api_read_file(state: AppStateDep, req: FileOpRequest):
    """Read content from a file."""
    try:
        # Assuming file_tools are integrated into the unified tool manager
        # or available as separate functions. For now, we call a mock/direct function.
        from tools.file_tools import read_file
        content = read_file(req.path, req.encoding)
        return {"success": True, "content": content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/write_file")
async def api_write_file(state: AppStateDep, req: FileOpRequest):
    """Write content to a file."""
    try:
        from tools.file_tools import write_file
        write_file(req.path, req.content or "", req.encoding)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/memory/add")
async def add_memory_entry(state: AppStateDep, req: MemoryEntryRequest):
    """Add an entry to the memory bank."""
    try:
        memory_id = state.memory_tools.add_memory(
            req.agent_id, req.content or "", req.tags, req.source, req.embedding
        )
        return {"success": True, "memory_id": memory_id}
    except Exception as e:
        logger.error(f"Failed to add memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/search")
async def search_memory(state: AppStateDep, req: MemoryEntryRequest):
    """Search memory by embedding."""
    try:
        if not req.embedding:
            raise HTTPException(status_code=400, detail="Embedding is required for search.")
        results = state.memory_tools.search_memory_by_embedding(
            req.agent_id, req.embedding, req.top_k or 5
        )
        return {"success": True, "memories": results}
    except Exception as e:
        logger.error(f"Failed to search memory: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prompt_optimization", response_model=PromptOptimizationResponse)
async def api_prompt_optimization(req: PromptOptimizationRequest):
    """Optimizes a user prompt in two steps:
    1. Discern explicit and latent needs, sorted by confidence.
    2. Structure the primary need into a JSON format for an LLM.
    """
    try:
        user_input = req.user_input.strip()
        if not user_input:
            return PromptOptimizationResponse(insights=[], success=False, error="User input is empty")

        # Simplified insight simulation
        insights = []
        if "分析" in user_input:
            insights.append({"need": "文档分析", "confidence": 0.95})
        if "撰写" in user_input or "写" in user_input:
            insights.append({"need": "内容创作", "confidence": 0.9})
        if "协作" in user_input:
            insights.append({"need": "多角色协作", "confidence": 0.8})
        if not insights:
            insights.append({"need": "需求不明确？", "confidence": 0.5})

        insights.sort(key=lambda x: x["confidence"], reverse=True)

        main_need = insights[0]["need"] if insights else "未知"
        structured_json = {
            "main_need": main_need,
            "all_needs": [i["need"] for i in insights],
            "raw_input": user_input,
        }
        return PromptOptimizationResponse(insights=insights, structured_json=structured_json)
    except Exception as e:
        logger.error(f"Prompt optimization failed: {e}", exc_info=True)
        return PromptOptimizationResponse(insights=[], success=False, error=str(e))
