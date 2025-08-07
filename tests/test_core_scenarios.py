# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 15:45:00
@Author  : DAIP-LIVE Team
@File    : test_core_scenarios.py
@Description:
    Comprehensive unit tests for the three core scenarios:
    - Expert Consultation Scenario
    - Academic Research Scenario  
    - Industry Analysis Scenario
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List, Any

# Import the scenarios to test
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


class TestExpertConsultationScenario:
    """Test suite for Expert Consultation Scenario"""
    
    @pytest.fixture
    def scenario(self):
        return ExpertConsultationScenario()
    
    @pytest.fixture
    def consultation_request(self):
        return ExpertConsultationRequest(
            id="test_consultation_001",
            title="Microservices Architecture Review",
            description="How to implement microservices architecture?",
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            priority=ConsultationPriority.HIGH,
            requester="test_user",
            domain="software_architecture",
            specific_areas=["microservices", "distributed_systems"],
            background_context="Planning to migrate from monolithic to microservices architecture",
            expected_outcomes=["architecture_recommendations", "best_practices"],
            time_constraints={"response_time": "72 hours"}
        )
    
    @pytest.mark.asyncio
    async def test_scenario_initialization(self, scenario):
        """Test scenario initialization"""
        assert scenario is not None
        assert hasattr(scenario, 'expert_pool')
        assert hasattr(scenario, 'consultation_history')
        assert len(scenario.expert_pool) > 0
    
    @pytest.mark.asyncio
    async def test_handle_consultation_basic(self, scenario, consultation_request):
        """Test basic consultation handling"""
        result = await scenario.handle_consultation(consultation_request)
        
        assert result['success'] is True
        assert 'consultation_id' in result
        assert 'selected_experts' in result
        assert 'synthesis' in result
        assert len(result['selected_experts']) > 0
    
    @pytest.mark.asyncio
    async def test_expert_selection(self, scenario):
        """Test expert selection logic"""
        experts = scenario._select_experts_for_consultation(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            required_experts=2,
            user_preferences={}
        )
        
        assert len(experts) <= 2
        assert len(experts) > 0
        for expert in experts:
            assert hasattr(expert, 'name')
            assert hasattr(expert, 'expertise_area')
    
    @pytest.mark.asyncio
    async def test_different_consultation_types(self, scenario):
        """Test different consultation types"""
        types_to_test = [
            ConsultationType.TECHNICAL_REVIEW,
            ConsultationType.STRATEGIC_ADVISORY,
            ConsultationType.PROBLEM_SOLVING
        ]
        
        for consultation_type in types_to_test:
            request = ExpertConsultationRequest(
                id=f"test_consultation_{consultation_type.value}",
                title=f"Test {consultation_type.value}",
                description=f"Test query for {consultation_type.value}",
                consultation_type=consultation_type,
                priority=ConsultationPriority.MEDIUM,
                requester="test_user",
                domain="test_domain",
                specific_areas=["test_area"],
                background_context="Test background",
                expected_outcomes=["test_outcome"],
                time_constraints={"response_time": "72 hours"}
            )
            
            result = await scenario.handle_consultation(request)
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_priority_handling(self, scenario):
        """Test different priority levels"""
        priorities_to_test = [
            ConsultationPriority.URGENT,
            ConsultationPriority.HIGH,
            ConsultationPriority.MEDIUM,
            ConsultationPriority.LOW
        ]
        
        for priority in priorities_to_test:
            request = ExpertConsultationRequest(
                id=f"test_consultation_{priority.value}",
                title=f"Test {priority.value}",
                description=f"Test query for {priority.value} priority",
                consultation_type=ConsultationType.TECHNICAL_REVIEW,
                priority=priority,
                requester="test_user",
                domain="test_domain",
                specific_areas=["test_area"],
                background_context="Test background",
                expected_outcomes=["test_outcome"],
                time_constraints={"response_time": "72 hours"}
            )
            
            result = await scenario.handle_consultation(request)
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_consultation_history(self, scenario, consultation_request):
        """Test consultation history tracking"""
        # Submit a consultation
        result = await scenario.handle_consultation(consultation_request)
        assert result['success'] is True
        
        # Check history
        history = scenario.get_consultation_history(limit=1)
        assert len(history) == 1
        assert history[0]['consultation_id'] == result['consultation_id']


