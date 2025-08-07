#!/usr/bin/env python3
"""
@Time: 2025-08-03
@Author: Claude Code
@File: run_v0_3_5_tests.py
@Description: Run V0.3.5 Critical Review Workflow tests
"""

import asyncio
import sys
import logging
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def run_unit_tests():
    """Run unit tests for V0.3.5 components"""
    logger.info("=== Running V0.3.5 Unit Tests ===")
    
    try:
        import pytest
        
        # Run unit tests
        test_result = pytest.main([
            'tests/test_v0_3_5_critical_review.py',
            '-v',
            '--tb=short',
            '--maxfail=5'
        ])
        
        if test_result == 0:
            logger.info("✅ All unit tests passed!")
            return True
        else:
            logger.warning(f"⚠️ Some unit tests failed (exit code: {test_result})")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unit test execution failed: {e}")
        traceback.print_exc()
        return False

async def run_integration_tests():
    """Run integration tests for V0.3.5 workflow"""
    logger.info("=== Running V0.3.5 Integration Tests ===")
    
    try:
        # Import components
        from src.core_services.smart_reviewer_allocator import SmartReviewerAllocator
        from src.core_services.multidimensional_assessment_engine import MultidimensionalAssessmentEngine
        from src.core_services.collaborative_review_environment import CollaborativeReviewEnvironment
        from src.core_services.conflict_resolution_system import ConflictResolutionSystem
        from src.core_services.review_analytics import ReviewAnalytics
        from src.core_services.automated_report_generator import AutomatedReportGenerator
        
        # Initialize components
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
        
        test_results = []
        
        # Test 1: Reviewer Selection
        logger.info("Test 1: Reviewer Selection")
        try:
            # Add test reviewers
            test_reviewers = {
                'test_reviewer_1': {
                    'expertise': ['python', 'testing'],
                    'workload': 0.3,
                    'availability': True
                },
                'test_reviewer_2': {
                    'expertise': ['python', 'security'],
                    'workload': 0.5,
                    'availability': True
                }
            }
            
            for reviewer_id, data in test_reviewers.items():
                allocator.add_reviewer(reviewer_id, data)
            
            result = await allocator.select_reviewers(
                content_type='code_review',
                content_tags=['python'],
                required_count=1
            )
            
            if result['success'] and len(result['selected_reviewers']) > 0:
                logger.info("✅ Reviewer selection test passed")
                test_results.append(True)
            else:
                logger.error(f"❌ Reviewer selection test failed: {result}")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Reviewer selection test error: {e}")
            test_results.append(False)
        
        # Test 2: Content Assessment
        logger.info("Test 2: Content Assessment")
        try:
            result = await engine.assess_content(
                content="def test_function():\n    return True",
                content_type="code_review",
                assessor_id="test_reviewer_1"
            )
            
            if result['success'] and 'overall_score' in result:
                logger.info("✅ Content assessment test passed")
                test_results.append(True)
            else:
                logger.error(f"❌ Content assessment test failed: {result}")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Content assessment test error: {e}")
            test_results.append(False)
        
        # Test 3: Session Management
        logger.info("Test 3: Session Management")
        try:
            result = await environment.create_session(
                session_name="Test Session",
                participants=["test_user_1", "test_user_2"],
                content_type="code_review"
            )
            
            if result['success'] and 'session_id' in result:
                logger.info("✅ Session management test passed")
                test_results.append(True)
            else:
                logger.error(f"❌ Session management test failed: {result}")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Session management test error: {e}")
            test_results.append(False)
        
        # Test 4: Conflict Detection
        logger.info("Test 4: Conflict Detection")
        try:
            operations = [
                {
                    'resource_id': 'test_file.py',
                    'user_id': 'user1',
                    'timestamp': datetime.now(),
                    'type': 'edit'
                },
                {
                    'resource_id': 'test_file.py',
                    'user_id': 'user2',
                    'timestamp': datetime.now(),
                    'type': 'edit'
                }
            ]
            
            conflict = await resolver.detect_conflict(operations)
            
            if conflict:
                logger.info("✅ Conflict detection test passed")
                test_results.append(True)
            else:
                logger.error("❌ Conflict detection test failed: No conflict detected")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Conflict detection test error: {e}")
            test_results.append(False)
        
        # Test 5: Analytics Recording
        logger.info("Test 5: Analytics Recording")
        try:
            from src.core_services.review_analytics import ReviewMetric, MetricType, AnalysisScope
            
            metric = ReviewMetric(
                metric_id="test_metric",
                metric_type=MetricType.QUALITY,
                name="test_quality_score",
                value=0.85,
                scope=AnalysisScope.SESSION,
                timestamp=datetime.now()
            )
            
            metric_id = await analytics.record_metric(metric)
            
            if metric_id == "test_metric":
                logger.info("✅ Analytics recording test passed")
                test_results.append(True)
            else:
                logger.error(f"❌ Analytics recording test failed: {metric_id}")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Analytics recording test error: {e}")
            test_results.append(False)
        
        # Test 6: Report Generation
        logger.info("Test 6: Report Generation")
        try:
            from src.core_services.automated_report_generator import ReportRequest, ReportType, ReportFormat
            
            request = ReportRequest(
                request_id="test_report",
                report_type=ReportType.SESSION_SUMMARY,
                report_format=ReportFormat.HTML,
                template_id=None,
                data_sources={
                    "test_data": {"message": "Test data"}
                },
                parameters={},
                requested_by="test_user",
                requested_at=datetime.now()
            )
            
            request_id = await generator.generate_report(request)
            
            if request_id == "test_report":
                logger.info("✅ Report generation test passed")
                test_results.append(True)
            else:
                logger.error(f"❌ Report generation test failed: {request_id}")
                test_results.append(False)
                
        except Exception as e:
            logger.error(f"❌ Report generation test error: {e}")
            test_results.append(False)
        
        # Cleanup
        await resolver.stop()
        await analytics.stop()
        await generator.stop()
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        logger.info(f"=== Integration Tests Summary ===")
        logger.info(f"Passed: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            logger.info("✅ All integration tests passed!")
            return True
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} integration tests failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test execution failed: {e}")
        traceback.print_exc()
        return False

