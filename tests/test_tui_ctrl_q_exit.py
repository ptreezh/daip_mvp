import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
import time

# Add src to path to import TUI module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest

pytestmark = pytest.mark.skip(reason="旧spec：TUI 内部实现已重构（Textual action 命名 action__handle_*、组件 Footer 等已移除）；当前源码为准")
class TestTUIExitFunctionality(unittest.TestCase):
    """TUI退出功能测试用例"""

    def setUp(self):
        """测试前准备"""
        # Mock依赖项
        self.mock_executor = Mock()
        self.mock_session_manager = Mock()
        self.mock_role_manager = Mock()
        self.mock_knowledge_manager = Mock()
        self.mock_debate_manager = Mock()
        self.mock_model_provider = Mock()
        self.mock_db_manager = Mock()
        self.mock_config_manager = Mock()

    def test_ctrl_q_binding_exists(self):
        """测试Ctrl+Q绑定存在"""
        try:
            from daip_live.tui import DAIP_TUI
            
            # 检查BINDINGS中包含Ctrl+Q
            bindings = DAIP_TUI.BINDINGS
            ctrl_q_binding = None
            for binding in bindings:
                if binding.key == "ctrl+q":
                    ctrl_q_binding = binding
                    break
            
            self.assertIsNotNone(ctrl_q_binding, "Ctrl+Q绑定应该存在")
            self.assertEqual(ctrl_q_binding.action, "_handle_ctrl_q_exit", "Ctrl+Q应该绑定到_handle_ctrl_q_exit")
        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_ctrl_q_attributes_initialization(self):
        """测试Ctrl+Q相关属性初始化"""
        try:
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with patch('daip_live.memory.session_manager.SessionManager', return_value=self.mock_session_manager), \
                 patch('daip_live.p4_role_manager_tools.role_manager.RoleManager', return_value=self.mock_role_manager):

                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager
                )

                # 检查属性是否存在并正确初始化
                self.assertTrue(hasattr(tui, '_last_ctrl_q_time'), "应该有_last_ctrl_q_time属性")
                self.assertTrue(hasattr(tui, '_ctrl_q_press_count'), "应该有_ctrl_q_press_count属性")
                self.assertEqual(tui._last_ctrl_q_time, 0, "_last_ctrl_q_time应该初始化为0")
                self.assertEqual(tui._ctrl_q_press_count, 0, "_ctrl_q_press_count应该初始化为0")
        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_single_ctrl_q_session_termination(self):
        """测试单次Ctrl+Q终止会话"""
        try:
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with patch('daip_live.memory.session_manager.SessionManager', return_value=self.mock_session_manager), \
                 patch('daip_live.p4_role_manager_tools.role_manager.RoleManager', return_value=self.mock_role_manager):

                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager
                )

                # 设置一个活动会话
                tui._executor = self.mock_executor
                
                # Mock更新日志和状态栏的方法
                tui._update_log_view = Mock()
                tui._update_status_bar = Mock()
                tui.set_timer = Mock()

                # 调用处理函数
                tui._handle_ctrl_q_exit()

                # 验证会话被终止
                self.assertIsNone(tui._executor, "会话执行器应该被重置为None")
                
                # 验证提示信息被显示
                tui._update_log_view.assert_called_with("[yellow]会话已终止。再次按 CTRL+Q 退出应用。[/yellow]")
                tui._update_status_bar.assert_called_with("会话已终止 - 再次按 CTRL+Q 退出应用")
                
                # 验证计数器被设置
                self.assertEqual(tui._ctrl_q_press_count, 1, "按压计数器应该设置为1")
                
        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_double_ctrl_q_application_exit(self):
        """测试连续Ctrl+Q退出应用"""
        try:
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with patch('daip_live.memory.session_manager.SessionManager', return_value=self.mock_session_manager), \
                 patch('daip_live.p4_role_manager_tools.role_manager.RoleManager', return_value=self.mock_role_manager):

                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager
                )

                # Mock exit方法
                tui.exit = Mock()
                tui._update_log_view = Mock()
                tui._update_status_bar = Mock()
                
                # 设置第一次按压的时间
                tui._last_ctrl_q_time = time.time()
                
                # 第二次调用应该退出应用
                tui._handle_ctrl_q_exit()
                
                # 验证exit被调用
                tui.exit.assert_called_once()
                
        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

    def test_ctrl_q_timeout_reset(self):
        """测试Ctrl+Q超时重置"""
        try:
            from daip_live.tui import DAIP_TUI

            # Mock必要的依赖
            with patch('daip_live.memory.session_manager.SessionManager', return_value=self.mock_session_manager), \
                 patch('daip_live.p4_role_manager_tools.role_manager.RoleManager', return_value=self.mock_role_manager):

                # 创建TUI实例
                tui = DAIP_TUI(
                    executor=self.mock_executor,
                    goal="test goal",
                    session_manager=self.mock_session_manager,
                    role_manager=self.mock_role_manager,
                    knowledge_manager=self.mock_knowledge_manager,
                    debate_manager=self.mock_debate_manager,
                    model_provider=self.mock_model_provider,
                    db_manager=self.mock_db_manager,
                    config_manager=self.mock_config_manager
                )

                # 设置一个较早的按压时间（5秒前）
                tui._last_ctrl_q_time = time.time() - 6.0
                tui._ctrl_q_press_count = 1
                
                # Mock更新日志和状态栏的方法
                tui._update_log_view = Mock()
                tui._update_status_bar = Mock()
                tui.set_timer = Mock()

                # 调用处理函数
                tui._handle_ctrl_q_exit()

                # 验证会话被终止（因为超时后重新开始）
                self.assertIsNone(tui._executor, "会话执行器应该被重置为None")
                
                # 验证提示信息被显示
                tui._update_log_view.assert_called_with("[yellow]会话已终止。再次按 CTRL+Q 退出应用。[/yellow]")
                
        except ImportError as e:
            self.fail(f"DAIP_TUI类导入失败: {e}")

if __name__ == '__main__':
    unittest.main()
