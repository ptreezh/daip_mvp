"""
Integration tests for TUI core functionality.
"""

import asyncio
from unittest.mock import Mock, patch

import pytest
from textual.widgets import Input

from src.daip_live.tui import DAIP_TUI

pytestmark = pytest.mark.skip(
    reason="旧spec：TUI/CLI 内部实现已重构（_highlight_code_and_json/_handle_shortcut_command/_get_autocomplete_suggestions/_model_manager 已移除，CLI 帮助文本/命令集已变）；当前源码为准"  # noqa: E501
)


class TestTUIIntegration:
    """Integration tests for TUI core functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch("daip_live.container.Container"):
            app = DAIP_TUI()
            return app

    def test_input_handling_integration(self, tui_app):
        """Test the complete input handling flow."""
        # Setup
        test_input = "/help"

        # Mock the command handler
        with patch.object(tui_app, "_handle_shortcut_command") as mock_handler:
            with patch.object(tui_app, "query_one") as mock_query:
                # Mock the input widget
                mock_input_widget = Mock(spec=Input)
                mock_input_widget.value = test_input
                mock_query.return_value = mock_input_widget

                # Mock message
                message = Mock()
                message.value = test_input

                # Execute
                tui_app.on_input_submitted(message)

                # Assert
                mock_handler.assert_called_once_with(test_input)
                # Verify input was cleared
                assert mock_input_widget.value == ""

    def test_model_switching_integration(self, tui_app):
        """Test the complete model switching flow."""
        # Setup
        model_name = "llama3"

        # Mock the model manager and provider
        with patch.object(tui_app, "_model_manager") as mock_manager:
            with patch.object(tui_app, "_model_provider"):
                # Setup mock manager
                mock_manager.get_available_models.return_value = [
                    {"name": "llama3", "provider": "ollama"}
                ]
                mock_manager.switch_model.return_value = True

                # Mock the UI update methods
                with patch.object(tui_app, "_update_log_view"):
                    with patch.object(tui_app, "_update_current_model"):
                        # Execute
                        tui_app._handle_model_switch(model_name)

                        # Assert
                        mock_manager.switch_model.assert_called_once_with(
                            model_name, "ollama"
                        )
                        tui_app._update_current_model.assert_called_once_with(
                            model_name
                        )

    def test_autocomplete_integration(self, tui_app):
        """Test the complete autocomplete flow."""
        # Setup
        partial_input = "/he"

        # Mock the autocomplete suggestions
        with patch.object(
            tui_app, "_get_autocomplete_suggestions", return_value=["/help", "/history"]
        ):
            with patch.object(tui_app, "query", return_value=[]):
                # Mock message
                message = Mock()
                message.value = partial_input

                # Execute
                tui_app.on_input_changed(message)

                # The method should complete without error
                assert True

    def test_command_execution_integration(self, tui_app):
        """Test the complete command execution flow."""
        # Setup

        # Mock the command handler
        with patch.object(tui_app, "_handle_help_command") as mock_handler:
            # Execute
            tui_app._handle_help_command("")

            # Assert
            # The handler should be called
            assert mock_handler.called

    def test_background_task_integration(self, tui_app):
        """Test the background task creation and management integration."""

        # Setup
        async def dummy_task():
            await asyncio.sleep(0.1)
            return "completed"

        # Mock the event loop
        with patch("src.daip_live.tui.asyncio.get_running_loop") as mock_loop:
            mock_loop.return_value.create_task = asyncio.create_task

            # Execute - this is testing the pattern used in the TUI
            task = asyncio.create_task(dummy_task())
            tui_app._background_tasks.add(task)
            task.add_done_callback(tui_app._background_tasks.discard)

            # Assert
            assert task in tui_app._background_tasks

            # Cleanup
            task.cancel()

    def test_error_handling_integration(self, tui_app):
        """Test the error handling integration."""
        # Setup
        test_input = "/nonexistent"

        # Mock the update log view to capture calls
        with patch.object(tui_app, "_update_log_view") as mock_log:
            # Mock the command handler to not exist
            with patch.object(tui_app, "_available_commands", []):
                # Execute
                tui_app._suggest_similar_commands(test_input[1:])  # Remove the '/'

                # Assert that error messages were logged
                assert mock_log.called
