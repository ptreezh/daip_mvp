#!/usr/bin/env python3
"""
集成测试 - 多模型Wiki协作功能集成
验证各个组件之间的正确协作
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


class TestWikiMultiModelIntegration:
    """多模型Wiki协作功能集成测试"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def complete_dependency_chain(self):
        """创建完整的依赖链"""
        # Session
        mock_session = Mock()
        mock_session.session_id = "integration_test_session"

        # SessionManager
        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.get_session.return_value = mock_session

        # RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            Mock(name="domain_expert", description="领域专家"),
            Mock(name="researcher", description="研究员"),
            Mock(name="editor", description="编辑"),
            Mock(name="critic", description="批评家"),
        ]

        # RoleModelManager（真实实例：EnhancedWikiManager 构造时校验真实类型）
        # 本文件无测试调用其方法，仅作构造参数与身份断言；roles/ 目录不存在仅 warning 不抛错  # noqa: E501
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        mock_role_model_manager = RoleModelManager()

        # ModelProvider（真实实例：EnhancedWikiManager 构造时校验真实类型）
        # 本文件无测试直接调用 generate；mock-llm 本地模型走 mock 响应，无需外部依赖
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
    async def test_complete_dependency_chain_integration(
        self, temp_wiki_dir, complete_dependency_chain
    ):
        """测试完整依赖链集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建完整的增强Wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
        )

        # 验证所有组件都正确初始化
        assert enhanced_wiki.session_manager is not None
        assert enhanced_wiki.role_manager is not None
        assert enhanced_wiki.collaborator is not None

        # 验证协作器包含所有必需的依赖
        collaborator = enhanced_wiki.collaborator
        assert (
            collaborator.session_manager is complete_dependency_chain["session_manager"]
        )
        assert collaborator.role_manager is complete_dependency_chain["role_manager"]
        assert (
            collaborator.role_model_manager
            is complete_dependency_chain["role_model_manager"]
        )
        assert (
            collaborator.model_provider is complete_dependency_chain["model_provider"]
        )

    @pytest.mark.asyncio
    async def test_role_intelligence_selector_integration(
        self, complete_dependency_chain
    ):
        """测试角色智能选择器集成"""
        from src.daip_live.intent_recognition.role_intelligence_selector import (
            RoleIntelligenceSelector,
        )

        selector = RoleIntelligenceSelector(complete_dependency_chain["role_manager"])

        # 测试多种主题类型
        test_topics = [
            ("量子计算原理", ["domain_expert", "researcher"]),
            ("AI市场分析", ["analyst", "researcher"]),
            ("机器学习教程", ["teacher", "domain_expert"]),
            ("技术评审", ["critic", "researcher"]),
        ]

        for topic, expected_roles in test_topics:
            selected_roles = selector.analyze_topic_for_roles(topic, max_roles=3)
            assert isinstance(selected_roles, list)
            assert len(selected_roles) > 0

            # 验证包含相关的角色类型
            for expected_role in expected_roles:
                if expected_role in [
                    "domain_expert",
                    "researcher",
                    "critic",
                    "teacher",
                    "analyst",
                ]:
                    assert expected_role in selected_roles, (
                        f"主题 '{topic}' 应该包含角色 '{expected_role}'"
                    )

    @pytest.mark.asyncio
    @patch("src.daip_live.wiki.collaborative_wiki.EnhancedDebateManager")
    async def test_collaboration_workflow_integration(
        self, mock_debate_manager_class, temp_wiki_dir, complete_dependency_chain
    ):
        """测试协作工作流集成"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        # 模拟辩论管理器
        mock_debate_manager = Mock()
        # 产品契约：run_debate 是 async generator（产品端 :110 async for 直接消费）；
        # 不能赋 AsyncMock——调用返回 coroutine 而非 async iterable，async for 会 TypeError  # noqa: E501

        # 模拟辩论事件
        from src.daip_live.core.models import DebateTurnCompleteEvent

        async def mock_debate_generator(topic, roles, rounds):
            # 生成开始事件
            from src.daip_live.core.models import DebateStartEvent

            yield DebateStartEvent(
                topic=topic, roles=roles, rounds=rounds, session_id="test_session"
            )

            # 为每个角色生成贡献
            for role in roles:
                yield DebateTurnCompleteEvent(
                    participant=role,
                    content_preview=f"{role}的贡献内容",
                    round_number=1,
                    session_id="test_session",
                )

            # 生成结束事件
            from src.daip_live.core.models import DebateCompleteEvent

            yield DebateCompleteEvent(
                topic=topic,
                total_rounds=rounds,
                summary="协作完成",
                session_id="test_session",
            )

        mock_debate_manager.run_debate = mock_debate_generator
        mock_debate_manager_class.return_value = mock_debate_manager

        # 创建组件
        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
            wiki_manager=wiki_manager,
        )

        # 执行协作创建
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="集成测试页面",
            initial_topic="多模型协作集成测试",
            roles=["domain_expert", "researcher"],
            rounds=1,
        )

        # 验证结果
        assert wiki_page is not None
        assert wiki_page.title == "集成测试页面"
        assert len(content) > 0
        assert "##" in content  # 应该有章节结构

    @pytest.mark.asyncio
    @patch("src.daip_live.wiki.collaborative_wiki.EnhancedDebateManager")
    async def test_enhanced_wiki_manager_collaboration_integration(
        self, mock_debate_manager_class, temp_wiki_dir, complete_dependency_chain
    ):
        """测试增强Wiki管理器协作集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 模拟辩论管理器
        mock_debate_manager = Mock()
        mock_debate_manager.run_debate = AsyncMock()

        async def mock_simple_debate(topic, roles, rounds):
            from src.daip_live.core.models import (
                DebateCompleteEvent,
                DebateStartEvent,
                DebateTurnCompleteEvent,
            )

            yield DebateStartEvent(
                topic=topic, roles=roles, rounds=rounds, session_id="integration_test"
            )

            for role in roles:
                yield DebateTurnCompleteEvent(
                    participant=role,
                    content_preview=f"{role}对{topic}的贡献",
                    round_number=1,
                )

            yield DebateCompleteEvent(
                topic=topic,
                total_rounds=rounds,
                summary="协作完成",
                session_id="integration_test",
            )

        mock_debate_manager.run_debate.side_effect = mock_simple_debate
        mock_debate_manager_class.return_value = mock_debate_manager

        # 创建增强Wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
        )

        # 执行协作创建
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="集成协作测试",
            topic="测试各个组件的集成协作",
            roles=["domain_expert", "researcher", "editor"],
            rounds=1,
        )

        # 验证Wiki页面
        assert wiki_page is not None
        assert wiki_page.title == "集成协作测试"
        assert len(wiki_page.content) > 0
        assert wiki_page.file_path.exists()

        # 验证文件内容
        file_content = wiki_page.file_path.read_text(encoding="utf-8")
        assert "集成协作测试" in file_content
        assert "协作" in file_content

    @pytest.mark.asyncio
    async def test_content_synthesis_integration(
        self, temp_wiki_dir, complete_dependency_chain
    ):
        """测试内容合成集成"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
            wiki_manager=wiki_manager,
        )

        # 测试复杂的内容合成
        contributions = {
            "domain_expert": [
                "技术原理：这是一个基于深度学习的复杂系统",
                "实现细节：使用Transformer架构进行建模",
            ],
            "researcher": [
                "研究发现：相关论文数量在过去三年增长了300%",
                "数据支撑：实验准确率达到92.5%",
            ],
            "editor": [
                "结构化整理：本文采用标准学术格式",
                "语言优化：确保专业性和可读性的平衡",
            ],
            "critic": [
                "潜在问题：需要考虑计算资源消耗",
                "改进建议：建议增加更多的实验验证",
            ],
        }

        content = await collaborator._synthesize_wiki_content(
            title="深度学习系统研究",
            contributions=contributions,
            topic="基于Transformer的深度学习系统研究",
        )

        # 验证合成结果
        assert "# 深度学习系统研究" in content
        assert "##" in content
        assert "领域专家" in content or "domain_expert" in content
        assert "研究" in content
        assert "编辑" in content
        assert "批评" in content or "critic" in content
        assert "协作" in content
        assert len(content) > 500  # 应该有足够长的内容

        # 验证结构
        sections = content.split("##")
        assert len(sections) >= 6  # 应该有多个章节

    @pytest.mark.asyncio
    async def test_error_handling_integration(
        self, temp_wiki_dir, complete_dependency_chain
    ):
        """测试错误处理集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 测试不完整依赖的情况
        incomplete_wiki = EnhancedWikiManager(wiki_root=temp_wiki_dir)
        assert incomplete_wiki.collaborator is None

        # 测试错误处理
        with pytest.raises(RuntimeError, match="Cannot create collaborative wiki"):
            await incomplete_wiki.create_collaborative_wiki(
                title="错误测试", topic="应该失败的测试"
            )

        # 测试完整依赖的情况
        complete_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
        )

        # 完整依赖的情况下协作器应该存在
        assert complete_wiki.collaborator is not None

    @pytest.mark.asyncio
    async def test_persistence_integration(
        self, temp_wiki_dir, complete_dependency_chain
    ):
        """测试持久化集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
        )

        # 创建普通页面
        page1 = enhanced_wiki.create_page(
            title="持久化测试页面",
            content="这是用于测试持久化功能的页面",
            tags=["测试", "持久化"],
        )

        # 验证页面持久化
        assert page1.file_path.exists()
        file_content = page1.file_path.read_text(encoding="utf-8")
        # wiki 文件正文只存 content（title 存数据库/文件名），断言内容已持久化
        assert "这是用于测试持久化功能的页面" in file_content

        # 创建新的增强Wiki管理器实例
        enhanced_wiki2 = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
        )

        # 验证页面可以被检索到
        found_page = enhanced_wiki2.get_page_by_title("持久化测试页面")
        assert found_page is not None
        assert found_page.title == "持久化测试页面"
        assert found_page.content == "这是用于测试持久化功能的页面"

    def test_search_and_statistics_integration(
        self, temp_wiki_dir, complete_dependency_chain
    ):
        """测试搜索和统计功能集成"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=complete_dependency_chain["session_manager"],
            role_manager=complete_dependency_chain["role_manager"],
            role_model_manager=complete_dependency_chain["role_model_manager"],
            model_provider=complete_dependency_chain["model_provider"],
        )

        # 创建测试页面
        test_pages = [
            ("Python编程", "Python是一种流行的编程语言", ["Python", "编程"]),
            ("机器学习", "机器学习是AI的一个重要分支", ["ML", "AI"]),
            ("数据科学", "数据科学结合了统计学和编程", ["数据", "科学"]),
            ("深度学习", "深度学习使用神经网络进行建模", ["DL", "神经网络"]),
        ]

        for title, content, tags in test_pages:
            enhanced_wiki.create_page(title, content, tags)

        # 测试搜索功能
        search_results = enhanced_wiki.search_pages_by_content("编程")
        assert len(search_results) >= 2

        tag_results = enhanced_wiki.search_pages_by_tag("Python")
        assert len(tag_results) >= 1

        advanced_results = enhanced_wiki.search_advanced("学习", search_type="content")
        assert len(advanced_results) >= 2

        # 测试统计功能
        stats = enhanced_wiki.get_statistics()
        assert stats.total_pages == 4
        assert stats.total_tags > 0
        assert stats.total_words > 0
        assert len(stats.most_used_tags) > 0


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])
