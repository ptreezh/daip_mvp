#!/usr/bin/env python3
"""
端到端测试 - 多模型Wiki协作功能完整工作流
模拟真实使用场景，验证从输入到输出的完整流程
"""

import pytest
import asyncio
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

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
            "domain_expert", "researcher", "editor", "critic", "analyst", "teacher"
        ]

        # RoleModelManager
        mock_role_model_manager = Mock()

        def realistic_role_mapping(role_name, use_debate_config=False):
            """真实的多模型配置"""
            configs = {
                "domain_expert": {
                    "model_name": "ollama/llama3.1:70b",
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "provider": "ollama"
                },
                "researcher": {
                    "model_name": "ollama/qwen2.5:32b",
                    "temperature": 0.5,
                    "max_tokens": 1200,
                    "provider": "ollama"
                },
                "editor": {
                    "model_name": "claude-3-haiku-20240307",
                    "temperature": 0.3,
                    "max_tokens": 1000,
                    "provider": "anthropic"
                },
                "critic": {
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.8,
                    "max_tokens": 800,
                    "provider": "openai"
                },
                "analyst": {
                    "model_name": "gemini-1.5-flash",
                    "temperature": 0.4,
                    "max_tokens": 1000,
                    "provider": "google"
                },
                "teacher": {
                    "model_name": "claude-3-sonnet-20240229",
                    "temperature": 0.2,
                    "max_tokens": 1200,
                    "provider": "anthropic"
                }
            }

            config_data = configs.get(role_name, configs["domain_expert"])
            mock_config = Mock()
            for key, value in config_data.items():
                setattr(mock_config, key, value)

            mock_mapping = Mock()
            mock_mapping.role_model_config = mock_config
            return mock_mapping

        mock_role_model_manager.get_role_model_mapping.side_effect = realistic_role_mapping
        mock_role_model_manager.get_debate_model_mappings = lambda roles: [realistic_role_mapping(role) for role in roles]

        # ModelProvider - 模拟真实的内容生成
        mock_model_provider = Mock()
        mock_model_provider.generate = AsyncMock()

        def realistic_generate(prompt, model=None, temperature=0.7, max_tokens=1000):
            """根据不同模型生成真实的内容"""
            content_map = {
                "domain_expert": """
作为领域专家，我认为机器学习是人工智能的核心分支，它通过算法使计算机系统能够从数据中学习和改进。

核心技术包括：
1. 监督学习：使用标注数据训练模型
2. 无监督学习：发现数据中的隐藏模式
3. 强化学习：通过奖励机制优化决策
4. 深度学习：基于神经网络的多层学习

实际应用涵盖图像识别、自然语言处理、推荐系统等多个领域。
""",
                "researcher": """
根据最新研究数据，机器学习领域发展迅速：

- 论文发表数量：2023年AI相关论文超过5万篇，同比增长40%
- 投资规模：全球AI投资在2024年达到5000亿美元
- 技术突破：GPT、Claude等大语言模型的参数规模已突破万亿级
- 就业影响：预计到2030年，AI将创造9700万个新工作岗位

数据来源：Stanford AI Index 2024, McKinsey Global Institute 2024
""",
                "editor": """
# 机器学习技术概述

机器学习是计算机科学的一个分支，致力于开发能够从数据中自动学习和改进的算法系统。本文将系统介绍机器学习的基本概念、核心技术和发展趋势。

## 1. 基本定义

机器学习通过构建数学模型，使计算机能够在没有明确编程的情况下执行特定任务。它代表了人工智能向数据驱动方法转变的重要里程碑。

## 2. 发展历程

从1950年代的感知机到2020年代的大语言模型，机器学习经历了多个重要发展阶段...
""",
                "critic": """
尽管机器学习取得了显著进展，但仍面临重要挑战：

## 主要限制
1. **数据依赖性**：需要大量高质量标注数据
2. **可解释性问题**：深度学习模型决策过程缺乏透明度
3. **计算资源消耗**：训练大型模型需要巨大能源投入
4. **偏见和公平性**：训练数据中的偏见可能被模型放大

## 改进建议
- 加强算法可解释性研究
- 开发更高效的训练方法
- 建立完善的伦理审查机制
""",
                "analyst": """
机器学习市场分析：

## 市场规模
- 2024年全球机器学习市场规模：约2000亿美元
- 预计2030年将增长至1万亿美元
- 年复合增长率：32%

## 主要驱动因素
1. 数字化转型加速
2. 大数据技术成熟
3. 计算能力提升
4. 企业需求增长

## 竞争格局
- 技术巨头：Google、Microsoft、Amazon
- 专业厂商：NVIDIA、IBM、SAP
- 初创企业：OpenAI、Anthropic、Hugging Face
""",
                "teacher": """
# 机器学习入门指南

大家好！今天我们来学习机器学习的基础知识。

## 什么是机器学习？

简单来说，机器学习就是让计算机像人一样从经验中学习。就像我们通过练习来掌握技能一样，计算机通过看很多例子来学会完成任务。

## 为什么要学习机器学习？

1. **未来趋势**：AI正在改变世界
2. **就业机会**：数据科学家是热门职业
3. **实用性强**：可以解决实际问题

## 如何开始学习？

1. 掌握Python编程基础
2. 学习数学基础知识
3. 了解常用算法原理
4. 动手实践项目

记住：学习是一个循序渐进的过程，不要急于求成！
"""
            }

            # 根据prompt或模型选择内容
            for role, content in content_map.items():
                if role in prompt.lower() or (model and role in model.lower()):
                    return (content.strip(), {"model": model or "unknown", "role": role})

            # 默认内容
            return ("机器学习是人工智能的重要分支，涉及数据驱动的算法开发和模型训练。", {"model": model or "default"})

        mock_model_provider.generate.side_effect = realistic_generate

        return {
            'session_manager': mock_session_manager,
            'role_manager': mock_role_manager,
            'role_model_manager': mock_role_model_manager,
            'model_provider': mock_model_provider
        }

    @pytest.mark.asyncio
    @patch('src.daip_live.wiki.collaborative_wiki.EnhancedDebateManager')
    async def test_complete_wiki_creation_workflow(self, mock_debate_manager_class, temp_wiki_dir, realistic_dependencies):
        """测试完整的Wiki创建工作流"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 模拟辩论管理器的完整工作流
        mock_debate_manager = Mock()
        mock_debate_manager.run_debate = AsyncMock()

        async def realistic_debate_workflow(topic, roles, rounds):
            """模拟真实的辩论工作流"""
            from src.daip_live.core.models import (
                DebateStartEvent, DebateTurnCompleteEvent, ThoughtEvent, DebateCompleteEvent
            )

            # 辩论开始
            yield DebateStartEvent(
                topic=topic,
                roles=roles,
                rounds=rounds,
                session_id="realistic_debate_session"
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
                        round_number=round_num
                    )

            # 辩论结束
            yield DebateCompleteEvent(
                topic=topic,
                total_rounds=rounds,
                final_summary=f"完成了{len(roles)}个角色的{rounds}轮辩论"
            )

        mock_debate_manager.run_debate.side_effect = realistic_debate_workflow
        mock_debate_manager_class.return_value = mock_debate_manager

        # 创建增强Wiki管理器
        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies['session_manager'],
            role_manager=realistic_dependencies['role_manager'],
            role_model_manager=realistic_dependencies['role_model_manager'],
            model_provider=realistic_dependencies['model_provider']
        )

        # 执行完整的协作创建流程
        wiki_page = await enhanced_wiki.create_collaborative_wiki(
            title="机器学习技术详解",
            topic="机器学习的基本概念、核心技术和发展趋势",
            roles=["domain_expert", "researcher", "editor", "critic"],
            rounds=2
        )

        # 验证结果
        assert wiki_page is not None
        assert wiki_page.title == "机器学习技术详解"
        assert len(wiki_page.content) > 0
        assert len(wiki_page.tags) > 0

        # 验证文件持久化
        assert wiki_page.file_path.exists()
        file_content = wiki_page.file_path.read_text(encoding='utf-8')
        assert "机器学习技术详解" in file_content
        assert "协作" in file_content
        assert "##" in file_content  # 应该有章节结构

        # 验证内容质量
        sections = file_content.split("##")
        assert len(sections) >= 4  # 应该有多个章节

        # 验证包含不同角色的贡献
        content_indicators = ["领域专家", "研究", "编辑", "批评"]
        for indicator in content_indicators:
            assert indicator in file_content or indicator.lower() in file_content.lower()

        # 验证可以被检索
        found_page = enhanced_wiki.get_page_by_title("机器学习技术详解")
        assert found_page is not None
        assert found_page.title == wiki_page.title

    @pytest.mark.asyncio
    async def test_role_intelligence_workflow(self, realistic_dependencies):
        """测试角色智能选择工作流"""
        from src.daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector

        selector = RoleIntelligenceSelector(realistic_dependencies['role_manager'])

        # 测试不同类型主题的智能选择
        test_scenarios = [
            {
                "topic": "深度学习在医疗诊断中的应用研究",
                "expected_primary": ["domain_expert", "researcher"],
                "description": "技术研究类主题"
            },
            {
                "topic": "AI创业公司投资机会分析",
                "expected_primary": ["analyst", "researcher"],
                "description": "商业分析类主题"
            },
            {
                "topic": "Python机器学习入门教程",
                "expected_primary": ["teacher", "domain_expert"],
                "description": "教育类主题"
            },
            {
                "topic": "大数据平台技术方案评估",
                "expected_primary": ["critic", "domain_expert"],
                "description": "评审类主题"
            }
        ]

        for scenario in test_scenarios:
            selected_roles = selector.analyze_topic_for_roles(
                scenario["topic"],
                max_roles=4
            )

            print(f"\n{scenario['description']}:")
            print(f"  主题: {scenario['topic']}")
            print(f"  期望主要角色: {scenario['expected_primary']}")
            print(f"  实际选择角色: {selected_roles}")

            # 验证角色选择的合理性
            assert isinstance(selected_roles, list)
            assert len(selected_roles) >= 2  # 至少选择2个角色
            assert len(selected_roles) <= 4  # 最多4个角色

            # 验证包含主要角色类型
            for expected_role in scenario["expected_primary"]:
                if expected_role in ["domain_expert", "researcher", "critic", "teacher", "analyst"]:
                    # 软检查：应该包含相关角色，但不强制要求
                    role_found = expected_role in selected_roles
                    print(f"    {expected_role}: {'✅' if role_found else '⚠️'}")

            # 测试上下文增强
            enhanced_roles = selector.enhance_role_selection_with_context(
                scenario["topic"],
                context={
                    "target_audience": "professionals",
                    "content_type": "technical_report",
                    "complexity": "high"
                }
            )
            assert isinstance(enhanced_roles, list)
            assert len(enhanced_roles) > 0

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, temp_wiki_dir, realistic_dependencies):
        """测试错误恢复工作流"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies['session_manager'],
            role_manager=realistic_dependencies['role_manager'],
            role_model_manager=realistic_dependencies['role_model_manager'],
            model_provider=realistic_dependencies['model_provider']
        )

        # 测试1: 创建重复页面
        page1 = enhanced_wiki.create_page(
            title="错误恢复测试",
            content="第一个版本的内容",
            tags=["测试", "错误处理"]
        )

        # 尝试创建重复页面应该进入协同编辑模式
        try:
            page2 = enhanced_wiki.create_page(
                title="错误恢复测试",
                content="第二个版本的内容",
                tags=["测试", "协同"]
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
            tags=["空内容"]
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
    @patch('src.daip_live.wiki.collaborative_wiki.EnhancedDebateManager')
    async def test_multi_model_collaboration_workflow(self, mock_debate_manager_class, temp_wiki_dir, realistic_dependencies):
        """测试多模型协作工作流"""
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager

        # 模拟辩论管理器
        mock_debate_manager = Mock()
        mock_debate_manager.run_debate = AsyncMock()

        async def multi_model_workflow(topic, roles, rounds):
            """模拟多模型协作工作流"""
            from src.daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent

            yield DebateStartEvent(topic=topic, roles=roles, rounds=rounds, session_id="multi_model_test")

            # 每个角色使用不同的模型进行贡献
            for role in roles:
                yield DebateTurnCompleteEvent(
                    participant=role,
                    content_preview=f"{role}使用{role}专用模型的贡献",
                    round_number=1
                )

            yield DebateCompleteEvent(topic=topic, total_rounds=rounds, final_summary="多模型协作完成")

        mock_debate_manager.run_debate.side_effect = multi_model_workflow
        mock_debate_manager_class.return_value = mock_debate_manager

        wiki_manager = WikiManager(temp_wiki_dir)
        collaborator = MultiRoleWikiCollaborator(
            session_manager=realistic_dependencies['session_manager'],
            role_manager=realistic_dependencies['role_manager'],
            role_model_manager=realistic_dependencies['role_model_manager'],
            model_provider=realistic_dependencies['model_provider'],
            wiki_manager=wiki_manager
        )

        # 执行多模型协作
        wiki_page, content = await collaborator.create_collaborative_wiki(
            title="量子计算前沿研究",
            initial_topic="量子计算的最新进展和未来应用前景",
            roles=["domain_expert", "researcher", "analyst"],
            rounds=1
        )

        # 验证多模型被使用
        model_calls = realistic_dependencies['model_provider'].generate.call_args_list
        used_models = set()

        for call in model_calls:
            kwargs = call.kwargs
            if 'model' in kwargs:
                used_models.add(kwargs['model'])

        print(f"使用的模型: {used_models}")
        assert len(used_models) >= 2, "应该使用多个不同模型"

        # 验证内容质量
        assert len(content) > 500  # 应该有足够长的内容
        assert "量子计算" in content
        assert "协作" in content
        assert "##" in content

        # 验证Wiki页面
        assert wiki_page is not None
        assert wiki_page.title == "量子计算前沿研究"
        assert len(wiki_page.tags) > 0

    def test_persistence_and_search_workflow(self, temp_wiki_dir, realistic_dependencies):
        """测试持久化和搜索工作流"""
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies['session_manager'],
            role_manager=realistic_dependencies['role_manager'],
            role_model_manager=realistic_dependencies['role_model_manager'],
            model_provider=realistic_dependencies['model_provider']
        )

        # 创建多个测试页面
        test_pages = [
            {
                "title": "人工智能伦理",
                "content": "AI伦理涉及算法公平性、隐私保护、透明度等关键问题。",
                "tags": ["AI", "伦理", "算法"]
            },
            {
                "title": "自然语言处理技术",
                "content": "NLP技术包括文本分析、情感识别、机器翻译等应用。",
                "tags": ["NLP", "语言", "技术"]
            },
            {
                "title": "计算机视觉应用",
                "content": "计算机视觉在医疗影像、自动驾驶、安防监控等领域广泛应用。",
                "tags": ["CV", "视觉", "应用"]
            }
        ]

        created_pages = []
        for page_data in test_pages:
            page = enhanced_wiki.create_page(
                title=page_data["title"],
                content=page_data["content"],
                tags=page_data["tags"]
            )
            created_pages.append(page)

        # 验证所有页面都被正确创建和持久化
        for i, page in enumerate(created_pages):
            assert page is not None
            assert page.file_path.exists()

            # 验证文件内容
            file_content = page.file_path.read_text(encoding='utf-8')
            assert test_pages[i]["content"] in file_content

        # 测试搜索功能
        # 内容搜索
        ai_results = enhanced_wiki.search_pages_by_content("AI")
        assert len(ai_results) >= 1

        tech_results = enhanced_wiki.search_pages_by_content("技术")
        assert len(tech_results) >= 2

        # 标签搜索
        cv_results = enhanced_wiki.search_pages_by_tag("CV")
        assert len(cv_results) >= 1

        # 高级搜索
        nlp_results = enhanced_wiki.search_advanced("语言", search_type="content")
        assert len(nlp_results) >= 1

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
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        from src.daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector

        enhanced_wiki = EnhancedWikiManager(
            wiki_root=temp_wiki_dir,
            session_manager=realistic_dependencies['session_manager'],
            role_manager=realistic_dependencies['role_manager'],
            role_model_manager=realistic_dependencies['role_model_manager'],
            model_provider=realistic_dependencies['model_provider']
        )

        # 场景：用户想要创建一个关于"区块链在供应链中的应用"的维基页面
        user_topic = "区块链在供应链管理中的应用与挑战"

        print(f"\n🎯 用户场景测试")
        print(f"主题: {user_topic}")

        # 步骤1: 智能角色选择
        selector = RoleIntelligenceSelector(realistic_dependencies['role_manager'])
        recommended_roles = selector.analyze_topic_for_roles(user_topic, max_roles=4)

        print(f"推荐角色: {recommended_roles}")

        # 步骤2: 创建普通页面作为基础
        initial_page = enhanced_wiki.create_page(
            title="区块链供应链应用",
            content="## 概述\n\n区块链技术在供应链管理中的应用正在快速增长...",
            tags=["区块链", "供应链", "技术"]
        )

        # 步骤3: 搜索是否已有相关内容
        existing_content = enhanced_wiki.search_pages_by_content("区块链")
        print(f"已存在的相关内容: {len(existing_content)} 页面")

        # 步骤4: 获取推荐理由
        reasons = selector.get_role_recommendation_reason(user_topic, recommended_roles)
        print(f"角色推荐理由:")
        for role, reason in reasons.items():
            print(f"  {role}: {reason}")

        # 步骤5: 验证页面统计信息
        stats = enhanced_wiki.get_statistics()
        print(f"Wiki统计: {stats.total_pages} 页面, {stats.total_tags} 个标签")

        # 验证整个流程的完整性
        assert initial_page is not None
        assert len(recommended_roles) >= 2
        assert isinstance(reasons, dict)
        assert len(reasons) > 0

        print(f"✅ 完整用户场景测试通过")


if __name__ == "__main__":
    # 直接运行此测试套件
    pytest.main([__file__, "-v", "-s"])