#!/usr/bin/env python3
"""V0.2.3 学术研究场景核心功能测试

测试文献检索、方法论指导、写作辅助和同行评议功能
"""

import asyncio
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core_services.virtual_team_service import VirtualTeamService
from src.memory_bank_tools import MemoryBankTools
from src.scenarios.enhanced_academic_research_scenario_complete import EnhancedAcademicResearchScenario


class TestV023AcademicResearch:
    """V0.2.3 学术研究场景测试"""
    
    @pytest.fixture()
    async def scenario(self):
        """创建测试场景实例"""
        memory_tools = MemoryBankTools()
        virtual_team_service = VirtualTeamService()
        scenario = EnhancedAcademicResearchScenario(memory_tools, virtual_team_service)
        await scenario.initialize_components()
        return scenario
    
    @pytest.mark.asyncio()
    async def test_start_research_project(self, scenario):
        """测试启动研究项目"""
        research_question = "How does artificial intelligence impact educational outcomes?"
        
        result = await scenario.start_research_project(
            research_question=research_question,
            domain="education",
            complexity="intermediate"
        )
        
        assert "project_id" in result
        assert result["research_question"] == research_question
        assert result["literature_found"] >= 0
        assert "next_steps" in result
        assert len(result["next_steps"]) > 0
        
        print(f"✅ Research project started: {result['project_id']}")
        print(f"   Literature found: {result['literature_found']}")
        print(f"   Top methodology: {result['top_methodology']}")
    
    @pytest.mark.asyncio()
    async def test_design_study(self, scenario):
        """测试研究设计"""
        # 先启动项目
        await scenario.start_research_project(
            "What are the effects of remote learning on student engagement?",
            "education",
            "intermediate"
        )
        
        # 设计研究
        result = await scenario.design_study("mixed_methods")
        
        assert "methodology" in result
        assert result["methodology"] == "mixed_methods"
        assert "study_design" in result
        assert "data_collection_methods" in result
        assert "timeline" in result
        assert "next_steps" in result
        
        print(f"✅ Study designed with methodology: {result['methodology']}")
        print(f"   Study design: {result['study_design']}")
        print(f"   Data collection: {result['data_collection_methods']}")
    
    @pytest.mark.asyncio()
    async def test_write_manuscript_section(self, scenario):
        """测试稿件写作"""
        # 先启动项目
        await scenario.start_research_project(
            "How do collaborative learning environments affect student performance?",
            "education",
            "intermediate"
        )
        
        # 测试生成模板
        template_result = await scenario.write_manuscript_section("abstract")
        
        assert "template" in template_result
        assert "message" in template_result
        
        print("✅ Abstract template generated")
        
        # 测试分析内容
        sample_abstract = """
        This study investigates the impact of collaborative learning environments on student performance 
        in higher education settings. Using a mixed-methods approach, we analyzed data from 200 students 
        across multiple courses. Results showed significant improvements in both academic performance and 
        student engagement. These findings suggest that collaborative learning can be an effective 
        pedagogical approach for enhancing educational outcomes.
        """
        
        analysis_result = await scenario.write_manuscript_section(
            "abstract", 
            sample_abstract,
            "journal_article"
        )
        
        assert "quality_score" in analysis_result
        assert "word_count" in analysis_result
        assert "strengths" in analysis_result
        assert "suggestions" in analysis_result
        assert analysis_result["quality_score"] > 0
        
        print(f"✅ Abstract analyzed - Quality score: {analysis_result['quality_score']}")
        print(f"   Word count: {analysis_result['word_count']}")
        print(f"   Strengths: {len(analysis_result['strengths'])}")
        print(f"   Suggestions: {len(analysis_result['suggestions'])}")
    
    @pytest.mark.asyncio()
    async def test_conduct_peer_review(self, scenario):
        """测试同行评议"""
        # 先启动项目并写作章节
        await scenario.start_research_project(
            "What is the effectiveness of gamification in online learning?",
            "education",
            "intermediate"
        )
        
        # 添加稿件章节
        sample_content = """
        This research examines the effectiveness of gamification elements in online learning platforms.
        Through a randomized controlled trial with 150 participants, we measured learning outcomes,
        engagement levels, and completion rates. The study found significant improvements in all
        measured variables when gamification elements were present.
        """
        
        await scenario.write_manuscript_section("abstract", sample_content)
        await scenario.write_manuscript_section("introduction", sample_content + " Extended introduction content.")
        
        # 进行同行评议
        review_result = await scenario.conduct_peer_review(num_reviewers=3)
        
        assert "num_reviewers" in review_result
        assert review_result["num_reviewers"] == 3
        assert "average_score" in review_result
        assert "final_decision" in review_result
        assert "strengths_identified" in review_result
        assert "weaknesses_identified" in review_result
        assert "suggestions_provided" in review_result
        
        print("✅ Peer review completed")
        print(f"   Average score: {review_result['average_score']}")
        print(f"   Decision: {review_result['final_decision']}")
        print(f"   Strengths identified: {review_result['strengths_identified']}")
        print(f"   Weaknesses identified: {review_result['weaknesses_identified']}")
    
    @pytest.mark.asyncio()
    async def test_project_status(self, scenario):
        """测试项目状态查询"""
        # 测试无项目状态
        status = await scenario.get_project_status()
        assert "message" in status
        
        # 启动项目后测试状态
        await scenario.start_research_project(
            "How does technology integration affect teaching practices?",
            "education",
            "advanced"
        )
        
        status = await scenario.get_project_status()
        
        assert "research_question" in status
        assert "domain" in status
        assert "status" in status
        assert "progress_indicators" in status
        assert "literature_search" in status["progress_indicators"]
        
        print("✅ Project status retrieved")
        print(f"   Status: {status['status']}")
        print(f"   Domain: {status['domain']}")
        print(f"   Progress indicators: {status['progress_indicators']}")
    
    @pytest.mark.asyncio()
    async def test_export_project_report(self, scenario):
        """测试项目报告导出"""
        # 创建完整的研究项目
        await scenario.start_research_project(
            "What are the benefits of personalized learning systems?",
            "education",
            "advanced"
        )
        
        await scenario.design_study("quantitative")
        
        sample_methodology = """
        This study employs a quantitative research design to investigate the benefits of personalized
        learning systems. A randomized controlled trial will be conducted with 300 participants
        across multiple educational institutions. Data will be collected through pre- and post-tests,
        learning analytics, and student surveys.
        """
        
        await scenario.write_manuscript_section("methodology", sample_methodology)
        
        # 导出报告
        report = await scenario.export_project_report()
        
        assert isinstance(report, str)
        assert len(report) > 100
        assert "Academic Research Project Report" in report
        assert "Project Overview" in report
        
        print("✅ Project report exported")
        print(f"   Report length: {len(report)} characters")
        print("   Report preview:")
        print(report[:300] + "...")
    
    @pytest.mark.asyncio()
    async def test_complete_research_workflow(self, scenario):
        """测试完整的研究工作流程"""
        print("\n🔬 Testing Complete Research Workflow")
        
        # 1. 启动研究项目
        print("1. Starting research project...")
        project_result = await scenario.start_research_project(
            "How does adaptive learning technology improve student outcomes in STEM education?",
            "education",
            "advanced"
        )
        assert "project_id" in project_result
        print(f"   ✅ Project started: {project_result['project_id']}")
        
        # 2. 设计研究
        print("2. Designing study...")
        design_result = await scenario.design_study("mixed_methods")
        assert "methodology" in design_result
        print(f"   ✅ Study designed with {design_result['methodology']}")
        
        # 3. 写作多个章节
        print("3. Writing manuscript sections...")
        
        sections_content = {
            "abstract": """
            This mixed-methods study investigates how adaptive learning technology improves student 
            outcomes in STEM education. Through a randomized controlled trial with 400 students and 
            follow-up interviews, we found significant improvements in learning outcomes, engagement, 
            and retention rates. The findings suggest that adaptive learning technology can be a 
            powerful tool for enhancing STEM education effectiveness.
            """,
            
            "introduction": """
            STEM education faces numerous challenges in the 21st century, including diverse learning 
            needs, varying skill levels, and the need for personalized instruction. Adaptive learning 
            technology has emerged as a promising solution to address these challenges by providing 
            personalized learning experiences tailored to individual student needs. This study 
            investigates the effectiveness of adaptive learning technology in improving student 
            outcomes in STEM education contexts.
            """,
            
            "methodology": """
            This study employed a mixed-methods research design combining quantitative and qualitative 
            approaches. The quantitative component involved a randomized controlled trial with 400 
            undergraduate STEM students across three universities. The qualitative component included 
            semi-structured interviews with 30 participants to gain deeper insights into their 
            experiences with adaptive learning technology.
            """
        }
        
        for section_type, content in sections_content.items():
            section_result = await scenario.write_manuscript_section(section_type, content)
            assert "quality_score" in section_result
            print(f"   ✅ {section_type.title()} written (Quality: {section_result['quality_score']:.2f})")
        
        # 4. 进行同行评议
        print("4. Conducting peer review...")
        review_result = await scenario.conduct_peer_review(num_reviewers=3)
        assert "final_decision" in review_result
        print(f"   ✅ Peer review completed (Decision: {review_result['final_decision']})")
        
        # 5. 检查项目状态
        print("5. Checking project status...")
        status = await scenario.get_project_status()
        assert status["status"] == "reviewed"
        print(f"   ✅ Project status: {status['status']}")
        
        # 6. 导出最终报告
        print("6. Exporting final report...")
        final_report = await scenario.export_project_report()
        assert len(final_report) > 1000
        print(f"   ✅ Final report exported ({len(final_report)} characters)")
        
        print("\n🎉 Complete research workflow test passed!")
        
        return {
            "project_id": project_result["project_id"],
            "methodology": design_result["methodology"],
            "sections_written": len(sections_content),
            "peer_review_decision": review_result["final_decision"],
            "final_status": status["status"],
            "report_length": len(final_report)
        }


