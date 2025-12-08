#!/usr/bin/env python3
"""
TDD RED阶段测试 - 多模型Wiki协作功能
目标：证明当前多模型协作功能存在的问题，为修复提供目标
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

class TestMultiModelWikiCollaborationRED:
    """RED阶段：测试多模型协作功能的缺失和问题"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_dependencies(self):
        """创建所有必需的依赖项的模拟对象"""
        # 模拟SessionManager
        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = Mock()
        mock_session_manager.get_session.return_value = Mock()
        mock_session_manager.get_session_id.return_value = "test_session_123"

        # 模拟RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            Mock(name="domain_expert", description="领域专家"),
            Mock(name="researcher", description="研究员"),
            Mock(name="editor", description="编辑"),
            Mock(name="critic", description="批评家")
        ]

        # 模拟RoleModelManager
        mock_role_model_manager = Mock()

        # 为不同角色配置不同模型
        def mock_get_role_model_mapping(role_name, use_debate_config=False):
            if role_name == "domain_expert":
                mock_config = Mock()
                mock_config.model_name = "ollama/llama3.1:70b"
                mock_config.temperature = 0.7
                mock_config.max_tokens = 1000
                mock_mapping = Mock()
                mock_mapping.role_model_config = mock_config
                return mock_mapping
            elif role_name == "researcher":
                mock_config = Mock()
                mock_config.model_name = "ollama/qwen2.5:32b"
                mock_config.temperature = 0.5
                mock_config.max_tokens = 1200
                mock_mapping = Mock()
                mock_mapping.role_model_config = mock_config
                return mock_mapping
            elif role_name == "editor":
                mock_config = Mock()
                mock_config.model_name = "claude-3-haiku-20240307"
                mock_config.temperature = 0.3
                mock_config.max_tokens = 800
                mock_mapping = Mock()
                mock_mapping.role_model_config = mock_config
                return mock_mapping
            elif role_name == "critic":
                mock_config = Mock()
                mock_config.model_name = "gpt-4o-mini"
                mock_config.temperature = 0.8
                mock_config.max_tokens = 600
                mock_mapping = Mock()
                mock_mapping.role_model_config = mock_config
                return mock_mapping
            return None

        mock_role_model_manager.get_role_model_mapping.side_effect = mock_get_role_model_mapping

        # 模拟LiteLLMProvider
        mock_model_provider = Mock()
        mock_model_provider.generate = AsyncMock()

        # 为不同模型返回不同的生成内容
        def mock_generate(prompt, model=None, temperature=0.7, max_tokens=1000):
            if "domain_expert" in prompt:
                return ("作为领域专家，我认为人工智能的核心技术包括机器学习、深度学习、神经网络等。这些技术在图像识别、自然语言处理等领域取得了突破性进展。", {})
            elif "researcher" in prompt:
                return ("根据最新研究，斯坦福大学2024年AI指数报告显示，全球AI投资同比增长35%。Nature期刊发表的论文表明，大型语言模型的参数规模每6个月翻一番。", {})
            elif "editor" in prompt:
                return ("人工智能概述\n\n人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。", {})
            elif "critic" in prompt:
                return ("当前AI技术仍存在局限性：数据偏见、能耗问题、可解释性不足、以及对就业市场的潜在冲击需要认真对待。", {})
            else:
                return ("通用AI内容生成", {})

        mock_model_provider.generate.side_effect = mock_generate

        return {
            'session_manager': mock_session_manager,
            'role_manager': mock_role_manager,
            'role_model_manager': mock_role_model_manager,
            'model_provider': mock_model_provider
        }

    @pytest.mark.asyncio
    async def test_multi_model_collaboration_uses_different_models(self, temp_wiki_dir, mock_dependencies):
        """RED测试：验证多模型协作是否真的使用不同模型"""
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
            title="人工智能测试",
            initial_topic="人工智能的发展现状和未来趋势",
            roles=["domain_expert", "researcher", "editor", "critic"],
            rounds=1
        )

        # RED阶段验证：这里应该失败，因为我们需要证明当前实现存在问题
        # 检查是否真的为不同角色使用了不同模型
        calls = mock_dependencies['model_provider'].generate.call_args_list
        models_used = []

        for call in calls:
            kwargs = call.kwargs
            if 'model' in kwargs:
                models_used.append(kwargs['model'])

        print(f"调用的模型列表: {models_used}")

        # 验证是否使用了不同的模型
        unique_models = set(models_used)

        # RED阶段：我们期望这个断言失败，证明当前实现没有使用不同模型
        # 但如果已经实现，这个断言应该通过
        assert len(unique_models) > 1, f"应该使用多个不同模型，但只使用了: {unique_models}"

        # 验证内容包含不同角色的贡献
        assert "领域专家" in content or "domain_expert" in content
        assert "研究" in content or "researcher" in content
        assert "编辑" in content or "editor" in content
        assert "批评" in content or "critic" in content

    @pytest.mark.asyncio
    async def test_enhanced_wiki_manager_collaboration_method(self, temp_wiki_dir, mock_dependencies):
        """RED测试：验证EnhancedWikiManager的协作方法"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建增强wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=mock_dependencies['role_model_manager'],
            model_provider=mock_dependencies['model_provider'],
            session_manager=mock_dependencies['session_manager'],
            role_manager=mock_dependencies['role_manager']
        )

        # 验证协作创建方法存在且可调用
        assert hasattr(enhanced_wiki, 'create_collaborative_wiki')
        assert callable(getattr(enhanced_wiki, 'create_collaborative_wiki'))

        # 执行协作创建
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="机器学习测试",
            topic="机器学习算法原理与应用",
            roles=["domain_expert", "researcher"],
            rounds=2
        )

        # 验证返回的WikiPage对象
        assert wiki_page is not None
        assert wiki_page.title == "机器学习测试"
        assert len(wiki_page.content) > 0

        # 验证文件被正确创建
        assert wiki_page.file_path.exists()

        # 验证内容包含协作信息
        file_content = wiki_page.file_path.read_text(encoding='utf-8')
        assert "协作" in file_content or "collaboration" in file_content.lower()

    @pytest.mark.asyncio
    async def test_role_intelligence_selector_integration(self, mock_dependencies):
        """RED测试：验证角色智能选择器"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator

        # 这个测试可能失败，因为角色智能选择器可能没有完全实现
        try:
            # 尝试导入角色智能选择器
            from src.daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector

            # 创建选择器
            selector = RoleIntelligenceSelector(mock_dependencies['role_manager'])

            # 测试智能选择
            roles = selector.analyze_topic_for_roles("量子计算在密码学中的应用", max_roles=4)

            # 验证返回的角色列表
            assert isinstance(roles, list)
            assert len(roles) > 0

        except ImportError:
            # 如果模块不存在，这是RED阶段期望的
            pytest.fail("角色智能选择器模块未找到，需要实现")
        except Exception as e:
            # 其他异常也表明功能不完善
            pytest.fail(f"角色智能选择器功能不完善: {e}")

    def test_debate_manager_integration_exists(self):
        """RED测试：验证辩论管理器集成"""
        try:
            from src.daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
            assert EnhancedDebateManager is not None
        except ImportError:
            pytest.fail("EnhancedDebateManager模块未找到")

    @pytest.mark.asyncio
    async def test_dependency_injection_completeness(self, temp_wiki_dir):
        """RED测试：验证依赖注入的完整性"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 测试缺少依赖时的行为
        incomplete_wiki = EnhancedWikiManager(wiki_root=temp_wiki_dir)

        # 验证缺少依赖时的错误处理
        assert incomplete_wiki.collaborator is None

        # 尝试创建协作wiki应该失败
        with pytest.raises(RuntimeError, match="Cannot create collaborative wiki"):
            await incomplete_wiki.create_collaborative_wiki(
                title="测试页面",
                topic="测试主题"
            )

    @pytest.mark.asyncio
    async def test_content_synthesis_quality(self, temp_wiki_dir, mock_dependencies):
        """RED测试：验证内容合成质量"""
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

        # 创建协作内容
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="区块链技术",
            initial_topic="区块链技术的原理和应用",
            roles=["domain_expert", "researcher", "editor"],
            rounds=1
        )

        # RED阶段：验证内容质量问题
        content_structure_checks = [
            ("标题", "# " in content or "##" in content),
            ("章节划分", "##" in content),
            ("角色贡献", any(role in content for role in ["领域专家", "研究员", "编辑"])),
            ("结构化内容", len(content.strip()) > 100),
            ("协作标识", "协作" in content or "collaboration" in content.lower())
        ]

        for check_name, check_result in content_structure_checks:
            print(f"内容检查 - {check_name}: {'✅' if check_result else '❌'}")
            if not check_result:
                pytest.fail(f"内容质量检查失败: {check_name}")

        # 验证内容的结构化程度
        sections = content.split("##")
        assert len(sections) >= 3, f"内容应该包含至少3个章节，但只有{len(sections)}个"


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])