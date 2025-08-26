#!/usr/bin/env python3
"""Simple test to check Python environment functionality."""

import sys
import os
import subprocess
import time

def test_basic_python():
    """Test basic Python functionality."""
    print("Testing basic Python functionality...")
    
    # Test Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Test basic operations
    try:
        result = 2 + 2
        print(f"Basic math test: 2 + 2 = {result}")
        
        # Test file operations
        test_file = "test_temp_file.txt"
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"File operations test: {content}")
            os.remove(test_file)
            print("File operations test passed")
        else:
            print("File operations test failed")
            
        return True
    except Exception as e:
        print(f"Basic Python test failed: {e}")
        return False

def test_imports():
    """Test basic imports."""
    print("\nTesting basic imports...")
    
    basic_modules = ['os', 'sys', 'json', 'time', 'datetime', 'pathlib']
    
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            return False
    
    return True

def test_poetry():
    """Test Poetry functionality."""
    print("\nTesting Poetry...")
    
    try:
        # Try to run poetry --version with timeout
        result = subprocess.run(
            [sys.executable, '-m', 'poetry', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(f"Poetry version: {result.stdout.strip()}")
        return True
    except subprocess.TimeoutExpired:
        print("Poetry command timed out")
        return False
    except Exception as e:
        print(f"Poetry test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Python Environment Diagnostic Test")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_basic_python()
    success &= test_imports()
    success &= test_poetry()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! Python environment appears functional.")
    else:
        print("✗ Some tests failed. There may be environment issues.")
    print("=" * 50)