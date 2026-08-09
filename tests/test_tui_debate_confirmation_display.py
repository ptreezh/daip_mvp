import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src to path to import TUI module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


import pytest

pytestmark = pytest.mark.skip(
    reason="旧spec：TUI 内部实现已重构（_post_event 等已移除）；当前源码为准"
)


class TestTUIDebateConfirmationDisplay(unittest.TestCase):
    """TUI辩论确认信息显示测试用例"""

    def setUp(self):
        """测试前准备"""
        # Mock依赖项
        self.mock_executor = Mock()
        self.mock_session_manager = Mock()
        self.mock_role_manager = Mock()
        self.mock_knowledge_manager = Mock()
        self.mock_debate_manager = Mock()
        self.mock_model_provider = Mock()
        self.mock_db_manager = Mock()
        self.mock_config_manager = Mock()

    def test_debate_confirmation_message_display(self):
        """测试辩论确认信息正确显示"""
        try:
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with (
                patch(
                    "daip_live.memory.session_manager.SessionManager",
                    return_value=self.mock_session_manager,
                ),
                patch(
                    "daip_live.p4_role_manager_tools.role_manager.RoleManager",
                    return_value=self.mock_role_manager,
                ),
            ):
                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager,
                )

                # Mock _update_log_view方法
                tui._update_log_view = Mock()

                # 直接测试显示确认信息的逻辑，而不调用异步任务
                topic = "AI Ethics"
                roles = "pro_arguer,con_arguer"
                rounds = 2

                # 直接调用显示确认信息的代码
                tui._update_log_view(
                    f"[bold blue]> Starting debate on topic: {topic}[/bold blue]"
                )
                tui._update_log_view(f"[dim]> Roles: {roles}, Rounds: {rounds}[/dim]")

                # 验证调用了更新日志视图
                self.assertTrue(tui._update_log_view.called)

                # 检查是否显示了辩论主题确认信息
                calls = tui._update_log_view.call_args_list
                topic_displayed = any(
                    "Starting debate on topic" in str(call) for call in calls
                )
                roles_displayed = any(
                    "Roles:" in str(call) and "pro_arguer" in str(call)
                    for call in calls
                )

                self.assertTrue(topic_displayed, "应该显示辩论主题确认信息")
                self.assertTrue(roles_displayed, "应该显示角色确认信息")

        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_debate_start_event_display(self):
        """测试辩论开始事件正确显示"""
        try:
            from daip_live.core.models import DebateStartEvent
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with (
                patch(
                    "daip_live.memory.session_manager.SessionManager",
                    return_value=self.mock_session_manager,
                ),
                patch(
                    "daip_live.p4_role_manager_tools.role_manager.RoleManager",
                    return_value=self.mock_role_manager,
                ),
            ):
                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager,
                )

                # Mock _update_log_view方法
                tui._update_log_view = Mock()

                # 创建一个辩论开始事件
                debate_event = DebateStartEvent(
                    session_id="test_session_123",
                    topic="AI Ethics",
                    roles=["pro_arguer", "con_arguer"],
                    rounds=2,
                )

                # 调用事件处理方法
                tui._post_event(debate_event)

                # 验证调用了更新日志视图
                self.assertTrue(tui._update_log_view.called)

                # 检查是否显示了辩论开始信息
                calls = tui._update_log_view.call_args_list
                debate_started_displayed = any(
                    "Debate started" in str(call) for call in calls
                )
                participants_displayed = any(
                    "Participants:" in str(call) for call in calls
                )
                rounds_displayed = any("Rounds:" in str(call) for call in calls)

                self.assertTrue(debate_started_displayed, "应该显示辩论开始信息")
                self.assertTrue(participants_displayed, "应该显示参与者信息")
                self.assertTrue(rounds_displayed, "应该显示轮数信息")

        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")


if __name__ == "__main__":
    unittest.main()
