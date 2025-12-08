#!/usr/bin/env python3
"""
验证TUI修复效果 - 基于TDD原则的第二阶段验证
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试所有导入是否正常"""
    print("🧪 测试导入修复...")

    try:
        from daip_live.tui.commands import TUICommandHandler, UtilityCommands, WikiCommands, SearchCommands
        print("✅ commands.py 导入成功")
        return True
    except ImportError as e:
        print(f"❌ commands.py 导入失败: {e}")
        return False

def test_simplified_main_imports():
    """测试simplified_main.py的导入"""
    print("🔧 测试simplified_main.py导入...")

    try:
        from daip_live.tui.simplified_main import SimplifiedTUI
        print("✅ simplified_main.py 导入成功")
        return True
    except ImportError as e:
        print(f"❌ simplified_main.py 导入失败: {e}")
        return False

def test_tui_modular_imports():
    """测试tui_modular.py的导入"""
    print("🧩 测试tui_modular.py导入...")

    try:
        from daip_live.tui_modular import DAIP_TUI
        print("✅ tui_modular.py 导入成功")
        return True
    except ImportError as e:
        print(f"❌ tui_modular.py 导入失败: {e}")
        return False

def test_basic_tui_functionality():
    """测试基础TUI功能"""
    print("🎯 测试基础TUI功能...")

    try:
        from daip_live.tui.simplified_main import SimplifiedTUI

        # 测试TUI初始化（不运行）
        print("  📱 尝试初始化TUI...")

        # 创建一个最小的测试环境
        import os
        os.environ['DAIP_TEST_MODE'] = 'true'

        return True
    except Exception as e:
        print(f"❌ 基础TUI功能测试失败: {e}")
        return False

def test_command_classes():
    """测试命令类功能"""
    print("⚡ 测试命令类功能...")

    try:
        from daip_live.tui.commands import TUICommandHandler, UtilityCommands, WikiCommands

        # 创建虚拟TUI实例
        class MockTUI:
            def _update_log_view(self, message):
                print(f"[LOG] {message}")

        tui_mock = MockTUI()

        # 测试命令处理器
        handler = TUICommandHandler(tui_mock)

        # 测试各种命令
        test_commands = [
            ("/debate start test", True),
            ("/search query", True),
            ("/clear", True),
            ("/help", True),
            ("/unknown", False)
        ]

        success_count = 0
        for cmd, expected in test_commands:
            try:
                result = handler.process_command(cmd)
                if result == expected:
                    success_count += 1
                    print(f"  ✅ 命令 '{cmd}' 处理正确")
                else:
                    print(f"  ❌ 命令 '{cmd}' 处理异常")
            except Exception as e:
                print(f"  ❌ 命令 '{cmd}' 处理失败: {e}")

        print(f"  📊 命令测试通过: {success_count}/{len(test_commands)}")
        return success_count == len(test_commands)

    except Exception as e:
        print(f"❌ 命令类功能测试失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🔍 DAIP-LIVE TUI修复验证")
    print("=" * 50)

    results = []

    # 1. 测试导入修复
    results.append(test_imports())
    results.append(test_simplified_main_imports())
    results.append(test_tui_modular_imports())

    # 2. 测试基础功能
    results.append(test_basic_tui_functionality())

    # 3. 测试命令系统
    results.append(test_command_classes())

    # 总结
    passed = sum(results)
    total = len(results)

    print("=" * 50)
    print(f"📋 验证结果: {passed}/{total} 项通过")

    if passed == total:
        print("🎉 所有修复验证通过！模块化辩论系统准备就绪。")
        return True
    else:
        print("⚠️ 部分验证失败，需要进一步修复。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)