class TestAcademicResearchScenario:
    """Test suite for Academic Research Scenario"""
    
    @pytest.fixture
    def scenario(self):
        return AcademicResearchScenario()
    
    @pytest.fixture
    def research_paper(self):
        return ResearchPaper(
            id="test_paper_001",
            title="Machine Learning in Healthcare",
            abstract="This paper explores the application of ML in healthcare settings.",
            authors=["John Doe", "Jane Smith"],
            keywords=["machine learning", "healthcare", "AI"],
            research_type=ResearchType.EMPIRICAL_RESEARCH,
            methodology="Experimental study with quantitative analysis",
            data_sources=["Hospital datasets", "Public health records"],
            findings=["ML models achieve 85% accuracy in diagnosis", "Early detection improves patient outcomes"],
            limitations=["Small sample size", "Single institution study"],
            references=[{"title": "Related study 1", "authors": ["Author1"], "year": 2022}],
            word_count=3500,
            submission_date=datetime.now()
        )
    
    @pytest.mark.asyncio
    async def test_scenario_initialization(self, scenario):
        """Test scenario initialization"""
        assert scenario is not None
        assert hasattr(scenario, 'expert_allocator')
        assert hasattr(scenario, 'research_history')
        assert hasattr(scenario, 'academic_standards')
    
    @pytest.mark.asyncio
    async def test_submit_research_paper(self, scenario, research_paper):
        """Test research paper submission"""
        result = await scenario.submit_research_paper(research_paper)
        
        assert result['success'] is True
        assert 'paper_id' in result
        assert 'session_id' in result
        assert 'peer_reviews' in result
        assert 'academic_assessment' in result
        assert len(result['peer_reviews']) > 0
    
    @pytest.mark.asyncio
    async def test_conduct_literature_review(self, scenario):
        """Test literature review functionality"""
        result = await scenario.conduct_literature_review(
            topic="Artificial Intelligence in Education",
            scope={"time_scope": "2018-2023", "quality_threshold": 0.7}
        )
        
        assert result['success'] is True
        assert 'topic' in result
        assert 'literature_search' in result
        assert 'thematic_analysis' in result
        assert 'research_gaps' in result
    
    @pytest.mark.asyncio
    async def test_different_research_types(self, scenario):
        """Test different research types"""
        research_types = [
            ResearchType.LITERATURE_REVIEW,
            ResearchType.EMPIRICAL_RESEARCH,
            ResearchType.THEORETICAL_RESEARCH,
            ResearchType.METHODOLOGICAL_RESEARCH,
            ResearchType.COMPARATIVE_RESEARCH
        ]
        
        for research_type in research_types:
            paper = ResearchPaper(
                title=f"Test {research_type.value} Paper",
                abstract="Test abstract",
                authors=["Test Author"],
                keywords=["test"],
                research_type=research_type
            )
            
            result = await scenario.submit_research_paper(paper)
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_multidimensional_assessment(self, scenario, research_paper):
        """Test multidimensional assessment"""
        result = await scenario.submit_research_paper(research_paper)
        
        if result['success']:
            # Check if assessment includes multiple dimensions
            paper_id = result['paper_id']
            assessment = await scenario.get_paper_assessment(paper_id)
            
            assert 'methodology_score' in assessment
            assert 'originality_score' in assessment
            assert 'clarity_score' in assessment
            assert 'impact_score' in assessment
            assert 'overall_score' in assessment
    
    @pytest.mark.asyncio
    async def test_research_history(self, scenario, research_paper):
        """Test research history tracking"""
        # Submit a paper
        result = await scenario.submit_research_paper(research_paper)
        assert result['success'] is True
        
        # Check history
        history = scenario.get_research_history(limit=1)
        assert len(history) == 1
        assert history[0]['paper_id'] == result['paper_id']