async def run_tests():
    """运行所有测试"""
    print("🧪 Starting V0.2.3 Academic Research Scenario Tests")
    print("=" * 60)
    
    # 创建测试实例
    memory_tools = MemoryBankTools()
    virtual_team_service = VirtualTeamService()
    scenario = EnhancedAcademicResearchScenario(memory_tools, virtual_team_service)
    await scenario.initialize_components()
    
    test_instance = TestV023AcademicResearch()
    
    try:
        # 运行各项测试
        print("\n📚 Test 1: Start Research Project")
        await test_instance.test_start_research_project(scenario)
        
        print("\n🔬 Test 2: Design Study")
        await test_instance.test_design_study(scenario)
        
        print("\n✍️ Test 3: Write Manuscript Section")
        await test_instance.test_write_manuscript_section(scenario)
        
        print("\n👥 Test 4: Conduct Peer Review")
        await test_instance.test_conduct_peer_review(scenario)
        
        print("\n📊 Test 5: Project Status")
        await test_instance.test_project_status(scenario)
        
        print("\n📄 Test 6: Export Project Report")
        await test_instance.test_export_project_report(scenario)
        
        print("\n🔄 Test 7: Complete Research Workflow")
        workflow_result = await test_instance.test_complete_research_workflow(scenario)
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
        print("\n📈 Test Summary:")
        print(f"✅ Project ID: {workflow_result['project_id']}")
        print(f"✅ Methodology: {workflow_result['methodology']}")
        print(f"✅ Sections Written: {workflow_result['sections_written']}")
        print(f"✅ Peer Review Decision: {workflow_result['peer_review_decision']}")
        print(f"✅ Final Status: {workflow_result['final_status']}")
        print(f"✅ Report Length: {workflow_result['report_length']} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)