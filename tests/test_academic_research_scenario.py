#!/usr/bin/env python3
"""V0.2.3 - 学术研究场景核心功能测试

测试学术研究场景的完整功能实现
"""

import asyncio
import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest

# 设置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAcademicResearchScenario:
    """学术研究场景测试"""
    
    @pytest.fixture()
    def mock_role_manager(self):
        """模拟角色管理器"""
        from src.core_services.role_manager import Role, RoleManager
        
        mock_manager = Mock(spec=RoleManager)
        
        # 创建测试角色
        test_roles = [
            Role(
                id="education_expert",
                name="教育学专家",
                description="专业的教育学研究专家",
                system_prompt="你是一位教育学专家，具有深厚的教育理论基础。",
                capabilities=["教育理论", "教学方法", "课程设计"]
            ),
            Role(
                id="tech_expert", 
                name="技术专家",
                description="专业的技术研究专家",
                system_prompt="你是一位技术专家，具有丰富的技术研发经验。",
                capabilities=["技术分析", "系统设计", "创新研究"]
            ),
            Role(
                id="psychology_expert",
                name="心理学家",
                description="专业的心理学研究专家", 
                system_prompt="你是一位心理学家，专注于认知和行为研究。",
                capabilities=["认知分析", "行为研究", "心理评估"]
            )
        ]
        
        mock_manager.list_roles.return_value = test_roles
        return mock_manager
    
    @pytest.fixture()
    def mock_workflow_result(self):
        """模拟工作流结果"""
        return {
            "success": True,
            "topic": "AI在教育中的应用",
            "synthesis": {
                "main_conclusion": "AI技术在教育领域具有巨大潜力，但需要谨慎应用",
                "detailed_analysis": "通过多视角分析，我们发现AI在个性化学习、智能评估等方面具有显著优势",
                "key_findings": "AI可以提高教学效率，但也带来了隐私和伦理挑战",
                "implications": "需要建立相应的规范和标准来指导AI在教育中的应用",
                "recommendations": "建议逐步推进AI技术在教育中的应用，同时加强相关研究"
            },
            "key_insights": [
                "个性化学习是AI在教育中最有前景的应用方向",
                "教师角色将从知识传授者转变为学习引导者",
                "数据隐私和算法公平性是需要重点关注的问题"
            ],
            "expert_contributions": {
                "教育学专家": {
                    "analysis": "从教育学角度，AI技术可以实现真正的因材施教",
                    "viewpoint": "AI应该作为教育的辅助工具，而不是替代传统教学"
                },
                "技术专家": {
                    "analysis": "当前AI技术已经足够成熟，可以支持大规模教育应用",
                    "viewpoint": "技术实现不是问题，关键是如何与教育理念相结合"
                },
                "心理学家": {
                    "analysis": "AI系统需要考虑学习者的认知特点和心理需求",
                    "viewpoint": "个性化学习算法应该基于认知科学的研究成果"
                }
            },
            "quality_score": 0.85,
            "execution_id": "test_execution_123"
        }
    
    async def test_academic_role_selector(self, mock_role_manager):
        """测试学术角色选择器"""
        from src.scenarios.academic_research_scenario import AcademicRoleSelector
        
        selector = AcademicRoleSelector(mock_role_manager)
        
        # 测试角色选择
        selected_roles = await selector.select_academic_roles("AI在教育中的应用", 3)
        
        # 验证结果
        assert len(selected_roles) == 3
        assert all(hasattr(role, 'name') for role in selected_roles)
        assert all(hasattr(role, 'description') for role in selected_roles)
        
        logger.info(f"Selected roles: {[role.name for role in selected_roles]}")
    
    async def test_academic_report_generator(self, mock_workflow_result):
        """测试学术报告生成器"""
        from src.scenarios.academic_research_scenario import AcademicReportGenerator, AcademicResearchConfig
        
        generator = AcademicReportGenerator()
        config = AcademicResearchConfig(target_word_count=5000)
        
        # 生成学术报告
        report = await generator.generate_academic_report(mock_workflow_result, config)
        
        # 验证报告结构
        assert report.title
        assert report.abstract
        assert report.introduction
        assert report.analysis
        assert report.findings
        assert report.conclusion
        assert len(report.references) > 0
        assert report.word_count > 0
        assert 0 <= report.quality_score <= 1
        
        logger.info(f"Generated report: {report.word_count} words, quality: {report.quality_score}")
    
    async def test_academic_research_scenario_integration(self, mock_role_manager):
        """测试学术研究场景集成"""
        from src.scenarios.academic_research_scenario import AcademicResearchConfig, AcademicResearchScenario
        
        # 模拟依赖
        with patch('src.scenarios.academic_research_scenario.MultiPerspectiveSynthesisWorkflow') as mock_workflow_class:
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "topic": "AI在教育中的应用",
                "synthesis": {"main_conclusion": "测试结论"},
                "key_insights": ["测试洞察1", "测试洞察2"],
                "expert_contributions": {"专家1": {"analysis": "测试分析"}},
                "quality_score": 0.8,
                "execution_id": "test_123"
            }
            mock_workflow_class.return_value = mock_workflow
            
            # 创建场景实例
            scenario = AcademicResearchScenario()
            scenario.role_manager = mock_role_manager
            scenario.knowledge_persistence = None  # 禁用知识持久化以简化测试
            
            # 执行学术研究
            config = AcademicResearchConfig(target_word_count=3000, quality_threshold=0.7)
            result = await scenario.conduct_academic_research("AI在教育中的应用", config)
            
            # 验证结果
            assert result["success"] == True
            assert "research_id" in result
            assert "academic_report" in result
            assert "synthesis_result" in result
            assert "selected_roles" in result
            assert "quality_assessment" in result
            assert "progress" in result
            
            # 验证报告内容
            report = result["academic_report"]
            assert report["word_count"] > 0
            assert report["title"]
            assert report["abstract"]
            
            logger.info(f"Research completed: {result['research_id']}")
            logger.info(f"Report word count: {report['word_count']}")
    
    async def test_quality_assessment(self):
        """测试质量评估功能"""
        from src.scenarios.academic_research_scenario import (
            AcademicReport,
            AcademicResearchConfig,
            AcademicResearchScenario,
        )
        
        scenario = AcademicResearchScenario()
        config = AcademicResearchConfig()
        
        # 创建测试报告
        test_report = AcademicReport(
            title="测试报告",
            abstract="这是一个测试摘要，包含了研究的主要内容和发现。" * 10,
            introduction="这是引言部分，介绍了研究背景和目标。" * 20,
            literature_review="这是文献综述部分。" * 15,
            methodology="这是方法论部分。" * 10,
            analysis="这是分析部分，包含了详细的数据分析和讨论。" * 50,
            findings="这是研究发现部分。" * 25,
            discussion="这是讨论部分。" * 30,
            conclusion="这是结论部分。" * 15,
            references=["参考文献1", "参考文献2", "参考文献3", "参考文献4", "参考文献5"],
            appendices={},
            metadata={},
            word_count=5000,
            quality_score=0.8
        )
        
        # 评估质量
        assessment = await scenario._assess_report_quality(test_report, config)
        
        # 验证评估结果
        assert "overall_score" in assessment
        assert "word_count_score" in assessment
        assert "structure_score" in assessment
        assert "content_depth_score" in assessment
        assert "academic_rigor_score" in assessment
        assert "coherence_score" in assessment
        assert "meets_threshold" in assessment
        
        assert 0 <= assessment["overall_score"] <= 1
        
        logger.info(f"Quality assessment: {assessment['overall_score']:.2f}")
    
    async def test_report_refinement(self, mock_workflow_result):
        """测试报告优化功能"""
        from src.scenarios.academic_research_scenario import (
            AcademicReport,
            AcademicResearchConfig,
            AcademicResearchScenario,
        )
        
        scenario = AcademicResearchScenario()
        config = AcademicResearchConfig()
        
        # 创建需要优化的报告
        initial_report = AcademicReport(
            title="初始报告",
            abstract="简短摘要",
            introduction="简短引言",
            literature_review="",
            methodology="",
            analysis="简短分析",
            findings="简短发现",
            discussion="简短讨论",
            conclusion="简短结论",
            references=["参考文献1"],
            appendices={},
            metadata={},
            word_count=500,  # 字数不足
            quality_score=0.6  # 质量不达标
        )
        
        quality_assessment = {
            "overall_score": 0.6,
            "word_count_score": 0.5,
            "content_depth_score": 0.4,
            "academic_rigor_score": 0.5
        }
        
        # 执行优化
        refined_report = await scenario._refine_academic_report(
            initial_report, mock_workflow_result, config, quality_assessment
        )
        
        # 验证优化结果
        assert refined_report.word_count > initial_report.word_count
        assert len(refined_report.analysis) > len(initial_report.analysis)
        assert len(refined_report.references) > len(initial_report.references)
        
        logger.info(f"Report refined: {initial_report.word_count} -> {refined_report.word_count} words")


