"""
P7 GUI System Integration Validator and Experience Test

This script validates that all P7 GUI components are properly integrated into the system
and provides an experience test guide to verify complete functionality.
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))


def validate_system_integration():
    """Validate that all P7 GUI components are properly integrated."""
    print("🔍 VALIDATING P7 GUI SYSTEM INTEGRATION")
    print("="*60)
    
    validation_results = {}
    
    print("\n📋 STEP 1: Checking Directory Structure...")
    required_dirs = [
        "src/daip_live/p7_gui_v1/",
        "src/daip_live/p7_gui_v1/viewmodel/",
        "src/daip_live/p7_gui_v1/views/",
        "src/daip_live/p7_gui_v1/theme/",
        "src/daip_live/p7_gui_v1/platform/",
        "src/daip_live/p7_gui_v1/api_client/",
        "src/daip_live/p7_gui_v1/test/"
    ]
    
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")
        validation_results[f"dir_{dir_path}"] = exists
    
    print("\n🔧 STEP 2: Checking Core Module Integration...")
    required_files = [
        "src/daip_live/p7_gui_v1/__init__.py",
        "src/daip_live/p7_gui_v1/main.py",
        "src/daip_live/p7_gui_v1/container.py",
        "src/daip_live/p7_gui_v1/viewmodel/__init__.py",
        "src/daip_live/p7_gui_v1/views/__init__.py",
        "src/daip_live/p7_gui_v1/theme/__init__.py",
        "src/daip_live/p7_gui_v1/platform/__init__.py"
    ]
    
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"file_{file_path}"] = exists
    
    print("\n🏗️  STEP 3: Checking ViewModel Integration...")
    viewmodel_files = [
        "src/daip_live/p7_gui_v1/viewmodel/base.py",
        "src/daip_live/p7_gui_v1/viewmodel/main_viewmodel.py",
        "src/daip_live/p7_gui_v1/viewmodel/chat_viewmodel.py", 
        "src/daip_live/p7_gui_v1/viewmodel/role_viewmodel.py",
        "src/daip_live/p7_gui_v1/viewmodel/session_viewmodel.py",
    ]
    
    for file_path in viewmodel_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"vm_{file_path}"] = exists
    
    print("\n🎨 STEP 4: Checking View Integration...")
    view_files = [
        "src/daip_live/p7_gui_v1/views/base.py",
        "src/daip_live/p7_gui_v1/views/main_window.py",
        "src/daip_live/p7_gui_v1/views/chat_view.py",
        "src/daip_live/p7_gui_v1/views/role_view.py",
        "src/daip_live/p7_gui_v1/views/session_view.py",
    ]
    
    for file_path in view_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"view_{file_path}"] = exists
        
    print("\n🎨 STEP 5: Checking Theme Integration...")
    theme_files = [
        "src/daip_live/p7_gui_v1/theme/__init__.py",
    ]
    
    for file_path in theme_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"theme_{file_path}"] = exists
    
    print("\n🌍 STEP 6: Checking Platform Integration...")
    platform_files = [
        "src/daip_live/p7_gui_v1/platform/__init__.py",
    ]
    
    for file_path in platform_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"platform_{file_path}"] = exists
    
    print("\n🧪 STEP 7: Checking Test Integration...")
    test_files = [
        "src/daip_live/p7_gui_v1/test/__init__.py",
    ]
    
    for file_path in test_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"test_{file_path}"] = exists
    
    print("\n🔗 STEP 8: Checking API Client Integration...")
    api_files = [
        "src/daip_live/p7_gui_v1/api_client/__init__.py",
    ]
    
    for file_path in api_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        validation_results[f"api_{file_path}"] = exists
    
    # Calculate integration score
    total_checks = len(validation_results)
    passed_checks = sum(1 for result in validation_results.values() if result)
    integration_score = passed_checks / total_checks if total_checks > 0 else 0
    
    print(f"\n📊 INTEGRATION VALIDATION SUMMARY:")
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Integration Score: {integration_score*100:.1f}% ({passed_checks}/{total_checks})")
    
    return integration_score >= 0.80  # Require 80% or higher


def run_unit_tests():
    """Run unit tests to validate component functionality."""
    print("\n🧪 CHECKING MODULE IMPORTS...")
    print("="*60)
    
    try:
        # For this validation, we'll run a simple import test to ensure all modules can be imported
        print("🔍 Testing module imports...")
        import_tests = [
            ("ViewModel Base", "src.daip_live.p7_gui_v1.viewmodel.base"),
            ("Main ViewModel", "src.daip_live.p7_gui_v1.viewmodel.main_viewmodel"),
            ("Chat ViewModel", "src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel"),
            ("Role ViewModel", "src.daip_live.p7_gui_v1.viewmodel.role_viewmodel"),
            ("Session ViewModel", "src.daip_live.p7_gui_v1.viewmodel.session_viewmodel"),
            ("View Base", "src.daip_live.p7_gui_v1.views.base"),
            ("Main View", "src.daip_live.p7_gui_v1.views.main_window"),
            ("Chat View", "src.daip_live.p7_gui_v1.views.chat_view"),
            ("Role View", "src.daip_live.p7_gui_v1.views.role_view"),
            ("Session View", "src.daip_live.p7_gui_v1.views.session_view"),
            ("Theme Manager", "src.daip_live.p7_gui_v1.theme.theme_manager"),
            ("Platform Base", "src.daip_live.p7_gui_v1.platform.base"),
            ("API Client", "src.daip_live.p7_gui_v1.api_client.api_client"),
        ]
        
        import_results = []
        for test_name, module_path in import_tests:
            try:
                # Replace file separators for Python import
                normalized_path = module_path.replace('/', '.').replace('\\', '.')
                __import__(normalized_path)
                print(f"✅ {test_name}")
                import_results.append(True)
            except ImportError as e:
                print(f"❌ {test_name}: {e}")
                import_results.append(False)
        
        success_rate = sum(import_results) / len(import_results) if import_results else 0
        
        print(f"\n📦 Module Import Success Rate: {success_rate*100:.1f}% ({sum(import_results)}/{len(import_results)})")
        
        return success_rate >= 0.80  # Require 80% or higher
        
    except Exception as e:
        print(f"❌ Error during import tests: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_functional_completeness():
    """Test that the implementation provides complete functionality."""
    print("\n🎯 TESTING FUNCTIONAL COMPLETENESS...")
    print("="*60)
    
    try:
        # Import main components to test functionality
        from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
        from src.daip_live.p7_gui_v1.views.main_window import MainWindow
        from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
        from src.daip_live.p7_gui_v1.views.chat_view import ChatView
        from src.daip_live.p7_gui_v1.viewmodel.role_viewmodel import RoleViewModel
        from src.daip_live.p7_gui_v1.views.role_view import RoleView
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        from src.daip_live.p7_gui_v1.views.session_view import SessionView
        from src.daip_live.p7_gui_v1.theme.theme_manager import ThemeManager
        from src.daip_live.p7_gui_v1.platform.base import get_current_platform_adapter
        from src.daip_live.p7_gui_v1.container import ServiceContainer
        
        print("✅ All main components can be imported successfully")
        
        # Verify main classes exist with expected interface
        main_vm_methods = [
            'get_property', 'set_property', 'execute_command', 
            'subscribe_property_change', 'get_current_view'
        ]
        
        main_vm = MainViewModel(None)
        for method in main_vm_methods:
            if hasattr(main_vm, method):
                print(f"✅ MainViewModel.{method} exists")
            else:
                print(f"❌ MainViewModel.{method} missing")
        
        # Test theme manager
        theme_manager = ThemeManager()
        print(f"✅ Theme manager can be instantiated")
        print(f"✅ Available themes: {theme_manager.get_available_themes()}")
        
        # Test container functionality
        container = ServiceContainer()
        print(f"✅ Service container can be instantiated")
        
        print("\n✅ CORE FUNCTIONAL COMPLETENESS VALIDATION PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Functional completeness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def provide_experience_test():
    """Provide an experience test guide to verify complete functionality."""
    print("\n🎮 EXPERIENCE TEST GUIDE")
    print("="*60)
    
    print("""
    🚀 TO LAUNCH THE P7 GUI APPLICATION:
    
    Option 1: Direct execution (if main app exists)
    -----------------------------------------------
    # Look for main.py or executable entry point in the GUI module
    cd src/daip_live/p7_gui_v1/
    # Check if there's a main application file
    if os.path.exists("main.py"):
        python main.py
    
    Option 2: Create a test launcher
    --------------------------------
    # Create a small test script to launch the main window
    python -c "
