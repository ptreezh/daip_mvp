"""
Assistant Profile Management for Personal Assistant System

Handles assistant personality, preferences, and profile management.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AssistantProfile:
    """Assistant profile management"""

    def __init__(
        self,
        name: str,
        personality: str = "helpful and professional",
        specialization: str = "general assistance",
        preferences: Optional[dict[str, Any]] = None,
        description: str = "",
        profile_id: Optional[str] = None,
    ):
        self.id = profile_id or str(uuid.uuid4())
        self.name = name
        self.personality = personality
        self.specialization = specialization
        self.preferences = preferences or {}
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.is_active = True

    def update_personality(self, personality: str) -> None:
        """Update assistant personality"""
        self.personality = personality
        self.updated_at = datetime.now()
        logger.info(f"Updated personality for {self.name}")

    def update_specialization(self, specialization: str) -> None:
        """Update assistant specialization"""
        self.specialization = specialization
        self.updated_at = datetime.now()
        logger.info(f"Updated specialization for {self.name}")

    def set_preference(self, key: str, value: Any) -> None:
        """Set a preference"""
        self.preferences[key] = value
        self.updated_at = datetime.now()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference with default"""
        return self.preferences.get(key, default)

    def update_description(self, description: str) -> None:
        """Update profile description"""
        self.description = description
        self.updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "personality": self.personality,
            "specialization": self.specialization,
            "preferences": self.preferences,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssistantProfile":
        """Create profile from dictionary"""
        profile = cls(
            name=data["name"],
            personality=data.get("personality", "helpful and professional"),
            specialization=data.get("specialization", "general assistance"),
            preferences=data.get("preferences", {}),
            description=data.get("description", ""),
            profile_id=data.get("id"),
        )

        if "created_at" in data:
            profile.created_at = datetime.fromisoformat(data["created_at"])

        if "updated_at" in data:
            profile.updated_at = datetime.fromisoformat(data["updated_at"])

        if "is_active" in data:
            profile.is_active = data["is_active"]

        return profile

    def __str__(self) -> str:
        """String representation"""
        return f"AssistantProfile({self.name})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (
            f"AssistantProfile(id={self.id[:8]}..., name='{self.name}', "
            f"specialization='{self.specialization}')"
        )
