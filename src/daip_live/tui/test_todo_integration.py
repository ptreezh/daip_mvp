"""
测试todo功能与系统的正确集成
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI
from daip_live.memory.service import MemoryService


class MockModelProvider:
    """模拟模型提供者"""
    pass


class TestTodoSystemIntegration(unittest.TestCase):
    """测试todo功能的系统集成"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建Mock容器
        self.mock_container = Mock()
        self.mock_model_provider = MockModelProvider()
        self.mock_container.model_provider.return_value = self.mock_model_provider
        self.mock_container.session_manager.return_value = Mock()
        self.mock_container.role_manager.return_value = Mock()
        self.mock_container.role_model_manager.return_value = Mock()
        self.mock_container.agent_executor.return_value = Mock()
        self.mock_container.knowledge_manager.return_value = Mock()

    def test_memory_service_initialization(self):
        """测试memory_service初始化"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_state()
            
            # 验证memory_service被正确初始化
            self.assertIsNotNone(tui._memory_service)
            # memory_service应该有todo_list属性（无论是真实MemoryService还是SimpleMemoryService）
            self.assertTrue(hasattr(tui._memory_service, 'todo_list'))
    
    def test_todo_list_functionality(self):
        """测试todo列表功能"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_state()
            
            # 添加一些测试待办事项
            from daip_live.core.models import TodoItem
            
            # 添加测试任务
            test_todo1 = TodoItem(description="测试任务1", status="pending", priority=1)
            test_todo2 = TodoItem(description="测试任务2", status="pending", priority=2)
            
            tui._memory_service.add_todo_item(test_todo1)
            tui._memory_service.add_todo_item(test_todo2)
            
            # 验证任务被添加
            todo_list = tui._memory_service.todo_list
            self.assertEqual(len(todo_list), 2)
            self.assertEqual(todo_list[0].description, "测试任务1")
            self.assertEqual(todo_list[1].description, "测试任务2")
    
    def test_todo_command_integration(self):
        """测试todo命令与系统的集成"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_state()
            
            # 模拟命令处理的输出记录
            original_update = tui._update_log_view
            tui._update_log_view = Mock()
            
            # 测试添加任务
            tui._handle_todo_command("add 测试任务")
            
            # 验证任务已添加到memory_service
            self.assertEqual(len(tui._memory_service.todo_list), 1)
            self.assertEqual(tui._memory_service.todo_list[0].description, "测试任务")
            
            # 恢复原始方法
            tui._update_log_view = original_update


if __name__ == '__main__':
    unittest.main()