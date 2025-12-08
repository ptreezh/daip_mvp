#!/usr/bin/env python3
"""
测试容器初始化和辩论系统
""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_container():
    print("🔍 测试容器初始化...")

    try:
        # 导入容器
        from daip_live.container import Container
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        from daip_live.p8_debate_system.model_availability_checker import perform_model_check

        print("✅ 成功导入容器模块")

        # 1. 检查模型可用性
        print("\n📊 检查模型可用性...")
        is_model_ok, check_message = await perform_model_check()
        print(f"模型检查结果: {is_model_ok}, {check_message}")

        # 2. 初始化容器
        print("\n🏗️ 初始化容器...")
        container = Container()

        # 3. 获取辩论管理器（使用from_container方法）
        print("\n🎯 获取辩论管理器...")
        debate_manager = container.debate_manager()
        print(f"✅ 辩论管理器: {type(debate_manager)}")

        # 4. 测试简单的辩论流
        print("\n🚀 测试辩论流...")
        topic = "AI的未来发展"
        roles = ["pro_arguer", "con_arguer"]

        event_count = 0
        print("开始异步迭代辩论事件...")

        async for event in debate_manager.run_debate(topic, roles, 1):
            event_count += 1
            print(f"📻 事件 {event_count}: {type(event).__name__}")

            # 只处理前5个事件以避免卡住
            if event_count >= 5:
                print("⏹️ 达到测试限制，停止")
                break

        print(f"\n✅ 辩论流测试完成，处理了 {event_count} 个事件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_container())
