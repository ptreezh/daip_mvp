"""Multi-role chat engine implementation.

This module provides the core engine for managing multi-role chat rooms,
including room creation, message handling, and role response generation.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.core_services.expert_service import ExpertService
from src.models import ChatMessage
from src.virtual_role_chat.models import ChatRoom, ChatRoomConfig

logger = logging.getLogger(__name__)


class RoleResponse(BaseModel):
    """Response from a role in a chat room."""
    
    id: str
    role_id: str
    role_name: str
    content: str
    timestamp: datetime
    message_type: str = "text"
    metadata: Dict[str, Any] = {}


class MultiRoleChatEngine:
    """Core engine for managing multi-role chat interactions."""
    
    def __init__(self, expert_service: ExpertService, model_type: str = "default"):
        """Initialize the multi-role chat engine.
        
        Args:
            expert_service: Service for managing experts/roles
            model_type: Type of language model to use
        """
        self.expert_service = expert_service
        self.model_type = model_type
        self.chat_rooms: Dict[str, ChatRoom] = {}
        self.room_messages: Dict[str, List[ChatMessage]] = {}  # room_id -> messages
        self.room_participants: Dict[str, List[Dict[str, Any]]] = {}  # room_id -> participants
        
        logger.info(f"MultiRoleChatEngine initialized with model: {model_type}")
    
    def create_chat_room(
        self,
        room_name: str,
        topic: str,
        initial_participants: Optional[List[str]] = None,
    ) -> str:
        """Create a new chat room.
        
        Args:
            room_name: Name of the chat room
            topic: Topic of discussion
            initial_participants: Initial role IDs to participate
            
        Returns:
            ID of the created chat room
        """
        room_id = f"room_{uuid.uuid4().hex[:8]}"
        
        # Create room config
        config = ChatRoomConfig(
            name=room_name,
            topic=topic,
            roles=initial_participants or [],
            description=f"Chat room for discussing: {topic}"
        )
        
        # Create chat room
        chat_room = ChatRoom(
            id=room_id,
            config=config,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store room
        self.chat_rooms[room_id] = chat_room
        self.room_messages[room_id] = []
        self.room_participants[room_id] = []
        
        # Add initial participants
        if initial_participants:
            for role_id in initial_participants:
                self._add_participant_to_room(room_id, role_id)
        
        logger.info(f"Created chat room '{room_name}' with ID: {room_id}")
        return room_id
    
    def _add_participant_to_room(self, room_id: str, role_id: str) -> bool:
        """Add a participant to a chat room.
        
        Args:
            room_id: ID of the chat room
            role_id: ID of the role to add
            
        Returns:
            True if participant was added, False otherwise
        """
        if room_id not in self.chat_rooms:
            return False
            
        # Check if role exists in expert service
        try:
            # Get all experts and find the one with matching ID
            experts = self.expert_service.get_all_experts()
            role = None
            for expert in experts:
                if hasattr(expert, 'name') and expert.name == role_id:
                    role = expert
                    break
        except Exception as e:
            logger.warning(f"Failed to get expert '{role_id}' from expert service: {e}")
            return False
            
        if not role:
            logger.warning(f"Role '{role_id}' not found in expert service")
            return False
            
        # Check if already participant
        participants = self.room_participants.get(room_id, [])
        if any(p["role_id"] == role_id for p in participants):
            return True  # Already a participant
            
        # Add participant
        role_data = {}
        if hasattr(role, 'to_dict'):
            try:
                role_data = role.to_dict()
            except Exception:
                role_data = {}
        elif hasattr(role, '__dict__'):
            role_data = role.__dict__
        
        participant = {
            "role_id": role_id,
            "role_name": getattr(role, 'name', role_id),
            "role_data": role_data,
            "is_active": True,
            "message_count": 0,
            "last_activity": datetime.now().isoformat()
        }
        
        self.room_participants.setdefault(room_id, []).append(participant)
        logger.info(f"Added participant '{role_id}' to room '{room_id}'")
        return True
    
    async def send_user_message(
        self,
        room_id: str,
        content: str,
        sender_name: str = "User"
    ) -> bool:
        """Send a user message to a chat room.
        
        Args:
            room_id: ID of the chat room
            content: Message content
            sender_name: Name of the sender
            
        Returns:
            True if message was sent, False otherwise
        """
        if room_id not in self.chat_rooms:
            return False
            
        # Create message
        message = ChatMessage(
            sender_name=sender_name,
            content=content,
            message_type="text",
            metadata={"sender_type": "user"}
        )
        
        # Store message
        self.room_messages.setdefault(room_id, []).append(message)
        
        # Update room timestamp
        self.chat_rooms[room_id].updated_at = datetime.now()
        
        logger.info(f"Sent user message to room '{room_id}'")
        return True
    
    async def generate_role_responses(
        self,
        room_id: str,
        target_roles: Optional[List[str]] = None
    ) -> List[RoleResponse]:
        """Generate responses from AI roles in a chat room.
        
        Args:
            room_id: ID of the chat room
            target_roles: Specific roles to generate responses from (None for all)
            
        Returns:
            List of role responses
        """
        if room_id not in self.chat_rooms:
            return []
            
        # Get participants
        participants = self.room_participants.get(room_id, [])
        if target_roles:
            participants = [p for p in participants if p["role_id"] in target_roles]
            
        # Get recent messages for context
        messages = self.room_messages.get(room_id, [])
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        
        # Generate responses from each participant
        responses = []
        for participant in participants:
            try:
                response_content = await self._generate_role_response(
                    participant, recent_messages
                )
                
                role_response = RoleResponse(
                    id=f"response_{uuid.uuid4().hex[:8]}",
                    role_id=participant["role_id"],
                    role_name=participant["role_name"],
                    content=response_content,
                    timestamp=datetime.now(),
                    metadata={"room_id": room_id}
                )
                
                responses.append(role_response)
                
                # Update participant stats
                participant["message_count"] += 1
                participant["last_activity"] = datetime.now().isoformat()
                
            except Exception as e:
                logger.error(f"Failed to generate response for role '{participant['role_id']}': {e}")
                # Create error response
                role_response = RoleResponse(
                    id=f"error_{uuid.uuid4().hex[:8]}",
                    role_id=participant["role_id"],
                    role_name=participant["role_name"],
                    content="Sorry, I encountered a technical issue while generating a response.",
                    timestamp=datetime.now(),
                    metadata={"room_id": room_id, "error": str(e)}
                )
                responses.append(role_response)
        
        # Update room timestamp
        self.chat_rooms[room_id].updated_at = datetime.now()
        
        logger.info(f"Generated {len(responses)} role responses for room '{room_id}'")
        return responses
    
    async def _generate_role_response(
        self,
        participant: Dict[str, Any],
        context_messages: List[ChatMessage]
    ) -> str:
        """Generate a response for a specific role based on context.
        
        Args:
            participant: Participant information
            context_messages: Recent messages for context
            
        Returns:
            Generated response content
        """
        # In a real implementation, this would call an LLM
        # For now, we'll simulate a response
        
        role_name = participant["role_name"]
        context_summary = "\n".join([
            f"{msg.sender_name}: {msg.content}" 
            for msg in context_messages[-3:]  # Last 3 messages
        ])
        
        # Simulate LLM processing delay
        await asyncio.sleep(0.1)
        
        # Generate simulated response
        if context_summary:
            return f"As {role_name}, I have some thoughts on the discussion we just had:\n\n{context_summary[:100]}...\n\nI think we can explore this issue further from a professional perspective."
        else:
            return f"As {role_name}, I'm happy to participate in this discussion. Please start sharing your thoughts!"
    
    def get_chat_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get a chat room by ID.
        
        Args:
            room_id: ID of the chat room
            
        Returns:
            ChatRoom object or None if not found
        """
        return self.chat_rooms.get(room_id)
    
    def get_all_rooms(self) -> List[ChatRoom]:
        """Get all chat rooms.
        
        Returns:
            List of all chat rooms
        """
        return list(self.chat_rooms.values())
    
    def add_participant(self, room_id: str, role_id: str) -> bool:
        """Add a participant to a chat room.
        
        Args:
            room_id: ID of the chat room
            role_id: ID of the role to add
            
        Returns:
            True if participant was added, False otherwise
        """
        return self._add_participant_to_room(room_id, role_id)
    
    def remove_participant(self, room_id: str, role_id: str) -> bool:
        """Remove a participant from a chat room.
        
        Args:
            room_id: ID of the chat room
            role_id: ID of the role to remove
            
        Returns:
            True if participant was removed, False otherwise
        """
        if room_id not in self.room_participants:
            return False
            
        participants = self.room_participants[room_id]
        initial_count = len(participants)
        
        # Remove participant
        self.room_participants[room_id] = [
            p for p in participants if p["role_id"] != role_id
        ]
        
        removed = len(participants) < initial_count
        if removed:
            logger.info(f"Removed participant '{role_id}' from room '{room_id}'")
        
        return removed
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Get chat statistics.
        
        Returns:
            Dictionary with chat statistics
        """
        total_rooms = len(self.chat_rooms)
        total_messages = sum(len(messages) for messages in self.room_messages.values())
        total_participants = sum(len(participants) for participants in self.room_participants.values())
        
        return {
            "total_rooms": total_rooms,
            "total_messages": total_messages,
            "total_participants": total_participants,
            "rooms": [
                {
                    "room_id": room_id,
                    "name": room.config.name,
                    "topic": room.config.topic,
                    "message_count": len(self.room_messages.get(room_id, [])),
                    "participant_count": len(self.room_participants.get(room_id, [])),
                    "last_activity": room.updated_at.isoformat()
                }
                for room_id, room in self.chat_rooms.items()
            ]
        }
    
    def delete_chat_room(self, room_id: str) -> bool:
        """Delete a chat room.
        
        Args:
            room_id: ID of the chat room to delete
            
        Returns:
            True if room was deleted, False otherwise
        """
        if room_id not in self.chat_rooms:
            return False
            
        # Remove room and associated data
        del self.chat_rooms[room_id]
        self.room_messages.pop(room_id, None)
        self.room_participants.pop(room_id, None)
        
        logger.info(f"Deleted chat room '{room_id}'")
        return True
    
    def get_room_recommendations(self, room_id: str, count: int = 6) -> List[Dict[str, Any]]:
        """Get role recommendations for a chat room.
        
        Args:
            room_id: ID of the chat room
            count: Number of recommendations to return
            
        Returns:
            List of role recommendations
        """
        # In a real implementation, this would use the expert library
        # to find relevant roles based on the room topic and current participants
        return [
            {
                "role_id": f"recommended_role_{i}",
                "role_name": f"Recommended Role {i}",
                "specialties": ["Specialty 1", "Specialty 2"],
                "relevance_score": 0.8 - (i * 0.1)
            }
            for i in range(count)
        ]
    
    def get_random_recommendations(self, count: int = 6, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get random role recommendations.
        
        Args:
            count: Number of recommendations to return
            category: Optional category filter
            
        Returns:
            List of role recommendations
        """
        # In a real implementation, this would use the expert library
        # to find random or category-specific roles
        return [
            {
                "role_id": f"random_role_{i}",
                "role_name": f"Random Role {i}",
                "specialties": ["Specialty A", "Specialty B"],
                "category": category or "General"
            }
            for i in range(count)
        ]