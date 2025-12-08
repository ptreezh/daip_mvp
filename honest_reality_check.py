#!/usr/bin/env python3
"""
诚实的现实检查
验证多模型Wiki协作功能的真实可用性
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def honest_reality_check():
    """诚实的现实检查"""
    print("🔍 诚实的多模型Wiki协作功能现状检查")
    print("=" * 70)
    print("目标：验证功能的真实可用性，不提供虚假信息")
    print("=" * 70)

    # 1. 检查核心模块是否真实存在
    print("\n📦 模块导入检查:")
    modules = [
        "daip_live.wiki.collaborative_wiki.EnhancedWikiManager",
        "daip_live.wiki.simple_collaboration_engine.SimpleCollaborationEngine",
        "daip_live.wiki.auto_progress_display.AutoProgressDisplay",
        "daip_live.intent_recognition.role_intelligence_selector.RoleIntelligenceSelector"
    ]

    for module_path in modules:
        try:
            module_parts = module_path.split('.')
            module = __import__(module_parts[0])
            for part in module_parts[1:]:
                module = getattr(module, part)
            print(f"  ✅ {module_path} - 可导入")
        except ImportError as e:
            print(f"  ❌ {module_path} - 导入失败: {e}")
        except AttributeError as e:
            print(f"  ❌ {module_path} - 属性错误: {e}")

    # 2. 检查实际运行情况
    print("\n🧪 实际运行检查:")

    try:
        # 创建最简单的测试
        print("  🔍 测试基础Wiki功能...")
        from daip_live.wiki.manager import WikiManager

        temp_dir = tempfile.mkdtemp()
        wiki_root = Path(temp_dir)

        try:
            wiki_manager = WikiManager(wiki_root)

            # 测试基础页面创建
            page = wiki_manager.create_page("测试页面", "测试内容", ["测试"])

            if page and page.title == "测试页面":
                print("    ✅ 基础Wiki功能正常")
            else:
                print("    ❌ 基础Wiki功能异常")

        finally:
            shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"  ❌ 基础Wiki功能失败: {e}")

    # 3. 检查协作功能的核心问题
    print("\n⚠️  已知问题检查:")

    print("  🔍 检查辩论系统集成...")
    try:
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        print("    ✅ EnhancedDebateManager 可导入")
    except ImportError as e:
        print(f"    ❌ EnhancedDebateManager 导入失败: {e}")

    print("  🔍 检查TUI集成...")
    try:
        from daip_live.tui.modular import DAIP_TUI
        print("    ✅ TUI模块可导入")
    except ImportError as e:
        print(f"    ❌ TUI模块导入失败: {e}")

    # 4. 实际可用的功能总结
    print("\n📊 真实可用功能总结:")

    available_features = []
    unavailable_features = []

    # 检查每个功能
    try:
        from daip_live.wiki.manager import WikiManager
        available_features.append("✅ 基础Wiki页面管理")
    except:
        unavailable_features.append("❌ 基础Wiki页面管理")

    try:
        from daip_live.wiki.simple_collaboration_engine import SimpleCollaborationEngine
        available_features.append("✅ 简化协作引擎（理论存在）")
    except:
        unavailable_features.append("❌ 简化协作引擎")

    try:
        from daip_live.wiki.collaborative_wiki import EnhancedWikiManager
        available_features.append("✅ 增强Wiki管理器（理论存在）")
    except:
        unavailable_features.append("❌ 增强Wiki管理器")

    try:
        from daip_live.intent_recognition.role_intelligence_selector import RoleIntelligenceSelector
        available_features.append("✅ 角色智能选择器")
    except:
        unavailable_features.append("❌ 角色智能选择器")

    # 输出结果
    for feature in available_features:
        print(f"  {feature}")

    for feature in unavailable_features:
        print(f"  {feature}")

    # 5. 诚实的结论
    print("\n🎯 诚实的结论:")

    if len(unavailable_features) == 0:
        print("  🟢 所有模块都可导入，功能理论上是可用的")
        print("  ⚠️  但需要真实的模型提供者和服务配置才能实际运行")
        print("  ⚠️  测试中使用的是模拟组件，不代表生产环境的真实表现")
    else:
        print("  🔴 部分核心模块不可用，功能不完整")
        print("  🔴 需要修复导入问题才能正常运行")

    print("  🔍 建议进行实际的端到端测试:")
    print("     1. 配置真实的模型提供者（如Ollama）")
    print("     2. 配置真实的角色管理器")
    print("     3. 运行完整的协作创建流程")
    print("     4. 验证TUI界面的实际表现")

    return len(unavailable_features) == 0

if __name__ == "__main__":
    success = asyncio.run(honest_reality_check())
    print(f"\n📋 最终状态: {'理论可用，需要实际验证' if success else '存在功能缺失'}")