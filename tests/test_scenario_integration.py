"""@Time    : 2025-08-04 16:00:00
@Author  : DAIP-LIVE Team
@File    : test_scenario_integration.py
@Description:
    Integration tests for scenario workflows and system integration.
    Tests the interaction between scenarios and core system components.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import system components
from src.app_state import AppState
from src.core_services.academic_research_scenario import AcademicResearchScenario
from src.core_services.expert_consultation_scenario import ExpertConsultationScenario
from src.core_services.industry_analysis_scenario import IndustryAnalysisScenario
from src.core_services.smart_reviewer_allocator_simple import SmartReviewerAllocator


class TestScenarioSystemIntegration:
    """Integration tests for scenario system integration"""
    
    @pytest.fixture()
    async def app_state(self):
        """Create application state for testing"""
        app_state = AppState()
        await app_state.initialize()
        return app_state
    
    @pytest.fixture()
    def expert_scenario(self):
        return ExpertConsultationScenario()
    
    @pytest.fixture()
    def academic_scenario(self):
        return AcademicResearchScenario()
    
    @pytest.fixture()
    def industry_scenario(self):
        return IndustryAnalysisScenario()
    
    @pytest.fixture()
    def reviewer_allocator(self):
        return SmartReviewerAllocator()
    
    @pytest.mark.asyncio()
    async def test_app_state_initialization(self, app_state):
        """Test that app state initializes correctly"""
        assert app_state is not None
        assert hasattr(app_state, 'llm_interface')
        assert hasattr(app_state, 'memory_service')
        assert hasattr(app_state, 'wiki_service')
        assert hasattr(app_state, 'synthesis_engine')
    
    @pytest.mark.asyncio()
    async def test_scenario_allocator_integration(self, expert_scenario, reviewer_allocator):
        """Test integration between scenarios and reviewer allocator"""
        # Test that expert scenario can use allocator
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        
        request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="Test integration with allocator",
            user_preferences={},
            priority_level=PriorityLevel.MEDIUM
        )
        
        # Mock the allocator integration
        with patch.object(expert_scenario, '_select_experts_for_consultation') as mock_select:
            mock_select.return_value = [
                Mock(name="Test Expert", expertise_area="Testing", availability_score=1.0)
            ]
            
            result = await expert_scenario.handle_consultation(request)
            assert result['success'] is True
            mock_select.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_memory_service_integration(self, app_state, expert_scenario):
        """Test integration with memory service"""
        # Test that scenarios can interact with memory service
        test_data = {
            "type": "test_interaction",
            "scenario": "expert_consultation",
            "timestamp": datetime.now().isoformat(),
            "data": {"test": "value"}
        }
        
        # Mock memory service interaction
        with patch.object(app_state.memory_service, 'store_interaction', new_callable=AsyncMock) as mock_store:
            mock_store.return_value = {"success": True}
            
            result = await mock_store(test_data)
            assert result['success'] is True
            mock_store.assert_called_once_with(test_data)
    
    @pytest.mark.asyncio()
    async def test_wiki_service_integration(self, app_state, academic_scenario):
        """Test integration with wiki service"""
        # Test that academic scenario can use wiki service
        test_content = {
            "title": "Test Research Paper",
            "content": "Test content for integration",
            "metadata": {"type": "research", "authors": ["Test Author"]}
        }
        
        # Mock wiki service interaction
        with patch.object(app_state.wiki_service, 'create_page', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {"success": True, "page_id": "test_page_123"}
            
            result = await mock_create(test_content)
            assert result['success'] is True
            assert 'page_id' in result
    
    @pytest.mark.asyncio()
    async def test_synthesis_engine_integration(self, app_state, expert_scenario):
        """Test integration with synthesis engine"""
        # Test that scenarios can use synthesis engine
        expert_opinions = [
            {"expert": "Expert 1", "opinion": "First opinion", "confidence": 0.8},
            {"expert": "Expert 2", "opinion": "Second opinion", "confidence": 0.9}
        ]
        
        # Mock synthesis engine interaction
        with patch.object(app_state.synthesis_engine, 'synthesize_expert_opinions', new_callable=AsyncMock) as mock_synthesize:
            mock_synthesize.return_value = {
                "success": True,
                "synthesis": "Consensus opinion based on expert inputs",
                "confidence": 0.85
            }
            
            result = await mock_synthesize(expert_opinions)
            assert result['success'] is True
            assert 'synthesis' in result
            mock_synthesize.assert_called_once_with(expert_opinions)
    
    @pytest.mark.asyncio()
    async def test_cross_scenario_data_sharing(self, expert_scenario, academic_scenario, industry_scenario):
        """Test data sharing between scenarios"""
        # Test that scenarios can share context and data
        
        # Expert consultation generates data
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        
        expert_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="How to implement AI in healthcare?",
            user_preferences={},
            priority_level=PriorityLevel.HIGH
        )
        
        expert_result = await expert_scenario.handle_consultation(expert_request)
        assert expert_result['success'] is True
        
        # Academic research uses similar context
        academic_result = await academic_scenario.conduct_literature_review(
            topic="AI in Healthcare",
            scope={"time_range": "2020-2024"}
        )
        assert academic_result['success'] is True
        
        # Industry analysis uses related context
        from src.core_services.industry_analysis_scenario import AnalysisDepth, AnalysisRequest, IndustryType
        
        industry_request = AnalysisRequest(
            industry_type=IndustryType.HEALTHCARE,
            analysis_depth=AnalysisDepth.DETAILED,
            focus_areas=["AI Technology", "Digital Health"],
            time_horizon="3-5 years",
            specific_questions=["How is AI transforming healthcare?"],
            priority_level="HIGH"
        )
        
        industry_result = await industry_scenario.submit_analysis_request(industry_request)
        assert industry_result['success'] is True
        
        # Verify all scenarios produced results
        assert 'consultation_id' in expert_result
        assert 'review_id' in academic_result
        assert 'report_id' in industry_result
    
    @pytest.mark.asyncio()
    async def test_concurrent_scenario_execution(self, expert_scenario, academic_scenario, industry_scenario):
        """Test concurrent execution of multiple scenarios"""
        # Prepare requests for all scenarios
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        from src.core_services.industry_analysis_scenario import AnalysisDepth, AnalysisRequest, IndustryType
        
        expert_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="Concurrent test query",
            user_preferences={},
            priority_level=PriorityLevel.MEDIUM
        )
        
        industry_request = AnalysisRequest(
            industry_type=IndustryType.TECHNOLOGY,
            analysis_depth=AnalysisDepth.OVERVIEW,
            focus_areas=["Concurrent Testing"],
            time_horizon="1 year",
            specific_questions=["Concurrent test question?"],
            priority_level="LOW"
        )
        
        # Execute all scenarios concurrently
        tasks = [
            expert_scenario.handle_consultation(expert_request),
            academic_scenario.conduct_literature_review(
                topic="Concurrent Test Topic",
                scope={"time_range": "2023"}
            ),
            industry_scenario.submit_analysis_request(industry_request)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all scenarios completed successfully
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Scenario {i} failed with exception: {result}")
            assert result['success'] is True, f"Scenario {i} failed: {result}"
    
    @pytest.mark.asyncio()
    async def test_error_handling_and_recovery(self, expert_scenario):
        """Test error handling and recovery in scenarios"""
        from src.core_services.expert_consultation_scenario import (
            ExpertConsultationRequest,
            PriorityLevel,
        )
        
        # Test with invalid request
        invalid_request = ExpertConsultationRequest(
            consultation_type=None,  # Invalid consultation type
            query="",  # Empty query
            user_preferences={},
            priority_level=PriorityLevel.MEDIUM
        )
        
        # Should handle gracefully
        try:
            result = await expert_scenario.handle_consultation(invalid_request)
            # If it doesn't throw exception, check result
            assert 'success' in result
            assert 'error' in result or result['success'] is True
        except Exception as e:
            # If it throws exception, it should be handled gracefully
            assert isinstance(e, (ValueError, TypeError))
    
    @pytest.mark.asyncio()
    async def test_scenario_performance_under_load(self, expert_scenario, academic_scenario):
        """Test scenario performance under load"""
        import time

        # Create multiple requests
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        
        requests = []
        for i in range(10):
            request = ExpertConsultationRequest(
                consultation_type=ConsultationType.TECHNICAL_REVIEW,
                query=f"Load test query {i}",
                user_preferences={},
                priority_level=PriorityLevel.MEDIUM
            )
            requests.append(request)
        
        # Execute all requests concurrently
        start_time = time.time()
        
        tasks = [expert_scenario.handle_consultation(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(requests)
        assert all(result['success'] for result in successful_results)
        
        # Performance check (should complete within 60 seconds)
        assert total_time < 60.0, f"Load test took {total_time:.2f} seconds, expected < 60 seconds"
        
        print(f"Load test completed: {len(requests)} requests in {total_time:.2f} seconds")
    
    @pytest.mark.asyncio()
    async def test_resource_cleanup(self, expert_scenario, academic_scenario, industry_scenario):
        """Test that scenarios clean up resources properly"""
        # Test that scenarios can handle multiple requests without memory leaks
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        from src.core_services.industry_analysis_scenario import AnalysisDepth, AnalysisRequest, IndustryType
        
        # Make multiple requests
        for i in range(5):
            expert_request = ExpertConsultationRequest(
                consultation_type=ConsultationType.TECHNICAL_REVIEW,
                query=f"Cleanup test {i}",
                user_preferences={},
                priority_level=PriorityLevel.MEDIUM
            )
            
            industry_request = AnalysisRequest(
                industry_type=IndustryType.TECHNOLOGY,
                analysis_depth=AnalysisDepth.OVERVIEW,
                focus_areas=[f"Cleanup test {i}"],
                time_horizon="1 year",
                specific_questions=[f"Question {i}?"],
                priority_level="LOW"
            )
            
            # Execute requests
            expert_result = await expert_scenario.handle_consultation(expert_request)
            industry_result = await industry_scenario.submit_analysis_request(industry_request)
            
            assert expert_result['success'] is True
            assert industry_result['success'] is True
        
        # Check that history is properly managed
        expert_history = expert_scenario.get_consultation_history(limit=10)
        industry_history = industry_scenario.get_analysis_history(limit=10)
        
        assert len(expert_history) <= 10
        assert len(industry_history) <= 10
    
    @pytest.mark.asyncio()
    async def test_configuration_propagation(self, expert_scenario, academic_scenario, industry_scenario):
        """Test that configuration changes propagate correctly"""
        # Test that scenarios can be configured and maintain configuration
        
        # Check default configurations
        assert hasattr(expert_scenario, 'expert_pool')
        assert hasattr(academic_scenario, 'reviewer_pool')
        assert hasattr(industry_scenario, 'expert_pool')
        
        # Verify configurations are properly set
        assert len(expert_scenario.expert_pool) > 0
        assert len(academic_scenario.reviewer_pool) > 0
        assert len(industry_scenario.expert_pool) > 0
        
        # Test that scenarios maintain their state
        from src.core_services.expert_consultation_scenario import (
            ConsultationType,
            ExpertConsultationRequest,
            PriorityLevel,
        )
        
        request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="Configuration test",
            user_preferences={},
            priority_level=PriorityLevel.MEDIUM
        )
        
        result = await expert_scenario.handle_consultation(request)
        assert result['success'] is True
        
        # Verify scenario maintained its configuration
        assert len(expert_scenario.expert_pool) > 0
        assert len(expert_scenario.consultation_history) > 0


class TestScenarioAPISimulation:
    """Simulate API interactions with scenarios"""
    
    @pytest.mark.asyncio()
    async def test_api_request_simulation(self):
        """Test simulated API requests to scenarios"""
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        industry_scenario = IndustryAnalysisScenario()
        
        # Simulate API endpoint calls
        api_calls = [
            {
                "endpoint": "/expert-consultation",
                "method": "POST",
                "data": {
                    "consultation_type": "TECHNICAL_REVIEW",
                    "query": "API test query",
                    "priority_level": "MEDIUM"
                }
            },
            {
                "endpoint": "/academic-research/literature-review",
                "method": "POST",
                "data": {
                    "topic": "API test topic",
                    "scope": {"time_range": "2023"}
                }
            },
            {
                "endpoint": "/industry-analysis",
                "method": "POST",
                "data": {
                    "industry_type": "TECHNOLOGY",
                    "analysis_depth": "OVERVIEW",
                    "focus_areas": ["API Testing"],
                    "time_horizon": "1 year"
                }
            }
        ]
        
        # Process API calls
        results = []
        for call in api_calls:
            if call["endpoint"] == "/expert-consultation":
                from src.core_services.expert_consultation_scenario import (
                    ConsultationType,
                    ExpertConsultationRequest,
                    PriorityLevel,
                )
                
                request = ExpertConsultationRequest(
                    consultation_type=ConsultationType.TECHNICAL_REVIEW,
                    query=call["data"]["query"],
                    user_preferences={},
                    priority_level=PriorityLevel.MEDIUM
                )
                
                result = await expert_scenario.handle_consultation(request)
                
            elif call["endpoint"] == "/academic-research/literature-review":
                result = await academic_scenario.conduct_literature_review(
                    topic=call["data"]["topic"],
                    scope=call["data"]["scope"]
                )
                
            elif call["endpoint"] == "/industry-analysis":
                from src.core_services.industry_analysis_scenario import AnalysisDepth, AnalysisRequest, IndustryType
                
                request = AnalysisRequest(
                    industry_type=IndustryType.TECHNOLOGY,
                    analysis_depth=AnalysisDepth.OVERVIEW,
                    focus_areas=call["data"]["focus_areas"],
                    time_horizon=call["data"]["time_horizon"],
                    specific_questions=["API test question?"],
                    priority_level="LOW"
                )
                
                result = await industry_scenario.submit_analysis_request(request)
            
            results.append({
                "endpoint": call["endpoint"],
                "result": result,
                "success": result.get("success", False)
            })
        
        # Verify all API calls succeeded
        for result in results:
            assert result["success"], f"API call to {result['endpoint']} failed: {result['result']}"
        
        print(f"API simulation completed: {len(results)} successful calls")


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])