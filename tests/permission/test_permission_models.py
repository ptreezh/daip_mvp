"""
权限模型测试 - 对齐当前真实实现（枚举/模型已在 core.models 实现）。

原文件为 TDD 红阶段空壳（断言全注释 + skip），功能已实现，重写为可执行测试。
"""

from daip_live.core.models import (
    PermissionInteraction,
    PermissionResponse,
    PermissionState,
)


class TestPermissionResponse:
    """测试PermissionResponse枚举"""

    def test_permission_response_enum_values(self):
        """验证PermissionResponse枚举值定义正确"""
        assert PermissionResponse.GRANT.value == "grant"
        assert PermissionResponse.DENY.value == "deny"
        assert PermissionResponse.ALWAYS.value == "always"
        assert PermissionResponse.NEVER.value == "never"
        assert PermissionResponse.CANCEL.value == "cancel"


class TestPermissionState:
    """测试PermissionState枚举"""

    def test_permission_state_enum_values(self):
        """验证PermissionState枚举值定义正确"""
        states = {s.name for s in PermissionState}
        assert "PENDING" in states
        assert "GRANTED" in states
        assert "DENIED" in states


class TestPermissionInteraction:
    """测试PermissionInteraction模型（对齐真实 API：args 必填 + update_response）"""

    def test_permission_interaction_creation(self):
        """创建PermissionInteraction实例"""
        interaction = PermissionInteraction(
            tool_name="read_file", args={"path": "/tmp/x"}
        )
        assert interaction.tool_name == "read_file"
        assert interaction.state == PermissionState.PENDING
        assert interaction.request_id.startswith("perm_")

    def test_permission_interaction_grant(self):
        """update_response(GRANT) 后 to_result().granted 为 True"""
        interaction = PermissionInteraction(tool_name="read_file", args={})
        interaction.update_response(PermissionResponse.GRANT)
        result = interaction.to_result()
        assert result.granted is True

    def test_permission_interaction_deny(self):
        """update_response(DENY) 后 to_result().granted 为 False"""
        interaction = PermissionInteraction(tool_name="read_file", args={})
        interaction.update_response(PermissionResponse.DENY)
        result = interaction.to_result()
        assert result.granted is False
