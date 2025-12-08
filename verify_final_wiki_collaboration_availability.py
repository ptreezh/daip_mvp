#!/usr/bin/env python3
"""
最终验证测试 - 多模型Wiki协作功能可用性验证
基于TDD驱动的完整验证，确认功能修复后的可用性
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

async def test_role_intelligence_selector():
    """测试角色智能选择器"""
    print("🔍 测试角色智能选择器...")

    try:
        from src.daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector
        from unittest.mock import Mock

        # 模拟RoleManager
        mock_role_manager = Mock()
        mock_role_manager.list_roles.return_value = ["domain_expert", "researcher", "editor", "critic", "analyst", "teacher"]

        # 创建选择器
        selector = RoleIntelligenceSelector(mock_role_manager)

        # 测试多种主题
        test_cases = [
            "机器学习算法原理",
            "AI市场分析报告",
            "Python编程入门教程",
            "技术方案评审"
        ]

        for topic in test_cases:
            roles = selector.analyze_topic_for_roles(topic, max_roles=4)
            print(f"  主题: {topic}")
            print(f"  选择角色: {roles}")
            assert isinstance(roles, list)
            assert len(roles) > 0

            # 测试上下文增强
            enhanced_roles = selector.enhance_role_selection_with_context(
                topic,
                context={"target_audience": "professionals", "content_type": "technical"}
            )
            assert isinstance(enhanced_roles, list)
            assert len(enhanced_roles) > 0

        print("✅ 角色智能选择器测试通过")
        return True

    except Exception as e:
        print(f"❌ 角色智能选择器测试失败: {e}")
        return False

async def test_wiki_manager_basic():
    """测试Wiki管理器基本功能"""
    print("\n🔍 测试Wiki管理器基本功能...")

    try:
        from src.daip_live.wiki.manager import WikiManager

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            wiki_manager = WikiManager(wiki_root)

            # 测试创建页面
            page = wiki_manager.create_page(
                title="测试页面",
                content="这是一个测试页面的内容",
                tags=["测试", "wiki"]
            )

            assert page is not None
            assert page.title == "测试页面"
            assert len(page.content) > 0

            # 测试获取页面
            found_page = wiki_manager.get_page_by_title("测试页面")
            assert found_page is not None
            assert found_page.title == page.title

            # 测试搜索功能
            search_results = wiki_manager.search_pages_by_content("测试")
            assert len(search_results) >= 1

            # 测试统计功能
            stats = wiki_manager.get_statistics()
            assert stats.total_pages >= 1

            print("✅ Wiki管理器基本功能测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ Wiki管理器基本功能测试失败: {e}")
        return False

async def test_enhanced_wiki_manager():
    """测试增强Wiki管理器"""
    print("\n🔍 测试增强Wiki管理器...")

    try:
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        from unittest.mock import Mock, AsyncMock

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            # 创建模拟依赖
            mock_session = Mock()
            mock_session.session_id = "test_session"

            mock_session_manager = Mock()
            mock_session_manager.create_session.return_value = mock_session

            mock_role_manager = Mock()
            mock_role_manager.list_roles.return_value = ["domain_expert", "researcher"]

            mock_role_model_manager = Mock()
            mock_role_model_manager.get_role_model_mapping.return_value = Mock(
                role_model_config=Mock(model_name="test_model", temperature=0.7, max_tokens=1000)
            )

            mock_model_provider = Mock()
            mock_model_provider.generate = AsyncMock(return_value=("测试内容", {}))

            # 测试不完整依赖的情况
            incomplete_wiki = EnhancedWikiManager(wiki_root=wiki_root)
            assert incomplete_wiki.collaborator is None

            # 测试完整依赖的情况
            complete_wiki = EnhancedWikiManager(
                wiki_root=wiki_root,
                session_manager=mock_session_manager,
                role_manager=mock_role_manager,
                role_model_manager=mock_role_model_manager,
                model_provider=mock_model_provider
            )

            assert complete_wiki.collaborator is not None

            # 测试基本页面创建
            page = complete_wiki.create_page(
                title="增强Wiki测试",
                content="这是增强Wiki管理器的测试页面",
                tags=["增强", "测试"]
            )

            assert page is not None
            assert page.title == "增强Wiki测试"

            print("✅ 增强Wiki管理器测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ 增强Wiki管理器测试失败: {e}")
        return False

async def test_multi_role_collaborator():
    """测试多角色协作器"""
    print("\n🔍 测试多角色协作器...")

    try:
        from src.daip_live.wiki.collaborative_wiki import MultiRoleWikiCollaborator
        from src.daip_live.wiki.manager import WikiManager
        from unittest.mock import Mock, AsyncMock

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            # 创建模拟依赖
            mock_session = Mock()
            mock_session.session_id = "collaborator_test"

            mock_session_manager = Mock()
            mock_session_manager.create_session.return_value = mock_session

            mock_role_manager = Mock()
            mock_role_manager.list_roles.return_value = ["domain_expert", "researcher", "editor"]

            mock_role_model_manager = Mock()
            mock_role_model_manager.get_role_model_mapping.return_value = Mock(
                role_model_config=Mock(model_name="test_model", temperature=0.7, max_tokens=1000)
            )

            mock_model_provider = Mock()
            mock_model_provider.generate = AsyncMock(return_value=("协作生成内容", {}))

            wiki_manager = WikiManager(wiki_root)

            # 创建协作器
            collaborator = MultiRoleWikiCollaborator(
                session_manager=mock_session_manager,
                role_manager=mock_role_manager,
                role_model_manager=mock_role_model_manager,
                model_provider=mock_model_provider,
                wiki_manager=wiki_manager
            )

            # 测试基本属性
            assert collaborator.wiki_manager is wiki_manager
            assert len(collaborator.default_roles) > 0

            # 测试内容合成（绕过复杂的辩论系统）
            contributions = {
                "domain_expert": ["专业技术内容"],
                "researcher": ["研究数据支撑"],
                "editor": ["编辑整理内容"]
            }

            content = await collaborator._synthesize_wiki_content(
                title="协作测试",
                contributions=contributions,
                topic="协作测试主题"
            )

            assert len(content) > 0
            assert "# 协作测试" in content
            assert "##" in content  # 应该有章节结构

            print("✅ 多角色协作器测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ 多角色协作器测试失败: {e}")
        return False

async def test_wiki_search_and_statistics():
    """测试Wiki搜索和统计功能"""
    print("\n🔍 测试Wiki搜索和统计功能...")

    try:
        from src.daip_live.wiki.manager import WikiManager

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            wiki_manager = WikiManager(wiki_root)

            # 创建多个测试页面
            test_pages = [
                ("机器学习", "机器学习是AI的核心技术", ["AI", "ML"]),
                ("深度学习", "深度学习使用神经网络", ["DL", "NN"]),
                ("自然语言处理", "NLP处理文本数据", ["NLP", "文本"]),
                ("计算机视觉", "CV处理图像数据", ["CV", "图像"])
            ]

            for title, content, tags in test_pages:
                wiki_manager.create_page(title, content, tags)

            # 测试内容搜索
            ml_results = wiki_manager.search_pages_by_content("学习")
            assert len(ml_results) >= 2

            # 测试标签搜索
            ai_results = wiki_manager.search_pages_by_tag("AI")
            assert len(ai_results) >= 1

            # 测试高级搜索
            tech_results = wiki_manager.search_advanced("技术", search_type="content")
            assert len(tech_results) >= 1

            # 测试统计功能
            stats = wiki_manager.get_statistics()
            assert stats.total_pages == 4
            assert stats.total_tags > 0
            assert stats.total_words > 0
            assert len(stats.most_used_tags) > 0

            # 测试最近页面
            recent_pages = wiki_manager.get_recent_pages(limit=3)
            assert len(recent_pages) == 3

            print("✅ Wiki搜索和统计功能测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ Wiki搜索和统计功能测试失败: {e}")
        return False

async def test_error_handling():
    """测试错误处理"""
    print("\n🔍 测试错误处理...")

    try:
        from src.daip_live.wiki.manager import WikiManager
        from src.daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            wiki_manager = WikiManager(wiki_root)

            # 测试获取不存在的页面
            non_existent = wiki_manager.get_page_by_title("绝对不存在的页面")
            assert non_existent is None

            # 测试更新不存在的页面
            try:
                wiki_manager.update_page("不存在的页面", "内容")
                assert False, "应该抛出异常"
            except ValueError:
                pass  # 期望的异常

            # 测试删除不存在的页面
            result = wiki_manager.delete_page("不存在的页面")
            assert result is False

            # 测试EnhancedWikiManager的错误处理
            enhanced_wiki = EnhancedWikiManager(wiki_root=wiki_root)
            assert enhanced_wiki.collaborator is None

            try:
                await enhanced_wiki.create_collaborative_wiki("测试", "主题")
                assert False, "应该抛出RuntimeError"
            except RuntimeError:
                pass  # 期望的异常

            print("✅ 错误处理测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 多模型Wiki协作功能最终可用性验证")
    print("=" * 60)

    tests = [
        ("角色智能选择器", test_role_intelligence_selector),
        ("Wiki管理器基本功能", test_wiki_manager_basic),
        ("增强Wiki管理器", test_enhanced_wiki_manager),
        ("多角色协作器", test_multi_role_collaborator),
        ("Wiki搜索和统计", test_wiki_search_and_statistics),
        ("错误处理", test_error_handling)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))

    # 统计结果
    print("\n" + "=" * 60)
    print("📊 测试结果统计:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总体结果: {passed}/{total} 测试通过")
    print(f"成功率: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 所有测试通过！多模型Wiki协作功能可用！")
        print("\n✨ 功能特性:")
        print("  🔍 智能角色选择器 - 根据主题自动推荐适合的角色组合")
        print("  📝 Wiki管理器 - 完整的页面创建、搜索、统计功能")
        print("  🤖 增强协作器 - 支持多角色AI协作创建内容")
        print("  🏷️  标签系统 - 智能标签提取和分类管理")
        print("  🔍 搜索功能 - 内容搜索、标签搜索、高级搜索")
        print("  📊 统计分析 - 页面统计、标签分析、使用情况")
        print("  🛡️  错误处理 - 完善的异常处理和回退机制")
        print("\n🚀 现在可以通过以下方式使用:")
        print("  1. TUI界面: daip run")
        print("  2. CLI命令: daip wiki create '主题'")
        print("  3. 程序化调用: EnhancedWikiManager.create_collaborative_wiki()")

        return True
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试需要修复")
        print("建议继续完善相关功能")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)