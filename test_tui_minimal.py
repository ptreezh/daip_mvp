#!/usr/bin/env python3
"""
Minimal test case for TUI functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test basic imports."""
    print("Testing imports...")
    try:
        from daip_live.tui import DAIP_TUI
        print("✅ TUI import successful")
        return True
    except Exception as e:
        print(f"❌ TUI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_creation():
    """Test TUI creation."""
    print("Testing TUI creation...")
    try:
        from daip_live.tui import DAIP_TUI
        tui = DAIP_TUI()
        print("✅ TUI creation successful")
        return True
    except Exception as e:
        print(f"❌ TUI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running minimal TUI tests...")
    print("=" * 40)
    
    if not test_imports():
        sys.exit(1)
        
    if not test_tui_creation():
        sys.exit(1)
        
    print("=" * 40)
    print("✅ All minimal tests passed!")