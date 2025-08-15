"""User Profile Service for managing user profiles and sessions.

This service provides functionality for creating, retrieving, and updating user profiles,
as well as managing user sessions. It serves as the foundation for the Human User Intelligence Layer.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UserSession(BaseModel):
    """Represents a user session with authentication and context information.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class UserProfile(BaseModel):
    """Represents a user profile with preferences, interaction history, and other metadata.
    This model serves as the foundation for personalized experiences in the Human User Intelligence Layer.
    """
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    preferences: dict[str, Any] = Field(default_factory=dict)
    background_knowledge: list[str] = Field(default_factory=list)
    interaction_history: list[dict[str, Any]] = Field(default_factory=list)
    intent_patterns: dict[str, float] = Field(default_factory=dict)
    sessions: list[str] = Field(default_factory=list)  # List of session IDs
    metadata: dict[str, Any] = Field(default_factory=dict)


class UserProfileService:
    """Service for managing user profiles and sessions.
    
    This service provides functionality for creating, retrieving, and updating user profiles,
    as well as managing user sessions. It serves as the foundation for the Human User Intelligence Layer.
    """
    
    def __init__(self, data_dir: str = "data/user_profiles"):
        """Initialize the UserProfileService.
        
        Args:
            data_dir: Directory where user profiles and sessions are stored
        """
        self.data_dir = Path(data_dir)
        self.profiles_dir = self.data_dir / "profiles"
        self.sessions_dir = self.data_dir / "sessions"
        
        # Create directories if they don't exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory caches for active profiles and sessions
        self._profile_cache: dict[str, UserProfile] = {}
        self._session_cache: dict[str, UserSession] = {}
        
        # Load active sessions into memory
        self._load_active_sessions()
        
        logger.info(f"UserProfileService initialized with data directory: {self.data_dir}")
    
    def _load_active_sessions(self) -> None:
        """Load active sessions from disk into memory cache."""
        if not self.sessions_dir.exists():
            return
            
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
                    session = UserSession(**session_data)
                    
                    # Skip expired or inactive sessions
                    if not session.is_active:
                        continue
                        
                    if session.expires_at and datetime.now() > session.expires_at:
                        session.is_active = False
                        self._save_session(session)
                        continue
                        
                    self._session_cache[session.session_id] = session
            except Exception as e:
                logger.warning(f"Error loading session from {session_file}: {e}")
    
    def _get_profile_path(self, user_id: str) -> Path:
        """Get the file path for a user profile."""
        return self.profiles_dir / f"{user_id}.json"
    
    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a user session."""
        return self.sessions_dir / f"{session_id}.json"
    
    def _save_profile(self, profile: UserProfile) -> None:
        """Save a user profile to disk."""
        profile_path = self._get_profile_path(profile.user_id)
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile.model_dump(), f, default=str, indent=2)
        self._profile_cache[profile.user_id] = profile
    
    def _save_session(self, session: UserSession) -> None:
        """Save a user session to disk."""
        session_path = self._get_session_path(session.session_id)
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(session.model_dump(), f, default=str, indent=2)
        if session.is_active:
            self._session_cache[session.session_id] = session
        elif session.session_id in self._session_cache:
            del self._session_cache[session.session_id]
    
    def create_profile(self, username: str, **kwargs) -> UserProfile:
        """Create a new user profile.
        
        Args:
            username: The username for the new profile
            **kwargs: Additional profile attributes
            
        Returns:
            The newly created UserProfile
        """
        profile = UserProfile(username=username, **kwargs)
        self._save_profile(profile)
        logger.info(f"Created new user profile for {username} with ID {profile.user_id}")
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user profile by ID.
        
        Args:
            user_id: The ID of the user profile to retrieve
            
        Returns:
            The UserProfile if found, None otherwise
        """
        # Check cache first
        if user_id in self._profile_cache:
            return self._profile_cache[user_id]
        
        # Try to load from disk
        profile_path = self._get_profile_path(user_id)
        if not profile_path.exists():
            return None
            
        try:
            with open(profile_path, encoding="utf-8") as f:
                profile_data = json.load(f)
                profile = UserProfile(**profile_data)
                self._profile_cache[user_id] = profile
                return profile
        except Exception as e:
            logger.error(f"Error loading profile {user_id}: {e}")
            return None
    
    def get_profile_by_username(self, username: str) -> Optional[UserProfile]:
        """Get a user profile by username.
        
        Args:
            username: The username to search for
            
        Returns:
            The UserProfile if found, None otherwise
        """
        # This is inefficient for large numbers of users, but works for now
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, encoding="utf-8") as f:
                    profile_data = json.load(f)
                    if profile_data.get("username") == username:
                        profile = UserProfile(**profile_data)
                        self._profile_cache[profile.user_id] = profile
                        return profile
            except Exception as e:
                logger.warning(f"Error reading profile file {profile_file}: {e}")
        
        return None
    
    def update_profile(self, user_id: str, **updates) -> Optional[UserProfile]:
        """Update a user profile.
        
        Args:
            user_id: The ID of the user profile to update
            **updates: The profile attributes to update
            
        Returns:
            The updated UserProfile if found, None otherwise
        """
        profile = self.get_profile(user_id)
        if not profile:
            return None
            
        # Update profile attributes
        profile_dict = profile.model_dump()
        for key, value in updates.items():
            if key in profile_dict:
                setattr(profile, key, value)
        
        profile.last_active = datetime.now()
        self._save_profile(profile)
        logger.info(f"Updated profile for user {profile.username} ({user_id})")
        return profile
    
    def create_session(self, user_id: str, expiry_minutes: int = 60, **kwargs) -> Optional[UserSession]:
        """Create a new session for a user.
        
        Args:
            user_id: The ID of the user
            expiry_minutes: Session expiry time in minutes
            **kwargs: Additional session attributes (metadata, context, etc.)
            
        Returns:
            The newly created UserSession if the user exists, None otherwise
        """
        profile = self.get_profile(user_id)
        if not profile:
            logger.warning(f"Cannot create session: User {user_id} not found")
            return None
            
        # Create new session
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        
        # Extract metadata from kwargs if present, otherwise use empty dict
        metadata = kwargs.get("metadata", {})
        
        session = UserSession(
            user_id=user_id,
            expires_at=expires_at,
            metadata=metadata
        )
        
        # Apply any other kwargs to the session
        for key, value in kwargs.items():
            if key != "metadata" and hasattr(session, key):
                setattr(session, key, value)
        
        # Update profile with new session
        profile.sessions.append(session.session_id)
        profile.last_active = datetime.now()
        
        # Save both session and updated profile
        self._save_session(session)
        self._save_profile(profile)
        
        logger.info(f"Created new session {session.session_id} for user {profile.username}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The UserSession if found and active, None otherwise
        """
        # Check cache first
        if session_id in self._session_cache:
            session = self._session_cache[session_id]
            if session.is_active and (not session.expires_at or datetime.now() < session.expires_at):
                return session
            else:
                # Session expired or inactive
                session.is_active = False
                self._save_session(session)
                return None
        
        # Try to load from disk
        session_path = self._get_session_path(session_id)
        if not session_path.exists():
            return None
            
        try:
            with open(session_path, encoding="utf-8") as f:
                session_data = json.load(f)
                session = UserSession(**session_data)
                
                # Check if session is active and not expired
                if not session.is_active:
                    return None
                    
                if session.expires_at and datetime.now() > session.expires_at:
                    session.is_active = False
                    self._save_session(session)
                    return None
                
                self._session_cache[session_id] = session
                return session
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, **updates) -> Optional[UserSession]:
        """Update a session.
        
        Args:
            session_id: The ID of the session to update
            **updates: The session attributes to update
            
        Returns:
            The updated UserSession if found, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None
            
        # Update session attributes
        session_dict = session.model_dump()
        for key, value in updates.items():
            if key in session_dict:
                setattr(session, key, value)
        
        session.last_active = datetime.now()
        self._save_session(session)
        
        # Also update the user's last_active time
        profile = self.get_profile(session.user_id)
        if profile:
            profile.last_active = datetime.now()
            self._save_profile(profile)
            
        logger.info(f"Updated session {session_id}")
        return session
    
    def end_session(self, session_id: str) -> bool:
        """End a session.
        
        Args:
            session_id: The ID of the session to end
            
        Returns:
            True if the session was found and ended, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False
            
        session.is_active = False
        self._save_session(session)
        
        if session_id in self._session_cache:
            del self._session_cache[session_id]
            
        logger.info(f"Ended session {session_id}")
        return True
    
    def get_active_sessions_for_user(self, user_id: str) -> list[UserSession]:
        """Get all active sessions for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of active UserSession objects for the user
        """
        profile = self.get_profile(user_id)
        if not profile:
            return []
            
        active_sessions = []
        for session_id in profile.sessions:
            session = self.get_session(session_id)
            if session and session.is_active:
                active_sessions.append(session)
        
        return active_sessions
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        for session_id, session in list(self._session_cache.items()):
            if session.expires_at and datetime.now() > session.expires_at:
                session.is_active = False
                self._save_session(session)
                del self._session_cache[session_id]
                count += 1
        
        logger.info(f"Cleaned up {count} expired sessions")
        return count
    
    def add_interaction_to_profile(self, user_id: str, interaction_type: str, content: str, metadata: dict[str, Any] = None) -> bool:
        """Add an interaction to a user's profile history.
        
        Args:
            user_id: The ID of the user
            interaction_type: The type of interaction (e.g., 'query', 'feedback')
            content: The content of the interaction
            metadata: Additional metadata about the interaction
            
        Returns:
            True if the interaction was added successfully, False otherwise
        """
        profile = self.get_profile(user_id)
        if not profile:
            return False
            
        interaction = {
            "type": interaction_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        profile.interaction_history.append(interaction)
        
        # Limit history size to prevent unbounded growth
        max_history = 100  # Could be configurable
        if len(profile.interaction_history) > max_history:
            profile.interaction_history = profile.interaction_history[-max_history:]
            
        self._save_profile(profile)
        return True
    
    def update_intent_patterns(self, user_id: str, intent: str, confidence: float) -> bool:
        """Update intent patterns for a user.
        
        Args:
            user_id: The ID of the user
            intent: The detected intent
            confidence: Confidence score for the intent
            
        Returns:
            True if the intent pattern was updated successfully, False otherwise
        """
        profile = self.get_profile(user_id)
        if not profile:
            return False
            
        # Update intent pattern with exponential moving average
        alpha = 0.3  # Weight for new observation
        current = profile.intent_patterns.get(intent, 0.0)
        profile.intent_patterns[intent] = (alpha * confidence) + ((1 - alpha) * current)
        
        self._save_profile(profile)
        return True