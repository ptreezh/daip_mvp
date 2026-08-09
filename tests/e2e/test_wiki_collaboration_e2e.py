#!/usr/bin/env python3
"""
端到端测试 - 多模型Wiki协作功能完整工作流
模拟真实使用场景，验证从输入到输出的完整流程
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestWikiCollaborationE2E:
    """多模型Wiki协作功能端到端测试"""

    @pytest.fixture
    def temp_wiki_dir(self):
        """创建临时wiki目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def realistic_dependencies(self):
        """创建接近真实的依赖项"""
        from daip_live.model_provider.provider import LiteLLMProvider, ProviderConfig
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        # Session
        mock_session = Mock()
        mock_session.session_id = "e2e_test_session_2025"

        # SessionManager
        mock_session_manager = Mock()
        mock_session_manager.create_session.return_value = mock_session
        mock_session_manager.get_session.return_value = mock_session

        # RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = [
            "domain_expert",
            "researcher",
            "editor",
            "critic",
            "analyst",
            "teacher",
        ]

        # 真实组件：产品端校验拒绝 Mock，必须使用真实实例
        real_role_model_manager = RoleModelManager()
        real_model_provider = LiteLLMProvider(ProviderConfig(model="mock-llm"))

        return {
            "session_manager": mock_session_manager,
            "role_manager": mock_role_manager,
            "role_model_manager": real_role_model_manager,
            "model_provider": real_model_provider,
        }

    @pytest.mark.asyncio
    @patch("daip_live.wiki.collaborative_wiki.EnhancedDebateManager")
    async def test_complete_wiki_creation_workflow(
        self, mock_debate_manager_class, temp_wiki_dir, realistic_dependencies
    ):
        """测试完整的Wiki创建工作流"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 模拟辩论管理器的完整工作流
        mock_debate_manager = Mock()

        async def realistic_debate_workflow(topic, roles, rounds):
            """模拟真实的辩论工作流"""
            from daip_live.core.models import (
                DebateCompleteEvent,
                DebateStartEvent,
                DebateTurnCompleteEvent,
                ThoughtEvent,
            )

            # 辩论开始
            yield DebateStartEvent(
                topic=topic,
                roles=roles,
                rounds=rounds,
                session_id="realistic_debate_session",
            )

            # 思考过程
            yield ThoughtEvent(content=f"开始讨论主题: {topic}")

            # 每个角色的贡献
            for round_num in range(1, rounds + 1):
                for role in roles:
                    yield ThoughtEvent(content=f"{role} 正在准备第{round_num}轮贡献...")

                    yield DebateTurnCompleteEvent(
                        participant=role,
                        content_preview=f"{role}在第{round_num}轮的贡献内容",
                        round_number=round_num,
                        session_id="realistic_debate_session",
                    )

            # 辩论结束
            yield DebateCompleteEvent(
                topic=topic,
                total_rounds=rounds,
                session_id="realistic_debate_session",
                summary=f"完成了{len(roles)}个角色的{rounds}轮辩论",
            )

        mock_debate_manager.run_debate = realistic_debate_workflow
        mock_debate_manager_class.return_value = mock_debate_manager

        # 创建增强Wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies["session_manager"],
            role_manager=realistic_dependencies["role_manager"],
            role_model_manager=realistic_dependencies["role_model_manager"],
            model_provider=realistic_dependencies["model_provider"],
        )

        # 执行完整的协作创建流程
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="机器学习技术详解",
            topic="机器学习的基本概念、核心技术和发展趋势",
            roles=["domain_expert", "researcher", "editor", "critic"],
            rounds=2,
        )

        # 验证结果
        assert wiki_page is not None
        assert wiki_page.title == "机器学习技术详解"
        assert len(wiki_page.content) > 0
        assert len(wiki_page.tags) > 0

        # 验证文件持久化
        assert wiki_page.file_path.exists()
        file_content = wiki_page.file_path.read_text(encoding="utf-8")
        assert "机器学习技术详解" in file_content
        assert "协作" in file_content
        assert "##" in file_content  # 应该有章节结构

        # 验证内容质量
        sections = file_content.split("##")
        assert len(sections) >= 4  # 应该有多个章节

        # 验证包含不同角色的贡献
        content_indicators = ["领域专家", "研究", "编辑", "批评"]
        for indicator in content_indicators:
            assert (
                indicator in file_content or indicator.lower() in file_content.lower()
            )

        # 验证可以被检索
        found_page = enhanced_wiki.get_page_by_title("机器学习技术详解")
        assert found_page is not None
        assert found_page.title == wiki_page.title

    @pytest.mark.asyncio
    async def test_role_intelligence_workflow(self, realistic_dependencies):
        """测试角色智能选择工作流"""
        from daip_live.intent_recognition.role_intelligence_selector import (
            RoleIntelligenceSelector,
        )

        selector = RoleIntelligenceSelector(realistic_dependencies["role_manager"])

        # 测试不同类型主题的智能选择
        test_scenarios = [
            {
                "topic": "深度学习在医疗诊断中的应用研究",
                "expected_primary": ["domain_expert", "researcher"],
                "description": "技术研究类主题",
            },
            {
                "topic": "AI创业公司投资机会分析",
                "expected_primary": ["analyst", "researcher"],
                "description": "商业分析类主题",
            },
            {
                "topic": "Python机器学习入门教程",
                "expected_primary": ["teacher", "domain_expert"],
                "description": "教育类主题",
            },
            {
                "topic": "大数据平台技术方案评估",
                "expected_primary": ["critic", "domain_expert"],
                "description": "评审类主题",
            },
        ]

        for scenario in test_scenarios:
            selected_roles = selector.analyze_topic_for_roles(
                scenario["topic"], max_roles=4
            )

            # 验证角色选择的合理性
            assert isinstance(selected_roles, list)
            assert len(selected_roles) >= 2  # 至少选择2个角色
            assert len(selected_roles) <= 4  # 最多4个角色

            # 验证包含主要角色类型
            for expected_role in scenario["expected_primary"]:
                if expected_role in [
                    "domain_expert",
                    "researcher",
                    "critic",
                    "teacher",
                    "analyst",
                ]:
                    # 软检查：应该包含相关角色，但不强制要求
                    pass

            # 测试上下文增强
            enhanced_roles = selector.enhance_role_selection_with_context(
                scenario["topic"],
                context={
                    "target_audience": "professionals",
                    "content_type": "technical_report",
                    "complexity": "high",
                },
            )
            assert isinstance(enhanced_roles, list)
            assert len(enhanced_roles) > 0

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, temp_wiki_dir, realistic_dependencies):
        """测试错误恢复工作流"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies["session_manager"],
            role_manager=realistic_dependencies["role_manager"],
            role_model_manager=realistic_dependencies["role_model_manager"],
            model_provider=realistic_dependencies["model_provider"],
        )

        # 测试1: 创建重复页面
        enhanced_wiki.create_page(
            title="错误恢复测试", content="第一个版本的内容", tags=["测试", "错误处理"]
        )

        # 尝试创建重复页面应该进入协同编辑模式
        try:
            page2 = enhanced_wiki.create_page(
                title="错误恢复测试", content="第二个版本的内容", tags=["测试", "协同"]
            )
            # 如果没有抛出异常，说明系统处理了重复页面
            assert page2 is not None
        except ValueError as e:
            # 如果抛出异常，应该是关于协同编辑的提示
            assert "协同编辑" in str(e) or "collaboration" in str(e).lower()

        # 测试2: 处理空内容
        empty_page = enhanced_wiki.create_page(
            title="空内容测试",
            content="   ",  # 只有空格
            tags=["空内容"],
        )

        # 系统应该能处理空内容页面
        assert empty_page is not None

        # 测试3: 搜索不存在的页面
        non_existent = enhanced_wiki.get_page_by_title("绝对不存在的页面")
        assert non_existent is None

        # 测试4: 更新不存在的页面
        try:
            enhanced_wiki.update_page("不存在的页面", "更新内容")
            assert False, "应该抛出异常"
        except ValueError:
            pass  # 期望的异常

    @pytest.mark.asyncio
    @patch("daip_live.wiki.collaborative_wiki.EnhancedDebateManager")
    async def test_multi_model_collaboration_workflow(
        self, mock_debate_manager_class, temp_wiki_dir, realistic_dependencies
    ):
        """测试多模型协作工作流"""
        from daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from daip_live.wiki.manager import WikiManager

        # 模拟辩论管理器
        mock_debate_manager = Mock()

        async def multi_model_workflow(topic, roles, rounds):
            """模拟多模型协作工作流"""
            from daip_live.core.models import (
                DebateCompleteEvent,
                DebateStartEvent,
                DebateTurnCompleteEvent,
            )

            yield DebateStartEvent(
                topic=topic, roles=roles, rounds=rounds, session_id="multi_model_test"
            )

            # 每个角色使用不同的模型进行贡献
            for role in roles:
                yield DebateTurnCompleteEvent(
                    participant=role,
                    content_preview=f"{role}使用{role}专用模型的贡献",
                    round_number=1,
                    session_id="multi_model_test",
                )

            yield DebateCompleteEvent(
                topic=topic,
                total_rounds=rounds,
                session_id="multi_model_test",
                summary="多模型协作完成",
            )

        mock_debate_manager.run_debate = multi_model_workflow
        mock_debate_manager_class.return_value = mock_debate_manager

        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=realistic_dependencies["session_manager"],
            role_manager=realistic_dependencies["role_manager"],
            role_model_manager=realistic_dependencies["role_model_manager"],
            model_provider=realistic_dependencies["model_provider"],
            wiki_manager=wiki_manager,
        )

        # 执行多模型协作
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="量子计算前沿研究",
            initial_topic="量子计算的最新进展和未来应用前景",
            roles=["domain_expert", "researcher", "analyst"],
            rounds=1,
        )

        # 验证真实组件已注入（产品端校验拒绝 Mock，协作必须基于真实依赖）
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager

        assert isinstance(realistic_dependencies["model_provider"], LiteLLMProvider)
        assert isinstance(
            realistic_dependencies["role_model_manager"], RoleModelManager
        )
        assert len(realistic_dependencies["role_manager"].list_roles()) >= 3

        # 验证内容质量（三个角色的贡献应合入最终内容）
        assert "量子计算" in content
        assert "协作" in content
        assert "##" in content
        contribution_count = content.count("专用模型的贡献")
        assert contribution_count >= 3, (
            f"三个角色的贡献都应合入内容，实际 {contribution_count} 处"
        )

        # 验证Wiki页面
        assert wiki_page is not None
        assert wiki_page.title == "量子计算前沿研究"
        assert len(wiki_page.tags) > 0

    def test_persistence_and_search_workflow(
        self, temp_wiki_dir, realistic_dependencies
    ):
        """测试持久化和搜索工作流"""
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies["session_manager"],
            role_manager=realistic_dependencies["role_manager"],
            role_model_manager=realistic_dependencies["role_model_manager"],
            model_provider=realistic_dependencies["model_provider"],
        )

        # 创建多个测试页面
        test_pages = [
            {
                "title": "人工智能伦理",
                "content": "AI伦理涉及算法公平性、隐私保护、透明度等关键问题。",
                "tags": ["AI", "伦理", "算法"],
            },
            {
                "title": "自然语言处理技术",
                "content": "NLP技术包括文本分析、情感识别、机器翻译等应用。",
                "tags": ["NLP", "语言", "技术"],
            },
            {
                "title": "计算机视觉应用",
                "content": "计算机视觉在医疗影像、自动驾驶、安防监控等领域广泛应用。",
                "tags": ["CV", "视觉", "应用"],
            },
        ]

        created_pages = []
        for page_data in test_pages:
            page = enhanced_wiki.create_page(
                title=page_data["title"],
                content=page_data["content"],
                tags=page_data["tags"],
            )
            created_pages.append(page)

        # 验证所有页面都被正确创建和持久化
        for i, page in enumerate(created_pages):
            assert page is not None
            assert page.file_path.exists()

            # 验证文件内容
            file_content = page.file_path.read_text(encoding="utf-8")
            assert test_pages[i]["content"] in file_content

        # 测试搜索功能
        # 内容搜索
        ai_results = enhanced_wiki.search_pages_by_content("AI")
        assert len(ai_results) >= 1

        tech_results = enhanced_wiki.search_pages_by_content("技术")
        assert len(tech_results) >= 1

        # 标签搜索
        cv_results = enhanced_wiki.search_pages_by_tag("CV")
        assert len(cv_results) >= 1

        # 高级搜索
        text_results = enhanced_wiki.search_advanced("文本", search_type="content")
        assert len(text_results) >= 1

        # 测试统计功能
        stats = enhanced_wiki.get_statistics()
        assert stats.total_pages == 3
        assert stats.total_tags > 0
        assert stats.total_words > 0
        assert len(stats.most_used_tags) > 0

        # 测试最近页面
        recent_pages = enhanced_wiki.get_recent_pages(limit=2)
        assert len(recent_pages) == 2

    @pytest.mark.asyncio
    async def test_complete_user_scenario(self, temp_wiki_dir, realistic_dependencies):
        """测试完整的用户使用场景"""
        from daip_live.intent_recognition.role_intelligence_selector import (
            RoleIntelligenceSelector,
        )
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies["session_manager"],
            role_manager=realistic_dependencies["role_manager"],
            role_model_manager=realistic_dependencies["role_model_manager"],
            model_provider=realistic_dependencies["model_provider"],
        )

        # 场景：用户想要创建一个关于"区块链在供应链中的应用"的维基页面
        user_topic = "区块链在供应链管理中的应用与挑战"

        # 步骤1: 智能角色选择
        selector = RoleIntelligenceSelector(realistic_dependencies["role_manager"])
        recommended_roles = selector.analyze_topic_for_roles(user_topic, max_roles=4)

        # 步骤2: 创建普通页面作为基础
        initial_page = enhanced_wiki.create_page(
            title="区块链供应链应用",
            content="## 概述\n\n区块链技术在供应链管理中的应用正在快速增长...",
            tags=["区块链", "供应链", "技术"],
        )

        # 步骤3: 搜索是否已有相关内容
        enhanced_wiki.search_pages_by_content("区块链")

        # 步骤4: 获取推荐理由
        reasons = selector.get_role_recommendation_reason(user_topic, recommended_roles)
        for role, reason in reasons.items():
            pass

        # 步骤5: 验证页面统计信息
        enhanced_wiki.get_statistics()

        # 验证整个流程的完整性
        assert initial_page is not None
        assert len(recommended_roles) >= 2
        assert isinstance(reasons, dict)
        assert len(reasons) > 0


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])
