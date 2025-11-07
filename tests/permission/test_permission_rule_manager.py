#!/usr/bin/env python3
"""
TUI权限命令功能测试脚本
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daip_live.permission.rule_manager import PermissionRuleManager


def test_permission_commands():
    """测试权限命令功能"""
    print("开始TUI权限命令功能测试...")
    
    # 创建临时配置文件
    temp_dir = tempfile.TemporaryDirectory()
    config_file = os.path.join(temp_dir.name, "permissions.yaml")
    
    try:
        # 创建权限规则管理器
        permission_manager = PermissionRuleManager(config_file)
        
        # 测试设置默认权限
        print("1. 测试设置默认权限...")
        permission_manager.set_default_permission("deny")
        assert permission_manager.get_default_permission() == "deny"
        print("   ✓ 默认权限设置成功")
        
        # 测试设置工具权限
        print("2. 测试设置工具权限...")
        permission_manager.set_tool_permission("test_tool", "allow")
        assert permission_manager.get_tool_permission("test_tool") == "allow"
        print("   ✓ 工具权限设置成功")
        
        # 测试列出权限规则
        print("3. 测试列出权限规则...")
        rules = permission_manager.list_permission_rules()
        assert "test_tool" in rules
        assert rules["test_tool"] == "allow"
        print("   ✓ 权限规则列表正确")
        
        # 测试重置工具权限
        print("4. 测试重置工具权限...")
        permission_manager.reset_tool_permission("test_tool")
        assert permission_manager.get_tool_permission("test_tool") == "deny"  # 应该回到默认值
        print("   ✓ 工具权限重置成功")
        
        # 测试配置持久化
        print("5. 测试配置持久化...")
        # 创建新的管理器实例
        new_manager = PermissionRuleManager(config_file)
        assert new_manager.get_default_permission() == "deny"
        print("   ✓ 配置持久化成功")
        
        print("\n🎉 所有TUI权限命令功能测试通过!")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False
        
    finally:
        # 清理临时目录
        temp_dir.cleanup()


def main():
    """主测试函数"""
    success = test_permission_commands()
    
    if success:
        print("\n🎉 TUI权限命令功能测试完成!")
        return 0
    else:
        print("\n❌ TUI权限命令功能测试失败!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)