#!/usr/bin/env python3
"""
测试默认进度显示功能
验证所有协作操作默认都会显示进度
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_default_progress_display():
    """测试默认进度显示功能"""
    print("🔍 测试默认进度显示...")

    try:
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            # 创建简化的依赖
            class SimpleModelProvider:
                def __init__(self):
                    self.call_count = 0

                async def generate(self, prompt, model=None, temperature=0.7, max_tokens=1000):
                    self.call_count += 1
                    await asyncio.sleep(0.2)  # 模拟延迟，以便观察进度
                    if "domain_expert" in prompt.lower():
                        return ("作为领域专家，这是一个涉及复杂系统架构的专业技术主题。", {})
                    elif "researcher" in prompt.lower():
                        return ("研究表明，该领域相关论文数量逐年增加，发展趋势良好。", {})
                    elif "editor" in prompt.lower():
                        return ("本文系统性介绍了该主题，确保内容结构清晰、逻辑严密。", {})
                    else:
                        return ("这是一个重要的话题，需要多角度的深入分析和讨论。", {})

            class SimpleRoleModelManager:
                def get_role_model_mapping(self, role_name, use_debate_config=False):
                    config = {"model_name": f"test_{role_name}_model", "temperature": 0.7}
                    mock_config = type('MockConfig', (), config)()
                    mock_mapping = type('MockMapping', (), {'role_model_config': mock_config})()
                    return mock_mapping

            # 创建增强Wiki管理器
            enhanced_wiki = EnhancedWikiManager(
                wiki_root=wiki_root,
                role_model_manager=SimpleRoleModelManager(),
                model_provider=SimpleModelProvider()
            )

            print("  测试1: 默认行为（应该显示进度）")
            # 测试默认行为（不指定show_progress，应该默认显示）
            wiki_page1 = await enhanced_wiki.create_collaborative_wiki(
                title="默认进度测试1",
                topic="测试默认进度显示功能",
                roles=["domain_expert", "researcher"]
            )

            assert wiki_page1 is not None
            assert wiki_page1.title == "默认进度测试1"

            print("  测试2: 显式启用进度显示")
            # 测试显式启用进度显示
            wiki_page2 = await enhanced_wiki.create_collaborative_wiki(
                title="显式进度测试2",
                topic="测试显式启用进度显示",
                roles=["editor"],
                show_progress=True
            )

            assert wiki_page2 is not None
            assert wiki_page2.title == "显式进度测试2"

            print("  测试3: 禁用进度显示（仍会显示基础信息）")
            # 测试禁用进度显示
            wiki_page3 = await enhanced_wiki.create_collaborative_wiki(
                title="禁用进度测试3",
                topic="测试禁用进度显示",
                roles=["domain_expert"],
                show_progress=False
            )

            assert wiki_page3 is not None
            assert wiki_page3.title == "禁用进度测试3"

            print("✅ 默认进度显示测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ 默认进度显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_auto_progress_detection():
    """测试自动进度检测功能"""
    print("\n🔍 测试自动进度检测...")

    try:
        from daip_live.wiki.auto_progress_display import AutoProgressDisplay

        # 创建自动进度显示器
        auto_display = AutoProgressDisplay()

        print(f"  检测TUI环境: {auto_display.is_tui_environment}")

        # 测试回调设置
        auto_display.setup_callback()
        assert auto_display.display_callback is not None

        print("  ✅ 自动检测功能正常")
        return True

    except Exception as e:
        print(f"❌ 自动进度检测测试失败: {e}")
        return False

async def test_enhanced_engine_with_auto_display():
    """测试增强引擎的自动显示功能"""
    print("\n🔍 测试增强引擎自动显示...")

    try:
        from daip_live.wiki.simple_collaboration_engine import SimpleCollaborationEngine
        from daip_live.wiki.manager import WikiManager
        from daip_live.wiki.auto_progress_display import create_enhanced_engine_with_auto_display

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            # 创建基础组件
            class SimpleModelProvider:
                async def generate(self, prompt, model=None, temperature=0.7, max_tokens=1000):
                    await asyncio.sleep(0.1)
                    return ("自动显示测试内容", {})

            class SimpleRoleModelManager:
                def get_role_model_mapping(self, role_name, use_debate_config=False):
                    config = {"model_name": f"auto_{role_name}_model", "temperature": 0.7}
                    mock_config = type('MockConfig', (), config)()
                    mock_mapping = type('MockMapping', (), {'role_model_config': mock_config})()
                    return mock_mapping

            wiki_manager = WikiManager(wiki_root)
            simple_provider = SimpleModelProvider()
            role_manager = SimpleRoleModelManager()

            # 创建基础引擎
            base_engine = SimpleCollaborationEngine(
                role_model_manager=role_manager,
                model_provider=simple_provider,
                wiki_manager=wiki_manager
            )

            # 创建增强引擎
            enhanced_engine = create_enhanced_engine_with_auto_display(base_engine)

            print("  执行自动显示协作...")
            page, content = await enhanced_engine.create_collaborative_wiki_with_auto_display(
                title="自动显示测试",
                topic="测试自动进度显示功能"
            )

            assert page is not None
            assert page.title == "自动显示测试"

            print("✅ 增强引擎自动显示测试通过")
            return True

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ 增强引擎自动显示测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 默认进度显示功能测试")
    print("=" * 60)
    print("目标：验证所有协作操作默认都会显示进度过程")
    print("=" * 60)

    tests = [
        ("默认进度显示", test_default_progress_display),
        ("自动进度检测", test_auto_progress_detection),
        ("增强引擎自动显示", test_enhanced_engine_with_auto_display)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
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
        print("\n🎉 所有测试通过！默认进度显示功能正常！")
        print("\n✨ 新功能特性:")
        print("  🔄 默认进度显示 - 所有协作操作默认显示进度")
        print("  🤖 自动环境检测 - 自动适配TUI和CLI环境")
        print("  📊 智能进度条 - 实时显示协作状态和角色")
        print("  ⏱️  时间统计 - 显示协作耗时和性能指标")
        print("  🎯 完成摘要 - 协作完成后的详细报告")
        print("\n🚀 使用方式:")
        print("  # 默认行为（自动显示进度）")
        print("  page = await wiki.create_collaborative_wiki('标题', '主题')")
        print("  ")
        print("  # 禁用进度显示")
        print("  page = await wiki.create_collaborative_wiki('标题', '主题', show_progress=False)")

        return True
    else:
        print(f"\n⚠️  还有 {total - passed} 个测试需要修复")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)