import sys
sys.path.insert(0, 'src')

try:
    from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
    print("Import successful")
    
    # Just instantiate to check if constructor has issues
    tracker = DebateHistoryTracker()
    print("Instantiation successful")
    print("DB path:", tracker.db_path)
    
    import asyncio
    import inspect
    
    # Check method signatures
    methods = ['start_tracking', 'add_turn', 'complete_debate', 'get_history', 'get_all_histories', 'clear_history']
    print("\nMethod signatures:")
    for method in methods:
        if hasattr(tracker, method):
            meth = getattr(tracker, method)
            is_async = inspect.iscoroutinefunction(meth)
            print(f"  {method}: {'async' if is_async else 'sync'}")
        else:
            print(f"  {method}: MISSING")
    
    print("\n✅ BASIC VALIDATION PASSED")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()