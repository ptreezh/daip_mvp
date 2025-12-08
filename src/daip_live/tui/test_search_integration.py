"""
测试SearchCommands与后台session_manager的集成
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.tui.commands import SearchCommands


class TestSearchCommandsIntegration(unittest.TestCase):
    """测试SearchCommands与后台session_manager的集成"""
    
    def test_search_commands_can_access_session_manager(self):
        """测试SearchCommands可以访问tui的session_manager"""
        # 创建模拟TUI实例
        mock_tui = Mock()
        mock_tui._session_manager = Mock()
        mock_tui._session_manager.list_sessions.return_value = []
        mock_tui._update_log_view = Mock()
        
        # 创建SearchCommands实例
        search_commands = SearchCommands(mock_tui)
        
        # 调用搜索功能
        search_commands.search_conversation_history("test query")
        
        # 验证session_manager被访问
        mock_tui._session_manager.list_sessions.assert_called_once()
    
    def test_search_commands_handles_missing_session_manager(self):
        """测试SearchCommands处理缺失session_manager的情况"""
        # 创建模拟TUI实例，但没有session_manager
        mock_tui = Mock()
        # 确保没有_session_manager属性
        type(mock_tui).hasattr = Mock(return_value=False)
        mock_tui._update_log_view = Mock()

        # 直接设置session_manager为None
        mock_tui._session_manager = None

        # 创建SearchCommands实例
        search_commands = SearchCommands(mock_tui)

        # 调用搜索功能
        search_commands.search_conversation_history("test query")

        # 验证没有报错，而是给出了提示信息
        # 应该调用了_update_log_view，但没有访问session_manager
        self.assertTrue(mock_tui._update_log_view.called)


if __name__ == '__main__':
    unittest.main()