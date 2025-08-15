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
            title="基于深度学习的自然语言处理模型优化研究",
            abstract="本研究提出了一种新的深度学习模型优化方法，通过改进注意力机制和引入自适应学习率策略，显著提升了自然语言处理任务的性能。实验结果表明，该方法在多个基准数据集上均取得了优于现有方法的性能表现。",
            authors=["张三", "李四", "王五"],
            keywords=["深度学习", "自然语言处理", "模型优化", "注意力机制", "自适应学习率"],
            research_type=ResearchType.EMPIRICAL_RESEARCH,
            methodology="采用实验研究方法，使用大规模数据集进行训练和测试。通过对比实验验证所提方法的有效性，并使用统计方法分析结果的显著性。实验环境为Python 3.9，PyTorch 1.12，NVIDIA RTX 3090 GPU。",
            data_sources=["GLUE基准数据集", "SQuAD数据集", "IMDB电影评论数据集", "自定义中文文本数据集"],
            findings=[
                "模型在GLUE基准测试上平均性能提升15.3%",
                "训练时间减少30%，推理速度提升25%",
                "在小样本学习场景下表现优异，准确率达到95.2%",
                "模型参数量减少20%，但性能保持不变"
            ],
            limitations=[
                "实验主要在英文数据集上进行，中文数据集验证有限",
                "计算资源需求较高，在普通硬件上部署困难",
                "长文本处理能力有待进一步提升",
                "模型解释性不足，难以分析内部决策机制"
            ],
            references=[
                {"title": "Attention Is All You Need", "authors": ["Vaswani, A.", "Shazeer, N.", "Parmar, N."], "year": 2017},
                {"title": "BERT: Pre-training of Deep Bidirectional Transformers", "authors": ["Devlin, J.", "Chang, M.W.", "Lee, K."], "year": 2018},
                {"title": "Improving Language Understanding by Generative Pre-Training", "authors": ["Radford, A.", "Wu, J.", "Child, R."], "year": 2018},
                {"title": "深度学习在自然语言处理中的应用", "authors": ["张明", "李华", "王强"], "year": 2022},
                {"title": "自适应学习率优化算法研究", "authors": ["陈志", "刘敏", "赵丽"], "year": 2023}
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
        print("\n Test 2: Initial paper assessment...")
        assessment = await scenario._initial_paper_assessment(paper)
        print("[OK] Initial assessment completed")
        print(f"   - Meets standards: {assessment['meets_standards']}")
        print(f"   - Word count: {assessment['basic_criteria']['word_count']}/{assessment['basic_criteria']['min_required']}")
        print(f"   - References: {assessment['basic_criteria']['reference_count']}/{assessment['basic_criteria']['min_references']}")
        print(f"   - Content quality score: {assessment['content_analysis']['abstract_quality']['quality_score']:.2f}")
        
        # Test 3: Peer reviewer selection
        print("\n Test 3: Peer reviewer selection...")
        reviewer_selection = await scenario._select_peer_reviewers(paper)
        print("[OK] Peer reviewer selection completed")
        print(f"   - Success: {reviewer_selection['success']}")
        
        if reviewer_selection['success']:
            selected_reviewers = reviewer_selection['selected_reviewers']
            print(f"   - Selected {len(selected_reviewers)} reviewers")
            for i, reviewer in enumerate(selected_reviewers[:3]):  # Show first 3
                print(f"   - Reviewer {i+1}: {reviewer['name']} ({reviewer['experience_level']})")
                print(f"     Specializations: {', '.join(reviewer['specializations'][:2])}")
        
        # Test 4: Peer review session creation
        if reviewer_selection['success']:
            print("\n🏛️ Test 4: Peer review session creation...")
            session_result = await scenario._create_peer_review_session(paper, reviewer_selection)
            print("[OK] Peer review session created")
            print(f"   - Session ID: {session_result['session_id']}")
            print(f"   - Success: {session_result['success']}")
            
            # Test 5: Peer review generation
            print("\n📋 Test 5: Peer review generation...")
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
        print("\n🎯 Test 6: Academic quality assessment...")
        academic_assessment = await scenario._academic_quality_assessment(paper, peer_reviews)
        print("[OK] Academic quality assessment completed")
        print(f"   - Overall score: {academic_assessment['overall_score']:.2f}")
        print(f"   - Recommendation: {academic_assessment['recommendation']}")
        print(f"   - Confidence level: {academic_assessment['confidence_level']:.2f}")
        
        # Test 7: Research synthesis
        print("\n🔬 Test 7: Research synthesis...")
        research_synthesis = await scenario._generate_research_synthesis(paper, peer_reviews, academic_assessment)
        print("[OK] Research synthesis generated")
        print(f"   - Synthesis ID: {research_synthesis.synthesis_id}")
        print(f"   - Key findings: {len(research_synthesis.key_findings)}")
        print(f"   - Research gaps: {len(research_synthesis.research_gaps)}")
        print(f"   - Future directions: {len(research_synthesis.future_directions)}")
        print(f"   - Practical implications: {len(research_synthesis.practical_implications)}")
        
        # Test 8: Research report generation
        print("\n📊 Test 8: Research report generation...")
        research_report = await scenario._generate_research_report(paper, peer_reviews, research_synthesis)
        print("[OK] Research report generated")
        print(f"   - Report ID: {research_report['report_id']}")
        print(f"   - Report URL: {research_report['report_url']}")
        print(f"   - Summary: {research_report['report_summary'][:100]}...")
        
        # Test 9: Literature review
        print("\n📚 Test 9: Literature review...")
        scope = {
            "quality_threshold": 0.7,
            "time_scope": "recent_5_years",
            "max_results": 50
        }
        literature_review = await scenario.conduct_literature_review("深度学习在自然语言处理中的应用", scope)
        print("[OK] Literature review completed")
        print(f"   - Success: {literature_review['success']}")
        print(f"   - Topic: {literature_review['topic']}")
        print(f"   - Total literature: {literature_review['metadata']['total_literature']}")
        print(f"   - Research gaps: {len(literature_review['research_gaps'])}")
        
        # Test 10: Complete research paper submission workflow
        print("\n🚀 Test 10: Complete research paper submission workflow...")
        complete_result = await scenario.submit_research_paper(paper)
        print("[OK] Complete workflow executed")
        print(f"   - Success: {complete_result['success']}")
        print(f"   - Paper ID: {complete_result['paper_id']}")
        print(f"   - Session ID: {complete_result['session_id']}")
        print(f"   - Total reviewers: {complete_result['metadata']['total_reviewers']}")
        print(f"   - Recommendation: {complete_result['recommendation']}")
        print(f"   - Processing time: {complete_result['metadata']['processing_time']:.2f} seconds")
        
        # Test 11: Research statistics
        print("\n📈 Test 11: Research statistics...")
        stats = scenario.get_research_statistics()
        print("[OK] Research statistics retrieved")
        print(f"   - Total papers submitted: {stats['total_papers_submitted']}")
        print(f"   - Papers accepted: {stats['papers_accepted']}")
        print(f"   - Acceptance rate: {stats['acceptance_rate']:.2%}")
        print(f"   - Average assessment score: {stats['average_assessment_score']:.2f}")
        
        # Performance metrics
        print("\n⏱️ Performance Metrics:")
        print(f"   - Total execution time: {complete_result['metadata']['processing_time']:.2f} seconds")
        print(f"   - Average time per reviewer: {complete_result['metadata']['processing_time']/len(peer_reviews):.2f} seconds")
        print(f"   - Report generation efficiency: {'High' if complete_result['metadata']['processing_time'] < 30 else 'Medium'}")
        
        # Validation results
        print("\n🎯 Validation Results:")
        print(f"   - Academic standards compliance: {'✅' if assessment['meets_standards'] else '❌'}")
        print(f"   - Peer review process: {'✅' if len(peer_reviews) >= 3 else '❌'}")
        print(f"   - Quality assessment: {'✅' if academic_assessment['overall_score'] >= 0.7 else '❌'}")
        print(f"   - Report generation: {'✅' if research_report['report_id'] else '❌'}")
        print(f"   - Literature review: {'✅' if literature_review['success'] else '❌'}")
        
        # Calculate overall score
        validation_checks = [
            assessment['meets_standards'],
            len(peer_reviews) >= 3,
            academic_assessment['overall_score'] >= 0.7,
            bool(research_report['report_id']),
            literature_review['success']
        ]
        overall_score = sum(validation_checks) / len(validation_checks)
        
        print(f"\n🏆 Overall Test Score: {overall_score:.1%}")
        
        if overall_score >= 0.8:
            print("🎉 Phase 4.2: Academic Research Scenario Test - PASSED")
            return True
        else:
            print("❌ Phase 4.2: Academic Research Scenario Test - FAILED")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_edge_cases():
    """Test edge cases and error handling"""
    try:
        from src.core_services.academic_research_scenario import AcademicResearchScenario, ResearchPaper, ResearchType
        
        print("\n🧪 Edge Cases Test:")
        print("-" * 40)
        
        scenario = AcademicResearchScenario()
        
        # Test 1: Paper with minimal content
        print("\n1. Testing minimal content paper...")
        minimal_paper = ResearchPaper(
            id="minimal_001",
            title="Minimal",
            abstract="Short abstract",
            authors=["Author"],
            keywords=["test"],
            research_type=ResearchType.THEORETICAL_RESEARCH,
            methodology="Simple",
            data_sources=["Test"],
            findings=["Finding"],
            limitations=["Limitation"],
            references=[{"title": "Ref", "authors": ["A"], "year": 2023}],
            word_count=100,  # Below minimum
            submission_date=datetime.now()
        )
        
        assessment = await scenario._initial_paper_assessment(minimal_paper)
        print(f"   - Meets standards: {assessment['meets_standards']}")
        print(f"   - Recommendations: {len(assessment['recommendations'])}")
        
        # Test 2: Empty literature review
        print("\n2. Testing empty literature review...")
        empty_scope = {"quality_threshold": 1.0, "max_results": 0}
        empty_review = await scenario.conduct_literature_review("nonexistent_topic", empty_scope)
        print(f"   - Success: {empty_review['success']}")
        print(f"   - Total literature: {empty_review['metadata']['total_literature']}")
        
        print("[OK] Edge cases test completed")
        return True
        
    except Exception as e:
        print(f"❌ Edge cases test failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("DAIP-LIVE Academic Research Scenario Test Suite")
        print("=" * 60)
        
        # Run main test
        main_test_passed = await test_academic_research_scenario()
        
        # Run edge cases test
        edge_test_passed = await test_edge_cases()
        
        # Final result
        print("\n" + "=" * 60)
        if main_test_passed and edge_test_passed:
            print("🎉 ALL TESTS PASSED - Academic Research Scenario is ready!")
            sys.exit(0)
        else:
            print("❌ SOME TESTS FAILED - Academic Research Scenario needs attention")
            sys.exit(1)
    
    asyncio.run(main())