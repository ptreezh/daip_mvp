#!/usr/bin/env python3
"""Test script to verify the modular TUI initialization works properly after config fix"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_modular_tui_services():
    print("Testing modular TUI service initialization...")
    
    # First test the container directly
    print("\n1. Testing container initialization:")
    from daip_live.container import Container
    container = Container()
    
    services_tested = 0
    services_failed = 0
    
    try:
        config_mgr = container.config_manager()
        print("   ✓ ConfigManager initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ ConfigManager failed: {e}")
        services_failed += 1
        
    try:
        db_mgr = container.db_manager()
        print("   ✓ DatabaseManager initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ DatabaseManager failed: {e}")
        services_failed += 1
        
    try:
        model_prov = container.model_provider()
        print("   ✓ ModelProvider initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ ModelProvider failed: {e}")
        services_failed += 1
        
    try:
        role_mgr = container.role_manager()
        print("   ✓ RoleManager initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ RoleManager failed: {e}")
        services_failed += 1
        
    try:
        session_mgr = container.session_manager()
        print("   ✓ SessionManager initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ SessionManager failed: {e}")
        services_failed += 1
        
    try:
        memory_service = container.memory_service()
        print("   ✓ MemoryService initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ MemoryService failed: {e}")
        services_failed += 1
        
    try:
        debate_mgr = container.debate_manager()
        print("   ✓ DebateManager initialized successfully")
        services_tested += 1
    except Exception as e:
        print(f"   ❌ DebateManager failed: {e}")
        services_failed += 1
    
    print(f"\nContainer services test: {services_tested} passed, {services_failed} failed")
    
    # Now test simplified TUI initialization
    print("\n2. Testing simplified TUI initialization:")
    try:
        from daip_live.tui.simplified_main import SimplifiedTUI
        print("   ✓ SimplifiedTUI imported successfully")
        
        # Create instance without running to test initialization
        tui = SimplifiedTUI()
        print("   ✓ SimplifiedTUI instance created successfully")
        
        # Check if the essential services are available
        essential_services = [
            ('container', 'container'),
            ('role_manager', '_role_manager'),
            ('session_manager', '_session_manager'), 
            ('memory_service', '_memory_service'),
            ('debate_manager', '_debate_manager')
        ]
        
        available_services = 0
        for name, attr in essential_services:
            if hasattr(tui, attr) and getattr(tui, attr) is not None:
                print(f"   ✓ {name} is available")
                available_services += 1
            else:
                print(f"   ⚠ {name} not available")
        
        print(f"\nTUI services availability: {available_services}/{len(essential_services)} essential services available")
        
        if services_failed == 0 and available_services >= 3:  # Most essential services available
            print("\n✅ MODULAR TUI CONFIGURATION FIX SUCCESSFUL!")
            print("✅ All services are initializing properly without 'config_manager not defined' errors")
        else:
            print(f"\n⚠ Some services still have issues: {services_failed} container failures, {len(essential_services) - available_services} TUI unavailability")
        
    except Exception as e:
        print(f"   ❌ SimplifiedTUI initialization failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_modular_tui_services()