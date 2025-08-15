"""@Time: 2025-08-03
@Author: Claude Code
@File: v0_3_5_critical_review_api.py
@Description: FastAPI integration for V0.3.5 Critical Review Workflow
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.core_services.automated_report_generator import (
    AutomatedReportGenerator,
    ReportFormat,
    ReportRequest,
    ReportType,
)
from src.core_services.collaborative_review_environment import CollaborativeReviewEnvironment
from src.core_services.conflict_resolution_system import ConflictResolutionSystem
from src.core_services.multidimensional_assessment_engine import MultidimensionalAssessmentEngine
from src.core_services.review_analytics import ReviewAnalytics

# Import V0.3.5 components
from src.core_services.smart_reviewer_allocator import SmartReviewerAllocator


# Pydantic models for API
class ReviewerSelectionRequest(BaseModel):
    content_type: str
    content_tags: list[str]
    required_count: int
    context: Optional[dict[str, Any]] = None

class AssessmentRequest(BaseModel):
    content: str
    content_type: str
    assessor_id: str
    context: Optional[dict[str, Any]] = None

class SessionCreationRequest(BaseModel):
    session_name: str
    participants: list[str]
    content_type: str
    initial_content: Optional[str] = None
    settings: Optional[dict[str, Any]] = None

class CommentRequest(BaseModel):
    session_id: str
    user_id: str
    content: str
    parent_comment_id: Optional[str] = None
    position: Optional[dict[str, Any]] = None

class ReportGenerationRequest(BaseModel):
    report_type: str
    report_format: str
    template_id: Optional[str] = None
    data_sources: dict[str, Any]
    parameters: Optional[dict[str, Any]] = None
    priority: str = "normal"

# Initialize components
allocator = SmartReviewerAllocator()
assessment_engine = MultidimensionalAssessmentEngine()
review_environment = CollaborativeReviewEnvironment()
conflict_resolver = ConflictResolutionSystem()
review_analytics = ReviewAnalytics()
report_generator = AutomatedReportGenerator()

# Create router
router = APIRouter(prefix="/api/v0.3.5/critical-review", tags=["v0.3.5-critical-review"])

# Startup and shutdown events
@router.on_event("startup")
async def startup_event():
    """Initialize V0.3.5 components"""
    await conflict_resolver.start()
    await review_analytics.start()
    await report_generator.start()
    print("V0.3.5 Critical Review Workflow components initialized")

@router.on_event("shutdown")
async def shutdown_event():
    """Shutdown V0.3.5 components"""
    await conflict_resolver.stop()
    await review_analytics.stop()
    await report_generator.stop()
    print("V0.3.5 Critical Review Workflow components shutdown")

# === Smart Reviewer Allocator Endpoints ===

@router.post("/reviewers/select", response_model=dict[str, Any])
async def select_reviewers(request: ReviewerSelectionRequest):
    """Select optimal reviewers for content"""
    try:
        result = await allocator.select_reviewers(
            content_type=request.content_type,
            content_tags=request.content_tags,
            required_count=request.required_count,
            context=request.context or {}
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reviewers/pool", response_model=dict[str, Any])
async def get_reviewer_pool():
    """Get current reviewer pool"""
    try:
        return {
            "success": True,
            "reviewer_pool": allocator.reviewer_pool,
            "pool_stats": allocator.get_pool_stats()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reviewers/add", response_model=dict[str, Any])
async def add_reviewer(reviewer_id: str, reviewer_data: dict[str, Any]):
    """Add a new reviewer to the pool"""
    try:
        result = allocator.add_reviewer(reviewer_id, reviewer_data)
        return {
            "success": True,
            "reviewer_id": reviewer_id,
            "message": "Reviewer added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Multidimensional Assessment Engine Endpoints ===

@router.post("/assessment/assess", response_model=dict[str, Any])
async def assess_content(request: AssessmentRequest):
    """Assess content using multidimensional criteria"""
    try:
        result = await assessment_engine.assess_content(
            content=request.content,
            content_type=request.content_type,
            assessor_id=request.assessor_id,
            context=request.context or {}
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        # Record assessment metric
        from src.core_services.review_analytics import AnalysisScope, MetricType, ReviewMetric
        
        metric = ReviewMetric(
            metric_id=f"assessment_{result['assessment_id']}",
            metric_type=MetricType.QUALITY,
            name=f"{request.content_type}_quality_score",
            value=result['overall_score'],
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context={
                'assessor_id': request.assessor_id,
                'content_type': request.content_type,
                'assessment_id': result['assessment_id']
            }
        )
        
        await review_analytics.record_metric(metric)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/batch", response_model=list[dict[str, Any]])
async def batch_assess_content(requests: list[AssessmentRequest]):
    """Batch assess multiple content items"""
    try:
        # Convert to engine format
        engine_requests = []
        for req in requests:
            engine_requests.append({
                'content': req.content,
                'content_type': req.content_type,
                'assessor_id': req.assessor_id,
                'context': req.context or {}
            })
        
        results = await assessment_engine.batch_assess(engine_requests)
        
        # Record batch metrics
        successful_results = [r for r in results if r['success']]
        if successful_results:
            avg_score = sum(r['overall_score'] for r in successful_results) / len(successful_results)
            
            from src.core_services.review_analytics import AnalysisScope, MetricType, ReviewMetric
            
            metric = ReviewMetric(
                metric_id=f"batch_assessment_{datetime.now().isoformat()}",
                metric_type=MetricType.QUALITY,
                name="batch_assessment_avg_score",
                value=avg_score,
                scope=AnalysisScope.TEAM,
                timestamp=datetime.now(),
                context={
                    'batch_size': len(requests),
                    'successful_count': len(successful_results)
                }
            )
            
            await review_analytics.record_metric(metric)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessment/criteria/{content_type}", response_model=dict[str, Any])
async def get_assessment_criteria(content_type: str):
    """Get assessment criteria for content type"""
    try:
        criteria = assessment_engine.get_criteria_for_content_type(content_type)
        return {
            "success": True,
            "content_type": content_type,
            "criteria": criteria
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Collaborative Review Environment Endpoints ===

@router.post("/sessions/create", response_model=dict[str, Any])
async def create_review_session(request: SessionCreationRequest):
    """Create a new collaborative review session"""
    try:
        result = await review_environment.create_session(
            session_name=request.session_name,
            participants=request.participants,
            content_type=request.content_type,
            initial_content=request.initial_content,
            settings=request.settings or {}
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        # Record session creation metric
        from src.core_services.review_analytics import AnalysisScope, MetricType, ReviewMetric
        
        metric = ReviewMetric(
            metric_id=f"session_{result['session_id']}",
            metric_type=MetricType.PARTICIPATION,
            name="session_creation",
            value=1.0,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context={
                'session_id': result['session_id'],
                'participant_count': len(request.participants),
                'content_type': request.content_type
            }
        )
        
        await review_analytics.record_metric(metric)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", response_model=dict[str, Any])
async def get_session_info(session_id: str):
    """Get session information"""
    try:
        session = review_environment.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {
            "success": True,
            "session": session.to_dict() if hasattr(session, 'to_dict') else session
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/join", response_model=dict[str, Any])
async def join_session(session_id: str, user_id: str):
    """Join a review session"""
    try:
        result = await review_environment.join_session(session_id, user_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/leave", response_model=dict[str, Any])
async def leave_session(session_id: str, user_id: str):
    """Leave a review session"""
    try:
        result = await review_environment.leave_session(session_id, user_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/comments", response_model=dict[str, Any])
async def add_comment(request: CommentRequest):
    """Add a comment to a review session"""
    try:
        result = await review_environment.add_comment(
            session_id=request.session_id,
            user_id=request.user_id,
            content=request.content,
            parent_comment_id=request.parent_comment_id,
            position=request.position
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        # Record comment metric
        from src.core_services.review_analytics import AnalysisScope, MetricType, ReviewMetric
        
        metric = ReviewMetric(
            metric_id=f"comment_{result['comment_id']}",
            metric_type=MetricType.PARTICIPATION,
            name="comment_added",
            value=1.0,
            scope=AnalysisScope.SESSION,
            timestamp=datetime.now(),
            context={
                'session_id': request.session_id,
                'user_id': request.user_id,
                'comment_id': result['comment_id']
            }
        )
        
        await review_analytics.record_metric(metric)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/comments", response_model=list[dict[str, Any]])
async def get_session_comments(session_id: str):
    """Get all comments for a session"""
    try:
        comments = review_environment.get_session_comments(session_id)
        return [comment.to_dict() if hasattr(comment, 'to_dict') else comment for comment in comments]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Conflict Resolution System Endpoints ===

@router.get("/conflicts/system-stats", response_model=dict[str, Any])
async def get_conflict_system_stats():
    """Get conflict resolution system statistics"""
    try:
        return await conflict_resolver.get_system_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conflicts/{conflict_id}/status", response_model=dict[str, Any])
async def get_conflict_status(conflict_id: str):
    """Get conflict resolution status"""
    try:
        status = await conflict_resolver.get_conflict_status(conflict_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conflicts/{conflict_id}/resolve", response_model=dict[str, Any])
async def resolve_conflict(conflict_id: str, strategy: Optional[str] = None):
    """Manually resolve a conflict"""
    try:
        from src.core_services.conflict_resolution_system import ResolutionStrategy
        
        resolution_strategy = None
        if strategy:
            try:
                resolution_strategy = ResolutionStrategy(strategy)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}")
        
        result = await conflict_resolver.resolve_conflict(conflict_id, resolution_strategy)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
            
        return {
            "success": True,
            "conflict_id": conflict_id,
            "resolution": result.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Review Analytics Endpoints ===

@router.get("/analytics/system-stats", response_model=dict[str, Any])
async def get_analytics_system_stats():
    """Get review analytics system statistics"""
    try:
        return await review_analytics.get_system_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/metrics/{scope}/{scope_id}", response_model=list[dict[str, Any]])
async def get_scope_metrics(scope: str, scope_id: str):
    """Get metrics for a specific scope"""
    try:
        from src.core_services.review_analytics import AnalysisScope
        
        analysis_scope = AnalysisScope(scope)
        metrics = await review_analytics._get_relevant_metrics(analysis_scope, scope_id)
        
        return [metric.to_dict() for metric in metrics]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/insights/{scope}/{scope_id}", response_model=list[dict[str, Any]])
async def get_scope_insights(scope: str, scope_id: str):
    """Get insights for a specific scope"""
    try:
        from src.core_services.review_analytics import AnalysisScope
        
        analysis_scope = AnalysisScope(scope)
        insights = await review_analytics.generate_insights(analysis_scope, scope_id)
        
        return [insight.to_dict() for insight in insights]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/reports/generate", response_model=dict[str, Any])
async def generate_analytics_report(
    scope: str,
    scope_id: str,
    start_date: datetime,
    end_date: datetime
):
    """Generate analytics report"""
    try:
        from src.core_services.review_analytics import AnalysisScope
        
        analysis_scope = AnalysisScope(scope)
        report = await review_analytics.generate_report(
            scope=analysis_scope,
            scope_id=scope_id,
            time_period=(start_date, end_date)
        )
        
        return {
            "success": True,
            "report": report.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Automated Report Generator Endpoints ===

@router.post("/reports/generate", response_model=dict[str, Any])
async def generate_report(request: ReportGenerationRequest):
    """Generate an automated report"""
    try:
        # Parse enum values
        report_type = ReportType(request.report_type)
        report_format = ReportFormat(request.report_format)
        
        # Create report request
        report_request = ReportRequest(
            request_id=f"report_{datetime.now().isoformat()}",
            report_type=report_type,
            report_format=report_format,
            template_id=request.template_id,
            data_sources=request.data_sources,
            parameters=request.parameters or {},
            requested_by="api_user",
            requested_at=datetime.now(),
            priority=request.priority
        )
        
        request_id = await report_generator.generate_report(report_request)
        
        return {
            "success": True,
            "request_id": request_id,
            "message": "Report generation started"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/status/{request_id}", response_model=dict[str, Any])
async def get_report_status(request_id: str):
    """Get report generation status"""
    try:
        status = await report_generator.get_report_status(request_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/download/{report_id}")
async def download_report(report_id: str):
    """Download a generated report"""
    try:
        content = await report_generator.download_report(report_id)
        if not content:
            raise HTTPException(status_code=404, detail="Report not found")
            
        # Return as HTML response
        return HTMLResponse(content=content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/templates", response_model=list[dict[str, Any]])
async def list_report_templates():
    """List available report templates"""
    try:
        templates = await report_generator.list_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Workflow Orchestration Endpoints ===

@router.post("/workflow/start", response_model=dict[str, Any])
async def start_critical_review_workflow(
    content: str,
    content_type: str,
    required_reviewers: int = 3,
    content_tags: Optional[list[str]] = None
):
    """Start a complete critical review workflow"""
    try:
        workflow_id = f"workflow_{datetime.now().isoformat()}"
        
        # Step 1: Select reviewers
        reviewer_result = await allocator.select_reviewers(
            content_type=content_type,
            content_tags=content_tags or [],
            required_count=required_reviewers
        )
        
        if not reviewer_result['success']:
            raise HTTPException(status_code=400, detail=f"Reviewer selection failed: {reviewer_result['error']}")
        
        # Step 2: Create review session
        session_result = await review_environment.create_session(
            session_name=f"Critical Review: {content_type}",
            participants=reviewer_result['selected_reviewers'],
            content_type=content_type,
            initial_content=content
        )
        
        if not session_result['success']:
            raise HTTPException(status_code=400, detail=f"Session creation failed: {session_result['error']}")
        
        # Step 3: Start assessments
        assessment_tasks = []
        for reviewer_id in reviewer_result['selected_reviewers']:
            task = assessment_engine.assess_content(
                content=content,
                content_type=content_type,
                assessor_id=reviewer_id,
                context={'session_id': session_result['session_id']}
            )
            assessment_tasks.append(task)
        
        # Run assessments in parallel
        assessment_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
        
        # Process results
        successful_assessments = []
        for i, result in enumerate(assessment_results):
            if isinstance(result, Exception):
                print(f"Assessment {i} failed: {result}")
            elif result.get('success'):
                successful_assessments.append(result)
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "session_id": session_result['session_id'],
            "selected_reviewers": reviewer_result['selected_reviewers'],
            "assessments_completed": len(successful_assessments),
            "assessment_results": successful_assessments,
            "next_steps": [
                f"Review session created: {session_result['session_id']}",
                f"Join session at: /sessions/{session_result['session_id']}",
                "Use analytics endpoints to monitor progress"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/status/{workflow_id}", response_model=dict[str, Any])
async def get_workflow_status(workflow_id: str):
    """Get workflow status (placeholder implementation)"""
    try:
        # In a real implementation, this would query a workflow database
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": "completed",
            "message": "Workflow status tracking not fully implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Health Check and System Status ===

@router.get("/health", response_model=dict[str, Any])
async def health_check():
    """Health check for all V0.3.5 components"""
    try:
        component_status = {
            "smart_reviewer_allocator": {
                "status": "healthy" if allocator else "unhealthy",
                "pool_size": len(allocator.reviewer_pool) if allocator else 0
            },
            "assessment_engine": {
                "status": "healthy" if assessment_engine else "unhealthy",
                "criteria_count": len(assessment_engine.assessment_criteria) if assessment_engine else 0
            },
            "review_environment": {
                "status": "healthy" if review_environment else "unhealthy",
                "active_sessions": len(review_environment.active_sessions) if review_environment else 0
            },
            "conflict_resolver": {
                "status": "healthy" if conflict_resolver else "unhealthy",
                "active_conflicts": len(conflict_resolver.active_conflicts) if conflict_resolver else 0
            },
            "review_analytics": {
                "status": "healthy" if review_analytics else "unhealthy",
                "metrics_recorded": len(review_analytics.metrics_history) if review_analytics else 0
            },
            "report_generator": {
                "status": "healthy" if report_generator else "unhealthy",
                "available_templates": len(report_generator.templates) if report_generator else 0
            }
        }
        
        overall_status = "healthy" if all(
            comp["status"] == "healthy" for comp in component_status.values()
        ) else "degraded"
        
        return {
            "status": overall_status,
            "version": "V0.3.5",
            "components": component_status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include this router in your main FastAPI app
# app.include_router(v0_3_5_router)