#!/usr/bin/env python3
"""
测试强制模型切换功能
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.persistence.database import DatabaseManager


async def test_forced_model_switching():
    """测试强制模型切换功能"""
    print("🧪 开始测试强制模型切换功能...")
    
    # 创建必要组件
    config = ProviderConfig(model='ollama/llama3:instruct')
    provider = LiteLLMProvider(config)

    # 创建数据库管理器
    db_manager = DatabaseManager(db_path=":memory:")  # 使用内存数据库进行测试

    # 创建会话管理器
    session_manager = SessionManager(db_manager=db_manager)
    role_manager = RoleManager(roles_dir_path="src/daip_live/p4_role_manager_tools/roles")  # 假设角色文件在这个目录
    role_model_manager = RoleModelManager(roles_dir_path="src/daip_live/p4_role_manager_tools/roles")

    # 创建辩论历史跟踪器
    history_tracker = DebateHistoryTracker()

    # 创建增强的辩论管理器
    debate_manager = EnhancedDebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        role_model_manager=role_model_manager,
        model_provider=provider,
        debate_history_tracker=history_tracker
    )
    
    print(f"✅ EnhancedDebateManager 创建成功")
    print(f"✅ 使用优化架构: {debate_manager.use_optimized_architecture}")
    print(f"✅ 配置了辩论历史跟踪器: {debate_manager.debate_history_tracker is not None}")
    
    # 模拟辩论参数
    topic = "人工智能的伦理问题"
    roles = ["pro_arguer", "con_arguer", "moderator"]  # 使用常见的角色
    num_rounds = 2
    
    print(f"\n🚀 开始辩论测试:")
    print(f"   主题: {topic}")
    print(f"   角色: {', '.join(roles)}")
    print(f"   轮次: {num_rounds}")
    
    # 运行辩论
    try:
        async for event in debate_manager.run_debate(topic, roles, num_rounds):
            # 处理事件并显示模型切换信息
            if hasattr(event, 'type'):
                if event.type == "thought":
                    if "模型切换至" in getattr(event, 'content', ''):
                        print(f"🔄 [模型切换] {event.content}")
                    else:
                        print(f"💭 [思考] {event.content}")
                elif event.type == "debate_turn_start":
                    print(f"👤 [轮次开始] {event.participant} 开始发言 (第{event.round_number}轮)")
                elif event.type == "debate_turn_complete":
                    print(f"✅ [轮次完成] {event.participant} 完成发言")
                elif event.type == "debate_round_start":
                    print(f"🔄 [辩论轮次] 第{event.round_number}轮开始")
                elif event.type == "debate_start":
                    print(f"🎮 [辩论开始] 主题: {event.topic}")
                    print(f"   角色: {', '.join(event.roles)}")
                elif event.type == "debate_complete":
                    print(f"🏁 [辩论完成] 摘要: {event.summary[:100]}...")
                elif event.type == "token_usage":
                    print(f"📊 [Token使用] 总计: {event.usage_info.get('total_tokens', 0)} tokens")
            else:
                # 兼容性处理：直接打印内容
                if hasattr(event, 'content'):
                    if "模型切换至" in event.content:
                        print(f"🔄 [模型切换] {event.content}")
                    else:
                        print(f"💭 [思考] {event.content}")
                else:
                    print(f"📝 [事件] {event}")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

    print(f"\n✅ 强制模型切换功能测试完成")


if __name__ == "__main__":
    asyncio.run(test_forced_model_switching())