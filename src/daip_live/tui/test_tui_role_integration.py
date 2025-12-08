"""
TUI交互式AI角色创建功能的集成测试
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import asyncio

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI
from daip_live.tui.interactive_role_creation import InteractiveRoleCreationService
from daip_live.p4_role_manager_tools.role_manager import RoleManager


class MockModelProvider:
    """模拟模型提供者用于测试"""
    
    def generate(self, prompt):
        # 模拟AI响应，返回JSON格式的角色配置
        if "数据科学家" in prompt or "数据分析师" in prompt:
            return '''
            {
                "name": "数据分析专家",
                "persona": "专业的数据分析师，擅长数据处理、统计分析和可视化",
                "tools": ["pandas", "numpy", "matplotlib"]
            }
            '''
        else:
            return '''
            {
                "name": "自定义助手",
                "persona": "多用途AI助手，可根据需求调整功能",
                "tools": ["搜索", "计算", "分析"]
            }
            '''


class TestTUIInteractiveRoleCreationIntegration(unittest.TestCase):
    """TUI交互式角色创建集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟依赖
        self.mock_role_manager = RoleManager()
        self.mock_model_provider = MockModelProvider()
        
        # 创建TUI实例（模拟）
        self.tui = Mock(spec=SimplifiedTUI)
        self.tui._role_manager = self.mock_role_manager
        self.tui._update_log_view = Mock()
        self.tui._background_tasks = set()
        
        # 创建服务实例
        self.service = InteractiveRoleCreationService(
            role_manager=self.mock_role_manager,
            llm_model_provider=self.mock_model_provider
        )
    
    def test_complete_role_creation_flow(self):
        """测试完整的角色创建流程"""
        # 1. 开始创建角色
        user_query = "创建一个数据分析专家角色"
        response = self.service.start_creation(user_query)
        
        # 验证响应
        self.assertEqual(response.status, 'success')
        self.assertIsNotNone(response.suggested_role)
        self.assertIsNotNone(response.session_id)
        self.assertIn('name', response.suggested_role)
        self.assertIn('persona', response.suggested_role)
        self.assertIn('tools', response.suggested_role)
        
        # 2. 确认角色创建
        confirm_response = self.service.continue_creation(response.session_id, {"confirm": True})
        
        # 验证确认结果
        self.assertEqual(confirm_response.status, 'success')
        self.assertIn('已成功创建并保存', confirm_response.message)
    
    def test_role_creation_with_customization(self):
        """测试角色创建和自定义"""
        # 1. 开始创建角色
        user_query = "法律咨询助手"
        response = self.service.start_creation(user_query)
        
        self.assertEqual(response.status, 'success')
        original_name = response.suggested_role['name']
        
        # 2. 修改角色配置
        updated_role = {
            'name': '法律专家',
            'persona': '专业法律咨询师，擅长合同审查和法律风险评估',
            'tools': ['法律数据库访问', '合同分析', '法规查询']
        }
        
        modify_response = self.service.continue_creation(response.session_id, {
            'updated_role': updated_role
        })
        
        self.assertEqual(modify_response.status, 'success')
        self.assertEqual(modify_response.suggested_role['name'], '法律专家')
        
        # 3. 确认修改后的角色
        confirm_response = self.service.continue_creation(response.session_id, {"confirm": True})
        self.assertEqual(confirm_response.status, 'success')
    
    def test_invalid_session_handling(self):
        """测试无效会话处理"""
        response = self.service.continue_creation("invalid_session_id", {"confirm": True})
        
        self.assertEqual(response.status, 'error')
        self.assertIn('会话不存在', response.message)


class TestTUIIntegration(unittest.TestCase):
    """TUI集成测试"""
    
    def setUp(self):
        """设置TUI集成测试环境"""
        self.mock_role_manager = RoleManager()
        self.mock_model_provider = MockModelProvider()
    
    @patch('daip_live.tui.simplified_main.get_container')
    def test_tui_role_command_integration(self, mock_get_container):
        """测试TUI中的角色命令集成"""
        # 模拟容器
        mock_container = Mock()
        mock_container.model_provider.return_value = self.mock_model_provider
        mock_get_container.return_value = mock_container
        
        # 创建TUI实例并初始化
        tui = SimplifiedTUI()
        tui._role_manager = self.mock_role_manager
        tui._model_provider = self.mock_model_provider
        tui._background_tasks = set()
        tui.container = mock_container
        
        # 手动初始化角色创建服务
        tui._initialize_role_creation_service()
        
        # 验证服务已初始化
        self.assertIsNotNone(tui._role_creation_service)
        self.assertIsNotNone(tui._tui_role_handler)
        
        # 检查角色列表功能
        tui._update_log_view = Mock()
        tui._handle_role_command("list")
        
        # 验证日志视图被调用
        self.assertTrue(tui._update_log_view.called)


if __name__ == '__main__':
    unittest.main()