class TestIndustryAnalysisScenario:
    """Test suite for Industry Analysis Scenario"""
    
    @pytest.fixture
    def scenario(self):
        return IndustryAnalysisScenario()
    
    @pytest.fixture
    def analysis_request(self):
        return AnalysisRequest(
            industry_type=IndustryType.TECHNOLOGY,
            analysis_depth=AnalysisDepth.DETAILED,
            focus_areas=["Market Trends", "Competitive Intelligence"],
            time_horizon="3-5 years",
            specific_questions=["What are the key growth drivers?"],
            priority_level="HIGH"
        )
    
    @pytest.mark.asyncio
    async def test_scenario_initialization(self, scenario):
        """Test scenario initialization"""
        assert scenario is not None
        assert hasattr(scenario, 'expert_pool')
        assert hasattr(scenario, 'analysis_history')
        assert len(scenario.expert_pool) > 0
    
    @pytest.mark.asyncio
    async def test_submit_analysis_request(self, scenario, analysis_request):
        """Test analysis request submission"""
        result = await scenario.submit_analysis_request(analysis_request)
        
        assert result['success'] is True
        assert 'request_id' in result
        assert 'report_id' in result
        assert 'selected_experts' in result
        assert 'quality_score' in result
        assert result['quality_score'] > 0.0
    
    @pytest.mark.asyncio
    async def test_different_industry_types(self, scenario):
        """Test different industry types"""
        industries_to_test = [
            IndustryType.TECHNOLOGY,
            IndustryType.HEALTHCARE,
            IndustryType.FINANCE,
            IndustryType.RETAIL
        ]
        
        for industry in industries_to_test:
            request = AnalysisRequest(
                industry_type=industry,
                analysis_depth=AnalysisDepth.OVERVIEW,
                focus_areas=["Market Analysis"],
                time_horizon="1-2 years",
                specific_questions=["What is the market size?"],
                priority_level="MEDIUM"
            )
            
            result = await scenario.submit_analysis_request(request)
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_different_analysis_depths(self, scenario):
        """Test different analysis depths"""
        depths_to_test = [
            AnalysisDepth.OVERVIEW,
            AnalysisDepth.DETAILED,
            AnalysisDepth.COMPREHENSIVE
        ]
        
        for depth in depths_to_test:
            request = AnalysisRequest(
                industry_type=IndustryType.TECHNOLOGY,
                analysis_depth=depth,
                focus_areas=["Market Trends"],
                time_horizon="2-3 years",
                specific_questions=["What are the key trends?"],
                priority_level="MEDIUM"
            )
            
            result = await scenario.submit_analysis_request(request)
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_expert_selection(self, scenario, analysis_request):
        """Test expert selection for industry analysis"""
        selected_experts = scenario._select_experts_for_analysis(analysis_request)
        
        assert len(selected_experts) > 0
        assert len(selected_experts) <= 4  # Max for detailed analysis
        
        # Check if selected experts have relevant industry focus
        for expert in selected_experts:
            assert analysis_request.industry_type in expert.industry_focus
    
    @pytest.mark.asyncio
    async def test_get_industry_overview(self, scenario):
        """Test industry overview functionality"""
        overview = await scenario.get_industry_overview(IndustryType.TECHNOLOGY)
        
        assert 'industry_type' in overview
        assert 'market_size' in overview
        assert 'growth_rate' in overview
        assert 'key_segments' in overview
        assert 'available_experts' in overview
        assert overview['available_experts'] > 0
    
    @pytest.mark.asyncio
    async def test_analysis_status_tracking(self, scenario, analysis_request):
        """Test analysis status tracking"""
        # Submit analysis
        result = await scenario.submit_analysis_request(analysis_request)
        assert result['success'] is True
        
        # Check status
        status = await scenario.get_analysis_status(result['request_id'])
        assert status['status'] == 'success'
        assert status['industry_type'] == analysis_request.industry_type.value
    
    @pytest.mark.asyncio
    async def test_analysis_history(self, scenario, analysis_request):
        """Test analysis history tracking"""
        # Submit analysis
        result = await scenario.submit_analysis_request(analysis_request)
        assert result['success'] is True
        
        # Check history
        history = scenario.get_analysis_history(limit=1)
        assert len(history) == 1
        assert history[0]['request_id'] == result['request_id']