class TestAcademicResearchIntegration:
    """学术研究场景集成测试"""
    
    async def test_end_to_end_academic_research(self):
        """端到端学术研究测试"""
        from src.scenarios.academic_research_scenario import conduct_academic_research
        
        # 模拟所有依赖
        with patch('src.scenarios.academic_research_scenario.RoleManager') as mock_role_manager_class, \
             patch('src.scenarios.academic_research_scenario.MultiPerspectiveSynthesisWorkflow') as mock_workflow_class:
            
            # 设置角色管理器模拟
            mock_role_manager = Mock()
            mock_role_manager.list_roles.return_value = [
                Mock(id="expert1", name="专家1", description="描述1", system_prompt="提示1", capabilities=["能力1"]),
                Mock(id="expert2", name="专家2", description="描述2", system_prompt="提示2", capabilities=["能力2"])
            ]
            mock_role_manager_class.return_value = mock_role_manager
            
            # 设置工作流模拟
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "topic": "测试主题",
                "synthesis": {"main_conclusion": "测试结论"},
                "key_insights": ["洞察1", "洞察2"],
                "expert_contributions": {"专家1": {"analysis": "分析1"}},
                "quality_score": 0.85,
                "execution_id": "test_execution"
            }
            mock_workflow_class.return_value = mock_workflow
            
            # 执行端到端测试
            result = await conduct_academic_research(
                topic="人工智能在教育中的应用前景分析",
                target_word_count=8000,
                quality_threshold=0.8
            )
            
            # 验证结果
            assert result["success"] == True
            assert "academic_report" in result
            assert result["academic_report"]["word_count"] > 0
            assert result["metadata"]["word_count"] > 0
            
            logger.info("End-to-end academic research test completed successfully")


