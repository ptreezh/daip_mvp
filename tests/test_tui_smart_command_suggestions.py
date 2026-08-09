import os
import sys
import unittest
from difflib import get_close_matches
from unittest.mock import Mock, patch

# Add src to path to import TUI module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestTUISmartCommandSuggestions(unittest.TestCase):
    """TUI智能指令建议功能测试用例"""

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

    def test_suggest_similar_commands_works(self):
        """测试智能指令建议功能正常工作"""
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

                # 设置一些可用命令用于测试
                tui._available_commands = [
                    ("/model", "模型管理命令"),
                    ("/role", "角色管理命令"),
                    ("/session", "会话管理命令"),
                    ("/debate", "辩论系统命令"),
                    ("/help", "帮助命令"),
                ]

                # 测试相似命令建议
                tui._suggest_similar_commands("modle")  # 应该建议"/model"

                # 验证调用了更新日志视图
                self.assertTrue(tui._update_log_view.called)

                # 检查是否显示了建议
                calls = tui._update_log_view.call_args_list
                self.assertTrue(any("Unknown command" in str(call) for call in calls))
                self.assertTrue(any("Did you mean" in str(call) for call in calls))

        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_suggest_similar_commands_no_matches(self):
        """测试无匹配命令时的处理"""
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

                # 设置一些可用命令用于测试
                tui._available_commands = [
                    ("/model", "模型管理命令"),
                    ("/role", "角色管理命令"),
                    ("/session", "会话管理命令"),
                    ("/debate", "辩论系统命令"),
                    ("/help", "帮助命令"),
                ]

                # 测试完全不匹配的命令
                tui._suggest_similar_commands("xyz123")  # 应该没有建议

                # 验证调用了更新日志视图
                self.assertTrue(tui._update_log_view.called)

                # 检查是否显示了帮助信息
                calls = tui._update_log_view.call_args_list
                self.assertTrue(any("Unknown command" in str(call) for call in calls))
                self.assertTrue(any("Type /help" in str(call) for call in calls))

        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_get_close_matches_functionality(self):
        """测试difflib.get_close_matches功能"""
        # 测试get_close_matches的基本功能
        available_commands = ["model", "role", "session", "debate", "help"]

        # 测试相似匹配
        suggestions = get_close_matches("modle", available_commands, n=3, cutoff=0.3)
        self.assertIn("model", suggestions)

        # 测试无匹配
        suggestions = get_close_matches("xyz123", available_commands, n=3, cutoff=0.8)
        self.assertEqual(len(suggestions), 0)


if __name__ == "__main__":
    unittest.main()
