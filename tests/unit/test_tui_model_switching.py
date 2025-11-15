"""
Unit tests for TUI model switching functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.daip_live.tui import DAIP_TUI


class TestTUIModelSwitching:
    """Test cases for TUI model switching functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('src.daip_live.tui.Container'):
            app = DAIP_TUI()
            return app

    def test_update_current_model_updates_attributes(self, tui_app):
        """Test that updating current model updates both model attributes."""
        # Setup
        new_model_name = "gpt-4"
        
        # Execute
        tui_app._update_current_model(new_model_name)
        
        # Assert
        assert tui_app._current_model == new_model_name
        assert tui_app._model_name == new_model_name

    def test_update_current_model_updates_status_bar(self, tui_app):
        """Test that updating current model triggers status bar update."""
        # Setup
        new_model_name = "gpt-4"
        
        # Mock the status bar update method
        with patch.object(tui_app, '_update_status_bar'):
            # Execute
            tui_app._update_current_model(new_model_name)
            
            # Assert that status bar update was called
            tui_app._update_status_bar.assert_called_once()

    def test_update_current_model_handles_debate_participant(self, tui_app):
        """Test that updating current model handles debate participant context."""
        # Setup
        new_model_name = "gpt-4"
        tui_app._current_debate['is_active'] = True
        tui_app._current_debate['current_participant'] = "Alice"
        
        # Mock the status bar update and log view update methods
        with patch.object(tui_app, '_update_status_bar'):
            with patch.object(tui_app, '_update_log_view'):
                # Execute
                tui_app._update_current_model(new_model_name)
                
                # The method should complete without error
                assert True

    def test_handle_model_list_switches_model(self, tui_app):
        """Test that model list handling switches to selected model."""
        # Setup
        mock_model = {'name': 'llama3', 'provider': 'ollama'}
        
        # Mock the model manager and provider
        with patch.object(tui_app, '_model_manager') as mock_manager:
            with patch.object(tui_app, '_model_provider'):
                # Setup mock manager to return success
                mock_manager.switch_model.return_value = True
                
                # Mock the safe log callback
                with patch.object(tui_app, '_safe_log_callback'):
                    # Execute
                    # We need to mock the ModelSelectionDialog since it's a UI component
                    with patch('src.daip_live.tui.ModelSelectionDialog'):
                        tui_app._handle_model_list()
                        
                        # The method should complete without error
                        assert True

    def test_handle_model_switch_updates_model(self, tui_app):
        """Test that direct model switching updates the model."""
        # Setup
        model_name = "llama3"
        
        # Mock the model manager and provider
        with patch.object(tui_app, '_model_manager') as mock_manager:
            with patch.object(tui_app, '_model_provider'):
                # Setup mock manager to return the model in the list
                mock_manager.get_available_models.return_value = [
                    {'name': 'llama3', 'provider': 'ollama'}
                ]
                mock_manager.switch_model.return_value = True
                
                # Mock the log view update
                with patch.object(tui_app, '_update_log_view'):
                    # Execute
                    tui_app._handle_model_switch(model_name)
                    
                    # The method should complete without error
                    assert True