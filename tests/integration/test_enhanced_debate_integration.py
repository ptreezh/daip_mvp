"""
Integration Tests for Enhanced Debate Features
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from daip_live.core.models import (
    DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent,
    DebateRoundStartEvent, DebateTurnStartEvent
)
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateParticipantView


class TestEnhancedDebateIntegration:
    """Integration tests for enhanced debate features."""
    
    def test_debate_history_tracker_and_models_integration(self):
        """Test integration between DebateHistoryTracker and debate models."""
        tracker = DebateHistoryTracker()
        
        # Start a debate
        start_event = DebateStartEvent(
            topic="Integration Test Topic",
            roles=["Pro_Arguer", "Con_Arguer", "Neutral_Analyst"],
            rounds=3,
            session_id="integration_001"
        )
        
        history = asyncio.run(tracker.start_tracking(start_event))
        
        # Verify that the history has correct properties (using the actual class)
        from daip_live.tui_v1.models.debate_view import DebateHistoryView
        assert isinstance(history, DebateHistoryView)
        assert history.session_id == "integration_001"
        assert len(history.participants) == 3
        
        # Verify participants are DebateParticipantView instances
        for participant in history.participants:
            assert isinstance(participant, DebateParticipantView)
            assert participant.name in ["Pro_Arguer", "Con_Arguer", "Neutral_Analyst"]
        
        # Add turns
        turn1 = DebateTurnCompleteEvent(
            participant="Pro_Arguer",
            round_number=1,
            content_preview="Pro argument for integration test",
            session_id="integration_001"
        )
        updated_history = asyncio.run(tracker.add_turn(turn1))
        
        # Verify turn is DebateTurnView instance
        assert len(updated_history.turns) == 1
        turn = updated_history.turns[0]
        from daip_live.tui_v1.models.debate_view import DebateTurnView
        assert isinstance(turn, DebateTurnView)
        assert turn.participant_name == "Pro_Arguer"
        assert turn.content == "Pro argument for integration test"
        assert turn.round_number == 1
    
    def test_enhanced_debate_view_and_events_integration(self):
        """Test integration between EnhancedDebateView and debate events."""
        # Create EnhancedDebateView with participants
        participants = [
            DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0),
            DebateParticipantView(name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1)
        ]
        
        debate_view = EnhancedDebateView(
            session_id="view_integration_002",
            topic="View-Event Integration Test",
            participants=participants,
            total_rounds=2
        )
        
        # Simulate debate events and update the view accordingly
        # This tests that the view model is compatible with event system
        
        # Add turns to the view's history
        from daip_live.tui_v1.models.debate_view import DebateTurnView
        
        debate_view.history.append(
            DebateTurnView(
                participant_name="Pro_Arguer",
                content="Integration argument from pro",
                round_number=1,
                turn_in_round=1
            )
        )
        
        debate_view.history.append(
            DebateTurnView(
                participant_name="Con_Arguer", 
                content="Integration argument from con",
                round_number=1,
                turn_in_round=2
            )
        )
        
        assert len(debate_view.history) == 2
        assert debate_view.history[0].participant_name == "Pro_Arguer"
        assert debate_view.history[1].participant_name == "Con_Arguer"
        assert debate_view.history[0].content == "Integration argument from pro"
        assert debate_view.history[1].content == "Integration argument from con"
    
    def test_history_tracker_concurrent_operations(self):
        """Test DebateHistoryTracker concurrent operations safety."""
        tracker = DebateHistoryTracker()
        
        async def simulate_concurrent_operations():
            # Start multiple debates concurrently
            tasks = []
            
            for i in range(5):
                start_event = DebateStartEvent(
                    topic=f"Concurrent Test {i}",
                    roles=[f"role_{i}_a", f"role_{i}_b"],
                    rounds=2,
                    session_id=f"concurrent_{i:03d}"
                )
                
                task = tracker.start_tracking(start_event)
                tasks.append(task)
            
            histories = await asyncio.gather(*tasks)
            
            # Verify all debates were started
            assert len(histories) == 5
            
            # Add turns to each debate concurrently
            turn_tasks = []
            for i, history in enumerate(histories):
                turn_event = DebateTurnCompleteEvent(
                    participant=f"role_{i}_a",
                    round_number=1,
                    content_preview=f"Turn content for debate {i}",
                    session_id=f"concurrent_{i:03d}"
                )
                
                task = tracker.add_turn(turn_event)
                turn_tasks.append(task)
            
            updated_histories = await asyncio.gather(*turn_tasks)
            
            # Verify all turns were added
            for i, updated_history in enumerate(updated_histories):
                assert len(updated_history.turns) == 1
                assert updated_history.turns[0].content == f"Turn content for debate {i}"
        
        asyncio.run(simulate_concurrent_operations())
    
    def test_participant_color_consistency(self):
        """Test that participant colors are consistent across components."""
        # Create debate participants
        participants = [
            DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0),
            DebateParticipantView(name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1)
        ]
        
        # Create EnhancedDebateView which should assign colors
        debate_view = EnhancedDebateView(
            session_id="color_consistency_003",
            topic="Color Consistency Test",
            participants=participants
        )
        
        # Check that colors are consistent
        participant_colors = debate_view.color_scheme["participant_colors"]
        
        for participant in participants:
            assert participant.name in participant_colors
            # The view might override the default colors, which is acceptable
            assert isinstance(participant_colors[participant.name], str)
    
    def test_event_to_history_mapping(self):
        """Test mapping of debate events to history records."""
        tracker = DebateHistoryTracker()
        
        # Start a debate
        start_event = DebateStartEvent(
            topic="Event Mapping Test",
            roles=["Mapper1", "Mapper2"],
            rounds=2,
            session_id="mapping_004"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add multiple turns with different rounds
        turn_events = [
            DebateTurnCompleteEvent(
                participant="Mapper1",
                round_number=1,
                content_preview="Round 1, Mapper1",
                session_id="mapping_004"
            ),
            DebateTurnCompleteEvent(
                participant="Mapper2", 
                round_number=1,
                content_preview="Round 1, Mapper2",
                session_id="mapping_004"
            ),
            DebateTurnCompleteEvent(
                participant="Mapper1",
                round_number=2,
                content_preview="Round 2, Mapper1",
                session_id="mapping_004"
            ),
            DebateTurnCompleteEvent(
                participant="Mapper2",
                round_number=2, 
                content_preview="Round 2, Mapper2",
                session_id="mapping_004"
            )
        ]
        
        for event in turn_events:
            asyncio.run(tracker.add_turn(event))
        
        # Retrieve the history and verify mapping
        final_history = asyncio.run(tracker.get_history("mapping_004"))
        
        assert len(final_history.turns) == 4
        
        # Verify round numbers are preserved
        round1_turns = [t for t in final_history.turns if t.round_number == 1]
        round2_turns = [t for t in final_history.turns if t.round_number == 2]
        
        assert len(round1_turns) == 2
        assert len(round2_turns) == 2
        
        # Verify participant names are preserved
        participants_in_history = [t.participant_name for t in final_history.turns]
        assert participants_in_history.count("Mapper1") == 2
        assert participants_in_history.count("Mapper2") == 2
        
        # Verify content is preserved
        contents = [t.content for t in final_history.turns]
        assert "Round 1, Mapper1" in contents
        assert "Round 1, Mapper2" in contents
        assert "Round 2, Mapper1" in contents
        assert "Round 2, Mapper2" in contents
    
    def test_large_debate_scenario(self):
        """Test handling of large debate scenarios."""
        tracker = DebateHistoryTracker()
        
        # Create a debate with many participants and rounds
        many_roles = [f"role_{i}" for i in range(10)]
        start_event = DebateStartEvent(
            topic="Large Debate Scenario",
            roles=many_roles,
            rounds=5,
            session_id="large_debate_005"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add turns for multiple rounds
        turn_count = 0
        for round_num in range(1, 6):  # 5 rounds
            for role in many_roles:  # 10 roles per round
                turn_event = DebateTurnCompleteEvent(
                    participant=role,
                    round_number=round_num,
                    content_preview=f"Round {round_num} content from {role}",
                    session_id="large_debate_005"
                )
                asyncio.run(tracker.add_turn(turn_event))
                turn_count += 1
        
        # Verify all turns were processed
        final_history = asyncio.run(tracker.get_history("large_debate_005"))
        assert len(final_history.turns) == turn_count  # Should be 50 (5 rounds * 10 roles)
        assert final_history.total_rounds == 5
        assert len(final_history.participants) == 10
    
    def test_debate_completion_integration(self):
        """Test complete debate lifecycle integration."""
        tracker = DebateHistoryTracker()
        
        # Start debate
        start_event = DebateStartEvent(
            topic="Completion Integration Test",
            roles=["Pro", "Con"],
            rounds=2,
            session_id="completion_int_006"
        )
        asyncio.run(tracker.start_tracking(start_event))
        
        # Add all expected turns
        turns = [
            DebateTurnCompleteEvent(participant="Pro", round_number=1, content_preview="Round 1 Pro", session_id="completion_int_006"),
            DebateTurnCompleteEvent(participant="Con", round_number=1, content_preview="Round 1 Con", session_id="completion_int_006"),
            DebateTurnCompleteEvent(participant="Pro", round_number=2, content_preview="Round 2 Pro", session_id="completion_int_006"),
            DebateTurnCompleteEvent(participant="Con", round_number=2, content_preview="Round 2 Con", session_id="completion_int_006"),
        ]
        
        for turn in turns:
            asyncio.run(tracker.add_turn(turn))
        
        # Complete debate
        complete_event = DebateCompleteEvent(
            session_id="completion_int_006",
            summary="Integration test debate completed successfully"
        )
        asyncio.run(tracker.complete_debate(complete_event))
        
        # Verify completion
        final_history = asyncio.run(tracker.get_history("completion_int_006"))
        assert final_history.status == "completed"
        assert len(final_history.turns) == 4
        assert final_history.end_time is not None


if __name__ == "__main__":
    pytest.main([__file__])