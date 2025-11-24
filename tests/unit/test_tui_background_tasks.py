"""
Unit tests for TUI background task management functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from asyncio import Future
import asyncio
import time
from src.daip_live.tui import DAIP_TUI


class TestTUIBackgroundTaskManagement:
    """Test cases for TUI background task management functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('src.daip_live.tui.Container'):
            app = DAIP_TUI()
            return app

    def test_background_tasks_set_initialized(self, tui_app):
        """Test that background tasks set is initialized."""
        # Assert
        assert hasattr(tui_app, '_background_tasks')
        assert isinstance(tui_app._background_tasks, set)

    def test_on_unmount_cancels_background_tasks(self, tui_app):
        """Test that unmounting the app cancels all background tasks."""
        # Setup - create some mock tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task1.done.return_value = False
        mock_task2.done.return_value = False
        
        tui_app._background_tasks.add(mock_task1)
        tui_app._background_tasks.add(mock_task2)
        
        # Execute
        tui_app.on_unmount()
        
        # Assert
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_called_once()
        assert len(tui_app._background_tasks) == 0

    def test_handle_ctrl_e_exit_cancels_background_tasks(self, tui_app):
        """Test that CTRL+E exit cancels all background tasks."""
        # Setup - create some mock tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task1.done.return_value = False
 # Task is not done initially
        mock_task2.done.return_value = False
    
        tui_app._background_tasks.add(mock_task1)
        tui_app._background_tasks.add(mock_task2)
    
        # Set up the timing so that the second press is within the 2-second window
        import time
        tui_app._last_ctrl_e_time = time.time() - 1  # First press was 1 second ago
    
        # Mock exit method
        with patch.object(tui_app, 'exit'):
            # Mock the set_timer method to avoid event loop issues
            with patch.object(tui_app, 'set_timer'):
                # Execute - this should trigger the exit since it's the second press
                tui_app._handle_ctrl_e_exit()
                
                # Assert
                mock_task1.cancel.assert_called_once()
                mock_task2.cancel.assert_called_once()

    def test_handle_ctrl_q_exit_cancels_background_tasks(self, tui_app):
        """Test that CTRL+Q exit cancels all background tasks."""
        # Setup - create some mock tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task1.done.return_value = False  # Task is not done initially
        mock_task2.done.return_value = False
    
        tui_app._background_tasks.add(mock_task1)
        tui_app._background_tasks.add(mock_task2)
    
        # Set up the timing so that the second press is within the 2-second window
        import time
        tui_app._last_ctrl_q_time = time.time() - 1  # First press was 1 second ago
    
        # Mock exit method
        with patch.object(tui_app, 'exit'):
            # Mock the set_timer method to avoid event loop issues
            with patch.object(tui_app, 'set_timer'):
                # Execute - this should trigger the exit since it's the second press
                tui_app._handle_ctrl_q_exit()
                
                # Assert
                mock_task1.cancel.assert_called_once()
                mock_task2.cancel.assert_called_once()

    def test_handle_quit_command_cancels_background_tasks(self, tui_app):
        """Test that quit command cancels all background tasks."""
        # Setup - create some mock tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task1.done.return_value = False
        mock_task2.done.return_value = False
        
        tui_app._background_tasks.add(mock_task1)
        tui_app._background_tasks.add(mock_task2)
        
        # Mock exit method
        with patch.object(tui_app, 'exit'):
            # Execute
            tui_app._handle_quit_command("")
            
            # Assert
            mock_task1.cancel.assert_called_once()
            mock_task2.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_compress_session_context_async_handles_success(self, tui_app):
        """Test that compress session context async handles successful compression."""
        # Setup
        mock_session = Mock()
        
        # Mock the memory service
        with patch.object(tui_app, '_memory_service') as mock_memory_service:
            # Setup mock to return successfully
            # Create a mock future to simulate async behavior
            future = Future()
            future.set_result(None)
            mock_memory_service.compress_history = MagicMock(return_value=future)
            
            # Mock the log view update
            with patch.object(tui_app, '_update_log_view'):
                # Execute
                await tui_app._compress_session_context_async(mock_session)
                
                # Assert
                mock_memory_service.compress_history.assert_called_once_with(mock_session)

    @pytest.mark.asyncio
    async def test_compress_session_context_async_handles_exception(self, tui_app):
        """Test that compress session context async handles exceptions."""
        # Setup
        mock_session = Mock()
        # Mock the history attribute to avoid subscriptable error
        mock_session.history = ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]
        
        # Mock the memory service to raise an exception
        with patch.object(tui_app, '_memory_service') as mock_memory_service:
            # Create a mock future that raises an exception
            future = Future()
            future.set_exception(Exception("Test error"))
            mock_memory_service.compress_history = MagicMock(return_value=future)
            
            # Mock the log view update
            with patch.object(tui_app, '_update_log_view'):
                # Execute
                await tui_app._compress_session_context_async(mock_session)
                
                # The method should complete without propagating the exception
                assert True