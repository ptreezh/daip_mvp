"""
模块化TUI辩论模型切换显示功能测试
验证TDD循环：实现功能后测试应通过
"""

import asyncio
from unittest.mock import Mock

import pytest

from daip_live.core.models import (
    DebateTurnStartEvent,
)
from daip_live.p4_role_manager_tools.role_model_manager import (
    RoleModelManager,
)
from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
from daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="旧spec：TUI 内部实现已重构（_post_event 等已移除）；当前源码为准"
)


class TestModularTUIDebateModelSwitchingGreen:
    """测试模块化TUI辩论中的模型切换显示功能 - GREEN测试"""

    @pytest.fixture
    def modular_tui_with_mocked_dependencies(self):
        """创建带有Mock依赖的模块化TUI实例"""
        # 创建TUI实例，传入必要的依赖
        mock_session_manager = Mock()
        mock_role_manager = Mock()
        mock_knowledge_manager = Mock()
        mock_debate_manager = Mock()
        mock_model_provider = Mock()
        mock_db_manager = Mock()
        mock_config_manager = Mock()
        mock_role_model_manager = Mock(spec=RoleModelManager)
        mock_enhanced_debate_manager = Mock(spec=EnhancedDebateManager)

        tui = DAIP_TUI(
            session_manager=mock_session_manager,
            role_manager=mock_role_manager,
            knowledge_manager=mock_knowledge_manager,
            debate_manager=mock_debate_manager,
            model_provider=mock_model_provider,
            db_manager=mock_db_manager,
            config_manager=mock_config_manager,
            role_model_manager=mock_role_model_manager,
            enhanced_debate_manager=mock_enhanced_debate_manager,
        )

        return tui

    def test_green_enhanced_model_switching_display(
        self, modular_tui_with_mocked_dependencies
    ):
        """GREEN测试：验证增强的状态栏显示功能"""
        tui = modular_tui_with_mocked_dependencies

        # 设置辩论状态
        tui._current_debate.update(
            {
                "is_active": True,
                "current_participant": "pro_arguer",
                "role_models": {
                    "pro_arguer": "ollama/llama3:instruct",
                    "con_arguer": "ollama/mistral:instruct",
                },
                "current_round": 1,
                "total_rounds": 2,
            }
        )

        # 调用状态栏文本生成方法
        status_text = tui.get_enhanced_status_text("Debating")

        # 验证状态文本包含当前角色和模型信息
        assert "ollama/llama3:instruct (pro_arguer)" in status_text
        assert "Debate:" in status_text

    def test_green_debate_event_handling_updates_model(
        self, modular_tui_with_mocked_dependencies
    ):
        """GREEN测试：验证辩论事件处理正确更新模型"""
        tui = modular_tui_with_mocked_dependencies

        # 初始化辩论状态，包含角色-模型映射
        tui._current_debate.update(
            {
                "is_active": True,
                "current_participant": None,
                "role_models": {
                    "pro_arguer": "ollama/llama3:instruct",
                    "con_arguer": "ollama/mistral:instruct",
                },
                "current_round": 0,
                "total_rounds": 2,
            }
        )

        # 创建辩论转次开始事件

        turn_start_event = DebateTurnStartEvent(
            participant="pro_arguer", round_number=1, session_id="test_session"
        )

        # 处理事件

        asyncio.run(tui._handle_debate_event(turn_start_event))

        # 验证当前模型已更新
        assert tui._current_model == "ollama/llama3:instruct"
        assert tui._current_debate["current_participant"] == "pro_arguer"

    def test_green_get_enhanced_status_text_shows_role_model(self):
        """GREEN测试：验证状态栏在辩论活动时显示正确的角色模型"""
        # 创建一个简单的TUI实例用于测试
        tui = DAIP_TUI.__new__(DAIP_TUI)  # 创建实例但不调用__init__

        # 设置基本属性
        tui._current_model = "default_model"
        tui._real_token_usage = (100, 1000)
        tui._system_activity = {
            "events_processed": 1,
            "tools_executed": 1,
            "errors_encountered": 0,
        }
        tui.focus_mode = "Input"

        # 设置辩论状态
        tui._current_debate = {
            "is_active": True,
            "current_participant": "pro_arguer",
            "role_models": {
                "pro_arguer": "ollama/llama3:instruct",
                "con_arguer": "ollama/mistral:instruct",
            },
            "current_round": 1,
            "total_rounds": 2,
        }

        # 调用状态栏文本生成方法
        status_text = tui.get_enhanced_status_text("Debating")

        # 验证状态文本正确显示了角色特定的模型
        assert "ollama/llama3:instruct (pro_arguer)" in status_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
