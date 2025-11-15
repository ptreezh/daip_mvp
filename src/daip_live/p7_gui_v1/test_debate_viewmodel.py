import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.debate_viewmodel import DebateViewModel


class TestDebateViewModel:
    """TDD for Debate System ViewModel"""
    
    def test_debate_viewmodel_initialization(self):
        """RED: Test that DebateViewModel can be initialized"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_debates')
        assert hasattr(vm, '_current_debate')
        assert hasattr(vm, '_participants')
    
    def test_debate_viewmodel_initial_properties(self):
        """RED: Test initial properties of DebateViewModel"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('available_debates') == []
        assert vm.get_property('current_debate_id') is None
        assert vm.get_property('current_debate_data') is None
        assert vm.get_property('available_participants') == []
        assert vm.get_property('current_participants') == []
        assert vm.get_property('debate_topic') == ''
        assert vm.get_property('is_active_debate') is False
        assert vm.get_property('is_loading_debates') is False
    
    @pytest.mark.asyncio
    async def test_start_debate_command(self):
        """RED: Test starting a debate functionality"""
        mock_interaction = AsyncMock()
        expected_debate = {
            'id': 'debate123', 
            'topic': 'AI Ethics', 
            'status': 'active',
            'participants': [],
            'arguments': []
        }
        mock_interaction.start_debate.return_value = expected_debate
        
        vm = DebateViewModel(mock_interaction)
        debate = await vm.start_debate('AI Ethics')
        
        assert debate == expected_debate
        mock_interaction.start_debate.assert_called_once_with('AI Ethics')
    
    @pytest.mark.asyncio
    async def test_join_debate_command(self):
        """RED: Test joining a debate functionality"""
        mock_interaction = AsyncMock()
        mock_interaction.join_debate.return_value = {
            'success': True, 
            'message': 'Joined debate successfully'
        }
        
        vm = DebateViewModel(mock_interaction)
        result = await vm.join_debate('debate123', 'participant1')
        
        assert result['success'] is True
        mock_interaction.join_debate.assert_called_once_with('debate123', 'participant1')
    
    def test_participant_management(self):
        """RED: Test participant management functionality"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        
        # Test adding participants
        assert hasattr(vm, 'add_participant')
        assert callable(vm.add_participant)
        
        # Test removing participants
        assert hasattr(vm, 'remove_participant')
        assert callable(vm.remove_participant)
    
    def test_argument_submission(self):
        """RED: Test argument submission functionality"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        
        # Test submitting argument method exists
        assert hasattr(vm, 'submit_argument')
        assert callable(vm.submit_argument)
    
    def test_property_management(self):
        """RED: Test property management functionality"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        
        # Test setting and getting properties
        vm.set_property('debate_topic', 'AI Ethics')
        assert vm.get_property('debate_topic') == 'AI Ethics'
        
        vm.set_property('is_active_debate', True)
        assert vm.get_property('is_active_debate') is True
    
    def test_active_debate_tracking(self):
        """RED: Test tracking of active debate"""
        mock_interaction = Mock()
        vm = DebateViewModel(mock_interaction)
        
        # Initially no active debate
        assert vm.get_active_debate_id() is None
        assert vm.is_debate_active() is False
        
        # Set active debate
        vm.set_property('current_debate_id', 'debate123')
        vm.set_property('is_active_debate', True)
        
        assert vm.get_active_debate_id() == 'debate123'
        assert vm.is_debate_active() is True