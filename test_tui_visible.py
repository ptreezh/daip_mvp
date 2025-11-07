#!/usr/bin/env python3
"""
Simple script to test TUI startup with visible output.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tui_with_output():
    """Test TUI with visible output."""
    print("=" * 50)
    print("TUI STARTUP TEST")
    print("=" * 50)
    
    try:
        print("1. Importing required modules...")
        from daip_live.cli import app
        print("   ✅ Imports successful")
        
        print("2. Running CLI help command...")
        try:
            app(['--help'])
        except SystemExit:
            print("   ✅ Help command executed (SystemExit is normal)")
        
        print("\n3. Testing run command (will start TUI)...")
        print("   NOTE: If TUI starts successfully, you should see a Textual interface.")
        print("   If it exits immediately, there may be an initialization issue.")
        print("   You can press Ctrl+C to exit if needed.")
        print("-" * 50)
        
        try:
            # This will start the TUI
            app(['run'])
        except SystemExit:
            print("   ✅ Run command executed")
        except KeyboardInterrupt:
            print("   ⚠️  TUI interrupted by user")
        except Exception as e:
            print(f"   ❌ Error running TUI: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    print("=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
    return True

if __name__ == "__main__":
    test_tui_with_output()