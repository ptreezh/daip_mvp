# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 18:00:00
@Author  : DAIP-LIVE Team
@File    : test_minimal_imports.py
@Description:
    Test minimal imports to identify import issues.
"""

import sys
import time

def test_import():
    """Test importing core modules"""
    print("Testing minimal imports...")
    
    # Test basic enum import
    try:
        from src.core_services.expert_consultation_scenario import ConsultationType
        print("✅ ConsultationType import successful")
    except Exception as e:
        print(f"❌ ConsultationType import failed: {e}")
        return False
    
    # Test basic scenario import
    try:
        from src.core_services.expert_consultation_scenario import ExpertConsultationScenario
        print("✅ ExpertConsultationScenario import successful")
    except Exception as e:
        print(f"❌ ExpertConsultationScenario import failed: {e}")
        return False
    
    # Test academic scenario import
    try:
        from src.core_services.academic_research_scenario import AcademicResearchScenario
        print("✅ AcademicResearchScenario import successful")
    except Exception as e:
        print(f"❌ AcademicResearchScenario import failed: {e}")
        return False
    
    # Test industry scenario import
    try:
        from src.core_services.industry_analysis_scenario import IndustryAnalysisScenario
        print("✅ IndustryAnalysisScenario import successful")
    except Exception as e:
        print(f"❌ IndustryAnalysisScenario import failed: {e}")
        return False
    
    # Test integration service import
    try:
        from src.core_services.scenario_integration_service import ScenarioIntegrationService
        print("✅ ScenarioIntegrationService import successful")
    except Exception as e:
        print(f"❌ ScenarioIntegrationService import failed: {e}")
        return False
    
    print("🎉 All imports successful!")
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = test_import()
    end_time = time.time()
    
    print(f"\nImport test completed in {end_time - start_time:.2f} seconds")
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")