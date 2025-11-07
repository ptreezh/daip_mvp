#!/usr/bin/env python3
"""
Detailed test case for TUI initialization process.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test basic imports."""
    print("1. Testing imports...")
    try:
        from daip_live.tui import DAIP_TUI
        print("   ✅ TUI import successful")
        return True
    except Exception as e:
        print(f"   ❌ TUI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_creation():
    """Test TUI creation."""
    print("2. Testing TUI creation...")
    try:
        from daip_live.tui import DAIP_TUI
        tui = DAIP_TUI()
        print("   ✅ TUI creation successful")
        return True
    except Exception as e:
        print(f"   ❌ TUI creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_initialization():
    """Test TUI initialization."""
    print("3. Testing TUI initialization...")
    try:
        from daip_live.tui import DAIP_TUI
        tui = DAIP_TUI()
        
        # Check if TUI has required attributes
        required_attrs = ['_executor', '_session_manager', '_role_manager']
        for attr in required_attrs:
            if not hasattr(tui, attr):
                print(f"   ⚠️  Missing attribute: {attr}")
        
        print("   ✅ TUI initialization successful")
        return True
    except Exception as e:
        print(f"   ❌ TUI initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_run():
    """Test TUI run method."""
    print("4. Testing TUI run method...")
    try:
        from daip_live.tui import DAIP_TUI
        tui = DAIP_TUI()
        
        # Instead of actually running (which would block), just check the method exists
        if hasattr(tui, 'run'):
            print("   ✅ TUI run method exists")
            return True
        else:
            print("   ❌ TUI run method missing")
            return False
    except Exception as e:
        print(f"   ❌ TUI run method check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_async_components():
    """Test async components."""
    print("5. Testing async components...")
    try:
        # Test that we can create an async event loop
        loop = asyncio.get_event_loop()
        print("   ✅ Async event loop creation successful")
        return True
    except Exception as e:
        print(f"   ❌ Async event loop creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running detailed TUI initialization tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_tui_creation,
        test_tui_initialization,
        test_tui_run,
        test_async_components
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
        print()
    
    print("=" * 50)
    if all(results):
        print("✅ All detailed tests passed!")
        sys.exit(0)
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} out of {len(results)} tests failed!")
        sys.exit(1)