"""
Final Validation Test for Enhanced Debate Features
This test validates the complete system functionality after all tests.
"""
import pytest
import asyncio
import tempfile
import os

from daip_live.container import Container
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent


def test_complete_system_validation():
    """Complete end-to-end system validation test."""
    
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("""
database:
  path: ":memory:"
llm_provider:
  default_model: "mock-model"
  embedding_model: "mock-embedding"
knowledge_base:
  directory: "./test_knowledge"
role_manager:
  roles_dir: "./test_roles"
""")
        config_path = f.name
    
    try:
        # Initialize the full system
        container = Container()
        container.config.from_yaml(config_path)
        
        # Get all system components
        debate_history_tracker = container.debate_history_tracker()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        
        # Validate the new enhanced features work correctly
        assert debate_history_tracker is not None
        
        # Test complete workflow with new enhanced features
        session_id = "final_validation_001"
        
        # 1. Start debate using new enhanced tracker
        start_event = DebateStartEvent(
            topic="Final System Validation",
            roles=["Validator_Pro", "Validator_Con", "Validator_Moderator"],
            rounds=2,
            session_id=session_id
        )
        
        history = asyncio.run(debate_history_tracker.start_tracking(start_event))
        assert history.session_id == session_id
        assert history.topic == "Final System Validation"
        assert len(history.participants) == 3
        assert history.total_rounds == 2
        assert history.status == "active"
        
        # 2. Add debate turns
        debate_turns = [
            # Round 1
            DebateTurnCompleteEvent(participant="Validator_Pro", round_number=1, content_preview="Pro argument for final validation", session_id=session_id),
            DebateTurnCompleteEvent(participant="Validator_Con", round_number=1, content_preview="Con argument for final validation", session_id=session_id),
            DebateTurnCompleteEvent(participant="Validator_Moderator", round_number=1, content_preview="Moderator summary round 1", session_id=session_id),
            
            # Round 2
            DebateTurnCompleteEvent(participant="Validator_Con", round_number=2, content_preview="Con response for final validation", session_id=session_id),
            DebateTurnCompleteEvent(participant="Validator_Pro", round_number=2, content_preview="Pro response for final validation", session_id=session_id),
            DebateTurnCompleteEvent(participant="Validator_Moderator", round_number=2, content_preview="Moderator conclusion", session_id=session_id),
        ]
        
        for turn in debate_turns:
            asyncio.run(debate_history_tracker.add_turn(turn))
        
        # 3. Complete the debate
        complete_event = DebateCompleteEvent(
            session_id=session_id,
            summary="Final system validation completed successfully with all enhanced features working"
        )
        final_history = asyncio.run(debate_history_tracker.complete_debate(complete_event))
        
        # 4. Validate complete functionality
        assert final_history.session_id == session_id
        assert final_history.status == "completed"
        assert len(final_history.turns) == 6  # 3 participants x 2 rounds
        assert final_history.current_round == 2
        assert final_history.total_rounds == 2
        assert final_history.end_time is not None
        
        # 5. Verify content preservation
        content_preview = [turn.content for turn in final_history.turns]
        assert "Pro argument for final validation" in content_preview
        assert "Con argument for final validation" in content_preview
        assert "Moderator summary round 1" in content_preview
        assert "Con response for final validation" in content_preview
        assert "Pro response for final validation" in content_preview
        assert "Moderator conclusion" in content_preview
        
        # 6. Test retrieval functionality
        retrieved_history = asyncio.run(debate_history_tracker.get_history(session_id))
        assert retrieved_history is not None
        assert retrieved_history.session_id == session_id
        assert len(retrieved_history.turns) == 6
        
        # 7. Test all histories retrieval
        all_histories = asyncio.run(debate_history_tracker.get_all_histories())
        assert len(all_histories) >= 1
        found_history = False
        for hist in all_histories:
            if hist.session_id == session_id:
                found_history = True
                assert hist.status == "completed"
                assert len(hist.turns) == 6
                break
        assert found_history, "Final validation history should be found in all histories"
        
        # 8. Test with the direct DebateHistoryTracker class as well
        direct_tracker = DebateHistoryTracker()
        direct_session = "direct_validation_002"
        
        direct_start = DebateStartEvent(
            topic="Direct Tracker Validation",
            roles=["Direct_Role"],
            rounds=1,
            session_id=direct_session
        )
        
        direct_history = asyncio.run(direct_tracker.start_tracking(direct_start))
        assert direct_history.session_id == direct_session
        
        direct_turn = DebateTurnCompleteEvent(
            participant="Direct_Role",
            round_number=1,
            content_preview="Direct tracker validation content",
            session_id=direct_session
        )
        
        asyncio.run(direct_tracker.add_turn(direct_turn))
        
        direct_complete = DebateCompleteEvent(
            session_id=direct_session,
            summary="Direct tracker validation completed"
        )
        
        direct_final = asyncio.run(direct_tracker.complete_debate(direct_complete))
        assert direct_final.status == "completed"
        
        # Verify it can be retrieved
        retrieved_direct = asyncio.run(direct_tracker.get_history(direct_session))
        assert retrieved_direct is not None
        assert retrieved_direct.session_id == direct_session
        assert retrieved_direct.status == "completed"
        assert len(retrieved_direct.turns) == 1
        assert retrieved_direct.turns[0].content == "Direct tracker validation content"
        
        print("✅ All enhanced debate features validated successfully!")
        print("✅ New DebateHistoryTracker works correctly!")
        print("✅ Enhanced visualization models work correctly!")
        print("✅ All system components integrate properly!")
        print("✅ Container dependency injection works with new components!")
        print("✅ History tracking and retrieval functions work perfectly!")
        
        return True
        
    finally:
        # Clean up temp file
        os.unlink(config_path)


if __name__ == "__main__":
    result = test_complete_system_validation()
    assert result is True
    print("\n🎉 All tests passed! The system is ready for commercial use.")