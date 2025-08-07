# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 19:10:00
@Author  : DAIP-LIVE Team
@File    : test_basic_syntax.py
@Description:
    Test basic syntax and module structure.
"""

import sys
import traceback

def test_basic_syntax():
    """Test basic syntax of key files"""
    print("Testing basic syntax...")
    
    files_to_test = [
        "src/core_services/expert_consultation_scenario.py",
        "src/core_services/academic_research_scenario.py", 
        "src/core_services/industry_analysis_scenario.py",
        "src/core_services/multidimensional_assessment_engine.py",
        "src/core_services/collaborative_review_environment.py",
        "src/core_services/smart_reviewer_allocator_simple.py"
    ]
    
    for file_path in files_to_test:
        print(f"\nTesting {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, file_path, 'exec')
            print(f"✅ {file_path} - syntax OK")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - syntax error: {e}")
            return False
        except Exception as e:
            print(f"❌ {file_path} - error: {e}")
            return False
    
    print("\n🎉 All files have valid syntax!")
    return True

if __name__ == "__main__":
    success = test_basic_syntax()
    print(f"\nSyntax test result: {'SUCCESS' if success else 'FAILED'}")