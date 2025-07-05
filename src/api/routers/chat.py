import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_chat_service
from src.models import (
    ChatMessage,
    MultiRoleChatRequest,
    MultiRoleChatResponse,
)
from src.core_services.chat_service import ChatService
from src.chat_config import DEFAULT_CHAT_MODEL

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

logger = logging.getLogger(__name__)


@router.post("/multi_role_chat_simple", response_model=MultiRoleChatResponse)
async def multi_role_chat_simple(
    request: MultiRoleChatRequest, chat_service: ChatService = Depends(get_chat_service)
):
    """
    A simplified multi-role chat endpoint that simulates a response from a random AI role.
    """
    try:
        return await chat_service.handle_simple_multi_role_chat(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-role chat failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Multi-role chat processing failed.")


@router.post("/multi_chat/create_engine")
async def create_chat_engine(
    engine_id: str,
    model_type: str = DEFAULT_CHAT_MODEL,
    chat_service: ChatService = Depends(get_chat_service),
):
    """Create a new multi-role chat engine instance."""
    try:
        chat_service.create_chat_engine(engine_id, model_type)
        return {
            "success": True,
            "engine_id": engine_id,
            "message": "Chat engine created successfully.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create chat engine: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create chat engine: {str(e)}")


@router.post("/multi_chat/send_message")
async def send_chat_message(
    room_id: str,
    content: str,
    sender_name: str = "User",
    engine_id: str = "default",
    chat_service: ChatService = Depends(get_chat_service),
):
    """Send a message to a specific chat room."""
    try:
        success = await chat_service.send_message_to_room(engine_id, room_id, content, sender_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send message internally after validation.")
        return {"success": True, "message": "Message sent successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/multi_chat/generate_responses")
async def generate_role_responses(
    room_id: str,
    target_roles: list[str] = None,
    engine_id: str = "default",
    chat_service: ChatService = Depends(get_chat_service),
):
    """Generate responses from AI roles in a chat room."""
    try:
        responses = await chat_service.generate_responses_for_room(engine_id, room_id, target_roles)
        response_data = [resp.dict() for resp in responses]
        return {"success": True, "responses": response_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate responses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate responses: {str(e)}")


@router.get("/multi_chat/room/{room_id}")
async def get_chat_room_details(
    room_id: str, engine_id: str = "default", chat_service: ChatService = Depends(get_chat_service)
):
    """Get details of a specific chat room."""
    try:
        room = chat_service.get_room_details(engine_id, room_id)
        return {"success": True, "room": room.dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get room details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get room details: {str(e)}")


@router.get("/multi_chat/rooms")
async def list_all_chat_rooms(
    engine_id: str = "default", chat_service: ChatService = Depends(get_chat_service)
):
    """List all available chat rooms in an engine."""
    try:
        rooms = chat_service.list_all_rooms(engine_id)
        room_data = [room.dict() for room in rooms]
        return {"success": True, "rooms": room_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list rooms: {str(e)}")