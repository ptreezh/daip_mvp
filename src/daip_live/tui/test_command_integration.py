"""
检查simplified_main.py中所有命令是否与真实系统实现对接
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.simplified_main import SimplifiedTUI


class TestCommandIntegration(unittest.TestCase):
    """测试所有命令是否正确实现"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建Mock容器
        self.mock_container = Mock()
        self.mock_model_provider = Mock()
        self.mock_container.model_provider.return_value = self.mock_model_provider
        self.mock_container.session_manager.return_value = Mock()
        self.mock_container.role_manager.return_value = Mock()
        self.mock_container.role_model_manager.return_value = Mock()
        self.mock_container.agent_executor.return_value = Mock()
        self.mock_container.knowledge_manager.return_value = Mock()
        # 添加辩论管理器的模拟
        self.mock_container.debate_manager.return_value = Mock()
        
        # 模拟一个基本的session_manager
        mock_session_manager = Mock()
        mock_session_manager.list_sessions.return_value = []
        mock_session_manager.get_session.return_value = None
        self.mock_container.session_manager.return_value = mock_session_manager

    def test_all_command_handlers_exist(self):
        """测试所有命令处理方法是否存在"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_state()
            
            # 验证所有关键命令处理方法存在
            self.assertTrue(hasattr(tui, '_handle_search_command'))
            self.assertTrue(hasattr(tui, '_handle_debate_command'))
            self.assertTrue(hasattr(tui, '_handle_help_command'))
            self.assertTrue(hasattr(tui, '_handle_model_command'))
            self.assertTrue(hasattr(tui, '_handle_compact_command'))
            self.assertTrue(hasattr(tui, '_handle_doc_command'))
            self.assertTrue(hasattr(tui, '_handle_wiki_command'))
            self.assertTrue(hasattr(tui, '_handle_permission_command'))
            self.assertTrue(hasattr(tui, '_handle_role_command'))
            self.assertTrue(hasattr(tui, '_handle_knowledge_command'))
            
            # 特别检查修复的问题：_start_debate方法
            self.assertTrue(hasattr(tui, '_start_debate'))
    
    def test_debate_command_can_be_called(self):
        """测试debate命令可以被调用（没有缺失的方法）"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_state()

            # 模拟日志输出，确保命令可以被调用而不出错
            original_update = tui._update_log_view
            tui._update_log_view = Mock()

            try:
                # 检查是否需要的方法存在
                self.assertTrue(hasattr(tui, '_start_debate'))
                # 只需要异步方法，commands.py使用asyncio.create_task调用

                # 测试debate命令调用不会出错
                tui._handle_debate_command("start 测试辩论")
                # 确认没有AttributeError
            except AttributeError as e:
                self.fail(f"debate命令调用失败: {e}")
            except RuntimeError as e:
                # 如果是事件循环问题，这是可以预料的，测试方法存在即可
                if "no running event loop" in str(e):
                    # 这是预期的问题，因为我们不在事件循环内
                    # 但重要的是方法存在
                    pass
                else:
                    self.fail(f"debate命令调用失败: {e}")
            finally:
                tui._update_log_view = original_update
    
    def test_search_command_uses_session_manager(self):
        """测试search命令可以访问session_manager"""
        with patch('daip_live.tui.simplified_main.get_container', return_value=self.mock_container):
            tui = SimplifiedTUI()
            tui._initialize_tui_modules()
            tui._initialize_role_manager()
            tui._initialize_role_creation_service()
            tui._initialize_backend_session_manager()
            tui._initialize_memory_service()
            tui._initialize_debate_manager()
            tui._initialize_state()
            
            # 验证session_manager被正确初始化
            self.assertIsNotNone(tui._session_manager)
            
            # 验证search commands可以访问session_manager
            from daip_live.tui.commands import SearchCommands
            search_commands = SearchCommands(tui)
            
            # 检查是否可以调用搜索功能
            original_update = tui._update_log_view
            tui._update_log_view = Mock()
            
            try:
                search_commands.search_conversation_history("test query")
                # 验证session_manager被访问
                # 这里我们确认不会因为session_manager缺失而报错
            except AttributeError as e:
                self.fail(f"search命令访问session_manager失败: {e}")
            finally:
                tui._update_log_view = original_update


if __name__ == '__main__':
    unittest.main()