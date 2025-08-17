"""@Time    : 2025-08-04 16:15:00
@Author  : DAIP-LIVE Team
@File    : test_user_stories.py
@Description:
    User story tests for real-world usage scenarios.
    Tests complete user workflows and experiences.
"""

import asyncio

import pytest

from src.core_services.academic_research_scenario import (
    AcademicResearchScenario,
    AcademicStandard,
    ResearchPaper,
    ResearchType,
)

# Import the scenarios
from src.core_services.expert_consultation_scenario import (
    ConsultationType,
    ConsultationPriority,
    ExpertConsultationRequest,
    ExpertConsultationScenario,
)
from src.core_services.industry_analysis_scenario import (
    AnalysisDepth,
    AnalysisRequest,
    IndustryAnalysisScenario,
    IndustryType,
)


class TestUserStoryAcademicResearcher:
    """User story: Academic researcher writing a paper on AI ethics"""
    
    @pytest.mark.asyncio()
    async def test_complete_research_workflow(self):
        """Test complete academic research workflow"""
        academic_scenario = AcademicResearchScenario()
        expert_scenario = ExpertConsultationScenario()
        
        print("🎓 User Story: Academic Researcher - AI Ethics Paper")
        
        # Step 1: Literature review to understand current research
        print("📚 Step 1: Conducting literature review...")
        literature_result = await academic_scenario.conduct_literature_review(
            topic="AI Ethics in Healthcare",
            scope={
                "time_range": "2018-2024",
                "min_papers": 15,
                "focus_areas": ["ethical frameworks", "bias detection", "transparency"]
            }
        )
        
        assert literature_result['success'] is True
        print(f"✅ Found {literature_result['papers_found']} relevant papers")
        
        # Step 2: Submit research paper for peer review
        print("📝 Step 2: Submitting research paper for review...")
        research_paper = ResearchPaper(
            title="Ethical Considerations in AI-Powered Medical Diagnosis",
            abstract="This paper examines the ethical implications of using AI systems in medical diagnosis, focusing on bias, transparency, and patient autonomy.",
            authors=["Dr. Sarah Chen", "Prof. Michael Rodriguez"],
            keywords=["AI ethics", "medical diagnosis", "bias", "transparency", "healthcare"],
            research_type=ResearchType.EMPIRICAL_RESEARCH,
            academic_standard=AcademicStandard.PEER_REVIEWED,
            content="Full research paper content..."
        )
        
        paper_result = await academic_scenario.submit_research_paper(research_paper)
        assert paper_result['success'] is True
        print(f"✅ Paper submitted with ID: {paper_result['paper_id']}")
        print(f"✅ Assigned {len(paper_result['assigned_reviewers'])} reviewers")
        
        # Step 3: Get expert consultation on methodology
        print("🎯 Step 3: Consulting methodology experts...")
        methodology_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.METHODOLOGY_REVIEW,
            query="What are the best methodological approaches for studying AI bias in healthcare systems?",
            user_preferences={
                "expertise_level": "advanced",
                "methodology_preference": "mixed_methods"
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["methodological_recommendations", "case_studies", "best_practices"]
        )
        
        methodology_result = await expert_scenario.handle_consultation(methodology_request)
        assert methodology_result['success'] is True
        print(f"✅ Consultation completed with {len(methodology_result['selected_experts'])} experts")
        
        # Step 4: Get ethical framework consultation
        print("⚖️ Step 4: Consulting ethics experts...")
        ethics_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.STRATEGIC_ADVISORY,
            query="What ethical frameworks should guide AI development in healthcare?",
            user_preferences={
                "focus_areas": ["patient autonomy", "bias mitigation", "transparency"]
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["ethical_frameworks", "guidelines", "policy_recommendations"]
        )
        
        ethics_result = await expert_scenario.handle_consultation(ethics_request)
        assert ethics_result['success'] is True
        print("✅ Ethics consultation completed")
        
        # Step 5: Track paper progress and get assessment
        print("📊 Step 5: Tracking paper assessment...")
        assessment = await academic_scenario.get_paper_assessment(paper_result['paper_id'])
        assert 'overall_score' in assessment
        print(f"✅ Paper assessment score: {assessment['overall_score']:.2f}")
        
        print("🎉 Complete academic research workflow successful!")
        
        return {
            "literature_review": literature_result,
            "paper_submission": paper_result,
            "methodology_consultation": methodology_result,
            "ethics_consultation": ethics_result,
            "paper_assessment": assessment
        }


