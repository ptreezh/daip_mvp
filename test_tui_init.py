#!/usr/bin/env python3
"""Test script to verify TUI initialization works properly without running the full interface"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tui_initialization():
    print("Testing TUI initialization...")
    
    try:
        # Import and create TUI instance without running
        from daip_live.tui_modular import DAIP_TUI
        print("✓ TUI module imported successfully")
        
        # Create instance (this will trigger all the initialization logic)
        tui = DAIP_TUI()
        print("✓ TUI instance created successfully - no config_manager errors!")
        
        # Check if essential services are available
        if hasattr(tui, 'container') and tui.container:
            print("✓ Container is available")
        else:
            print("⚠ Container not available")
            
        if hasattr(tui, '_executor'):
            print("✓ Executor is available")
        else:
            print("⚠ Executor not available")
            
        if hasattr(tui, '_role_manager'):
            print("✓ Role manager is available")
        else:
            print("⚠ Role manager not available")
            
        if hasattr(tui, '_session_manager'):
            print("✓ Session manager is available")
        else:
            print("⚠ Session manager not available")
            
        if hasattr(tui, '_memory_service'):
            print("✓ Memory service is available")
        else:
            print("⚠ Memory service not available")
            
        if hasattr(tui, '_debate_manager'):
            print("✓ Debate manager is available")
        else:
            print("⚠ Debate manager not available")
        
        print("\n✓ TUI initialization test completed successfully - no config_manager errors!")
        
    except Exception as e:
        print(f"\n❌ Error during TUI initialization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tui_initialization()