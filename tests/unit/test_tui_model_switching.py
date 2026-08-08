"""TUI 模型管理单元测试 - 对齐 SimplifiedTUI 真实 API"""

from unittest.mock import Mock, patch

import pytest

from daip_live.tui.simplified_main import SimplifiedTUI


@pytest.fixture
def tui_app():
    container = Mock()
    container.config_manager.get.return_value = 100
    with patch("daip_live.container.Container", return_value=container):
        return SimplifiedTUI()


def _join_logs(app):
    return "".join(app._log_text_buffer)


def test_handle_model_command_no_args_lists_models(tui_app):
    """无参数时默认列出可用模型"""
    tui_app._handle_model_command("")
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    assert "gpt-4 - OpenAI GPT-4" in logs
    assert "mistral - Mistral AI" in logs


def test_handle_model_command_list(tui_app):
    """list 子命令列出可用模型"""
    tui_app._handle_model_command("list")
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    assert "claude-3 - Anthropic Claude 3" in logs
    assert "llama2 - Meta LLaMA 2" in logs


def test_handle_model_command_switch(tui_app):
    """switch 子命令切换模型"""
    tui_app._handle_model_command("switch gpt-4")
    logs = _join_logs(tui_app)
    assert "🔄 切换到模型: gpt-4" in logs
    assert "✅ 模型切换完成" in logs


def test_handle_model_command_switch_no_name(tui_app):
    """switch 未指定模型名时提示"""
    tui_app._handle_model_command("switch")
    logs = _join_logs(tui_app)
    assert "⚠️ 请指定模型名称" in logs


def test_handle_model_command_status(tui_app):
    """status 子命令显示当前模型状态"""
    tui_app._handle_model_command("status")
    logs = _join_logs(tui_app)
    assert "🤖 当前模型状态" in logs
    assert "活动模型: gpt-4" in logs
    assert "状态: ✅ 正常" in logs


def test_handle_model_command_unknown_subcommand(tui_app):
    """未知子命令提示"""
    tui_app._handle_model_command("foo")
    logs = _join_logs(tui_app)
    assert "⚠️ 未知子命令: foo" in logs


def test_handle_model_list_output(tui_app):
    """可用模型列表包含全部 5 个模型"""
    tui_app._handle_model_list()
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    for model in ("gpt-4", "gpt-3.5-turbo", "claude-3", "llama2", "mistral"):
        assert model in logs


def test_handle_model_switch_direct(tui_app):
    """直接调用模型切换"""
    tui_app._handle_model_switch("llama2")
    logs = _join_logs(tui_app)
    assert "🔄 切换到模型: llama2" in logs
    assert "✅ 模型切换完成" in logs
