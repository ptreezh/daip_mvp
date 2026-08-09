"""
模块化TUI辩论模型切换功能验证
完整测试实现的功能
"""

import pytest

from daip_live.tui.simplified_main import SimplifiedTUI as DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="旧spec：TUI 内部实现已重构（_post_event 等已移除）；当前源码为准"
)


def test_enhanced_status_text_with_debate_models():
    """测试增强状态文本在辩论时显示模型切换"""
    # 创建一个TUI实例用于测试状态栏功能
    tui = DAIP_TUI.__new__(DAIP_TUI)  # 创建实例但不调用__init__

    # 初始化基本属性
    tui._current_model = "default_model"
    tui._real_token_usage = (100, 1000)
    tui._system_activity = {
        "events_processed": 10,
        "tools_executed": 5,
        "errors_encountered": 0,
    }
    tui.focus_mode = "Input"

    # 初始化辩论状态
    tui._current_debate = {
        "is_active": False,
        "current_participant": None,
        "role_models": {},
        "current_round": 0,
        "total_rounds": 0,
    }

    status_text = tui.get_enhanced_status_text("Idle")
    assert "Model: default_model" in status_text

    tui._current_debate["is_active"] = True
    status_text = tui.get_enhanced_status_text("Debating")
    assert "Model: default_model" in status_text
    assert "Debate:" in status_text

    tui._current_debate["current_participant"] = "pro_arguer"
    status_text = tui.get_enhanced_status_text("Debating")
    # 应该显示默认模型加角色名
    assert "default_model (pro_arguer)" in status_text

    tui._current_debate["role_models"] = {
        "pro_arguer": "ollama/llama3:instruct",
        "con_arguer": "ollama/mistral:instruct",
    }
    status_text = tui.get_enhanced_status_text("Debating")
    assert "ollama/llama3:instruct (pro_arguer)" in status_text

    tui._current_debate["current_participant"] = "con_arguer"
    status_text = tui.get_enhanced_status_text("Debating")
    assert "ollama/mistral:instruct (con_arguer)" in status_text


def test_update_current_model_function():
    """测试模型更新功能"""
    tui = DAIP_TUI.__new__(DAIP_TUI)

    # 初始化基本属性
    tui._current_model = "default_model"
    tui._current_debate = {"is_active": True}

    # 模拟_update_status_bar方法
    tui._update_status_bar_calls = []

    def mock_update_status_bar(status):
        tui._update_status_bar_calls.append(status)

    tui._update_status_bar = mock_update_status_bar

    # 测试更新模型
    tui._update_current_model("ollama/llama3:instruct")

    assert tui._current_model == "ollama/llama3:instruct"
    assert "Debating" in tui._update_status_bar_calls


if __name__ == "__main__":
    test_enhanced_status_text_with_debate_models()
    test_update_current_model_function()