if __name__ == "__main__":
    async def run_tests():
        """运行所有测试"""
        logger.info("开始学术研究场景功能测试")
        
        try:
            # 基础功能测试
            test_class = TestAcademicResearchScenario()
            
            logger.info("测试学术角色选择器...")
            mock_role_manager = test_class.mock_role_manager()
            await test_class.test_academic_role_selector(mock_role_manager)
            logger.info("✅ 学术角色选择器测试通过")
            
            logger.info("测试学术报告生成器...")
            mock_workflow_result = test_class.mock_workflow_result()
            await test_class.test_academic_report_generator(mock_workflow_result)
            logger.info("✅ 学术报告生成器测试通过")
            
            logger.info("测试质量评估功能...")
            await test_class.test_quality_assessment()
            logger.info("✅ 质量评估功能测试通过")
            
            logger.info("测试报告优化功能...")
            await test_class.test_report_refinement(mock_workflow_result)
            logger.info("✅ 报告优化功能测试通过")
            
            logger.info("测试学术研究场景集成...")
            await test_class.test_academic_research_scenario_integration(mock_role_manager)
            logger.info("✅ 学术研究场景集成测试通过")
            
            # 集成测试
            logger.info("测试端到端学术研究...")
            integration_test = TestAcademicResearchIntegration()
            await integration_test.test_end_to_end_academic_research()
            logger.info("✅ 端到端学术研究测试通过")
            
            logger.info("🎉 所有学术研究场景功能测试通过！")
            
        except Exception as e:
            logger.error(f"❌ 测试失败: {e}")
            raise
    
    # 运行测试
    asyncio.run(run_tests())