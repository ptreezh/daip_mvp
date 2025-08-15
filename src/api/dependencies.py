from typing import TYPE_CHECKING, Annotated, Optional

from fastapi import Depends, HTTPException

if TYPE_CHECKING:
    from src.app_state import AppState
    from src.core_services.chat_service import ChatService
    from src.core_services.collaboration_service import CollaborationService
    from src.core_services.document_service import DocumentService
    from src.core_services.expert_service import ExpertService

# This global variable will be populated by the main application instance
# upon startup.
app_state: Optional["AppState"] = None

def get_app_state() -> "AppState":
    if app_state is None:
        raise HTTPException(status_code=503, detail="Application state not initialized.")
    return app_state

AppStateDep = Annotated["AppState", Depends(get_app_state)]

def get_expert_service(state: AppStateDep) -> "ExpertService":
    from src.core_services.expert_service import ExpertService
    return ExpertService(state)  # Pass state directly, not as app_state parameter

def get_document_service(state: AppStateDep) -> "DocumentService":
    from src.core_services.document_service import DocumentService
    return DocumentService(app_state=state)

def get_chat_service(state: AppStateDep) -> "ChatService":
    from src.core_services.chat_service import ChatService
    return ChatService(app_state=state)

def get_collaboration_service(state: AppStateDep) -> "CollaborationService":
    from src.core_services.collaboration_service import CollaborationService
    return CollaborationService(app_state=state)