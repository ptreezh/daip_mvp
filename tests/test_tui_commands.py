import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daip_live.tui import DAIP_TUI


class TestTUICommandHandlers(unittest.TestCase):
    """Test cases for TUI shortcut command handlers."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the executor and other dependencies
        self.mock_executor = Mock()
        self.mock_session_manager = Mock()
        self.mock_role_manager = Mock()

        # Create TUI instance
        self.tui = DAIP_TUI(self.mock_executor, "test goal")

        # Replace the internal session manager and role manager with our mocks
        self.tui._session_manager = self.mock_session_manager
        self.tui._role_manager = self.mock_role_manager

        # Mock the log view
        from textual.widgets import Static
        self.mock_log_view = Mock(spec=Static)
        self.mock_log_view.text = ""

        # Mock query_one to return our mock log view
        self.tui.query_one = Mock(return_value=self.mock_log_view)

        # Ensure all session manager methods are properly mocked
        self.mock_session_manager.create_session = Mock()
        self.mock_session_manager.list_sessions = Mock()
        self.mock_session_manager.get_session = Mock()
        self.mock_session_manager.save_session = Mock()

    def test_handle_pa_command_with_args(self):
        """Test /pa command with arguments."""
        # Mock session creation
        mock_session = Mock()
        mock_session.session_id = "test-session-id"
        self.mock_session_manager.create_session.return_value = mock_session

        # Test the command handler
        self.tui._handle_pa_command("write a project plan", "", self.mock_log_view)

        # Verify session manager was called correctly
        self.mock_session_manager.create_session.assert_called_once_with(
            goal="write a project plan",
            session_type="chat",
            participant_ids=["user", "pa"]
        )

        # Verify log output
        self.assertIn("Personal Assistant executing: write a project plan",
                      self.mock_log_view.text)
        self.assertIn("Personal Assistant session started with ID: test-session-id",
                      self.mock_log_view.text)

    def test_handle_pa_command_without_args(self):
        """Test /pa command without arguments."""
        self.tui._handle_pa_command("", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Personal Assistant command requires a goal argument",
                      self.mock_log_view.text)

    def test_handle_role_add_command_with_args(self):
        """Test /role add command with arguments."""
        # Ensure role doesn't exist
        self.mock_role_manager.get_role_by_name.return_value = None
        self.mock_role_manager._roles = {}

        # Mock the file save operation
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', create=True), \
             patch('yaml.dump'):
            self.tui._handle_role_add_command("项目经理 负责项目管理的专业人员", "", self.mock_log_view)

        # Verify success message
        self.assertIn("Role '项目经理' created successfully", self.mock_log_view.text)

    def test_handle_role_add_command_without_args(self):
        """Test /role add command without arguments."""
        self.tui._handle_role_add_command("", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Role add command requires a name and persona",
                      self.mock_log_view.text)

    def test_handle_role_add_command_role_already_exists(self):
        """Test /role add command when role already exists."""
        # Mock existing role
        mock_role = Mock()
        mock_role.name = "项目经理"
        self.mock_role_manager.get_role_by_name.return_value = mock_role

        self.tui._handle_role_add_command("项目经理 负责项目管理的专业人员", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Role '项目经理' already exists", self.mock_log_view.text)

    def test_handle_role_view_command_with_existing_role(self):
        """Test /role view command with existing role."""
        # Mock role
        mock_role = Mock()
        mock_role.name = "项目经理"
        mock_role.persona = "负责项目管理的专业人员"
        mock_role.tools = ["read_file", "write_file"]

        self.mock_role_manager.get_role_by_name.return_value = mock_role

        self.tui._handle_role_view_command("项目经理", "", self.mock_log_view)

        # Verify role details are displayed
        self.assertIn("Role: 项目经理", self.mock_log_view.text)
        self.assertIn("Persona: 负责项目管理的专业人员", self.mock_log_view.text)
        self.assertIn("Tools: read_file, write_file", self.mock_log_view.text)

    def test_handle_role_view_command_with_nonexistent_role(self):
        """Test /role view command with nonexistent role."""
        self.mock_role_manager.get_role_by_name.return_value = None

        self.tui._handle_role_view_command("不存在的角色", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Role '不存在的角色' not found",
                      self.mock_log_view.text)

    def test_handle_role_view_command_without_args(self):
        """Test /role view command without arguments."""
        self.tui._handle_role_view_command("", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Role view command requires a role name",
                      self.mock_log_view.text)

    def test_handle_role_list_command_with_roles(self):
        """Test /role list command with existing roles."""
        # Mock roles
        mock_role1 = Mock()
        mock_role1.name = "项目经理"
        mock_role1.persona = "负责项目管理的专业人员，需要处理各种项目相关事务"

        mock_role2 = Mock()
        mock_role2.name = "开发人员"
        mock_role2.persona = "负责软件开发工作"

        self.mock_role_manager._roles = {
            "项目经理": mock_role1,
            "开发人员": mock_role2
        }

        self.tui._handle_role_list_command("", self.mock_log_view)

        # Verify roles are listed
        self.assertIn("Available Roles:", self.mock_log_view.text)
        self.assertIn("项目经理: 负责项目管理的专业人员，需要处理各种项目相关事务", self.mock_log_view.text)
        self.assertIn("开发人员: 负责软件开发工作", self.mock_log_view.text)

    def test_handle_role_list_command_without_roles(self):
        """Test /role list command without roles."""
        self.mock_role_manager._roles = {}

        self.tui._handle_role_list_command("", self.mock_log_view)

        # Verify no roles message
        self.assertIn("No roles found", self.mock_log_view.text)

    def test_handle_knowledge_command_with_args(self):
        """Test /0 command with arguments."""
        self.tui._handle_knowledge_command("项目管理方法", "", self.mock_log_view)

        # Verify search message
        self.assertIn("Searching knowledge base for: 项目管理方法", self.mock_log_view.text)
        self.assertIn("Search results would appear here", self.mock_log_view.text)

    def test_handle_knowledge_command_without_args(self):
        """Test /0 command without arguments."""
        self.tui._handle_knowledge_command("", "", self.mock_log_view)

        # Verify sync message
        self.assertIn("Syncing knowledge base...", self.mock_log_view.text)
        self.assertIn("Knowledge base sync completed", self.mock_log_view.text)

    def test_handle_debate_command_with_args(self):
        """Test /debate command with arguments."""
        # Mock session creation
        mock_session = Mock()
        mock_session.session_id = "debate-session-id"
        self.mock_session_manager.create_session.return_value = mock_session

        self.tui._handle_debate_command("远程办公的优缺点", "", self.mock_log_view)

        # Verify session creation
        self.mock_session_manager.create_session.assert_called_once_with(
            goal="远程办公的优缺点",
            session_type="debate",
            participant_ids=["pro_arguer", "con_arguer", "neutral_observer"]
        )

        # Verify output messages
        self.assertIn("Starting debate on: 远程办公的优缺点", self.mock_log_view.text)
        self.assertIn("Debate session started with ID: debate-session-id", self.mock_log_view.text)
        self.assertIn("Debate participants: pro_arguer, con_arguer, neutral_observer", self.mock_log_view.text)

    def test_handle_debate_command_without_args(self):
        """Test /debate command without arguments."""
        self.tui._handle_debate_command("", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Debate command requires a topic argument",
                      self.mock_log_view.text)

    def test_handle_session_search_command_with_args(self):
        """Test /v command with arguments."""
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.session_id = "session-1"
        mock_session1.goal = "项目计划"
        mock_session1.status.name = "COMPLETED"

        mock_session2 = Mock()
        mock_session2.session_id = "session-2"
        mock_session2.goal = "需求分析"
        mock_session2.status.name = "RUNNING"

        self.mock_session_manager.list_sessions.return_value = [mock_session1, mock_session2]

        self.tui._handle_session_search_command("项目", "", self.mock_log_view)

        # Verify search results
        self.assertIn("Searching sessions for: 项目", self.mock_log_view.text)
        self.assertIn("Found 1 matching sessions:", self.mock_log_view.text)
        self.assertIn("session-1 - 项目计划 (COMPLETED)", self.mock_log_view.text)

    def test_handle_session_search_command_without_args(self):
        """Test /v command without arguments."""
        # This should call _handle_session_list_command
        with patch.object(self.tui, '_handle_session_list_command') as mock_list:
            self.tui._handle_session_search_command("", "", self.mock_log_view)
            mock_list.assert_called_once_with("", self.mock_log_view)

    def test_handle_session_list_command_with_sessions(self):
        """Test /l command with sessions."""
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.session_id = "session-1"
        mock_session1.goal = "项目计划"
        mock_session1.status.name = "COMPLETED"

        mock_session2 = Mock()
        mock_session2.session_id = "session-2"
        mock_session2.goal = "需求分析"
        mock_session2.status.name = "RUNNING"

        self.mock_session_manager.list_sessions.return_value = [mock_session1, mock_session2]

        self.tui._handle_session_list_command("", self.mock_log_view)

        # Verify session list
        self.assertIn("Session History:", self.mock_log_view.text)
        self.assertIn("1. session-1 - 项目计划 (COMPLETED)", self.mock_log_view.text)
        self.assertIn("2. session-2 - 需求分析 (RUNNING)", self.mock_log_view.text)

    def test_handle_session_list_command_without_sessions(self):
        """Test /l command without sessions."""
        self.mock_session_manager.list_sessions.return_value = []

        self.tui._handle_session_list_command("", self.mock_log_view)

        # Verify no sessions message
        self.assertIn("No sessions found", self.mock_log_view.text)

    def test_handle_session_abort_command_with_active_session(self):
        """Test /c command with active session."""
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "active-session"
        mock_session.status = Mock()
        mock_session.status.name = "FAILED"
        self.mock_session_manager.get_session.return_value = mock_session
        self.tui._current_session_id = "active-session"

        self.tui._handle_session_abort_command("", self.mock_log_view)

        # Verify session aborted
        self.assertEqual(mock_session.status.name, "FAILED")
        self.mock_session_manager.save_session.assert_called_once_with(mock_session)
        self.assertIn("Session active-session aborted", self.mock_log_view.text)

    def test_handle_session_abort_command_without_active_session(self):
        """Test /c command without active session."""
        self.tui._current_session_id = None

        self.tui._handle_session_abort_command("", self.mock_log_view)

        # Verify no session message
        self.assertIn("No active session to abort", self.mock_log_view.text)

    def test_handle_session_continue_command_with_active_session(self):
        """Test /g command with active session."""
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "active-session"
        mock_session.goal = "项目计划"
        mock_session.status.name = "RUNNING"
        self.mock_session_manager.get_session.return_value = mock_session
        self.tui._current_session_id = "active-session"

        self.tui._handle_session_continue_command("", self.mock_log_view)

        # Verify session details
        self.assertIn("Continuing session active-session", self.mock_log_view.text)
        self.assertIn("Goal: 项目计划", self.mock_log_view.text)
        self.assertIn("Status: RUNNING", self.mock_log_view.text)

    def test_handle_session_continue_command_without_active_session(self):
        """Test /g command without active session."""
        self.tui._current_session_id = None

        self.tui._handle_session_continue_command("", self.mock_log_view)

        # Verify no session message
        self.assertIn("No active session to continue", self.mock_log_view.text)

    def test_handle_session_pause_command_with_active_session(self):
        """Test /p command with active session."""
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "active-session"
        mock_session.goal = "项目计划"
        mock_session.status = Mock()
        mock_session.status.name = "OBSERVING"
        self.mock_session_manager.get_session.return_value = mock_session
        self.tui._current_session_id = "active-session"

        self.tui._handle_session_pause_command("", self.mock_log_view)

        # Verify session paused
        self.assertEqual(mock_session.status.name, "OBSERVING")
        self.mock_session_manager.save_session.assert_called_once_with(mock_session)
        self.assertIn("Session active-session paused", self.mock_log_view.text)
        self.assertIn("Goal: 项目计划", self.mock_log_view.text)

    def test_handle_session_pause_command_without_active_session(self):
        """Test /p command without active session."""
        self.tui._current_session_id = None

        self.tui._handle_session_pause_command("", self.mock_log_view)

        # Verify no session message
        self.assertIn("No active session to pause", self.mock_log_view.text)

    def test_handle_session_tree_command_with_sessions(self):
        """Test /t command with sessions."""
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.session_id = "session-1"
        mock_session1.goal = "项目计划"
        mock_session1.status.name = "COMPLETED"

        mock_session2 = Mock()
        mock_session2.session_id = "session-2"
        mock_session2.goal = "需求分析"
        mock_session2.status.name = "RUNNING"

        self.mock_session_manager.list_sessions.return_value = [mock_session1, mock_session2]
        self.tui._current_session_id = "session-1"
        self.tui._session_stack = ["session-2"]

        self.tui._handle_session_tree_command("", self.mock_log_view)

        # Verify session tree
        self.assertIn("Session Tree:", self.mock_log_view.text)
        self.assertIn("session-1 - 项目计划 (COMPLETED)", self.mock_log_view.text)
        self.assertIn("session-2 - 需求分析 (RUNNING)", self.mock_log_view.text)

    def test_handle_session_tree_command_without_sessions(self):
        """Test /t command without sessions."""
        self.mock_session_manager.list_sessions.return_value = []

        self.tui._handle_session_tree_command("", self.mock_log_view)

        # Verify no sessions message
        self.assertIn("No sessions found", self.mock_log_view.text)

    def test_handle_session_abort_and_jump_command_with_valid_index(self):
        """Test /tc command with valid index."""
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.session_id = "session-1"
        mock_session1.goal = "项目计划"
        mock_session1.status = Mock()
        mock_session1.status.name = "COMPLETED"

        mock_session2 = Mock()
        mock_session2.session_id = "session-2"
        mock_session2.goal = "需求分析"
        mock_session2.status = Mock()
        mock_session2.status.name = "RUNNING"

        self.mock_session_manager.list_sessions.return_value = [mock_session1, mock_session2]
        self.tui._current_session_id = "current-session"

        self.tui._handle_session_abort_and_jump_command("1", "", self.mock_log_view)

        # Verify session abort and jump
        self.assertIn("Session current-session aborted", self.mock_log_view.text)
        self.assertIn("Jumped to session session-1", self.mock_log_view.text)
        self.assertIn("Goal: 项目计划", self.mock_log_view.text)
        self.assertIn("Status: COMPLETED", self.mock_log_view.text)

    def test_handle_session_abort_and_jump_command_with_invalid_index(self):
        """Test /tc command with invalid index."""
        # Mock empty sessions list
        self.mock_session_manager.list_sessions.return_value = []

        self.tui._handle_session_abort_and_jump_command("999", "", self.mock_log_view)

        # Verify invalid index message
        self.assertIn("Invalid session index: 999", self.mock_log_view.text)

    def test_handle_session_abort_and_jump_command_without_args(self):
        """Test /tc command without arguments."""
        self.tui._handle_session_abort_and_jump_command("", "", self.mock_log_view)

        # Verify missing argument message
        self.assertIn("Session abort and jump command requires a session index",
                      self.mock_log_view.text)

    def test_handle_session_pause_and_jump_command_with_valid_index(self):
        """Test /tt command with valid index."""
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.session_id = "session-1"
        mock_session1.goal = "项目计划"
        mock_session1.status = Mock()
        mock_session1.status.name = "COMPLETED"

        mock_session2 = Mock()
        mock_session2.session_id = "session-2"
        mock_session2.goal = "需求分析"
        mock_session2.status = Mock()
        mock_session2.status.name = "RUNNING"

        self.mock_session_manager.list_sessions.return_value = [mock_session1, mock_session2]
        self.tui._current_session_id = "current-session"

        self.tui._handle_session_pause_and_jump_command("1", "", self.mock_log_view)

        # Verify session pause and jump
        self.assertIn("Session current-session paused", self.mock_log_view.text)
        self.assertIn("Jumped to session session-1", self.mock_log_view.text)
        self.assertIn("Goal: 项目计划", self.mock_log_view.text)
        self.assertIn("Status: COMPLETED", self.mock_log_view.text)

    def test_handle_session_pause_and_jump_command_with_invalid_index(self):
        """Test /tt command with invalid index."""
        # Mock empty sessions list
        self.mock_session_manager.list_sessions.return_value = []

        self.tui._handle_session_pause_and_jump_command("999", "", self.mock_log_view)

        # Verify invalid index message
        self.assertIn("Invalid session index: 999", self.mock_log_view.text)

    def test_handle_session_pause_and_jump_command_without_args(self):
        """Test /tt command without arguments."""
        self.tui._handle_session_pause_and_jump_command("", "", self.mock_log_view)

        # Verify missing argument message
        self.assertIn("Session pause and jump command requires a session index",
                      self.mock_log_view.text)

    def test_handle_escape_key(self):
        """Test ESC key handling."""
        self.tui._current_session_id = "test-session"
        self.tui._session_stack = ["parent-session"]

        self.tui._handle_escape_key()

        # Verify all sessions aborted
        self.assertIsNone(self.tui._current_session_id)
        self.assertEqual(len(self.tui._session_stack), 0)
        self.assertIn("All sessions aborted. Back to default session.", self.mock_log_view.text)
        self.assertIn("Do you want to clear all context? (Y/N)", self.mock_log_view.text)

    def test_handle_role_add_command_with_single_arg(self):
        """Test /role add command with only one argument."""
        self.tui._handle_role_add_command("项目经理", "", self.mock_log_view)

        # Verify error message
        self.assertIn("Role add command requires both name and persona", self.mock_log_view.text)


if __name__ == '__main__':
    unittest.main()
