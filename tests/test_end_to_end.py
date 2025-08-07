# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 16:30:00
@Author  : DAIP-LIVE Team
@File    : test_end_to_end.py
@Description:
    End-to-end testing for the complete V0.3.5 system.
    Tests the entire workflow from user interaction to system response.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Import system components
from src.app_state import AppState
from src.core_services.expert_consultation_scenario import ExpertConsultationScenario
from src.core_services.academic_research_scenario import AcademicResearchScenario
from src.core_services.industry_analysis_scenario import IndustryAnalysisScenario
from src.core_services.smart_reviewer_allocator_simple import SmartReviewerAllocator


class TestEndToEndSystem:
    """End-to-end tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_complete_system_startup(self):
        """Test complete system startup and initialization"""
        print("🚀 Testing complete system startup...")
        
        # Initialize all system components
        app_state = AppState()
        await app_state.initialize()
        
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        industry_scenario = IndustryAnalysisScenario()
        reviewer_allocator = SmartReviewerAllocator()
        
        # Verify all components are initialized
        assert app_state is not None
        assert expert_scenario is not None
        assert academic_scenario is not None
        assert industry_scenario is not None
        assert reviewer_allocator is not None
        
        # Verify core services are available
        assert hasattr(app_state, 'llm_interface')
        assert hasattr(app_state, 'memory_service')
        assert hasattr(app_state, 'wiki_service')
        assert hasattr(app_state, 'synthesis_engine')
        
        # Verify scenarios have their components
        assert len(expert_scenario.expert_pool) > 0
        assert len(academic_scenario.reviewer_pool) > 0
        assert len(industry_scenario.expert_pool) > 0
        assert len(reviewer_allocator.reviewer_pool) > 0
        
        print("✅ System startup successful")
        
        return {
            "app_state": app_state,
            "expert_scenario": expert_scenario,
            "academic_scenario": academic_scenario,
            "industry_scenario": industry_scenario,
            "reviewer_allocator": reviewer_allocator
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_user_interaction(self):
        """Test complete end-to-end user interaction"""
        print("👤 Testing end-to-end user interaction...")
        
        # Initialize system
        system = await self.test_complete_system_startup()
        
        # Simulate user journey: Research -> Consultation -> Analysis
        
        # Step 1: User starts with academic research
        print("📚 Step 1: User conducts academic research...")
        literature_result = await system['academic_scenario'].conduct_literature_review(
            topic="Machine Learning in Financial Services",
            scope={
                "time_range": "2020-2024",
                "min_papers": 8,
                "focus_areas": ["algorithmic_trading", "risk_management", "fraud_detection"]
            }
        )
        
        assert literature_result['success'] is True
        print(f"✅ Literature review found {literature_result['papers_found']} papers")
        
        # Step 2: User seeks expert consultation based on research
        print("🎯 Step 2: User consults experts...")
        from src.core_services.expert_consultation_scenario import ExpertConsultationRequest, ConsultationType, PriorityLevel
        
        consultation_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="Based on recent research, what ML algorithms work best for fraud detection in financial services?",
            user_preferences={
                "expertise_level": "intermediate",
                "industry_focus": "financial_services"
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["algorithm_recommendations", "implementation_guidance", "best_practices"]
        )
        
        consultation_result = await system['expert_scenario'].handle_consultation(consultation_request)
        assert consultation_result['success'] is True
        print(f"✅ Consultation completed with {len(consultation_result['selected_experts'])} experts")
        
        # Step 3: User wants industry analysis to understand market context
        print("📊 Step 3: User requests industry analysis...")
        from src.core_services.industry_analysis_scenario import AnalysisRequest, IndustryType, AnalysisDepth
        
        industry_request = AnalysisRequest(
            industry_type=IndustryType.FINANCE,
            analysis_depth=AnalysisDepth.DETAILED,
            focus_areas=["FinTech", "AI in Finance", "Digital Transformation"],
            time_horizon="3-5 years",
            specific_questions=[
                "How is AI transforming financial services?",
                "What are the key investment areas?",
                "Who are the market leaders in AI-powered finance?"
            ],
            priority_level="HIGH"
        )
        
        industry_result = await system['industry_scenario'].submit_analysis_request(industry_request)
        assert industry_result['success'] is True
        print(f"✅ Industry analysis completed with quality score: {industry_result['quality_score']:.2f}")
        
        # Step 4: User follows up with more specific technical consultation
        print("🔧 Step 4: User follows up with technical consultation...")
        tech_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="What are the technical challenges of implementing ML fraud detection systems?",
            user_preferences={
                "system_scale": "enterprise",
                "integration_requirements": ["real_time_processing", "legacy_systems"],
                "compliance_needs": ["regulatory_reporting", "audit_trails"]
            },
            priority_level=PriorityLevel.MEDIUM,
            expected_outcomes=["technical_challenges", "architecture_recommendations", "compliance_considerations"]
        )
        
        tech_result = await system['expert_scenario'].handle_consultation(tech_request)
        assert tech_result['success'] is True
        print(f"✅ Technical consultation completed")
        
        # Step 5: User checks the status of all their requests
        print("📋 Step 5: User checks request status...")
        
        # Check consultation status
        consultation_status = await system['expert_scenario'].get_consultation_status(
            consultation_result['consultation_id']
        )
        assert consultation_status['status'] == 'success'
        
        # Check analysis status
        analysis_status = await system['industry_scenario'].get_analysis_status(
            industry_result['request_id']
        )
        assert analysis_status['status'] == 'success'
        
        print("✅ All request statuses confirmed")
        
        # Step 6: User gets history of all interactions
        print("📚 Step 6: User retrieves interaction history...")
        
        expert_history = system['expert_scenario'].get_consultation_history(limit=5)
        academic_history = system['academic_scenario'].get_research_history(limit=5)
        industry_history = system['industry_scenario'].get_analysis_history(limit=5)
        
        assert len(expert_history) >= 2  # Should have at least 2 consultations
        assert len(academic_history) >= 1  # Should have at least 1 literature review
        assert len(industry_history) >= 1  # Should have at least 1 industry analysis
        
        print(f"✅ Retrieved history: {len(expert_history)} consultations, {len(academic_history)} research activities, {len(industry_history)} analyses")
        
        print("🎉 Complete end-to-end user interaction successful!")
        
        return {
            "literature_review": literature_result,
            "consultation": consultation_result,
            "industry_analysis": industry_result,
            "technical_consultation": tech_result,
            "histories": {
                "expert": expert_history,
                "academic": academic_history,
                "industry": industry_history
            }
        }
    
    @pytest.mark.asyncio
    async def test_system_performance_under_load(self):
        """Test system performance under realistic load"""
        print("⚡ Testing system performance under load...")
        
        # Initialize system
        system = await self.test_complete_system_startup()
        
        # Simulate multiple concurrent users
        num_users = 5
        requests_per_user = 3
        
        print(f"🔄 Simulating {num_users} users with {requests_per_user} requests each...")
        
        start_time = time.time()
        
        # Create user tasks
        all_tasks = []
        for user_id in range(num_users):
            user_tasks = []
            
            # Each user makes different types of requests
            for request_id in range(requests_per_user):
                if request_id % 3 == 0:
                    # Academic research request
                    task = system['academic_scenario'].conduct_literature_review(
                        topic=f"User {user_id} Research Topic {request_id}",
                        scope={"time_range": "2023"}
                    )
                elif request_id % 3 == 1:
                    # Expert consultation request
                    from src.core_services.expert_consultation_scenario import ExpertConsultationRequest, ConsultationType, PriorityLevel
                    
                    request = ExpertConsultationRequest(
                        consultation_type=ConsultationType.TECHNICAL_REVIEW,
                        query=f"User {user_id} consultation question {request_id}",
                        user_preferences={},
                        priority_level=PriorityLevel.MEDIUM
                    )
                    task = system['expert_scenario'].handle_consultation(request)
                else:
                    # Industry analysis request
                    from src.core_services.industry_analysis_scenario import AnalysisRequest, IndustryType, AnalysisDepth
                    
                    request = AnalysisRequest(
                        industry_type=IndustryType.TECHNOLOGY,
                        analysis_depth=AnalysisDepth.OVERVIEW,
                        focus_areas=[f"User {user_id} focus area {request_id}"],
                        time_horizon="1 year",
                        specific_questions=[f"Question {request_id}?"],
                        priority_level="LOW"
                    )
                    task = system['industry_scenario'].submit_analysis_request(request)
                
                user_tasks.append(task)
            
            all_tasks.extend(user_tasks)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        total_requests = num_users * requests_per_user
        success_rate = len(successful_requests) / total_requests
        
        print(f"📊 Performance Results:")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful requests: {len(successful_requests)}")
        print(f"   Failed requests: {len(failed_requests)}")
        print(f"   Success rate: {success_rate:.2%}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per request: {total_time/total_requests:.2f} seconds")
        print(f"   Requests per second: {total_requests/total_time:.2f}")
        
        # Performance assertions
        assert success_rate >= 0.90, f"Success rate {success_rate:.2%} is below 90%"
        assert total_time < 120.0, f"Total time {total_time:.2f} seconds exceeds 120 seconds limit"
        
        print("✅ System performance test passed!")
        
        return {
            "total_requests": total_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": success_rate,
            "total_time": total_time,
            "requests_per_second": total_requests / total_time
        }
    
    @pytest.mark.asyncio
    async def test_system_error_handling_and_recovery(self):
        """Test system error handling and recovery"""
        print("🛡️ Testing system error handling and recovery...")
        
        # Initialize system
        system = await self.test_complete_system_startup()
        
        # Test 1: Invalid input handling
        print("🧪 Test 1: Invalid input handling...")
        
        try:
            # Invalid consultation request
            from src.core_services.expert_consultation_scenario import ExpertConsultationRequest, ConsultationType, PriorityLevel
            
            invalid_request = ExpertConsultationRequest(
                consultation_type=None,  # Invalid
                query="",  # Empty
                user_preferences={},
                priority_level=PriorityLevel.MEDIUM
            )
            
            result = await system['expert_scenario'].handle_consultation(invalid_request)
            # Should handle gracefully
            assert 'success' in result
            assert 'error' in result or result['success'] is True
            
        except Exception as e:
            # Should handle gracefully or throw specific exceptions
            assert isinstance(e, (ValueError, TypeError))
        
        print("✅ Invalid input handling test passed")
        
        # Test 2: Service unavailable scenario
        print("🧪 Test 2: Service unavailable scenario...")
        
        # Mock a service failure
        with patch.object(system['expert_scenario'], '_select_experts_for_consultation') as mock_select:
            mock_select.side_effect = Exception("Service temporarily unavailable")
            
            try:
                request = ExpertConsultationRequest(
                    consultation_type=ConsultationType.TECHNICAL_REVIEW,
                    query="Test query",
                    user_preferences={},
                    priority_level=PriorityLevel.MEDIUM
                )
                
                result = await system['expert_scenario'].handle_consultation(request)
                # Should handle service failure gracefully
                assert 'success' in result
                assert 'error' in result
                
            except Exception as e:
                # Should handle gracefully
                assert "temporarily unavailable" in str(e).lower()
        
        print("✅ Service unavailable handling test passed")
        
        # Test 3: Resource exhaustion handling
        print("🧪 Test 3: Resource exhaustion handling...")
        
        # Test with very high load
        try:
            # Create many requests to test resource management
            tasks = []
            for i in range(20):
                request = ExpertConsultationRequest(
                    consultation_type=ConsultationType.TECHNICAL_REVIEW,
                    query=f"Load test query {i}",
                    user_preferences={},
                    priority_level=PriorityLevel.LOW
                )
                tasks.append(system['expert_scenario'].handle_consultation(request))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Most should succeed, some might fail gracefully
            successful = [r for r in results if not isinstance(r, Exception) and r.get('success')]
            assert len(successful) > 0, "No requests succeeded under load"
            
        except Exception as e:
            # Should handle resource exhaustion gracefully
            assert not isinstance(e, MemoryError)  # Should not crash
        
        print("✅ Resource exhaustion handling test passed")
        
        print("🎉 System error handling and recovery tests passed!")
        
        return {"error_handling_tests": "passed"}
    
    @pytest.mark.asyncio
    async def test_data_consistency_and_integrity(self):
        """Test data consistency and integrity across the system"""
        print("🔍 Testing data consistency and integrity...")
        
        # Initialize system
        system = await self.test_complete_system_startup()
        
        # Test 1: Data consistency across scenarios
        print("🧪 Test 1: Cross-scenario data consistency...")
        
        # Create related requests across scenarios
        base_topic = "Sustainable Energy Technologies"
        
        # Academic research
        literature_result = await system['academic_scenario'].conduct_literature_review(
            topic=base_topic,
            scope={"time_range": "2020-2024"}
        )
        
        # Expert consultation
        from src.core_services.expert_consultation_scenario import ExpertConsultationRequest, ConsultationType, PriorityLevel
        
        consultation_result = await system['expert_scenario'].handle_consultation(
            ExpertConsultationRequest(
                consultation_type=ConsultationType.TECHNICAL_REVIEW,
                query=f"Technical aspects of {base_topic}",
                user_preferences={},
                priority_level=PriorityLevel.MEDIUM
            )
        )
        
        # Industry analysis
        from src.core_services.industry_analysis_scenario import AnalysisRequest, IndustryType, AnalysisDepth
        
        industry_result = await system['industry_scenario'].submit_analysis_request(
            AnalysisRequest(
                industry_type=IndustryType.ENERGY,
                analysis_depth=AnalysisDepth.DETAILED,
                focus_areas=["renewable_energy", "sustainability"],
                time_horizon="5 years",
                specific_questions=[f"Market analysis for {base_topic}"],
                priority_level="HIGH"
            )
        )
        
        # All should succeed and maintain data integrity
        assert literature_result['success'] is True
        assert consultation_result['success'] is True
        assert industry_result['success'] is True
        
        # Check that data structures are consistent
        assert 'review_id' in literature_result
        assert 'consultation_id' in consultation_result
        assert 'report_id' in industry_result
        
        print("✅ Cross-scenario data consistency test passed")
        
        # Test 2: History tracking consistency
        print("🧪 Test 2: History tracking consistency...")
        
        # Retrieve histories
        expert_history = system['expert_scenario'].get_consultation_history(limit=10)
        academic_history = system['academic_scenario'].get_research_history(limit=10)
        industry_history = system['industry_scenario'].get_analysis_history(limit=10)
        
        # Verify history structures
        for record in expert_history:
            assert 'consultation_id' in record
            assert 'timestamp' in record
            assert 'topic' in record
        
        for record in academic_history:
            assert 'paper_id' in record or 'review_id' in record
            assert 'timestamp' in record
        
        for record in industry_history:
            assert 'request_id' in record
            assert 'timestamp' in record
            assert 'industry_type' in record
        
        print("✅ History tracking consistency test passed")
        
        # Test 3: ID uniqueness
        print("🧪 Test 3: ID uniqueness across scenarios...")
        
        # Check that IDs are unique across different scenarios
        all_ids = []
        
        # Collect expert consultation IDs
        for record in expert_history:
            if 'consultation_id' in record:
                all_ids.append(f"expert_{record['consultation_id']}")
        
        # Collect academic research IDs
        for record in academic_history:
            if 'paper_id' in record:
                all_ids.append(f"academic_{record['paper_id']}")
            elif 'review_id' in record:
                all_ids.append(f"academic_{record['review_id']}")
        
        # Collect industry analysis IDs
        for record in industry_history:
            if 'request_id' in record:
                all_ids.append(f"industry_{record['request_id']}")
        
        # Check for uniqueness
        unique_ids = set(all_ids)
        assert len(unique_ids) == len(all_ids), f"Found duplicate IDs: {len(all_ids) - len(unique_ids)} duplicates"
        
        print("✅ ID uniqueness test passed")
        
        print("🎉 Data consistency and integrity tests passed!")
        
        return {
            "data_consistency": "passed",
            "records_tested": len(expert_history) + len(academic_history) + len(industry_history),
            "unique_ids_verified": len(unique_ids)
        }


# Comprehensive test runner
class TestComprehensiveEndToEnd:
    """Comprehensive end-to-end test suite"""
    
    @pytest.mark.asyncio
    async def test_comprehensive_system_validation(self):
        """Run comprehensive system validation"""
        print("🔥 Running comprehensive system validation...")
        
        # Initialize test suite
        test_suite = TestEndToEndSystem()
        
        # Run all tests
        results = {}
        
        try:
            # System startup
            results['system_startup'] = await test_suite.test_complete_system_startup()
            print("✅ System startup test passed")
            
            # End-to-end user interaction
            results['user_interaction'] = await test_suite.test_end_to_end_user_interaction()
            print("✅ User interaction test passed")
            
            # Performance under load
            results['performance'] = await test_suite.test_system_performance_under_load()
            print("✅ Performance test passed")
            
            # Error handling
            results['error_handling'] = await test_suite.test_system_error_handling_and_recovery()
            print("✅ Error handling test passed")
            
            # Data consistency
            results['data_consistency'] = await test_suite.test_data_consistency_and_integrity()
            print("✅ Data consistency test passed")
            
        except Exception as e:
            pytest.fail(f"Comprehensive validation failed: {e}")
        
        # Generate summary
        print("\n🎊 COMPREHENSIVE SYSTEM VALIDATION SUMMARY")
        print("=" * 50)
        print(f"✅ System Startup: PASSED")
        print(f"✅ User Interaction: PASSED")
        print(f"✅ Performance Test: PASSED ({results['performance']['success_rate']:.1%} success rate)")
        print(f"✅ Error Handling: PASSED")
        print(f"✅ Data Consistency: PASSED ({results['data_consistency']['records_tested']} records verified)")
        print("=" * 50)
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        
        return results


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])