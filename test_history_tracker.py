import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent, DebateTurnCompleteEvent, DebateCompleteEvent

async def test_history_tracker():
    print("Testing DebateHistoryTracker...")
    tracker = DebateHistoryTracker()
    print("✓ Tracker created")

    # Create a test event
    start_evt = DebateStartEvent(
        topic='Test Topic',
        roles=['Pro_Arguer', 'Con_Arguer'],
        rounds=2,
        session_id='test_session_001'
    )
    
    print(f"Created start event: {start_evt.session_id}")
    
    # Try to start tracking
    try:
        history = await tracker.start_tracking(start_evt)
        print(f"✓ Started tracking: {history.session_id}, participants: {len(history.participants)}")
    except Exception as e:
        print(f"✗ Error in start_tracking: {e}")
        import traceback
        traceback.print_exc()
        return

    # Add a turn
    try:
        turn_evt = DebateTurnCompleteEvent(
            participant='Pro_Arguer',
            round_number=1,
            content_preview='This is a test argument.',
            session_id='test_session_001'
        )
        updated_history = await tracker.add_turn(turn_evt)
        print(f"✓ Added turn, now have {len(updated_history.turns)} turns")
    except Exception as e:
        print(f"✗ Error in add_turn: {e}")
        import traceback
        traceback.print_exc()
        return

    # Complete debate
    try:
        complete_evt = DebateCompleteEvent(
            session_id='test_session_001',
            summary='Test debate completed successfully.'
        )
        final_history = await tracker.complete_debate(complete_evt)
        print(f"✓ Completed debate: {final_history.status}")
    except Exception as e:
        print(f"✗ Error in complete_debate: {e}")
        import traceback
        traceback.print_exc()
        return

    # Retrieve history
    try:
        retrieved = await tracker.get_history('test_session_001')
        if retrieved:
            print(f"✓ Retrieved history: {retrieved.session_id}, status: {retrieved.status}, turns: {len(retrieved.turns)}")
        else:
            print("✗ Failed to retrieve history - got None")
    except Exception as e:
        print(f"✗ Error in get_history: {e}")
        import traceback
        traceback.print_exc()
        return

    # Get all histories
    try:
        all_histories = await tracker.get_all_histories()
        print(f"✓ Retrieved all histories: {len(all_histories)} total")
        for hist in all_histories:
            print(f"  - {hist.session_id}: {hist.status} with {len(hist.turns)} turns")
    except Exception as e:
        print(f"✗ Error in get_all_histories: {e}")
        import traceback
        traceback.print_exc()
        return

    print("All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_history_tracker())