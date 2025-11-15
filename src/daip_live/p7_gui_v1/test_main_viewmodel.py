import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel


class TestMainViewModel:
    """TDD for Main Window ViewModel"""
    
    def test_main_viewmodel_initialization(self):
        """RED: Test that MainViewModel can be initialized"""
        mock_interaction = Mock()
        vm = MainViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_current_view')
        assert hasattr(vm, '_session_data')
    
    def test_main_viewmodel_initial_properties(self):
        """RED: Test initial properties of MainViewModel"""
        mock_interaction = Mock()
        vm = MainViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('current_view') == 'chat'
        assert vm.get_property('is_processing') is False
        assert vm.get_property('current_session') is None
        assert vm.get_property('available_sessions') == []
        assert vm.get_property('available_roles') == []
    
    @pytest.mark.asyncio
    async def test_execute_command_method(self):
        """RED: Test execute_command method exists and is callable"""
        mock_interaction = Mock()
        vm = MainViewModel(mock_interaction)
        
        # Check that command execution method exists
        assert hasattr(vm, 'execute_command')
        assert callable(vm.execute_command)
        
        # This should work without errors
        result = vm.execute_command('initialize')
        assert result is not None  # Should return some command result
    
    @pytest.mark.asyncio
    async def test_switch_view_command(self):
        """RED: Test switch_view command functionality"""
        mock_interaction = Mock()
        vm = MainViewModel(mock_interaction)
        
        # Register and execute switch view command
        def switch_view_cmd(view_name):
            vm.set_property('current_view', view_name)
            return f"Switched to {view_name}"
        
        vm.register_command('switch_view', switch_view_cmd)
        
        result = vm.execute_command('switch_view', 'settings')
        assert result == "Switched to settings"
        assert vm.get_property('current_view') == 'settings'
    
    @pytest.mark.asyncio
    async def test_get_sessions_command(self):
        """RED: Test get_sessions command functionality"""
        mock_interaction = AsyncMock()
        mock_interaction.get_sessions.return_value = [
            {"id": "session1", "title": "Test Session 1"},
            {"id": "session2", "title": "Test Session 2"}
        ]
        
        vm = MainViewModel(mock_interaction)
        
        # Execute get sessions
        sessions = await vm.get_sessions()
        
        assert len(sessions) == 2
        assert sessions[0]["id"] == "session1"
        mock_interaction.get_sessions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session_command(self):
        """RED: Test create_session command functionality"""
        mock_interaction = AsyncMock()
        expected_session = {"id": "new_session", "title": "New Session", "goal": "Test Goal"}
        mock_interaction.create_session.return_value = expected_session
        
        vm = MainViewModel(mock_interaction)
        
        # Execute create session
        session = await vm.create_session("Test Goal")
        
        assert session == expected_session
        mock_interaction.create_session.assert_called_once_with("Test Goal")