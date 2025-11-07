#!/usr/bin/env python3
"""
测试用例：重现TUI删除键无法删除斜杠指令的问题
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

class TestTUIInputDeletion(unittest.TestCase):
    """测试TUI输入删除问题"""
    
    def setUp(self):
        """设置测试环境"""
        # 导入TUI类
        from daip_live.tui import DAIP_TUI
        self.tui = DAIP_TUI()
        
        # 创建模拟的输入组件
        self.mock_input = Mock()
        self.mock_input.value = ""
        
        # 模拟query_one方法返回我们的mock输入
        self.tui.query_one = Mock(return_value=self.mock_input)
        
    def test_input_change_with_autocomplete_selection(self):
        """测试输入改变时自动完成选择的问题"""
        print("\n=== 测试输入改变时自动完成选择的问题 ===")
        
        # 模拟用户输入"/role"
        self.mock_input.value = "/role"
        
        # 创建模拟的消息
        class MockMessage:
            def __init__(self, value):
                self.value = value
        
        message = MockMessage("/role")
        
        # 调用on_input_changed方法
        with patch.object(self.tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟返回一个建议
            mock_get_suggestions.return_value = ["/role list - 角色管理"]
            
            # 调用输入改变处理方法
            self.tui.on_input_changed(message)
            
            # 检查是否设置了自动完成建议
            print(f"输入值: {self.mock_input.value}")
            print(f"是否调用了_get_autocomplete_suggestions: {mock_get_suggestions.called}")
            
    def test_input_deletion_issue(self):
        """测试删除键问题"""
        print("\n=== 测试删除键问题 ===")
        
        # 模拟用户先输入"/role"，然后删除到"/ro"
        self.mock_input.value = "/ro"
        
        # 创建模拟的消息
        class MockMessage:
            def __init__(self, value):
                self.value = value
        
        message = MockMessage("/ro")
        
        # 调用on_input_changed方法
        with patch.object(self.tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟返回一个建议（这会导致问题）
            mock_get_suggestions.return_value = ["/role list - 角色管理"]
            
            # 调用输入改变处理方法
            self.tui.on_input_changed(message)
            
            # 检查输入值是否被自动完成覆盖
            print(f"删除后的输入值: {self.mock_input.value}")
            print(f"是否存在问题: 输入值被自动完成建议覆盖")
            
    def test_correct_deletion_behavior(self):
        """测试正确的删除行为"""
        print("\n=== 测试正确的删除行为 ===")
        
        # 模拟用户想要删除整个指令
        self.mock_input.value = ""
        
        # 创建模拟的消息
        class MockMessage:
            def __init__(self, value):
                self.value = value
        
        message = MockMessage("")
        
        # 调用on_input_changed方法
        with patch.object(self.tui, '_get_autocomplete_suggestions') as mock_get_suggestions:
            # 模拟没有建议
            mock_get_suggestions.return_value = []
            
            # 调用输入改变处理方法
            self.tui.on_input_changed(message)
            
            # 检查输入值是否保持为空
            print(f"清空后的输入值: {self.mock_input.value}")
            print(f"正确行为: 输入值保持为空，允许用户输入新内容")

def main():
    """主函数"""
    print("开始测试TUI输入删除问题...")
    print("=" * 50)
    
    # 运行测试
    unittest.main(verbosity=2)

if __name__ == "__main__":
    main()