async def run_workflow_test():
    """Run complete workflow test"""
    logger.info("=== Running V0.3.5 Complete Workflow Test ===")
    
    try:
        # Import demo system
        from v0_3_5_demo_system import V0_3_5_DemoSystem
        
        # Create demo system
        demo_system = V0_3_5_DemoSystem()
        
        # Simulate workflow
        workflow_result = await demo_system._simulate_complete_workflow()
        
        if workflow_result['success']:
            logger.info("✅ Complete workflow test passed!")
            logger.info(f"Workflow ID: {workflow_result['workflow_id']}")
            logger.info(f"Session ID: {workflow_result['session_id']}")
            logger.info(f"Summary: {workflow_result['summary']}")
            return True
        else:
            logger.error(f"❌ Complete workflow test failed: {workflow_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Complete workflow test error: {e}")
        traceback.print_exc()
        return False

async def run_performance_tests():
    """Run performance benchmarks"""
    logger.info("=== Running V0.3.5 Performance Tests ===")
    
    try:
        import time
        from src.core_services.smart_reviewer_allocator import SmartReviewerAllocator
        
        # Test reviewer selection performance
        allocator = SmartReviewerAllocator()
        
        # Create large reviewer pool
        logger.info("Creating large reviewer pool...")
        for i in range(1000):
            reviewer_data = {
                'expertise': ['python', 'testing', 'security'],
                'workload': 0.1 + (i % 10) * 0.1,
                'availability': True
            }
            allocator.add_reviewer(f'reviewer_{i}', reviewer_data)
        
        # Benchmark selection
        logger.info("Benchmarking reviewer selection...")
        start_time = time.time()
        
        for _ in range(100):
            result = await allocator.select_reviewers(
                content_type='code_review',
                content_tags=['python'],
                required_count=5
            )
            
            if not result['success']:
                raise Exception(f"Selection failed: {result['error']}")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        logger.info(f"Average selection time: {avg_time:.4f} seconds")
        
        if avg_time < 1.0:  # Should be under 1 second
            logger.info("✅ Performance test passed!")
            return True
        else:
            logger.warning(f"⚠️ Performance test warning: Average time {avg_time:.4f}s > 1.0s")
            return False
            
    except Exception as e:
        logger.error(f"❌ Performance test error: {e}")
        traceback.print_exc()
        return False

async def main():
    """Main test runner"""
    logger.info("🚀 Starting V0.3.5 Critical Review Workflow Test Suite")
    logger.info("=" * 60)
    
    test_results = []
    
    # Run all test suites
    test_results.append(("Unit Tests", await run_unit_tests()))
    test_results.append(("Integration Tests", await run_integration_tests()))
    test_results.append(("Workflow Test", await run_workflow_test()))
    test_results.append(("Performance Tests", await run_performance_tests()))
    
    # Summary
    logger.info("=" * 60)
    logger.info("📊 Test Results Summary:")
    logger.info("=" * 60)
    
    passed_count = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:20} {status}")
        if result:
            passed_count += 1
    
    logger.info("=" * 60)
    logger.info(f"Overall: {passed_count}/{len(test_results)} test suites passed")
    
    if passed_count == len(test_results):
        logger.info("🎉 All tests passed! V0.3.5 is ready for production!")
        return 0
    else:
        logger.warning("⚠️ Some tests failed. Please review the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)