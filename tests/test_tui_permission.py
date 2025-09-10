import unittest
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import TextArea, Static
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daip_live.tui import DAIP_TUI, FocusMode, PermissionDialog


class TestTUIPermissionDialog(unittest.TestCase):
    """Test cases for TUI permission dialog features."""

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

    def test_permission_dialog_creation(self):
        """Test permission dialog creation with tool name and args."""
        # Create a permission dialog
        dialog = PermissionDialog("test_tool", {"arg1": "value1"}, lambda x: None)
        
        # Verify dialog properties
        self.assertEqual(dialog.tool_name, "test_tool")
        self.assertEqual(dialog.args, {"arg1": "value1"})
        self.assertIsNotNone(dialog.callback)

    def test_handle_permission_response_allowed(self):
        """Test handling of permission response when allowed."""
        # Mock the log view
        mock_log_view = Mock(spec=Static)
        mock_log_view.text = ""
        mock_log_view.renderable = ""
        
        # Mock the update method to capture what it was called with
        mock_log_view.update = Mock()
        
        # Mock query_one to return our mock log view
        self.tui.query_one = Mock(return_value=mock_log_view)
        
        # Handle permission response
        self.tui._handle_permission_response(True)
        
        # Verify update was called with the correct text
        mock_log_view.update.assert_called_once()
        call_args = mock_log_view.update.call_args[0][0]
        self.assertIn("Permission granted", call_args)

    def test_handle_permission_response_denied(self):
        """Test handling of permission response when denied."""
        # Mock the log view
        mock_log_view = Mock(spec=Static)
        mock_log_view.text = ""
        mock_log_view.renderable = ""
        
        # Mock the update method to capture what it was called with
        mock_log_view.update = Mock()
        
        # Mock query_one to return our mock log view
        self.tui.query_one = Mock(return_value=mock_log_view)
        
        # Handle permission response
        self.tui._handle_permission_response(False)
        
        # Verify update was called with the correct text
        mock_log_view.update.assert_called_once()
        call_args = mock_log_view.update.call_args[0][0]
        self.assertIn("Permission denied", call_args)


if __name__ == '__main__':
    unittest.main()