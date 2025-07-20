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
    protocols,
    roles,
    tools,
    virtual_team,
)
from src.app_state import AppState

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DAIP-LIVE MVP API",
    description="API for multi-role debate, agile project execution, and hallucination suppression.",
    version="0.1.0",
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
    """
    Handles any other unhandled exceptions.
    Returns a 500 Internal Server Error to prevent leaking details.
    """
    logger.error(f"Unhandled exception for request {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
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
app.include_router(protocols.router)
app.include_router(roles.router)
app.include_router(tools.router)
app.include_router(virtual_team.router)

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
        "timestamp": datetime.now(datetime.timezone.utc).isoformat(),
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
                ("unified_tool_manager", "Tool Manager")
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
