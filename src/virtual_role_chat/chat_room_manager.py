"""ChatRoomManager implementation for the Virtual Role Chat System.

This module provides the implementation of ChatRoomManager that handles
the creation, configuration, and lifecycle management of chat rooms.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config_validator import ConfigValidationError, ConfigValidator
from .interfaces import ChatRoomManagerInterface
from .models import (
    ChatRoom,
    ChatRoomConfig,
    ChatRoomID,
    ChatRoomSummary,
)
from .role_validator import RoleValidationError, RoleValidator


class ChatRoomManager(ChatRoomManagerInterface):
    """Implementation of ChatRoomManager for managing chat rooms."""
    
    def __init__(self, storage_path: Optional[str] = None, role_validator: Optional[RoleValidator] = None, config_validator: Optional[ConfigValidator] = None):
        """Initialize the ChatRoomManager.
        
        Args:
            storage_path: Path to store chat room data. If None, uses in-memory storage.
            role_validator: Optional RoleValidator instance. If None, creates a new one.
            config_validator: Optional ConfigValidator instance. If None, creates a new one.
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self._rooms: dict[ChatRoomID, ChatRoom] = {}
        self.role_validator = role_validator or RoleValidator()
        self.config_validator = config_validator or ConfigValidator()
        self._load_rooms()
    
    def _load_rooms(self) -> None:
        """Load chat rooms from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, encoding='utf-8') as f:
                rooms_data = json.load(f)
                
            for room_data in rooms_data:
                # Convert datetime strings back to datetime objects
                room_data['created_at'] = datetime.fromisoformat(room_data['created_at'])
                room_data['updated_at'] = datetime.fromisoformat(room_data['updated_at'])
                
                room = ChatRoom(**room_data)
                self._rooms[room.id] = room
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load chat rooms from storage: {e}")
    
    def _save_rooms(self) -> None:
        """Save chat rooms to storage."""
        if not self.storage_path:
            return
        
        try:
            # Ensure the directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert rooms to serializable format
            rooms_data = []
            for room in self._rooms.values():
                room_dict = room.model_dump()
                # Convert datetime objects to ISO format strings
                room_dict['created_at'] = room.created_at.isoformat()
                room_dict['updated_at'] = room.updated_at.isoformat()
                rooms_data.append(room_dict)
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(rooms_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save chat rooms to storage: {e}")
    
    def create_chat_room(self, config: ChatRoomConfig) -> ChatRoomID:
        """Create a new chat room with the given configuration.
        
        Args:
            config: The configuration for the chat room.
            
        Returns:
            The ID of the created chat room.
            
        Raises:
            RoleValidationError: If the role configuration is invalid.
        """
        # Validate the chat room configuration (both config and roles)
        config_validation = self.config_validator.validate_config(config)
        if not config_validation.is_valid:
            raise ConfigValidationError(f"Invalid chat room configuration: {config_validation.reasoning}")
        
        role_validation = self.role_validator.validate_chat_room_config(config)
        if not role_validation.is_valid:
            raise RoleValidationError(f"Invalid role configuration: {role_validation.reasoning}")
        
        # Generate a unique ID for the chat room
        room_id = f"room_{uuid.uuid4().hex[:8]}"
        
        # Create the chat room
        now = datetime.now()
        room = ChatRoom(
            id=room_id,
            config=config,
            created_at=now,
            updated_at=now,
            status="active"
        )
        
        # Initialize roles for the room
        room_context = {
            "topic": config.topic,
            "mode": config.mode,
            "other_roles": config.roles,
            "interaction_rules": config.interaction_rules,
            "created_at": now
        }
        initialized_roles = self.role_validator.initialize_roles_for_room(config.roles, room_context)
        
        # Store the room
        self._rooms[room_id] = room
        self._save_rooms()
        
        return room_id
    
    def get_chat_room(self, room_id: ChatRoomID) -> ChatRoom:
        """Get a chat room by its ID.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            The chat room.
            
        Raises:
            ValueError: If the chat room does not exist.
        """
        if room_id not in self._rooms:
            raise ValueError(f"Chat room with ID '{room_id}' does not exist")
        
        return self._rooms[room_id]
    
    def update_chat_room(self, room_id: ChatRoomID, config: ChatRoomConfig) -> bool:
        """Update a chat room with the given configuration.
        
        Args:
            room_id: The ID of the chat room.
            config: The new configuration for the chat room.
            
        Returns:
            True if the chat room was updated successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.
            RoleValidationError: If the new role configuration is invalid.
        """
        if room_id not in self._rooms:
            raise ValueError(f"Chat room with ID '{room_id}' does not exist")
        
        try:
            # Validate the new configuration (both config and roles)
            config_validation = self.config_validator.validate_config(config)
            if not config_validation.is_valid:
                raise ConfigValidationError(f"Invalid chat room configuration: {config_validation.reasoning}")
            
            role_validation = self.role_validator.validate_chat_room_config(config)
            if not role_validation.is_valid:
                raise RoleValidationError(f"Invalid role configuration: {role_validation.reasoning}")
            
            # Update the room configuration
            room = self._rooms[room_id]
            updated_room = ChatRoom(
                id=room.id,
                config=config,
                created_at=room.created_at,
                updated_at=datetime.now(),
                status=room.status
            )
            
            # Re-initialize roles if they changed
            if set(config.roles) != set(room.config.roles):
                room_context = {
                    "topic": config.topic,
                    "mode": config.mode,
                    "other_roles": config.roles,
                    "interaction_rules": config.interaction_rules,
                    "created_at": room.created_at
                }
                initialized_roles = self.role_validator.initialize_roles_for_room(config.roles, room_context)
            
            self._rooms[room_id] = updated_room
            self._save_rooms()
            
            return True
            
        except (RoleValidationError, ConfigValidationError):
            raise  # Re-raise validation errors
        except Exception as e:
            print(f"Error updating chat room {room_id}: {e}")
            return False
    
    def delete_chat_room(self, room_id: ChatRoomID) -> bool:
        """Delete a chat room.
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            True if the chat room was deleted successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.
        """
        if room_id not in self._rooms:
            raise ValueError(f"Chat room with ID '{room_id}' does not exist")
        
        try:
            # Remove the room
            del self._rooms[room_id]
            self._save_rooms()
            
            return True
            
        except Exception as e:
            print(f"Error deleting chat room {room_id}: {e}")
            return False
    
    def list_chat_rooms(self) -> list[ChatRoomSummary]:
        """List all chat rooms.
        
        Returns:
            A list of chat room summaries.
        """
        summaries = []
        
        for room in self._rooms.values():
            summary = ChatRoomSummary(
                id=room.id,
                name=room.config.name,
                topic=room.config.topic,
                role_count=len(room.config.roles),
                message_count=0,  # Will be updated when sessions are implemented
                status=room.status,
                last_active=room.updated_at
            )
            summaries.append(summary)
        
        # Sort by last active time (most recent first)
        summaries.sort(key=lambda x: x.last_active, reverse=True)
        
        return summaries
    
    def archive_chat_room(self, room_id: ChatRoomID) -> bool:
        """Archive a chat room (set status to archived).
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            True if the chat room was archived successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.
        """
        if room_id not in self._rooms:
            raise ValueError(f"Chat room with ID '{room_id}' does not exist")
        
        try:
            room = self._rooms[room_id]
            archived_room = ChatRoom(
                id=room.id,
                config=room.config,
                created_at=room.created_at,
                updated_at=datetime.now(),
                status="archived"
            )
            
            self._rooms[room_id] = archived_room
            self._save_rooms()
            
            return True
            
        except Exception as e:
            print(f"Error archiving chat room {room_id}: {e}")
            return False
    
    def activate_chat_room(self, room_id: ChatRoomID) -> bool:
        """Activate a chat room (set status to active).
        
        Args:
            room_id: The ID of the chat room.
            
        Returns:
            True if the chat room was activated successfully, False otherwise.
            
        Raises:
            ValueError: If the chat room does not exist.
        """
        if room_id not in self._rooms:
            raise ValueError(f"Chat room with ID '{room_id}' does not exist")
        
        try:
            room = self._rooms[room_id]
            activated_room = ChatRoom(
                id=room.id,
                config=room.config,
                created_at=room.created_at,
                updated_at=datetime.now(),
                status="active"
            )
            
            self._rooms[room_id] = activated_room
            self._save_rooms()
            
            return True
            
        except Exception as e:
            print(f"Error activating chat room {room_id}: {e}")
            return False
    
    def get_room_count(self) -> int:
        """Get the total number of chat rooms.
        
        Returns:
            The total number of chat rooms.
        """
        return len(self._rooms)
    
    def get_active_rooms(self) -> list[ChatRoom]:
        """Get all active chat rooms.
        
        Returns:
            A list of active chat rooms.
        """
        return [room for room in self._rooms.values() if room.status == "active"]
    
    def get_archived_rooms(self) -> list[ChatRoom]:
        """Get all archived chat rooms.
        
        Returns:
            A list of archived chat rooms.
        """
        return [room for room in self._rooms.values() if room.status == "archived"]
    
    def validate_room_config(self, config: ChatRoomConfig) -> dict[str, any]:
        """Validate a chat room configuration without creating the room.
        
        Args:
            config: The configuration to validate.
            
        Returns:
            Dictionary containing validation results and suggestions.
        """
        # Validate configuration structure and rules
        config_validation = self.config_validator.validate_config(config)
        
        # Validate roles
        role_validation = self.role_validator.validate_chat_room_config(config)
        
        # Combine results
        overall_valid = config_validation.is_valid and role_validation.is_valid
        
        reasons = []
        suggestions = []
        
        if not config_validation.is_valid:
            reasons.append(f"Configuration: {config_validation.reasoning}")
            if config_validation.suggested_correction:
                suggestions.append(config_validation.suggested_correction)
        
        if not role_validation.is_valid:
            reasons.append(f"Roles: {role_validation.reasoning}")
            if role_validation.suggested_correction:
                suggestions.append(role_validation.suggested_correction)
        
        return {
            "is_valid": overall_valid,
            "confidence": min(config_validation.confidence, role_validation.confidence),
            "reasoning": "; ".join(reasons) if reasons else "Configuration is valid",
            "suggested_correction": "; ".join(suggestions) if suggestions else None,
            "available_roles": self.role_validator.get_available_roles(),
            "suggested_roles": self.role_validator.suggest_roles_for_topic(config.topic) if config.topic else [],
            "mode_requirements": self.config_validator.get_mode_requirements(config.mode),
            "suggested_rules": self.config_validator.suggest_rules_for_mode(config.mode)
        }
    
    def get_available_roles(self) -> list[dict[str, str]]:
        """Get all available roles that can be used in chat rooms.
        
        Returns:
            List of available roles with their information.
        """
        return self.role_validator.get_available_roles()
    
    def suggest_roles_for_topic(self, topic: str, max_suggestions: int = 5) -> list[str]:
        """Suggest roles that might be relevant for a given topic.
        
        Args:
            topic: The topic to find relevant roles for.
            max_suggestions: Maximum number of suggestions to return.
            
        Returns:
            List of suggested role IDs.
        """
        return self.role_validator.suggest_roles_for_topic(topic, max_suggestions)
    
    def get_rooms_by_role(self, role_id: str) -> list[ChatRoomSummary]:
        """Get all chat rooms that include a specific role.
        
        Args:
            role_id: The role ID to search for.
            
        Returns:
            List of chat room summaries that include the role.
        """
        matching_rooms = []
        
        for room in self._rooms.values():
            if role_id in room.config.roles:
                summary = ChatRoomSummary(
                    id=room.id,
                    name=room.config.name,
                    topic=room.config.topic,
                    role_count=len(room.config.roles),
                    message_count=0,  # Will be updated when sessions are implemented
                    status=room.status,
                    last_active=room.updated_at
                )
                matching_rooms.append(summary)
        
        # Sort by last active time (most recent first)
        matching_rooms.sort(key=lambda x: x.last_active, reverse=True)
        
        return matching_rooms
    
    def get_rooms_by_topic_keyword(self, keyword: str) -> list[ChatRoomSummary]:
        """Get chat rooms that have a keyword in their topic.
        
        Args:
            keyword: The keyword to search for in topics.
            
        Returns:
            List of matching chat room summaries.
        """
        matching_rooms = []
        keyword_lower = keyword.lower()
        
        for room in self._rooms.values():
            if keyword_lower in room.config.topic.lower():
                summary = ChatRoomSummary(
                    id=room.id,
                    name=room.config.name,
                    topic=room.config.topic,
                    role_count=len(room.config.roles),
                    message_count=0,  # Will be updated when sessions are implemented
                    status=room.status,
                    last_active=room.updated_at
                )
                matching_rooms.append(summary)
        
        # Sort by last active time (most recent first)
        matching_rooms.sort(key=lambda x: x.last_active, reverse=True)
        
        return matching_rooms
    
    def get_valid_modes(self) -> list[str]:
        """Get all valid chat room modes.
        
        Returns:
            List of valid mode names.
        """
        return self.config_validator.get_valid_modes()
    
    def get_mode_requirements(self, mode: str) -> dict[str, Any]:
        """Get requirements for a specific chat mode.
        
        Args:
            mode: The mode to get requirements for.
            
        Returns:
            Dictionary containing mode requirements.
        """
        return self.config_validator.get_mode_requirements(mode)
    
    def suggest_rules_for_mode(self, mode: str) -> dict[str, list[str]]:
        """Get suggested rules for a specific mode.
        
        Args:
            mode: The mode to get suggestions for.
            
        Returns:
            Dictionary with required and optional rules.
        """
        return self.config_validator.suggest_rules_for_mode(mode)
    
    def validate_interaction_rules(self, rules: dict[str, Any], mode: str) -> dict[str, Any]:
        """Validate interaction rules for a specific mode.
        
        Args:
            rules: The interaction rules to validate.
            mode: The chat mode.
            
        Returns:
            Dictionary containing validation results.
        """
        validation_result = self.config_validator._validate_interaction_rules(rules, mode)
        
        return {
            "is_valid": validation_result.is_valid,
            "confidence": validation_result.confidence,
            "reasoning": validation_result.reasoning,
            "suggested_correction": validation_result.suggested_correction
        }