"""
Unit tests for TUI debate output display functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from src.daip_live.tui import DAIP_TUI
from daip_live.core.models import (
    DebateStartEvent, DebateRoundStartEvent, DebateTurnStartEvent, 
    DebateTurnCompleteEvent, DebateCompleteEvent
)


class TestTUIDebateOutputDisplay:
    """Test cases for TUI debate output display functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('src.daip_live.tui.Container'):
            app = DAIP_TUI()
            return app

    def test_debate_start_event_displays_output(self, tui_app):
        """Test that DebateStartEvent displays output in TUI."""
        # Setup
        event = DebateStartEvent(
            topic="Should AI be regulated?",
            roles=["proponent", "opponent"],
            rounds=3,
            session_id="test_session"
        )
        
        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            tui_app._post_event(event)
            
            # Assert that output was displayed
            mock_update_log.assert_called()
            # Check that the call contains debate start information
            call_args = mock_update_log.call_args_list
            assert any("Debate started" in str(call) for call in call_args)
            assert any("Should AI be regulated?" in str(call) for call in call_args)

    def test_debate_round_start_event_displays_output(self, tui_app):
        """Test that DebateRoundStartEvent displays output in TUI."""
        # Setup
        event = DebateRoundStartEvent(
            round_number=1,
            total_rounds=3,
            session_id="test_session"
        )
        
        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            tui_app._post_event(event)
            
            # Assert that output was displayed
            mock_update_log.assert_called()
            # Check that the call contains round start information
            call_args = mock_update_log.call_args_list
            assert any("Round 1/3 starting" in str(call) for call in call_args)

    def test_debate_turn_start_event_displays_output(self, tui_app):
        """Test that DebateTurnStartEvent displays output in TUI."""
        # Setup
        event = DebateTurnStartEvent(
            participant="proponent",
            round_number=1,
            session_id="test_session"
        )
        
        # Initialize debate tracking
        tui_app._current_debate.update({
            'is_active': True,
            'participant_colors': {'proponent': 'blue', 'opponent': 'red'}
        })
        
        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            tui_app._post_event(event)
            
            # Assert that output was displayed
            mock_update_log.assert_called()
            # Check that the call contains turn start information
            call_args = mock_update_log.call_args_list
            assert any("proponent speaking" in str(call) for call in call_args)

    def test_debate_turn_complete_event_displays_output(self, tui_app):
        """Test that DebateTurnCompleteEvent displays output in TUI."""
        # Setup
        event = DebateTurnCompleteEvent(
            participant="proponent",
            round_number=1,
            content_preview="AI regulation is necessary for safety",
            session_id="test_session"
        )
        
        # Initialize debate tracking
        tui_app._current_debate.update({
            'is_active': True,
            'participant_colors': {'proponent': 'blue', 'opponent': 'red'}
        })
        
        # Mock the log view update method
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            # Execute
            tui_app._post_event(event)
            
            # Assert that output was displayed
            mock_update_log.assert_called()
            # Check that the call contains turn complete information and content
            call_args = mock_update_log.call_args_list
            assert any("proponent finished" in str(call) for call in call_args)
            assert any("AI regulation is necessary for safety" in str(call) for call in call_args)

    def test_debate_complete_event_displays_output(self, tui_app):
        """Test that DebateCompleteEvent displays output in TUI."""
        # Setup
        event = DebateCompleteEvent(
            session_id="test_session",
            summary="The debate concluded with agreement on the need for balanced AI regulation."
        )
        
        # Initialize debate tracking
        tui_app._current_debate.update({
            'is_active': True,
            'participant_colors': {'proponent': 'blue', 'opponent': 'red'}
        })
        
        # Mock the log view update method and save debate results
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            with patch.object(tui_app, '_save_debate_results'):
                # Execute
                tui_app._post_event(event)
                
                # Assert that output was displayed
                mock_update_log.assert_called()
                # Check that the call contains debate complete information and summary
                call_args = mock_update_log.call_args_list
                assert any("Debate completed" in str(call) for call in call_args)
                assert any("balanced AI regulation" in str(call) for call in call_args)

    def test_all_debate_events_display_output_in_sequence(self, tui_app):
        """Test that all debate events display output in correct sequence."""
        # Setup events in sequence
        start_event = DebateStartEvent(
            topic="Should AI be regulated?",
            roles=["proponent", "opponent"],
            rounds=1,
            session_id="test_session"
        )
        
        round_event = DebateRoundStartEvent(
            round_number=1,
            total_rounds=1,
            session_id="test_session"
        )
        
        turn_start_event = DebateTurnStartEvent(
            participant="proponent",
            round_number=1,
            session_id="test_session"
        )
        
        turn_complete_event = DebateTurnCompleteEvent(
            participant="proponent",
            round_number=1,
            content_preview="AI regulation is necessary for safety",
            session_id="test_session"
        )
        
        complete_event = DebateCompleteEvent(
            session_id="test_session",
            summary="The debate concluded with agreement on the need for balanced AI regulation."
        )
        
        # Initialize debate tracking
        tui_app._current_debate.update({
            'is_active': True,
            'participant_colors': {'proponent': 'blue', 'opponent': 'red'}
        })
        
        # Mock the log view update method and save debate results
        with patch.object(tui_app, '_update_log_view') as mock_update_log:
            with patch.object(tui_app, '_save_debate_results'):
                # Execute all events in sequence
                tui_app._post_event(start_event)
                tui_app._post_event(round_event)
                tui_app._post_event(turn_start_event)
                tui_app._post_event(turn_complete_event)
                tui_app._post_event(complete_event)
                
                # Assert that output was displayed for each event
                assert mock_update_log.call_count >= 5  # At least one call per event
                
                # Check that all types of information were displayed
                call_args_list = [str(call) for call in mock_update_log.call_args_list]
                all_calls = " ".join(call_args_list)
                
                assert "Debate started" in all_calls
                assert "Round 1/1 starting" in all_calls
                assert "proponent speaking" in all_calls
                assert "proponent finished" in all_calls
                assert "AI regulation is necessary for safety" in all_calls
                assert "Debate completed" in all_calls
                assert "balanced AI regulation" in all_calls