class TestUserStoryStartupFounder:
    """User story: Startup founder seeking market analysis and funding advice"""
    
    @pytest.mark.asyncio()
    async def test_complete_startup_workflow(self):
        """Test complete startup founder workflow"""
        industry_scenario = IndustryAnalysisScenario()
        expert_scenario = ExpertConsultationScenario()
        
        print("🚀 User Story: Startup Founder - SaaS Platform")
        
        # Step 1: Industry analysis for SaaS market
        print("📈 Step 1: Analyzing SaaS industry...")
        industry_request = AnalysisRequest(
            industry_type=IndustryType.TECHNOLOGY,
            analysis_depth=AnalysisDepth.COMPREHENSIVE,
            focus_areas=["SaaS", "Cloud Computing", "Market Trends", "Competition"],
            time_horizon="3-5 years",
            specific_questions=[
                "What is the current market size for SaaS?",
                "Who are the main competitors?",
                "What are the key growth drivers?",
                "What are the barriers to entry?"
            ],
            priority_level="HIGH"
        )
        
        industry_result = await industry_scenario.submit_analysis_request(industry_request)
        assert industry_result['success'] is True
        print(f"✅ Industry analysis completed with quality score: {industry_result['quality_score']:.2f}")
        
        # Step 2: Expert consultation on business strategy
        print("💼 Step 2: Consulting business strategy experts...")
        strategy_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.STRATEGIC_ADVISORY,
            query="How should we position our AI-powered SaaS platform in the current market?",
            user_preferences={
                "business_stage": "seed_stage",
                "target_market": "mid_size_enterprises",
                "competitive_advantage": "ai_integration"
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["market_positioning", "competitive_strategy", "growth_plan"]
        )
        
        strategy_result = await expert_scenario.handle_consultation(strategy_request)
        assert strategy_result['success'] is True
        print("✅ Strategy consultation completed")
        
        # Step 3: Technical architecture consultation
        print("🔧 Step 3: Consulting technical architecture experts...")
        tech_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="What technical architecture should we use for our AI SaaS platform?",
            user_preferences={
                "tech_stack": "cloud_native",
                "scalability_requirements": "high",
                "security_requirements": "enterprise_grade"
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["architecture_recommendations", "tech_stack", "scalability_plan"]
        )
        
        tech_result = await expert_scenario.handle_consultation(tech_request)
        assert tech_result['success'] is True
        print("✅ Technical consultation completed")
        
        # Step 4: Funding strategy consultation
        print("💰 Step 4: Consulting funding experts...")
        funding_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.FINANCIAL_ADVISORY,
            query="What funding strategy should we pursue for our SaaS startup?",
            user_preferences={
                "funding_stage": "seed",
                "funding_amount": "1-2M",
                "investor_type": "vc"
            },
            priority_level=PriorityLevel.URGENT,
            expected_outcomes=["funding_strategy", "investor_targeting", "valuation_guidance"]
        )
        
        funding_result = await expert_scenario.handle_consultation(funding_request)
        assert funding_result['success'] is True
        print("✅ Funding consultation completed")
        
        # Step 5: Quick market overview for follow-up
        print("🔍 Step 5: Getting updated market overview...")
        market_overview = await industry_scenario.get_industry_overview(IndustryType.TECHNOLOGY)
        assert 'market_size' in market_overview
        print(f"✅ Market size: ${market_overview['market_size']:,.0f}")
        print(f"✅ Growth rate: {market_overview['growth_rate']*100:.1f}%")
        
        print("🎉 Complete startup founder workflow successful!")
        
        return {
            "industry_analysis": industry_result,
            "strategy_consultation": strategy_result,
            "technical_consultation": tech_result,
            "funding_consultation": funding_result,
            "market_overview": market_overview
        }


