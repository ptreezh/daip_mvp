"""Session Management Service for handling user authentication and session tracking.

This service provides functionality for authenticating users, creating and managing sessions,
and handling session-related security concerns. It works closely with the UserProfileService
to provide a complete user management solution.
"""

import hashlib
import hmac
import json
import logging
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel

from src.core_services.user_profile_service import UserProfile, UserProfileService, UserSession

logger = logging.getLogger(__name__)


class AuthenticationRequest(BaseModel):
    """Model for authentication requests.
    """
    username: str
    password: str


class AuthenticationResponse(BaseModel):
    """Model for authentication responses.
    """
    success: bool
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message: str = ""
    expires_at: Optional[datetime] = None


class SessionManagementService:
    """Service for managing user authentication and sessions.
    
    This service provides functionality for authenticating users, creating and managing sessions,
    and handling session-related security concerns. It works closely with the UserProfileService
    to provide a complete user management solution.
    """
    
    def __init__(
        self, 
        user_profile_service: UserProfileService,
        auth_data_dir: str = "data/auth",
        session_expiry_minutes: int = 60,
        token_secret: Optional[str] = None
    ):
        """Initialize the SessionManagementService.
        
        Args:
            user_profile_service: The UserProfileService instance to use
            auth_data_dir: Directory where authentication data is stored
            session_expiry_minutes: Default session expiry time in minutes
            token_secret: Secret key for token signing (generated if not provided)
        """
        self.user_profile_service = user_profile_service
        self.auth_data_dir = Path(auth_data_dir)
        self.credentials_file = self.auth_data_dir / "credentials.json"
        self.session_expiry_minutes = session_expiry_minutes
        
        # Create auth data directory if it doesn't exist
        self.auth_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize credentials storage if it doesn't exist
        if not self.credentials_file.exists():
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
        
        # Generate or use provided token secret
        self.token_secret = token_secret or secrets.token_hex(32)
        
        logger.info(f"SessionManagementService initialized with auth directory: {self.auth_data_dir}")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password using PBKDF2 with SHA-256.
        
        Args:
            password: The password to hash
            salt: Optional salt (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)
            
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Number of iterations
        ).hex()
        
        return key, salt
    
    def _verify_password(self, stored_hash: str, stored_salt: str, provided_password: str) -> bool:
        """Verify a password against a stored hash.
        
        Args:
            stored_hash: The stored password hash
            stored_salt: The salt used for hashing
            provided_password: The password to verify
            
        Returns:
            True if the password matches, False otherwise
        """
        key, _ = self._hash_password(provided_password, stored_salt)
        return hmac.compare_digest(key, stored_hash)
    
    def _load_credentials(self) -> dict[str, dict[str, Any]]:
        """Load user credentials from storage.
        
        Returns:
            Dictionary of user credentials indexed by user_id
        """
        try:
            with open(self.credentials_file, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return {}
    
    def _save_credentials(self, credentials: dict[str, dict[str, Any]]) -> None:
        """Save user credentials to storage.
        
        Args:
            credentials: Dictionary of user credentials indexed by user_id
        """
        try:
            with open(self.credentials_file, "w", encoding="utf-8") as f:
                json.dump(credentials, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def register_user(self, username: str, password: str, **profile_data) -> tuple[bool, str, Optional[UserProfile]]:
        """Register a new user.
        
        Args:
            username: The username for the new user
            password: The password for the new user
            **profile_data: Additional profile data
            
        Returns:
            Tuple of (success, message, user_profile)
        """
        # Check if username already exists
        existing_profile = self.user_profile_service.get_profile_by_username(username)
        if existing_profile:
            return False, "Username already exists", None
        
        # Create user profile
        profile = self.user_profile_service.create_profile(username=username, **profile_data)
        
        # Hash password and store credentials
        password_hash, salt = self._hash_password(password)
        
        credentials = self._load_credentials()
        credentials[profile.user_id] = {
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat()
        }
        self._save_credentials(credentials)
        
        logger.info(f"Registered new user: {username} with ID {profile.user_id}")
        return True, "User registered successfully", profile
    
    def authenticate(self, username: str, password: str) -> AuthenticationResponse:
        """Authenticate a user and create a session.
        
        Args:
            username: The username to authenticate
            password: The password to verify
            
        Returns:
            AuthenticationResponse with authentication result
        """
        # Find user profile by username
        profile = self.user_profile_service.get_profile_by_username(username)
        if not profile:
            return AuthenticationResponse(
                success=False,
                message="Invalid username or password"
            )
        
        # Get credentials for the user
        credentials = self._load_credentials()
        user_creds = credentials.get(profile.user_id)
        if not user_creds:
            return AuthenticationResponse(
                success=False,
                message="Invalid username or password"
            )
        
        # Verify password
        if not self._verify_password(
            user_creds["password_hash"],
            user_creds["salt"],
            password
        ):
            return AuthenticationResponse(
                success=False,
                message="Invalid username or password"
            )
        
        # Create new session
        session = self.user_profile_service.create_session(
            profile.user_id,
            expiry_minutes=self.session_expiry_minutes
        )
        
        if not session:
            return AuthenticationResponse(
                success=False,
                message="Failed to create session"
            )
        
        logger.info(f"User {username} authenticated successfully")
        return AuthenticationResponse(
            success=True,
            user_id=profile.user_id,
            session_id=session.session_id,
            message="Authentication successful",
            expires_at=session.expires_at
        )
    
    def validate_session(self, session_id: str) -> tuple[bool, Optional[str], Optional[UserSession]]:
        """Validate a session.
        
        Args:
            session_id: The ID of the session to validate
            
        Returns:
            Tuple of (is_valid, user_id, session)
        """
        session = self.user_profile_service.get_session(session_id)
        if not session:
            return False, None, None
        
        # Update session last_active time
        session = self.user_profile_service.update_session(
            session_id,
            last_active=datetime.now()
        )
        
        return True, session.user_id, session
    
    def end_session(self, session_id: str) -> bool:
        """End a session.
        
        Args:
            session_id: The ID of the session to end
            
        Returns:
            True if the session was ended successfully, False otherwise
        """
        return self.user_profile_service.end_session(session_id)
    
    def end_all_user_sessions(self, user_id: str) -> int:
        """End all sessions for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Number of sessions ended
        """
        sessions = self.user_profile_service.get_active_sessions_for_user(user_id)
        count = 0
        
        for session in sessions:
            if self.user_profile_service.end_session(session.session_id):
                count += 1
                
        return count
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> tuple[bool, str]:
        """Change a user's password.
        
        Args:
            user_id: The ID of the user
            current_password: The current password
            new_password: The new password
            
        Returns:
            Tuple of (success, message)
        """
        # Get credentials for the user
        credentials = self._load_credentials()
        user_creds = credentials.get(user_id)
        if not user_creds:
            return False, "User not found"
        
        # Verify current password
        if not self._verify_password(
            user_creds["password_hash"],
            user_creds["salt"],
            current_password
        ):
            return False, "Current password is incorrect"
        
        # Hash new password and update credentials
        password_hash, salt = self._hash_password(new_password)
        user_creds["password_hash"] = password_hash
        user_creds["salt"] = salt
        user_creds["updated_at"] = datetime.now().isoformat()
        
        self._save_credentials(credentials)
        
        # End all existing sessions for security
        self.end_all_user_sessions(user_id)
        
        logger.info(f"Password changed for user {user_id}")
        return True, "Password changed successfully"
    
    def reset_password(self, username: str, new_password: str) -> tuple[bool, str]:
        """Reset a user's password (admin function).
        
        Args:
            username: The username of the user
            new_password: The new password
            
        Returns:
            Tuple of (success, message)
        """
        # Find user profile by username
        profile = self.user_profile_service.get_profile_by_username(username)
        if not profile:
            return False, "User not found"
        
        # Get credentials for the user
        credentials = self._load_credentials()
        user_creds = credentials.get(profile.user_id)
        if not user_creds:
            return False, "User credentials not found"
        
        # Hash new password and update credentials
        password_hash, salt = self._hash_password(new_password)
        user_creds["password_hash"] = password_hash
        user_creds["salt"] = salt
        user_creds["updated_at"] = datetime.now().isoformat()
        user_creds["password_reset"] = True
        
        self._save_credentials(credentials)
        
        # End all existing sessions for security
        self.end_all_user_sessions(profile.user_id)
        
        logger.info(f"Password reset for user {username}")
        return True, "Password reset successfully"
    
    def generate_token(self, user_id: str, expiry_minutes: int = 60) -> str:
        """Generate an authentication token for a user.
        
        Args:
            user_id: The ID of the user
            expiry_minutes: Token expiry time in minutes
            
        Returns:
            Authentication token
        """
        # Create a simple JWT-like token
        payload = {
            "user_id": user_id,
            "exp": int((datetime.now() + timedelta(minutes=expiry_minutes)).timestamp()),
            "iat": int(datetime.now().timestamp()),
            "jti": secrets.token_hex(8)
        }
        
        # Convert payload to JSON and encode
        payload_bytes = json.dumps(payload).encode('utf-8')
        payload_b64 = payload_bytes.hex()
        
        # Create signature
        signature = hmac.new(
            self.token_secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        token = f"{payload_b64}.{signature}"
        return token
    
    def validate_token(self, token: str) -> tuple[bool, Optional[str], Optional[dict[str, Any]]]:
        """Validate an authentication token.
        
        Args:
            token: The token to validate
            
        Returns:
            Tuple of (is_valid, user_id, payload)
        """
        try:
            # Split token into payload and signature
            payload_b64, signature = token.split('.')
            
            # Decode payload
            payload_bytes = bytes.fromhex(payload_b64)
            payload = json.loads(payload_bytes.decode('utf-8'))
            
            # Verify signature
            expected_signature = hmac.new(
                self.token_secret.encode('utf-8'),
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, None, None
            
            # Check expiration
            if payload.get("exp", 0) < int(datetime.now().timestamp()):
                return False, None, None
            
            return True, payload.get("user_id"), payload
        except Exception as e:
            logger.warning(f"Token validation error: {e}")
            return False, None, None