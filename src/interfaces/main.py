# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : main.py
@Description:
    FastAPI main application for DAIP backend.
    Creates and configures the FastAPI app with all routers and middleware.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os

from fastapi import FastAPI, HTTPException, Depends, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

from ..application import (
    PersonalAssistantService, SessionManager, TaskOrchestrator, 
    EntranceSelector, WebSocketManager
)
from ..infrastructure import (
    get_database_manager, get_redis_manager, get_vector_store_manager,
    close_database_connection, close_redis_connection, close_vector_store_connection
)
from .models import (
    ErrorResponse, SuccessResponse, HealthResponse, 
    SystemConfig, WebSocketMessage, WebSocketConnection
)
from .routers import (
    users_router, sessions_router, tasks_router, 
    messages_router, websocket_router, admin_router
)
from .dependencies import get_current_user, get_session_manager
from .websocket_manager import WebSocketEndpoint


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局服务实例
personal_assistant_service: Optional[PersonalAssistantService] = None
session_manager: Optional[SessionManager] = None
task_orchestrator: Optional[TaskOrchestrator] = None
entrance_selector: Optional[EntranceSelector] = None
websocket_manager: Optional[WebSocketManager] = None

# 应用配置
APP_CONFIG = {
    "title": "DAIP Backend API",
    "description": "Dual-Entrance AI Platform Backend API",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
    "cors_origins": [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173"
    ],
    "trusted_hosts": ["localhost", "127.0.0.1"],
    "debug": os.getenv("DEBUG", "false").lower() == "true"
}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        
        # 记录请求信息
        logger.info(f"Request: {request.method} {request.url}")
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = (datetime.now() - start_time).total_seconds()
        
        # 记录响应信息
        logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="internal_server_error",
                    message="Internal server error",
                    details={"exception": str(e)} if APP_CONFIG["debug"] else None
                ).dict()
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global personal_assistant_service, session_manager, task_orchestrator, entrance_selector, websocket_manager
    
    logger.info("Starting DAIP Backend API...")
    
    try:
        # 初始化基础设施
        database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://daip:daip@localhost:5432/daip_db")
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # 初始化数据库
        db_manager = await get_database_manager(database_url)
        
        # 初始化Redis
        redis_manager = await get_redis_manager(redis_url)
        await redis_manager.start()
        
        # 初始化向量存储
        vector_store_manager = await get_vector_store_manager()
        
        # 初始化应用服务
        personal_assistant_service = PersonalAssistantService()
        await personal_assistant_service.initialize()
        
        session_manager = SessionManager()
        await session_manager.start()
        
        task_orchestrator = TaskOrchestrator()
        await task_orchestrator.start()
        
        entrance_selector = EntranceSelector()
        await entrance_selector.start()
        
        websocket_manager = WebSocketManager()
        await websocket_manager.start()
        
        # 设置WebSocket端点
        websocket_endpoint = WebSocketEndpoint(websocket_manager)
        app.add_websocket_route("/ws", websocket_endpoint.handle_websocket)
        
        logger.info("DAIP Backend API started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start DAIP Backend API: {e}", exc_info=True)
        raise
    
    finally:
        logger.info("Shutting down DAIP Backend API...")
        
        # 关闭服务
        if websocket_manager:
            await websocket_manager.stop()
        
        if entrance_selector:
            await entrance_selector.stop()
        
        if task_orchestrator:
            await task_orchestrator.stop()
        
        if session_manager:
            await session_manager.stop()
        
        # 关闭基础设施
        await close_vector_store_connection()
        await close_redis_connection()
        await close_database_connection()
        
        logger.info("DAIP Backend API shutdown completed")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    
    # 创建应用
    app = FastAPI(
        title=APP_CONFIG["title"],
        description=APP_CONFIG["description"],
        version=APP_CONFIG["version"],
        docs_url=APP_CONFIG["docs_url"],
        redoc_url=APP_CONFIG["redoc_url"],
        openapi_url=APP_CONFIG["openapi_url"],
        lifespan=lifespan,
        debug=APP_CONFIG["debug"]
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=APP_CONFIG["cors_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=APP_CONFIG["trusted_hosts"]
    )
    
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)
    
    # 静态文件服务
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 添加路由
    app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["Sessions"])
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
    app.include_router(messages_router, prefix="/api/v1/messages", tags=["Messages"])
    app.include_router(websocket_router, prefix="/api/v1/websocket", tags=["WebSocket"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
    
    @app.get("/", response_model=SuccessResponse)
    async def root():
        """根路径"""
        return SuccessResponse(
            message="DAIP Backend API is running",
            data={
                "version": APP_CONFIG["version"],
                "docs_url": APP_CONFIG["docs_url"],
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """健康检查"""
        try:
            # 检查各服务健康状态
            services = {}
            
            # 数据库健康检查
            if db_manager := await get_database_manager():
                db_health = await db_manager.health_check()
                services["database"] = db_health
            else:
                services["database"] = {
                    "name": "database",
                    "status": "disconnected",
                    "is_healthy": False,
                    "message": "Database not connected",
                    "last_check": datetime.now().isoformat()
                }
            
            # Redis健康检查
            if redis_manager := await get_redis_manager():
                redis_health = await redis_manager.health_check()
                services["redis"] = redis_health
            else:
                services["redis"] = {
                    "name": "redis",
                    "status": "disconnected",
                    "is_healthy": False,
                    "message": "Redis not connected",
                    "last_check": datetime.now().isoformat()
                }
            
            # 向量存储健康检查
            if vector_store_manager := await get_vector_store_manager():
                vector_health = await vector_store_manager.health_check()
                services["vector_store"] = vector_health
            else:
                services["vector_store"] = {
                    "name": "vector_store",
                    "status": "disconnected",
                    "is_healthy": False,
                    "message": "Vector store not connected",
                    "last_check": datetime.now().isoformat()
                }
            
            # 应用服务健康检查
            app_services = {
                "personal_assistant": {
                    "name": "personal_assistant",
                    "status": "running" if personal_assistant_service else "stopped",
                    "is_healthy": personal_assistant_service is not None,
                    "message": "Personal Assistant Service" + (" is running" if personal_assistant_service else " is not running"),
                    "last_check": datetime.now().isoformat()
                },
                "session_manager": {
                    "name": "session_manager",
                    "status": "running" if session_manager else "stopped",
                    "is_healthy": session_manager is not None,
                    "message": "Session Manager" + (" is running" if session_manager else " is not running"),
                    "last_check": datetime.now().isoformat()
                },
                "task_orchestrator": {
                    "name": "task_orchestrator",
                    "status": "running" if task_orchestrator else "stopped",
                    "is_healthy": task_orchestrator is not None,
                    "message": "Task Orchestrator" + (" is running" if task_orchestrator else " is not running"),
                    "last_check": datetime.now().isoformat()
                },
                "entrance_selector": {
                    "name": "entrance_selector",
                    "status": "running" if entrance_selector else "stopped",
                    "is_healthy": entrance_selector is not None,
                    "message": "Entrance Selector" + (" is running" if entrance_selector else " is not running"),
                    "last_check": datetime.now().isoformat()
                },
                "websocket_manager": {
                    "name": "websocket_manager",
                    "status": "running" if websocket_manager else "stopped",
                    "is_healthy": websocket_manager is not None,
                    "message": "WebSocket Manager" + (" is running" if websocket_manager else " is not running"),
                    "last_check": datetime.now().isoformat()
                }
            }
            
            services.update(app_services)
            
            # 确定整体状态
            all_healthy = all(service["is_healthy"] for service in services.values())
            overall_status = "healthy" if all_healthy else "degraded"
            
            return HealthResponse(
                overall_status=overall_status,
                services=services,
                uptime=0.0,  # TODO: 实现运行时间计算
                version=APP_CONFIG["version"],
                last_check=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            return HealthResponse(
                overall_status="unhealthy",
                services={},
                uptime=0.0,
                version=APP_CONFIG["version"],
                last_check=datetime.now().isoformat()
            )
    
    @app.get("/config", response_model=SystemConfig)
    async def get_config():
        """获取系统配置"""
        return SystemConfig(
            database_url=os.getenv("DATABASE_URL", "postgresql+asyncpg://daip:daip@localhost:5432/daip_db"),
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            vector_store_config={
                "collection_name": "daip_knowledge",
                "persist_directory": "./data/vector_store"
            },
            ollama_config={
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                "model": os.getenv("OLLAMA_MODEL", "nomic-embed-text")
            },
            session_config={
                "max_duration_hours": 24,
                "max_tasks_per_session": 50,
                "max_messages_per_session": 1000
            },
            task_config={
                "max_concurrent_tasks": 10,
                "max_queue_size": 100,
                "task_timeout_seconds": 1800
            },
            websocket_config={
                "connection_timeout_minutes": 30,
                "ping_interval_seconds": 30,
                "max_connections_per_user": 5
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP异常处理器"""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.detail.__class__.__name__.lower(),
                message=str(exc.detail),
                details={"path": request.url.path} if APP_CONFIG["debug"] else None
            ).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理器"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_server_error",
                message="Internal server error",
                details={"exception": str(exc), "path": request.url.path} if APP_CONFIG["debug"] else None
            ).dict()
        )
    
    return app


def custom_openapi(app: FastAPI):
    """自定义OpenAPI配置"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加自定义信息
    openapi_schema["info"]["x-logo"] = {
        "url": "https://daip.live/logo.png"
    }
    
    # 添加服务器配置
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# 创建应用实例
app = create_app()
app.openapi = custom_openapi


if __name__ == "__main__":
    # 运行开发服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=APP_CONFIG["debug"],
        log_level="info"
    )