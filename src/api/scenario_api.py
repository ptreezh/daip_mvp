"""@Time    : 2025-08-04 17:00:00
@Author  : DAIP-LIVE Team
@File    : scenario_api.py
@Description:
    API endpoints for the three core scenarios.
    Provides RESTful interface for scenario integration service.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import scenario integration service
from src.core_services.scenario_integration_service import (
    ScenarioIntegrationService,
    ScenarioType,
    UnifiedRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/scenarios", tags=["scenarios"])

# Global service instance
scenario_service = None


async def get_scenario_service():
    """Get or create scenario service instance."""
    global scenario_service
    if scenario_service is None:
        scenario_service = await ScenarioIntegrationService()
    return scenario_service


# Pydantic models for API
class ExpertConsultationRequest(BaseModel):
    consultation_type: str = Field(..., description="Type of consultation")
    query: str = Field(..., description="Consultation query")
    user_preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")
    priority_level: str = Field(default="MEDIUM", description="Priority level")
    expected_outcomes: list[str] = Field(default_factory=list, description="Expected outcomes")


class AcademicResearchRequest(BaseModel):
    request_type: str = Field(..., description="Type of research request")
    topic: Optional[str] = Field(None, description="Research topic")
    scope: dict[str, Any] = Field(default_factory=dict, description="Research scope")
    paper: Optional[dict[str, Any]] = Field(None, description="Paper data for submission")


class IndustryAnalysisRequest(BaseModel):
    industry_type: str = Field(..., description="Industry type")
    analysis_depth: str = Field(default="OVERVIEW", description="Analysis depth")
    focus_areas: list[str] = Field(default_factory=list, description="Focus areas")
    time_horizon: str = Field(..., description="Time horizon")
    specific_questions: list[str] = Field(default_factory=list, description="Specific questions")
    priority_level: str = Field(default="MEDIUM", description="Priority level")


class UnifiedScenarioRequest(BaseModel):
    scenario_type: str = Field(..., description="Scenario type")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    request_data: dict[str, Any] = Field(..., description="Request data")
    priority: str = Field(default="medium", description="Request priority")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Request metadata")


class ScenarioResponse(BaseModel):
    success: bool
    scenario_type: str
    request_id: str
    response_data: dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    completed_at: str


# Expert Consultation Endpoints
@router.post("/expert-consultation", response_model=ScenarioResponse)
async def create_expert_consultation(
    request: ExpertConsultationRequest,
    user_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Create an expert consultation request."""
    try:
        unified_request = UnifiedRequest(
            scenario_type=ScenarioType.EXPERT_CONSULTATION,
            user_id=user_id,
            session_id=session_id,
            request_data=request.dict(),
            priority=request.priority_level.lower()
        )
        
        response = await service.process_request(unified_request)
        
        return ScenarioResponse(
            success=response.success,
            scenario_type=response.scenario_type.value,
            request_id=response.request_id,
            response_data=response.response_data,
            execution_time=response.execution_time,
            error_message=response.error_message,
            metadata=response.metadata,
            completed_at=response.completed_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Expert consultation request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expert-consultation/{consultation_id}")
async def get_expert_consultation(
    consultation_id: str,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get expert consultation status and details."""
    try:
        status = await service.get_request_status(consultation_id)
        
        if not status["success"]:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get expert consultation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expert-consultation/user/{user_id}")
async def get_user_expert_consultations(
    user_id: str,
    session_id: Optional[str] = None,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get user's expert consultation history."""
    try:
        session_info = await service.get_user_session_info(user_id, session_id)
        
        if not session_info["success"]:
            raise HTTPException(status_code=404, detail=session_info["error"])
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user expert consultations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Academic Research Endpoints
@router.post("/academic-research", response_model=ScenarioResponse)
async def create_academic_research(
    request: AcademicResearchRequest,
    user_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Create an academic research request."""
    try:
        unified_request = UnifiedRequest(
            scenario_type=ScenarioType.ACADEMIC_RESEARCH,
            user_id=user_id,
            session_id=session_id,
            request_data=request.dict(),
            priority="medium"
        )
        
        response = await service.process_request(unified_request)
        
        return ScenarioResponse(
            success=response.success,
            scenario_type=response.scenario_type.value,
            request_id=response.request_id,
            response_data=response.response_data,
            execution_time=response.execution_time,
            error_message=response.error_message,
            metadata=response.metadata,
            completed_at=response.completed_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Academic research request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/academic-research/{research_id}")
async def get_academic_research(
    research_id: str,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get academic research status and details."""
    try:
        status = await service.get_request_status(research_id)
        
        if not status["success"]:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get academic research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/academic-research/user/{user_id}")
async def get_user_academic_research(
    user_id: str,
    session_id: Optional[str] = None,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get user's academic research history."""
    try:
        session_info = await service.get_user_session_info(user_id, session_id)
        
        if not session_info["success"]:
            raise HTTPException(status_code=404, detail=session_info["error"])
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user academic research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Industry Analysis Endpoints
@router.post("/industry-analysis", response_model=ScenarioResponse)
async def create_industry_analysis(
    request: IndustryAnalysisRequest,
    user_id: str,
    session_id: str,
    background_tasks: BackgroundTasks,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Create an industry analysis request."""
    try:
        unified_request = UnifiedRequest(
            scenario_type=ScenarioType.INDUSTRY_ANALYSIS,
            user_id=user_id,
            session_id=session_id,
            request_data=request.dict(),
            priority=request.priority_level.lower()
        )
        
        response = await service.process_request(unified_request)
        
        return ScenarioResponse(
            success=response.success,
            scenario_type=response.scenario_type.value,
            request_id=response.request_id,
            response_data=response.response_data,
            execution_time=response.execution_time,
            error_message=response.error_message,
            metadata=response.metadata,
            completed_at=response.completed_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Industry analysis request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-analysis/{analysis_id}")
async def get_industry_analysis(
    analysis_id: str,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get industry analysis status and details."""
    try:
        status = await service.get_request_status(analysis_id)
        
        if not status["success"]:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get industry analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/industry-analysis/user/{user_id}")
async def get_user_industry_analysis(
    user_id: str,
    session_id: Optional[str] = None,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get user's industry analysis history."""
    try:
        session_info = await service.get_user_session_info(user_id, session_id)
        
        if not session_info["success"]:
            raise HTTPException(status_code=404, detail=session_info["error"])
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user industry analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Unified Scenario Endpoints
@router.post("/unified", response_model=ScenarioResponse)
async def process_unified_scenario_request(
    request: UnifiedScenarioRequest,
    background_tasks: BackgroundTasks,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Process a unified scenario request."""
    try:
        unified_request = UnifiedRequest(
            scenario_type=ScenarioType(request.scenario_type),
            user_id=request.user_id,
            session_id=request.session_id,
            request_data=request.request_data,
            priority=request.priority,
            metadata=request.metadata
        )
        
        response = await service.process_request(unified_request)
        
        return ScenarioResponse(
            success=response.success,
            scenario_type=response.scenario_type.value,
            request_id=response.request_id,
            response_data=response.response_data,
            execution_time=response.execution_time,
            error_message=response.error_message,
            metadata=response.metadata,
            completed_at=response.completed_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Unified scenario request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Service Management Endpoints
@router.get("/health")
async def scenario_health_check(
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Health check for scenario services."""
    try:
        health = await service.health_check()
        return health
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_scenario_metrics(
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get scenario service metrics."""
    try:
        metrics = await service.get_service_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_scenario_capabilities(
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get scenario capabilities."""
    try:
        capabilities = await service.get_scenario_capabilities()
        return capabilities
        
    except Exception as e:
        logger.error(f"Failed to get capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{request_id}")
async def get_request_status(
    request_id: str,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get status of any request by ID."""
    try:
        status = await service.get_request_status(request_id)
        
        if not status["success"]:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get request status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Get all sessions for a user."""
    try:
        session_info = await service.get_user_session_info(user_id)
        
        if not session_info["success"]:
            raise HTTPException(status_code=404, detail=session_info["error"])
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Batch Processing Endpoints
@router.post("/batch")
async def process_batch_requests(
    requests: list[UnifiedScenarioRequest],
    background_tasks: BackgroundTasks,
    service: ScenarioIntegrationService = Depends(get_scenario_service)
):
    """Process multiple scenario requests in batch."""
    try:
        results = []
        
        for request in requests:
            try:
                unified_request = UnifiedRequest(
                    scenario_type=ScenarioType(request.scenario_type),
                    user_id=request.user_id,
                    session_id=request.session_id,
                    request_data=request.request_data,
                    priority=request.priority,
                    metadata=request.metadata
                )
                
                response = await service.process_request(unified_request)
                
                results.append(ScenarioResponse(
                    success=response.success,
                    scenario_type=response.scenario_type.value,
                    request_id=response.request_id,
                    response_data=response.response_data,
                    execution_time=response.execution_time,
                    error_message=response.error_message,
                    metadata=response.metadata,
                    completed_at=response.completed_at.isoformat()
                ))
                
            except Exception as e:
                logger.error(f"Batch request failed: {e}")
                results.append(ScenarioResponse(
                    success=False,
                    scenario_type=request.scenario_type,
                    request_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                    response_data={},
                    execution_time=0.0,
                    error_message=str(e),
                    metadata={},
                    completed_at=datetime.now().isoformat()
                ))
        
        return {
            "success": True,
            "total_requests": len(requests),
            "successful_requests": len([r for r in results if r.success]),
            "failed_requests": len([r for r in results if not r.success]),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handling - these will be registered with the main app
def value_error_handler(request, exc):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


def general_error_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include router in main application
def include_scenario_router(app):
    """Include scenario router in FastAPI application."""
    app.include_router(router)
    logger.info("Scenario API router included in application")