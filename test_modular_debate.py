#!/usr/bin/env python3
"""
测试模块化辩论系统
"""
import sys
import asyncio
import time
sys.path.insert(0, 'debate_module')

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from debate_module.simple_debate import SimpleDebateEngine

async def test_modular_debate():
    print("=== 模块化辩论系统测试 ===")

    try:
        # 创建辩论引擎
        engine = SimpleDebateEngine()
        print("✅ 辩论引擎创建成功")

        # 运行辩论
        topic = "模块化辩论的优势"
        roles = ["支持者", "反对者"]
        rounds = 2

        print(f"🎮 开始辩论: {topic}")
        print(f"👥 角色: {roles}")
        print(f"🔢 轮次: {rounds}")

        event_count = 0
        async for event in engine.run_debate(topic, roles, rounds):
            event_count += 1
            event_type = event.get("type", "unknown")

            if event_type == "debate_start":
                print(f"📦 辩论开始: {event.get('topic')}")
            elif event_type == "turn_complete":
                print(f"💬 {event.get('role')} 发言: {event.get('content')[:50]}...")
            elif event_type == "complete":
                print(f"✅ 辩论完成: {event.get('conclusion')}")
            elif event_type == "error":
                print(f"❌ 错误: {event.get('error')}")

            if event_count > 10:  # 防止无限循环
                print("⚠️ 达到最大事件数，停止测试")
                break

        print(f"🎯 测试完成，共处理 {event_count} 个事件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_modular_debate())