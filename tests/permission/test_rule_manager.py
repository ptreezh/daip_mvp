#!/usr/bin/env python3
"""
权限规则配置功能测试
基于TDD驱动，遵循KISS YAGNI SOLID原则
"""

import unittest
import os
import sys
import tempfile
import yaml
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daip_live.permission.rule_manager import (
    PermissionRuleManagerInterface,
    PermissionRuleManager,
    PermissionRuleManagerFactory
)


class TestPermissionRuleManagerInterface(unittest.TestCase):
    """权限规则管理器接口测试"""
    
    def test_interface_methods_exist(self):
        """测试接口方法是否存在"""
        # 检查接口是否定义了所有必需的方法
        self.assertTrue(hasattr(PermissionRuleManagerInterface, 'get_tool_permission'))
        self.assertTrue(hasattr(PermissionRuleManagerInterface, 'set_tool_permission'))
        self.assertTrue(hasattr(PermissionRuleManagerInterface, 'reset_tool_permission'))
        self.assertTrue(hasattr(PermissionRuleManagerInterface, 'set_default_permission'))
        self.assertTrue(hasattr(PermissionRuleManagerInterface, 'list_permission_rules'))


class TestPermissionRuleManager(unittest.TestCase):
    """权限规则管理器实现测试"""
    
    def setUp(self):
        """测试前置条件"""
        # 创建临时配置文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "permissions.yaml")
        self.permission_manager = PermissionRuleManager(self.config_file)
    
    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()
    
    def test_initialization_with_default_config(self):
        """测试使用默认配置初始化"""
        # 测试权限规则管理器能否使用默认配置初始化
        manager = PermissionRuleManager()
        self.assertIsInstance(manager, PermissionRuleManagerInterface)
        self.assertEqual(manager.get_default_permission(), "ask")
    
    def test_initialization_with_custom_config_file(self):
        """测试使用自定义配置文件初始化"""
        # 测试权限规则管理器能否使用自定义配置文件初始化
        manager = PermissionRuleManager(self.config_file)
        self.assertIsInstance(manager, PermissionRuleManagerInterface)
        self.assertEqual(manager.get_default_permission(), "ask")
    
    def test_get_tool_permission_default(self):
        """测试获取工具默认权限"""
        # 测试未配置的工具应返回默认权限
        permission = self.permission_manager.get_tool_permission("test_tool")
        self.assertEqual(permission, "ask")
    
    def test_set_and_get_tool_permission(self):
        """测试设置和获取工具权限"""
        # 测试设置工具权限后能否正确获取
        self.permission_manager.set_tool_permission("test_tool", "allow")
        permission = self.permission_manager.get_tool_permission("test_tool")
        self.assertEqual(permission, "allow")
    
    def test_set_tool_permission_invalid_value(self):
        """测试设置工具权限时使用无效值"""
        # 测试设置无效权限值时应抛出异常
        with self.assertRaises(ValueError):
            self.permission_manager.set_tool_permission("test_tool", "invalid")
    
    def test_reset_tool_permission(self):
        """测试重置工具权限"""
        # 先设置工具权限
        self.permission_manager.set_tool_permission("test_tool", "deny")
        self.assertEqual(self.permission_manager.get_tool_permission("test_tool"), "deny")
        
        # 重置工具权限后应返回默认值
        self.permission_manager.reset_tool_permission("test_tool")
        self.assertEqual(self.permission_manager.get_tool_permission("test_tool"), "ask")
    
    def test_set_and_get_default_permission(self):
        """测试设置和获取默认权限"""
        # 测试设置默认权限后能否正确获取
        self.permission_manager.set_default_permission("deny")
        self.assertEqual(self.permission_manager.get_default_permission(), "deny")
        
        # 测试工具未配置时应使用新的默认权限
        permission = self.permission_manager.get_tool_permission("another_tool")
        self.assertEqual(permission, "deny")
    
    def test_set_default_permission_invalid_value(self):
        """测试设置默认权限时使用无效值"""
        # 测试设置无效默认权限值时应抛出异常
        with self.assertRaises(ValueError):
            self.permission_manager.set_default_permission("invalid")
    
    def test_list_permission_rules(self):
        """测试列出权限规则"""
        # 设置几个工具的权限
        self.permission_manager.set_tool_permission("tool1", "allow")
        self.permission_manager.set_tool_permission("tool2", "deny")
        
        # 获取权限规则列表
        rules = self.permission_manager.list_permission_rules()
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules["tool1"], "allow")
        self.assertEqual(rules["tool2"], "deny")
    
    def test_config_persistence(self):
        """测试配置持久化"""
        # 设置一些权限规则
        self.permission_manager.set_tool_permission("persistent_tool", "allow")
        self.permission_manager.set_default_permission("deny")
        
        # 创建新的管理器实例
        new_manager = PermissionRuleManager(self.config_file)
        
        # 验证配置是否持久化
        self.assertEqual(new_manager.get_default_permission(), "deny")
        self.assertEqual(new_manager.get_tool_permission("persistent_tool"), "allow")


class TestPermissionRuleManagerFactory(unittest.TestCase):
    """权限规则管理器工厂测试"""
    
    def test_create_permission_rule_manager(self):
        """测试创建权限规则管理器"""
        # 测试工厂能否创建权限规则管理器实例
        manager = PermissionRuleManagerFactory.create_permission_rule_manager()
        self.assertIsInstance(manager, PermissionRuleManagerInterface)
        self.assertIsInstance(manager, PermissionRuleManager)


class TestPermissionRuleManagerWithExistingConfig(unittest.TestCase):
    """使用现有配置文件的权限规则管理器测试"""
    
    def setUp(self):
        """测试前置条件"""
        # 创建临时配置文件并写入测试数据
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "permissions.yaml")
        
        # 创建测试配置
        test_config = {
            'permission_rules': {
                'default': 'deny',
                'tools': {
                    'read_file': 'allow',
                    'write_file': 'ask'
                }
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
    
    def tearDown(self):
        """测试后清理"""
        self.temp_dir.cleanup()
    
    def test_load_existing_config(self):
        """测试加载现有配置"""
        # 创建权限规则管理器，应加载现有配置
        manager = PermissionRuleManager(self.config_file)
        
        # 验证配置是否正确加载
        self.assertEqual(manager.get_default_permission(), "deny")
        self.assertEqual(manager.get_tool_permission("read_file"), "allow")
        self.assertEqual(manager.get_tool_permission("write_file"), "ask")
        self.assertEqual(manager.get_tool_permission("unknown_tool"), "deny")


def run_tests():
    """运行所有测试"""
    print("开始权限规则配置功能测试...")
    
    # 创建测试套件
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加所有测试类
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionRuleManagerInterface))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionRuleManager))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionRuleManagerFactory))
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionRuleManagerWithExistingConfig))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


def main():
    """主测试函数"""
    success = run_tests()
    
    if success:
        print("\n🎉 所有权限规则配置功能测试通过!")
        return 0
    else:
        print("\n❌ 部分权限规则配置功能测试失败!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
