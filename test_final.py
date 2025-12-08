#!/usr/bin/env python3
"""
最终测试：模块化辩论系统
"""

def test_final():
    print("=== 最终测试开始 ===")

    try:
        # 直接导入模块化系统，跳过复杂的CLI
        print("1. 直接导入模块化系统...")
        from debate_module.clean_simple_debate import CleanSimpleDebateEngine
        print("✅ 模块化系统导入成功")

        # 创建引擎实例
        print("2. 创建辩论引擎...")
        engine = CleanSimpleDebateEngine()
        print("✅ 辩论引擎创建成功")

        # 运行辩论
        print("3. 开始运行辩论演示...")
        topic = "模块化设计的优势"
        roles = ["支持者", "反对者"]

        event_count = 0
        async for event in engine.run_debate(topic, roles, rounds=1):
            event_count += 1
            event_type = event.get("type", "unknown")

            if event_type == "debate_start":
                print(f"📦 辩论开始: {event.get('topic')}")
            elif event_type == "turn_start":
                print(f"💬 {event.get('role')} 第{event.get('round')}轮发言:")
                content = event.get("content", "")[:50] + "..." if len(event.get("content", "")) > 50 else ""
                print(f"   {content}")
            elif event_type == "turn_complete":
                print(f"✅ {event.get('role')} 发言完成")
            elif event_type == "debate_complete":
                print(f"🎯 辩论完成！")
                print(f"   摘要: {event.get('conclusion')}")
                print(f"   执行时间: {event.get('execution_time', 0):.2f}秒")
                break

            if event_count > 10:
                print("⚠️ 达到最大事件数，停止测试")
                break

        print(f"✅ 辩论测试完成，共处理 {event_count} 个事件")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final()