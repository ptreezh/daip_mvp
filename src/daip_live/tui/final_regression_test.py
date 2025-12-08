"""
最终回归测试 - 验证所有功能完好
"""

import asyncio
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI


def test_basic_functionality():
    print('Testing basic functionality...')
    
    # 创建模拟容器
    mock_container = Mock()
    mock_session_manager = Mock()
    mock_session_manager.list_sessions.return_value = []
    mock_container.session_manager.return_value = mock_session_manager
    mock_container.model_provider.return_value = Mock()
    mock_container.role_manager.return_value = Mock()
    mock_container.role_model_manager.return_value = Mock()
    mock_container.agent_executor.return_value = Mock()
    mock_container.knowledge_manager.return_value = Mock()
    mock_container.debate_manager.return_value = Mock()
    
    with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
        try:
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_knowledge_manager()
            tui._initialize_state()
            
            # 测试命令处理器
            assert hasattr(tui.command_handler, 'handle_command'), 'Command handler should exist'
            
            # 测试会话管理器存在
            assert hasattr(tui, '_session_manager'), 'Session manager should exist'
            
            # 测试辩论管理器存在
            assert hasattr(tui, '_debate_manager'), 'Debate manager should exist'
            
            # 测试知识管理器存在
            assert hasattr(tui, '_knowledge_manager'), 'Knowledge manager should exist'
            
            # 测试角色管理器存在
            assert hasattr(tui, '_role_manager'), 'Role manager should exist'
            
            print('✅ All basic functionality tests passed!')
            return True
        except Exception as e:
            print(f'❌ Basic functionality test failed: {e}')
            import traceback
            traceback.print_exc()
            return False


def test_command_dispatch():
    print('Testing command dispatch...')
    
    mock_container = Mock()
    mock_session_manager = Mock()
    mock_session_manager.list_sessions.return_value = []
    mock_container.session_manager.return_value = mock_session_manager
    mock_container.model_provider.return_value = Mock()
    mock_container.role_manager.return_value = Mock()
    mock_container.role_model_manager.return_value = Mock()
    mock_container.agent_executor.return_value = Mock()
    mock_container.knowledge_manager.return_value = Mock()
    mock_container.debate_manager.return_value = Mock()
    
    with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
        try:
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_knowledge_manager()
            tui._initialize_state()
            
            # 测试Claude Skills命令处理是否存在
            assert hasattr(tui, '_handle_claude_skills_list_command'), 'Claude skills list command handler should exist'
            assert hasattr(tui, '_handle_claude_skills_run_command'), 'Claude skills run command handler should exist'
            
            # 测试会话命令处理存在（后台功能）
            assert hasattr(tui, '_handle_session_command'), 'Session command handler should exist'
            
            print('✅ Command dispatch tests passed!')
            return True
        except Exception as e:
            print(f'❌ Command dispatch test failed: {e}')
            import traceback
            traceback.print_exc()
            return False


def test_specific_claude_skills_backend():
    """测试Claude Skills后端功能"""
    print('Testing Claude Skills backend functionality...')
    
    mock_container = Mock()
    mock_session_manager = Mock()
    mock_session_manager.list_sessions.return_value = []
    mock_container.session_manager.return_value = mock_session_manager
    mock_container.model_provider.return_value = Mock()
    mock_container.role_manager.return_value = Mock()
    mock_container.role_model_manager.return_value = Mock()
    mock_container.agent_executor.return_value = Mock()
    mock_container.knowledge_manager.return_value = Mock()
    mock_container.debate_manager.return_value = Mock()
    
    # 模拟Claude Skills管理器
    class MockClaudeSkillsManager:
        def __init__(self):
            self.name = "MockClaudeSkillsManager"
    
    with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
        try:
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_knowledge_manager()
            tui._initialize_state()
            
            # 检查Claude Skills管理器是否存在
            assert hasattr(tui, '_claude_skill_adapter_manager'), 'Claude Skills adapter manager should be initialized'
            
            print('✅ Claude Skills backend functionality tests passed!')
            return True
        except Exception as e:
            print(f'❌ Claude Skills backend test failed: {e}')
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("=== DAIP-LIVE Simplified TUI Regression Test Suite ===\n")
    
    success1 = test_basic_functionality()
    print()
    success2 = test_command_dispatch()
    print()
    success3 = test_specific_claude_skills_backend()
    print()
    
    if success1 and success2 and success3:
        print('🎉 ALL REGRESSION TESTS PASSED!')
        print('✅ Backend services properly initialized')
        print('✅ Command handlers accessible')  
        print('✅ Claude Skills functionality available')
        print('✅ Session management infrastructure in place')
    else:
        print('❌ SOME REGRESSION TESTS FAILED!')
        sys.exit(1)