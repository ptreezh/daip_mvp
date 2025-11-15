"""
User Acceptance Test Runner

This module provides utilities to execute User Acceptance Tests for the P7 GUI application.
"""

import unittest
import sys
import os
from typing import Dict, Any


def run_uat_tests() -> bool:
    """
    Execute all User Acceptance Tests.
    
    Returns:
        True if all tests pass, False otherwise
    """
    # Create test suite
    from .uat_tests import create_uat_suite
    suite = create_uat_suite()
    
    # Run the tests
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout
    )
    
    result = runner.run(suite)
    
    # Print summary
    print(f"
{'='*60}")
    print("USER ACCEPTANCE TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 100
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


def run_comprehensive_uat() -> bool:
    """Run comprehensive UAT covering all required areas."""
    print("🚀 Starting Comprehensive User Acceptance Testing...")
    print(f"{'='*60}")
    
    # Validate different aspects
    validation_points = [
        "GUI matches TUI functionality",
        "Cross-platform compatibility", 
        "Performance and responsiveness",
        "Quality and error handling"
    ]
    
    print(f"Validating {len(validation_points)} acceptance criteria:")
    for i, point in enumerate(validation_points, 1):
        print(f"  {i}. {point}")
    
    print(f"
Executing UAT suites...")
    
    # Run the actual tests
    success = run_uat_tests()
    
    # Overall summary
    print(f"
{'='*60}")
    print("COMPREHENSIVE UAT RESULTS")
    print(f"{'='*60}")
    
    overall_status = "✅ ALL ACCEPTANCE CRITERIA MET" if success else "❌ SOME ACCEPTANCE CRITERIA FAILED"
    print(f"Overall Status: {overall_status}")
    
    print(f"{'='*60}")
    
    return success


if __name__ == "__main__":
    success = run_comprehensive_uat()
    sys.exit(0 if success else 1)
