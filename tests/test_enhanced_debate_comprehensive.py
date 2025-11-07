"""
Comprehensive Test Suite for Enhanced TUI Debate Features

This test suite provides comprehensive validation of:
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests for complete workflows
"""

import asyncio
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
import pytest
from pathlib import Path

# Import the enhanced debate features
from daip_live.core.models import (
    DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent, 
    DebateRoundStartEvent, DebateTurnStartEvent
)
from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateHistoryView, DebateParticipantView, DebateTurnView
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker


class TestUnitTests:
    """Unit tests for individual components."""
    
    def test_enhanced_debate_view_creation(self):
        """Test EnhancedDebateView model creation and properties."""
        participant = DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0)
        
        view = EnhancedDebateView(
            session_id="test_session_123",
            topic="Sample Debate Topic",
            participants=[participant],
            total_rounds=3
        )
        
        assert view.session_id == "test_session_123"
        assert view.topic == "Sample Debate Topic"
        assert view.total_rounds == 3
        assert len(view.participants) == 1
        assert view.status == "active"
        assert view.color_scheme["background"] == "#1E1E1E"
    
    def test_debate_participant_view(self):
        """Test DebateParticipantView model."""
        participant = DebateParticipantView(
            name="Test_Pro", 
            color="#FF0000", 
            symbol="🔵",
            turn_order=1
        )
        
        assert participant.name == "Test_Pro"
        assert participant.color == "#FF0000"
        assert participant.symbol == "🔵"
        assert participant.turn_order == 1
    
    def test_debate_turn_view(self):
        """Test DebateTurnView model."""
        from datetime import datetime
        turn = DebateTurnView(
            participant_name="Con_Arguer",
            content="My counter argument",
            round_number=2,
            turn_in_round=1
        )
        
        assert turn.participant_name == "Con_Arguer"
        assert turn.content == "My counter argument"
        assert turn.round_number == 2
        assert turn.turn_in_round == 1
        assert turn.timestamp is not None  # Should be set to current time
    
    def test_debate_history_view(self):
        """Test DebateHistoryView model."""
        participant = DebateParticipantView(name="Pro", color="#87CEEB", symbol="👤", turn_order=0)
        history = DebateHistoryView(
            session_id="history_session_456",
            topic="Historical Topic",
            participants=[participant],
            total_rounds=5
        )
        
        assert history.session_id == "history_session_456"
        assert history.topic == "Historical Topic"
        assert len(history.participants) == 1
        assert history.total_rounds == 5
        assert history.status == "active"


