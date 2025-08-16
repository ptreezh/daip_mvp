import asyncio
import json
import logging
import random
<<<<<<< HEAD
from typing import Any, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from fastapi import HTTPException

from src.models import ChatMessage, MultiRoleChatRequest, MultiRoleChatResponse

# Assuming MultiRoleChatEngine is available
try:
    from src.multi_role_chat import ChatRoom, MultiRoleChatEngine, RoleResponse

    CHAT_ENGINE_AVAILABLE = True
except ImportError:
    CHAT_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChatService:
    """Service layer for handling all chat-related functionalities,
    including multi-role chat simulations and engine management.
    """

    def __init__(self, app_state: Any): # Use Any to avoid circular import type hint
        self.app_state = app_state
        if not CHAT_ENGINE_AVAILABLE:
            logger.warning("MultiRoleChatEngine not available. Chat functionalities will be limited.")

    async def handle_simple_multi_role_chat(self, request: MultiRoleChatRequest) -> MultiRoleChatResponse:
        """Handles the logic for a simplified multi-role chat simulation.
        """
        # Log the conversation history
        with open(self.app_state.chat_log_file, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": asyncio.get_event_loop().time(),
                "topic": request.topic,
                "roles": request.roles,
                "messages": [msg.model_dump() for msg in request.messages],
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        # Select a random AI role to respond
        ai_roles = [r for r in request.roles if r.lower() not in ["user", "system"]]
        if not ai_roles:
            raise HTTPException(status_code=400, detail="No available AI roles in the chat.")

        selected_role = random.choice(ai_roles)

        # Simulate an LLM call
        context_messages = request.messages[-random.randint(1, 5) :]
        llm_response_content = await self.app_state.call_llm_simulation(
            selected_role, request.topic, context_messages
        )

        new_message = ChatMessage(sender_name=selected_role, content=llm_response_content)

        return MultiRoleChatResponse(new_message=new_message)

    def create_chat_engine(self, engine_id: str, model_type: str) -> None:
        """Creates and registers a new multi-role chat engine.
        """
        if not CHAT_ENGINE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Chat Engine feature is not available.")

        if engine_id in self.app_state.chat_engines:
            raise HTTPException(status_code=400, detail="Chat engine with this ID already exists.")

        # Ensure expert library is loaded
        if not self.app_state.expert_library.experts:
            self.app_state.expert_library.load_experts_from_directory()

        self.app_state.chat_engines[engine_id] = MultiRoleChatEngine(self.app_state.expert_library, model_type)
        logger.info(f"Chat engine '{engine_id}' created with model '{model_type}'.")

    def _get_engine(self, engine_id: str) -> "MultiRoleChatEngine":
        """Helper to get a chat engine instance."""
        if engine_id not in self.app_state.chat_engines:
            raise HTTPException(status_code=404, detail="Chat engine not found.")
        return self.app_state.chat_engines[engine_id]

    async def send_message_to_room(self, engine_id: str, room_id: str, content: str, sender_name: str) -> bool:
        """Sends a message to a specific chat room after validation.
        """
        chat_engine = self._get_engine(engine_id)
        room = chat_engine.get_chat_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail=f"Chat room with ID '{room_id}' not found.")

        participant_names = {p.role_name for p in room.participants}
        if sender_name != "User" and sender_name not in participant_names:
            raise HTTPException(
                status_code=400,
                detail=f"Sender '{sender_name}' is not a participant in room '{room_id}'.",
            )

        return await chat_engine.send_user_message(room_id, content, sender_name)

<<<<<<< HEAD
    async def generate_responses_for_room(self, engine_id: str, room_id: str, target_roles: Optional[List[str]]) -> List["RoleResponse"]:
=======
    async def generate_responses_for_room(self, engine_id: str, room_id: str, target_roles: Optional[list[str]]) -> list["RoleResponse"]:
>>>>>>> feature/core-services-refactor
        """Generates responses from AI roles in a chat room.
        """
        chat_engine = self._get_engine(engine_id)
        return await chat_engine.generate_role_responses(room_id, target_roles)

    def get_room_details(self, engine_id: str, room_id: str) -> "ChatRoom":
        """Retrieves details for a specific chat room.
        """
        chat_engine = self._get_engine(engine_id)
        room = chat_engine.get_chat_room(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Chat room not found.")
        return room

<<<<<<< HEAD
    def list_all_rooms(self, engine_id: str) -> List["ChatRoom"]:
=======
    def list_all_rooms(self, engine_id: str) -> list["ChatRoom"]:
>>>>>>> feature/core-services-refactor
        """Lists all available chat rooms in a given engine.
        """
        chat_engine = self._get_engine(engine_id)
        return chat_engine.get_all_rooms()
