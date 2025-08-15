"""@Time: 2025-08-03
@Author: Claude Code
@File: test_v0_3_5_critical_review.py
@Description: Comprehensive test suite for V0.3.5 Critical Review Workflow components
"""

import asyncio

# Import the components to test
import sys
from datetime import datetime

import pytest

sys.path.append('.')

from src.core_services.automated_report_generator import (
    AutomatedReportGenerator,
    ReportFormat,
    ReportRequest,
    ReportType,
)
from src.core_services.collaborative_review_environment import CollaborativeReviewEnvironment
from src.core_services.conflict_resolution_system import Conflict, ConflictResolutionSystem, ConflictType
from src.core_services.multidimensional_assessment_engine import MultidimensionalAssessmentEngine
from src.core_services.review_analytics import MetricType, ReviewAnalytics, ReviewMetric
from src.core_services.smart_reviewer_allocator import SmartReviewerAllocator


class TestSmartReviewerAllocator:
    """Test suite for SmartReviewerAllocator"""
    
    @pytest.fixture()
    def allocator(self):
        return SmartReviewerAllocator()
    
    @pytest.mark.asyncio()
    async def test_allocator_initialization(self, allocator):
        """Test allocator initialization"""
        assert allocator is not None
        assert hasattr(allocator, 'reviewer_pool')
        assert hasattr(allocator, 'allocation_history')
    
    @pytest.mark.asyncio()
    async def test_select_reviewers_basic(self, allocator):
        """Test basic reviewer selection"""
        # Mock reviewer pool
        allocator.reviewer_pool = {
            'reviewer1': {
                'expertise': ['python', 'testing'],
                'workload': 0.5,
                'availability': True
            },
            'reviewer2': {
                'expertise': ['python', 'security'],
                'workload': 0.3,
                'availability': True
            }
        }
        
        result = await allocator.select_reviewers(
            content_type='code_review',
            content_tags=['python'],
            required_count=1
        )
        
        assert result['success'] is True
        assert len(result['selected_reviewers']) == 1
        assert 'allocation_id' in result
    
    @pytest.mark.asyncio()
    async def test_select_reviewers_no_available(self, allocator):
        """Test reviewer selection when no reviewers available"""
        allocator.reviewer_pool = {}
        
        result = await allocator.select_reviewers(
            content_type='code_review',
            content_tags=['python'],
            required_count=1
        )
        
        assert result['success'] is False
        assert 'No available reviewers' in result['error']
    
    @pytest.mark.asyncio()
    async def test_calculate_match_score(self, allocator):
        """Test match score calculation"""
        reviewer = {
            'expertise': ['python', 'testing'],
            'experience_level': 0.8,
            'workload': 0.3
        }
        
        score = allocator._calculate_match_score(
            reviewer, 
            ['python', 'testing'], 
            'code_review'
        )
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be a good match


class TestMultidimensionalAssessmentEngine:
    """Test suite for MultidimensionalAssessmentEngine"""
    
    @pytest.fixture()
    def engine(self):
        return MultidimensionalAssessmentEngine()
    
    @pytest.mark.asyncio()
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert hasattr(engine, 'assessment_criteria')
        assert hasattr(engine, 'weight_configs')
    
    @pytest.mark.asyncio()
    async def test_assess_content_basic(self, engine):
        """Test basic content assessment"""
        result = await engine.assess_content(
            content="Test code content",
            content_type="code_review",
            assessor_id="test_assessor"
        )
        
        assert result['success'] is True
        assert 'assessment_id' in result
        assert 'overall_score' in result
        assert 'dimension_scores' in result
        assert 0 <= result['overall_score'] <= 1
    
    @pytest.mark.asyncio()
    async def test_assess_content_invalid_type(self, engine):
        """Test assessment with invalid content type"""
        result = await engine.assess_content(
            content="Test content",
            content_type="invalid_type",
            assessor_id="test_assessor"
        )
        
        assert result['success'] is False
        assert 'Unsupported content type' in result['error']
    
    @pytest.mark.asyncio()
    async def test_batch_assessment(self, engine):
        """Test batch assessment"""
        requests = [
            {
                'content': f'Test content {i}',
                'content_type': 'code_review',
                'assessor_id': f'assessor_{i}'
            }
            for i in range(3)
        ]
        
        results = await engine.batch_assess(requests)
        
        assert len(results) == 3
        for result in results:
            assert result['success'] is True
            assert 'assessment_id' in result


