"""DAIP-LIVE FastAPI Application

Main web API server providing REST endpoints and WebSocket support
for the DAIP-LIVE system.

## Quick Start

```bash
# Start the server
uvicorn daip_live.p7_gui.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
open http://localhost:8000/docs
```
"""

import asyncio
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.config import create_config_yaml_if_not_exists
from daip_live.config_bridge import config_bridge
from daip_live.core.models import ProviderConfig, Session
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.persistence.database import DatabaseManager
from daip_live.p7_gui.api_docs import (
    API_TAGS,
    OPENAPI_SPEC,
    SessionCreateRequest,
    HealthCheckResponse,
    RoleInfoResponse,
    KnowledgeStatusResponse,
    ErrorResponse,
    register_api_docs
)

# ============================================================================
# Application Configuration
# ============================================================================

# Server start time for uptime tracking
_start_time = time.time()

app = FastAPI(
    title="DAIP-LIVE API",
    description="Dynamic AI-driven Project-execution LIVE System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    tags=API_TAGS
)

# Apply OpenAPI enhancements
register_api_docs(app)

# --- Dependency Injection System ---

def get_config():
    create_config_yaml_if_not_exists()
    # Use config bridge to get configuration data
    return config_bridge.get_config_data()

def get_db_manager(cfg=Depends(get_config)) -> DatabaseManager:
    return DatabaseManager(db_path=cfg.get('database', {}).get('path', 'daip_live.db'))

def get_session_manager(db_manager=Depends(get_db_manager)) -> SessionManager:
    return SessionManager(db_manager=db_manager)

def get_agent_executor(session_id: str, cfg=Depends(get_config), db_manager=Depends(get_db_manager), session_manager=Depends(get_session_manager)) -> AgentExecutor:
    model_provider = LiteLLMProvider(ProviderConfig(model=cfg.get('llm_provider', {}).get('default_model', 'gpt-3.5-turbo')))
    tool_manager = ToolManager()
    knowledge_manager = KnowledgeManager(db_manager=db_manager, model_provider=model_provider, config=cfg.get('knowledge_base', {}))
    memory_service = MemoryService(model_provider)  # Pass model_provider to MemoryService
    user_input_queue = asyncio.Queue()

    return AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
    )

def get_role_manager(cfg=Depends(get_config)) -> RoleManager:
    """Dependency injection for RoleManager."""
    return RoleManager(roles_dir_path=cfg.get('role_manager', {}).get('roles_dir', 'roles/'))

def get_knowledge_manager(cfg=Depends(get_config), db_manager=Depends(get_db_manager)) -> KnowledgeManager:
    """Dependency injection for KnowledgeManager."""
    model_provider = LiteLLMProvider(ProviderConfig(model=cfg.get('llm_provider', {}).get('default_model', 'gpt-3.5-turbo')))
    return KnowledgeManager(db_manager=db_manager, model_provider=model_provider, config=cfg.get('knowledge_base', {}))

# ============================================================================
# API Endpoint Definitions
# ============================================================================

