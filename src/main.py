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

    # 3. Use the factory to register those strategies as tools in the ToolExecutor,
    #    which is managed by the central AppState.
    dependencies.app_state.tool_executor.register_strategies_from_factory(consensus_factory)
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
