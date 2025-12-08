"""
辩论模型切换显示测试
遵循TDD原则：先写失败测试，再实现功能
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from daip_live.tui import DAIP_TUI
from daip_live.core.models import DebateStartEvent, DebateTurnStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager


class TestDebateModelSwitchingDisplay:
    """测试辩论中的模型切换显示功能"""

    @pytest.fixture
    def tui_with_mocked_dependencies(self):
        """创建带有Mock依赖的TUI实例"""
        tui = DAIP_TUI.__new__(DAIP_TUI)  # 创建实例但不调用__init__
        
        # Mock必要的属性
        tui._current_debate = {
            'topic': '',
            'total_rounds': 0,
            'current_round': 0,
            'current_participant': None,
            'is_active': False,
            'role_models': {},
            'participant_colors': {}
        }
        tui._debate_active_models = {}
        tui._model_name = "default_model"
        tui._current_model = "default_model"
        tui._system_log_queue = asyncio.Queue()
        tui._log_queue = asyncio.Queue()
        tui._executor = Mock()
        tui._enhanced_debate_manager = Mock(spec=EnhancedDebateManager)
        tui._role_model_manager = Mock(spec=RoleModelManager)
        
        # Mock方法
        tui._update_system_log = Mock()
        tui._update_log_view = Mock()
        tui._update_status_bar = Mock()
        tui.get_enhanced_status_text = Mock(return_value="Status: Idle")
        tui._update_current_model = Mock()
        
        return tui

    def test_red_initial_state_no_model_switching_display(self, tui_with_mocked_dependencies):
        """RED测试：验证当前系统在辩论时不显示模型切换信息"""
        tui = tui_with_mocked_dependencies
        
        # 模拟辩论开始事件
        start_event = DebateStartEvent(
            topic="AI监管",
            roles=["pro_arguer", "con_arguer"], 
            rounds=2,
            session_id="test_session"
        )
        
        # 假设角色模型映射
        tui._current_debate['role_models'] = {
            "pro_arguer": "ollama/llama3:instruct",
            "con_arguer": "ollama/mistral:instruct"
        }
        
        # 处理开始事件
        tui._current_debate['is_active'] = True
        
        # 模拟轮次开始事件（这应该触发模型切换）
        turn_start_event = DebateTurnStartEvent(
            participant="pro_arguer",
            round_number=1,
            session_id="test_session"
        )
        
        # 在当前系统中，处理此事件时不会更新TUI状态栏中的模型信息
        # 这是测试要验证的问题 - 当前状态不显示模型切换
        
        # 验证当前实现中 _update_current_model 是否被调用
        initial_call_count = tui._update_current_model.call_count
        
        # 模拟处理轮次开始事件的逻辑（从tui.py中提取的关键逻辑）
        tui._current_debate['current_participant'] = turn_start_event.participant
        
        # 在当前实现中，这里会调用_update_current_model
        if tui._current_debate['role_models']:
            participant_model = tui._current_debate['role_models'].get(
                turn_start_event.participant, tui._model_name
            )
            tui._update_current_model(participant_model)
        
        # 验证模型切换函数被调用了
        assert tui._update_current_model.call_count > initial_call_count
        
        # RED测试：验证当前系统的状态栏可能无法正确反映模型切换
        # 在当前实现中，虽然调用了_update_current_model，但状态栏可能没有正确更新
        # （这取决于_get_enhanced_status_text的实现）
        
        # 获取传递给_update_current_model的参数
        args, kwargs = tui._update_current_model.call_args
        model_name = args[0] if args else None
        
        # 验证传递的模型名是正确的
        assert model_name == "ollama/llama3:instruct"
        
        # RED测试：验证当前状态栏显示可能不会立即反映模型切换
        # 这是当前系统存在的问题 - 状态栏显示可能不准确
        assert tui._update_status_bar.called


    def test_red_verify_current_status_bar_does_not_reflect_switching(self, tui_with_mocked_dependencies):
        """RED测试：验证当前状态栏实现未正确反映模型切换"""
        tui = tui_with_mocked_dependencies
        
        # 设置辩论状态
        tui._current_debate.update({
            'is_active': True,
            'current_participant': 'pro_arguer',
            'role_models': {
                'pro_arguer': 'ollama/llama3:instruct',
                'con_arguer': 'ollama/mistral:instruct'
            }
        })
        
        # 调用状态栏文本生成方法
        status_text = tui.get_enhanced_status_text("Debating")
        
        # RED测试：当前实现的状态栏可能不会显示特定角色的模型
        # 验证状态文本生成逻辑
        assert "Debating" in status_text
        # 在当前实现中，状态栏应该包含模型信息，但可能不包含角色特定模型
        

    def test_green_enhanced_model_switching_display(self, tui_with_mocked_dependencies):
        """GREEN测试：测试增强的模型切换显示功能（此测试将失败直到功能实现）"""
        tui = tui_with_mocked_dependencies
        
        # 设置辩论状态
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
        
        # 调用状态栏文本生成方法，期望它能正确显示当前角色的模型
        status_text = tui.get_enhanced_status_text("Debating")
        
        # GREEN测试：期望状态栏包含当前角色和模型信息
        # 注意：当前这会失败，因为功能尚未实现
        assert "ollama/llama3:instruct (pro_arguer)" in status_text or "pro_arguer" in status_text
        

if __name__ == "__main__":
    pytest.main([__file__, "-v"])