class TestCollaborativeReviewEnvironment:
    """Test suite for CollaborativeReviewEnvironment"""
    
    @pytest.fixture()
    def environment(self):
        return CollaborativeReviewEnvironment()
    
    @pytest.mark.asyncio()
    async def test_environment_initialization(self, environment):
        """Test environment initialization"""
        assert environment is not None
        assert hasattr(environment, 'active_sessions')
        assert hasattr(environment, 'event_handlers')
    
    @pytest.mark.asyncio()
    async def test_create_session(self, environment):
        """Test session creation"""
        result = await environment.create_session(
            session_name="Test Session",
            participants=["user1", "user2"],
            content_type="code_review"
        )
        
        assert result['success'] is True
        assert 'session_id' in result
        assert result['session_name'] == "Test Session"
    
    @pytest.mark.asyncio()
    async def test_join_session(self, environment):
        """Test joining a session"""
        # First create a session
        create_result = await environment.create_session(
            session_name="Test Session",
            participants=["user1"],
            content_type="code_review"
        )
        session_id = create_result['session_id']
        
        # Join session
        join_result = await environment.join_session(
            session_id=session_id,
            user_id="user2"
        )
        
        assert join_result['success'] is True
        assert join_result['user_id'] == "user2"
    
    @pytest.mark.asyncio()
    async def test_add_comment(self, environment):
        """Test adding comments"""
        # Create session
        create_result = await environment.create_session(
            session_name="Test Session",
            participants=["user1"],
            content_type="code_review"
        )
        session_id = create_result['session_id']
        
        # Add comment
        comment_result = await environment.add_comment(
            session_id=session_id,
            user_id="user1",
            content="Test comment"
        )
        
        assert comment_result['success'] is True
        assert 'comment_id' in result
        assert comment_result['content'] == "Test comment"


class TestConflictResolutionSystem:
    """Test suite for ConflictResolutionSystem"""
    
    @pytest.fixture()
    def resolver(self):
        return ConflictResolutionSystem()
    
    @pytest.mark.asyncio()
    async def test_resolver_initialization(self, resolver):
        """Test resolver initialization"""
        assert resolver is not None
        assert hasattr(resolver, 'active_conflicts')
        assert hasattr(resolver, 'resolved_conflicts')
    
    @pytest.mark.asyncio()
    async def test_detect_concurrent_edit_conflict(self, resolver):
        """Test concurrent edit conflict detection"""
        operations = [
            {
                'resource_id': 'file1.py',
                'user_id': 'user1',
                'timestamp': datetime.now(),
                'type': 'edit'
            },
            {
                'resource_id': 'file1.py',
                'user_id': 'user2',
                'timestamp': datetime.now(),
                'type': 'edit'
            }
        ]
        
        conflict = await resolver.detect_conflict(operations)
        
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.CONCURRENT_EDIT
        assert len(conflict.user_ids) == 2
    
    @pytest.mark.asyncio()
    async def test_submit_conflict(self, resolver):
        """Test conflict submission"""
        conflict = Conflict(
            conflict_id="test_conflict",
            conflict_type=ConflictType.CONCURRENT_EDIT,
            priority=resolver.ConflictPriority.HIGH,
            affected_resources=["file1.py"],
            conflicting_operations=[],
            timestamp=datetime.now(),
            user_ids={"user1", "user2"}
        )
        
        conflict_id = await resolver.submit_conflict(conflict)
        
        assert conflict_id == "test_conflict"
        assert conflict_id in resolver.active_conflicts
    
    @pytest.mark.asyncio()
    async def test_resolve_conflict(self, resolver):
        """Test conflict resolution"""
        # Create and submit conflict
        conflict = Conflict(
            conflict_id="test_conflict",
            conflict_type=ConflictType.CONCURRENT_EDIT,
            priority=resolver.ConflictPriority.HIGH,
            affected_resources=["file1.py"],
            conflicting_operations=[
                {'user_id': 'user1', 'timestamp': datetime.now()},
                {'user_id': 'user2', 'timestamp': datetime.now()}
            ],
            timestamp=datetime.now(),
            user_ids={"user1", "user2"}
        )
        
        await resolver.submit_conflict(conflict)
        
        # Resolve conflict
        result = await resolver.resolve_conflict("test_conflict")
        
        assert result.success is True
        assert result.conflict_id == "test_conflict"
        assert result.resolution_strategy is not None


