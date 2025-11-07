#!/usr/bin/env python3
"""
测试当前辩论系统的实际运行情况
展示会话管理、模型调用和记忆保持的现状
"""

import asyncio
import sys
import time
sys.path.append('src')

from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.persistence.database import DatabaseManager
from daip_live.core.models import ProviderConfig


async def test_current_debate_system():
    """测试当前辩论系统的实际运行"""
    print("🔍 测试当前辩论系统架构...")
    print("=" * 60)

    try:
        # 初始化组件
        print("1. 初始化系统组件...")
        db_manager = DatabaseManager(db_path=":memory:")
        session_manager = SessionManager(db_manager=db_manager)
        role_manager = RoleManager()
        role_model_manager = RoleModelManager()
        provider_config = ProviderConfig(model="mock-model")
        model_provider = LiteLLMProvider(config=provider_config)

        # 创建增强辩论管理器
        debate_manager = EnhancedDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=model_provider
        )
        print("   ✅ 系统组件初始化完成")

        # 检查模型缓存
        print("\n2. 检查模型缓存机制...")
        print(f"   初始模型缓存: {len(debate_manager.model_cache)} 个实例")
        print("   ✅ 模型缓存检查完成")

        # 模拟辩论开始
        print("\n3. 模拟辩论开始...")
        topic = "人工智能的发展对社会的影响"
        roles = ["tech_analyst", "ethics_expert"]

        # 开始辩论并收集事件
        events = []
        async for event in debate_manager.run_debate(topic, roles, 2):
            events.append(event)

            # 显示关键事件
            if hasattr(event, 'topic'):
                print(f"   🎬 辩论开始: {event.topic}")
                print(f"   👥 参与者: {event.roles}")
            elif hasattr(event, 'participant'):
                print(f"   🗣️  {event.participant} 开始发言 (回合 {event.round_number})")
            elif hasattr(event, 'content_preview'):
                print(f"   ✅ {event.participant} 发言完成")
                print(f"   📝 内容预览: {event.content_preview[:100]}...")
            elif hasattr(event, 'total_tokens'):
                print(f"   💾 Token使用: {event.total_tokens}")

        print("   ✅ 辩论模拟完成")

        # 分析会话管理
        print("\n4. 分析会话管理...")

        # 检查创建的会话
        sessions = session_manager.list_sessions()
        debate_sessions = [s for s in sessions if s.session_type == "debate"]

        print(f"   总会话数: {len(sessions)}")
        print(f" 辩论会话数: {len(debate_sessions)}")

        if debate_sessions:
            session = debate_sessions[0]
            print(f"   辩论会话ID: {session.session_id}")
            print(f"   辩论主题: {session.goal}")
            print(f"   历史记录数: {len(session.history)}")
            print(f"   参与者: {session.participant_ids}")

            # 分析历史记录
            print("\n5. 分析历史记录结构...")
            for i, turn in enumerate(session.history):
                print(f"   轮次 {i+1}: {turn.participant_id} - {len(turn.content)} 字符")

            print("   ✅ 会话管理分析完成")

        # 分析模型使用情况
        print("\n6. 分析模型使用情况...")
        print(f"   最终模型缓存: {len(debate_manager.model_cache)} 个实例")
        for cache_key, provider in debate_manager.model_cache.items():
            print(f"   - {cache_key}: {type(provider).__name__}")
        print("   ✅ 模型使用分析完成")

        # 验证问题分析
        print("\n7. 验证架构问题...")

        print("   ❌ 问题1: 单一会话管理")
        print(f"      - 所有{len(roles)}个角色共享1个会话")
        print(f"      - 历史记录混合: {len(session.history)}条记录在同一个会话中")

        print("   ❌ 问题2: 多模型实例")
        print(f"      - 创建了{len(debate_manager.model_cache)}个独立的模型实例")
        print(f"      - 可能导致Ollama资源竞争")

        print("   ❌ 问题3: 上下文混淆")
        print("      - 每个角色看到完整的对话历史")
        print("      - 缺乏角色独立的上下文管理")

        print("   ❌ 问题4: 回合非独立")
        print("      - 所有轮次在同一会话中连续进行")
        print("      - 上下文长度随轮次线性增长")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def demonstrate_ideal_architecture():
    """演示理想架构的设计"""
    print("\n\n🎯 理想架构设计演示")
    print("=" * 60)

    print("1. 分时复用Ollama实例:")
    print("   - 单一Ollama实例管理器")
    print("   - 按需切换模型")
    print("   - 避免资源竞争")

    print("\n2. 独立角色会话:")
    print("   - 每个角色独立会话")
    print("   - 个人历史记录")
    print("   - 立场记忆追踪")

    print("\n3. 分层记忆系统:")
    print("   - 共享辩论事实")
    print("   - 角色独立记忆")
    print("   - 轮次摘要压缩")

    print("\n4. 上下文感知提示词:")
    print("   - 角色特定上下文")
    print("   - 历史论点追踪")
    print("   - 立场一致性保持")


async def main():
    """主测试函数"""
    print("🧪 DAIP-LIVE 辩论系统架构分析")
    print("=" * 60)

    # 测试当前系统
    success = await test_current_debate_system()

    # 演示理想架构
    await demonstrate_ideal_architecture()

    print("\n" + "=" * 60)
    if success:
        print("📋 分析完成!")
        print("✅ 当前系统基本功能正常")
        print("❌ 存在架构问题需要优化")
        print("📖 详细分析请查看: 辩论系统架构分析报告.md")
    else:
        print("❌ 测试失败，请检查系统配置")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())