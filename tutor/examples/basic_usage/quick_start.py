#!/usr/bin/env python3
"""
🚀 DAIP-LIVE 快速开始示例

这个示例展示了如何快速启动和使用DAIP-LIVE的核心功能。
适合初学者了解项目的基本用法和功能特性。
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.daip_live.tui.simplified_main import SimplifiedTUI


async def quick_start_demo():
    """快速开始演示"""
    print("🎓 DAIP-LIVE 快速开始演示")
    print("=" * 50)

    print("\n📋 第1步: 创建TUI实例")
    tui = SimplifiedTUI()
    print("✅ TUI实例创建成功")

    print("\n🔍 第2步: 检查可用命令")
    commands = tui._available_commands
    print(f"📝 可用命令数量: {len(commands)}")

    # 显示主要命令
    main_commands = [cmd for cmd, desc in commands if 'copy' in cmd or 'help' in cmd or 'wiki' in cmd]
    print("🎯 主要命令:")
    for cmd, desc in main_commands:
        print(f"  {cmd:<15} - {desc}")

    print("\n🎨 第3步: 模拟对话内容")
    # 添加一些模拟的对话内容
    tui._log_text_buffer = [
        "👋 欢迎使用DAIP-LIVE智能助手！",
        "🤖 这是一个展示SPEC驱动开发的AI应用系统。",
        "📚 您可以使用 /copy 命令复制对话内容。",
        "🔧 支持多种AI模型和自然语言交互。",
        "✨ 让我们一起探索AI应用开发的最佳实践！"
    ]

    print("✅ 对话内容已准备")

    print("\n📋 第4步: 测试复制功能")
    try:
        import pyperclip

        # 测试复制功能
        await tui.action_copy_text()
        print("✅ 复制功能测试成功")

        # 测试复制最近内容
        tui.copy_recent_content(3)
        print("✅ 复制最近3行内容成功")

    except ImportError:
        print("⚠️  pyperclip库未安装，复制功能不可用")
        print("💡 请运行: pip install pyperclip")

    print("\n🎯 第5步: 核心功能展示")
    print("🏗️  架构特性:")
    print("  • P1-P8 模块化设计")
    print("  • 异步优先架构")
    print("  • 隐私保护设计")
    print("  • 多模型支持")

    print("\n🤖 AI功能:")
    print("  • 自然语言对话")
    print("  • 意图识别")
    print("  • 多模型辩论")
    print("  • Wiki协作")

    print("\n🖥️  用户界面:")
    print("  • 现代化TUI")
    print("  • 命令驱动操作")
    print("  • 复制功能支持")
    print("  • 响应式设计")

    print("\n🎉 快速开始演示完成！")
    print("💡 要启动完整界面，请运行: daip run")


def show_learning_tips():
    """显示学习提示"""
    print("\n📚 学习建议:")
    print("1. 📖 先阅读项目规格书了解整体架构")
    print("2. 🎮 尝试运行TUI界面体验实际功能")
    print("3. 🔧 研究代码结构理解模块设计")
    print("4. 🤝 参与社区讨论和贡献")

    print("\n🛠️ 开发环境:")
    print("• Python 3.9+")
    print("• Poetry (推荐) 或 pip")
    print("• 现代终端支持")
    print("• Ollama (本地模型，可选)")


if __name__ == "__main__":
    try:
        asyncio.run(quick_start_demo())
        show_learning_tips()

        print("\n" + "=" * 50)
        print("🚀 准备好开始您的AI应用开发之旅了吗？")
        print("📚 更多教程请查看: tutor/tutorials/")
        print("🔧 实践练习请查看: tutor/exercises/")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 演示运行失败: {e}")
        print("💡 请检查环境配置和依赖安装")
        sys.exit(1)