#!/bin/bash
# DAIP-MVP Comprehensive Test Runner
# This script runs the complete automated testing suite

echo "Starting DAIP-MVP Comprehensive Automated Testing..."
echo "===================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH"
    exit 1
fi

# Check if required directories exist
if [ ! -d "personal_intelligence_hub" ]; then
    echo "Error: personal_intelligence_hub directory not found"
    exit 1
fi

if [ ! -d "src" ]; then
    echo "Error: src directory not found"
    exit 1
fi

if [ ! -d "src/debate_system" ]; then
    echo "Error: src/debate_system directory not found"
    exit 1
fi

# Create test reports directory
mkdir -p test_reports

# Install test requirements if needed
echo "Checking test requirements..."
if ! python3 -c "import selenium" &> /dev/null; then
    echo "Installing test requirements..."
    pip3 install -r test_requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install test requirements"
        exit 1
    fi
fi

# Run the comprehensive test
echo ""
echo "Running comprehensive automated tests..."
echo "This may take several minutes..."
echo ""

python3 tests/ddd/test_runner.py

if [ $? -eq 0 ]; then
    echo ""
    echo "All tests passed successfully!"
else
    echo ""
    echo "Tests completed with failures"
    echo "Check test_reports directory for detailed results"
fi

echo ""
echo "Test execution completed"