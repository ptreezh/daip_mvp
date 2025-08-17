"""API Endpoints for Multi-Role Chat and Role Management."""

from fastapi import APIRouter

from src.api.dependencies import AppStateDep, get_app_state
from src.chat_config import DEFAULT_CHAT_MODEL
from src.multi_role_chat import MultiRoleChatEngine

router = APIRouter(
    tags=["Roles & Multi-Role Chat"],
)