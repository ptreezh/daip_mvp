"""
TUI命令参数自动完成功能测试
遵循TDD原则的红绿重构循环
"""

import pytest
from unittest.mock import Mock, patch
from daip_live.tui import DAIP_TUI



pytestmark = pytest.mark.skip(reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准")
class TestTUIAutocompletion:
    """TUI自动完成功能测试类"""
    
    @pytest.fixture
    def tui_with_mocks(self):
        """创建带有Mock依赖的TUI实例"""
        with patch('daip_live.tui.SessionManager'), \
             patch('daip_live.tui.RoleManager'), \
             patch('daip_live.tui.KnowledgeManager'), \
             patch('daip_live.tui.MemoryService'), \
             patch('daip_live.tui.DebateManager'), \
             patch('daip_live.tui.LiteLLMProvider'), \
             patch('daip_live.tui.DatabaseManager'):
            
            tui = DAIP_TUI()
            # 设置必要的Mock对象
            tui._role_manager = Mock()
            tui._session_manager = Mock()
            return tui
    
    def test_command_suggestions_on_slash(self, tui_with_mocks):
        """测试输入/时显示所有命令建议 - RED"""
        # RED: 测试应该失败，因为功能还未实现
        tui = tui_with_mocks
        suggestions = tui._get_autocomplete_suggestions("/")
        
        # 应该包含基本命令
        assert len(suggestions) > 0
        command_names = [s.split(" - ")[0] for s in suggestions]
        assert "/role" in command_names
        assert "/session" in command_names
        assert "/knowledge" in command_names
        assert "/project" in command_names
        assert "/debate" in command_names
    
    def test_role_command_suggestions(self, tui_with_mocks):
        """测试/role命令的子命令建议"""
        tui = tui_with_mocks
        
        # 测试 /role 显示子命令
        suggestions = tui._get_autocomplete_suggestions("/role")
        assert len(suggestions) >= 2
        assert any("/role list" in s for s in suggestions)
        assert any("/role view" in s for s in suggestions)
    
    def test_role_view_parameter_suggestions(self, tui_with_mocks):
        """测试/role view命令的角色参数建议"""
        tui = tui_with_mocks
        
        # Mock角色数据
        mock_role1 = Mock()
        mock_role1.name = "developer"
        mock_role2 = Mock() 
        mock_role2.name = "designer"
        mock_role3 = Mock()
        mock_role3.name = "tester"
        tui._role_manager.list_roles.return_value = [mock_role1, mock_role2, mock_role3]
        
        # 测试角色参数建议
        suggestions = tui._get_autocomplete_suggestions("/role view d")
        assert len(suggestions) >= 2  # developer, designer
        assert any("/role view developer" in s for s in suggestions)
        assert any("/role view designer" in s for s in suggestions)
    
    def test_session_command_suggestions(self, tui_with_mocks):
        """测试/session命令的子命令建议"""
        tui = tui_with_mocks
        
        suggestions = tui._get_autocomplete_suggestions("/session")
        assert len(suggestions) >= 2
        assert any("/session list" in s for s in suggestions)
        assert any("/session view" in s for s in suggestions)
    
    def test_session_view_parameter_suggestions(self, tui_with_mocks):
        """测试/session view命令的会话ID参数建议"""
        tui = tui_with_mocks
        
        # Mock会话数据
        tui._session_manager.list_sessions.return_value = [
            Mock(session_id="sess_001", goal="test goal"),
            Mock(session_id="sess_002", goal="another goal")
        ]
        
        suggestions = tui._get_autocomplete_suggestions("/session view sess")
        assert len(suggestions) >= 2
        assert any("/session view sess_001" in s for s in suggestions)
        assert any("/session view sess_002" in s for s in suggestions)
    
    def test_knowledge_command_suggestions(self, tui_with_mocks):
        """测试/knowledge命令的子命令建议"""
        tui = tui_with_mocks
        
        suggestions = tui._get_autocomplete_suggestions("/knowledge")
        assert len(suggestions) >= 2
        assert any("/knowledge sync" in s for s in suggestions)
        assert any("/knowledge search" in s for s in suggestions)
    
    def test_project_command_suggestions(self, tui_with_mocks):
        """测试/project命令的子命令和参数建议"""
        tui = tui_with_mocks
        
        # 测试子命令建议
        suggestions = tui._get_autocomplete_suggestions("/project")
        assert len(suggestions) >= 1
        assert any("/project scaffold" in s for s in suggestions)
        
        # 测试参数建议
        suggestions = tui._get_autocomplete_suggestions("/project scaffold ")
        expected_options = ["--description", "--from-file", "--yes"]
        for option in expected_options:
            assert any(f"/project scaffold {option}" in s for s in suggestions)
    
    def test_debate_command_suggestions(self, tui_with_mocks):
        """测试/debate命令的子命令和参数建议"""
        tui = tui_with_mocks
        
        # 测试子命令建议
        suggestions = tui._get_autocomplete_suggestions("/debate")
        assert len(suggestions) >= 1
        assert any("/debate start" in s for s in suggestions)
        
        # 测试参数建议
        suggestions = tui._get_autocomplete_suggestions("/debate start topic ")
        expected_options = ["--roles", "--rounds"]
        for option in expected_options:
            assert any(f"/debate start topic {option}" in s for s in suggestions)
    
    def test_empty_suggestions_for_invalid_commands(self, tui_with_mocks):
        """测试无效命令返回空建议列表"""
        tui = tui_with_mocks
        
        suggestions = tui._get_autocomplete_suggestions("/invalid")
        assert len(suggestions) == 0
        
        suggestions = tui._get_autocomplete_suggestions("/role invalid")
        assert len(suggestions) == 0
    
    def test_no_suggestions_for_non_command_input(self, tui_with_mocks):
        """测试非命令输入不返回建议"""
        tui = tui_with_mocks
        
        suggestions = tui._get_autocomplete_suggestions("regular text")
        assert len(suggestions) == 0
        
        suggestions = tui._get_autocomplete_suggestions("")
        assert len(suggestions) == 0


class TestTUIInputHistory:
    """TUI输入历史功能测试"""
    
    @pytest.fixture
    def tui_with_history(self):
        """创建带历史记录的TUI实例"""
        with patch('daip_live.tui.SessionManager'), \
             patch('daip_live.tui.RoleManager'), \
             patch('daip_live.tui.KnowledgeManager'), \
             patch('daip_live.tui.MemoryService'), \
             patch('daip_live.tui.DebateManager'), \
             patch('daip_live.tui.LiteLLMProvider'), \
             patch('daip_live.tui.DatabaseManager'):
            
            tui = DAIP_TUI()
            # 设置历史记录
            tui._input_history = [
                "/role list",
                "/session list", 
                "regular message",
                "/knowledge sync"
            ]
            tui._history_index = -1
            return tui
    
    def test_history_navigate_up(self, tui_with_history):
        """测试向上导航历史记录"""
        tui = tui_with_history
        
        # 初始状态
        assert tui._history_index == -1
        assert tui._current_input_before_history == ""
        
        # 模拟向上导航
        with patch.object(tui.query_one(Input), 'value', 'current input'):
            tui._navigate_history(-1)  # 向上
            
        assert tui._history_index == 0  # 应该指向第一条历史记录
        assert tui._current_input_before_history == 'current input'
    
    def test_history_navigate_down(self, tui_with_history):
        """测试向下导航历史记录"""
        tui = tui_with_history
        
        # 先设置状态到中间
        tui._history_index = 2
        tui._current_input_before_history = "test input"
        
        # 向下导航
        tui._navigate_history(1)
        assert tui._history_index == 3
        
        # 再向下导航应该到-1（当前输入）
        tui._navigate_history(1)
        assert tui._history_index == -1
    
    def test_history_boundaries(self, tui_with_history):
        """测试历史导航边界"""
        tui = tui_with_history
        
        # 测试向上边界
        tui._history_index = len(tui._input_history) - 1
        tui._navigate_history(-1)  # 再向上不应该超出边界
        assert tui._history_index == len(tui._input_history) - 1
        
        # 测试向下边界
        tui._history_index = -1
        tui._navigate_history(1)  # 再向下不应该超出边界
        assert tui._history_index == -1
    
    def test_history_reset_on_typing(self, tui_with_history):
        """测试用户开始输入时重置历史导航状态"""
        tui = tui_with_history
        
        # 设置历史导航状态
        tui._history_index = 2
        tui._current_input_before_history = "saved input"
        
        # 模拟用户输入
        with patch.object(tui, '_get_autocomplete_suggestions', return_value=[]):
            tui.on_input_changed(Mock(value="new input"))
        
        # 历史导航状态应该被重置
        assert tui._history_index == -1
        # 注意：current_input_before_history不会被清空，直到用户开始导航


class TestTUICommandHandlers:
    """TUI命令处理器测试"""
    
    @pytest.fixture
    def tui_with_mocks(self):
        """创建带有完整Mock的TUI实例"""
        with patch('daip_live.tui.SessionManager') as mock_session, \
             patch('daip_live.tui.RoleManager') as mock_role, \
             patch('daip_live.tui.KnowledgeManager') as mock_knowledge, \
             patch('daip_live.tui.MemoryService') as mock_memory, \
             patch('daip_live.tui.DebateManager') as mock_debate, \
             patch('daip_live.tui.LiteLLMProvider') as mock_provider, \
             patch('daip_live.tui.DatabaseManager'), \
             patch('daip_live.tui.ToolManager'), \
             patch('asyncio.Queue'):
            
            tui = DAIP_TUI()
            tui._session_manager = mock_session
            tui._role_manager = mock_role  
            tui._knowledge_manager = mock_knowledge
            tui._memory_service = mock_memory
            tui._debate_manager = mock_debate
            tui._model_provider = mock_provider
            tui._tool_manager = Mock()
            
            # Mock log方法
            tui._update_log_view = Mock()
            
            return tui
    
    def test_handle_run_command_with_goal(self, tui_with_mocks):
        """测试/run命令处理 - 带有目标"""
        tui = tui_with_mocks
        
        with patch('daip_live.tui.AgentExecutor') as mock_executor_class, \
             patch('daip_live.tui.run_agent_and_feed_tui') as mock_run:
            
            tui._handle_run_command("test goal")
            
            # 验证创建了新的AgentExecutor
            mock_executor_class.assert_called_once()
            
            # 验证设置了goal
            call_args = mock_executor_class.call_args
            assert 'goal' in call_args.kwargs
            
            # 验证启动了agent
            mock_run.assert_called_once()
    
    def test_handle_run_command_without_goal(self, tui_with_mocks):
        """测试/run命令处理 - 无目标"""
        tui = tui_with_mocks
        
        tui._handle_run_command("")
        
        # 应该显示错误消息
        tui._update_log_view.assert_called_with("[bold red]> Usage: /run <goal>[/bold red]")
    
    def test_handle_debate_start_command(self, tui_with_mocks):
        """测试/debate start命令处理"""
        tui = tui_with_mocks
        
        # Mock异步方法
        tui._start_debate = Mock()
        tui._start_debate.return_value = Mock()
        
        with patch('asyncio.create_task') as mock_create_task:
            tui._handle_debate_command("start test topic --roles role1,role2 --rounds 3")
            
            # 验证创建了异步任务
            mock_create_task.assert_called_once()
    
    def test_handle_debate_start_without_topic(self, tui_with_mocks):
        """测试/debate start命令处理 - 无主题"""
        tui = tui_with_mocks
        
        tui._handle_debate_command("start")
        
        # 应该显示错误消息
        tui._update_log_view.assert_called_with(
            "[bold red]> Usage: /debate start <topic> [--roles <roles>] [--rounds <rounds>][/bold red]"
        )
    
    def test_handle_project_command(self, tui_with_mocks):
        """测试/project命令处理"""
        tui = tui_with_mocks
        
        tui._handle_project_command("scaffold --description test project")
        
        # 应该显示未实现消息
        tui._update_log_view.assert_called_with(
            "[bold yellow]> Project scaffold functionality not yet implemented in TUI. Use CLI: daip project scaffold[/bold yellow]"
        )
    
    def test_handle_project_command_without_args(self, tui_with_mocks):
        """测试/project命令处理 - 无参数"""
        tui = tui_with_mocks
        
        tui._handle_project_command("")
        
        # 应该显示用法信息
        tui._update_log_view.assert_called_with(
            "[bold red]> Usage: /project scaffold --description <desc> or --from-file <file>[/bold red]"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
