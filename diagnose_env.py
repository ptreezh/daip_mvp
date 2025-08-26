#!/usr/bin/env python3
"""Diagnose Python environment issues."""

import os
import sys
import subprocess
import time

def run_command_with_timeout(cmd, timeout=10):
    """Run command with timeout."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -2, "", str(e)

def diagnose_environment():
    """Diagnose Python environment issues."""
    print("=" * 60)
    print("Python Environment Diagnostic")
    print("=" * 60)
    
    # Test 1: Basic Python functionality
    print("\n1. Testing basic Python commands:")
    
    tests = [
        ("python --version", "Python version"),
        ("python -c \"print('hello')\"", "Simple print"),
        ("python -c \"import os; print(os.getcwd())\"", "Import os"),
        ("python -c \"import sys; print(sys.version)\"", "Import sys"),
    ]
    
    for cmd, description in tests:
        print(f"   {description}: ", end="")
        returncode, stdout, stderr = run_command_with_timeout(cmd, 5)
        if returncode == 0:
            print(f"✅ OK - {stdout.strip()}")
        elif returncode == -1:
            print("❌ TIMEOUT")
        else:
            print(f"❌ ERROR: {stderr}")
    
    # Test 2: Check Python installations
    print("\n2. Checking Python installations:")
    
    # Try different ways to find Python
    python_paths = []
    
    # Check common Python locations
    common_paths = [
        "C:\\Python312\\python.exe",
        "C:\\Python311\\python.exe", 
        "C:\\Python310\\python.exe",
        "C:\\Program Files\\Python312\\python.exe",
        "C:\\Program Files\\Python311\\python.exe",
        "C:\\Users\\{}\\AppData\\Local\\Programs\\Python\\Python312\\python.exe".format(os.getenv('USERNAME')),
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            python_paths.append(path)
            print(f"   ✅ Found: {path}")
    
    if not python_paths:
        print("   ⚠️  No Python installations found in common locations")
    
    # Test 3: Check environment variables
    print("\n3. Checking environment variables:")
    
    env_vars = ['PATH', 'PYTHONPATH', 'PYTHONHOME']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: Set (length: {len(value)} chars)")
            # Show first 200 chars to avoid huge output
            if len(value) > 200:
                print(f"     {value[:200]}...")
            else:
                print(f"     {value}")
        else:
            print(f"   {var}: Not set")
    
    # Test 4: Check current working directory
    print(f"\n4. Current working directory: {os.getcwd()}")
    
    # Test 5: Check if we can import basic modules
    print("\n5. Testing basic imports:")
    basic_modules = ['os', 'sys', 'json', 'time']
    
    for module in basic_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}: OK")
        except ImportError:
            print(f"   ❌ {module}: FAIL")
    
    print("\n" + "=" * 60)
    print("Diagnosis complete")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_environment()