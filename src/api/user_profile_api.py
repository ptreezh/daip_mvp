"""API endpoints for user profile and session management.

This module provides FastAPI endpoints for user registration, authentication,
profile management, and session handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel

from src.app_state import AppState
from src.core_services.session_management_service import AuthenticationRequest, AuthenticationResponse


# Define API models
class UserRegistrationRequest(BaseModel):
    username: str
    password: str
    display_name: Optional[str] = None
    email: Optional[str] = None


class UserProfileResponse(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str] = None
    created_at: datetime
    last_active: datetime
    preferences: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class UserProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
    last_active: datetime
    expires_at: Optional[datetime] = None
    is_active: bool


# Create router
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# Dependency to get app state
def get_app_state():
    return AppState()


# Dependency to validate session and get user_id
async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    app_state: AppState = Depends(get_app_state)
) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # Check if it's a session ID
    if authorization.startswith("Session "):
        session_id = authorization.replace("Session ", "")
        is_valid, user_id, _ = app_state.session_management_service.validate_session(session_id)
        if not is_valid or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        return user_id

    # Check if it's a token
    elif authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        is_valid, user_id, _ = app_state.session_management_service.validate_token(token)
        if not is_valid or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        return user_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authorization header format"
    )


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserRegistrationRequest,
    app_state: AppState = Depends(get_app_state)
):
    """Register a new user."""
    success, message, profile = app_state.session_management_service.register_user(
        username=request.username,
        password=request.password,
        display_name=request.display_name,
        email=request.email
    )

    if not success or not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return UserProfileResponse(
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.metadata.get("display_name"),
        created_at=profile.created_at,
        last_active=profile.last_active,
        preferences=profile.preferences,
        metadata=profile.metadata
    )


@router.post("/login", response_model=AuthenticationResponse)
async def login(
    request: AuthenticationRequest,
    app_state: AppState = Depends(get_app_state)
):
    """Authenticate a user and create a session."""
    response = app_state.session_management_service.authenticate(
        username=request.username,
        password=request.password
    )

    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=response.message
        )

    return response


@router.post("/logout")
async def logout(
    request: Request,
    authorization: Optional[str] = Header(None),
    app_state: AppState = Depends(get_app_state)
):
    """End the current session."""
    if not authorization or not authorization.startswith("Session "):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session header"
        )

    session_id = authorization.replace("Session ", "")
    success = app_state.session_management_service.end_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session"
        )

    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """Get the current user's profile."""
    profile = app_state.user_profile_service.get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserProfileResponse(
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.metadata.get("display_name"),
        created_at=profile.created_at,
        last_active=profile.last_active,
        preferences=profile.preferences,
        metadata=profile.metadata
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UserProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """Update the current user's profile."""
    updates = {}

    if request.display_name is not None:
        if not hasattr(updates, "metadata"):
            updates["metadata"] = {}
        updates["metadata"]["display_name"] = request.display_name

    if request.preferences is not None:
        updates["preferences"] = request.preferences

    if request.metadata is not None:
        if not hasattr(updates, "metadata"):
            updates["metadata"] = {}
        updates["metadata"].update(request.metadata)

    profile = app_state.user_profile_service.update_profile(user_id, **updates)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return UserProfileResponse(
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.metadata.get("display_name"),
        created_at=profile.created_at,
        last_active=profile.last_active,
        preferences=profile.preferences,
        metadata=profile.metadata
    )


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """Change the current user's password."""
    success, message = app_state.session_management_service.change_password(
        user_id=user_id,
        current_password=request.current_password,
        new_password=request.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return {"message": message}


@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """Get all active sessions for the current user."""
    sessions = app_state.user_profile_service.get_active_sessions_for_user(user_id)

    return [
        SessionResponse(
            session_id=session.session_id,
            created_at=session.created_at,
            last_active=session.last_active,
            expires_at=session.expires_at,
            is_active=session.is_active
        )
        for session in sessions
    ]


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """End a specific session."""
    # Verify the session belongs to the current user
    sessions = app_state.user_profile_service.get_active_sessions_for_user(user_id)
    session_ids = [session.session_id for session in sessions]

    if session_id not in session_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to end this session"
        )

    success = app_state.session_management_service.end_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to end session"
        )

    return {"message": "Session ended successfully"}


@router.post("/token")
async def create_token(
    user_id: str = Depends(get_current_user_id),
    app_state: AppState = Depends(get_app_state)
):
    """Create an authentication token for the current user."""
    token = app_state.session_management_service.generate_token(
        user_id=user_id,
        expiry_minutes=app_state.session_management_service.session_expiry_minutes
    )

    return {"token": token}
