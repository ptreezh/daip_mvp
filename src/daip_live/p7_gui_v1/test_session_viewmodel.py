import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel


class TestSessionViewModel:
    """TDD for Session Management ViewModel"""
    
    def test_session_viewmodel_initialization(self):
        """RED: Test that SessionViewModel can be initialized"""
        mock_interaction = Mock()
        vm = SessionViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_sessions')
        assert hasattr(vm, '_current_session')
    
    def test_session_viewmodel_initial_properties(self):
        """RED: Test initial properties of SessionViewModel"""
        mock_interaction = Mock()
        vm = SessionViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('available_sessions') == []
        assert vm.get_property('current_session_id') is None
        assert vm.get_property('current_session_data') is None
        assert vm.get_property('is_loading_sessions') is False
        assert vm.get_property('session_filter') == 'all'
    
    @pytest.mark.asyncio
    async def test_load_sessions_command(self):
        """RED: Test loading sessions functionality"""
        mock_interaction = AsyncMock()
        mock_interaction.get_sessions.return_value = [
            {"id": "session1", "title": "Session 1", "status": "active", "created_at": "2025-11-08"},
            {"id": "session2", "title": "Session 2", "status": "completed", "created_at": "2025-11-07"}
        ]
        
        vm = SessionViewModel(mock_interaction)
        loaded_sessions = await vm.load_sessions()
        
        assert len(loaded_sessions) == 2
        assert loaded_sessions[0]["id"] == "session1"
        assert loaded_sessions[1]["id"] == "session2"
        mock_interaction.get_sessions.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_session_command(self):
        """RED: Test creating a session functionality"""
        mock_interaction = AsyncMock()
        expected_session = {
            "id": "new_session_123", 
            "title": "New Session", 
            "goal": "Test Goal", 
            "status": "active",
            "created_at": "2025-11-08"
        }
        mock_interaction.create_session.return_value = expected_session
        
        vm = SessionViewModel(mock_interaction)
        created_session = await vm.create_session("Test Goal")
        
        assert created_session == expected_session
        mock_interaction.create_session.assert_called_once_with("Test Goal")
        
        # Verify the session was added to available sessions
        available_sessions = vm.get_property('available_sessions')
        assert len(available_sessions) == 1
        assert available_sessions[0]["id"] == "new_session_123"
    
    def test_active_session_management(self):
        """RED: Test active session management"""
        mock_interaction = Mock()
        vm = SessionViewModel(mock_interaction)
        
        # Add some sessions
        sessions = [
            {"id": "session1", "title": "Session 1", "status": "active"},
            {"id": "session2", "title": "Session 2", "status": "completed"}
        ]
        vm.set_property('available_sessions', sessions)
        
        # Select a session as current
        result = vm.select_session('session1')
        assert result == "Selected session: session1"
        assert vm.get_property('current_session_id') == 'session1'
        assert vm.get_property('current_session_data') == sessions[0]
    
    def test_session_filtering(self):
        """RED: Test session filtering functionality"""
        mock_interaction = Mock()
        vm = SessionViewModel(mock_interaction)
        
        # Add some sessions with different statuses
        sessions = [
            {"id": "session1", "title": "Active Session", "status": "active"},
            {"id": "session2", "title": "Completed Session", "status": "completed"},
            {"id": "session3", "title": "Pending Session", "status": "pending"}
        ]
        vm.set_property('available_sessions', sessions)
        
        # Test filtering by status
        active_sessions = vm.get_sessions_by_status('active')
        assert len(active_sessions) == 1
        assert active_sessions[0]["id"] == "session1"
        
        all_sessions = vm.get_sessions_by_status('all')
        assert len(all_sessions) == 3
    
    def test_property_management(self):
        """RED: Test property management functionality"""
        mock_interaction = Mock()
        vm = SessionViewModel(mock_interaction)
        
        # Test setting and getting properties
        vm.set_property('session_filter', 'active')
        assert vm.get_property('session_filter') == 'active'
        
        vm.set_property('is_loading_sessions', True)
        assert vm.get_property('is_loading_sessions') is True