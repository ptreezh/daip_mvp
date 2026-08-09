"""
TUI 交互冒烟测试（G10 自动化，2026-08-09）。

使用 Textual 的 run_test() 在 headless 模式启动 SimplifiedTUI，
验证应用可挂载、渲染并接受基本输入——此前 G10 仅有"进程存活"级冒烟。
"""

from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_simplified_tui_launches_and_renders():
    """TUI 启动 + 渲染（输入区存在）。"""
    from daip_live.tui.simplified_main import SimplifiedTUI

    with patch("daip_live.container.Container"):
        app = SimplifiedTUI()
        async with app.run_test() as pilot:
            await pilot.pause()

            assert app.is_running
            # 核心组件已渲染
            input_widget = app.query_one("#user_input")
            assert input_widget is not None


@pytest.mark.asyncio
async def test_simplified_tui_accepts_input_and_system_keys():
    """基本交互：输入文本 + 系统快捷键路径不崩溃（ctrl+e 委托 _handle_system_keys）。"""
    from daip_live.tui.simplified_main import SimplifiedTUI

    with patch("daip_live.container.Container"):
        app = SimplifiedTUI()
        async with app.run_test() as pilot:
            await pilot.pause()

            input_widget = app.query_one("#user_input")
            input_widget.value = "你好"
            await pilot.pause()

            # 系统快捷键处理不崩溃（action_show_exit_confirmation 需容器动作，仅验证路径可达性）
            app._handle_system_keys(
                type("E", (), {"key": "escape", "prevent_default": lambda: None})()
            )
            await pilot.pause()
            assert app.is_running
