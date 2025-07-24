"""
Role validation and assignment service for the Virtual Role Chat System.

This module provides functionality to validate role existence, initialize roles
with appropriate context, and manage role assignments in chat rooms.
"""

import logging
from typing import Dict, List, Optional, Set

from src.core_services.role_manager import RoleManager, Role
from .models import ChatRoomConfig, ValidationResult

logger = logging.getLogger(__name__)


class RoleValidationError(Exception):
    """Exception raised when role validation fails."""
    pass


class RoleValidator:
    """Service for validating and managing role assignments in chat rooms."""
    
    def __init__(self, role_manager: Optional[RoleManager] = None):
        """Initialize the RoleValidator.
        
        Args:
            role_manager: Optional RoleManager instance. If None, creates a new one.
        """
        self.role_manager = role_manager or RoleManager()
        self._role_cache: Dict[str, Role] = {}
    
    def validate_roles(self, role_ids: List[str]) -> ValidationResult:
        """Validate that all specified roles exist and are available.
        
        Args:
            role_ids: List of role IDs to validate.
            
        Returns:
            ValidationResult indicating whether all roles are valid.
        """
        if not role_ids:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning="No roles specified. At least one role is required.",
                suggested_correction="Add at least one role to the chat room configuration."
            )
        
        missing_roles = []
        invalid_roles = []
        valid_roles = []
        
        for role_id in role_ids:
            try:
                role = self._get_role(role_id)
                if role is None:
                    missing_roles.append(role_id)
                elif not self._is_role_valid(role):
                    invalid_roles.append(role_id)
                else:
                    valid_roles.append(role_id)
            except Exception as e:
                logger.error(f"Error validating role {role_id}: {e}")
                invalid_roles.append(role_id)
        
        if missing_roles or invalid_roles:
            error_parts = []
            if missing_roles:
                error_parts.append(f"Missing roles: {', '.join(missing_roles)}")
            if invalid_roles:
                error_parts.append(f"Invalid roles: {', '.join(invalid_roles)}")
            
            reasoning = "; ".join(error_parts)
            suggested_correction = self._generate_role_suggestions(missing_roles + invalid_roles)
            
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=reasoning,
                suggested_correction=suggested_correction
            )
        
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning=f"All {len(valid_roles)} roles are valid and available.",
            suggested_correction=None
        )
    
    def validate_chat_room_config(self, config: ChatRoomConfig) -> ValidationResult:
        """Validate the role configuration for a chat room.
        
        Args:
            config: The chat room configuration to validate.
            
        Returns:
            ValidationResult indicating whether the configuration is valid.
        """
        # First validate that roles exist
        role_validation = self.validate_roles(config.roles)
        if not role_validation.is_valid:
            return role_validation
        
        # Check for duplicate roles
        if len(config.roles) != len(set(config.roles)):
            duplicates = [role for role in set(config.roles) if config.roles.count(role) > 1]
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Duplicate roles found: {', '.join(duplicates)}",
                suggested_correction="Remove duplicate roles from the configuration."
            )
        
        # Validate role compatibility with chat mode
        compatibility_result = self._validate_mode_compatibility(config.roles, config.mode)
        if not compatibility_result.is_valid:
            return compatibility_result
        
        # Check minimum and maximum role limits
        min_roles = self._get_min_roles_for_mode(config.mode)
        max_roles = self._get_max_roles_for_mode(config.mode)
        
        if len(config.roles) < min_roles:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Too few roles for {config.mode} mode. Minimum: {min_roles}, provided: {len(config.roles)}",
                suggested_correction=f"Add at least {min_roles - len(config.roles)} more roles."
            )
        
        if len(config.roles) > max_roles:
            return ValidationResult(
                is_valid=False,
                confidence=1.0,
                reasoning=f"Too many roles for {config.mode} mode. Maximum: {max_roles}, provided: {len(config.roles)}",
                suggested_correction=f"Remove at least {len(config.roles) - max_roles} roles."
            )
        
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning="Chat room configuration is valid.",
            suggested_correction=None
        )
    
    def initialize_roles_for_room(self, role_ids: List[str], room_context: Dict) -> Dict[str, Dict]:
        """Initialize roles with appropriate context for a chat room.
        
        Args:
            role_ids: List of role IDs to initialize.
            room_context: Context information about the chat room.
            
        Returns:
            Dictionary mapping role IDs to their initialized context.
        """
        initialized_roles = {}
        
        for role_id in role_ids:
            try:
                role = self._get_role(role_id)
                if role is None:
                    logger.error(f"Cannot initialize missing role: {role_id}")
                    continue
                
                role_context = self._create_role_context(role, room_context)
                initialized_roles[role_id] = role_context
                logger.info(f"Initialized role: {role_id}")
                
            except Exception as e:
                logger.error(f"Error initializing role {role_id}: {e}")
        
        return initialized_roles
    
    def get_available_roles(self) -> List[Dict[str, str]]:
        """Get a list of all available roles.
        
        Returns:
            List of dictionaries containing role information.
        """
        roles = self.role_manager.list_roles()
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "capabilities": role.capabilities
            }
            for role in roles
        ]
    
    def get_roles_by_capability(self, capability: str) -> List[str]:
        """Get roles that have a specific capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            List of role IDs that have the specified capability.
        """
        matching_roles = []
        roles = self.role_manager.list_roles()
        
        for role in roles:
            if capability.lower() in [cap.lower() for cap in role.capabilities]:
                matching_roles.append(role.id)
        
        return matching_roles
    
    def suggest_roles_for_topic(self, topic: str, max_suggestions: int = 5) -> List[str]:
        """Suggest roles that might be relevant for a given topic.
        
        Args:
            topic: The topic to find relevant roles for.
            max_suggestions: Maximum number of role suggestions to return.
            
        Returns:
            List of suggested role IDs.
        """
        roles = self.role_manager.list_roles()
        scored_roles = []
        
        topic_lower = topic.lower()
        
        for role in roles:
            score = 0
            
            # Check if topic keywords appear in role description
            if any(word in role.description.lower() for word in topic_lower.split()):
                score += 2
            
            # Check if topic keywords appear in role name
            if any(word in role.name.lower() for word in topic_lower.split()):
                score += 3
            
            # Check capabilities
            for capability in role.capabilities:
                if any(word in capability.lower() for word in topic_lower.split()):
                    score += 1
            
            if score > 0:
                scored_roles.append((role.id, score))
        
        # Sort by score and return top suggestions
        scored_roles.sort(key=lambda x: x[1], reverse=True)
        return [role_id for role_id, _ in scored_roles[:max_suggestions]]
    
    def _get_role(self, role_id: str) -> Optional[Role]:
        """Get a role by ID, using cache when possible.
        
        Args:
            role_id: The ID of the role to retrieve.
            
        Returns:
            The Role object if found, None otherwise.
        """
        if role_id not in self._role_cache:
            role = self.role_manager.get_role_by_id(role_id)
            if role:
                self._role_cache[role_id] = role
            return role
        return self._role_cache[role_id]
    
    def _is_role_valid(self, role: Role) -> bool:
        """Check if a role is valid and properly configured.
        
        Args:
            role: The role to validate.
            
        Returns:
            True if the role is valid, False otherwise.
        """
        # Check required fields
        if not role.id or not role.name or not role.system_prompt:
            return False
        
        # Check that system prompt is not empty
        if not role.system_prompt.strip():
            return False
        
        # Additional validation can be added here
        return True
    
    def _validate_mode_compatibility(self, role_ids: List[str], mode: str) -> ValidationResult:
        """Validate that roles are compatible with the chat mode.
        
        Args:
            role_ids: List of role IDs to check.
            mode: The chat mode to validate against.
            
        Returns:
            ValidationResult indicating compatibility.
        """
        # For debate mode, we might want specific types of roles
        if mode == "debate":
            # Check if we have roles that can take opposing positions
            roles = [self._get_role(role_id) for role_id in role_ids if self._get_role(role_id)]
            
            # This is a simplified check - in a real implementation,
            # you might have more sophisticated compatibility rules
            if len(roles) < 2:
                return ValidationResult(
                    is_valid=False,
                    confidence=0.8,
                    reasoning="Debate mode requires at least 2 roles to enable meaningful debate.",
                    suggested_correction="Add more roles to enable debate functionality."
                )
        
        return ValidationResult(
            is_valid=True,
            confidence=1.0,
            reasoning="Roles are compatible with the selected mode.",
            suggested_correction=None
        )
    
    def _get_min_roles_for_mode(self, mode: str) -> int:
        """Get the minimum number of roles required for a chat mode.
        
        Args:
            mode: The chat mode.
            
        Returns:
            Minimum number of roles required.
        """
        mode_requirements = {
            "free_form": 1,
            "structured": 1,
            "debate": 2
        }
        return mode_requirements.get(mode, 1)
    
    def _get_max_roles_for_mode(self, mode: str) -> int:
        """Get the maximum number of roles allowed for a chat mode.
        
        Args:
            mode: The chat mode.
            
        Returns:
            Maximum number of roles allowed.
        """
        mode_requirements = {
            "free_form": 10,
            "structured": 8,
            "debate": 6
        }
        return mode_requirements.get(mode, 10)
    
    def _generate_role_suggestions(self, invalid_roles: List[str]) -> str:
        """Generate suggestions for invalid or missing roles.
        
        Args:
            invalid_roles: List of invalid role IDs.
            
        Returns:
            Suggestion string for the user.
        """
        available_roles = self.get_available_roles()
        if not available_roles:
            return "No roles are currently available. Please add role definitions to the system."
        
        # Suggest similar roles based on name similarity
        suggestions = []
        for invalid_role in invalid_roles[:3]:  # Limit to first 3 invalid roles
            similar_roles = [
                role["id"] for role in available_roles
                if invalid_role.lower() in role["name"].lower() or 
                   role["name"].lower() in invalid_role.lower()
            ]
            if similar_roles:
                suggestions.append(f"For '{invalid_role}', consider: {', '.join(similar_roles[:3])}")
        
        if suggestions:
            return "Suggestions: " + "; ".join(suggestions)
        else:
            available_ids = [role["id"] for role in available_roles[:5]]
            return f"Available roles include: {', '.join(available_ids)}"
    
    def _create_role_context(self, role: Role, room_context: Dict) -> Dict:
        """Create initialization context for a role in a chat room.
        
        Args:
            role: The role to initialize.
            room_context: Context information about the chat room.
            
        Returns:
            Dictionary containing the role's initialization context.
        """
        return {
            "role_id": role.id,
            "role_name": role.name,
            "role_description": role.description,
            "system_prompt": role.system_prompt,
            "capabilities": role.capabilities,
            "room_topic": room_context.get("topic", ""),
            "room_mode": room_context.get("mode", "free_form"),
            "other_roles": room_context.get("other_roles", []),
            "interaction_rules": room_context.get("interaction_rules", {}),
            "initialized_at": room_context.get("created_at"),
        }