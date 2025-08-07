# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 16:45:00
@Author  : DAIP-LIVE Team
@File    : scenario_integration_service.py
@Description:
    Integration service for the three core scenarios.
    Connects scenarios with the main system and provides unified API.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

# Import the three core scenarios
from src.core_services.expert_consultation_scenario import (
    ExpertConsultationScenario,
    ExpertConsultationRequest,
    ConsultationType,
    ConsultationPriority
)
from src.core_services.academic_research_scenario import (
    AcademicResearchScenario,
    ResearchPaper,
    ResearchType,
    AcademicStandard
)
from src.core_services.industry_analysis_scenario import (
    IndustryAnalysisScenario,
    AnalysisRequest,
    IndustryType,
    AnalysisDepth
)

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Scenario types for unified interface"""
    EXPERT_CONSULTATION = "expert_consultation"
    ACADEMIC_RESEARCH = "academic_research"
    INDUSTRY_ANALYSIS = "industry_analysis"


@dataclass
class UnifiedRequest:
    """Unified request format for all scenarios"""
    scenario_type: ScenarioType
    user_id: str
    session_id: str
    request_data: Dict[str, Any]
    priority: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class UnifiedResponse:
    """Unified response format for all scenarios"""
    success: bool
    scenario_type: ScenarioType
    request_id: str
    response_data: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)


class ScenarioIntegrationService:
    """
    Integration service for the three core scenarios.
    Provides unified interface and manages scenario lifecycle.
    """
    
    def __init__(self):
        """Initialize the scenario integration service."""
        self.service_id = f"scenario_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize scenarios
        self.expert_scenario = ExpertConsultationScenario()
        self.academic_scenario = AcademicResearchScenario()
        self.industry_scenario = IndustryAnalysisScenario()
        
        # Request tracking
        self.active_requests = {}
        self.request_history = []
        self.user_sessions = {}
        
        # Performance metrics
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_execution_time": 0.0,
            "scenario_usage": {
                "expert_consultation": 0,
                "academic_research": 0,
                "industry_analysis": 0
            }
        }
        
        logger.info(f"Scenario Integration Service initialized: {self.service_id}")
    
    async def process_request(self, request: UnifiedRequest) -> UnifiedResponse:
        """Process a unified request and route to appropriate scenario."""
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing {request.scenario_type.value} request for user {request.user_id}")
            
            # Update metrics
            self.performance_metrics["total_requests"] += 1
            self.performance_metrics["scenario_usage"][request.scenario_type.value] += 1
            
            # Route to appropriate scenario
            if request.scenario_type == ScenarioType.EXPERT_CONSULTATION:
                result = await self._process_expert_consultation(request)
            elif request.scenario_type == ScenarioType.ACADEMIC_RESEARCH:
                result = await self._process_academic_research(request)
            elif request.scenario_type == ScenarioType.INDUSTRY_ANALYSIS:
                result = await self._process_industry_analysis(request)
            else:
                raise ValueError(f"Unsupported scenario type: {request.scenario_type}")
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Update metrics
            if result["success"]:
                self.performance_metrics["successful_requests"] += 1
            else:
                self.performance_metrics["failed_requests"] += 1
            
            # Update average execution time
            total_time = self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_requests"] - 1)
            total_time += execution_time
            self.performance_metrics["average_execution_time"] = total_time / self.performance_metrics["total_requests"]
            
            # Create unified response
            response = UnifiedResponse(
                success=result["success"],
                scenario_type=request.scenario_type,
                request_id=request.request_data.get("request_id", f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                response_data=result,
                execution_time=execution_time,
                metadata={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "scenario_specific_data": result.get("metadata", {})
                }
            )
            
            # Store request in history
            self._store_request_history(request, response)
            
            # Update user session
            self._update_user_session(request.user_id, request.session_id, response)
            
            logger.info(f"Request processed successfully in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            
            # Create error response
            execution_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics["failed_requests"] += 1
            
            return UnifiedResponse(
                success=False,
                scenario_type=request.scenario_type,
                request_id=request.request_data.get("request_id", f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                response_data={},
                execution_time=execution_time,
                error_message=str(e),
                metadata={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "error_details": {"exception_type": type(e).__name__}
                }
            )
    
    async def _process_expert_consultation(self, request: UnifiedRequest) -> Dict[str, Any]:
        """Process expert consultation request."""
        data = request.request_data
        
        # Create consultation request
        consultation_request = ExpertConsultationRequest(
            consultation_type=ConsultationType(data.get("consultation_type", "TECHNICAL_REVIEW")),
            query=data.get("query", ""),
            user_preferences=data.get("user_preferences", {}),
            priority_level=ConsultationPriority(data.get("priority_level", "MEDIUM")),
            expected_outcomes=data.get("expected_outcomes", [])
        )
        
        # Process consultation
        result = await self.expert_scenario.handle_consultation(consultation_request)
        
        return {
            "success": result.get("success", False),
            "consultation_id": result.get("consultation_id"),
            "selected_experts": result.get("selected_experts", []),
            "synthesis": result.get("synthesis", {}),
            "metadata": {
                "expert_count": len(result.get("selected_experts", [])),
                "consultation_type": data.get("consultation_type"),
                "priority_level": data.get("priority_level")
            }
        }
    
    async def _process_academic_research(self, request: UnifiedRequest) -> Dict[str, Any]:
        """Process academic research request."""
        data = request.request_data
        
        # Determine request type
        request_type = data.get("request_type", "literature_review")
        
        if request_type == "literature_review":
            # Process literature review
            result = await self.academic_scenario.conduct_literature_review(
                topic=data.get("topic", ""),
                scope=data.get("scope", {})
            )
            
            return {
                "success": result.get("success", False),
                "review_id": result.get("review_id"),
                "papers_found": result.get("papers_found", 0),
                "key_themes": result.get("key_themes", []),
                "metadata": {
                    "request_type": "literature_review",
                    "topic": data.get("topic"),
                    "papers_found": result.get("papers_found", 0)
                }
            }
        
        elif request_type == "paper_submission":
            # Process paper submission
            paper_data = data.get("paper", {})
            research_paper = ResearchPaper(
                title=paper_data.get("title", ""),
                abstract=paper_data.get("abstract", ""),
                authors=paper_data.get("authors", []),
                keywords=paper_data.get("keywords", []),
                research_type=ResearchType(paper_data.get("research_type", "EMPIRICAL_RESEARCH")),
                academic_standard=AcademicStandard(paper_data.get("academic_standard", "PEER_REVIEWED")),
                content=paper_data.get("content", "")
            )
            
            result = await self.academic_scenario.submit_research_paper(research_paper)
            
            return {
                "success": result.get("success", False),
                "paper_id": result.get("paper_id"),
                "assigned_reviewers": result.get("assigned_reviewers", []),
                "review_deadline": result.get("review_deadline"),
                "metadata": {
                    "request_type": "paper_submission",
                    "title": paper_data.get("title"),
                    "authors": paper_data.get("authors", [])
                }
            }
        
        else:
            raise ValueError(f"Unsupported academic research request type: {request_type}")
    
    async def _process_industry_analysis(self, request: UnifiedRequest) -> Dict[str, Any]:
        """Process industry analysis request."""
        data = request.request_data
        
        # Create analysis request
        analysis_request = AnalysisRequest(
            industry_type=IndustryType(data.get("industry_type", "TECHNOLOGY")),
            analysis_depth=AnalysisDepth(data.get("analysis_depth", "OVERVIEW")),
            focus_areas=data.get("focus_areas", []),
            time_horizon=data.get("time_horizon", "1-2 years"),
            specific_questions=data.get("specific_questions", []),
            priority_level=data.get("priority_level", "MEDIUM")
        )
        
        # Process analysis
        result = await self.industry_scenario.submit_analysis_request(analysis_request)
        
        return {
            "success": result.get("success", False),
            "request_id": result.get("request_id"),
            "report_id": result.get("report_id"),
            "selected_experts": result.get("selected_experts", []),
            "quality_score": result.get("quality_score", 0.0),
            "metadata": {
                "industry_type": data.get("industry_type"),
                "analysis_depth": data.get("analysis_depth"),
                "expert_count": len(result.get("selected_experts", [])),
                "quality_score": result.get("quality_score", 0.0)
            }
        }
    
    def _store_request_history(self, request: UnifiedRequest, response: UnifiedResponse):
        """Store request in history."""
        history_record = {
            "request_id": response.request_id,
            "scenario_type": request.scenario_type.value,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "success": response.success,
            "execution_time": response.execution_time,
            "created_at": request.created_at.isoformat(),
            "completed_at": response.completed_at.isoformat(),
            "priority": request.priority,
            "error_message": response.error_message
        }
        
        self.request_history.append(history_record)
        
        # Keep history size manageable
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-500:]
    
    def _update_user_session(self, user_id: str, session_id: str, response: UnifiedResponse):
        """Update user session information."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "user_id": user_id,
                "active_sessions": {},
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "last_activity": datetime.now().isoformat()
            }
        
        user_session = self.user_sessions[user_id]
        
        # Update session
        if session_id not in user_session["active_sessions"]:
            user_session["active_sessions"][session_id] = {
                "session_id": session_id,
                "requests": [],
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat()
            }
        
        session = user_session["active_sessions"][session_id]
        session["requests"].append({
            "request_id": response.request_id,
            "scenario_type": response.scenario_type.value,
            "success": response.success,
            "execution_time": response.execution_time,
            "timestamp": response.completed_at.isoformat()
        })
        
        session["last_activity"] = response.completed_at.isoformat()
        
        # Update user metrics
        user_session["total_requests"] += 1
        if response.success:
            user_session["successful_requests"] += 1
        else:
            user_session["failed_requests"] += 1
        
        user_session["last_activity"] = response.completed_at.isoformat()
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get status of a specific request."""
        # Search in history
        for record in self.request_history:
            if record["request_id"] == request_id:
                return {
                    "success": True,
                    "request_id": request_id,
                    "status": "completed",
                    "record": record
                }
        
        return {
            "success": False,
            "error": f"Request {request_id} not found"
        }
    
    async def get_user_session_info(self, user_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user session information."""
        if user_id not in self.user_sessions:
            return {
                "success": False,
                "error": f"User {user_id} not found"
            }
        
        user_session = self.user_sessions[user_id]
        
        if session_id:
            # Get specific session
            if session_id not in user_session["active_sessions"]:
                return {
                    "success": False,
                    "error": f"Session {session_id} not found for user {user_id}"
                }
            
            return {
                "success": True,
                "user_id": user_id,
                "session": user_session["active_sessions"][session_id]
            }
        else:
            # Get all user sessions
            return {
                "success": True,
                "user_id": user_id,
                "user_session": user_session,
                "active_sessions": list(user_session["active_sessions"].values())
            }
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics."""
        return {
            "service_id": self.service_id,
            "performance_metrics": self.performance_metrics,
            "active_users": len(self.user_sessions),
            "active_sessions": sum(len(user["active_sessions"]) for user in self.user_sessions.values()),
            "total_requests_history": len(self.request_history),
            "success_rate": (
                self.performance_metrics["successful_requests"] / 
                max(self.performance_metrics["total_requests"], 1)
            ) * 100,
            "average_execution_time": self.performance_metrics["average_execution_time"]
        }
    
    async def get_scenario_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all scenarios."""
        return {
            "expert_consultation": {
                "name": "Expert Consultation",
                "description": "Get expert advice and consultation on various topics",
                "consultation_types": [ct.value for ct in ConsultationType],
                "priority_levels": [pl.value for pl in ConsultationPriority],
                "expert_pool_size": len(self.expert_scenario.expert_pool)
            },
            "academic_research": {
                "name": "Academic Research",
                "description": "Conduct academic research and literature reviews",
                "research_types": [rt.value for rt in ResearchType],
                "academic_standards": [as_val.value for as_val in AcademicStandard],
                "reviewer_pool_size": len(self.academic_scenario.reviewer_pool)
            },
            "industry_analysis": {
                "name": "Industry Analysis",
                "description": "Analyze industries and markets with expert insights",
                "industry_types": [it.value for it in IndustryType],
                "analysis_depths": [ad.value for ad in AnalysisDepth],
                "expert_pool_size": len(self.industry_scenario.expert_pool)
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of all scenarios."""
        health_status = {
            "service_id": self.service_id,
            "overall_status": "healthy",
            "scenarios": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check expert consultation scenario
        try:
            expert_health = {
                "status": "healthy",
                "expert_pool_size": len(self.expert_scenario.expert_pool),
                "recent_requests": len([r for r in self.request_history[-10:] if r["scenario_type"] == "expert_consultation"])
            }
        except Exception as e:
            expert_health = {"status": "unhealthy", "error": str(e)}
        
        # Check academic research scenario
        try:
            academic_health = {
                "status": "healthy",
                "reviewer_pool_size": len(self.academic_scenario.reviewer_pool),
                "recent_requests": len([r for r in self.request_history[-10:] if r["scenario_type"] == "academic_research"])
            }
        except Exception as e:
            academic_health = {"status": "unhealthy", "error": str(e)}
        
        # Check industry analysis scenario
        try:
            industry_health = {
                "status": "healthy",
                "expert_pool_size": len(self.industry_scenario.expert_pool),
                "recent_requests": len([r for r in self.request_history[-10:] if r["scenario_type"] == "industry_analysis"])
            }
        except Exception as e:
            industry_health = {"status": "unhealthy", "error": str(e)}
        
        health_status["scenarios"] = {
            "expert_consultation": expert_health,
            "academic_research": academic_health,
            "industry_analysis": industry_health
        }
        
        # Determine overall status
        scenario_statuses = [health["status"] for health in health_status["scenarios"].values()]
        if "unhealthy" in scenario_statuses:
            health_status["overall_status"] = "degraded"
        
        return health_status


# Convenience functions
async def create_scenario_integration_service() -> ScenarioIntegrationService:
    """Create and initialize scenario integration service."""
    return ScenarioIntegrationService()


async def process_unified_request(
    scenario_type: str,
    user_id: str,
    session_id: str,
    request_data: Dict[str, Any],
    priority: str = "medium"
) -> Dict[str, Any]:
    """Convenience function to process a unified request."""
    service = await create_scenario_integration_service()
    
    request = UnifiedRequest(
        scenario_type=ScenarioType(scenario_type),
        user_id=user_id,
        session_id=session_id,
        request_data=request_data,
        priority=priority
    )
    
    response = await service.process_request(request)
    
    # Convert to dict for JSON serialization
    return {
        "success": response.success,
        "scenario_type": response.scenario_type.value,
        "request_id": response.request_id,
        "response_data": response.response_data,
        "execution_time": response.execution_time,
        "error_message": response.error_message,
        "metadata": response.metadata,
        "completed_at": response.completed_at.isoformat()
    }


# Example usage
async def main():
    """Example usage of the scenario integration service."""
    service = await create_scenario_integration_service()
    
    # Test expert consultation
    consultation_request = UnifiedRequest(
        scenario_type=ScenarioType.EXPERT_CONSULTATION,
        user_id="test_user",
        session_id="test_session",
        request_data={
            "consultation_type": "TECHNICAL_REVIEW",
            "query": "How to implement microservices architecture?",
            "priority_level": "HIGH"
        }
    )
    
    result = await service.process_request(consultation_request)
    print(f"Consultation result: {result.success}")
    
    # Test academic research
    research_request = UnifiedRequest(
        scenario_type=ScenarioType.ACADEMIC_RESEARCH,
        user_id="test_user",
        session_id="test_session",
        request_data={
            "request_type": "literature_review",
            "topic": "Machine Learning in Healthcare",
            "scope": {"time_range": "2020-2024"}
        }
    )
    
    result = await service.process_request(research_request)
    print(f"Research result: {result.success}")
    
    # Test industry analysis
    industry_request = UnifiedRequest(
        scenario_type=ScenarioType.INDUSTRY_ANALYSIS,
        user_id="test_user",
        session_id="test_session",
        request_data={
            "industry_type": "TECHNOLOGY",
            "analysis_depth": "DETAILED",
            "focus_areas": ["AI", "Cloud Computing"],
            "time_horizon": "3-5 years"
        }
    )
    
    result = await service.process_request(industry_request)
    print(f"Industry analysis result: {result.success}")
    
    # Get service metrics
    metrics = await service.get_service_metrics()
    print(f"Service metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())