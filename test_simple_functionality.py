import sys
import os
import tempfile
sys.path.insert(0, 'src')

print("Testing system functionality...")

# Simple import test
try:
    from daip_live.p8_debate_system.history_tracker import DebateHistoryTracker
    print("✓ DebateHistoryTracker imports successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create tracker with file-based database
temp_db = os.path.join(tempfile.gettempdir(), "test_debate_tracker.db")
try:
    tracker = DebateHistoryTracker(db_path=temp_db)
    print(f"✓ DebateHistoryTracker created with DB: {tracker.db_path}")
except Exception as e:
    print(f"❌ Creation error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if database file was created with tables
import sqlite3
try:
    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"✓ Database tables: {tables}")
    
    if 'debate_sessions' in tables and 'debate_turns' in tables:
        print("✓ Required debate tables exist in database")
    else:
        print(f"❌ Missing required tables. Expected: debate_sessions, debate_turns. Got: {tables}")
    
    conn.close()
    print("\\n🎉 DATABASE SETUP IS WORKING!")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)