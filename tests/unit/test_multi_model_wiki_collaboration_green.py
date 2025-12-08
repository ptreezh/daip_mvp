#!/usr/bin/env python3
"""
TDD GREEN阶段测试 - 多模型Wiki协作功能修复验证
目标：验证修复后的多模型协作功能正常工作
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

class TestMultiModelWikiCollaborationGREEN:
    """GREEN阶段：测试修复后的多模型协作功能"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_dependencies(self):
        """创建完整且正确配置的依赖项"""
        # 模拟SessionManager - 返回字符串session_id
        mock_session = Mock()
        mock_session.session_id = "test_session_123"

        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.get_session.return_value = mock_session
        mock_session_manager.get_session_id.return_value = "test_session_123"

        # 模拟RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            Mock(name="domain_expert", description="领域专家"),
            Mock(name="researcher", description="研究员"),
            Mock(name="editor", description="编辑"),
            Mock(name="critic", description="批评家")
        ]

        # 模拟RoleModelManager - 正确配置get_debate_model_mappings
        mock_role_model_manager = Mock()

        def mock_get_role_model_mapping(role_name, use_debate_config=False):
            """为不同角色配置不同模型"""
            mock_config = Mock()
            if role_name == "domain_expert":
                mock_config.model_name = "ollama/llama3.1:70b"
                mock_config.temperature = 0.7
                mock_config.max_tokens = 1000
            elif role_name == "researcher":
                mock_config.model_name = "ollama/qwen2.5:32b"
                mock_config.temperature = 0.5
                mock_config.max_tokens = 1200
            elif role_name == "editor":
                mock_config.model_name = "claude-3-haiku-20240307"
                mock_config.temperature = 0.3
                mock_config.max_tokens = 800
            elif role_name == "critic":
                mock_config.model_name = "gpt-4o-mini"
                mock_config.temperature = 0.8
                mock_config.max_tokens = 600
            else:
                mock_config.model_name = "ollama/llama3:instruct"
                mock_config.temperature = 0.7
                mock_config.max_tokens = 1000

            mock_mapping = Mock()
            mock_mapping.role_model_config = mock_config
            return mock_mapping

        def mock_get_debate_model_mappings(role_names):
            """返回角色模型映射列表"""
            return [mock_get_role_model_mapping(role) for role in role_names]

        mock_role_model_manager.get_role_model_mapping.side_effect = mock_get_role_model_mapping
        mock_role_model_manager.get_debate_model_mappings = mock_get_debate_model_mappings

        # 模拟LiteLLMProvider
        mock_model_provider = Mock()
        mock_model_provider.generate = AsyncMock()

        # 为不同模型生成不同内容
        def mock_generate(prompt, model=None, temperature=0.7, max_tokens=1000):
            if "domain_expert" in prompt or model == "ollama/llama3.1:70b":
                return ("作为领域专家，人工智能的核心技术包括机器学习、深度学习、神经网络等。这些技术在图像识别、自然语言处理等领域取得了突破性进展。", {"model": "ollama/llama3.1:70b"})
            elif "researcher" in prompt or model == "ollama/qwen2.5:32b":
                return ("根据斯坦福大学2024年AI指数报告，全球AI投资同比增长35%。研究表明，大型语言模型的参数规模每6个月翻一番，技术发展速度超出预期。", {"model": "ollama/qwen2.5:32b"})
            elif "editor" in prompt or model == "claude-3-haiku-20240307":
                return ("# 人工智能技术概述\n\n人工智能是计算机科学的前沿分支，致力于创建能够执行通常需要人类智能的任务的智能系统。", {"model": "claude-3-haiku-20240307"})
            elif "critic" in prompt or model == "gpt-4o-mini":
                return ("尽管AI技术发展迅速，但仍面临数据偏见、能耗问题、可解释性不足等挑战。对就业市场的潜在冲击和社会伦理问题需要认真对待。", {"model": "gpt-4o-mini"})
            else:
                return ("通用AI内容生成", {"model": "default"})

        mock_model_provider.generate.side_effect = mock_generate

        return {
            'session_manager': mock_session_manager,
            'role_manager': mock_role_manager,
            'role_model_manager': mock_role_model_manager,
            'model_provider': mock_model_provider
        }

    @pytest.mark.asyncio
    async def test_role_intelligence_selector_functionality(self):
        """GREEN测试：验证角色智能选择器功能"""
        from src.daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector

        # 模拟RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = ["domain_expert", "researcher", "editor", "critic"]

        # 创建选择器
        selector = RoleIntelligenceSelector(mock_role_manager)

        # 测试不同类型主题的角色选择
        test_cases = [
            {
                "topic": "人工智能技术原理与实现",
                "expected_roles": ["domain_expert", "researcher"],
                "description": "技术类主题"
            },
            {
                "topic": "AI市场发展趋势分析",
                "expected_roles": ["analyst", "researcher"],
                "description": "分析类主题"
            },
            {
                "topic": "机器学习入门教程",
                "expected_roles": ["teacher", "domain_expert"],
                "description": "教育类主题"
            }
        ]

        for case in test_cases:
            roles = selector.analyze_topic_for_roles(case["topic"], max_roles=4)

            print(f"\n{case['description']}:")
            print(f"  主题: {case['topic']}")
            print(f"  期望角色: {case['expected_roles']}")
            print(f"  实际角色: {roles}")

            # 验证返回了角色列表
            assert isinstance(roles, list)
            assert len(roles) > 0

            # 验证包含期望的角色类型
            for expected_role in case["expected_roles"]:
                assert expected_role in roles, f"应该包含角色 {expected_role}"

        # 测试上下文增强
        context_enhanced_roles = selector.enhance_role_selection_with_context(
            "Python编程基础",
            context={
                "target_audience": "beginners",
                "content_type": "tutorial"
            }
        )
        assert "teacher" in context_enhanced_roles

    @pytest.mark.asyncio
    async def test_multi_model_collaboration_with_different_models(self, temp_wiki_dir, mock_dependencies):
        """GREEN测试：验证多模型协作使用不同模型"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        # 创建基础组件
        wiki_manager = WikiManager(temp_wiki_dir)

        # 创建协作器
        collaborator = MultiRoleWikiCollaborator(
            session_manager=mock_dependencies['session_manager'],
            role_manager=mock_dependencies['role_manager'],
            role_model_manager=mock_dependencies['role_model_manager'],
            model_provider=mock_dependencies['model_provider'],
            wiki_manager=wiki_manager
        )

        # 执行协作创建
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="多模型协作测试",
            initial_topic="多模型协作的优势与挑战",
            roles=["domain_expert", "researcher", "editor"],
            rounds=1
        )

        # 验证结果
        assert wiki_page is not None
        assert wiki_page.title == "多模型协作测试"
        assert len(content) > 0

        # 验证使用了不同的模型
        calls = mock_dependencies['model_provider'].generate.call_args_list
        models_used = []

        for call in calls:
            kwargs = call.kwargs
            if 'model' in kwargs:
                models_used.append(kwargs['model'])

        unique_models = set(models_used)
        print(f"使用的模型: {unique_models}")

        # GREEN阶段：现在应该通过，因为我们使用了不同的模型
        assert len(unique_models) >= 2, f"应该使用至少2个不同模型，但只使用了: {unique_models}"

        # 验证内容质量
        assert "协作" in content
        assert len(content.strip()) > 100

    @pytest.mark.asyncio
    async def test_enhanced_wiki_manager_complete_workflow(self, temp_wiki_dir, mock_dependencies):
        """GREEN测试：验证EnhancedWikiManager完整工作流"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建增强wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_dependencies['role_model_manager'],
            model_provider=mock_dependencies['model_provider'],
            session_manager=mock_dependencies['session_manager'],
            role_manager=mock_dependencies['role_manager']
        )

        # 验证协作器已正确初始化
        assert enhanced_wiki.collaborator is not None

        # 执行协作创建
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="区块链技术详解",
            topic="区块链的原理、技术和应用",
            roles=["domain_expert", "researcher"],
            rounds=2
        )

        # 验证WikiPage对象
        assert wiki_page is not None
        assert wiki_page.title == "区块链技术详解"
        assert len(wiki_page.content) > 0
        assert len(wiki_page.tags) > 0

        # 验证文件被正确创建
        assert wiki_page.file_path.exists()

        # 验证文件内容
        file_content = wiki_page.file_path.read_text(encoding='utf-8')
        assert "区块链技术详解" in file_content
        assert "##" in file_content  # 应该有章节标题
        assert "协作" in file_content

        # 验证可以被搜索到
        found_page = enhanced_wiki.get_page_by_title("区块链技术详解")
        assert found_page is not None
        assert found_page.title == wiki_page.title

    @pytest.mark.asyncio
    async def test_content_synthesis_structure(self, temp_wiki_dir, mock_dependencies):
        """GREEN测试：验证内容合成的结构化质量"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=mock_dependencies['session_manager'],
            role_manager=mock_dependencies['role_manager'],
            role_model_manager=mock_dependencies['role_model_manager'],
            model_provider=mock_dependencies['model_provider'],
            wiki_manager=wiki_manager
        )

        # 创建结构化内容
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="云计算架构",
            initial_topic="云计算的架构设计和服务模式",
            roles=["domain_expert", "researcher", "editor", "critic"],
            rounds=1
        )

        # 验证内容结构
        structure_checks = {
            "标题格式": content.startswith("# "),
            "章节结构": "##" in content,
            "角色贡献": any(indicator in content for indicator in ["领域专家", "研究员", "编辑", "批评"]),
            "内容长度": len(content.strip()) > 200,
            "协作标识": "协作" in content,
            "时间戳": "2025" in content,  # 应该包含创建时间
        }

        for check_name, check_result in structure_checks.items():
            print(f"结构检查 - {check_name}: {'✅' if check_result else '❌'}")
            assert check_result, f"结构检查失败: {check_name}"

        # 验证章节数量
        sections = content.split("##")
        assert len(sections) >= 5, f"应该包含至少5个章节，但只有{len(sections)}个"

    @pytest.mark.asyncio
    async def test_error_handling_and_fallbacks(self, temp_wiki_dir, mock_dependencies):
        """GREEN测试：验证错误处理和回退机制"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=mock_dependencies['session_manager'],
            role_manager=mock_dependencies['role_manager'],
            role_model_manager=mock_dependencies['role_model_manager'],
            model_provider=mock_dependencies['model_provider'],
            wiki_manager=wiki_manager
        )

        # 测试空角色列表的处理
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="空角色测试",
            initial_topic="测试主题",
            roles=None,  # 应该使用智能选择
            rounds=1
        )

        assert wiki_page is not None
        assert len(content) > 0

        # 验证使用了默认角色
        calls = mock_dependencies['model_provider'].generate.call_args_list
        assert len(calls) > 0  # 应该有模型调用

    @pytest.mark.asyncio
    async def test_integration_with_all_dependencies(self, temp_wiki_dir):
        """GREEN测试：验证与所有依赖的集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建完整的依赖模拟
        mock_session_manager = Mock()
        mock_session_manager.get_session_id.return_value = "integration_test_session"

        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = ["domain_expert", "researcher"]

        mock_role_model_manager = Mock()
        mock_role_model_manager.get_debate_model_mappings.return_value = [
            Mock(role_model_config=Mock(model_name="test_model_1")),
            Mock(role_model_config=Mock(model_name="test_model_2"))
        ]

        mock_model_provider = Mock()
        mock_model_provider.generate = AsyncMock(return_value=("测试内容", {}))

        # 测试完整集成
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            role_model_manager=mock_role_model_manager,
            model_provider=mock_model_provider
        )

        # 验证所有依赖都正确注入
        assert enhanced_wiki.session_manager is mock_session_manager
        assert enhanced_wiki.role_manager is mock_role_manager
        assert enhanced_wiki.collaborator is not None

        # 执行协作创建
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="集成测试页面",
            topic="集成测试主题"
        )

        assert wiki_page is not None
        assert wiki_page.title == "集成测试页面"


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])