#!/usr/bin/env python3
"""Phase 4.2: Academic Research Scenario Test
Test research report generation and multi-angle analysis
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_academic_research_scenario():
    """Test academic research scenario with comprehensive validation"""
    try:
        from src.core_services.academic_research_scenario import (
            AcademicResearchScenario,
            ResearchPaper,
            ResearchType,
        )
        
        print("Phase 4.2: Academic Research Scenario Test")
        print("=" * 60)
        
        # Create scenario
        scenario = AcademicResearchScenario()
        print("[OK] AcademicResearchScenario initialized")
        
        # Test 1: Create comprehensive research paper
        print("\nTest 1: Creating comprehensive research paper...")
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
        print("[OK] Comprehensive research paper created")
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
            for i, reviewer in enumerate(selected_reviewers[:3]):  # Show first 3
                print(f"   - Reviewer {i+1}: {reviewer['name']} ({reviewer['experience_level']})")
                print(f"     Specializations: {', '.join(reviewer['specializations'][:2])}")
            
            # Test 4: Peer review session creation
            print("\nTest 4: Peer review session creation...")
            session_result = await scenario._create_peer_review_session(paper, reviewer_selection)
            print("[OK] Peer review session created")
            print(f"   - Session ID: {session_result['session_id']}")
            print(f"   - Success: {session_result['success']}")
            
            # Test 5: Peer review generation
            print("\nTest 5: Peer review generation...")
            peer_reviews = await scenario._conduct_peer_review(session_result['session_id'], paper)
            print("[OK] Peer reviews generated")
            print(f"   - Generated {len(peer_reviews)} peer reviews")
            
            for i, review in enumerate(peer_reviews[:2]):  # Show first 2
                print(f"   - Review {i+1}: {review.reviewer_name}")
                print(f"     Recommendation: {review.recommendation}")
                print(f"     Confidence: {review.confidence_score:.2f}")
                print(f"     Strengths: {len(review.strengths)} points")
                print(f"     Suggestions: {len(review.suggestions)} points")
        
        # Test 6: Academic quality assessment
        print("\nTest 6: Academic quality assessment...")
        academic_assessment = await scenario._academic_quality_assessment(paper, peer_reviews)
        print("[OK] Academic quality assessment completed")
        print(f"   - Overall score: {academic_assessment['overall_score']:.2f}")
        print(f"   - Recommendation: {academic_assessment['recommendation']}")
        print(f"   - Confidence level: {academic_assessment['confidence_level']:.2f}")
        
        # Test 7: Research synthesis
        print("\nTest 7: Research synthesis...")
        research_synthesis = await scenario._generate_research_synthesis(paper, peer_reviews, academic_assessment)
        print("[OK] Research synthesis generated")
        print(f"   - Synthesis ID: {research_synthesis.synthesis_id}")
        print(f"   - Key findings: {len(research_synthesis.key_findings)}")
        print(f"   - Research gaps: {len(research_synthesis.research_gaps)}")
        print(f"   - Future directions: {len(research_synthesis.future_directions)}")
        print(f"   - Practical implications: {len(research_synthesis.practical_implications)}")
        
        # Test 8: Research report generation
        print("\nTest 8: Research report generation...")
        research_report = await scenario._generate_research_report(paper, peer_reviews, research_synthesis)
        print("[OK] Research report generated")
        print(f"   - Report ID: {research_report['report_id']}")
        print(f"   - Report URL: {research_report['report_url']}")
        print(f"   - Summary: {research_report['report_summary'][:100]}...")
        
        # Test 9: Literature review
        print("\nTest 9: Literature review...")
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
        
        # Test 10: Complete research paper submission workflow
        print("\nTest 10: Complete research paper submission workflow...")
        start_time = datetime.now()
        complete_result = await scenario.submit_research_paper(paper)
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print("[OK] Complete workflow executed")
        print(f"   - Success: {complete_result['success']}")
        print(f"   - Paper ID: {complete_result['paper_id']}")
        print(f"   - Session ID: {complete_result['session_id']}")
        print(f"   - Total reviewers: {complete_result['metadata']['total_reviewers']}")
        print(f"   - Recommendation: {complete_result['recommendation']}")
        print(f"   - Processing time: {processing_time:.2f} seconds")
        
        # Test 11: Research statistics
        print("\nTest 11: Research statistics...")
        stats = scenario.get_research_statistics()
        print("[OK] Research statistics retrieved")
        print(f"   - Total papers submitted: {stats['total_papers_submitted']}")
        print(f"   - Papers accepted: {stats['papers_accepted']}")
        print(f"   - Acceptance rate: {stats['acceptance_rate']:.2%}")
        print(f"   - Average assessment score: {stats['average_assessment_score']:.2f}")
        
        # Performance metrics
        print("\nPerformance Metrics:")
        print(f"   - Total execution time: {processing_time:.2f} seconds")
        if len(peer_reviews) > 0:
            print(f"   - Average time per reviewer: {processing_time/len(peer_reviews):.2f} seconds")
        print(f"   - Report generation efficiency: {'High' if processing_time < 30 else 'Medium'}")
        
        # Validation results
        print("\nValidation Results:")
        print(f"   - Academic standards compliance: {'[OK]' if assessment['meets_standards'] else '[FAIL]'}")
        print(f"   - Peer review process: {'[OK]' if len(peer_reviews) >= 3 else '[FAIL]'}")
        print(f"   - Quality assessment: {'[OK]' if academic_assessment['overall_score'] >= 0.7 else '[FAIL]'}")
        print(f"   - Report generation: {'[OK]' if research_report['report_id'] else '[FAIL]'}")
        print(f"   - Literature review: {'[OK]' if literature_review['success'] else '[FAIL]'}")
        
        # Calculate overall score
        validation_checks = [
            assessment['meets_standards'],
            len(peer_reviews) >= 3,
            academic_assessment['overall_score'] >= 0.7,
            bool(research_report['report_id']),
            literature_review['success']
        ]
        overall_score = sum(validation_checks) / len(validation_checks)
        
        print(f"\nOverall Test Score: {overall_score:.1%}")
        
        if overall_score >= 0.8:
            print("PASSED: Phase 4.2 - Academic Research Scenario Test")
            return True
        else:
            print("FAILED: Phase 4.2 - Academic Research Scenario Test")
            return False
        
    except Exception as e:
        print(f"FAILED: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    async def main():
        print("DAIP-LIVE Academic Research Scenario Test Suite")
        print("=" * 60)
        
        # Run main test
        main_test_passed = await test_academic_research_scenario()
        
        # Final result
        print("\n" + "=" * 60)
        if main_test_passed:
            print("PASSED: Academic Research Scenario is ready!")
            sys.exit(0)
        else:
            print("FAILED: Academic Research Scenario needs attention")
            sys.exit(1)
    
    asyncio.run(main())