# -*- coding: utf-8 -*-
"""ChatCoordinator implementation for the Virtual Role Chat System."""

import uuid
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from pathlib import Path
import json

from .models import ChatRoomConfig

if TYPE_CHECKING:
    from .chat_room_manager import ChatRoomManager
    from .chat_session_service import ChatSessionService
    from src.core_services.role_manager import RoleManager
    from src.institutional_primitives.registry import PrimitiveRegistry
    from src.core_services.wiki_service import WikiService


class ChatCoordinator:
    """Coordinator for chat room related operations."""
    
    def __init__(
        self, 
        chat_room_manager: "ChatRoomManager", 
        chat_session_service: "ChatSessionService",
        role_manager: Optional["RoleManager"] = None,
        primitive_registry: Optional["PrimitiveRegistry"] = None,
        wiki_service: Optional["WikiService"] = None,
        state_file: Path = Path("data/chat_coordinator_state.json"),
    ):
        """Initialize the ChatCoordinator."""
        self.chat_room_manager = chat_room_manager
        self.chat_session_service = chat_session_service
        self.role_manager = role_manager
        self.primitive_registry = primitive_registry
        self.wiki_service = wiki_service
        self._current_room_id: Optional[str] = None
        self.state_file = state_file
        self.load_state()

    def save_state(self):
        """Saves the current state of the coordinator to a file."""
        try:
            state = {"current_room_id": self._current_room_id}
            # Ensure the directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(state, f)
        except Exception as e:
            print(f"Error saving chat coordinator state: {e}")

    def load_state(self):
        """Loads the state of the coordinator from a file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                    self._current_room_id = state.get("current_room_id")
        except Exception as e:
            print(f"Error loading chat coordinator state: {e}")
            self._current_room_id = None

    def recommend_roles_for_topic(self, topic: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend roles based on the chat topic.
        
        Args:
            topic: The chat topic to recommend roles for.
            limit: Maximum number of roles to recommend.
            
        Returns:
            List of recommended role dictionaries.
        """
        if not self.role_manager:
            return []
        
        # Simple keyword-based role recommendation
        # In a real implementation, this could use more sophisticated NLP
        topic_lower = topic.lower()
        all_roles = self.role_manager.list_roles()
        
        recommended_roles = []
        for role in all_roles:
            score = 0
            # Check if role name or description matches topic keywords
            if any(keyword in role.name.lower() for keyword in topic_lower.split()):
                score += 2
            if role.description and any(keyword in role.description.lower() for keyword in topic_lower.split()):
                score += 1
            
            if score > 0:
                recommended_roles.append({
                    "id": role.id,
                    "name": role.name, 
                    "description": role.description,
                    "score": score
                })
        
        # Sort by score and return top results
        recommended_roles.sort(key=lambda x: x["score"], reverse=True)
        return recommended_roles[:limit]

    def get_available_chat_primitives(self) -> List[Dict[str, Any]]:
        """Get available chat primitives (rules).
        
        Returns:
            List of available primitive information.
        """
        if not self.primitive_registry:
            return []
        
        primitives = []
        for primitive_type, primitive_class in self.primitive_registry._primitives.items():
            try:
                # Get primitive info without instantiating
                primitives.append({
                    "type": primitive_type,
                    "description": getattr(primitive_class, '__doc__', 'No description available'),
                })
            except Exception:
                continue
        
        return primitives

    def upload_document_to_chat(self, room_id: str, file_path: str, description: str = "") -> bool:
        """Upload a document to a chat room.
        
        Args:
            room_id: The ID of the chat room.
            file_path: Path to the document file.
            description: Optional description of the document.
            
        Returns:
            True if upload was successful, False otherwise.
        """
        try:
            # Read document content
            document_path = Path(file_path)
            if not document_path.exists():
                return False
            
            content = document_path.read_text(encoding='utf-8')
            
            # Create a wiki page for the document if wiki service is available
            if self.wiki_service:
                doc_name = f"ChatDocument_{room_id}_{document_path.stem}"
                self.wiki_service.create_entry(
                    entry_name=doc_name,
                    content=content,
                    author_role="document_upload",
                    tags=["chat_document", room_id],
                    category="chat_documents"
                )
            
            # Store document reference in chat room
            # This would typically involve updating the chat room metadata
            return True
            
        except Exception:
            return False

    def get_chat_consensus_info(self, room_id: str) -> Dict[str, Any]:
        """Get consensus information for a chat room.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            Dictionary containing consensus information.
        """
        # Get chat history
        history = self.get_room_history(room_id)
        
        # Simple consensus analysis (placeholder implementation)
        # In a real implementation, this would use more sophisticated NLP
        messages = [msg["content"] for msg in history if msg.get("content")]
        
        if not messages:
            return {"consensus_level": "no_data", "agreement_points": [], "disagreement_points": []}
        
        # Placeholder analysis - in real implementation this would:
        # - Use sentiment analysis
        # - Identify common themes
        # - Detect points of agreement and disagreement
        return {
            "consensus_level": "partial",
            "agreement_points": ["General discussion topic"],
            "disagreement_points": ["Specific details need clarification"],
            "total_messages": len(messages),
            "analysis_method": "placeholder"
        }

    def create_chat_room(
        self,
        topic: str,
        room_name: Optional[str] = None,
        roles: Optional[List[str]] = None,
        mode: str = "free_form",
        interaction_rules: Optional[Dict[str, Any]] = None,
        auto_recommend_roles: bool = True
    ) -> str:
        """Create a new chat room with enhanced configuration.
        
        Args:
            topic: The topic of the chat room.
            room_name: The name of the chat room. If None, a default name will be generated.
            roles: A list of role IDs to participate in the chat room.
            mode: The mode of the chat room (e.g., "free_form", "structured").
            interaction_rules: Mode-specific interaction rules.
            auto_recommend_roles: Whether to automatically recommend roles based on topic.
            
        Returns:
            The ID of the created chat room.
        """
        # Generate a default name if none is provided
        if not room_name:
            room_name = f"ChatRoom-{uuid.uuid4().hex[:8]}"
            
        # Use default interaction rules if none are provided
        if interaction_rules is None:
            interaction_rules = {}
            
        # Auto-recommend roles if requested and no roles provided
        if auto_recommend_roles and not roles and self.role_manager:
            recommended_roles = self.recommend_roles_for_topic(topic)
            if recommended_roles:
                roles = [role["id"] for role in recommended_roles[:3]]  # Use top 3 recommendations
            else:
                # Fallback to available roles
                available_roles = self.role_manager.list_roles()
                if available_roles:
                    roles = [available_roles[0].id]
                else:
                    roles = []
        elif not roles:
            roles = []
            
        # Create the chat room configuration
        config = ChatRoomConfig(
            name=room_name,
            topic=topic,
            roles=roles,
            mode=mode,
            interaction_rules=interaction_rules
        )
        
        # Delegate to the chat room manager to create the room
        room_id = self.chat_room_manager.create_chat_room(config)
        
        # Start a new session for the room
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        session_id = loop.run_until_complete(self.chat_session_service.start_session(room_id))
        
        # Set as current room
        self._current_room_id = room_id
        
        return room_id

    def send_message_to_room(self, room_id: Optional[str] = None, message: str = "", sender: str = "user") -> bool:
        """Send a message to a chat room.
        
        Args:
            room_id: The ID of the chat room. If None, uses current room.
            message: The message content.
            sender: The sender of the message.
            
        Returns:
            True if message was sent successfully, False otherwise.
        """
        target_room_id = room_id or self._current_room_id
        if not target_room_id:
            return False
        
        session_id = self.chat_session_service.get_session_by_room_id(target_room_id)
        if not session_id:
            return False

        try:
            import asyncio
            # Create message object with correct fields
            from .models import ChatMessage
            from datetime import datetime
            message_obj = ChatMessage(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                sender_id=sender,
                sender_type="user" if sender == "user" else "role",
                content=message,
                timestamp=datetime.now(),
                metadata={}
            )
            
            # Use chat session service to add message
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(
                self.chat_session_service.add_message(session_id, message_obj)
            )
        except Exception:
            return False

    def get_room_history(self, room_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the history of a chat room.
        
        Args:
            room_id: The ID of the chat room. If None, gets history for current room.
            
        Returns:
            A list of messages in the chat room.
        """
        target_room_id = room_id or self._current_room_id
        if not target_room_id:
            return []
        
        try:
            import asyncio
            # Get active session for the room
            session_id = self.chat_session_service.get_session_by_room_id(target_room_id)
            if not session_id:
                return []
            
            # Get messages from session service
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            messages = loop.run_until_complete(
                self.chat_session_service.get_messages(session_id)
            )
            
            # Convert to dictionary format
            return [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender": msg.sender_id,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            print(f"Error getting room history: {e}")
            return []

    def clear_room_history(self, room_id: Optional[str] = None) -> bool:
        """Clear the history of a chat room.
        
        Args:
            room_id: The ID of the chat room. If None, clears history for current room.
            
        Returns:
            True if the history was successfully cleared, False otherwise.
        """
        target_room_id = room_id or self._current_room_id
        if not target_room_id:
            return False
            
        try:
            import asyncio
            # Get active session for the room
            session_id = self.chat_session_service.get_session_by_room_id(target_room_id)
            if not session_id:
                return False
            
            # Clear messages from session by updating the session with an empty message list
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Update the session with an empty message list
            success = self.chat_session_service._update_session(session_id, messages=[])
            
            return success
        except Exception as e:
            print(f"Error clearing room history: {e}")
            return False

    def close_current_room(self) -> bool:
        """Close the current chat room.
        
        Returns:
            True if the room was successfully closed, False otherwise.
        """
        if not self._current_room_id:
            return False
        
        try:
            import asyncio
            # End the session for the current room
            # Get the actual session ID from the session service
            session_id = self.chat_session_service.get_session_by_room_id(self._current_room_id)
            if not session_id:
                return False
            
            # Use chat session service to end session
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is running, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.chat_session_service.end_session(session_id)
            )
            
            if success:
                self._current_room_id = None
                # Save the state to persist the change
                self.save_state()
            return success
        except Exception:
            return False

    def delete_room(self, room_id: str) -> bool:
        """Delete a chat room.
        
        Args:
            room_id: The ID of the chat room to delete.
            
        Returns:
            True if the room was successfully deleted, False otherwise.
        """
        try:
            # Delete from chat room manager
            success = self.chat_room_manager.delete_chat_room(room_id)
            
            # Clear current room if it was the deleted one
            if self._current_room_id == room_id:
                self._current_room_id = None
            
            return success
        except Exception:
            return False

    def get_current_room_id(self) -> Optional[str]:
        """Get the current active room ID.
        
        Returns:
            The current room ID or None if no room is active.
        """
        return self._current_room_id

    def set_current_room(self, room_id: str) -> bool:
        """Set the current active room.
        
        Args:
            room_id: The room ID to set as current.
            
        Returns:
            True if successful, False otherwise.
        """
        # Verify room exists
        if not self.chat_room_manager.get_chat_room(room_id):
            return False
        
        self._current_room_id = room_id
        return True