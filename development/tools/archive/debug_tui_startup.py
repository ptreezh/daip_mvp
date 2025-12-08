#!/usr/bin/env python3
"""
Debug TUI startup to identify why it exits immediately.
"""

import sys
import os
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_tui_startup():
    """Debug TUI startup process."""
    print("Debugging TUI startup process...")
    print("=" * 50)
    
    # Step 1: Import TUI
    print("1. Importing TUI module...")
    try:
        from daip_live.tui import DAIP_TUI
        print("   ✅ Successfully imported DAIP_TUI")
    except Exception as e:
        print(f"   ❌ Failed to import DAIP_TUI: {e}")
        traceback.print_exc()
        return False

    # Step 2: Create TUI instance
    print("2. Creating TUI instance...")
    try:
        tui = DAIP_TUI()
        print("   ✅ Successfully created TUI instance")
    except Exception as e:
        print(f"   ❌ Failed to create TUI instance: {e}")
        traceback.print_exc()
        return False

    # Step 3: Try to run TUI (non-blocking way)
    print("3. Attempting to run TUI (non-blocking)...")
    try:
        # Check if TUI has the run method
        if hasattr(tui, 'run'):
            print("   ✅ TUI has run method")
            
            # Let's check what the run method looks like
            import inspect
            sig = inspect.signature(tui.run)
            print(f"   📋 TUI.run signature: {sig}")
        else:
            print("   ❌ TUI does not have run method")
            return False
    except Exception as e:
        print(f"   ❌ Error checking TUI run method: {e}")
        traceback.print_exc()
        return False

    # Step 4: Check if there are any initial exceptions during creation
    print("4. Checking for initial exceptions during initialization...")
    try:
        # Try to access some basic attributes that might trigger initialization
        attrs_to_check = ['_current_model', '_model_name', '_token_usage']
        for attr in attrs_to_check:
            if hasattr(tui, attr):
                val = getattr(tui, attr)
                print(f"   📋 {attr}: {val}")
            else:
                print(f"   ⚠️  {attr}: attribute not found")
    except Exception as e:
        print(f"   ❌ Error accessing TUI attributes: {e}")
        traceback.print_exc()
        return False

    print("5. TUI initialization completed successfully")
    print("=" * 50)
    print("✅ No immediate errors found in TUI startup process!")
    return True

def try_real_tui_launch():
    """Try to launch TUI in a way that allows debugging."""
    print("\nTrying to launch TUI in debug mode...")
    print("=" * 50)
    
    try:
        from daip_live.tui import DAIP_TUI
        import threading
        import time
        
        # Create TUI instance
        tui = DAIP_TUI()
        
        # Try to run in a separate thread with timeout
        def run_tui():
            try:
                print("   Starting TUI...")
                tui.run()
                print("   TUI stopped.")
            except Exception as e:
                print(f"   TUI error: {e}")
                import traceback
                traceback.print_exc()
        
        # Start TUI in thread
        tui_thread = threading.Thread(target=run_tui, daemon=True)
        tui_thread.start()
        
        # Wait for a short time to see if it's immediately exiting
        time.sleep(2)
        
        if tui_thread.is_alive():
            print("   ✅ TUI appears to be running in background")
        else:
            print("   ❌ TUI thread terminated quickly")
            
    except Exception as e:
        print(f"   ❌ Error launching TUI: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    success = debug_tui_startup()
    if success:
        try_real_tui_launch()
    else:
        print("❌ Debug failed")
        sys.exit(1)