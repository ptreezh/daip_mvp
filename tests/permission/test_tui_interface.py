"""
TUI权限界面测试 - 真实功能验证
测试权限请求界面的显示和用户交互功能
"""

import asyncio

import pytest

from daip_live.core.models import PermissionRequestEvent, PermissionResponse
from daip_live.permission.tui_interface import (
    PermissionTUIInterface,
    PermissionUIDisplay,
    PermissionUITheme,
    PermissionUITimeout,
)


class TestPermissionTUIInterface:
    """测试TUI权限界面功能"""

    @pytest.fixture
    def user_input_queue(self):
        """提供用户输入队列"""
        return asyncio.Queue()

    @pytest.fixture
    def tui_interface(self, user_input_queue):
        """提供TUI界面实例"""
        return PermissionTUIInterface(user_input_queue)

    @pytest.fixture
    def sample_permission_request(self):
        """提供权限请求测试数据"""
        return PermissionRequestEvent(
            tool_name="read_file",
            args={"path": "test.txt", "mode": "r"},
            risk_level="low",
            description="Read file contents for analysis",
            timeout_seconds=30.0,
        )

    def test_permission_interface_creation(self):
        """验证TUI界面创建 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        assert tui.user_input_queue == user_queue
        assert tui.current_request is None
        assert tui.response_future is None

    def test_permission_interface_rendering_basic(self, tui_interface):
        """验证权限界面基本渲染 - 绿"""
        request = PermissionRequestEvent(
            tool_name="read_file",
            args={"path": "test.txt"},
            risk_level="low",
        )

        content = tui_interface._render_permission_interface_content(request)

        assert "TOOL PERMISSION REQUEST" in content
        assert "read_file" in content
        assert "test.txt" in content
        assert "[Y] Yes" in content
        assert "[N] No" in content

    def test_permission_interface_risk_levels(self, tui_interface):
        """验证不同风险等级的界面渲染 - 绿"""
        test_cases = [("low", "🟢"), ("medium", "🟡"), ("high", "🔴")]

        for risk_level, expected_indicator in test_cases:
            request = PermissionRequestEvent(
                tool_name="test_tool",
                args={},
                risk_level=risk_level,  # type: ignore[arg-type]
            )

            content = tui_interface._render_permission_interface_content(request)

            assert expected_indicator in content
            assert risk_level.upper() in content

    def test_permission_interface_special_tools(self, tui_interface):
        """验证特殊工具的警告信息 - 绿"""
        request = PermissionRequestEvent(
            tool_name="read_file",
            args={"path": "/etc/passwd"},
            risk_level="high",
        )

        warning = tui_interface._get_risk_warning(
            request.tool_name, request.args, request.risk_level
        )

        assert "file system resources" in warning
        assert "/etc/passwd" in warning

    def test_user_input_parsing_valid(self):
        """验证有效用户输入解析 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        test_cases = [
            ("y", PermissionResponse.GRANT),
            ("Y", PermissionResponse.GRANT),
            ("yes", PermissionResponse.GRANT),
            ("n", PermissionResponse.DENY),
            ("N", PermissionResponse.DENY),
            ("no", PermissionResponse.DENY),
            ("a", PermissionResponse.ALWAYS),
            ("A", PermissionResponse.ALWAYS),
            ("always", PermissionResponse.ALWAYS),
            ("v", PermissionResponse.NEVER),
            ("V", PermissionResponse.NEVER),
            ("never", PermissionResponse.NEVER),
            ("c", PermissionResponse.CANCEL),
            ("C", PermissionResponse.CANCEL),
            ("cancel", PermissionResponse.CANCEL),
        ]

        for input_str, expected_response in test_cases:
            response = tui._parse_user_input(input_str)
            assert response == expected_response

    def test_user_input_parsing_invalid(self):
        """验证无效用户输入处理 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        invalid_inputs = [
            "",
            "invalid",
            "xyz",
            "123",
            "maybe",
            None,
        ]

        for invalid_input in invalid_inputs:
            response = tui._parse_user_input(invalid_input)
            assert response is None

    def test_user_input_parsing_whitespace(self):
        """验证带空白字符的输入处理 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        test_cases = [
            (" y ", PermissionResponse.GRANT),
            ("\t\n", PermissionResponse.DENY),
            ("  a  ", PermissionResponse.ALWAYS),
        ]

        for input_str, expected_response in test_cases:
            response = tui._parse_user_input(input_str)
            assert response == expected_response

    @pytest.mark.asyncio
    async def test_permission_timeout_handling(self):
        """验证权限请求超时处理 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        await tui.show_permission_request(request)

        # 不放入任何用户输入，模拟超时
        response = await tui.get_user_response(timeout=0.1)

        assert response == PermissionResponse.DENY

    @pytest.mark.asyncio
    async def test_permission_confirmation_always(self):
        """验证"始终授予"确认流程 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        await user_queue.put("a")
        await user_queue.put("y")  # 确认选择

        request = PermissionRequestEvent(tool_name="test", args={})
        await tui.show_permission_request(request)
        response = await tui.get_user_response()

        assert response == PermissionResponse.ALWAYS

    @pytest.mark.asyncio
    async def test_permission_confirmation_cancelled(self):
        """验证确认取消处理 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        # 用户选择"始终授予"但取消确认，然后重新选择普通授予
        await user_queue.put("a")
        await user_queue.put("n")  # 取消确认
        await user_queue.put("y")  # 重新选择授予

        request = PermissionRequestEvent(tool_name="test", args={})
        await tui.show_permission_request(request)
        response = await tui.get_user_response()

        # 取消确认后重新等待输入，第二次选择生效
        assert response == PermissionResponse.GRANT

    def test_permission_interface_argument_formatting(self):
        """验证参数格式化 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)

        long_args = {
            "data": "x" * 200,
            "path": "/very/long/path/to/some/file.txt",
            "extra1": "y" * 200,
            "extra2": "z" * 200,
        }

        formatted = tui._format_arguments(long_args)

        assert len(formatted) < 200
        assert "..." in formatted  # 4个参数只显示前3个

    @pytest.mark.asyncio
    async def test_permission_interface_error_handling(self, monkeypatch):
        """验证界面渲染错误处理 - 绿"""
        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)
        request = PermissionRequestEvent(tool_name="test", args={})

        rendered: list[str] = []

        async def capture_render(content: str) -> None:
            rendered.append(content)

        monkeypatch.setattr(tui, "_render_to_screen", capture_render)

        def boom(req):
            raise RuntimeError("render failed")

        monkeypatch.setattr(tui, "_render_permission_interface_content", boom)

        # 渲染失败时应降级到简化界面而不是崩溃
        await tui.show_permission_request(request)

        assert rendered
        assert any("Permission Request for:" in c for c in rendered)

    def test_permission_ui_theme_configuration(self):
        """验证UI主题配置 - 绿"""
        custom_theme = PermissionUITheme(
            border_char="*",
            header_prefix=">>",
            warning_prefix="!!",
        )

        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)
        tui.theme = custom_theme

        request = PermissionRequestEvent(tool_name="test", args={})
        content = tui._render_permission_interface_content(request)

        assert "*" * 70 in content
        assert ">> TOOL PERMISSION REQUEST" in content

    def test_permission_ui_display_configuration(self):
        """验证显示配置 - 绿"""
        custom_display = PermissionUIDisplay(
            show_risk_level=False,
            show_arguments=False,
            show_description=False,
        )

        user_queue = asyncio.Queue()
        tui = PermissionTUIInterface(user_queue)
        tui.display_config = custom_display

        request = PermissionRequestEvent(tool_name="test", args={}, risk_level="high")
        content = tui._render_permission_interface_content(request)

        assert "Risk Level:" not in content
        assert "Arguments:" not in content
        assert "Description:" not in content


