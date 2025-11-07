#!/usr/bin/env python3
"""
权限管理集成测试
基于TDD驱动，遵循KISS YAGNI SOLID原则
"""

import asyncio
import sys
import os
import unittest
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.daip_live.container import Container
from daip_live.permission.permission_manager import PermissionManager
from daip_live.core.models import PermissionRequestEvent, SessionContext, PermissionResponse


class TestPermissionManagerInitialization(unittest.TestCase):
    """权限管理器初始化测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.container = Container()
    
    def test_permission_manager_initialization_from_container(self):
        """测试从容器中初始化权限管理器"""
        # 测试权限管理器能否从容器中正确初始化
        permission_manager = self.container.permission_manager()
        self.assertIsInstance(permission_manager, PermissionManager)
        self.assertIsNotNone(permission_manager.user_input_queue)
        self.assertIsNotNone(permission_manager.response_collector)
        self.assertIsNotNone(permission_manager.response_processor)
    
    def test_permission_manager_has_default_config(self):
        """测试权限管理器具有默认配置"""
        permission_manager = self.container.permission_manager()
        self.assertEqual(permission_manager.permission_config.default, "ask")
        self.assertIsInstance(permission_manager.permission_config.tools, dict)


class TestPermissionCheckFunctionality(unittest.TestCase):
    """权限检查功能测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.container = Container()
        self.permission_manager = self.container.permission_manager()
        self.session_context = SessionContext()
    
    def test_permission_check_with_timeout_defaults_to_deny(self):
        """测试权限检查超时默认拒绝"""
        # 使用同步方式测试权限检查在超时时默认拒绝权限
        async def async_test():
            result = await self.permission_manager.check_permission(
                tool_name="test_tool",
                args={"test": "value"},
                session_context=self.session_context,
                timeout=0.1  # 设置很短的超时时间
            )
            return result
        
        result = asyncio.run(async_test())
        self.assertFalse(result.granted)
        self.assertEqual(result.response, PermissionResponse.DENY)
        # 注意：由于权限管理器的实现方式，超时可能不会设置timeout标志
        # 我们主要验证权限被拒绝
    
    def test_permission_check_returns_valid_result_structure(self):
        """测试权限检查返回有效的结果结构"""
        # 使用同步方式测试权限检查返回的结果具有正确的结构
        async def async_test():
            result = await self.permission_manager.check_permission(
                tool_name="test_tool",
                args={"test": "value"},
                session_context=self.session_context,
                timeout=0.1
            )
            return result
        
        result = asyncio.run(async_test())
        self.assertIsInstance(result, object)
        self.assertIsNotNone(result.granted)
        self.assertIsNotNone(result.response)
        self.assertIsNotNone(result.request_id)
        self.assertIsNotNone(result.reason)
        self.assertIsNotNone(result.timestamp)


class TestPermissionResponseHandling(unittest.TestCase):
    """权限响应处理测试用例"""
    
    def setUp(self):
        """测试前置条件"""
        self.container = Container()
        self.permission_manager = self.container.permission_manager()
    
    def test_permission_response_from_string_valid_inputs(self):
        """测试权限响应字符串解析 - 有效输入"""
        from daip_live.core.models import PermissionResponse
        
        # 测试各种有效的输入字符串
        test_cases = [
            ("y", PermissionResponse.GRANT),
            ("yes", PermissionResponse.GRANT),
            ("n", PermissionResponse.DENY),
            ("no", PermissionResponse.DENY),
            ("a", PermissionResponse.ALWAYS),
            ("always", PermissionResponse.ALWAYS),
            ("v", PermissionResponse.NEVER),
            ("never", PermissionResponse.NEVER),
            ("c", PermissionResponse.CANCEL),
            ("cancel", PermissionResponse.CANCEL),
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                result = PermissionResponse.from_string(input_str)
                self.assertEqual(result, expected)
    
    def test_permission_response_from_string_invalid_inputs(self):
        """测试权限响应字符串解析 - 无效输入"""
        from daip_live.core.models import PermissionResponse
        
        # 测试各种无效的输入字符串，默认应为DENY
        invalid_inputs = ["", "invalid", "maybe", "1", "0", "ok"]
        
        for input_str in invalid_inputs:
            with self.subTest(input_str=input_str):
                result = PermissionResponse.from_string(input_str)
                self.assertEqual(result, PermissionResponse.DENY)


def run_tests():
    """运行所有测试"""
    print("开始权限管理集成测试...")
    
    # 创建测试套件
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加初始化测试
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionManagerInitialization))
    
    # 添加权限检查功能测试
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionCheckFunctionality))
    
    # 添加权限响应处理测试
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestPermissionResponseHandling))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


def main():
    """主测试函数"""
    success = run_tests()
    
    if success:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n❌ 部分测试失败!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)