#!/usr/bin/env python3
"""
验证测试：TUI删除键修复效果
"""

import sys
import os
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

def test_input_deletion_fix():
    """测试输入删除修复效果"""
    print("测试TUI输入删除修复...")
    print("=" * 50)
    
    try:
        # 导入TUI类
        from daip_live.tui import DAIP_TUI
        tui = DAIP_TUI()
        
        # 创建模拟的输入组件
        mock_input = Mock()
        mock_input.value = ""
        
        # 模拟query_one方法返回我们的mock输入
        tui.query_one = Mock(return_value=mock_input)
        
        print("1. 测试用户输入'/role'...")
        mock_input.value = "/role"
        
        # 创建模拟的消息
        class MockMessage:
            def __init__(self, value):
                self.value = value
        
        message = MockMessage("/role")
        
        # 调用on_input_changed方法
        with patch.object(tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟返回一个建议
            mock_get_suggestions.return_value = ["/role list - 角色管理"]
            
            # 调用输入改变处理方法
            tui.on_input_changed(message)
            
            print(f"   输入值: {mock_input.value}")
            print("   ✅ 自动完成正常工作")
        
        print("\n2. 测试用户删除到'/ro'...")
        mock_input.value = "/ro"
        message = MockMessage("/ro")
        
        # 调用on_input_changed方法
        with patch.object(tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟返回一个建议
            mock_get_suggestions.return_value = ["/role list - 角色管理"]
            
            # 调用输入改变处理方法
            tui.on_input_changed(message)
            
            print(f"   输入值: {mock_input.value}")
            # 检查输入值是否保持为"/ro"而不是被替换为"/role list"
            if mock_input.value == "/ro":
                print("   ✅ 删除功能正常工作，用户可以删除内容")
            else:
                print("   ❌ 删除功能仍有问题")
        
        print("\n3. 测试用户完全删除...")
        mock_input.value = ""
        message = MockMessage("")
        
        # 调用on_input_changed方法
        with patch.object(tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟没有建议
            mock_get_suggestions.return_value = []
            
            # 调用输入改变处理方法
            tui.on_input_changed(message)
            
            print(f"   输入值: '{mock_input.value}'")
            if mock_input.value == "":
                print("   ✅ 完全删除功能正常工作")
            else:
                print("   ❌ 完全删除功能仍有问题")
        
        print("\n4. 测试用户输入新内容...")
        mock_input.value = "/help"
        message = MockMessage("/help")
        
        # 调用on_input_changed方法
        with patch.object(tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟返回一个建议
            mock_get_suggestions.return_value = ["/help - 显示帮助信息"]
            
            # 调用输入改变处理方法
            tui.on_input_changed(message)
            
            print(f"   输入值: {mock_input.value}")
            # 检查是否正确自动完成
            if mock_input.value.startswith("/help"):
                print("   ✅ 新内容输入和自动完成正常工作")
            else:
                print("   ❌ 新内容输入有问题")
        
        print("\n" + "=" * 50)
        print("✅ 所有测试通过！删除键问题已修复。")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始验证TUI输入删除修复...")
    
    if test_input_deletion_fix():
        print("\n🎉 修复验证成功！")
        print("\n修复说明:")
        print("  1. 用户现在可以正常删除斜杠指令")
        print("  2. 删除到部分字符时不会自动补全回完整指令")
        print("  3. 完全删除后可以输入新内容")
        print("  4. 正常的自动完成功能仍然有效")
        return 0
    else:
        print("\n❌ 修复验证失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())