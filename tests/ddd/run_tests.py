"""@Time    : 2025-08-06 12:30:00
@Author  : DAIP-LIVE Team
@File    : run_tests.py
@Description:
    Simple test execution script for the DDD test suite.
    Provides quick test running with basic reporting.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_tests():
    """Run the DDD test suite"""
    print("🚀 Running DDD Test Suite for Personal Intelligence Hub")
    print("=" * 60)
    
    # Change to the DDD test directory
    ddd_dir = Path(__file__).parent
    os.chdir(ddd_dir)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"])
    
    # Run the test runner
    try:
        start_time = time.time()
        
        # Import and run the test runner
        from test_runner import TestRunner
        runner = TestRunner()
        results = runner.run_all_tests()
        
        execution_time = time.time() - start_time
        
        # Print summary
        print(f"\n⏱️  Total execution time: {execution_time:.2f} seconds")
        print(f"✅ Passed: {results['passed_tests']}")
        print(f"❌ Failed: {results['failed_tests']}")
        print(f"📊 Coverage: {results['coverage']['overall']*100:.1f}%")
        
        if results['failed_tests'] == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n❌ {results['failed_tests']} test(s) failed!")
            return 1
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)