#!/usr/bin/env python3
"""
Test script to validate all critical imports work correctly
"""

import sys
import time
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_import(module_name):
    """Test importing a module and return success status"""
    try:
        start = time.time()
        __import__(module_name)
        duration = time.time() - start
        print(f"PASS {module_name} ({duration:.2f}s)")
        return True, duration
    except Exception as e:
        print(f"FAIL {module_name} - {e}")
        traceback.print_exc()
        return False, 0

def test_critical_imports():
    """Test all critical imports for application startup"""
    print("Testing critical imports...")
    print("=" * 60)
    
    critical_imports = [
        'src.config',
        'src.app_state',
        'src.main',
        'src.kernel.llm_interface',
        'src.core_services.role_manager',
        'src.core_services.memory_service',
        'src.core_services.wiki_service',
        'src.core_services.synthesis_engine',
        'src.core_services.scenario_integration_service',
        'src.core_services.expert_consultation_scenario',
        'src.api.dependencies',
        'src.protocols.consensus_strategies',
        'src.models',
        'src.composition'
    ]
    
    failed = []
    import_times = {}
    
    for module in critical_imports:
        success, duration = test_import(module)
        if success:
            import_times[module] = duration
        else:
            failed.append(module)
    
    print("\n" + "=" * 60)
    print("CRITICAL IMPORTS SUMMARY")
    print("=" * 60)
    print(f"Total modules tested: {len(critical_imports)}")
    print(f"Successful imports: {len(critical_imports) - len(failed)}")
    print(f"Failed imports: {len(failed)}")
    
    if failed:
        print(f"\nFAILED IMPORTS:")
        for module in failed:
            print(f"   - {module}")
        return False
    
    print(f"\nALL CRITICAL IMPORTS SUCCESSFUL!")
    
    # Performance summary
    total_time = sum(import_times.values())
    avg_time = total_time / len(import_times)
    slowest = max(import_times.items(), key=lambda x: x[1])
    
    print(f"\nPERFORMANCE SUMMARY:")
    print(f"   Total import time: {total_time:.2f}s")
    print(f"   Average import time: {avg_time:.2f}s")
    print(f"   Slowest module: {slowest[0]} ({slowest[1]:.2f}s)")
    
    return True

def test_service_initialization():
    """Test that key services can be initialized"""
    print("\n" + "=" * 60)
    print("TESTING SERVICE INITIALIZATION")
    print("=" * 60)
    
    try:
        # Test AppState initialization (this tests all service imports)
        print("Testing AppState initialization...")
        start = time.time()
        
        from src.app_state import AppState
        app_state = AppState()
        
        duration = time.time() - start
        print(f"OK AppState initialized successfully ({duration:.2f}s)")
        
        # Test specific services
        services_to_test = [
            ('llm_interface', 'LLM Interface'),
            ('memory_service', 'Memory Service'),
            ('wiki_service', 'Wiki Service'),
            ('synthesis_engine', 'Synthesis Engine'),
            ('role_manager', 'Role Manager'),
            ('token_management_service', 'Token Management Service'),
            ('unified_tool_manager', 'Unified Tool Manager')
        ]
        
        for attr_name, display_name in services_to_test:
            try:
                service = getattr(app_state, attr_name, None)
                if service is not None:
                    print(f"OK {display_name}: Available")
                else:
                    print(f"WARN {display_name}: Not initialized")
            except Exception as e:
                print(f"FAIL {display_name}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"FAIL Service initialization failed: {e}")
        traceback.print_exc()
        return False

def test_scenario_services():
    """Test scenario service imports and initialization"""
    print("\n" + "=" * 60)
    print("TESTING SCENARIO SERVICES")
    print("=" * 60)
    
    try:
        from src.core_services.scenario_integration_service import ScenarioIntegrationService
        
        print("Testing ScenarioIntegrationService initialization...")
        start = time.time()
        
        service = ScenarioIntegrationService()
        
        duration = time.time() - start
        print(f"OK ScenarioIntegrationService initialized successfully ({duration:.2f}s)")
        
        # Test individual scenario access
        scenarios = [
            ('expert_scenario', 'Expert Consultation'),
            ('academic_scenario', 'Academic Research'),
            ('industry_scenario', 'Industry Analysis')
        ]
        
        for attr_name, display_name in scenarios:
            try:
                scenario = getattr(service, attr_name, None)
                if scenario is not None:
                    print(f"OK {display_name} Scenario: Available")
                else:
                    print(f"WARN {display_name} Scenario: Not initialized")
            except Exception as e:
                print(f"FAIL {display_name} Scenario: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"FAIL Scenario service initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("DAIP-LIVE IMPORT VALIDATION")
    print("Testing all critical imports and service initialization")
    print("This test ensures the application can start successfully.")
    print()
    
    overall_success = True
    
    # Test 1: Critical imports
    if not test_critical_imports():
        overall_success = False
    
    # Test 2: Service initialization
    if not test_service_initialization():
        overall_success = False
    
    # Test 3: Scenario services
    if not test_scenario_services():
        overall_success = False
    
    # Final result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    
    if overall_success:
        print("SUCCESS: ALL TESTS PASSED!")
        print("The application should start successfully.")
        print("\nNext steps:")
        print("1. Run: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. Test the API endpoints")
        print("3. Verify all services are working correctly")
        return 0
    else:
        print("FAILURE: SOME TESTS FAILED!")
        print("Please fix the failed imports before starting the application.")
        print("\nTroubleshooting:")
        print("1. Check missing dependencies: pip install -e .")
        print("2. Verify all required files exist")
        print("3. Check for circular dependencies")
        print("4. Review the error messages above")
        return 1

if __name__ == "__main__":
    sys.exit(main())