class TestReviewAnalytics:
    """Test suite for ReviewAnalytics"""
    
    @pytest.fixture()
    def analytics(self):
        return ReviewAnalytics()
    
    @pytest.mark.asyncio()
    async def test_analytics_initialization(self, analytics):
        """Test analytics initialization"""
        assert analytics is not None
        assert hasattr(analytics, 'metrics_history')
        assert hasattr(analytics, 'insights_history')
    
    @pytest.mark.asyncio()
    async def test_record_metric(self, analytics):
        """Test metric recording"""
        metric = ReviewMetric(
            metric_id="test_metric",
            metric_type=MetricType.PARTICIPATION,
            name="test_participation",
            value=0.8,
            scope=analytics.AnalysisScope.SESSION,
            timestamp=datetime.now()
        )
        
        metric_id = await analytics.record_metric(metric)
        
        assert metric_id == "test_metric"
        assert len(analytics.metrics_history) == 1
    
    @pytest.mark.asyncio()
    async def test_calculate_session_metrics(self, analytics):
        """Test session metrics calculation"""
        metrics = await analytics.calculate_session_metrics("test_session")
        
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        for metric in metrics:
            assert hasattr(metric, 'metric_id')
            assert hasattr(metric, 'value')
            assert 0 <= metric.value <= 1
    
    @pytest.mark.asyncio()
    async def test_generate_insights(self, analytics):
        """Test insight generation"""
        # Record some metrics first
        metric = ReviewMetric(
            metric_id="low_participation",
            metric_type=MetricType.PARTICIPATION,
            name="participation_rate",
            value=0.3,  # Low value to trigger insight
            scope=analytics.AnalysisScope.SESSION,
            timestamp=datetime.now(),
            threshold=0.7
        )
        
        await analytics.record_metric(metric)
        
        insights = await analytics.generate_insights(
            analytics.AnalysisScope.SESSION,
            "test_session"
        )
        
        assert isinstance(insights, list)
        # Should generate insight for low participation
        assert len(insights) > 0


class TestAutomatedReportGenerator:
    """Test suite for AutomatedReportGenerator"""
    
    @pytest.fixture()
    def generator(self, tmp_path):
        return AutomatedReportGenerator(output_dir=str(tmp_path))
    
    @pytest.mark.asyncio()
    async def test_generator_initialization(self, generator):
        """Test generator initialization"""
        assert generator is not None
        assert hasattr(generator, 'templates')
        assert hasattr(generator, 'active_requests')
        assert len(generator.templates) > 0  # Should have default templates
    
    @pytest.mark.asyncio()
    async def test_generate_html_report(self, generator):
        """Test HTML report generation"""
        request = ReportRequest(
            request_id="test_request",
            report_type=ReportType.SESSION_SUMMARY,
            report_format=ReportFormat.HTML,
            template_id=None,
            data_sources={
                "session_data": {
                    "session_id": "test_session",
                    "participants": 5,
                    "duration": 3600
                }
            },
            parameters={},
            requested_by="test_user",
            requested_at=datetime.now()
        )
        
        request_id = await generator.generate_report(request)
        
        assert request_id == "test_request"
        assert request_id in generator.active_requests
        
        # Wait for processing (in real test, would need to wait for worker)
        await asyncio.sleep(0.1)
    
    @pytest.mark.asyncio()
    async def test_create_template(self, generator):
        """Test template creation"""
        from src.core_services.automated_report_generator import ReportTemplate
        
        template = ReportTemplate(
            template_id="custom_template",
            name="Custom Template",
            description="Test template",
            template_type=ReportType.SESSION_SUMMARY,
            template_format=ReportFormat.HTML,
            template_content="<html><body>{{ data }}</body></html>",
            required_data=["data"],
            created_at=datetime.now()
        )
        
        template_id = await generator.create_template(template)
        
        assert template_id == "custom_template"
        assert template_id in generator.templates


