"""
模块化TUI辩论模型切换功能端到端测试
验证完整的辩论流程中模型切换显示功能
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager, RoleModelMapping, RoleModelConfig


async def test_complete_debate_model_switching_flow():
    """测试完整的辩论模型切换流程"""
    
    # 创建mock依赖
    mock_session_manager = Mock()
    mock_role_manager = Mock()
    mock_knowledge_manager = Mock()
    mock_debate_manager = Mock()
    mock_model_provider = Mock()
    mock_db_manager = Mock()
    mock_config_manager = Mock()
    mock_role_model_manager = Mock(spec=RoleModelManager)
    mock_enhanced_debate_manager = Mock(spec=EnhancedDebateManager)
    
    # 配置role_model_manager mock来返回模型映射
    def mock_get_debate_model_mappings(role_names):
        mappings = []
        for name in role_names:
            if name == "pro_arguer":
                config = RoleModelConfig(
                    model_name="ollama/llama3:instruct",
                    provider="ollama",
                    max_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.2,
                    is_primary=True
                )
                mapping = RoleModelMapping(
                    role_name=name,
                    role_model_config=config
                )
                mappings.append(mapping)
            elif name == "con_arguer":
                config = RoleModelConfig(
                    model_name="ollama/mistral:instruct",
                    provider="ollama",
                    max_tokens=2048,
                    temperature=0.8,
                    top_p=0.95,
                    frequency_penalty=0.15,
                    presence_penalty=0.25,
                    is_primary=True
                )
                mapping = RoleModelMapping(
                    role_name=name,
                    role_model_config=config
                )
                mappings.append(mapping)
            else:
                # 默认映射
                config = RoleModelConfig(
                    model_name="ollama/llama3:instruct",
                    provider="ollama",
                    max_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.2,
                    is_primary=True
                )
                mapping = RoleModelMapping(
                    role_name=name,
                    role_model_config=config
                )
                mappings.append(mapping)
        return mappings
    
    mock_role_model_manager.get_debate_model_mappings.side_effect = mock_get_debate_model_mappings
    
    # 创建debate manager mock来模拟辩论事件流
    async def mock_run_debate(topic, roles, rounds):
        from daip_live.core.models import (
            DebateStartEvent, DebateRoundStartEvent, 
            DebateTurnStartEvent, DebateTurnCompleteEvent, 
            DebateCompleteEvent
        )
        
        # 生成辩论开始事件
        yield DebateStartEvent(
            topic=topic,
            roles=roles,
            rounds=rounds,
            session_id="test_session_001"
        )
        
        # 生成轮次开始事件
        yield DebateRoundStartEvent(
            round_number=1,
            total_rounds=rounds,
            session_id="test_session_001"
        )
        
        # 生成角色发言开始事件
        for role in roles:
            yield DebateTurnStartEvent(
                participant=role,
                round_number=1,
                session_id="test_session_001"
            )
            
            # 生成角色发言完成事件
            yield DebateTurnCompleteEvent(
                participant=role,
                round_number=1,
                content_preview=f"This is {role}'s argument",
                session_id="test_session_001"
            )
        
        # 生成辩论完成事件
        yield DebateCompleteEvent(
            session_id="test_session_001",
            summary="Debate completed successfully"
        )
    
    mock_enhanced_debate_manager.run_debate = mock_run_debate
    mock_debate_manager.run_debate = mock_run_debate
    
    # 创建TUI实例
    try:
        tui = DAIP_TUI(
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager
        )
        
        print("✅ TUI实例创建成功")
        
        # 模拟更新方法
        update_calls = []
        def mock_update_log_view(msg):
            update_calls.append(('log', msg))
            print(f"Log: {msg}")
        
        def mock_update_system_log(msg):
            update_calls.append(('system', msg))
            print(f"System: {msg}")
        
        tui._update_log_view = mock_update_log_view
        tui._update_system_log = mock_update_system_log
        
        # 运行辩论测试
        print("\n=== 开始辩论测试 ===")
        await tui._start_debate(
            topic="AI是否应该被监管",
            roles="pro_arguer,con_arguer",
            rounds=1
        )
        
        print("✅ 辩论流程完成")
        
        # 验证辩论状态
        assert tui._current_debate['is_active'] == False
        assert tui._current_debate['topic'] == "AI是否应该被监管"
        print("✅ 辩论状态正确")
        
        # 验证模型切换
        print(f"最终模型: {tui._current_model}")
        assert tui._current_model == "default"  # 辩论完成后应重置
        print("✅ 模型重置正确")
        
        # 验证状态栏显示功能
        print("\n=== 测试状态栏显示 ===")
        
        # 模拟辩论中的状态
        tui._current_debate.update({
            'is_active': True,
            'current_participant': 'pro_arguer',
            'role_models': {
                'pro_arguer': 'ollama/llama3:instruct',
                'con_arguer': 'ollama/mistral:instruct'
            },
            'current_round': 1,
            'total_rounds': 2
        })
        
        # 获取状态栏文本
        status_text = tui.get_enhanced_status_text("Debating")
        print(f"辩论中状态栏: {status_text}")
        
        assert "ollama/llama3:instruct (pro_arguer)" in status_text
        print("✅ 辩论中状态栏显示正确")
        
        # 切换到另一个角色
        tui._current_debate['current_participant'] = 'con_arguer'
        status_text = tui.get_enhanced_status_text("Debating")
        print(f"切换后状态栏: {status_text}")
        
        assert "ollama/mistral:instruct (con_arguer)" in status_text
        print("✅ 角色切换后状态栏显示正确")
        
        print("\n🎉 所有测试通过！模块化TUI辩论模型切换功能完整实现！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_complete_debate_model_switching_flow())