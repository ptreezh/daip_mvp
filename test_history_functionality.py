"""
Test script to verify debate history tracking functionality
"""
import asyncio
import sys
import os
from pathlib import Path

# Add source path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from daip_live.container import Container
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent


def test_history_tracking():
    print("Testing debate history tracking functionality...")
    
    # Create container and get components
    container = Container()
    try:
        container.config.from_yaml("config.yaml")
    except:
        # If config file doesn't exist, use defaults
        from daip_live.config import AppConfig
        default_cfg = AppConfig(
            database={"path": ":memory:"},
            llm_provider={"default_model": "mock-model", "embedding_model": "mock-embedding"},
            knowledge_base={"directory": "./test_knowledge"},
            role_manager={"roles_dir": "./test_roles"}
        )
        container.config.from_value(default_cfg)
    
    # Get the debate history tracker
    debate_history_tracker = container.debate_history_tracker()
    print("✓ Got debate history tracker from container")
    
    # Create a test debate
    session_id = "test_history_tracking_001"
    start_event = DebateStartEvent(
        topic="History Tracking Test",
        roles=["Pro_Test", "Con_Test"],
        rounds=2,
        session_id=session_id
    )
    
    # Start tracking
    history = asyncio.run(debate_history_tracker.start_tracking(start_event))
    print(f"✓ Started tracking debate: {history.session_id}")
    
    # Add some turns
    turn1 = DebateTurnCompleteEvent(
        participant="Pro_Test",
        round_number=1,
        content_preview="Pro argument in test debate",
        session_id=session_id
    )
    updated_history = asyncio.run(debate_history_tracker.add_turn(turn1))
    print(f"✓ Added turn 1, now have {len(updated_history.turns)} turns")
    
    turn2 = DebateTurnCompleteEvent(
        participant="Con_Test", 
        round_number=1,
        content_preview="Con argument in test debate",
        session_id=session_id
    )
    updated_history = asyncio.run(debate_history_tracker.add_turn(turn2))
    print(f"✓ Added turn 2, now have {len(updated_history.turns)} turns")
    
    # Complete debate
    complete_event = DebateCompleteEvent(
        session_id=session_id,
        summary="History tracking test debate completed successfully"
    )
    final_history = asyncio.run(debate_history_tracker.complete_debate(complete_event))
    print(f"✓ Completed debate: {final_history.status}")
    
    # Try to retrieve the specific history
    retrieved_history = asyncio.run(debate_history_tracker.get_history(session_id))
    if retrieved_history:
        print(f"✓ Retrieved specific history: {retrieved_history.session_id}")
        print(f"  - Topic: {retrieved_history.topic}")
        print(f"  - Status: {retrieved_history.status}")
        print(f"  - Turns: {len(retrieved_history.turns)}")
        print(f"  - Participants: {len(retrieved_history.participants)}")
    else:
        print("✗ Failed to retrieve specific history")
        return False
    
    # Get all histories
    all_histories = asyncio.run(debate_history_tracker.get_all_histories())
    print(f"✓ Retrieved all histories: {len(all_histories)} total")
    
    # Verify our test debate is in the list
    found_test_debate = any(h.session_id == session_id for h in all_histories)
    if found_test_debate:
        print(f"✓ Test debate found in all histories list")
    else:
        print(f"✗ Test debate NOT found in all histories list")
        return False
    
    # Test clearing history
    clear_success = asyncio.run(debate_history_tracker.clear_history(session_id))
    if clear_success:
        print(f"✓ Successfully cleared history for {session_id}")
    else:
        print(f"✗ Failed to clear history for {session_id}")
    
    # Verify it's gone
    cleared_history = asyncio.run(debate_history_tracker.get_history(session_id))
    if cleared_history is None:
        print(f"✓ History properly cleared - no longer retrievable")
    else:
        print(f"✗ History still exists after clear")
        return False
    
    print("\n🎉 All history tracking tests passed!")
    return True


if __name__ == "__main__":
    success = test_history_tracking()
    if success:
        print("\n✓ HISTORY TRACKING FUNCTIONALITY IS WORKING PROPERLY!")
    else:
        print("\n❌ HISTORY TRACKING HAS ISSUES!")
        sys.exit(1)