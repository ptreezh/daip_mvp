# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : __init__.py
@Description:
    Interfaces layer package for DAIP backend.
    This layer contains FastAPI REST and WebSocket endpoints, request/response models,
    and API documentation.
"""

from .main import create_app
from .models import (
    UserCreate, UserResponse, SessionCreate, SessionResponse,
    TaskCreate, TaskResponse, MessageCreate, MessageResponse,
    EntranceSuggestionResponse, TransparencyResponse, HealthResponse
)
from .routers import (
    users_router, sessions_router, tasks_router, 
    messages_router, websocket_router, admin_router
)
from .websocket_manager import WebSocketEndpoint
from .dependencies import get_current_user, get_session_manager

__all__ = [
    "create_app",
    "UserCreate", "UserResponse", "SessionCreate", "SessionResponse",
    "TaskCreate", "TaskResponse", "MessageCreate", "MessageResponse",
    "EntranceSuggestionResponse", "TransparencyResponse", "HealthResponse",
    "users_router", "sessions_router", "tasks_router",
    "messages_router", "websocket_router", "admin_router",
    "WebSocketEndpoint",
    "get_current_user", "get_session_manager"
]