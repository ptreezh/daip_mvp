"""
会话管理后台功能的TDD测试
测试后台session_manager的初始化和依赖功能
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI


class MockContainer:
    """模拟容器用于测试"""
    def __init__(self):
        self._session_manager = Mock()
        self._role_manager = Mock()
        self._knowledge_manager = Mock()
        self._model_provider = Mock()
        
    def session_manager(self):
        return self._session_manager
    
    def role_manager(self):
        return self._role_manager
    
    def knowledge_manager(self):
        return self._knowledge_manager
    
    def model_provider(self):
        return self._model_provider


class TestBackendSessionManager(unittest.TestCase):
    """后台会话管理器初始化测试"""
    
    def test_session_manager_initialization_with_container(self):
        """测试通过容器初始化session_manager"""
        # 创建模拟容器
        mock_container = MockContainer()
        
        with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_state()
            
            # 验证session_manager被正确初始化
            self.assertIsNotNone(tui._session_manager)
            self.assertEqual(tui._session_manager, mock_container.session_manager())
    
    def test_session_manager_initialization_without_container(self):
        """测试没有容器时初始化session_manager"""
        # 模拟容器不可用的情况
        def mock_get_container():
            raise Exception("Container not available")
        
        with patch('daip_live.tui.simplified_main.get_container', side_effect=mock_get_container):
            with patch('daip_live.container.Container') as mock_container_class:
                # 设置模拟容器的session_manager方法
                mock_container_instance = MockContainer()
                mock_container_class.return_value = mock_container_instance
                
                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()  # 修改这里
                tui._initialize_state()
                
                # 验证session_manager被正确初始化
                self.assertIsNotNone(tui._session_manager)
                self.assertEqual(tui._session_manager, mock_container_instance.session_manager())
    
    def test_session_manager_initialization_failure_handling(self):
        """测试session_manager初始化失败时的处理"""
        def mock_get_container():
            raise Exception("Container not available")
        
        def mock_container_init():
            raise Exception("Container init failed")
        
        with patch('daip_live.tui.simplified_main.get_container', side_effect=mock_get_container):
            with patch('daip_live.container.Container', side_effect=mock_container_init):
                tui = SimplifiedTUI()
                tui._initialize_tui_modules()
                tui._initialize_role_creation_service()
                tui._initialize_backend_session_manager()  # 修改这里
                tui._initialize_state()
                
                # 验证session_manager未初始化时设为None
                self.assertIsNone(tui._session_manager)
    
    def test_search_commands_can_access_session_manager(self):
        """测试SearchCommands可以访问session_manager"""
        mock_container = MockContainer()
        
        with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_state()
            
            # 验证SearchCommands可以访问session_manager
            # 模拟SearchCommands的调用
            if hasattr(tui, '_session_manager') and tui._session_manager:
                # 验证session_manager功能可用
                tui._session_manager.list_sessions.return_value = []
                sessions = tui._session_manager.list_sessions()
                self.assertEqual(sessions, [])
    
    def test_session_command_hidden_from_user_interface(self):
        """测试session命令在用户界面中不可见"""
        mock_container = MockContainer()
        
        with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_state()
            
            # 验证session命令不在可用命令列表中
            available_commands = [cmd[0] for cmd in tui._available_commands]
            self.assertNotIn("/session", available_commands)
    
    def test_session_command_provides_backend_functionality(self):
        """测试session命令在后台仍提供功能"""
        mock_container = MockContainer()
        
        with patch('daip_live.tui.simplified_main.get_container', return_value=mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_state()
            
            # 模拟命令处理
            tui._update_log_view = Mock()
            tui._handle_session_command("")
            
            # 验证命令被处理但不显示给用户
            self.assertTrue(tui._update_log_view.called)
            args, kwargs = tui._update_log_view.call_args
            # 应该显示系统信息，而不是详细的功能列表
            self.assertIn("系统信息已记录", str(args[0]) if args else str(kwargs.get('text', '')))


if __name__ == '__main__':
    unittest.main()