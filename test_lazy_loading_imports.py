# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 19:00:00
@Author  : DAIP-LIVE Team
@File    : test_lazy_loading_imports.py
@Description:
    Test lazy loading imports to verify performance improvements.
"""

import sys
import time

def test_lazy_imports():
    """Test lazy loading imports"""
    print("Testing lazy loading imports...")
    
    # Test 1: Import basic enums and dataclasses
    start_time = time.time()
    try:
        from src.core_services.expert_consultation_scenario import ConsultationType, ConsultationPriority
        print("✅ Consultation enums import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ Consultation enums import failed: {e}")
        return False
    
    # Test 2: Import scenario classes without heavy dependencies
    start_time = time.time()
    try:
        from src.core_services.expert_consultation_scenario import ExpertConsultationScenario
        print("✅ ExpertConsultationScenario import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ ExpertConsultationScenario import failed: {e}")
        return False
    
    # Test 3: Import assessment engine classes
    start_time = time.time()
    try:
        from src.core_services.multidimensional_assessment_engine import (
            AssessmentDimension, QualityLevel, ContentType, 
            AssessmentCriteria, MetricResult, DimensionResult, 
            AssessmentResult, ContentToAssess, MultiDimensionalAssessmentEngine
        )
        print("✅ Assessment engine classes import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ Assessment engine classes import failed: {e}")
        return False
    
    # Test 4: Test instantiation with lazy loading
    start_time = time.time()
    try:
        # Test creating instances with None dependencies
        engine = MultiDimensionalAssessmentEngine(None, None, None)
        print("✅ MultiDimensionalAssessmentEngine instantiation successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ MultiDimensionalAssessmentEngine instantiation failed: {e}")
        return False
    
    # Test 5: Test scenario instantiation
    start_time = time.time()
    try:
        consultation_scenario = ExpertConsultationScenario()
        print("✅ ExpertConsultationScenario instantiation successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ ExpertConsultationScenario instantiation failed: {e}")
        return False
    
    print("🎉 All lazy loading imports successful!")
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = test_lazy_imports()
    end_time = time.time()
    
    print(f"\nLazy loading import test completed in {end_time - start_time:.2f} seconds")
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")