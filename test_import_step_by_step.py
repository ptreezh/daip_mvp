# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-04 18:30:00
@Author  : DAIP-LIVE Team
@File    : test_import_step_by_step.py
@Description:
    Test imports step by step to identify the bottleneck.
"""

import sys
import time

def test_step_by_step():
    """Test imports step by step"""
    print("Testing imports step by step...")
    
    # Test 1: Basic imports
    start_time = time.time()
    try:
        import asyncio
        import json
        import logging
        import re
        import statistics
        from typing import Dict, List, Optional, Any, Tuple, Set
        from dataclasses import dataclass, asdict
        from datetime import datetime, timedelta
        from enum import Enum
        import numpy as np
        from collections import defaultdict, Counter
        import threading
        import time
        from textstat import flesch_reading_ease, flesch_kincaid_grade
        print("✅ Basic imports successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False
    
    # Test 2: Try importing the assessment engine module directly
    start_time = time.time()
    try:
        from src.core_services import multidimensional_assessment_engine
        print("✅ Module import successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False
    
    # Test 3: Try importing specific classes
    start_time = time.time()
    try:
        from src.core_services.multidimensional_assessment_engine import (
            AssessmentDimension, QualityLevel, ContentType, 
            AssessmentCriteria, MetricResult, DimensionResult, 
            AssessmentResult, ContentToAssess, MultiDimensionalAssessmentEngine
        )
        print("✅ Class imports successful ({:.2f}s)".format(time.time() - start_time))
    except Exception as e:
        print(f"❌ Class imports failed: {e}")
        return False
    
    print("🎉 All step-by-step imports successful!")
    return True

if __name__ == "__main__":
    start_time = time.time()
    success = test_step_by_step()
    end_time = time.time()
    
    print(f"\nStep-by-step import test completed in {end_time - start_time:.2f} seconds")
    print(f"Result: {'SUCCESS' if success else 'FAILED'}")