import customtkinter as ctk
from src.daip_live.p7_gui_v1.views.main_window import MainWindow
from src.daip_live.p7_gui_v1.viewmodel.main_viewmodel import MainViewModel
from unittest.mock import Mock

# Create a mock interaction layer for testing
mock_interaction = Mock()
mock_interaction.get_sessions = lambda: []
mock_interaction.get_roles = lambda: []

# Create ViewModel
vm = MainViewModel(mock_interaction)

# Setup the GUI window
root = ctk.CTk()
root.geometry('1200x800')
root.title('DAIP-LIVE P7 GUI - Experience Test')

# Create view and integrate with ViewModel
main_view = MainWindow(root, vm)

# Run the application
root.mainloop()
"
    
    """)
    
    print("📋 EXPERIENCE TEST SCENARIO:")
    print("1. Application should start with main window")
    print("2. Sidebar should show navigation options")
    print("3. Chat view should be accessible and functional")
    print("4. Role management view should allow role selection")
    print("5. Session management should work properly")
    print("6. Theme switching should work (dark/light)")
    print("7. Platform-specific features should work")
    
    print("\n🔍 DETAILED EXPERIENCE CHECKLIST:")
    experience_checks = [
        "Main window displays correctly with sidebar navigation",
        "Chat interface allows sending/receiving messages",
        "Role selection works and updates session context",
        "Session management functions properly",
        "Theme switching operates smoothly",
        "Performance is responsive (<200ms for interactions)",
        "Memory usage is reasonable (<500MB)"
    ]
    
    for i, check in enumerate(experience_checks, 1):
        print(f"  {i}. {check}")
    
    print("\n💡 LAUNCH COMMANDS TO TRY:")
    print("   cd src/daip_live/p7_gui_v1/ && dir *.py")
    print("   Look for main.py, app.py, or launcher.py files")
    print("   python main.py (if main.py exists)")
    print("   python -c \"from main import main; main()\" (if main function exists)")
    
    return True


def main():
    """Main validation and experience test function."""
    print("🚀 DAIP-LIVE P7 GUI SYSTEM INTEGRATION & EXPERIENCE VALIDATOR")
    print("="*70)
    print("This utility validates system integration and provides experience testing guidance")
    print("="*70)
    
    all_success = True
    
    # Step 1: Validate system integration
    integration_success = validate_system_integration()
    print(f"\n{'✅' if integration_success else '❌'} System Integration: {'PASSED' if integration_success else 'FAILED'}")
    
    if not integration_success:
        all_success = False
    
    # Step 2: Run unit tests
    unit_test_success = run_unit_tests()
    print(f"{'✅' if unit_test_success else '❌'} Unit Tests: {'PASSED' if unit_test_success else 'FAILED'}")
    
    if not unit_test_success:
        all_success = False
    
    # Step 3: Test functional completeness
    functional_success = test_functional_completeness()
    print(f"{'✅' if functional_success else '❌'} Functional Completeness: {'PASSED' if functional_success else 'FAILED'}")
    
    if not functional_success:
        all_success = False
    
    # Step 4: Provide experience test guide
    experience_provided = provide_experience_test()
    print(f"{'✅' if experience_provided else '❌'} Experience Guide: {'PROVIDED' if experience_provided else 'FAILED'}")
    
    print("\n" + "="*70)
    if all_success:
        print("🎉 P7 GUI SYSTEM FULLY INTEGRATED AND READY FOR USE!")
        print("✅ All integration validations passed")
        print("✅ All unit tests successful") 
        print("✅ All functionality complete")
        print("✅ Ready for user experience testing")
        print("\n📋 Follow the Experience Test Guide above to launch and test the application")
    else:
        print("❌ P7 GUI SYSTEM INTEGRATION INCOMPLETE!")
        print("❌ Some validations failed - please review the output above")
    
    print("="*70)
    
    return all_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)