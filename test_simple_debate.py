#!/usr/bin/env python3
"""
独立的简化辩论测试
不依赖容器系统，直接测试辩论逻辑
"""
import sys
import asyncio
import time
sys.path.insert(0, 'src')

from daip_live.p8_debate_system.simple_debate_manager import SimpleDebateManager

# 模拟必要的组件
class MockSessionManager:
    pass

class MockRoleManager:
    pass

class MockModelProvider:
    pass

async def test_simple_debate():
    print("=== 简化辩论测试开始 ===")

    try:
        # 创建模拟组件
        session_manager = MockSessionManager()
        role_manager = MockRoleManager()
        model_provider = MockModelProvider()

        # 创建简化辩论管理器
        debate_manager = SimpleDebateManager.create_simple_debate(
            session_manager=session_manager,
            role_manager=role_manager,
            model_provider=model_provider
        )

        print("✅ 简化辩论管理器创建成功")

        # 运行辩论
        topic = "AI的未来发展"
        roles = ["pro_arguer", "con_arguer"]
        rounds = 1

        print(f"🎮 开始辩论: {topic}")

        event_count = 0
        async for event in debate_manager.run_debate(topic, roles, rounds):
            event_count += 1
            print(f"📦 事件 {event_count}: {type(event).__name__}")

            if event_count > 5:  # 防止无限循环
                print("⚠️ 达到最大事件数，停止测试")
                break

        print(f"✅ 辩论测试完成，共处理 {event_count} 个事件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_debate())