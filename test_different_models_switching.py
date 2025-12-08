#!/usr/bin/env python3
"""
测试强制模型切换功能 - 使用不同模型配置
"""

import asyncio
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.memory.session_manager import SessionManager
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager, RoleModelMapping, RoleModelConfig
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.persistence.database import DatabaseManager


async def test_different_models_for_roles():
    """测试不同角色使用不同模型的强制切换"""
    print("🧪 开始测试不同角色使用不同模型的强制切换...")
    
    # 创建必要组件
    config = ProviderConfig(model='ollama/llama3:instruct')
    provider = LiteLLMProvider(config)
    
    # 创建数据库管理器
    db_manager = DatabaseManager(db_path=":memory:")  # 使用内存数据库进行测试
    
    # 创建会话管理器
    session_manager = SessionManager(db_manager=db_manager)
    
    # 创建角色管理器和模型管理器
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
    
    # 模拟辩论参数
    topic = "人工智能的伦理问题"
    roles = ["pro_arguer", "con_arguer", "moderator"]  # 使用常见的角色
    num_rounds = 2
    
    print(f"\n🚀 开始辩论测试 (使用不同模型):")
    print(f"   主题: {topic}")
    print(f"   角色: {', '.join(roles)}")
    print(f"   轮次: {num_rounds}")
    
    # 手动设置角色模型映射以测试不同的模型
    print(f"\n📋 设置不同角色使用不同模型:")
    print(f"   pro_arguer: ollama/llama3:instruct")
    print(f"   con_arguer: ollama/mistral:instruct")
    print(f"   moderator: ollama/gemma:instruct")
    
    # 为测试目的，直接修改RoleModelManager的映射
    # 创建不同的模型映射
    from daip_live.p4_role_manager_tools.role_model_manager import RoleModelMapping, RoleModelConfig
    
    # 创建不同的角色模型配置
    pro_config = RoleModelConfig(
        model_name="ollama/llama3:instruct",
        provider="ollama",
        max_tokens=2048,
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.2,
        priority=1  # 中等优先级
    )
    
    con_config = RoleModelConfig(
        model_name="ollama/mistral:instruct",
        provider="ollama",
        max_tokens=2048,
        temperature=0.8,
        top_p=0.95,
        frequency_penalty=0.15,
        presence_penalty=0.25,
        priority=2  # 较高优先级
    )
    
    mod_config = RoleModelConfig(
        model_name="ollama/gemma:instruct",
        provider="ollama",
        max_tokens=2048,
        temperature=0.6,
        top_p=0.85,
        frequency_penalty=0.05,
        presence_penalty=0.15,
        priority=3  # 最高优先级
    )
    
    # 创建映射
    role_mappings = [
        RoleModelMapping(role_name="pro_arguer", role_model_config=pro_config),
        RoleModelMapping(role_name="con_arguer", role_model_config=con_config),
        RoleModelMapping(role_name="moderator", role_model_config=mod_config)
    ]
    
    # 临时替换辩论管理器中的模型映射获取方法
    original_get_mappings = role_model_manager.get_debate_model_mappings
    def mock_get_mappings(role_names):
        result = []
        for role_name in role_names:
            if role_name == "pro_arguer":
                result.append(RoleModelMapping(role_name="pro_arguer", role_model_config=pro_config))
            elif role_name == "con_arguer":
                result.append(RoleModelMapping(role_name="con_arguer", role_model_config=con_config))
            elif role_name == "moderator":
                result.append(RoleModelMapping(role_name="moderator", role_model_config=mod_config))
            else:
                # 默认使用llama3
                result.append(RoleModelMapping(
                    role_name=role_name,
                    role_model_config=RoleModelConfig(
                        model_name="ollama/llama3:instruct",
                        provider="ollama",
                        max_tokens=2048,
                        temperature=0.7,
                        top_p=0.9,
                        frequency_penalty=0.1,
                        presence_penalty=0.2,
                        priority=0
                    )
                ))
        return result
    
    # 临时替换
    role_model_manager.get_debate_model_mappings = mock_get_mappings
    
    # 运行辩论
    try:
        print(f"\n🔄 开始辩论，每个角色将使用不同模型...")
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
    
    # 恢复原始方法
    role_model_manager.get_debate_model_mappings = original_get_mappings

    print(f"\n✅ 不同角色使用不同模型的强制切换测试完成")


if __name__ == "__main__":
    asyncio.run(test_different_models_for_roles())