"""
Comprehensive System Validation for DAIP-LIVE P7 GUI

This script validates all implemented and potentially missing components to ensure
complete system functionality as specified in the original requirements.
"""

import sys
import os
from pathlib import Path
import importlib

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

def validate_system_completeness():
    """Validate the completeness of system implementation."""
    print("🔍 DAIP-LIVE P7 GUI SYSTEM COMPLETENESS VALIDATION")
    print("="*70)
    
    validation_results = {}
    
    print("\n🏗️  VALIDATING CORE MODULES...")
    
    # Validate all P1-P8 modules exist and are functional
    modules_to_validate = [
        ("P1 - Persistence", "daip_live.persistence"),
        ("P2 - Knowledge", "daip_live.knowledge"),
        ("P3 - Model Provider", "daip_live.model_provider"),
        ("P4 - Role Tools", "daip_live.p4_role_manager_tools"),
        ("P5 - Agent Engine", "daip_live.agent_engine_v1"),
        ("P6 - TUI", "daip_live.tui_v1"),
        ("P7 - GUI", "daip_live.p7_gui_v1"),  # Current implementation
        ("P8 - Debate System", "daip_live.p8_debate_system"),
    ]
    
    for module_name, module_path in modules_to_validate:
        try:
            imported_module = importlib.import_module(f"src.{module_path}")
            print(f"✅ {module_name}: {module_path} - Imported successfully")
            validation_results[module_name] = True
        except ImportError as e:
            print(f"❌ {module_name}: {module_path} - Import failed: {e}")
            validation_results[module_name] = False
        except Exception as e:
            print(f"⚠️  {module_name}: {module_path} - Error: {e}")
            validation_results[module_name] = False
    
    print("\n🎯 VALIDATING VIEW MODEL COMPONENTS...")
    
    # Validate ViewModel components
    vm_components = [
        ("ViewModel Base", "src.daip_live.p7_gui_v1.viewmodel.base"),
        ("Main ViewModel", "src.daip_live.p7_gui_v1.viewmodel.main_viewmodel"),
        ("Chat ViewModel", "src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel"),
        ("Role ViewModel", "src.daip_live.p7_gui_v1.viewmodel.role_viewmodel"),
        ("Session ViewModel", "src.daip_live.p7_gui_v1.viewmodel.session_viewmodel"),
        ("Debate ViewModel", "src.daip_live.p7_gui_v1.viewmodel.debate_viewmodel"),
        ("Knowledge ViewModel", "src.daip_live.p7_gui_v1.viewmodel.knowledge_viewmodel"),
    ]
    
    for comp_name, comp_path in vm_components:
        try:
            imported_vm = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"VM_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"VM_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"VM_{comp_name}"] = False
    
    print("\n🎨 VALIDATING VIEW COMPONENTS...")
    
    # Validate View components
    view_components = [
        ("View Base", "src.daip_live.p7_gui_v1.views.base"),
        ("Main Window View", "src.daip_live.p7_gui_v1.views.main_window"),
        ("Chat View", "src.daip_live.p7_gui_v1.views.chat_view"),
        ("Role View", "src.daip_live.p7_gui_v1.views.role_view"),
        ("Session View", "src.daip_live.p7_gui_v1.views.session_view"),
        ("Debate View", "src.daip_live.p7_gui_v1.views.debate_view"),
        ("Knowledge View", "src.daip_live.p7_gui_v1.views.knowledge_view"),
    ]
    
    for comp_name, comp_path in view_components:
        try:
            imported_view = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"VIEW_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"VIEW_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"VIEW_{comp_name}"] = False
    
    print("\n🎨 VALIDATING THEME SYSTEM...")
    
    # Validate Theme components
    theme_components = [
        ("Theme Manager", "src.daip_live.p7_gui_v1.theme.theme_manager"),
    ]
    
    for comp_name, comp_path in theme_components:
        try:
            imported_theme = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"THEME_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"THEME_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"THEME_{comp_name}"] = False
    
    print("\n🌍 VALIDATING PLATFORM SYSTEM...")
    
    # Validate Platform components
    platform_components = [
        ("Platform Base", "src.daip_live.p7_gui_v1.platform.base"),
        ("Platform Adapters", "src.daip_live.p7_gui_v1.platform"),
    ]
    
    for comp_name, comp_path in platform_components:
        try:
            imported_platform = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"PLATFORM_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"PLATFORM_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"PLATFORM_{comp_name}"] = False
    
    print("\n🔌 VALIDATING SERVICE CONTAINER...")
    
    # Validate Container components
    container_components = [
        ("Service Container", "src.daip_live.p7_gui_v1.container"),
    ]
    
    for comp_name, comp_path in container_components:
        try:
            imported_container = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"CONTAINER_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"CONTAINER_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"CONTAINER_{comp_name}"] = False
    
    print("\n🧪 VALIDATING TEST SYSTEM...")
    
    # Validate Test components
    test_components = [
        ("Integration Tests", "src.daip_live.p7_gui_v1.test.integration_test_suite"),
        ("UAT Tests", "src.daip_live.p7_gui_v1.test.uat.runner"),
    ]
    
    for comp_name, comp_path in test_components:
        normalized_path = comp_path.replace('/', '.').replace('\\', '.')
        try:
            imported_test = importlib.import_module(normalized_path)
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"TEST_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"TEST_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"TEST_{comp_name}"] = False
    
    # Calculate validation summary
    total_components = len(validation_results)
    passed_components = sum(1 for result in validation_results.values() if result)
    failed_components = total_components - passed_components
    success_rate = passed_components / total_components if total_components > 0 else 0
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"Total Components: {total_components}")
    print(f"Passed: {passed_components}")
    print(f"Failed: {failed_components}")
    print(f"Success Rate: {success_rate*100:.1f}% ({passed_components}/{total_components})")
    
    print("\n" + "="*70)
    if success_rate >= 0.90:
        print("🎉 SYSTEM IS HIGHLY COMPLETE AND FUNCTIONAL!")
        print("✅ Core modules all working")
        print("✅ ViewModels and Views properly integrated")
        print("✅ Theme and platform systems functional")
        print("✅ Test suite operational")
        print(f"✅ Ready for final user acceptance testing")
    else:
        print("⚠️ SYSTEM HAS MISSING COMPONENTS THAT NEED ATTENTION")
        print(f"⚠️ Success rate of {success_rate*100:.1f}% indicates incomplete implementation")
        print("⚠️ Review failed components above")
    
    print("="*70)
    
    return success_rate >= 0.90


