#!/usr/bin/env python3
"""@Time    : 2025-08-05 16:20:00
@Author  : DAIP-LIVE Team
@File    : validate_ux_modules.py
@Description:
    Simple validation script to check UX enhancement modules exist and are properly structured.
"""

import sys
from pathlib import Path


def validate_module_structure():
    """Validate that all UX enhancement modules exist and have proper structure"""
    base_dir = Path(__file__).parent
    core_services_dir = base_dir / "src" / "core_services"
    
    # Required UX modules
    required_modules = [
        "import_health_checker.py",
        "user_friendly_errors.py", 
        "graceful_degradation.py",
        "startup_progress.py",
        "self_healing_system.py",
        "enhanced_app_state.py"
    ]
    
    print("🔍 Validating UX Enhancement Modules")
    print("=" * 50)
    
    all_valid = True
    
    for module_file in required_modules:
        module_path = core_services_dir / module_file
        
        if module_path.exists():
            print(f"✅ {module_file} - EXISTS")
            
            # Check if file has proper header
            with open(module_path, encoding='utf-8') as f:
                content = f.read()
                
            if '@Time' in content and '@Author' in content and '@Description' in content:
                print("   - Proper file header")
            else:
                print("   ⚠️  Missing or incomplete file header")
                all_valid = False
                
            # Check if file has proper class/function definitions
            if 'class ' in content or 'def ' in content:
                print("   - Contains class/function definitions")
            else:
                print("   ⚠️  No class/function definitions found")
                all_valid = False
                
        else:
            print(f"❌ {module_file} - MISSING")
            all_valid = False
    
    print("\n" + "=" * 50)
    
    if all_valid:
        print("🎉 All UX enhancement modules are properly structured!")
        return True
    else:
        print("❌ Some UX enhancement modules have issues!")
        return False

def validate_comprehensive_test():
    """Validate the comprehensive test script exists"""
    test_file = Path(__file__).parent / "comprehensive_ux_test.py"
    
    if test_file.exists():
        print("✅ comprehensive_ux_test.py - EXISTS")
        
        with open(test_file, encoding='utf-8') as f:
            content = f.read()
            
        # Check for key test functions
        test_functions = [
            "test_import_health_checker",
            "test_user_friendly_errors", 
            "test_graceful_degradation",
            "test_startup_progress",
            "test_self_healing_system",
            "test_enhanced_app_state"
        ]
        
        all_tests_present = True
        for test_func in test_functions:
            if f"def {test_func}" in content:
                print(f"   ✅ {test_func}")
            else:
                print(f"   ❌ {test_func} - MISSING")
                all_tests_present = False
        
        return all_tests_present
    else:
        print("❌ comprehensive_ux_test.py - MISSING")
        return False

def main():
    """Main validation function"""
    print("🧪 UX Enhancement Modules Validation")
    print("=" * 60)
    
    modules_valid = validate_module_structure()
    test_valid = validate_comprehensive_test()
    
    print("\n" + "=" * 60)
    
    if modules_valid and test_valid:
        print("🎉 All validations passed! UX enhancement system is ready.")
        return 0
    else:
        print("❌ Some validations failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())