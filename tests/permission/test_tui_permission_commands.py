#!/usr/bin/env python3
"""
权限管理TUI集成测试
"""

import sys
import os
import tempfile
import asyncio
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daip_live.permission.rule_manager import PermissionRuleManager
from daip_live.tui import DAIP_TUI


class MockTUI(DAIP_TUI):
    """模拟TUI类用于测试"""
    
    def __init__(self):
        # 创建临时配置文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "permissions.yaml")
        
        # 初始化权限规则管理器
        self._permission_rule_manager = PermissionRuleManager(self.config_file)
        
        # 模拟日志更新方法
        self.log_messages = []
    
    def _update_log_view(self, message):
        """模拟日志更新方法"""
        self.log_messages.append(message)
        print(message)
    
    def cleanup(self):
        """清理临时目录"""
        self.temp_dir.cleanup()


def test_tui_permission_commands():
    """测试TUI权限命令功能"""
    print("开始TUI权限命令集成测试...")
    
    # 创建模拟TUI实例
    tui = MockTUI()
    
    try:
        # 测试权限列表命令
        print("1. 测试权限列表命令...")
        tui._handle_permission_list()
        assert len(tui.log_messages) > 0
        print("   ✓ 权限列表命令执行成功")
        
        # 测试设置默认权限命令
        print("2. 测试设置默认权限命令...")
        tui.log_messages.clear()
        tui._handle_permission_default("allow")
        assert any("Default permission set to 'allow'" in msg for msg in tui.log_messages)
        print("   ✓ 设置默认权限命令执行成功")
        
        # 验证默认权限已设置
        assert tui._permission_rule_manager.get_default_permission() == "allow"
        print("   ✓ 默认权限设置验证成功")
        
        # 测试设置工具权限命令
        print("3. 测试设置工具权限命令...")
        tui.log_messages.clear()
        tui._handle_permission_set("test_tool", "deny")
        assert any("Permission rule for 'test_tool' set to 'deny'" in msg for msg in tui.log_messages)
        print("   ✓ 设置工具权限命令执行成功")
        
        # 验证工具权限已设置
        assert tui._permission_rule_manager.get_tool_permission("test_tool") == "deny"
        print("   ✓ 工具权限设置验证成功")
        
        # 测试权限列表命令（带数据）
        print("4. 测试权限列表命令（带数据）...")
        tui.log_messages.clear()
        tui._handle_permission_list()
        assert any("Permission Rules:" in msg for msg in tui.log_messages)
        assert any("test_tool: deny" in msg for msg in tui.log_messages)
        print("   ✓ 权限列表命令（带数据）执行成功")
        
        # 测试重置工具权限命令
        print("5. 测试重置工具权限命令...")
        tui.log_messages.clear()
        tui._handle_permission_reset("test_tool")
        assert any("Permission rule for 'test_tool' reset to default" in msg for msg in tui.log_messages)
        print("   ✓ 重置工具权限命令执行成功")
        
        # 验证工具权限已重置
        assert tui._permission_rule_manager.get_tool_permission("test_tool") == "allow"  # 应该回到默认值
        print("   ✓ 工具权限重置验证成功")
        
        # 测试无效权限值处理
        print("6. 测试无效权限值处理...")
        tui.log_messages.clear()
        tui._handle_permission_set("test_tool2", "invalid")
        assert any("Invalid permission value: invalid" in msg for msg in tui.log_messages)
        print("   ✓ 无效权限值处理成功")
        
        print("\n🎉 所有TUI权限命令集成测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理
        tui.cleanup()


def test_tui_autocomplete():
    """测试TUI自动补全功能"""
    print("\n开始TUI自动补全功能测试...")
    
    # 创建模拟TUI实例
    tui = MockTUI()
    
    try:
        # 测试权限命令自动补全
        print("1. 测试权限命令自动补全...")
        suggestions = tui._get_autocomplete_suggestions("/permission ")
        expected_commands = ["/permission list", "/permission set", "/permission reset", "/permission default"]
        for cmd in expected_commands:
            assert cmd in suggestions, f"缺少自动补全命令: {cmd}"
        print("   ✓ 权限命令自动补全成功")
        
        # 测试权限设置命令自动补全
        print("2. 测试权限设置命令自动补全...")
        suggestions = tui._get_autocomplete_suggestions("/permission set test_tool ")
        expected_values = ["/permission set test_tool allow", "/permission set test_tool deny", "/permission set test_tool ask"]
        for value in expected_values:
            assert value in suggestions, f"缺少权限值自动补全: {value}"
        print("   ✓ 权限设置命令自动补全成功")
        
        # 测试默认权限命令自动补全
        print("3. 测试默认权限命令自动补全...")
        suggestions = tui._get_autocomplete_suggestions("/permission default ")
        expected_values = ["/permission default allow", "/permission default deny", "/permission default ask"]
        for value in expected_values:
            assert value in suggestions, f"缺少默认权限值自动补全: {value}"
        print("   ✓ 默认权限命令自动补全成功")
        
        print("\n🎉 所有TUI自动补全功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 自动补全测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理
        tui.cleanup()


def main():
    """主测试函数"""
    # 测试TUI权限命令功能
    command_success = test_tui_permission_commands()
    
    # 测试TUI自动补全功能
    autocomplete_success = test_tui_autocomplete()
    
    if command_success and autocomplete_success:
        print("\n🎉 所有TUI权限管理集成测试通过!")
        return 0
    else:
        print("\n❌ 部分TUI权限管理集成测试失败!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)