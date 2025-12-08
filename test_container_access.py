#!/usr/bin/env python3
"""Test script to verify specific container service access as done in TUI"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_container_service_access():
    print("Testing container service access as done in TUI...")
    
    from daip_live.container import Container
    container = Container()
    
    print("Creating container instance...")
    
    # Test accessing services the same way TUI does
    try:
        print("Testing agent_executor access...")
        executor = container.agent_executor()
        print("✓ agent_executor accessible")
    except Exception as e:
        print(f"❌ agent_executor failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("Testing role_manager access...")
        role_manager = container.role_manager()
        print("✓ role_manager accessible")
    except Exception as e:
        print(f"❌ role_manager failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("Testing session_manager access...")
        session_manager = container.session_manager()
        print("✓ session_manager accessible")
    except Exception as e:
        print(f"❌ session_manager failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("Testing memory_service access...")
        memory_service = container.memory_service()
        print("✓ memory_service accessible")
    except Exception as e:
        print(f"❌ memory_service failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        print("Testing debate_manager access...")
        debate_manager = container.debate_manager()
        print("✓ debate_manager accessible")
    except Exception as e:
        print(f"❌ debate_manager failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_container_service_access()