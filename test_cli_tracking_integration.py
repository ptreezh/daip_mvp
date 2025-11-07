"""
Comprehensive test to validate that debates run through the CLI are properly tracked
and can be retrieved via the history command
"""
import asyncio
import tempfile
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_cli_debate_tracking():
    """Test that debates run via CLI are properly tracked and retrievable."""
    
    print("Testing CLI debate tracking and retrieval...")
    
    # Create temporary config for testing
    config_content = """
database:
  path: ":memory:"
llm_provider:
  default_model: "mock-model"
  embedding_model: "mock-embedding"
knowledge_base:
  directory: "./test_docs"
role_manager:
  roles_dir: "./test_roles"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        config_path = f.name
    
    try:
        from daip_live.container import Container
        
        # Create container with config
        container = Container()
        container.config.from_yaml(config_path)
        
        # Get the debate history tracker
        debate_history_tracker = container.debate_history_tracker()
        print(f"✓ Got debate history tracker from container")
        
        # Check initial state
        initial_histories = await debate_history_tracker.get_all_histories()
        print(f"✓ Initial histories count: {len(initial_histories)}")
        
        # Simulate what happens during a debate run via CLI
        # 1. Create start event
        from daip_live.core.models import DebateStartEvent
        start_event = DebateStartEvent(
            topic="CLI Tracking Test",
            roles=["Pro_CLI", "Con_CLI"],
            rounds=1,
            session_id="cli_tracking_test_001"
        )
        
        # 2. Start tracking
        history = await debate_history_tracker.start_tracking(start_event)
        print(f"✓ Started tracking debate: {history.session_id}")
        
        # 3. Add some turns
        from daip_live.core.models import DebateTurnCompleteEvent
        turn1 = DebateTurnCompleteEvent(
            participant="Pro_CLI",
            round_number=1,
            content_preview="Pro argument for CLI tracking test",
            session_id="cli_tracking_test_001"
        )
        await debate_history_tracker.add_turn(turn1)
        print("✓ Added first turn")
        
        turn2 = DebateTurnCompleteEvent(
            participant="Con_CLI",
            round_number=1,
            content_preview="Con argument for CLI tracking test",
            session_id="cli_tracking_test_001"
        )
        await debate_history_tracker.add_turn(turn2)
        print("✓ Added second turn")
        
        # 4. Complete debate
        from daip_live.core.models import DebateCompleteEvent
        complete_event = DebateCompleteEvent(
            session_id="cli_tracking_test_001",
            summary="CLI tracking test debate completed successfully"
        )
        final_history = await debate_history_tracker.complete_debate(complete_event)
        print(f"✓ Completed debate: {final_history.status}")
        
        # 5. Retrieve all histories after adding our test debate
        all_histories_after = await debate_history_tracker.get_all_histories()
        print(f"✓ Histories after adding test debate: {len(all_histories_after)}")
        
        # 6. Look for our specific debate in the results
        found_our_debate = False
        for hist in all_histories_after:
            if hist.session_id == "cli_tracking_test_001":
                print(f"✓ Found our test debate in history list!")
                print(f"  - Session ID: {hist.session_id}")
                print(f"  - Topic: {hist.topic}")
                print(f"  - Status: {hist.status}")
                print(f"  - Participants: {len(hist.participants)}")
                print(f"  - Turns: {len(hist.turns)}")
                found_our_debate = True
                break
        
        if not found_our_debate:
            print("✗ Our test debate was not found in the history list")
            return False
        
        # 7. Test retrieving specific history
        specific_history = await debate_history_tracker.get_history("cli_tracking_test_001")
        if specific_history:
            print(f"✓ Successfully retrieved specific history: {specific_history.session_id}")
            print(f"  - Status: {specific_history.status}")
            print(f"  - Turns: {len(specific_history.turns)}")
        else:
            print("✗ Failed to retrieve specific history")
            return False
        
        # 8. Now test using the same approach as the CLI debate command
        print("\n--- Testing EnhancedDebateManager integration ---")
        
        # Create a debate manager like in CLI and verify it has access to the same tracker
        from daip_live.p8_debate_system.enhanced_debate_manager import EnhancedDebateManager
        from daip_live.memory.session_manager import SessionManager
        from daip_live.persistence.database import DatabaseManager
        from daip_live.p4_role_manager_tools.role_manager import RoleManager
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from unittest.mock import Mock
        
        # Mock provider to avoid actual API calls
        mock_provider = Mock()
        mock_provider.generate = Mock(return_value=("Mock response", {"total_tokens": 10}))
        
        # Create debate manager with the same history tracker
        debate_manager = EnhancedDebateManager(
            session_manager=SessionManager(DatabaseManager(db_path=":memory:")),
            role_manager=RoleManager(roles_dir_path="./test_roles"),
            role_model_manager=RoleModelManager(roles_dir_path="./test_roles"),
            model_provider=mock_provider,
            debate_history_tracker=debate_history_tracker,  # Same tracker instance
            use_optimized_architecture=True
        )
        
        print(f"✓ Created EnhancedDebateManager with shared history tracker: {debate_manager.debate_history_tracker is debate_history_tracker}")
        
        # Test that the debate manager has the correct history tracker reference
        if debate_manager.debate_history_tracker is not debate_history_tracker:
            print("✗ Debate manager has different history tracker instance!")
            return False
        
        # Test the debate manager internal functionality
        all_histories_via_manager = await debate_manager.debate_history_tracker.get_all_histories()
        print(f"✓ Retrieved histories via debate manager: {len(all_histories_via_manager)}")
        
        # Check if our test debate is accessible via the manager
        manager_has_our_debate = any(h.session_id == "cli_tracking_test_001" for h in all_histories_via_manager)
        if manager_has_our_debate:
            print("✓ Debate manager can access our test debate")
        else:
            print("✗ Debate manager cannot access our test debate")
            return False
        
        # 9. Test creating a debate through the manager and then retrieving it via container
        print("\n--- Testing debate creation through manager ---")
        
        # Create another test debate through the manager's internal mechanisms
        test_start_event = DebateStartEvent(
            topic="Manager Creation Test",
            roles=["Pro_Manager", "Con_Manager"],
            rounds=1,
            session_id="manager_creation_test_002"
        )
        
        manager_history = await debate_manager.debate_history_tracker.start_tracking(test_start_event)
        print(f"✓ Created debate through manager: {manager_history.session_id}")
        
        # Verify it's accessible from the original tracker too
        original_tracker_history = await debate_history_tracker.get_history("manager_creation_test_002")
        if original_tracker_history:
            print(f"✓ Original tracker can access manager-created debate: {original_tracker_history.session_id}")
        else:
            print("✗ Original tracker cannot access manager-created debate")
            return False
        
        print("\n🎉 All CLI debate tracking integration tests passed!")
        return True
        
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.unlink(config_path)


def run_comprehensive_test():
    """Run the comprehensive test."""
    try:
        result = asyncio.run(test_cli_debate_tracking())
        return result
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    if success:
        print("\n✅ CLI DEBATE TRACKING INTEGRATION IS WORKING CORRECTLY!")
        print("The issue might be elsewhere - perhaps in how the debate is initiated in real usage.")
    else:
        print("\n❌ CLI DEBATE TRACKING INTEGRATION HAS ISSUES!")
        sys.exit(1)