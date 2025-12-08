import asyncio
from typing import List
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

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

app = FastAPI()

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

# --- API Endpoints ---

class CreateSessionRequest(BaseModel):
    goal: str

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class RoleInfo(BaseModel):
    name: str
    description: str
    system_prompt: str

class KnowledgeStatusResponse(BaseModel):
    status: str
    last_sync: datetime
    total_documents: int

@app.post("/api/sessions", response_model=Session)
def create_session(
    request: CreateSessionRequest,
    session_manager: SessionManager = Depends(get_session_manager)
):
    session = session_manager.create_session(
        goal=request.goal,
        session_type="workflow",
        participant_ids=["agent", "user"]
    )
    session_manager.save_session(session)
    return session

@app.get("/api/sessions", response_model=List[Session])
def list_sessions(session_manager: SessionManager = Depends(get_session_manager)):
    return session_manager.list_sessions()

@app.get("/api/sessions/{session_id}", response_model=Session)
def get_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Get a specific session by ID."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/api/sessions/{session_id}")
def delete_session(
    session_id: str,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """Delete a specific session by ID."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session_manager.delete_session(session_id)
    return {"message": "Session deleted successfully"}

@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="1.0.0"
    )

@app.get("/api/roles", response_model=List[RoleInfo])
def list_roles(role_manager: RoleManager = Depends(get_role_manager)):
    """List all available roles."""
    try:
        roles = role_manager.list_roles()
        return [
            RoleInfo(
                name=role_name,
                description=role_data.get("description", "No description available"),
                system_prompt=role_data.get("system_prompt", "")
            )
            for role_name, role_data in roles.items()
        ]
    except Exception as e:
        # If role listing fails, return empty list with graceful degradation
        return []

@app.get("/api/knowledge/status", response_model=KnowledgeStatusResponse)
def get_knowledge_status(knowledge_manager: KnowledgeManager = Depends(get_knowledge_manager)):
    """Get knowledge base status and statistics."""
    try:
        # Get basic status from knowledge manager
        status = knowledge_manager.get_status() if hasattr(knowledge_manager, 'get_status') else "unknown"

        # Try to get document count if available
        doc_count = 0
        if hasattr(knowledge_manager, 'get_document_count'):
            try:
                doc_count = knowledge_manager.get_document_count()
            except:
                pass

        return KnowledgeStatusResponse(
            last_sync=datetime.now(timezone.utc),
            total_documents=doc_count
        )
    except Exception as e:
        # Return a default status if there's an error
        return KnowledgeStatusResponse(
            status="error",
            last_sync=datetime.now(timezone.utc),
            total_documents=0
        )

@app.websocket("/ws/sessions/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    agent_executor: AgentExecutor = Depends(get_agent_executor),
    session_manager: SessionManager = Depends(get_session_manager)
):
    await websocket.accept()
    session = session_manager.get_session(session_id)

    if not session:
        await websocket.close(code=4004, reason="Session not found")
        return

    async def forward_agent_events():
        async for event in agent_executor.run(goal=session.goal):
            await websocket.send_json(event.dict())

    async def receive_user_input():
        try:
            while True:
                data = await websocket.receive_json()
                await agent_executor.user_input_queue.put(data)
        except WebSocketDisconnect:
            pass

    agent_task = asyncio.create_task(forward_agent_events())
    user_task = asyncio.create_task(receive_user_input())

    done, pending = await asyncio.wait(
        [agent_task, user_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()