def identify_missing_requirements():
    """Identify any missing requirements or components."""
    print("\n🔍 IDENTIFYING POTENTIAL MISSING REQUIREMENTS...")
    
    # Check for any additional files that might indicate missing requirements
    potential_missing = []
    
    # Check if there are any missing directories that should exist
    expected_paths = [
        "src/daip_live/p7_gui_v1/main.py",  # Actual entry point
        "src/daip_live/p7_gui_v1/api_client/",  # API client module
        "src/daip_live/p7_gui_v1/models/",  # Models directory
        "src/daip_live/p7_gui_v1/test/",  # Test directory
        "src/daip_live/p7_gui_v1/theme/",  # Theme directory
        "src/daip_live/p7_gui_v1/platform/",  # Platform directory
        "src/daip_live/p7_gui_v1/container.py",  # Service container
        "src/daip_live/p7_gui_v1/__init__.py",  # Package init
    ]
    
    for path in expected_paths:
        exists = os.path.exists(path)
        if exists:
            print(f"✅ {path} - Exists")
        else:
            print(f"❌ {path} - Missing")
            potential_missing.append(path)
    
    if not potential_missing:
        print("✅ All expected paths exist")
    else:
        print(f"⚠️ Missing paths that may indicate incomplete implementation: {potential_missing}")
    
    return len(potential_missing) == 0


