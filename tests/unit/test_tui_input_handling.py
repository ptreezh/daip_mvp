"""TUI 输入处理单元测试 - 对齐 SimplifiedTUI 真实 API"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from textual.widgets import Input

from daip_live.tui.simplified_main import SimplifiedTUI
from daip_live.tui.utils import HistoryManager


@pytest.fixture
def tui_app(tmp_path):
    container = Mock()
    container.config_manager.get.return_value = 100
    with patch("daip_live.container.Container", return_value=container):
        app = SimplifiedTUI()
    app.history_manager = HistoryManager(
        100, history_file=str(tmp_path / "history.json")
    )
    return app


@pytest.mark.asyncio
async def test_on_input_submitted_processes_input(tui_app):
    """提交非空输入: 记录历史、显示回显、分发处理、清空输入框"""
    input_widget = Input()
    with (
        patch.object(tui_app, "query_one", return_value=input_widget),
        patch.object(tui_app, "_process_user_input", new=AsyncMock()) as mock_process,
    ):
        await tui_app.on_input_submitted(Mock(value="hello"))

    assert tui_app.history_manager.history == ["hello"]
    mock_process.assert_awaited_once_with("hello")
    assert input_widget.value == ""
    assert "[bold cyan]> hello[/bold cyan]" in tui_app._log_text_buffer


@pytest.mark.asyncio
async def test_on_input_submitted_blank_input_skips(tui_app):
    """空白输入不记录历史也不分发处理"""
    input_widget = Input()
    with (
        patch.object(tui_app, "query_one", return_value=input_widget),
        patch.object(tui_app, "_process_user_input", new=AsyncMock()) as mock_process,
    ):
        await tui_app.on_input_submitted(Mock(value="   "))

    mock_process.assert_not_awaited()
    assert tui_app.history_manager.history == []
    assert input_widget.value == ""


@pytest.mark.asyncio
async def test_process_user_input_dispatches_command(tui_app):
    """斜杠开头的输入走命令处理分支"""
    with (
        patch.object(tui_app, "_handle_command_input", new=AsyncMock()) as mock_cmd,
        patch.object(tui_app, "_handle_chat_input", new=AsyncMock()) as mock_chat,
    ):
        await tui_app._process_user_input("/help")

    mock_cmd.assert_awaited_once_with("/help")
    mock_chat.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_user_input_dispatches_chat(tui_app):
    """普通文本走聊天处理分支"""
    with (
        patch.object(tui_app, "_handle_command_input", new=AsyncMock()) as mock_cmd,
        patch.object(tui_app, "_handle_chat_input", new=AsyncMock()) as mock_chat,
    ):
        await tui_app._process_user_input("你好")

    mock_chat.assert_awaited_once_with("你好")
    mock_cmd.assert_not_awaited()


def test_get_command_suggestions_empty(tui_app):
    """空输入不产生补全建议"""
    assert tui_app.get_command_suggestions([]) == []


def test_get_command_suggestions_main_prefix(tui_app):
    """主命令前缀匹配（返回带斜杠的完整命令）"""
    suggestions = tui_app.get_command_suggestions(["/comp"])
    assert "/compact" in suggestions


def test_get_command_suggestions_subcommand(tui_app):
    """子命令渐进式补全"""
    suggestions = tui_app.get_command_suggestions(["/debate", ""])
    assert "/debate start" in suggestions
    assert "/debate history" in suggestions
    assert "/debate search" in suggestions


def test_suggest_similar_commands_with_match(tui_app):
    """近似命令给出建议"""
    tui_app._suggest_similar_commands("hlp")
    calls = "".join(tui_app._log_text_buffer)
    assert "> Unknown command: /hlp" in calls
    assert "Did you mean:" in calls
    assert "   /help" in calls


def test_suggest_similar_commands_no_match(tui_app):
    """无近似命令时提示查看帮助"""
    tui_app._suggest_similar_commands("zzzz")
    calls = "".join(tui_app._log_text_buffer)
    assert "> Unknown command: /zzzz" in calls
    assert "Type /help to see available commands" in calls
