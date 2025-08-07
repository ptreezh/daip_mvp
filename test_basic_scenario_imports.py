# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 18:40:00
@Author  : DAIP-LIVE Team
@File    : test_basic_scenario_imports.py
@Description:
    Test basic scenario imports without multidimensional assessment engine.
"""

import sys
import time

def test_basic_imports():
    """Test basic scenario imports"""
    print("Testing basic scenario imports...")
    
    # Test basic enum import
    start_time = time.time()
    try:
        from src.core_services.expert_consultation_scenario import ConsultationType
        print("✅ ConsultationType import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ ConsultationType import failed: {e}")
        return False
    
    # Test smart reviewer allocator
    start_time = time.time()
    try:
        from src.core_services.smart_reviewer_allocator_simple import SmartReviewerAllocator
        print("✅ SmartReviewerAllocator import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ SmartReviewerAllocator import failed: {e}")
        return False
    
    # Test collaborative review environment
    start_time = time.time()
    try:
        from src.core_services.collaborative_review_environment import CollaborativeReviewEnvironment
        print("✅ CollaborativeReviewEnvironment import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ CollaborativeReviewEnvironment import failed: {e}")
        return False
    
    print("🎉 All basic imports successful!")
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = test_basic_imports()
    end_time = time.time()
    
    print(f"\nBasic imports test completed in {end_time - start_time:.2f} seconds")
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")