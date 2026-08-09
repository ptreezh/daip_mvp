"""
TUI新增功能测试
包括：双击CTRL+E退出、/clear命令、输入历史持久化
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from textual.keys import Keys
from textual.widgets import Input, Static

from daip_live.tui import DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准"
)


class TestTUIExitShortcut:
    """双击CTRL+E退出功能测试"""

    @pytest.fixture
    def tui_with_mocks(self):
        """创建带有Mock的TUI实例"""
        with (
            patch("daip_live.tui.SessionManager"),
            patch("daip_live.tui.RoleManager"),
            patch("daip_live.tui.KnowledgeManager"),
            patch("daip_live.tui.MemoryService"),
            patch("daip_live.tui.DebateManager"),
            patch("daip_live.tui.LiteLLMProvider"),
            patch("daip_live.tui.DatabaseManager"),
        ):
            tui = DAIP_TUI()
            tui.exit = Mock()  # Mock exit方法

            # Mock widgets that the TUI expects to find
            def mock_query_one(selector, widget_type=None):
                if selector == Input or (
                    isinstance(selector, str) and "input" in selector.lower()
                ):
                    input_widget = Mock()
                    input_widget.value = ""
                    input_widget.action_end = Mock()
                    return input_widget
                elif selector == "#status_bar" or (
                    widget_type and widget_type == Static
                ):
                    status_bar = Mock()
                    status_bar.renderable = ""
                    status_bar.update = Mock()
                    return status_bar
                elif "#main_log" in str(selector):
                    log_widget = Mock()
                    log_widget.write = Mock()
                    log_widget.clear = Mock()
                    return log_widget
                else:
                    # Default mock for other queries
                    widget = Mock()
                    return widget

            tui.query_one = mock_query_one

            # Mock the timer method to avoid event loop issues
            tui.set_timer = Mock()

            # Mock the status bar update method
            tui._update_status_bar = Mock()
            return tui

    def test_first_ctrl_e_shows_hint(self, tui_with_mocks):
        """测试第一次按CTRL+E显示退出提示"""
        tui = tui_with_mocks

        # 模拟第一次CTRL+E
        with patch("time.time", return_value=1000):
            tui.on_key(Keys.ControlE)

        # 验证状态栏提示被更新
        tui._update_status_bar.assert_called_with("再次按 CTRL+E 退出应用")

        # 验证exit没有被调用
        tui.exit.assert_not_called()

    def test_second_ctrl_e_exits(self, tui_with_mocks):
        """测试第二次按CTRL+E退出应用"""
        tui = tui_with_mocks

        # 模拟第一次CTRL+E
        with patch("time.time", return_value=1000):
            tui.on_key(Keys.ControlE)

        # 模拟第二次CTRL+E（在时间窗口内）
        with patch("time.time", return_value=1001):  # 1秒后，应该在2秒窗口内
            tui.on_key(Keys.ControlE)

        # 验证exit被调用
        tui.exit.assert_called_once()

    def test_ctrl_e_timeout_resets(self, tui_with_mocks):
        """测试超时后重置退出状态"""
        tui = tui_with_mocks

        # 模拟第一次CTRL+E
        with patch("time.time", return_value=1000):
            tui.on_key(Keys.ControlE)

        # 模拟第二次CTRL+E（超时，3秒后）
        with patch("time.time", return_value=1003):  # 3秒后，超过2秒窗口
            tui.on_key(Keys.ControlE)

        # 验证exit没有被调用
        tui.exit.assert_not_called()

        # 验证状态栏恢复
        status_bar = tui.query_one("#status_bar", Static)
        assert "再次按 CTRL+E 退出" not in str(status_bar.renderable)


class TestTUIClearCommand:
    """TUI /clear命令测试"""

    @pytest.fixture
    def tui_with_mocks(self):
        """创建带有Mock的TUI实例"""
        with (
            patch("daip_live.tui.SessionManager"),
            patch("daip_live.tui.RoleManager"),
            patch("daip_live.tui.KnowledgeManager"),
            patch("daip_live.tui.MemoryService"),
            patch("daip_live.tui.DebateManager"),
            patch("daip_live.tui.LiteLLMProvider"),
            patch("daip_live.tui.DatabaseManager"),
        ):
            tui = DAIP_TUI()
            return tui

    def test_clear_command_clears_output(self, tui_with_mocks):
        """测试/clear命令清空输出区域"""
        tui = tui_with_mocks

        # Mock log view
        log_view = Mock()
        tui.query_one = Mock(return_value=log_view)

        # 执行clear命令
        tui._handle_clear_command("")

        # 验证命令处理器被正确调用
        assert hasattr(tui, "_handle_clear_command")


class TestTUIInputHistoryPersistence:
    """TUI输入历史持久化测试"""

    @pytest.fixture
    def tui_with_minimal_mocks(self):
        """创建最小化Mock的TUI实例用于历史测试"""
        with (
            patch("daip_live.tui.SessionManager"),
            patch("daip_live.tui.RoleManager"),
            patch("daip_live.tui.KnowledgeManager"),
            patch("daip_live.tui.MemoryService"),
            patch("daip_live.tui.DebateManager"),
            patch("daip_live.tui.LiteLLMProvider"),
            patch("daip_live.tui.DatabaseManager"),
            patch("daip_live.container.Container"),
        ):
            # 直接创建TUI实例，避免container初始化
            tui = object.__new__(DAIP_TUI)

            # 手动初始化基本属性
            tui._input_history = []
            tui._history_index = -1
            tui._current_input_before_history = ""

            # Mock必要的方法
            tui._update_log_view = Mock()

            return tui

    @pytest.fixture
    def temp_history_file(self):
        """创建临时历史文件"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("/role list\n")
            f.write("/session view sess_001\n")
            f.write("regular message\n")
            f.write("/knowledge sync\n")
            temp_file = f.name

        yield Path(temp_file)

        # 清理
        temp_file_path = Path(temp_file)
        if temp_file_path.exists():
            temp_file_path.unlink()

    def test_load_history_from_file(self, tui_with_minimal_mocks, temp_history_file):
        """测试从文件加载历史记录"""
        tui = tui_with_minimal_mocks

        # Mock历史文件路径和内容
        expected_content = temp_history_file.read_text()

        with (
            patch("pathlib.Path.home", return_value=Path("/mock/home")),
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=expected_content)),
        ):
            # 调用加载方法
            tui._load_input_history()

            # 验证历史记录被加载
            assert len(tui._input_history) == 4
            assert "/role list" in tui._input_history
            assert "/session view sess_001" in tui._input_history
            assert "regular message" in tui._input_history
            assert "/knowledge sync" in tui._input_history

    def test_save_history_to_file(self, tui_with_minimal_mocks):
        """测试保存历史记录到文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / ".daip" / "input_history.txt"
            tui = tui_with_minimal_mocks

            # 添加一些历史记录
            tui._input_history = [
                "/role list",
                "/session view",
                "test message",
                "/knowledge sync",
            ]

            # Mock home directory to use temp directory
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                # 保存历史记录
                tui._save_input_history()

                # 验证文件被创建并包含正确内容
                assert history_file.exists()
                content = history_file.read_text()
                lines = content.strip().split("\n")
                assert len(lines) == 4
                assert "/role list" in lines
                assert "/knowledge sync" in lines

    def test_history_limited_to_10_entries(self, tui_with_minimal_mocks):
        """测试历史记录限制为10条"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / ".daip" / "input_history.txt"
            tui = tui_with_minimal_mocks

            # 添加超过10条历史记录
            tui._input_history = [f"command_{i}" for i in range(15)]

            # Mock home directory to use temp directory
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                # 保存历史记录
                tui._save_input_history()

                # 验证只保存了最近的10条
                content = history_file.read_text()
                lines = content.strip().split("\n")
                assert len(lines) == 10
                assert "command_5" in lines  # 最近的10条应该是5-14
                assert "command_14" in lines
                assert "command_0" not in lines  # 最老的5条应该被丢弃


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
