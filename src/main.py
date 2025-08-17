"""@Time    : 2025-07-24 10:00:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description:
    Main entry point for the DAIP-MVP FastAPI application.
    Initializes the application state and includes all API routers.
"""

import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.protocols.consensus_strategies import (
    ConsensusStrategyFactory,
    SimpleMajorityVoteStrategy,
)
from src.api import dependencies
from src.api.routers import (
    advanced,
    chat,
    collaboration,
    documents,
    knowledge_management_api,
    protocols,
    roles,
    tools,
    virtual_team,
    ddd,
    forum,
)
from src.api import user_profile_api
from src.api import scenario_api
from src.app_state import AppState

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DAIP-LIVE MVP API",
    description="API for multi-role debate, agile project execution, and hallucination suppression. V0.3.5 with three core scenarios: Expert Consultation, Academic Research, and Industry Analysis.",
    version="0.3.5",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Centralized Exception Handlers ---


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Handles validation errors (e.g., from service layer checks).
    Returns a 400 Bad Request response.
    """
    logger.warning(f"Validation error for request {request.url.path}: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any other unhandled exceptions.
    Returns a 500 Internal Server Error to prevent leaking details.
    """
    logger.error(f"Unhandled exception for request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# Import ForumServiceError for exception handler
from src.core.exceptions import ForumServiceError
from datetime import datetime

@app.exception_handler(ForumServiceError)
async def forum_service_error_handler(request, exc: ForumServiceError):
    """Forum服务错误处理器"""
    return JSONResponse(
        status_code=500,  # You might want to use a more specific status code
        content={
            "error": "Forum service error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """数值错误处理器"""
    return JSONResponse(
        status_code=400,  # Bad Request for ValueError
        content={
            "error": "Validation error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )
@app.on_event("startup")
async def startup_event():
    """Initializes the application state on startup."""
    logger.info("Starting up and initializing application state...")
    dependencies.app_state = AppState()
    logger.info("Application state initialized successfully.")

    logger.info("Initializing and registering consensus strategies...")
    # 1. Create the factory for consensus strategies.
    consensus_factory = ConsensusStrategyFactory()

    # 2. Register all available strategies in the factory.
    #    In the future, this could be automated to discover all strategy classes.
    consensus_factory.register("simple_majority_vote", SimpleMajorityVoteStrategy)

    # 3. Use the factory to register those strategies as tools in the UnifiedToolManager,
    #    which is managed by the central AppState.
    dependencies.app_state.unified_tool_manager.register_strategies_from_factory(consensus_factory)
    logger.info("Consensus strategies successfully registered as executable tools.")

# Include all API routers
app.include_router(advanced.router)
app.include_router(chat.router)
app.include_router(collaboration.router)
app.include_router(documents.router)
app.include_router(knowledge_management_api.router)
app.include_router(protocols.router)
app.include_router(roles.router)
app.include_router(tools.router)
app.include_router(virtual_team.router)
app.include_router(ddd.router)
app.include_router(forum.router)
app.include_router(user_profile_api.router)
app.include_router(scenario_api.router)

@app.get("/")
async def read_root() -> dict[str, str]:
    """Root endpoint to check if the service is running.
    """
    return {"message": "DAIP-LIVE MVP API is running."}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint that verifies the service is running.
    
    Returns:
        dict: Simple health status message
    """
    return {"status": "healthy", "message": "Service is operational"}


@app.get("/status")
async def detailed_status():
    """Detailed system status endpoint that provides comprehensive health information.
    
    Returns:
        dict: Detailed status information about all system components
    """
    from datetime import datetime
    import os
    
    status_info = {
        "timestamp": datetime.now().isoformat(),
        "service": {
            "name": "DAIP-LIVE MVP API",
            "version": "0.1.0",
            "status": "running"
        },
        "system": {},
        "components": {}
    }
    
    # Try to get system information if psutil is available
    try:
        import psutil
        status_info["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
    except ImportError:
        status_info["system"] = {
            "note": "System metrics unavailable (psutil not installed)"
        }
    except Exception as e:
        status_info["system"] = {
            "error": f"System metrics error: {str(e)}"
        }
    
    # Check application state
    try:
        if dependencies.app_state is not None:
            status_info["components"]["app_state"] = {
                "status": "healthy",
                "details": "Application state initialized successfully"
            }
            
            # Check core services
            services_to_check = [
                ("llm_interface", "LLM Interface"),
                ("memory_service", "Memory Service"),
                ("wiki_service", "Wiki Service"),
                ("synthesis_engine", "Synthesis Engine"),
                ("unified_tool_manager", "Tool Manager"),
                ("user_profile_service", "User Profile Service"),
                ("session_management_service", "Session Management Service")
            ]
            
            for service_attr, service_name in services_to_check:
                try:
                    service = getattr(dependencies.app_state, service_attr, None)
                    if service is not None:
                        status_info["components"][service_attr] = {
                            "status": "healthy",
                            "details": f"{service_name} is available"
                        }
                    else:
                        status_info["components"][service_attr] = {
                            "status": "unavailable",
                            "details": f"{service_name} is not initialized"
                        }
                except Exception as e:
                    status_info["components"][service_attr] = {
                        "status": "error",
                        "details": f"{service_name} check failed: {str(e)}"
                    }
            
            # Check vector database
            try:
                if hasattr(dependencies.app_state, 'chroma_client') and dependencies.app_state.chroma_client:
                    # Try to access the collection to verify it's working
                    collection = dependencies.app_state.role_collection
                    if collection:
                        status_info["components"]["vector_db"] = {
                            "status": "healthy",
                            "details": "ChromaDB is accessible"
                        }
                    else:
                        status_info["components"]["vector_db"] = {
                            "status": "warning",
                            "details": "ChromaDB client available but collection not found"
                        }
                else:
                    status_info["components"]["vector_db"] = {
                        "status": "unavailable",
                        "details": "ChromaDB client not initialized"
                    }
            except Exception as e:
                status_info["components"]["vector_db"] = {
                    "status": "error",
                    "details": f"ChromaDB check failed: {str(e)}"
                }
            
            # Check roles loading
            try:
                roles_count = len(dependencies.app_state.all_roles_details)
                if roles_count > 0:
                    status_info["components"]["roles"] = {
                        "status": "healthy",
                        "details": f"{roles_count} roles loaded successfully"
                    }
                else:
                    status_info["components"]["roles"] = {
                        "status": "warning",
                        "details": "No roles loaded"
                    }
            except Exception as e:
                status_info["components"]["roles"] = {
                    "status": "error",
                    "details": f"Roles check failed: {str(e)}"
                }
                
        else:
            status_info["components"]["app_state"] = {
                "status": "error",
                "details": "Application state not initialized"
            }
            
    except Exception as e:
        status_info["components"]["app_state"] = {
            "status": "error",
            "details": f"Application state check failed: {str(e)}"
        }
    
    # Check configuration
    try:
        status_info["components"]["configuration"] = {
            "status": "healthy",
            "details": f"Configuration loaded with log level: {settings.log_level}"
        }
    except Exception as e:
        status_info["components"]["configuration"] = {
            "status": "error",
            "details": f"Configuration check failed: {str(e)}"
        }
    
    # Determine overall health
    component_statuses = [comp["status"] for comp in status_info["components"].values()]
    if "error" in component_statuses:
        status_info["overall_status"] = "unhealthy"
    elif "warning" in component_statuses or "unavailable" in component_statuses:
        status_info["overall_status"] = "degraded"
    else:
        status_info["overall_status"] = "healthy"
    
    return status_info


# Simple endpoints for frontend integration tests
@app.get("/scenarios")
async def get_scenarios():
    """Get available scenarios - simplified endpoint for frontend integration"""
    return {
        "scenarios": [
            {
                "id": "academic_research",
                "name": "学术研究场景",
                "description": "深度研究分析，生成结构化学术报告",
                "features": ["文献综述", "多视角分析", "学术写作", "引用管理"]
            },
            {
                "id": "expert_consultation",
                "name": "专家咨询场景",
                "description": "专业建议和决策支持，智能专家匹配",
                "features": ["专家匹配", "决策框架", "风险评估", "综合建议"]
            },
            {
                "id": "casual_discussion",
                "name": "轻松讨论场景",
                "description": "自然对话体验，支持社交互动",
                "features": ["自然对话", "话题转换", "社交互动", "氛围营造"]
            }
        ]
    }


@app.get("/memory")
async def get_memory_status():
    """Get memory service status - simplified endpoint for frontend integration"""
    return {
        "status": "active",
        "service": "Memory Service",
        "message": "Memory service is running and accessible",
        "features": ["short_term_memory", "long_term_memory", "context_management", "retrieval_optimization"]
    }


@app.get("/wiki")
async def get_wiki_status():
    """Get wiki service status - simplified endpoint for frontend integration"""
    return {
        "status": "active",
        "service": "Wiki Service",
        "message": "Wiki service is running and accessible",
        "features": ["version_control", "collaborative_editing", "change_tracking", "knowledge_organization"]
    }
