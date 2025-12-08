#!/usr/bin/env python3
"""
简单的辩论系统测试脚本
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_debate_system():
    print("🔍 测试辩论系统...")

    try:
        # 导入必要的模块
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.core.models import DebateStartEvent
        from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
        from daip_live.p8_debate_system.model_availability_checker import perform_model_check

        print("✅ 成功导入所有辩论模块")

        # 1. 检查模型可用性
        print("\n📊 检查模型可用性...")
        is_model_ok, check_message = await perform_model_check()
        print(f"模型检查结果: {is_model_ok}, {check_message}")

        if not is_model_ok:
            print("❌ 模型检查失败，尝试继续...")

        # 2. 初始化组件
        print("\n🔧 初始化辩论组件...")
        model_provider = LiteLLMProvider()
        role_model_manager = RoleModelManager()
        debate_manager = EnhancedDebateManager(model_provider, role_model_manager)
        history_tracker = DebateHistoryTracker()

        print("✅ 辩论组件初始化成功")

        # 3. 测试简单的辩论事件流
        print("\n🎯 测试辩论事件流...")
        topic = "AI的未来发展"
        roles = ["pro_arguer", "con_arguer"]

        # 创建测试开始事件
        session_id = f"test_debate_{int(asyncio.get_event_loop().time())}"
        start_event = DebateStartEvent(
            topic=topic,
            roles=roles,
            rounds=1,
            session_id=session_id
        )

        print(f"✅ 创建辩论开始事件: {start_event}")

        # 4. 开始测试辩论流
        print("\n🚀 开始辩论流测试...")
        event_count = 0

        async for event in debate_manager.run_debate(topic, roles, 1):
            event_count += 1
            print(f"📻 收到事件 {event_count}: {type(event).__name__}")

            if event_count >= 10:  # 限制事件数量以避免无限循环
                print("⏹️ 达到事件数量限制，停止测试")
                break

        print(f"\n✅ 辩论流测试完成，共处理 {event_count} 个事件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_debate_system())