class TestUserStoryHealthcareAdministrator:
    """User story: Healthcare administrator implementing AI solutions"""
    
    @pytest.mark.asyncio()
    async def test_complete_healthcare_workflow(self):
        """Test complete healthcare administrator workflow"""
        industry_scenario = IndustryAnalysisScenario()
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        
        print("🏥 User Story: Healthcare Administrator - AI Implementation")
        
        # Step 1: Healthcare industry analysis
        print("🏥 Step 1: Analyzing healthcare industry trends...")
        healthcare_request = AnalysisRequest(
            industry_type=IndustryType.HEALTHCARE,
            analysis_depth=AnalysisDepth.DETAILED,
            focus_areas=["AI in Healthcare", "Digital Transformation", "Regulatory Compliance"],
            time_horizon="2-3 years",
            specific_questions=[
                "How is AI being adopted in healthcare?",
                "What are the regulatory considerations?",
                "What are the implementation challenges?",
                "What are the cost implications?"
            ],
            priority_level="HIGH"
        )
        
        healthcare_result = await industry_scenario.submit_analysis_request(healthcare_request)
        assert healthcare_result['success'] is True
        print("✅ Healthcare analysis completed")
        
        # Step 2: Literature review on AI in healthcare
        print("📚 Step 2: Reviewing academic literature on AI in healthcare...")
        literature_result = await academic_scenario.conduct_literature_review(
            topic="AI Implementation in Healthcare Settings",
            scope={
                "time_range": "2020-2024",
                "min_papers": 10,
                "focus_areas": ["clinical outcomes", "cost effectiveness", "implementation barriers"]
            }
        )
        
        assert literature_result['success'] is True
        print(f"✅ Literature review found {literature_result['papers_found']} papers")
        
        # Step 3: Technical implementation consultation
        print("🔧 Step 3: Consulting technical implementation experts...")
        implementation_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="What are the best practices for implementing AI in hospital settings?",
            user_preferences={
                "setting": "hospital",
                "scale": "large",
                "integration_requirements": ["EHR", "clinical_workflows"]
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["implementation_guide", "integration_strategy", "best_practices"]
        )
        
        implementation_result = await expert_scenario.handle_consultation(implementation_request)
        assert implementation_result['success'] is True
        print("✅ Implementation consultation completed")
        
        # Step 4: Regulatory compliance consultation
        print("⚖️ Step 4: Consulting regulatory compliance experts...")
        regulatory_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.COMPLIANCE_REVIEW,
            query="What regulatory requirements apply to AI in healthcare?",
            user_preferences={
                "region": "US",
                "application_type": "clinical_support",
                "data_sensitivity": "high"
            },
            priority_level=PriorityLevel.URGENT,
            expected_outcomes=["regulatory_requirements", "compliance_checklist", "risk_assessment"]
        )
        
        regulatory_result = await expert_scenario.handle_consultation(regulatory_request)
        assert regulatory_result['success'] is True
        print("✅ Regulatory consultation completed")
        
        # Step 5: Change management consultation
        print("👥 Step 5: Consulting change management experts...")
        change_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.ORGANIZATIONAL_ADVISORY,
            query="How should we manage change when implementing AI in healthcare?",
            user_preferences={
                "organization_size": "large",
                "staff_count": 1000,
                "union_presence": True
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["change_strategy", "training_plan", "stakeholder_management"]
        )
        
        change_result = await expert_scenario.handle_consultation(change_request)
        assert change_result['success'] is True
        print("✅ Change management consultation completed")
        
        print("🎉 Complete healthcare administrator workflow successful!")
        
        return {
            "healthcare_analysis": healthcare_result,
            "literature_review": literature_result,
            "implementation_consultation": implementation_result,
            "regulatory_consultation": regulatory_result,
            "change_management_consultation": change_result
        }


