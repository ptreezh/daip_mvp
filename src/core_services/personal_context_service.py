"""Personal Context Service for managing user-specific context and background knowledge.

This service provides functionality for maintaining individual user profiles,
tracking interaction patterns, storing personal background knowledge, and
managing user-specific conversation history. It serves as a key component
of the Human User Intelligence Layer.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.core_services.user_profile_service import UserProfile

logger = logging.getLogger(__name__)


class PersonalContext(BaseModel):
    """Represents personal context information for a user.
    """
    user_id: str
    background_knowledge: list[dict[str, Any]] = Field(default_factory=list)
    interaction_patterns: dict[str, float] = Field(default_factory=dict)
    learning_preferences: dict[str, Any] = Field(default_factory=dict)
    expertise_areas: list[dict[str, Any]] = Field(default_factory=list)
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)


class PersonalContextServiceInterface(ABC):
    """Abstract interface for personal context services.
    
    This interface defines the contract that all personal context services must implement.
    It provides methods for managing user profiles, tracking interaction patterns,
    storing background knowledge, and managing conversation history.
    """
    
    @abstractmethod
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve comprehensive user profile.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            UserProfile if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_personal_context(self, user_id: str) -> Optional[PersonalContext]:
        """Retrieve personal context for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            PersonalContext if found, None otherwise
        """
        pass
    
    @abstractmethod
    def update_user_preferences(
        self, 
        user_id: str, 
        interaction_data: dict[str, Any]
    ) -> bool:
        """Learn from user interactions to improve personalization.
        
        Args:
            user_id: The ID of the user
            interaction_data: Data about the user interaction
            
        Returns:
            True if preferences were updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def add_background_knowledge(
        self, 
        user_id: str, 
        knowledge_item: dict[str, Any]
    ) -> bool:
        """Add background knowledge for a user.
        
        Args:
            user_id: The ID of the user
            knowledge_item: Background knowledge item to add
            
        Returns:
            True if knowledge was added successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_relevant_background(
        self, 
        user_id: str, 
        topic: str
    ) -> list[dict[str, Any]]:
        """Get user's relevant background knowledge for a topic.
        
        Args:
            user_id: The ID of the user
            topic: The topic to get background knowledge for
            
        Returns:
            List of relevant background knowledge items
        """
        pass
    
    @abstractmethod
    def add_conversation_entry(
        self, 
        user_id: str, 
        entry: dict[str, Any]
    ) -> bool:
        """Add an entry to the user's conversation history.
        
        Args:
            user_id: The ID of the user
            entry: Conversation entry to add
            
        Returns:
            True if entry was added successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent conversation history for a user.
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation history entries
        """
        pass


class BasicPersonalContextService(PersonalContextServiceInterface):
    """Basic implementation of the PersonalContextService interface.
    
    This implementation provides simple personal context management functionality
    using the UserProfileService. It serves as a placeholder that can be replaced
    with more sophisticated implementations in the future.
    """
    
    def __init__(self, user_profile_service, memory_service=None):
        """Initialize the BasicPersonalContextService.
        
        Args:
            user_profile_service: The UserProfileService instance to use
            memory_service: Optional MemoryService for more advanced functionality
        """
        self.user_profile_service = user_profile_service
        self.memory_service = memory_service
        self._context_cache = {}  # Simple in-memory cache
        logger.info("BasicPersonalContextService initialized")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile using the UserProfileService.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            UserProfile if found, None otherwise
        """
        return self.user_profile_service.get_profile(user_id)
    
    def get_personal_context(self, user_id: str) -> Optional[PersonalContext]:
        """Retrieve or create personal context for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            PersonalContext if found or created, None if user doesn't exist
        """
        # Check cache first
        if user_id in self._context_cache:
            return self._context_cache[user_id]
        
        # Get user profile
        profile = self.get_user_profile(user_id)
        if not profile:
            return None
        
        # Create personal context from profile
        context = PersonalContext(
            user_id=user_id,
            background_knowledge=[
                {"content": item, "source": "user_profile", "timestamp": datetime.now().isoformat()}
                for item in profile.background_knowledge
            ],
            interaction_patterns={
                "intent_patterns": profile.intent_patterns
            },
            learning_preferences=profile.preferences.get("learning", {}),
            expertise_areas=[
                {"area": area, "level": level}
                for area, level in profile.preferences.get("expertise", {}).items()
            ],
            conversation_history=[
                entry for entry in profile.interaction_history
                if entry.get("type") == "conversation"
            ][:20]  # Limit to 20 most recent entries
        )
        
        # Cache the context
        self._context_cache[user_id] = context
        
        return context
    
    def update_user_preferences(
        self, 
        user_id: str, 
        interaction_data: dict[str, Any]
    ) -> bool:
        """Update user preferences based on interaction data.
        
        Args:
            user_id: The ID of the user
            interaction_data: Data about the user interaction
            
        Returns:
            True if preferences were updated successfully, False otherwise
        """
        try:
            # Get user profile
            profile = self.get_user_profile(user_id)
            if not profile:
                return False
            
            # Extract preference updates from interaction data
            preference_updates = {}
            
            # Update learning preferences
            if "learning_style" in interaction_data:
                if "learning" not in profile.preferences:
                    profile.preferences["learning"] = {}
                profile.preferences["learning"]["style"] = interaction_data["learning_style"]
                preference_updates["preferences"] = profile.preferences
            
            # Update expertise areas
            if "expertise" in interaction_data:
                if "expertise" not in profile.preferences:
                    profile.preferences["expertise"] = {}
                profile.preferences["expertise"].update(interaction_data["expertise"])
                preference_updates["preferences"] = profile.preferences
            
            # Update communication preferences
            if "communication" in interaction_data:
                if "communication" not in profile.preferences:
                    profile.preferences["communication"] = {}
                profile.preferences["communication"].update(interaction_data["communication"])
                preference_updates["preferences"] = profile.preferences
            
            # Update profile if we have changes
            if preference_updates:
                self.user_profile_service.update_profile(user_id, **preference_updates)
                
                # Invalidate cache
                if user_id in self._context_cache:
                    del self._context_cache[user_id]
                
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Error updating user preferences: {e}")
            return False
    
    def add_background_knowledge(
        self, 
        user_id: str, 
        knowledge_item: dict[str, Any]
    ) -> bool:
        """Add background knowledge for a user.
        
        Args:
            user_id: The ID of the user
            knowledge_item: Background knowledge item to add
            
        Returns:
            True if knowledge was added successfully, False otherwise
        """
        try:
            # Get user profile
            profile = self.get_user_profile(user_id)
            if not profile:
                return False
            
            # Extract content from knowledge item
            content = knowledge_item.get("content")
            if not content:
                return False
            
            # Add to background knowledge
            if content not in profile.background_knowledge:
                profile.background_knowledge.append(content)
                
                # Update profile
                self.user_profile_service.update_profile(
                    user_id, 
                    background_knowledge=profile.background_knowledge
                )
                
                # Invalidate cache
                if user_id in self._context_cache:
                    del self._context_cache[user_id]
                
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Error adding background knowledge: {e}")
            return False
    
    def get_relevant_background(
        self, 
        user_id: str, 
        topic: str
    ) -> list[dict[str, Any]]:
        """Get user's relevant background knowledge for a topic.
        
        Args:
            user_id: The ID of the user
            topic: The topic to get background knowledge for
            
        Returns:
            List of relevant background knowledge items
        """
        try:
            # Get personal context
            context = self.get_personal_context(user_id)
            if not context:
                return []
            
            # Simple keyword matching for relevance
            topic_lower = topic.lower()
            relevant_items = []
            
            for item in context.background_knowledge:
                content = item.get("content", "").lower()
                if topic_lower in content or any(
                    keyword in content 
                    for keyword in topic_lower.split()
                    if len(keyword) > 3
                ):
                    relevant_items.append(item)
            
            # Use memory service for more advanced retrieval if available
            if self.memory_service and hasattr(self.memory_service, "search_memories"):
                try:
                    # This is a placeholder for more sophisticated memory retrieval
                    # In a real implementation, this would use the memory service to find relevant memories
                    pass
                except Exception as e:
                    logger.warning(f"Error using memory service for background retrieval: {e}")
            
            return relevant_items
        except Exception as e:
            logger.warning(f"Error getting relevant background: {e}")
            return []
    
    def add_conversation_entry(
        self, 
        user_id: str, 
        entry: dict[str, Any]
    ) -> bool:
        """Add an entry to the user's conversation history.
        
        Args:
            user_id: The ID of the user
            entry: Conversation entry to add
            
        Returns:
            True if entry was added successfully, False otherwise
        """
        try:
            # Ensure entry has required fields
            if "content" not in entry:
                return False
            
            # Format the entry
            formatted_entry = {
                "type": "conversation",
                "content": entry["content"],
                "timestamp": entry.get("timestamp", datetime.now().isoformat()),
                "metadata": entry.get("metadata", {})
            }
            
            # Add to interaction history
            success = self.user_profile_service.add_interaction_to_profile(
                user_id,
                "conversation",
                entry["content"],
                entry.get("metadata", {})
            )
            
            # Invalidate cache if successful
            if success and user_id in self._context_cache:
                del self._context_cache[user_id]
            
            return success
        except Exception as e:
            logger.warning(f"Error adding conversation entry: {e}")
            return False
    
    def get_conversation_history(
        self, 
        user_id: str, 
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent conversation history for a user.
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation history entries
        """
        try:
            # Get user profile
            profile = self.get_user_profile(user_id)
            if not profile:
                return []
            
            # Filter conversation entries
            conversation_entries = [
                entry for entry in profile.interaction_history
                if entry.get("type") == "conversation"
            ]
            
            # Sort by timestamp (newest first) and limit
            sorted_entries = sorted(
                conversation_entries,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
            
            return sorted_entries[:limit]
        except Exception as e:
            logger.warning(f"Error getting conversation history: {e}")
            return []