class TestPermissionUIConfiguration:
    """测试权限UI配置功能"""

    def test_permission_ui_theme_defaults(self):
        """验证默认主题配置 - 绿"""
        theme = PermissionUITheme()

        assert theme.border_char == "═"
        assert theme.header_prefix == "🔒"
        assert theme.warning_prefix == "⚠️"
        assert theme.success_prefix == "✅"
        assert theme.error_prefix == "❌"
        assert theme.info_prefix == "ℹ️"

    def test_permission_ui_timeout_defaults(self):
        """验证默认超时配置 - 绿"""
        timeout = PermissionUITimeout()

        assert timeout.default_timeout == 30.0
        assert timeout.warning_threshold == 10.0
        assert timeout.countdown_interval == 1.0
        assert timeout.confirmation_timeout == 10.0

    def test_permission_ui_display_defaults(self):
        """验证默认显示配置 - 绿"""
        display = PermissionUIDisplay()

        assert display.show_risk_level
        assert display.show_arguments
        assert display.show_description
        assert display.show_countdown
        assert display.show_confirmation


# 测试工具函数
@pytest.fixture
def mock_user_input_queue():
    """提供模拟用户输入队列"""
    queue = asyncio.Queue()
    return queue


@pytest.fixture
def sample_permission_requests():
    """提供各种权限请求测试数据"""
    return {
        "basic": {
            "tool_name": "read_file",
            "args": {"path": "test.txt"},
            "risk_level": "low",
        },
        "medium_risk": {
            "tool_name": "write_file",
            "args": {"path": "output.txt"},
            "risk_level": "medium",
            "description": "Write output to file",
        },
        "high_risk": {
            "tool_name": "execute_command",
            "args": {"command": "ls -la"},
            "risk_level": "high",
            "description": "Execute system command",
        },
        "file_system": {
            "tool_name": "read_file",
            "args": {"path": "/etc/passwd"},
            "risk_level": "high",
        },
        "network": {
            "tool_name": "http_request",
            "args": {"url": "https://api.example.com/data"},
            "risk_level": "medium",
        },
    }


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
