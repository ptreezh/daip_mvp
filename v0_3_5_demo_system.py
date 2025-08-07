"""
@Time: 2025-08-03
@Author: Claude Code
@File: v0_3_5_demo_system.py
@Description: V0.3.5 Critical Review Workflow Demo System
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import V0.3.5 components
from src.api.v0_3_5_critical_review_api import router as v0_3_5_router
from src.core_services.smart_reviewer_allocator import SmartReviewerAllocator
from src.core_services.multidimensional_assessment_engine import MultidimensionalAssessmentEngine
from src.core_services.collaborative_review_environment import CollaborativeReviewEnvironment
from src.core_services.conflict_resolution_system import ConflictResolutionSystem
from src.core_services.review_analytics import ReviewAnalytics
from src.core_services.automated_report_generator import AutomatedReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class V0_3_5_DemoSystem:
    """
    V0.3.5 Critical Review Workflow Demo System
    Complete demonstration of all components working together
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="V0.3.5 Critical Review Workflow Demo",
            description="智能协作评审系统演示",
            version="0.3.5"
        )
        
        # Initialize components
        self.allocator = SmartReviewerAllocator()
        self.assessment_engine = MultidimensionalAssessmentEngine()
        self.review_environment = CollaborativeReviewEnvironment()
        self.conflict_resolver = ConflictResolutionSystem()
        self.review_analytics = ReviewAnalytics()
        self.report_generator = AutomatedReportGenerator()
        
        # Setup demo data
        self._setup_demo_data()
        
        # Setup FastAPI app
        self._setup_app()
        
    def _setup_demo_data(self):
        """Setup demo data for the system"""
        # Add demo reviewers
        demo_reviewers = {
            'alice_chen': {
                'expertise': ['python', 'testing', 'security'],
                'experience_level': 0.9,
                'workload': 0.3,
                'availability': True,
                'specialties': ['代码质量', '安全审查', '测试覆盖'],
                'performance_score': 0.88
            },
            'bob_wang': {
                'expertise': ['java', 'architecture', 'performance'],
                'experience_level': 0.85,
                'workload': 0.5,
                'availability': True,
                'specialties': ['系统架构', '性能优化', 'Java开发'],
                'performance_score': 0.82
            },
            'carol_liu': {
                'expertise': ['frontend', 'ui_ux', 'accessibility'],
                'experience_level': 0.8,
                'workload': 0.4,
                'availability': True,
                'specialties': ['前端开发', '用户体验', '无障碍设计'],
                'performance_score': 0.85
            },
            'david_zhang': {
                'expertise': ['devops', 'security', 'cloud'],
                'experience_level': 0.9,
                'workload': 0.6,
                'availability': True,
                'specialties': ['DevOps', '云安全', '基础设施'],
                'performance_score': 0.87
            },
            'emma_wang': {
                'expertise': ['python', 'ml', 'data_science'],
                'experience_level': 0.75,
                'workload': 0.2,
                'availability': True,
                'specialties': ['机器学习', '数据分析', 'Python'],
                'performance_score': 0.79
            }
        }
        
        # Add reviewers to allocator
        for reviewer_id, reviewer_data in demo_reviewers.items():
            self.allocator.add_reviewer(reviewer_id, reviewer_data)
        
        logger.info(f"Added {len(demo_reviewers)} demo reviewers")
        
        # Create demo assessment criteria
        demo_criteria = {
            'code_review': {
                'code_quality': {'weight': 0.3, 'description': '代码质量评分'},
                'security': {'weight': 0.25, 'description': '安全性评估'},
                'performance': {'weight': 0.2, 'description': '性能考量'},
                'maintainability': {'weight': 0.15, 'description': '可维护性'},
                'testing': {'weight': 0.1, 'description': '测试覆盖'}
            },
            'document_review': {
                'clarity': {'weight': 0.3, 'description': '清晰度'},
                'completeness': {'weight': 0.25, 'description': '完整性'},
                'accuracy': {'weight': 0.25, 'description': '准确性'},
                'structure': {'weight': 0.2, 'description': '结构合理性'}
            },
            'design_review': {
                'ux_quality': {'weight': 0.3, 'description': '用户体验'},
                'visual_design': {'weight': 0.25, 'description': '视觉设计'},
                'accessibility': {'weight': 0.2, 'description': '无障碍设计'},
                'consistency': {'weight': 0.15, 'description': '一致性'},
                'innovation': {'weight': 0.1, 'description': '创新性'}
            }
        }
        
        # Add criteria to assessment engine
        for content_type, criteria in demo_criteria.items():
            self.assessment_engine.add_criteria(content_type, criteria)
        
        logger.info(f"Added criteria for {len(demo_criteria)} content types")
        
    def _setup_app(self):
        """Setup FastAPI application"""
        
        # Mount static files
        self.app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
        
        # Setup templates
        self.templates = Jinja2Templates(directory="templates")
        
        # Include V0.3.5 API routes
        self.app.include_router(v0_3_5_router)
        
        # Add demo-specific routes
        @self.app.get("/", response_class=HTMLResponse)
        async def demo_homepage(request: Request):
            """Demo homepage"""
            return self.templates.TemplateResponse(
                "v0_3_5_critical_review_ui.html",
                {"request": request}
            )
        
        @self.app.get("/demo/status", response_model=Dict[str, Any])
        async def demo_status():
            """Get demo system status"""
            return {
                "demo_system": "V0.3.5 Critical Review Workflow",
                "status": "running",
                "components": {
                    "smart_reviewer_allocator": "active",
                    "multidimensional_assessment_engine": "active",
                    "collaborative_review_environment": "active",
                    "conflict_resolution_system": "active",
                    "review_analytics": "active",
                    "automated_report_generator": "active"
                },
                "demo_data": {
                    "reviewers_count": len(self.allocator.reviewer_pool),
                    "criteria_count": len(self.assessment_engine.assessment_criteria),
                    "active_sessions": len(self.review_environment.active_sessions)
                },
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/demo/reset")
        async def reset_demo():
            """Reset demo data"""
            try:
                # Reset components
                self.allocator.reviewer_pool.clear()
                self.review_environment.active_sessions.clear()
                self.conflict_resolver.active_conflicts.clear()
                self.review_analytics.metrics_history.clear()
                
                # Re-setup demo data
                self._setup_demo_data()
                
                return {
                    "success": True,
                    "message": "Demo system reset successfully",
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.app.post("/demo/simulate-workflow")
        async def simulate_workflow():
            """Simulate a complete workflow"""
            try:
                workflow_result = await self._simulate_complete_workflow()
                return workflow_result
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        @self.app.get("/demo/metrics", response_model=Dict[str, Any])
        async def get_demo_metrics():
            """Get demo metrics and analytics"""
            try:
                # Get system stats
                allocator_stats = self.allocator.get_pool_stats()
                analytics_stats = await self.review_analytics.get_system_stats()
                conflict_stats = await self.conflict_resolver.get_system_stats()
                
                return {
                    "allocator_stats": allocator_stats,
                    "analytics_stats": analytics_stats,
                    "conflict_stats": conflict_stats,
                    "demo_summary": {
                        "total_reviewers": len(self.allocator.reviewer_pool),
                        "active_sessions": len(self.review_environment.active_sessions),
                        "resolved_conflicts": len(self.conflict_resolver.resolved_conflicts),
                        "metrics_recorded": len(self.review_analytics.metrics_history),
                        "reports_generated": len(self.report_generator.reports_history)
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Startup and shutdown events
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize demo system"""
            logger.info("Starting V0.3.5 Demo System...")
            
            # Start all components
            await self.conflict_resolver.start()
            await self.review_analytics.start()
            await self.report_generator.start()
            
            logger.info("V0.3.5 Demo System started successfully")
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Shutdown demo system"""
            logger.info("Shutting down V0.3.5 Demo System...")
            
            # Stop all components
            await self.conflict_resolver.stop()
            await self.review_analytics.stop()
            await self.report_generator.stop()
            
            logger.info("V0.3.5 Demo System shutdown completed")
    
    async def _simulate_complete_workflow(self) -> Dict[str, Any]:
        """Simulate a complete critical review workflow"""
        workflow_id = f"demo_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting workflow simulation: {workflow_id}")
        
        # Step 1: Select reviewers for code review
        logger.info("Step 1: Selecting reviewers...")
        reviewer_selection = await self.allocator.select_reviewers(
            content_type="code_review",
            content_tags=["python", "security", "testing"],
            required_count=3
        )
        
        if not reviewer_selection['success']:
            raise Exception(f"Reviewer selection failed: {reviewer_selection['error']}")
        
        selected_reviewers = reviewer_selection['selected_reviewers']
        logger.info(f"Selected reviewers: {selected_reviewers}")
        
        # Step 2: Create collaborative review session
        logger.info("Step 2: Creating review session...")
        session_creation = await self.review_environment.create_session(
            session_name=f"Demo Code Review - {workflow_id}",
            participants=selected_reviewers,
            content_type="code_review",
            initial_content="""
def authenticate_user(username, password):
    # Demo code for review
    if username == "admin" and password == "admin123":
        return True
    return False

def get_user_data(user_id):
    # Get user from database
    query = "SELECT * FROM users WHERE id = ?"
    return execute_query(query, (user_id,))
            """
        )
        
        if not session_creation['success']:
            raise Exception(f"Session creation failed: {session_creation['error']}")
        
        session_id = session_creation['session_id']
        logger.info(f"Created session: {session_id}")
        
        # Step 3: Perform multidimensional assessments
        logger.info("Step 3: Performing assessments...")
        assessment_tasks = []
        demo_content = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def validate_input(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary")
    return True
        """
        
        for reviewer_id in selected_reviewers:
            task = self.assessment_engine.assess_content(
                content=demo_content,
                content_type="code_review",
                assessor_id=reviewer_id,
                context={'session_id': session_id, 'workflow_id': workflow_id}
            )
            assessment_tasks.append(task)
        
        # Run assessments in parallel
        assessment_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)
        
        successful_assessments = []
        for i, result in enumerate(assessment_results):
            if isinstance(result, Exception):
                logger.error(f"Assessment {i} failed: {result}")
            elif result.get('success'):
                successful_assessments.append(result)
                # Record metrics
                from src.core_services.review_analytics import ReviewMetric, MetricType, AnalysisScope
                
                metric = ReviewMetric(
                    metric_id=f"assessment_{result['assessment_id']}",
                    metric_type=MetricType.QUALITY,
                    name="demo_assessment_score",
                    value=result['overall_score'],
                    scope=AnalysisScope.SESSION,
                    timestamp=datetime.now(),
                    context={
                        'assessor_id': selected_reviewers[i],
                        'session_id': session_id,
                        'workflow_id': workflow_id
                    }
                )
                await self.review_analytics.record_metric(metric)
        
        logger.info(f"Completed {len(successful_assessments)} assessments")
        
        # Step 4: Simulate collaborative discussion
        logger.info("Step 4: Simulating collaborative discussion...")
        demo_comments = [
            {
                'user_id': selected_reviewers[0],
                'content': '代码整体质量不错，但建议添加输入验证'
            },
            {
                'user_id': selected_reviewers[1],
                'content': '同意，另外建议添加错误处理机制'
            },
            {
                'user_id': selected_reviewers[2],
                'content': '函数命名很清晰，建议添加类型注释'
            }
        ]
        
        for comment_data in demo_comments:
            comment_result = await self.review_environment.add_comment(
                session_id=session_id,
                user_id=comment_data['user_id'],
                content=comment_data['content']
            )
            
            if comment_result['success']:
                # Record participation metric
                from src.core_services.review_analytics import ReviewMetric, MetricType, AnalysisScope
                
                metric = ReviewMetric(
                    metric_id=f"comment_{comment_result['comment_id']}",
                    metric_type=MetricType.PARTICIPATION,
                    name="demo_comment_added",
                    value=1.0,
                    scope=AnalysisScope.SESSION,
                    timestamp=datetime.now(),
                    context={
                        'user_id': comment_data['user_id'],
                        'session_id': session_id,
                        'workflow_id': workflow_id
                    }
                )
                await self.review_analytics.record_metric(metric)
        
        logger.info("Added demo comments")
        
        # Step 5: Simulate conflict and resolution
        logger.info("Step 5: Simulating conflict resolution...")
        conflict_operations = [
            {
                'resource_id': f'code_{session_id}',
                'user_id': selected_reviewers[0],
                'timestamp': datetime.now(),
                'type': 'edit',
                'content': '建议使用更安全的认证方式'
            },
            {
                'resource_id': f'code_{session_id}',
                'user_id': selected_reviewers[1],
                'timestamp': datetime.now(),
                'type': 'edit',
                'content': '当前认证方式足够安全'
            }
        ]
        
        detected_conflict = await self.conflict_resolver.detect_conflict(conflict_operations)
        if detected_conflict:
            conflict_id = await self.conflict_resolver.submit_conflict(detected_conflict)
            resolution_result = await self.conflict_resolver.resolve_conflict(conflict_id)
            
            logger.info(f"Conflict {conflict_id} resolved: {resolution_result.success}")
        
        # Step 6: Generate analytics insights
        logger.info("Step 6: Generating analytics insights...")
        insights = await self.review_analytics.generate_insights(
            self.review_analytics.AnalysisScope.SESSION,
            session_id
        )
        
        logger.info(f"Generated {len(insights)} insights")
        
        # Step 7: Generate final report
        logger.info("Step 7: Generating final report...")
        from src.core_services.automated_report_generator import ReportRequest, ReportType, ReportFormat
        
        report_request = ReportRequest(
            request_id=f"report_{workflow_id}",
            report_type=ReportType.SESSION_SUMMARY,
            report_format=ReportFormat.HTML,
            template_id=None,
            data_sources={
                "session_data": {
                    "session_id": session_id,
                    "workflow_id": workflow_id,
                    "participants": selected_reviewers,
                    "assessments": successful_assessments,
                    "insights": [insight.to_dict() for insight in insights],
                    "comments_count": len(demo_comments),
                    "conflicts_resolved": 1 if detected_conflict else 0
                }
            },
            parameters={},
            requested_by="demo_system",
            requested_at=datetime.now()
        )
        
        report_id = await self.report_generator.generate_report(report_request)
        
        # Wait for report generation (simplified for demo)
        await asyncio.sleep(2)
        
        logger.info(f"Workflow simulation completed: {workflow_id}")
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "session_id": session_id,
            "summary": {
                "reviewers_selected": len(selected_reviewers),
                "assessments_completed": len(successful_assessments),
                "comments_added": len(demo_comments),
                "conflicts_resolved": 1 if detected_conflict else 0,
                "insights_generated": len(insights),
                "report_generated": report_id
            },
            "next_steps": [
                f"View session: /sessions/{session_id}",
                f"View report: /reports/status/{report_id}",
                "Continue monitoring analytics"
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Run the demo system"""
        logger.info(f"Starting V0.3.5 Demo System on {host}:{port}")
        logger.info("Open http://localhost:8000 in your browser to access the demo")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            log_level="info"
        )


def main():
    """Main entry point for demo system"""
    demo_system = V0_3_5_DemoSystem()
    demo_system.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()