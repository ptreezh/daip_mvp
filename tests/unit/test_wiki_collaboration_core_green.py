#!/usr/bin/env python3
"""
TDD GREEN阶段核心测试 - 验证Wiki协作功能核心部分
专注于验证基本协作流程，绕过复杂的辩论系统问题
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestWikiCollaborationCoreGREEN:
    """GREEN阶段：测试Wiki协作功能的核心部分"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def basic_mock_dependencies(self):
        """创建基础依赖项"""
        # 模拟Session
        mock_session = Mock()
        mock_session.session_id = "core_test_session_123"

        # 模拟SessionManager
        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.get_session.return_value = mock_session

        # 模拟RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            "domain_expert",
            "researcher",
            "editor",
            "critic",
        ]

        # 使用真实的RoleModelManager（EnhancedWikiManager 构造时校验真实类型）
        # 必须用 daip_live 前缀：产品校验用 daip_live.p4_role_manager_tools.role_model_manager 导入，  # noqa: E501
        # src.daip_live 前缀会得到另一个模块实例导致 isinstance 失败
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        mock_role_model_manager = RoleModelManager()

        # 使用真实的LiteLLMProvider（mock-llm 本地模型走 mock 响应，无需外部依赖）
        # 必须用 daip_live 前缀：产品校验用 daip_live.model_provider.provider 导入，
        # src.daip_live 前缀会得到另一个模块实例导致 isinstance 失败
        from daip_live.core.models import ProviderConfig
        from daip_live.model_provider.provider import LiteLLMProvider

        mock_model_provider = LiteLLMProvider(ProviderConfig(model="mock-llm"))

        return {
            "session_manager": mock_session_manager,
            "role_manager": mock_role_manager,
            "role_model_manager": mock_role_model_manager,
            "model_provider": mock_model_provider,
        }

    @pytest.mark.asyncio
    async def test_role_intelligence_selector_works(self, basic_mock_dependencies):
        """测试角色智能选择器基本功能"""
        from src.daip_live.intent_recognition.role_intelligence_selector import (
            RoleIntelligenceSelector,
        )

        selector = RoleIntelligenceSelector(basic_mock_dependencies["role_manager"])

        # 测试基本角色选择
        roles = selector.analyze_topic_for_roles("人工智能技术", max_roles=3)

        assert isinstance(roles, list)
        assert len(roles) > 0
        assert "domain_expert" in roles  # 技术主题应该包含领域专家

    @pytest.mark.asyncio
    async def test_wiki_manager_basic_functionality(self, temp_wiki_dir):
        """测试WikiManager基本功能"""
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 测试创建页面
        page = wiki_manager.create_page(
            title="测试页面", content="这是一个测试页面的内容", tags=["测试", "wiki"]
        )

        assert page is not None
        assert page.title == "测试页面"
        assert page.content == "这是一个测试页面的内容"
        assert "测试" in page.tags
        assert "wiki" in page.tags

        # 测试获取页面
        found_page = wiki_manager.get_page_by_title("测试页面")
        assert found_page is not None
        assert found_page.title == page.title

        # 测试文件被正确创建
        assert page.file_path.exists()
        file_content = page.file_path.read_text(encoding="utf-8")
        assert "这是一个测试页面的内容" in file_content

    @pytest.mark.asyncio
    async def test_enhanced_wiki_manager_creation(
        self, temp_wiki_dir, basic_mock_dependencies
    ):
        """测试EnhancedWikiManager创建和配置"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建增强wiki管理器（不提供完整依赖）
        incomplete_wiki = EnhancedWikiManager(wiki_root=temp_wiki_dir)
        assert incomplete_wiki.collaborator is None

        # 创建增强wiki管理器（提供完整依赖）
        complete_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=basic_mock_dependencies["role_model_manager"],
            model_provider=basic_mock_dependencies["model_provider"],
            session_manager=basic_mock_dependencies["session_manager"],
            role_manager=basic_mock_dependencies["role_manager"],
        )
        assert complete_wiki.collaborator is not None

    @pytest.mark.asyncio
    @patch("src.daip_live.wiki.collaborative_wiki.EnhancedDebateManager")
    async def test_multi_role_collaborator_creation(
        self, mock_debate_manager_class, temp_wiki_dir, basic_mock_dependencies
    ):
        """测试MultiRoleWikiCollaborator创建"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        # 模拟辩论管理器
        mock_debate_manager = Mock()
        mock_debate_manager.run_debate = AsyncMock()
        mock_debate_manager_class.return_value = mock_debate_manager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 创建协作器
        collaborator = MultiRoleWikiCollaborator(
            session_manager=basic_mock_dependencies["session_manager"],
            role_manager=basic_mock_dependencies["role_manager"],
            role_model_manager=basic_mock_dependencies["role_model_manager"],
            model_provider=basic_mock_dependencies["model_provider"],
            wiki_manager=wiki_manager,
        )

        assert collaborator is not None
        assert collaborator.wiki_manager is wiki_manager
        assert len(collaborator.default_roles) > 0

    @pytest.mark.asyncio
    async def test_content_synthesis_basic(self, temp_wiki_dir):
        """测试内容合成基本功能"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        # 创建最小化的依赖
        mock_session = Mock()
        mock_session.session_id = "synthesis_test"

        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = mock_session

        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = ["domain_expert", "researcher"]

        mock_role_model_manager = Mock()
        mock_model_provider = Mock()
        mock_model_provider.generate = AsyncMock(return_value=("生成的内容", {}))

        wiki_manager = WikiManager(temp_wiki_dir)

        # 创建协作器
        collaborator = MultiRoleWikiCollaborator(
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            role_model_manager=mock_role_model_manager,
            model_provider=mock_model_provider,
            wiki_manager=wiki_manager,
        )

        # 测试内容合成方法
        contributions = {
            "domain_expert": ["领域专家的专业观点"],
            "researcher": ["研究人员的分析数据"],
        }

        content = await collaborator._synthesize_wiki_content(
            title="测试主题", contributions=contributions, topic="测试主题描述"
        )

        # 验证合成内容
        assert "# 测试主题" in content
        assert "领域专家" in content
        assert "研究人员" in content
        assert "##" in content  # 应该有章节标题
        assert len(content) > 100  # 内容应该足够长

    @pytest.mark.asyncio
    async def test_wiki_page_creation_flow(
        self, temp_wiki_dir, basic_mock_dependencies
    ):
        """测试维基页面创建流程"""
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 测试空文档检测
        empty_content = "   \n\n   "  # 只有空白字符
        assert wiki_manager._is_empty_document(empty_content)

        # 测试短文档检测
        short_content = "短内容"
        assert wiki_manager._is_empty_document(short_content)

        # 测试正常文档检测
        normal_content = "这是一个正常的文档内容，包含足够的文字用于测试。"
        assert not wiki_manager._is_empty_document(normal_content)

        # 测试创建页面的标签提取
        page = wiki_manager.create_page(
            title="机器学习算法",
            content="机器学习是人工智能的一个分支，包括监督学习、无监督学习等方法。",
            tags=["AI", "ML", "算法"],
        )

        tags = wiki_manager._extract_tags_from_content("机器学习算法", page.content)
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert any("机器学习" in tag or "algorithm" in tag.lower() for tag in tags)

    @pytest.mark.asyncio
    async def test_error_handling_in_collaboration(
        self, temp_wiki_dir, basic_mock_dependencies
    ):
        """测试协作中的错误处理"""
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 测试重复页面创建
        wiki_manager.create_page(
            "重复测试", "这是用于测试重复创建的第一个页面内容", ["标签1"]
        )

        # 尝试创建重复页面应该抛出异常
        with pytest.raises(ValueError, match="already exists"):
            wiki_manager.create_page(
                "重复测试", "这是用于测试重复创建的第二个页面内容", ["标签2"]
            )

        # 测试更新不存在的页面
        with pytest.raises(ValueError, match="not found"):
            wiki_manager.update_page("不存在的页面", "新内容")

        # 测试获取不存在的页面
        assert wiki_manager.get_page_by_title("绝对不存在的页面") is None

    def test_wiki_statistics(self, temp_wiki_dir):
        """测试Wiki统计功能"""
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 创建一些测试页面
        wiki_manager.create_page("页面1", "内容1", ["标签A", "标签B"])
        wiki_manager.create_page("页面2", "内容2 稍长一些", ["标签B", "标签C"])
        wiki_manager.create_page("页面3", "内容3 更加长的内容用于统计测试", ["标签A"])

        # 获取统计信息
        stats = wiki_manager.get_statistics()

        assert stats.total_pages == 3
        assert stats.total_tags >= 3  # 至少有3个不同标签
        assert stats.total_words > 0
        assert stats.last_updated is not None
        assert len(stats.most_used_tags) > 0

    @pytest.mark.asyncio
    async def test_wiki_search_functionality(self, temp_wiki_dir):
        """测试Wiki搜索功能"""
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)

        # 创建测试页面
        wiki_manager.create_page(
            "Python编程", "Python是一种流行的编程语言", ["Python", "编程"]
        )
        wiki_manager.create_page(
            "机器学习", "机器学习使用Python实现算法", ["ML", "Python"]
        )
        wiki_manager.create_page("数据分析", "数据分析需要编程技能", ["数据", "分析"])

        # 测试内容搜索
        results = wiki_manager.search_pages_by_content("Python")
        assert len(results) >= 2  # 应该找到至少2个页面

        # 测试标签搜索
        results = wiki_manager.search_pages_by_tag("Python")
        assert len(results) >= 2  # 应该找到至少2个页面

        # 测试高级搜索
        results = wiki_manager.search_advanced("编程", search_type="content")
        assert len(results) >= 2  # 应该找到包含"编程"的页面


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])
