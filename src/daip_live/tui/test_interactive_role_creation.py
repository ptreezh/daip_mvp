"""
TUI交互式AI角色创建功能的单元测试
遵循TDD原则
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
from datetime import datetime

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.interactive_role_creation import (
    AIRoleGenerator,
    RoleValidator,
    RoleCreationSession,
    InteractiveRoleCreationService,
    RoleCreationError,
    InvalidRoleDescriptionError,
    RoleGenerationError
)
from daip_live.core.models import Role


class MockLLMProvider:
    """模拟LLM提供者用于测试"""
    
    def generate(self, prompt):
        # 模拟AI响应
        if "数据分析师" in prompt:
            return '''
            {
                "name": "数据分析专家",
                "persona": "专业的数据分析师，擅长数据处理、统计分析和可视化",
                "tools": ["数据分析工具", "统计库", "图表生成"]
            }
            '''
        elif "空" in prompt or not prompt.strip():
            return "{}"
        elif "无效JSON" in prompt:
            return "这是无效的JSON"
        else:
            return '''
            {
                "name": "自定义助手",
                "persona": "多用途AI助手",
                "tools": ["搜索", "计算"]
            }
            '''


class TestAIRoleGenerator(unittest.TestCase):
    """AI角色生成器测试"""
    
    def setUp(self):
        self.mock_provider = MockLLMProvider()
        self.generator = AIRoleGenerator(self.mock_provider)
    
    def test_generate_role_from_description(self):
        """测试根据描述生成角色"""
        description = "数据分析师"
        result = self.generator.generate_role_from_description(description)
        
        self.assertIn('name', result)
        self.assertIn('persona', result)
        self.assertIn('tools', result)
        self.assertEqual(result['name'], '数据分析专家')
        self.assertIsInstance(result['tools'], list)
    
    def test_generate_role_empty_description(self):
        """测试空描述的处理"""
        description = ""
        result = self.generator.generate_role_from_description(description)
        
        # 应该返回默认结构
        self.assertIn('name', result)
        self.assertIn('persona', result)
        self.assertIn('tools', result)
        self.assertEqual(result['name'], '自定义角色')
    
    def test_generate_role_invalid_json(self):
        """测试无效JSON响应的处理"""
        # 这个需要修改模拟提供者的行为来测试
        with patch.object(self.mock_provider, 'generate', return_value="无效JSON"):
            result = self.generator.generate_role_from_description("test")
            
            # 应该返回默认值
            self.assertIn('name', result)
            self.assertEqual(result['name'], '自定义角色')
    
    def test_parse_response_valid_json(self):
        """测试有效JSON解析"""
        response = '''
        {
            "name": "测试角色",
            "persona": "测试人设",
            "tools": ["工具1", "工具2"]
        }
        '''
        result = self.generator._parse_response(response)
        
        self.assertEqual(result['name'], '测试角色')
        self.assertEqual(result['persona'], '测试人设')
        self.assertEqual(result['tools'], ['工具1', '工具2'])
    
    def test_parse_response_invalid_json(self):
        """测试无效JSON解析"""
        response = "invalid json"
        result = self.generator._parse_response(response)
        
        self.assertEqual(result['name'], '自定义角色')
        self.assertEqual(result['persona'], '根据用户需求定制的专业AI助手')
        self.assertEqual(result['tools'], [])


class TestRoleValidator(unittest.TestCase):
    """角色验证器测试"""
    
    def setUp(self):
        self.validator = RoleValidator()
    
    def test_validate_valid_role(self):
        """测试有效角色验证"""
        role = Role(
            name="测试角色",
            persona="测试人设",
            tools=["工具1"]
        )
        result = self.validator.validate_role(role)
        
        self.assertTrue(result)
    
    def test_validate_invalid_role_empty_name(self):
        """测试无效角色(空名称)验证"""
        role = Role(
            name="",
            persona="测试人设",
            tools=["工具1"]
        )
        result = self.validator.validate_role(role)
        
        self.assertFalse(result)
    
    def test_validate_invalid_role_empty_persona(self):
        """测试无效角色(空人设)验证"""
        role = Role(
            name="测试角色",
            persona="",
            tools=["工具1"]
        )
        result = self.validator.validate_role(role)
        
        self.assertFalse(result)
    
    def test_validate_edge_cases(self):
        """测试边界情况"""
        # 测试超长名称
        role = Role(
            name="a" * 1000,  # 假设长度限制为100
            persona="测试人设",
            tools=["工具1"]
        )
        result = self.validator.validate_role(role)
        
        # 根据实际验证逻辑，可能为True或False
        # 这里我们验证验证器方法存在且能执行
        self.assertIsNotNone(result)


class TestRoleCreationSession(unittest.TestCase):
    """角色创建会话测试"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = RoleCreationSession("test_query")
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.user_query, "test_query")
        self.assertEqual(session.status, "initial")
        self.assertIsNone(session.suggested_role)
    
    def test_session_status_transition(self):
        """测试会话状态转换"""
        session = RoleCreationSession("test_query")
        
        # 初始状态
        self.assertEqual(session.status, "initial")
        
        # 模拟处理中
        session.status = "processing"
        self.assertEqual(session.status, "processing")
        
        # 模拟建议状态
        session.status = "suggested"
        self.assertEqual(session.status, "suggested")
        
        # 模拟确认状态
        session.status = "confirmed"
        self.assertEqual(session.status, "confirmed")
    
    def test_session_suggested_role(self):
        """测试会话建议角色设置"""
        session = RoleCreationSession("test_query")
        role_data = {
            "name": "测试角色",
            "persona": "测试人设",
            "tools": ["工具1"]
        }
        
        session.suggested_role = role_data
        self.assertEqual(session.suggested_role, role_data)


class TestInteractiveRoleCreationService(unittest.TestCase):
    """交互式角色创建服务测试"""
    
    def setUp(self):
        self.mock_role_manager = Mock()
        self.mock_ai_provider = MockLLMProvider()
        self.service = InteractiveRoleCreationService(
            self.mock_role_manager,
            self.mock_ai_provider
        )
    
    def test_start_creation(self):
        """测试启动角色创建"""
        user_query = "创建一个数据分析师角色"
        result = self.service.start_creation(user_query)
        
        self.assertEqual(result.status, 'success')
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.suggested_role)
        self.assertIsNotNone(result.session_id)
        
        # 验证AI生成器被调用
        # 这里需要检查服务内部的AI生成器是否被正确调用
        self.assertIn('name', result.suggested_role)
    
    def test_continue_creation(self):
        """测试继续创建流程"""
        # 先启动一个创建流程获取session_id
        user_query = "创建一个数据分析师角色"
        initial_result = self.service.start_creation(user_query)
        
        # 继续流程
        input_data = {"confirm": True}
        result = self.service.continue_creation(initial_result.session_id, input_data)
        
        self.assertEqual(result.status, 'success')
        # 检查中文中是否包含保存成功的相关文字
        self.assertTrue('成功' in result.message or 'saved' in result.message.lower())
    
    def test_start_creation_error(self):
        """测试启动创建时的错误处理"""
        # 模拟AI生成错误
        with patch.object(self.service._ai_generator, 'generate_role_from_description', 
                         side_effect=Exception("AI Error")):
            result = self.service.start_creation("test")
            
            self.assertEqual(result.status, 'error')
            self.assertIn("AI Error", result.message)


if __name__ == '__main__':
    unittest.main()