class TestIntegrationTests:
    """Integration tests for component interactions."""
    
    def test_debate_history_tracker_lifecycle(self):
        """Test complete lifecycle of debate history tracking."""
        tracker = DebateHistoryTracker()
        
        # 1. Start a debate
        start_event = DebateStartEvent(
            topic="AI Regulation Debate",
            roles=["pro_regulation", "anti_regulation"],
            rounds=3,
            session_id="integration_test_001"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == "integration_test_001"
        assert history.topic == "AI Regulation Debate"
        assert len(history.participants) == 2
        assert history.total_rounds == 3
        
        # 2. Add multiple turns
        turn1 = DebateTurnCompleteEvent(
            participant="pro_regulation",
            round_number=1,
            content_preview="We need regulation to prevent AI misuse",
            session_id="integration_test_001"
        )
        
        updated_history = asyncio.run(tracker.add_turn(turn1))
        assert len(updated_history.turns) == 1
        assert updated_history.turns[0].participant_name == "pro_regulation"
        
        turn2 = DebateTurnCompleteEvent(
            participant="anti_regulation",
            round_number=1,
            content_preview="Regulation would stifle innovation",
            session_id="integration_test_001"
        )
        
        updated_history = asyncio.run(tracker.add_turn(turn2))
        assert len(updated_history.turns) == 2
        assert updated_history.turns[1].participant_name == "anti_regulation"
        
        # 3. Complete the debate
        complete_event = DebateCompleteEvent(
            session_id="integration_test_001",
            summary="Debate concluded with mixed opinions"
        )
        
        final_history = asyncio.run(tracker.complete_debate(complete_event))
        assert final_history.status == "completed"
        assert final_history.end_time is not None
        assert len(final_history.turns) == 2
    
    def test_history_tracker_concurrent_sessions(self):
        """Test multiple concurrent debate sessions."""
        tracker = DebateHistoryTracker()
        
        # Start first debate
        start_event1 = DebateStartEvent(
            topic="First Debate",
            roles=["role1", "role2"],
            rounds=2,
            session_id="session_001"
        )
        asyncio.run(tracker.start_tracking(start_event1))
        
        # Start second debate
        start_event2 = DebateStartEvent(
            topic="Second Debate",
            roles=["roleA", "roleB"],
            rounds=2,
            session_id="session_002"
        )
        asyncio.run(tracker.start_tracking(start_event2))
        
        # Add turns to both debates
        turn1 = DebateTurnCompleteEvent(
            participant="role1",
            round_number=1,
            content_preview="Content for session 1",
            session_id="session_001"
        )
        asyncio.run(tracker.add_turn(turn1))
        
        turn2 = DebateTurnCompleteEvent(
            participant="roleA",
            round_number=1,
            content_preview="Content for session 2",
            session_id="session_002"
        )
        asyncio.run(tracker.add_turn(turn2))
        
        # Verify both histories exist and are separate
        history1 = asyncio.run(tracker.get_history("session_001"))
        history2 = asyncio.run(tracker.get_history("session_002"))
        
        assert history1 is not None
        assert history2 is not None
        assert history1.topic == "First Debate"
        assert history2.topic == "Second Debate"
        assert len(history1.turns) == 1
        assert len(history2.turns) == 1
        
        # Verify all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) == 2
    
    def test_participant_color_assignment(self):
        """Test that participant colors are properly assigned."""
        tracker = DebateHistoryTracker()
        
        # Create a debate with multiple roles
        start_event = DebateStartEvent(
            topic="Color Test Debate",
            roles=["researcher", "developer", "ethicist", "business", "policy", "user"],
            rounds=2,
            session_id="color_test_123"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        
        # Verify all participants have been assigned colors
        assert len(history.participants) == 6
        participant_names = [p.name for p in history.participants]
        assert "researcher" in participant_names
        assert "developer" in participant_names
        assert "ethicist" in participant_names
        assert "business" in participant_names
        assert "policy" in participant_names
        assert "user" in participant_names
        
        # Verify colors are assigned
        for participant in history.participants:
            assert participant.color.startswith("#")  # Should be a hex color


class TestEndToEndTests:
    """End-to-end tests for complete workflows."""
    
    def test_complete_debate_workflow(self):
        """Test complete debate workflow from start to end."""
        # This would normally test the full interaction between CLI/TUI and debate system
        # For now, we'll simulate the event flow that would occur
        
        tracker = DebateHistoryTracker()
        
        # Simulate a complete debate flow with all events
        debate_session_id = "e2e_debate_999"
        
        # 1. Debate starts
        start_event = DebateStartEvent(
            topic="The Future of AI",
            roles=["optimist", "pessimist", "realist"],
            rounds=3,
            session_id=debate_session_id
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        assert history.session_id == debate_session_id
        assert history.status == "active"
        assert len(history.participants) == 3
        
        # 2. Round 1 - All participants speak
        round1_events = [
            DebateTurnStartEvent(participant="optimist", round_number=1, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="optimist", round_number=1, content_preview="AI will solve all problems", session_id=debate_session_id),
            DebateTurnStartEvent(participant="pessimist", round_number=1, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="pessimist", round_number=1, content_preview="AI will cause mass unemployment", session_id=debate_session_id),
            DebateTurnStartEvent(participant="realist", round_number=1, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="realist", round_number=1, content_preview="AI will have mixed impacts", session_id=debate_session_id),
        ]
        
        for event in round1_events:
            if isinstance(event, DebateTurnCompleteEvent):
                asyncio.run(tracker.add_turn(event))
        
        # Check history after round 1
        history = asyncio.run(tracker.get_history(debate_session_id))
        assert len(history.turns) == 3
        assert history.current_round == 1
        
        # 3. Round 2 - All participants speak
        round2_events = [
            DebateTurnStartEvent(participant="pessimist", round_number=2, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="pessimist", round_number=2, content_preview="More concerns about AI", session_id=debate_session_id),
            DebateTurnStartEvent(participant="optimist", round_number=2, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="optimist", round_number=2, content_preview="More benefits of AI", session_id=debate_session_id),
            DebateTurnStartEvent(participant="realist", round_number=2, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="realist", round_number=2, content_preview="Balanced view of AI", session_id=debate_session_id),
        ]
        
        for event in round2_events:
            if isinstance(event, DebateTurnCompleteEvent):
                asyncio.run(tracker.add_turn(event))
        
        # Check history after round 2
        history = asyncio.run(tracker.get_history(debate_session_id))
        assert len(history.turns) == 6
        assert history.current_round == 2
        
        # 4. Round 3 - All participants speak
        round3_events = [
            DebateTurnStartEvent(participant="realist", round_number=3, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="realist", round_number=3, content_preview="Final balanced summary", session_id=debate_session_id),
            DebateTurnStartEvent(participant="optimist", round_number=3, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="optimist", round_number=3, content_preview="Final optimistic summary", session_id=debate_session_id),
            DebateTurnStartEvent(participant="pessimist", round_number=3, session_id=debate_session_id),
            DebateTurnCompleteEvent(participant="pessimist", round_number=3, content_preview="Final pessimistic summary", session_id=debate_session_id),
        ]
        
        for event in round3_events:
            if isinstance(event, DebateTurnCompleteEvent):
                asyncio.run(tracker.add_turn(event))
        
        # 5. Complete the debate
        complete_event = DebateCompleteEvent(
            session_id=debate_session_id,
            summary="Debate on The Future of AI completed with diverse perspectives presented"
        )
        asyncio.run(tracker.complete_debate(complete_event))
        
        # Final verification
        final_history = asyncio.run(tracker.get_history(debate_session_id))
        assert final_history.status == "completed"
        assert len(final_history.turns) == 9  # 3 rounds * 3 participants
        assert final_history.end_time is not None
        
        # Verify participant content is properly tracked
        participant_contents = {}
        for turn in final_history.turns:
            if turn.participant_name not in participant_contents:
                participant_contents[turn.participant_name] = []
            participant_contents[turn.participant_name].append(turn.content)
        
        assert len(participant_contents) == 3
        for participant, contents in participant_contents.items():
            assert len(contents) == 3  # Each participant spoke in each round
    
    def test_debate_history_retrieval_workflow(self):
        """Test the workflow for retrieving and displaying debate history."""
        tracker = DebateHistoryTracker()
        
        # Create a debate with multiple rounds
        start_event = DebateStartEvent(
            topic="History Retrieval Test",
            roles=["analyst", "critic"],
            rounds=2,
            session_id="history_test_777"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add several turns
        turns = [
            DebateTurnCompleteEvent(participant="analyst", round_number=1, content_preview="First analytical point", session_id="history_test_777"),
            DebateTurnCompleteEvent(participant="critic", round_number=1, content_preview="First critical response", session_id="history_test_777"),
            DebateTurnCompleteEvent(participant="analyst", round_number=2, content_preview="Second analytical point", session_id="history_test_777"),
            DebateTurnCompleteEvent(participant="critic", round_number=2, content_preview="Second critical response", session_id="history_test_777"),
        ]
        
        for turn in turns:
            asyncio.run(tracker.add_turn(turn))
        
        # Complete the debate
        complete_event = DebateCompleteEvent(
            session_id="history_test_777",
            summary="History retrieval test completed"
        )
        asyncio.run(tracker.complete_debate(complete_event))
        
        # Test retrieval of specific history
        retrieved_history = asyncio.run(tracker.get_history("history_test_777"))
        assert retrieved_history is not None
        assert retrieved_history.session_id == "history_test_777"
        assert len(retrieved_history.turns) == 4
        assert retrieved_history.status == "completed"
        
        # Test retrieval of all histories
        all_histories = asyncio.run(tracker.get_all_histories())
        assert len(all_histories) >= 1  # Should include our test history
        found = False
        for h in all_histories:
            if h.session_id == "history_test_777":
                found = True
                break
        assert found, "Test history should be found in all histories"
    
    def test_enhanced_debate_view_with_realistic_data(self):
        """Test EnhancedDebateView with realistic debate data."""
        participants = [
            DebateParticipantView(name="Pro_Ai", color="#87CEEB", symbol="🤖", turn_order=0),
            DebateParticipantView(name="Con_Ai", color="#FFB6C1", symbol="⚠️", turn_order=1),
            DebateParticipantView(name="Mod_Ai", color="#98FB98", symbol="📋", turn_order=2),
        ]
        
        # Create a debate with multiple turns
        history = [
            DebateTurnView(participant_name="Pro_Ai", content="AI will bring unprecedented benefits", round_number=1, turn_in_round=1),
            DebateTurnView(participant_name="Con_Ai", content="AI poses serious safety risks", round_number=1, turn_in_round=2),
            DebateTurnView(participant_name="Mod_Ai", content="Both perspectives have merit", round_number=1, turn_in_round=3),
            DebateTurnView(participant_name="Pro_Ai", content="Technical solutions address safety", round_number=2, turn_in_round=1),
            DebateTurnView(participant_name="Con_Ai", content="Solutions may not prevent misuse", round_number=2, turn_in_round=2),
            DebateTurnView(participant_name="Mod_Ai", content="Regulation can balance both", round_number=2, turn_in_round=3),
        ]
        
        enhanced_view = EnhancedDebateView(
            session_id="complete_debate_view_888",
            topic="AI Benefits vs Risks",
            participants=participants,
            current_round=2,
            total_rounds=2,
            history=history,
            status="completed"
        )
        
        # Verify the enhanced view contains all expected data
        assert enhanced_view.session_id == "complete_debate_view_888"
        assert enhanced_view.topic == "AI Benefits vs Risks"
        assert len(enhanced_view.participants) == 3
        assert len(enhanced_view.history) == 6
        assert enhanced_view.current_round == 2
        assert enhanced_view.total_rounds == 2
        assert enhanced_view.status == "completed"
        
        # Verify participants have proper attributes
        names = [p.name for p in enhanced_view.participants]
        assert "Pro_Ai" in names
        assert "Con_Ai" in names
        assert "Mod_Ai" in names
        
        # Verify history has proper round distribution
        round1_turns = [t for t in enhanced_view.history if t.round_number == 1]
        round2_turns = [t for t in enhanced_view.history if t.round_number == 2]
        assert len(round1_turns) == 3
        assert len(round2_turns) == 3


def run_comprehensive_tests():
    """Run all tests in the suite."""
    test_suite = TestUnitTests()
    test_integration = TestIntegrationTests()
    test_e2e = TestEndToEndTests()
    
    # Run all unit tests
    print("Running Unit Tests...")
    test_suite.test_enhanced_debate_view_creation()
    test_suite.test_debate_participant_view()
    test_suite.test_debate_turn_view()
    test_suite.test_debate_history_view()
    print("✓ Unit Tests Passed")
    
    # Run all integration tests
    print("Running Integration Tests...")
    test_integration.test_debate_history_tracker_lifecycle()
    test_integration.test_history_tracker_concurrent_sessions()
    test_integration.test_participant_color_assignment()
    print("✓ Integration Tests Passed")
    
    # Run all end-to-end tests
    print("Running End-to-End Tests...")
    test_e2e.test_complete_debate_workflow()
    test_e2e.test_debate_history_retrieval_workflow()
    test_e2e.test_enhanced_debate_view_with_realistic_data()
    print("✓ End-to-End Tests Passed")
    
    print("\n🎉 All Comprehensive Tests Passed!")


if __name__ == "__main__":
    run_comprehensive_tests()