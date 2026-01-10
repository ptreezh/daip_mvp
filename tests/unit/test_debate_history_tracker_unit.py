"""
Unit Tests for DebateHistoryTracker
"""
import pytest
import asyncio
import tempfile
import os
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent


@pytest.fixture
def tracker():
    """Create a tracker with a temporary file for test isolation."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    tracker = DebateHistoryTracker(db_path=db_path)
    yield tracker
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def tracker_memory():
    """Create a tracker with in-memory database for testing."""
    # Note: For in-memory DB, each connection is a separate DB
    # So we use a file-based approach for reliable testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    tracker = DebateHistoryTracker(db_path=db_path)
    yield tracker
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


class TestDebateHistoryTrackerUnit:
    """Unit tests for DebateHistoryTracker service."""
    
    def test_debate_history_tracker_initialization(self, tracker):
        """Test DebateHistoryTracker initialization."""
        # The tracker uses file-based SQLite, not in-memory dict
        assert tracker.db_path.endswith('.db') or tracker.db_path == ":memory:"
        assert tracker._db_lock is not None
    
    def test_start_tracking_creates_history(self, tracker):
        """Test start_tracking creates a new debate history."""
        
        start_event = DebateStartEvent(
            topic="Test Topic",
            roles=["pro_arguer", "con_arguer"],
            rounds=3,
            session_id="test_session_001"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        
        assert history.session_id == "test_session_001"
        assert history.topic == "Test Topic"
        assert len(history.participants) == 2  # pro_arguer, con_arguer
        assert history.total_rounds == 3
        assert history.current_round == 0
        assert history.status == "active"
    
    def test_start_tracking_with_multiple_roles(self, tracker):
        """Test start_tracking with multiple roles."""
        
        start_event = DebateStartEvent(
            topic="Multiple Roles Test",
            roles=["role1", "role2", "role3", "role4"],
            rounds=5,
            session_id="multi_role_002"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        
        assert history.session_id == "multi_role_002"
        assert len(history.participants) == 4
        participant_names = [p.name for p in history.participants]
        assert "role1" in participant_names
        assert "role2" in participant_names
        assert "role3" in participant_names
        assert "role4" in participant_names
    
    def test_add_turn_to_history(self, tracker):
        """Test adding a turn to debate history."""
        
        # Start a debate first
        start_event = DebateStartEvent(
            topic="Turn Test",
            roles=["pro_arguer", "con_arguer"],
            rounds=2,
            session_id="turn_test_003"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add a turn
        turn_event = DebateTurnCompleteEvent(
            participant="pro_arguer",
            round_number=1,
            content_preview="This is my argument.",
            session_id="turn_test_003"
        )
        
        updated_history = asyncio.run(tracker.add_turn(turn_event))
        
        assert len(updated_history.turns) == 1
        assert updated_history.turns[0].participant_name == "pro_arguer"
        assert updated_history.turns[0].content == "This is my argument."
        assert updated_history.turns[0].round_number == 1
        assert updated_history.current_round == 1
    
    def test_add_multiple_turns(self, tracker):
        """Test adding multiple turns to debate history."""
        
        # Start a debate
        start_event = DebateStartEvent(
            topic="Multi-Turn Test",
            roles=["role1", "role2"],
            rounds=2,
            session_id="multi_turn_004"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add first turn
        turn1 = DebateTurnCompleteEvent(
            participant="role1",
            round_number=1,
            content_preview="First argument from role1",
            session_id="multi_turn_004"
        )
        asyncio.run(tracker.add_turn(turn1))
        
        # Add second turn
        turn2 = DebateTurnCompleteEvent(
            participant="role2",
            round_number=1,
            content_preview="Response from role2",
            session_id="multi_turn_004"
        )
        updated_history = asyncio.run(tracker.add_turn(turn2))
        
        assert len(updated_history.turns) == 2
        assert updated_history.turns[0].participant_name == "role1"
        assert updated_history.turns[1].participant_name == "role2"
        assert updated_history.turns[0].content == "First argument from role1"
        assert updated_history.turns[1].content == "Response from role2"
    
    def test_complete_debate(self, tracker):
        """Test completing a debate."""
        
        # Start and add some turns
        start_event = DebateStartEvent(
            topic="Completion Test",
            roles=["pro_arguer"],
            rounds=1,
            session_id="completion_005"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        turn_event = DebateTurnCompleteEvent(
            participant="pro_arguer",
            round_number=1,
            content_preview="Final statement",
            session_id="completion_005"
        )
        asyncio.run(tracker.add_turn(turn_event))
        
        complete_event = DebateCompleteEvent(
            session_id="completion_005",
            summary="Debate completed with final statement"
        )
        
        final_history = asyncio.run(tracker.complete_debate(complete_event))
        
        assert final_history.status == "completed"
        assert final_history.end_time is not None
        assert final_history.turns[0].content == "Final statement"
    
    def test_get_history(self, tracker):
        """Test retrieving a specific debate history."""
        
        # Start a debate
        start_event = DebateStartEvent(
            topic="Get Test",
            roles=["test_role"],
            rounds=1,
            session_id="get_test_006"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add a turn
        turn_event = DebateTurnCompleteEvent(
            participant="test_role",
            round_number=1,
            content_preview="Test content for retrieval",
            session_id="get_test_006"
        )
        asyncio.run(tracker.add_turn(turn_event))
        
        # Retrieve the history
        retrieved_history = asyncio.run(tracker.get_history("get_test_006"))
        
        assert retrieved_history is not None
        assert retrieved_history.session_id == "get_test_006"
        assert retrieved_history.topic == "Get Test"
        assert len(retrieved_history.turns) == 1
        assert retrieved_history.turns[0].content == "Test content for retrieval"
    
    def test_get_nonexistent_history(self, tracker):
        """Test retrieving a non-existent debate history."""
        
        retrieved_history = asyncio.run(tracker.get_history("nonexistent_007"))
        
        assert retrieved_history is None
    
    def test_get_all_histories(self, tracker):
        """Test retrieving all debate histories."""
        
        # Create multiple debates
        start_event1 = DebateStartEvent(
            topic="All Histories Test 1",
            roles=["role1"],
            rounds=1,
            session_id="all_hist_008"
        )
        asyncio.run(tracker.start_tracking(start_event1))
        
        start_event2 = DebateStartEvent(
            topic="All Histories Test 2",
            roles=["role2"],
            rounds=1,
            session_id="all_hist_009"
        )
        asyncio.run(tracker.start_tracking(start_event2))
        
        # Add turns to both
        turn1 = DebateTurnCompleteEvent(
            participant="role1",
            round_number=1,
            content_preview="Content 1",
            session_id="all_hist_008"
        )
        asyncio.run(tracker.add_turn(turn1))
        
        turn2 = DebateTurnCompleteEvent(
            participant="role2",
            round_number=1,
            content_preview="Content 2",
            session_id="all_hist_009"
        )
        asyncio.run(tracker.add_turn(turn2))
        
        # Get all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        
        assert len(all_histories) == 2
        
        session_ids = [h.session_id for h in all_histories]
        assert "all_hist_008" in session_ids
        assert "all_hist_009" in session_ids
    
    def test_clear_history(self, tracker):
        """Test clearing a debate history."""
        
        # Start a debate
        start_event = DebateStartEvent(
            topic="Clear Test",
            roles=["test_role"],
            rounds=1,
            session_id="clear_test_010"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add a turn
        turn_event = DebateTurnCompleteEvent(
            participant="test_role",
            round_number=1,
            content_preview="Content before clear",
            session_id="clear_test_010"
        )
        asyncio.run(tracker.add_turn(turn_event))
        
        # Verify history exists
        history_before = asyncio.run(tracker.get_history("clear_test_010"))
        assert history_before is not None
        assert len(history_before.turns) == 1
        
        # Clear the history
        cleared = asyncio.run(tracker.clear_history("clear_test_010"))
        
        assert cleared is True
        
        # Verify history no longer exists
        history_after = asyncio.run(tracker.get_history("clear_test_010"))
        assert history_after is None
    
    def test_clear_nonexistent_history(self, tracker):
        """Test clearing a non-existent debate history."""
        
        cleared = asyncio.run(tracker.clear_history("nonexistent_clear_011"))
        
        assert cleared is False


if __name__ == "__main__":
    pytest.main([__file__])