class TestV0_3_5Integration:
    """Integration tests for V0.3.5 components"""
    
    @pytest.mark.asyncio()
    async def test_full_workflow_integration(self):
        """Test complete workflow integration"""
        # Initialize all components
        allocator = SmartReviewerAllocator()
        engine = MultidimensionalAssessmentEngine()
        environment = CollaborativeReviewEnvironment()
        resolver = ConflictResolutionSystem()
        analytics = ReviewAnalytics()
        generator = AutomatedReportGenerator()
        
        # Start components
        await resolver.start()
        await analytics.start()
        await generator.start()
        
        try:
            # Step 1: Select reviewers
            allocator.reviewer_pool = {
                'reviewer1': {
                    'expertise': ['python', 'testing'],
                    'workload': 0.5,
                    'availability': True
                }
            }
            
            selection_result = await allocator.select_reviewers(
                content_type='code_review',
                content_tags=['python'],
                required_count=1
            )
            
            assert selection_result['success'] is True
            
            # Step 2: Create review session
            session_result = await environment.create_session(
                session_name="Integration Test Session",
                participants=selection_result['selected_reviewers'],
                content_type="code_review"
            )
            
            assert session_result['success'] is True
            
            # Step 3: Assess content
            assessment_result = await engine.assess_content(
                content="def test_function():\n    return True",
                content_type="code_review",
                assessor_id=selection_result['selected_reviewers'][0]
            )
            
            assert assessment_result['success'] is True
            
            # Step 4: Record metrics
            from src.core_services.review_analytics import MetricType, ReviewMetric
            
            metric = ReviewMetric(
                metric_id="integration_test_metric",
                metric_type=MetricType.QUALITY,
                name="integration_quality_score",
                value=assessment_result['overall_score'],
                scope=analytics.AnalysisScope.SESSION,
                timestamp=datetime.now()
            )
            
            await analytics.record_metric(metric)
            
            # Step 5: Generate insights
            insights = await analytics.generate_insights(
                analytics.AnalysisScope.SESSION,
                session_result['session_id']
            )
            
            assert isinstance(insights, list)
            
            # Step 6: Generate report
            from src.core_services.automated_report_generator import ReportFormat, ReportRequest, ReportType
            
            report_request = ReportRequest(
                request_id="integration_test_report",
                report_type=ReportType.SESSION_SUMMARY,
                report_format=ReportFormat.HTML,
                template_id=None,
                data_sources={
                    "session_data": {
                        "session_id": session_result['session_id'],
                        "assessment": assessment_result,
                        "insights": [i.to_dict() for i in insights]
                    }
                },
                parameters={},
                requested_by="integration_test",
                requested_at=datetime.now()
            )
            
            report_id = await generator.generate_report(report_request)
            
            assert report_id == "integration_test_report"
            
        finally:
            # Cleanup
            await resolver.stop()
            await analytics.stop()
            await generator.stop()
    
    @pytest.mark.asyncio()
    async def test_error_handling_and_graceful_degradation(self):
        """Test error handling and graceful degradation"""
        # Test with failing components
        allocator = SmartReviewerAllocator()
        
        # Test with empty reviewer pool
        result = await allocator.select_reviewers(
            content_type='invalid_type',
            content_tags=[],
            required_count=1
        )
        
        assert result['success'] is False
        assert 'error' in result
        
        # Test assessment engine with invalid input
        engine = MultidimensionalAssessmentEngine()
        result = await engine.assess_content(
            content="",
            content_type="invalid_type",
            assessor_id=""
        )
        
        assert result['success'] is False
        assert 'error' in result


@pytest.mark.asyncio()
async def test_performance_benchmarks():
    """Performance benchmark tests"""
    import time
    
    # Test reviewer selection performance
    allocator = SmartReviewerAllocator()
    
    # Setup large reviewer pool
    allocator.reviewer_pool = {
        f'reviewer_{i}': {
            'expertise': ['python', 'testing', 'security'],
            'workload': 0.1 + (i % 10) * 0.1,
            'availability': True
        }
        for i in range(1000)
    }
    
    start_time = time.time()
    result = await allocator.select_reviewers(
        content_type='code_review',
        content_tags=['python'],
        required_count=5
    )
    end_time = time.time()
    
    assert result['success'] is True
    assert (end_time - start_time) < 1.0  # Should complete within 1 second


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])