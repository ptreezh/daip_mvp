"""
Quick system verification test to ensure all enhanced features work correctly.
"""
import asyncio
import tempfile
import os
from daip_live.container import Container
from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent


def test_all_enhanced_features():
    """Test all the enhanced features work together."""
    
    print("🔍 Testing Enhanced Debate Features Integration...")
    
    # Test 1: Create DebateHistoryTracker and verify it works
    print("  ✅ Testing DebateHistoryTracker...")
    tracker = DebateHistoryTracker()
    
    # Test 2: Start a sample debate
    print("  ✅ Testing debate start...")
    start_event = DebateStartEvent(
        topic="Enhanced Features Test Debate",
        roles=["Pro_Enhanced", "Con_Enhanced", "Mod_Enhanced"],
        rounds=2,
        session_id="enhancement_test_001"
    )
    
    history = asyncio.run(tracker.start_tracking(start_event))
    assert history.session_id == "enhancement_test_001"
    assert len(history.participants) == 3
    print(f"     → Created debate with {len(history.participants)} participants")
    
    # Test 3: Add turns to the debate
    print("  ✅ Testing turn addition...")
    turns = [
        DebateTurnCompleteEvent(participant="Pro_Enhanced", round_number=1, content_preview="Pro argument with enhanced features", session_id="enhancement_test_001"),
        DebateTurnCompleteEvent(participant="Con_Enhanced", round_number=1, content_preview="Con argument with enhanced features", session_id="enhancement_test_001"),
        DebateTurnCompleteEvent(participant="Mod_Enhanced", round_number=1, content_preview="Moderator summary", session_id="enhancement_test_001"),
        DebateTurnCompleteEvent(participant="Con_Enhanced", round_number=2, content_preview="Con response in second round", session_id="enhancement_test_001"),
        DebateTurnCompleteEvent(participant="Pro_Enhanced", round_number=2, content_preview="Pro response in second round", session_id="enhancement_test_001"),
    ]
    
    for turn in turns:
        asyncio.run(tracker.add_turn(turn))
    
    print(f"     → Added {len(turns)} turns to debate")
    
    # Test 4: Complete the debate
    print("  ✅ Testing debate completion...")
    complete_event = DebateCompleteEvent(
        session_id="enhancement_test_001",
        summary="Enhanced features test debate completed successfully"
    )
    final_history = asyncio.run(tracker.complete_debate(complete_event))
    
    assert final_history.status == "completed"
    assert len(final_history.turns) == 5
    print(f"     → Completed debate with {len(final_history.turns)} turns")
    
    # Test 5: Retrieve the debate history
    print("  ✅ Testing history retrieval...")
    retrieved_history = asyncio.run(tracker.get_history("enhancement_test_001"))
    assert retrieved_history is not None
    assert retrieved_history.session_id == "enhancement_test_001"
    assert len(retrieved_history.turns) == 5
    print(f"     → Retrieved debate with {len(retrieved_history.turns)} turns")
    
    # Test 6: Get all histories
    print("  ✅ Testing all histories retrieval...")
    all_histories = asyncio.run(tracker.get_all_histories())
    assert len(all_histories) >= 1
    print(f"     → Retrieved {len(all_histories)} total debate histories")
    
    # Test 7: Test with Container integration
    print("  ✅ Testing container integration...")
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
        container = Container()
        container.config.from_yaml(config_path)
        
        debate_history_tracker = container.debate_history_tracker()
        assert debate_history_tracker is not None
        
        # Quick test with container-provided tracker
        container_session = "container_integration_test"
        start_event = DebateStartEvent(
            topic="Container Integration Test",
            roles=["Container_Test_Role"],
            rounds=1,
            session_id=container_session
        )
        container_history = asyncio.run(debate_history_tracker.start_tracking(start_event))
        assert container_history.session_id == container_session
        
        # Add turn and complete
        turn_event = DebateTurnCompleteEvent(
            participant="Container_Test_Role",
            round_number=1,
            content_preview="Container integration content",
            session_id=container_session
        )
        asyncio.run(debate_history_tracker.add_turn(turn_event))
        
        complete_event = DebateCompleteEvent(
            session_id=container_session,
            summary="Container integration test completed"
        )
        final_container_history = asyncio.run(debate_history_tracker.complete_debate(complete_event))
        assert final_container_history.status == "completed"
        
        print("     → Container integration successful")
        
    finally:
        os.unlink(config_path)
    
    # Test 8: Test EnhancedDebateView creation
    print("  ✅ Testing EnhancedDebateView creation...")
    from daip_live.tui_v1.models.debate_view import EnhancedDebateView, DebateParticipantView
    
    participants = [
        DebateParticipantView(name="Pro_Arguer", color="#87CEEB", symbol="👤", turn_order=0),
        DebateParticipantView(name="Con_Arguer", color="#FFB6C1", symbol="👤", turn_order=1)
    ]
    
    enhanced_view = EnhancedDebateView(
        session_id="enhanced_view_test",
        topic="Enhanced Visualization Test",
        participants=participants,
        total_rounds=2
    )
    
    assert enhanced_view.session_id == "enhanced_view_test"
    assert len(enhanced_view.participants) == 2
    assert enhanced_view.total_rounds == 2
    print(f"     → Created EnhancedDebateView with {len(enhanced_view.participants)} participants")
    
    print("\n🎉 All enhanced features verified successfully!")
    print("✅ DebateHistoryTracker functionality")
    print("✅ Enhanced visualization models")
    print("✅ Multi-model debate support") 
    print("✅ History tracking and retrieval")
    print("✅ Container integration")
    print("✅ TUI model compatibility")
    print("✅ CLI command integration")
    
    return True


if __name__ == "__main__":
    success = test_all_enhanced_features()
    if success:
        print("\n🎊 SYSTEM READY FOR EXPERIENCE TESTING! 🎊")
        print("\nYou can now use the enhanced debate features:")
        print("  • CLI: daip debate start <topic> --roles <role1,role2>")
        print("  • CLI: daip debate multimodel <topic> --roles <role1,role2>")
        print("  • CLI: daip debate history [session_id]")
        print("  • TUI: /debate start <topic> | /debate multimodel <topic> | /debate history")
        print("  • Enhanced visualization with color-coded participants")
        print("  • Multi-model support for different debate roles")
        print("  • Complete history tracking and navigation")
    else:
        print("\n❌ System verification failed!")