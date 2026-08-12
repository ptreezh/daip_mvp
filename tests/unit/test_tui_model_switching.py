"""TUI 模型管理单元测试 - 对齐真实实现（真实 Ollama 列表 + 诚实切换提示）"""

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
    """无参数时默认列出可用模型（真实 ModelManager）"""
    fake_models = [
        {"name": "llama3:latest", "size_mb": 4340},
        {"name": "qwen3.5:4b", "size_mb": 3160},
    ]
    with patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=fake_models,
    ):
        tui_app._handle_model_command("")
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    assert "llama3:latest" in logs
    assert "qwen3.5:4b" in logs
    assert "gpt-4" not in logs  # 不再硬编码


def test_handle_model_command_list(tui_app):
    """list 子命令列出真实模型"""
    with patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=[{"name": "llama3:latest", "size_mb": 4340}],
    ):
        tui_app._handle_model_command("list")
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    assert "llama3:latest" in logs


def test_handle_model_command_switch(tui_app):
    """switch 子命令真实校验模型存在性（不存在时提示 pull）"""
    with patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=[{"name": "llama3:latest", "size_mb": 4340}],
    ):
        tui_app._handle_model_command("switch gpt-4")
    logs = _join_logs(tui_app)
    assert "🔄 切换到模型: gpt-4" in logs
    assert "不在本地 Ollama 可用列表中" in logs
    assert "ollama pull" in logs


def test_handle_model_command_switch_no_name(tui_app):
    """switch 未指定模型名时提示"""
    tui_app._handle_model_command("switch")
    logs = _join_logs(tui_app)
    assert "⚠️ 请指定模型名称" in logs


def test_handle_model_command_status(tui_app):
    """status 子命令显示真实默认模型 + Ollama 在线检测"""
    with patch(
        "daip_live.tui.simplified_main.SimplifiedTUI._handle_model_status"
    ) as mock_status:
        tui_app._handle_model_command("status")
        mock_status.assert_called_once()
    # 直接验证 status 实现（读 config 默认模型）
    with patch(
        "urllib.request.urlopen",
        return_value=Mock(),
    ):
        tui_app._handle_model_status()
    logs = _join_logs(tui_app)
    assert "🤖 当前模型状态" in logs
    assert "配置默认模型" in logs
    assert "活动模型: gpt-4" not in logs  # 不再硬编码


def test_handle_model_command_unknown_subcommand(tui_app):
    """未知子命令提示"""
    tui_app._handle_model_command("foo")
    logs = _join_logs(tui_app)
    assert "⚠️ 未知子命令: foo" in logs


def test_handle_model_list_output(tui_app):
    """可用模型列表来自真实 ModelManager（非硬编码 5 个）"""
    fake_models = [
        {"name": "deepseek-r1:8b", "size_mb": 4870},
        {"name": "nomic-embed-text:latest", "size_mb": 260},
    ]
    with patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=fake_models,
    ):
        tui_app._handle_model_list()
    logs = _join_logs(tui_app)
    assert "🤖 可用模型列表" in logs
    assert "deepseek-r1:8b" in logs
    assert "nomic-embed-text:latest" in logs
    for fake in ("gpt-4", "gpt-3.5-turbo", "claude-3", "llama2", "mistral"):
        assert fake not in logs


def test_handle_model_switch_direct(tui_app):
    """直接调用模型切换 - 真实校验 + 存在时持久化"""
    with patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=[{"name": "llama3:latest", "size_mb": 4340}],
    ):
        tui_app._handle_model_switch("llama3:latest")
    logs = _join_logs(tui_app)
    assert "🔄 切换到模型: llama3:latest" in logs
    assert "✅ 模型已切换并持久化" in logs


def test_handle_model_switch_validates_existence(tui_app):
    """切换不存在的模型时提示 pull，不写 config"""
    from unittest.mock import patch as _patch

    with _patch(
        "daip_live.model_manager.ModelManager.get_available_models",
        return_value=[{"name": "llama3:latest", "size_mb": 4340}],
    ):
        tui_app._handle_model_switch("nonexistent-model")
    logs = _join_logs(tui_app)
    assert "不在本地 Ollama 可用列表中" in logs
    assert "✅ 模型已切换并持久化" not in logs