@app.post(
    "/api/sessions",
    response_model=Session,
    tags=["sessions"],
    summary="Create a new session",
    description="Creates a new session with the specified goal and configuration. Returns the created session with its unique identifier."
)
def create_session(
    request: SessionCreateRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Create a new session for agent execution.

    Args:
        request: Session creation request with goal and configuration
        session_manager: Injected session manager

    Returns:
        Session: Created session with generated session_id

    Raises:
        HTTPException: If session creation fails
    """
    session = session_manager.create_session(
        goal=request.goal,
        session_type=request.session_type or "workflow",
        participant_ids=request.participant_ids or ["agent", "user"]
    )
    session_manager.save_session(session)
    return session


@app.get(
    "/api/sessions",
    response_model=List[Session],
    tags=["sessions"],
    summary="List all sessions",
    description="Retrieves a list of all existing sessions with their metadata."
)
def list_sessions(session_manager: SessionManager = Depends(get_session_manager)):
    """List all available sessions.

    Args:
        session_manager: Injected session manager

    Returns:
        List[Session]: List of all sessions
    """
    return session_manager.list_sessions()


@app.get(
    "/api/sessions/{session_id}",
    response_model=Session,
    tags=["sessions"],
    summary="Get a specific session",
    description="Retrieves details of a specific session by ID.",
    responses={
        404: {"description": "Session not found", "model": ErrorResponse}
    }
)
def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get a specific session by ID.

    Args:
        session_id: Unique session identifier
        session_manager: Injected session manager

    Returns:
        Session: Session details

    Raises:
        HTTPException: If session not found (404)
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="SESSION_NOT_FOUND",
                message=f"Session '{session_id}' does not exist",
                timestamp=datetime.now(timezone.utc)
            ).model_dump()
        )
    return session


@app.delete(
    "/api/sessions/{session_id}",
    tags=["sessions"],
    summary="Delete a session",
    description="Deletes a specific session by ID. This operation cannot be undone.",
    responses={
        404: {"description": "Session not found", "model": ErrorResponse}
    }
)
def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Delete a specific session by ID.

    Args:
        session_id: Unique session identifier
        session_manager: Injected session manager

    Returns:
        dict: Confirmation message

    Raises:
        HTTPException: If session not found (404)
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error="SESSION_NOT_FOUND",
                message=f"Session '{session_id}' does not exist",
                timestamp=datetime.now(timezone.utc)
            ).model_dump()
        )

    session_manager.delete_session(session_id)
    return {"message": "Session deleted successfully", "session_id": session_id}


@app.get(
    "/api/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Health check",
    description="Returns the current health status of the system including uptime and component status."
)
def health_check():
    """System health check endpoint.

    Returns:
        HealthCheckResponse: Current system health status including uptime
    """
    uptime = time.time() - _start_time
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0",
        uptime_seconds=uptime,
        components={
            "database": "healthy",
            "knowledge_base": "healthy",
            "model_provider": "healthy"
        }
    )


@app.get(
    "/api/roles",
    response_model=List[RoleInfoResponse],
    tags=["roles"],
    summary="List available roles",
    description="Retrieves a list of all available agent roles with their configurations and capabilities."
)
def list_roles(role_manager: RoleManager = Depends(get_role_manager)):
    """List all available roles.

    Args:
        role_manager: Injected role manager

    Returns:
        List[RoleInfoResponse]: List of role configurations
    """
    try:
        roles = role_manager.list_roles()
        return [
            RoleInfoResponse(
                name=role_name,
                description=role_data.get("description", "No description available"),
                system_prompt=role_data.get("system_prompt", ""),
                model=role_data.get("model"),
                capabilities=role_data.get("capabilities", [])
            )
            for role_name, role_data in roles.items()
        ]
    except Exception as e:
        # Graceful degradation on error
        return []


@app.get(
    "/api/knowledge/status",
    response_model=KnowledgeStatusResponse,
    tags=["knowledge"],
    summary="Get knowledge base status",
    description="Retrieves the current status and statistics of the knowledge base including document count and index size."
)
def get_knowledge_status(knowledge_manager: KnowledgeManager = Depends(get_knowledge_manager)):
    """Get knowledge base status and statistics.

    Args:
        knowledge_manager: Injected knowledge manager

    Returns:
        KnowledgeStatusResponse: Knowledge base status
    """
    try:
        # Try to get document count if available
        doc_count = 0
        if hasattr(knowledge_manager, 'get_document_count'):
            try:
                doc_count = knowledge_manager.get_document_count()
            except Exception:
                pass

        # Get index info if available
        index_size = None
        embedding_dim = None
        if hasattr(knowledge_manager, 'index'):
            try:
                index_size = knowledge_manager.index.ntotal
            except Exception:
                pass

        return KnowledgeStatusResponse(
            status="healthy",
            last_sync=datetime.now(timezone.utc),
            total_documents=doc_count,
            index_size=index_size,
            embedding_dimension=embedding_dim
        )
    except Exception as e:
        # Return error status on exception
        return KnowledgeStatusResponse(
            status="error",
            last_sync=datetime.now(timezone.utc),
            total_documents=0
        )

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    agent_executor: AgentExecutor = Depends(get_agent_executor),
    session_manager: SessionManager = Depends(get_session_manager)
):
    """WebSocket endpoint for real-time agent communication.

    Establishes a bidirectional WebSocket connection for streaming
    agent execution events and receiving user input.

    Args:
        websocket: WebSocket connection
        session_id: Session identifier for the execution
        agent_executor: Injected agent executor
        session_manager: Injected session manager

    Connection Flow:
        1. Connect with valid session_id
        2. Receive real-time events from agent executor
        3. Send user input via JSON messages

    Event Types:
        - step_complete: Agent completed an execution step
        - error: An error occurred during execution
        - user_input_required: Agent needs additional user input
    """
    await websocket.accept()
    session = session_manager.get_session(session_id)

    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    async def forward_agent_events():
        """Forward agent execution events to the WebSocket client."""
        async for event in agent_executor.run(goal=session.goal):
            await websocket.send_json(event.model_dump())

    async def receive_user_input():
        """Receive user input from the WebSocket client."""
        try:
            while True:
                data = await websocket.receive_json()
                await agent_executor.user_input_queue.put(data)
        except WebSocketDisconnect:
            pass

    # Run both tasks concurrently
    agent_task = asyncio.create_task(forward_agent_events())
    user_task = asyncio.create_task(receive_user_input())

    done, pending = await asyncio.wait(
        [agent_task, user_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    # Cancel pending tasks
    for task in pending:
        task.cancel()
