import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import List

from src.daip_live.core.models import Session, AgentEvent, ProviderConfig
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.persistence.database import DatabaseManager
from src.daip_live.config import config_manager, create_config_yaml_if_not_exists
from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.knowledge.manager import KnowledgeManager
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.tool_manager import ToolManager
from src.daip_live.memory.service import MemoryService

app = FastAPI()

# --- Dependency Injection System ---

def get_config():
    create_config_yaml_if_not_exists()
    # Lazy loading is now handled by get_config() itself
    return config_manager.get_config()

def get_db_manager(cfg=Depends(get_config)) -> DatabaseManager:
    return DatabaseManager(db_path=cfg.database.path)

def get_session_manager(db_manager=Depends(get_db_manager)) -> SessionManager:
    return SessionManager(db_manager=db_manager)

def get_agent_executor(session_id: str, cfg=Depends(get_config), db_manager=Depends(get_db_manager), session_manager=Depends(get_session_manager)) -> AgentExecutor:
    model_provider = LiteLLMProvider(ProviderConfig(model=cfg.llm_provider.default_model))
    tool_manager = ToolManager()
    knowledge_manager = KnowledgeManager(db_manager=db_manager, model_provider=model_provider, config=cfg.knowledge_base)
    memory_service = MemoryService()
    user_input_queue = asyncio.Queue()

    return AgentExecutor(
        session_manager=session_manager,
        memory_service=memory_service,
        knowledge_manager=knowledge_manager,
        model_provider=model_provider,
        tool_manager=tool_manager,
        user_input_queue=user_input_queue,
    )

# --- API Endpoints ---

class CreateSessionRequest(BaseModel):
    goal: str

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
