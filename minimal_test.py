import sys
import asyncio
sys.path.insert(0, 'src')

from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
from daip_live.core.models import DebateStartEvent

async def test_simple_operation():
    tracker = DebateHistoryTracker()
    
    print("Creating test debate event...")
    start_event = DebateStartEvent(
        topic='Test',
        roles=['Pro', 'Con'],
        rounds=1,
        session_id='test_001'
    )
    
    print("Calling start_tracking...")
    try:
        history = await tracker.start_tracking(start_event)
        print(f"Success! Created history: {history.session_id}")
        print(f"Topic: {history.topic}")
        print(f"Participants: {len(history.participants)}")
        print("✅ OPERATION SUCCESSFUL")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

# Run the test
asyncio.run(test_simple_operation())