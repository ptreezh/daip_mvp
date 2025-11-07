"""
Tests for Enhanced TUI Debate Features
This test suite validates the implementation of enhanced debate features including:
- Enhanced visual representation of debate participants
- Debate history tracking and navigation
- Multi-model support for different debate participants
"""
import asyncio
from unittest.mock import Mock, AsyncMock, patch

import pytest

from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent
from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateHistoryView
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker


class TestEnhancedDebateFeatures:
    """Test suite for enhanced debate functionality."""
    
    def test_enhanced_debate_view_creation(self):
        """Test creation of EnhancedDebateView with proper data structures."""
        participants = [
            {"name": "pro_arguer", "color": "#87CEEB", "symbol": "👤"},
            {"name": "con_arguer", "color": "#FFB6C1", "symbol": "👤"}
        ]
        
        view = EnhancedDebateView(
            session_id="test_session_123",
            topic="Sample Debate Topic",
            participants=participants,
            total_rounds=3
        )
        
        assert view.session_id == "test_session_123"
        assert view.topic == "Sample Debate Topic"
        assert view.total_rounds == 3
        assert len(view.participants) == 2
        assert view.status == "active"
    
    def test_debate_history_tracker(self):
        """Test debate history tracking functionality."""
        tracker = DebateHistoryTracker()
        
        # Create a mock debate start event
        start_event = DebateStartEvent(
            topic="Test Topic",
            roles=["pro_arguer", "con_arguer"],
            rounds=2,
            session_id="test_session_456"
        )
        
        # Start tracking
        history = asyncio.run(tracker.start_tracking(start_event))
        
        assert history.session_id == "test_session_456"
        assert history.topic == "Test Topic"
        assert len(history.participants) == 2
        assert history.total_rounds == 2
        
        # Add a turn to the debate
        turn_event = DebateTurnCompleteEvent(
            participant="pro_arguer",
            round_number=1,
            content_preview="This is a test argument.",
            session_id="test_session_456"
        )
        
        updated_history = asyncio.run(tracker.add_turn(turn_event))
        
        assert len(updated_history.turns) == 1
        assert updated_history.turns[0].participant_name == "pro_arguer"
        assert updated_history.turns[0].content == "This is a test argument."
        
        # Complete the debate
        complete_event = DebateCompleteEvent(
            session_id="test_session_456",
            summary="Debate completed successfully."
        )
        
        final_history = asyncio.run(tracker.complete_debate(complete_event))
        assert final_history.status == "completed"
        assert final_history.end_time is not None

    def test_participant_color_assignment(self):
        """Test proper color assignment for debate participants."""
        tracker = DebateHistoryTracker()
        
        # Create a mock debate start event with multiple roles
        start_event = DebateStartEvent(
            topic="Multi-Participant Test",
            roles=["role1", "role2", "role3", "role4", "role5"],
            rounds=3,
            session_id="multi_test_789"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        
        # Verify that each participant has been assigned a color
        assert len(history.participants) == 5
        for participant in history.participants:
            assert participant.name in ["role1", "role2", "role3", "role4", "role5"]
            assert participant.color.startswith("#")  # Should be a hex color

    def test_debate_history_retrieval(self):
        """Test retrieving debate history by session ID."""
        tracker = DebateHistoryTracker()
        
        # Create and track a debate
        start_event = DebateStartEvent(
            topic="Retrieval Test",
            roles=["test_role"],
            rounds=1,
            session_id="retrieve_test_111"
        )
        
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add a turn
        turn_event = DebateTurnCompleteEvent(
            participant="test_role",
            round_number=1,
            content_preview="Test content for retrieval.",
            session_id="retrieve_test_111"
        )
        
        asyncio.run(tracker.add_turn(turn_event))
        
        # Retrieve the specific history
        retrieved_history = asyncio.run(tracker.get_history("retrieve_test_111"))
        
        assert retrieved_history is not None
        assert retrieved_history.session_id == "retrieve_test_111"
        assert len(retrieved_history.turns) == 1
        assert retrieved_history.turns[0].content == "Test content for retrieval."
        
        # Test retrieval of all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) == 1
        assert all_histories[0].session_id == "retrieve_test_111"


if __name__ == "__main__":
    pytest.main([__file__])