class TestUserStoryCrossScenarioIntegration:
    """User story testing cross-scenario integration and complex workflows"""
    
    @pytest.mark.asyncio()
    async def test_mixed_scenario_workflow(self):
        """Test workflow using all three scenarios together"""
        expert_scenario = ExpertConsultationScenario()
        academic_scenario = AcademicResearchScenario()
        industry_scenario = IndustryAnalysisScenario()
        
        print("🌐 User Story: Cross-Scenario Integration - Smart City Project")
        
        # Step 1: Industry analysis for smart city market
        print("🏙️ Step 1: Smart city industry analysis...")
        smart_city_request = AnalysisRequest(
            industry_type=IndustryType.TECHNOLOGY,
            analysis_depth=AnalysisDepth.COMPREHENSIVE,
            focus_areas=["Smart Cities", "IoT", "Urban Planning", "Sustainability"],
            time_horizon="5-10 years",
            specific_questions=[
                "What is the smart city market size?",
                "What are the key technology trends?",
                "Who are the main players?",
                "What are the implementation challenges?"
            ],
            priority_level="HIGH"
        )
        
        industry_result = await industry_scenario.submit_analysis_request(smart_city_request)
        assert industry_result['success'] is True
        print("✅ Smart city analysis completed")
        
        # Step 2: Academic research on smart city technologies
        print("🎓 Step 2: Academic research on smart city technologies...")
        research_paper = ResearchPaper(
            title="Sustainable Smart City Technologies: A Comprehensive Analysis",
            abstract="This paper analyzes sustainable technologies for smart city implementation, focusing on IoT, AI, and renewable energy integration.",
            authors=["Dr. Jane Smith", "Prof. John Doe"],
            keywords=["smart cities", "IoT", "sustainability", "AI", "urban planning"],
            research_type=ResearchType.THEORETICAL_RESEARCH,
            academic_standard=AcademicStandard.PEER_REVIEWED,
            content="Full research content..."
        )
        
        paper_result = await academic_scenario.submit_research_paper(research_paper)
        assert paper_result['success'] is True
        print("✅ Research paper submitted")
        
        # Step 3: Technical consultation on smart city architecture
        print("🔧 Step 3: Technical architecture consultation...")
        tech_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.TECHNICAL_REVIEW,
            query="What architecture should we use for our smart city platform?",
            user_preferences={
                "scale": "city_wide",
                "technologies": ["IoT", "AI", "edge_computing"],
                "requirements": ["scalability", "security", "interoperability"]
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["architecture_design", "technology_stack", "integration_plan"]
        )
        
        tech_result = await expert_scenario.handle_consultation(tech_request)
        assert tech_result['success'] is True
        print("✅ Technical consultation completed")
        
        # Step 4: Policy and governance consultation
        print="🏛️ Step 4: Policy and governance consultation..."
        policy_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.POLICY_ADVISORY,
            query="What policies should govern smart city data collection and usage?",
            user_preferences={
                "jurisdiction": "municipal",
                "data_types": ["citizen_data", "sensor_data", "operational_data"],
                "stakeholders": ["citizens", "businesses", "government"]
            },
            priority_level=PriorityLevel.HIGH,
            expected_outcomes=["policy_framework", "governance_model", "privacy_protections"]
        )
        
        policy_result = await expert_scenario.handle_consultation(policy_request)
        assert policy_result['success'] is True
        print("✅ Policy consultation completed")
        
        # Step 5: Sustainability consultation
        print="🌱 Step 5: Sustainability consultation..."
        sustainability_request = ExpertConsultationRequest(
            consultation_type=ConsultationType.STRATEGIC_ADVISORY,
            query="How can we ensure our smart city project is sustainable?",
            user_preferences={
                "sustainability_goals": ["carbon_neutral", "renewable_energy", "circular_economy"],
                "timeline": "10_years",
                "budget_constraints": "moderate"
            },
            priority_level=PriorityLevel.MEDIUM,
            expected_outcomes=["sustainability_strategy", "implementation_plan", "metrics"]
        )
        
        sustainability_result = await expert_scenario.handle_consultation(sustainability_request)
        assert sustainability_result['success'] is True
        print("✅ Sustainability consultation completed")
        
        print("🎉 Complete cross-scenario workflow successful!")
        
        return {
            "industry_analysis": industry_result,
            "research_paper": paper_result,
            "technical_consultation": tech_result,
            "policy_consultation": policy_result,
            "sustainability_consultation": sustainability_result
        }


class TestUserStoryPerformanceAndReliability:
    """Test performance and reliability of user workflows"""
    
    @pytest.mark.asyncio()
    async def test_concurrent_user_workflows(self):
        """Test multiple concurrent user workflows"""
        import time
        
        print("🔄 Testing concurrent user workflows...")
        
        start_time = time.time()
        
        # Create multiple workflow tasks
        tasks = [
            TestUserStoryAcademicResearcher().test_complete_research_workflow(),
            TestUserStoryStartupFounder().test_complete_startup_workflow(),
            TestUserStoryHealthcareAdministrator().test_complete_healthcare_workflow(),
            TestUserStoryCrossScenarioIntegration().test_mixed_scenario_workflow()
        ]
        
        # Run all workflows concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check that all workflows completed successfully
        successful_workflows = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_workflows) == len(tasks), f"Some workflows failed: {results}"
        
        print(f"✅ All {len(tasks)} concurrent workflows completed successfully")
        print(f"⏱️ Total time: {total_time:.2f} seconds")
        print(f"⏱️ Average time per workflow: {total_time/len(tasks):.2f} seconds")
        
        # Performance check (should complete within 120 seconds)
        assert total_time < 120.0, f"Concurrent workflows took {total_time:.2f} seconds, expected < 120 seconds"
        
        return {
            "total_workflows": len(tasks),
            "successful_workflows": len(successful_workflows),
            "total_time": total_time,
            "average_time": total_time / len(tasks),
            "results": results
        }


# Test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])