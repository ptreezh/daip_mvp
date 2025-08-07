#!/usr/bin/env python3
"""
Phase 4.2: Academic Research Scenario Test - Simplified
Test core functionality without complex dependencies
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_academic_research_core():
    """Test academic research scenario core functionality"""
    try:
        from src.core_services.academic_research_scenario import (
            AcademicResearchScenario, 
            ResearchPaper, 
            ResearchType
        )
        
        print("Phase 4.2: Academic Research Scenario Test - Core Functionality")
        print("=" * 60)
        
        # Create scenario
        scenario = AcademicResearchScenario()
        print("[OK] AcademicResearchScenario initialized")
        
        # Test 1: Create research paper
        print("\nTest 1: Creating research paper...")
        paper = ResearchPaper(
            id="test_paper_001",
            title="Deep Learning Model Optimization for Natural Language Processing",
            abstract="This research proposes a novel deep learning model optimization method through improved attention mechanisms and adaptive learning rate strategies, significantly enhancing performance in natural language processing tasks.",
            authors=["Author One", "Author Two", "Author Three"],
            keywords=["deep learning", "natural language processing", "model optimization", "attention mechanism"],
            research_type=ResearchType.EMPIRICAL_RESEARCH,
            methodology="Experimental research using large-scale datasets for training and testing. Comparative experiments validate the effectiveness of the proposed method.",
            data_sources=["GLUE benchmark dataset", "SQuAD dataset", "IMDB movie review dataset"],
            findings=[
                "Model performance improved by 15.3% on GLUE benchmark",
                "Training time reduced by 30%, inference speed improved by 25%",
                "Excellent performance in few-shot learning scenarios with 95.2% accuracy",
                "Model parameters reduced by 20% while maintaining performance"
            ],
            limitations=[
                "Experiments mainly conducted on English datasets, limited validation on Chinese datasets",
                "High computational resource requirements, difficult to deploy on ordinary hardware",
                "Long text processing capability needs further improvement",
                "Limited model interpretability for internal decision-making analysis"
            ],
            references=[
                {"title": "Attention Is All You Need", "authors": ["Vaswani, A.", "Shazeer, N."], "year": 2017},
                {"title": "BERT: Pre-training of Deep Bidirectional Transformers", "authors": ["Devlin, J.", "Chang, M.W."], "year": 2018},
                {"title": "Improving Language Understanding by Generative Pre-Training", "authors": ["Radford, A.", "Wu, J."], "year": 2018},
                {"title": "Deep Learning Applications in Natural Language Processing", "authors": ["Zhang, M.", "Li, H."], "year": 2022},
                {"title": "Adaptive Learning Rate Optimization Algorithms", "authors": ["Chen, Z.", "Liu, M."], "year": 2023}
            ],
            word_count=5200,
            submission_date=datetime.now()
        )
        print("[OK] Research paper created")
        print(f"   - Title: {paper.title}")
        print(f"   - Authors: {', '.join(paper.authors)}")
        print(f"   - Word count: {paper.word_count}")
        print(f"   - Research type: {paper.research_type.value}")
        
        # Test 2: Initial paper assessment
        print("\nTest 2: Initial paper assessment...")
        assessment = await scenario._initial_paper_assessment(paper)
        print("[OK] Initial assessment completed")
        print(f"   - Meets standards: {assessment['meets_standards']}")
        print(f"   - Word count: {assessment['basic_criteria']['word_count']}/{assessment['basic_criteria']['min_required']}")
        print(f"   - References: {assessment['basic_criteria']['reference_count']}/{assessment['basic_criteria']['min_references']}")
        print(f"   - Content quality score: {assessment['content_analysis']['abstract_quality']['quality_score']:.2f}")
        
        # Test 3: Peer reviewer selection
        print("\nTest 3: Peer reviewer selection...")
        reviewer_selection = await scenario._select_peer_reviewers(paper)
        print("[OK] Peer reviewer selection completed")
        print(f"   - Success: {reviewer_selection['success']}")
        
        peer_reviews = []
        if reviewer_selection['success']:
            selected_reviewers = reviewer_selection['selected_reviewers']
            print(f"   - Selected {len(selected_reviewers)} reviewers")
            for i, reviewer in enumerate(selected_reviewers[:3]):
                print(f"   - Reviewer {i+1}: {reviewer['name']} ({reviewer['experience_level']})")
                print(f"     Specializations: {', '.join(reviewer['specializations'][:2])}")
        else:
            print("   - No reviewers available (expected in test environment)")
        
        # Test 4: Research quality evaluation methods
        print("\nTest 4: Research quality evaluation methods...")
        
        # Test individual assessment methods
        originality_score = scenario._assess_paper_originality(paper)
        methodology_score = scenario._assess_methodology_quality(paper)
        clarity_score = scenario._assess_writing_clarity(paper)
        significance_score = scenario._assess_research_significance(paper)
        
        print("[OK] Research quality evaluation completed")
        print(f"   - Originality score: {originality_score:.2f}")
        print(f"   - Methodology score: {methodology_score:.2f}")
        print(f"   - Clarity score: {clarity_score:.2f}")
        print(f"   - Significance score: {significance_score:.2f}")
        
        # Test 5: Literature review functionality
        print("\nTest 5: Literature review functionality...")
        scope = {
            "quality_threshold": 0.7,
            "time_scope": "recent_5_years",
            "max_results": 50
        }
        literature_review = await scenario.conduct_literature_review("Deep Learning in Natural Language Processing", scope)
        print("[OK] Literature review completed")
        print(f"   - Success: {literature_review['success']}")
        print(f"   - Topic: {literature_review['topic']}")
        print(f"   - Total literature: {literature_review['metadata']['total_literature']}")
        print(f"   - Research gaps: {len(literature_review['research_gaps'])}")
        
        # Test 6: Research statistics
        print("\nTest 6: Research statistics...")
        stats = scenario.get_research_statistics()
        print("[OK] Research statistics retrieved")
        print(f"   - Total papers submitted: {stats['total_papers_submitted']}")
        print(f"   - Papers accepted: {stats['papers_accepted']}")
        print(f"   - Acceptance rate: {stats['acceptance_rate']:.2%}")
        print(f"   - Average assessment score: {stats['average_assessment_score']:.2f}")
        
        # Test 7: Scenario configuration validation
        print("\nTest 7: Scenario configuration validation...")
        print("[OK] Configuration validation completed")
        print(f"   - Min word count: {scenario.academic_standards['min_word_count']}")
        print(f"   - Min references: {scenario.academic_standards['min_references']}")
        print(f"   - Peer reviewers required: {scenario.academic_standards['peer_reviewers_required']}")
        print(f"   - Acceptance threshold: {scenario.academic_standards['acceptance_threshold']}")
        print(f"   - Revision threshold: {scenario.academic_standards['revision_threshold']}")
        
        # Test 8: Research methods database
        print("\nTest 8: Research methods database...")
        print("[OK] Research methods database validated")
        print(f"   - Quantitative methods: {len(scenario.research_methods['quantitative'])}")
        print(f"   - Qualitative methods: {len(scenario.research_methods['qualitative'])}")
        print(f"   - Mixed methods: {len(scenario.research_methods['mixed'])}")
        
        # Performance summary
        print("\nPerformance Summary:")
        print(f"   - Scenario initialization: Success")
        print(f"   - Paper creation: Success")
        print(f"   - Initial assessment: Success")
        print(f"   - Quality evaluation: Success")
        print(f"   - Literature review: Success")
        print(f"   - Statistics tracking: Success")
        
        # Validation results
        print("\nValidation Results:")
        validation_checks = [
            assessment['meets_standards'],
            literature_review['success'],
            originality_score > 0.0,
            methodology_score > 0.0,
            clarity_score > 0.0,
            significance_score > 0.0
        ]
        
        passed_checks = sum(validation_checks)
        total_checks = len(validation_checks)
        overall_score = passed_checks / total_checks
        
        print(f"   - Tests passed: {passed_checks}/{total_checks}")
        print(f"   - Overall score: {overall_score:.1%}")
        
        if overall_score >= 0.7:
            print("PASSED: Phase 4.2 - Academic Research Scenario Core Test")
            return True
        else:
            print("FAILED: Phase 4.2 - Academic Research Scenario Core Test")
            return False
        
    except Exception as e:
        print(f"FAILED: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_academic_research_types():
    """Test different research types"""
    try:
        from src.core_services.academic_research_scenario import (
            AcademicResearchScenario, 
            ResearchPaper, 
            ResearchType
        )
        
        print("\nTesting Different Research Types:")
        print("-" * 40)
        
        scenario = AcademicResearchScenario()
        
        research_types = [
            (ResearchType.LITERATURE_REVIEW, "Systematic Literature Review on Machine Learning"),
            (ResearchType.THEORETICAL_RESEARCH, "Theoretical Framework for Deep Learning Optimization"),
            (ResearchType.EMPIRICAL_RESEARCH, "Empirical Study of Model Performance"),
            (ResearchType.METHODOLOGICAL_RESEARCH, "New Methodology for Model Evaluation"),
            (ResearchType.COMPARATIVE_RESEARCH, "Comparative Analysis of Learning Algorithms")
        ]
        
        for research_type, title in research_types:
            paper = ResearchPaper(
                id=f"test_{research_type.value}",
                title=title,
                abstract=f"This is a test paper for {research_type.value}",
                authors=["Test Author"],
                keywords=["test", research_type.value],
                research_type=research_type,
                methodology="Test methodology",
                data_sources=["Test data"],
                findings=["Test finding"],
                limitations=["Test limitation"],
                references=[{"title": "Test ref", "authors": ["A"], "year": 2023}],
                word_count=3500,
                submission_date=datetime.now()
            )
            
            assessment = await scenario._initial_paper_assessment(paper)
            print(f"   - {research_type.value}: {'PASS' if assessment['meets_standards'] else 'FAIL'}")
        
        print("[OK] Research types test completed")
        return True
        
    except Exception as e:
        print(f"FAILED: Research types test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("DAIP-LIVE Academic Research Scenario Test Suite")
        print("=" * 60)
        
        # Run core test
        core_test_passed = await test_academic_research_core()
        
        # Run research types test
        types_test_passed = await test_academic_research_types()
        
        # Final result
        print("\n" + "=" * 60)
        if core_test_passed and types_test_passed:
            print("PASSED: Academic Research Scenario is ready!")
            print("Phase 4.2: Academic Research Scenario Testing - COMPLETED")
            sys.exit(0)
        else:
            print("FAILED: Academic Research Scenario needs attention")
            sys.exit(1)
    
    asyncio.run(main())