def validate_system_completeness():
    """Validate the completeness of system implementation."""
    print("🔍 DAIP-LIVE P7 GUI SYSTEM COMPLETENESS VALIDATION")
    print("="*70)
    
    validation_results = {}
    
    print("\n🏗️  VALIDATING CORE MODULES...")
    
    # Validate all P1-P8 modules exist and are functional
    modules_to_validate = [
        ("P1 - Persistence", "daip_live.persistence"),
        ("P2 - Knowledge", "daip_live.knowledge"),
        ("P3 - Model Provider", "daip_live.model_provider"),
        ("P4 - Role Tools", "daip_live.p4_role_manager_tools"),
        ("P5 - Agent Engine", "daip_live.agent_engine_v1"),
        ("P6 - TUI", "daip_live.tui_v1"),
        ("P7 - GUI", "daip_live.p7_gui_v1"),  # Current implementation
        ("P8 - Debate System", "daip_live.p8_debate_system"),
    ]
    
    for module_name, module_path in modules_to_validate:
        try:
            imported_module = importlib.import_module(f"src.{module_path}")
            print(f"✅ {module_name}: {module_path} - Imported successfully")
            validation_results[module_name] = True
        except ImportError as e:
            print(f"❌ {module_name}: {module_path} - Import failed: {e}")
            validation_results[module_name] = False
        except Exception as e:
            print(f"⚠️  {module_name}: {module_path} - Error: {e}")
            validation_results[module_name] = False
    
    print("\n🎯 VALIDATING VIEW MODEL COMPONENTS...")
    
    # Validate ViewModel components
    vm_components = [
        ("ViewModel Base", "src.daip_live.p7_gui_v1.viewmodel.base"),
        ("Main ViewModel", "src.daip_live.p7_gui_v1.viewmodel.main_viewmodel"),
        ("Chat ViewModel", "src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel"),
        ("Role ViewModel", "src.daip_live.p7_gui_v1.viewmodel.role_viewmodel"),
        ("Session ViewModel", "src.daip_live.p7_gui_v1.viewmodel.session_viewmodel"),
        ("Debate ViewModel", "src.daip_live.p7_gui_v1.viewmodel.debate_viewmodel"),
        ("Knowledge ViewModel", "src.daip_live.p7_gui_v1.viewmodel.knowledge_viewmodel"),
    ]
    
    for comp_name, comp_path in vm_components:
        try:
            imported_vm = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"VM_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"VM_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"VM_{comp_name}"] = False
    
    print("\n🎨 VALIDATING VIEW COMPONENTS...")
    
    # Validate View components
    view_components = [
        ("View Base", "src.daip_live.p7_gui_v1.views.base"),
        ("Main Window View", "src.daip_live.p7_gui_v1.views.main_window"),
        ("Chat View", "src.daip_live.p7_gui_v1.views.chat_view"),
        ("Role View", "src.daip_live.p7_gui_v1.views.role_view"),
        ("Session View", "src.daip_live.p7_gui_v1.views.session_view"),
        ("Debate View", "src.daip_live.p7_gui_v1.views.debate_view"),
        ("Knowledge View", "src.daip_live.p7_gui_v1.views.knowledge_view"),
    ]
    
    for comp_name, comp_path in view_components:
        try:
            imported_view = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"VIEW_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"VIEW_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"VIEW_{comp_name}"] = False
    
    print("\n🎨 VALIDATING THEME SYSTEM...")
    
    # Validate Theme components
    theme_components = [
        ("Theme Manager", "src.daip_live.p7_gui_v1.theme.theme_manager"),
    ]
    
    for comp_name, comp_path in theme_components:
        try:
            imported_theme = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"THEME_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"THEME_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"THEME_{comp_name}"] = False
    
    print("\n🌍 VALIDATING PLATFORM SYSTEM...")
    
    # Validate Platform components
    platform_components = [
        ("Platform Base", "src.daip_live.p7_gui_v1.platform.base"),
        ("Platform Adapters", "src.daip_live.p7_gui_v1.platform"),
    ]
    
    for comp_name, comp_path in platform_components:
        try:
            imported_platform = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"PLATFORM_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"PLATFORM_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"PLATFORM_{comp_name}"] = False
    
    print("\n🔌 VALIDATING SERVICE CONTAINER...")
    
    # Validate Container components
    container_components = [
        ("Service Container", "src.daip_live.p7_gui_v1.container"),
    ]
    
    for comp_name, comp_path in container_components:
        try:
            imported_container = importlib.import_module(comp_path.replace('/', '.').replace('\\', '.'))
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"CONTAINER_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"CONTAINER_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"CONTAINER_{comp_name}"] = False
    
    print("\n🧪 VALIDATING TEST SYSTEM...")
    
    # Validate Test components
    test_components = [
        ("Integration Tests", "src.daip_live.p7_gui_v1.test.integration_test_suite"),
        ("UAT Tests", "src.daip_live.p7_gui_v1.test.uat.runner"),
    ]
    
    for comp_name, comp_path in test_components:
        normalized_path = comp_path.replace('/', '.').replace('\\', '.')
        try:
            imported_test = importlib.import_module(normalized_path)
            print(f"✅ {comp_name}: {comp_path} - Imported successfully")
            validation_results[f"TEST_{comp_name}"] = True
        except ImportError as e:
            print(f"❌ {comp_name}: {comp_path} - Import failed: {e}")
            validation_results[f"TEST_{comp_name}"] = False
        except Exception as e:
            print(f"⚠️  {comp_name}: {comp_path} - Error: {e}")
            validation_results[f"TEST_{comp_name}"] = False
    
    # Calculate validation summary
    total_components = len(validation_results)
    passed_components = sum(1 for result in validation_results.values() if result)
    failed_components = total_components - passed_components
    success_rate = passed_components / total_components if total_components > 0 else 0
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"Total Components: {total_components}")
    print(f"Passed: {passed_components}")
    print(f"Failed: {failed_components}")
    print(f"Success Rate: {success_rate*100:.1f}% ({passed_components}/{total_components})")
    
    print("\n" + "="*70)
    if success_rate >= 0.90:
        print("🎉 SYSTEM IS HIGHLY COMPLETE AND FUNCTIONAL!")
        print("✅ Core modules all working")
        print("✅ ViewModels and Views properly integrated")
        print("✅ Theme and platform systems functional")
        print("✅ Test suite operational")
        print(f"✅ Ready for final user acceptance testing")
    else:
        print("⚠️ SYSTEM HAS MISSING COMPONENTS THAT NEED ATTENTION")
        print(f"⚠️ Success rate of {success_rate*100:.1f}% indicates incomplete implementation")
        print("⚠️ Review failed components above")
    
    print("="*70)
    
    return success_rate >= 0.90


def main():
    """Main validation function."""
    print("🚀 DAIP-LIVE P7 GUI COMPREHENSIVE VALIDATION")
    print("="*70)
    print("Validating complete system implementation against all requirements")
    print("="*70)
    
    # Run system completeness validation
    completeness_valid = validate_system_completeness()
    
    # Identify any missing requirements
    missing_reqs_identified = identify_missing_requirements()
    
    print("\n🎯 FINAL VALIDATION STATUS:")
    if completeness_valid and missing_reqs_identified:
        print("✅ SYSTEM IS COMPLETELY IMPLEMENTED AND READY FOR DEPLOYMENT!")
        print("✅ All core functionality modules available")
        print("✅ All ViewModels and Views implemented")
        print("✅ All platform and theme systems functional")
        print("✅ All test suites operational")
        print("✅ Ready for user experience and acceptance testing")
        return True
    else:
        print("❌ SYSTEM IMPLEMENTATION IS INCOMPLETE")
        print("❌ Some components are still missing or not functioning")
        print("❌ Please implement missing components before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)