class TestScenarioIntegration:
    """Integration tests for all three scenarios"""
    
    @pytest.mark.asyncio
    async def test_cross_scenario_functionality(self):
        """Test that all scenarios can coexist and function together"""
        # Initialize all scenarios
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        industry_scenario = IndustryAnalysisScenario()
        
        # Test that all scenarios initialize properly
        assert expert_scenario is not None
        assert academic_scenario is not None
        assert industry_scenario is not None
        
        # Test that all scenarios have expert pools
        assert len(expert_scenario.expert_pool) > 0
        assert len(academic_scenario.reviewer_pool) > 0
        assert len(industry_scenario.expert_pool) > 0
        
        # Test basic functionality of all scenarios
        expert_request = ExpertConsultationRequest(
            id="integration_test",
            title="Integration Test",
            description="Integration test query",
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            priority=ConsultationPriority.MEDIUM,
            requester="test_user",
            domain="test_domain",
            specific_areas=["test_area"],
            background_context="Test background",
            expected_outcomes=["test_outcome"],
            time_constraints={"response_time": "72 hours"}
        )
        
        expert_result = await expert_scenario.handle_consultation(expert_request)
        assert expert_result['success'] is True
        
        # Test that all scenarios can run concurrently
        tasks = [
            expert_scenario.handle_consultation(expert_request),
            academic_scenario.conduct_literature_review(
                topic="Integration test topic",
                scope={"time_range": "2023"}
            ),
            industry_scenario.submit_analysis_request(
                AnalysisRequest(
                    industry_type=IndustryType.TECHNOLOGY,
                    analysis_depth=AnalysisDepth.OVERVIEW,
                    focus_areas=["Integration test"],
                    time_horizon="1 year",
                    specific_questions=["Integration test question?"],
                    priority_level="LOW"
                )
            )
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all scenarios completed successfully
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Scenario failed with exception: {result}")
            assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_performance_benchmark(self):
        """Test performance benchmark for all scenarios"""
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        industry_scenario = IndustryAnalysisScenario()
        
        import time
        start_time = time.time()
        
        # Run multiple requests across all scenarios
        tasks = []
        for i in range(5):
            expert_request = ExpertConsultationRequest(
                id=f"performance_test_{i}",
                title=f"Performance Test {i}",
                description=f"Performance test query {i}",
                consultation_type=ConsultationType.TECHNICAL_REVIEW,
                priority=ConsultationPriority.MEDIUM,
                requester="test_user",
                domain="test_domain",
                specific_areas=["test_area"],
                background_context="Test background",
                expected_outcomes=["test_outcome"],
                time_constraints={"response_time": "72 hours"}
            )
            
            analysis_request = AnalysisRequest(
                industry_type=IndustryType.TECHNOLOGY,
                analysis_depth=AnalysisDepth.OVERVIEW,
                focus_areas=[f"Performance test {i}"],
                time_horizon="1 year",
                specific_questions=[f"Question {i}?"],
                priority_level="LOW"
            )
            
            tasks.extend([
                expert_scenario.handle_consultation(expert_request),
                academic_scenario.conduct_literature_review(
                    topic=f"Performance test topic {i}",
                    scope={"time_range": "2023"}
                ),
                industry_scenario.submit_analysis_request(analysis_request)
            ])
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == len(results)
        assert all(result['success'] for result in successful_results)
        
        # Performance check (should complete within 30 seconds)
        assert total_time < 30.0, f"Performance test took {total_time:.2f} seconds, expected < 30 seconds"
        
        print(f"Performance benchmark completed in {total_time:.2f} seconds")


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])