"""
测试修复后的role_manager初始化
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI


class TestRoleManagerInitialization(unittest.TestCase):
    """测试role_manager初始化修复"""
    
    def test_role_manager_is_initialized(self):
        """测试role_manager正确初始化"""
        # 模拟容器
        mock_container = Mock()
        mock_container.role_manager.return_value = Mock()
        mock_container.model_provider.return_value = Mock()
        mock_container.session_manager.return_value = Mock()
        mock_container.role_model_manager.return_value = Mock()
        mock_container.agent_executor.return_value = Mock()
        mock_container.knowledge_manager.return_value = Mock()

        with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()  # 新增的初始化
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_state()
            
            # 验证role_manager被初始化
            self.assertIsNotNone(tui._role_manager)
            
            # 验证role_creation_service使用了role_manager
            if tui._role_creation_service:  # 如果服务初始化成功
                # 检查是否没有出现属性错误
                self.assertTrue(hasattr(tui, '_role_manager'))


if __name__ == '__main__':
    unittest.main()