# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 18:00:00
@Author  : DAIP-LIVE Team
@File    : api_interface.py
@Description:
    REST API interface for the Virtual Role Chat System workflows.
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from ..workflows.critical_review_workflow import CriticalReviewWorkflow
from ..workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow
from .progress_monitor import ProgressMonitor
from .result_formatter import ResultFormatter

logger = logging.getLogger(__name__)


# Request/Response Models
class CriticalReviewRequest(BaseModel):
    """Request model for Critical Review Workflow."""
    content: str = Field(..., description="Content to review")
    role_context: str = Field("", description="Additional context for the creator role")
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    execution_id: Optional[str] = Field(None, description="Optional execution ID for tracking")


class MultiPerspectiveRequest(BaseModel):
    """Request model for Multi-perspective Synthesis Workflow."""
    topic: str = Field(..., description="Topic to analyze")
    perspectives: List[str] = Field(default_factory=list, description="List of perspectives to consider")
    config: Dict[str, Any] = Field(default_factory=dict, description="Workflow configuration")
    execution_id: Optional[str] = Field(None, description="Optional execution ID for tracking")


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    success: bool
    execution_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class WorkflowStatus(BaseModel):
    """Model for workflow execution status."""
    execution_id: str
    status: str  # "running", "completed", "failed", "cancelled"
    progress: float = Field(ge=0.0, le=1.0, description="Progress percentage")
    current_step: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class APIInterface:
    """REST API interface for workflow execution."""
    
    def __init__(self):
        """Initialize the API interface."""
        self.app = FastAPI(
            title="Virtual Role Chat System API",
            description="REST API for executing institutional primitive workflows",
            version="1.0.0"
        )
        self.progress_monitor = ProgressMonitor()
        self.result_formatter = ResultFormatter()
        self.execution_status: Dict[str, WorkflowStatus] = {}
        
        # Set up routes
        self._setup_routes()
    
    async def setup_services(self) -> Dict[str, Any]:
        """Set up required services for workflow execution."""
        try:
            from ..core_services.llm_interface import EnhancedLLMInterface
            from ..core_services.role_manager import RoleManager
            from ..kernel.tool_executor import ToolExecutor
            from ..core_services.synthesis_engine import SynthesisEngine
            from ..core_services.fact_extraction_service import FactExtractionService
            from ..core_services.wiki_service import WikiService
            
            # Initialize services
            llm_interface = EnhancedLLMInterface()
            role_manager = RoleManager()
            tool_executor = ToolExecutor()
            synthesis_engine = SynthesisEngine(llm_interface)
            fact_extraction_service = FactExtractionService()
            wiki_service = WikiService()
            
            return {
                "llm_interface": llm_interface,
                "role_manager": role_manager,
                "tool_executor": tool_executor,
                "synthesis_engine": synthesis_engine,
                "fact_extraction_service": fact_extraction_service,
                "wiki_service": wiki_service
            }
        except ImportError as e:
            logger.warning(f"Some services not available: {e}")
            return {}
    
    def _setup_routes(self):
        """Set up API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                "name": "Virtual Role Chat System API",
                "version": "1.0.0",
                "description": "REST API for executing institutional primitive workflows",
                "endpoints": {
                    "workflows": "/workflows",
                    "critical_review": "/workflows/critical-review",
                    "multi_perspective": "/workflows/multi-perspective",
                    "status": "/workflows/{execution_id}/status"
                }
            }
        
        @self.app.get("/workflows")
        async def list_workflows():
            """List available workflows."""
            return {
                "workflows": [
                    {
                        "name": "critical-review",
                        "description": "Systematic fact validation through multi-role review",
                        "endpoint": "/workflows/critical-review"
                    },
                    {
                        "name": "multi-perspective",
                        "description": "Comprehensive analysis from multiple expert perspectives",
                        "endpoint": "/workflows/multi-perspective"
                    }
                ]
            }
        
        @self.app.post("/workflows/critical-review", response_model=WorkflowResponse)
        async def execute_critical_review(
            request: CriticalReviewRequest,
            background_tasks: BackgroundTasks
        ):
            """Execute Critical Review Workflow."""
            execution_id = request.execution_id or str(uuid.uuid4())
            started_at = datetime.now()
            
            # Initialize status
            self.execution_status[execution_id] = WorkflowStatus(
                execution_id=execution_id,
                status="running",
                progress=0.0,
                current_step="Initializing",
                started_at=started_at
            )
            
            # Execute workflow in background
            background_tasks.add_task(
                self._execute_critical_review_background,
                execution_id,
                request
            )
            
            return WorkflowResponse(
                success=True,
                execution_id=execution_id,
                started_at=started_at
            )
        
        @self.app.post("/workflows/multi-perspective", response_model=WorkflowResponse)
        async def execute_multi_perspective(
            request: MultiPerspectiveRequest,
            background_tasks: BackgroundTasks
        ):
            """Execute Multi-perspective Synthesis Workflow."""
            execution_id = request.execution_id or str(uuid.uuid4())
            started_at = datetime.now()
            
            # Initialize status
            self.execution_status[execution_id] = WorkflowStatus(
                execution_id=execution_id,
                status="running",
                progress=0.0,
                current_step="Initializing",
                started_at=started_at
            )
            
            # Execute workflow in background
            background_tasks.add_task(
                self._execute_multi_perspective_background,
                execution_id,
                request
            )
            
            return WorkflowResponse(
                success=True,
                execution_id=execution_id,
                started_at=started_at
            )
        
        @self.app.get("/workflows/{execution_id}/status", response_model=WorkflowStatus)
        async def get_workflow_status(execution_id: str):
            """Get workflow execution status."""
            if execution_id not in self.execution_status:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            return self.execution_status[execution_id]
        
        @self.app.get("/workflows/{execution_id}/result")
        async def get_workflow_result(execution_id: str, format: str = "json"):
            """Get workflow execution result."""
            if execution_id not in self.execution_status:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            status = self.execution_status[execution_id]
            
            if status.status == "running":
                raise HTTPException(status_code=202, detail="Workflow still running")
            
            if status.status == "failed":
                raise HTTPException(status_code=500, detail=status.error)
            
            if not status.result:
                raise HTTPException(status_code=404, detail="No result available")
            
            if format == "json":
                return JSONResponse(content=status.result)
            elif format == "markdown":
                markdown_content = self.result_formatter.format_as_markdown(status.result)
                return StreamingResponse(
                    iter([markdown_content]),
                    media_type="text/markdown",
                    headers={"Content-Disposition": f"attachment; filename=result_{execution_id}.md"}
                )
            else:
                return JSONResponse(content=status.result)
        
        @self.app.delete("/workflows/{execution_id}")
        async def cancel_workflow(execution_id: str):
            """Cancel workflow execution."""
            if execution_id not in self.execution_status:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            status = self.execution_status[execution_id]
            
            if status.status == "running":
                status.status = "cancelled"
                status.completed_at = datetime.now()
                return {"message": "Workflow cancelled"}
            else:
                return {"message": f"Workflow already {status.status}"}
        
        @self.app.get("/workflows/{execution_id}/progress")
        async def get_workflow_progress(execution_id: str):
            """Get real-time workflow progress."""
            if execution_id not in self.execution_status:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            status = self.execution_status[execution_id]
            
            return {
                "execution_id": execution_id,
                "status": status.status,
                "progress": status.progress,
                "current_step": status.current_step,
                "started_at": status.started_at,
                "completed_at": status.completed_at
            }
    
    async def _execute_critical_review_background(
        self,
        execution_id: str,
        request: CriticalReviewRequest
    ):
        """Execute Critical Review Workflow in background."""
        try:
            # Update status
            self.execution_status[execution_id].current_step = "Setting up services"
            self.execution_status[execution_id].progress = 0.1
            
            # Set up services
            services = await self.setup_services()
            
            # Update status
            self.execution_status[execution_id].current_step = "Executing workflow"
            self.execution_status[execution_id].progress = 0.2
            
            # Create and execute workflow
            workflow = CriticalReviewWorkflow(f"api_{execution_id}", request.config)
            
            # Monitor progress during execution
            async def progress_callback(step: str, progress: float):
                if execution_id in self.execution_status:
                    self.execution_status[execution_id].current_step = step
                    self.execution_status[execution_id].progress = 0.2 + (progress * 0.7)
            
            result = await workflow.execute(
                prompt=f"Please review the following content: {request.content}",
                role_context=request.role_context,
                services=services,
                execution_id=execution_id
            )
            
            # Update final status
            self.execution_status[execution_id].status = "completed" if result.get("success") else "failed"
            self.execution_status[execution_id].progress = 1.0
            self.execution_status[execution_id].current_step = "Completed"
            self.execution_status[execution_id].completed_at = datetime.now()
            self.execution_status[execution_id].result = result
            
            if not result.get("success"):
                self.execution_status[execution_id].error = result.get("error", "Unknown error")
            
        except Exception as e:
            logger.exception(f"Critical Review Workflow failed: {e}")
            self.execution_status[execution_id].status = "failed"
            self.execution_status[execution_id].error = str(e)
            self.execution_status[execution_id].completed_at = datetime.now()
    
    async def _execute_multi_perspective_background(
        self,
        execution_id: str,
        request: MultiPerspectiveRequest
    ):
        """Execute Multi-perspective Synthesis Workflow in background."""
        try:
            # Update status
            self.execution_status[execution_id].current_step = "Setting up services"
            self.execution_status[execution_id].progress = 0.1
            
            # Set up services
            services = await self.setup_services()
            
            # Update status
            self.execution_status[execution_id].current_step = "Executing workflow"
            self.execution_status[execution_id].progress = 0.2
            
            # Create and execute workflow
            workflow = MultiPerspectiveSynthesisWorkflow(f"api_{execution_id}", request.config)
            
            result = await workflow.execute(
                topic=request.topic,
                perspectives=request.perspectives,
                services=services,
                execution_id=execution_id
            )
            
            # Update final status
            self.execution_status[execution_id].status = "completed" if result.get("success") else "failed"
            self.execution_status[execution_id].progress = 1.0
            self.execution_status[execution_id].current_step = "Completed"
            self.execution_status[execution_id].completed_at = datetime.now()
            self.execution_status[execution_id].result = result
            
            if not result.get("success"):
                self.execution_status[execution_id].error = result.get("error", "Unknown error")
            
        except Exception as e:
            logger.exception(f"Multi-perspective Synthesis Workflow failed: {e}")
            self.execution_status[execution_id].status = "failed"
            self.execution_status[execution_id].error = str(e)
            self.execution_status[execution_id].completed_at = datetime.now()
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
        """Run the API server."""
        uvicorn.run(self.app, host=host, port=port, reload=reload)


# Standalone server script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Virtual Role Chat System API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run API
    api = APIInterface()
    api.run(host=args.host, port=args.port, reload=args.reload)