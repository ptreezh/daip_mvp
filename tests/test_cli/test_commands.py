import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from src.daip_live.cli import app

runner = CliRunner()

# 测试个人助手命令
def test_pa_command():
    """测试个人助手命令"""
    # 红: 测试命令执行失败的情况
    with patch('src.daip_live.cli.run') as mock_run:
        mock_run.side_effect = Exception("执行错误")
        result = runner.invoke(app, ["pa", "测试任务"])
        assert result.exit_code != 0
        
    # 绿: 测试命令正常执行
    with patch('src.daip_live.cli.run') as mock_run:
        result = runner.invoke(app, ["pa", "测试任务"])
        assert result.exit_code == 0
        mock_run.assert_called_once_with(goal="测试任务")

# 测试角色列表命令
def test_role_list_command():
    """测试角色列表命令"""
    # 红: 测试无角色情况
    with patch('src.daip_live.p4_role_manager_tools.role_manager.RoleManager') as mock_role_manager:
        # 确保模拟对象有 _roles 属性
        mock_instance = MagicMock()
        mock_instance._roles = {}
        mock_role_manager.return_value = mock_instance
        result = runner.invoke(app, ["role", "list"])
        assert result.exit_code == 0
        assert "No roles found" in result.stdout
        
    # 绿: 测试有角色情况
    with patch('src.daip_live.p4_role_manager_tools.role_manager.RoleManager') as mock_role_manager:
        mock_role = MagicMock()
        mock_role.name = "test_role"
        mock_role.persona = "测试角色描述"
        mock_role.tools = []
        mock_instance = MagicMock()
        mock_instance._roles = {"test_role": mock_role}
        mock_role_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["role", "list"])
        assert result.exit_code == 0
        assert "test_role" in result.stdout

# 测试角色查看命令
def test_role_view_command():
    """测试角色查看命令"""
    # 红: 测试角色不存在情况
    with patch('src.daip_live.p4_role_manager_tools.role_manager.RoleManager') as mock_role_manager:
        mock_instance = MagicMock()
        mock_instance.get_role_by_name.return_value = None
        mock_role_manager.return_value = mock_instance
        result = runner.invoke(app, ["role", "view", "nonexistent"])
        assert result.exit_code == 1
        assert "Role 'nonexistent' not found" in result.stdout
        
    # 绿: 测试角色存在情况
    with patch('src.daip_live.p4_role_manager_tools.role_manager.RoleManager') as mock_role_manager:
        mock_role = MagicMock()
        mock_role.name = "test_role"
        mock_role.persona = "测试角色描述"
        mock_role.tools = ["tool1", "tool2"]
        mock_instance = MagicMock()
        mock_instance.get_role_by_name.return_value = mock_role
        mock_role_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["role", "view", "test_role"])
        assert result.exit_code == 0
        assert "test_role" in result.stdout
        assert "测试角色描述" in result.stdout

# 测试会话列表命令
def test_session_list_command():
    """测试会话列表命令"""
    # 红: 测试无会话情况
    with patch('src.daip_live.memory.session_manager.SessionManager') as mock_session_manager:
        mock_instance = MagicMock()
        mock_instance.list_sessions.return_value = []
        mock_session_manager.return_value = mock_instance
        result = runner.invoke(app, ["session", "list"])
        assert result.exit_code == 0
        assert "No sessions found" in result.stdout
        
    # 绿: 测试有会话情况
    with patch('src.daip_live.memory.session_manager.SessionManager') as mock_session_manager:
        mock_session = MagicMock()
        mock_session.session_id = "test_session_id"
        mock_session.goal = "测试目标"
        mock_session.session_type = "workflow"
        mock_session.status.name = "completed"
        mock_session.start_time = "2023-01-01 00:00:00"
        mock_instance = MagicMock()
        mock_instance.list_sessions.return_value = [mock_session]
        mock_session_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["session", "list"])
        assert result.exit_code == 0
        assert "test_session_id" in result.stdout

# 测试会话查看命令
def test_session_view_command():
    """测试会话查看命令"""
    # 红: 测试会话不存在情况
    with patch('src.daip_live.memory.session_manager.SessionManager') as mock_session_manager:
        mock_instance = MagicMock()
        mock_instance.get_session.return_value = None
        mock_session_manager.return_value = mock_instance
        result = runner.invoke(app, ["session", "view", "nonexistent"])
        assert result.exit_code == 1
        assert "Session with ID 'nonexistent' not found" in result.stdout
        
    # 绿: 测试会话存在情况
    with patch('src.daip_live.memory.session_manager.SessionManager') as mock_session_manager:
        mock_session = MagicMock()
        mock_session.session_id = "test_session_id"
        mock_session.goal = "测试目标"
        mock_session.session_type = "workflow"
        mock_session.status.name = "completed"
        mock_session.participant_ids = ["user", "agent"]
        mock_session.summary = "测试总结"
        mock_session.history = []
        mock_instance = MagicMock()
        mock_instance.get_session.return_value = mock_session
        mock_session_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["session", "view", "test_session_id"])
        assert result.exit_code == 0
        assert "test_session_id" in result.stdout
        assert "测试目标" in result.stdout

# 测试知识库同步命令
def test_knowledge_sync_command():
    """测试知识库同步命令"""
    # 绿: 测试同步命令执行
    with patch('src.daip_live.cli.config_manager') as mock_config_manager, \
         patch('src.daip_live.cli.DatabaseManager') as mock_db_manager, \
         patch('src.daip_live.cli.LiteLLMProvider') as mock_provider, \
         patch('src.daip_live.cli.KnowledgeManager') as mock_knowledge_manager:
        
        mock_config = MagicMock()
        mock_config.database.path = "test.db"
        mock_config.llm_provider.embedding_model = "test_model"
        mock_config.knowledge_base.directory = "test_dir"
        mock_config_manager.get_config.return_value = mock_config
        
        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        assert "Knowledge base sync started" in result.stdout