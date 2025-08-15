#!/bin/bash

# DAIP-LIVE Mandatory Rules Validation Script
# This script enforces all mandatory development rules

set -e  # Exit on any error

echo "🚀 DAIP-LIVE Mandatory Rules Validation"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}[${1}]${NC}"
}

print_status "INFO" "$GREEN" "Starting mandatory rules validation..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "CLAUDE.md" ]; then
    print_status "ERROR" "$RED" "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Code Quality Gates
print_status "STEP 1" "$GREEN" "Checking Code Quality Gates..."

echo "  • Running Black formatting check..."
if ! black --check src/ tests/ > /dev/null 2>&1; then
    print_status "FAIL" "$RED" "Black formatting check failed"
    echo "  🔧 Run: black src/ tests/"
    exit 1
fi
print_status "PASS" "$GREEN" "Black formatting check passed"

echo "  • Running Ruff linting check..."
if ! ruff check src/ tests/ > /dev/null 2>&1; then
    print_status "FAIL" "$RED" "Ruff linting check failed"
    echo "  🔧 Fix linting issues before committing"
    exit 1
fi
print_status "PASS" "$GREEN" "Ruff linting check passed"

echo "  • Running MyPy type checking..."
if ! mypy src/ > /dev/null 2>&1; then
    print_status "FAIL" "$RED" "MyPy type checking failed"
    echo "  🔧 Fix type hint issues"
    exit 1
fi
print_status "PASS" "$GREEN" "MyPy type checking passed"

# Step 2: Run Python checker for comprehensive validation
print_status "STEP 2" "$GREEN" "Running comprehensive rules checker..."
if ! python mandatory_rules_checker.py > /dev/null 2>&1; then
    print_status "FAIL" "$RED" "Comprehensive rules check failed"
    echo "  🔧 Check mandatory_rules_report.json for details"
    exit 1
fi
print_status "PASS" "$GREEN" "Comprehensive rules check passed"

# Step 3: Test validation
print_status "STEP 3" "$GREEN" "Running test suite..."
if ! pytest --tb=short -x > /dev/null 2>&1; then
    print_status "FAIL" "$RED" "Test suite failed"
    echo "  🔧 Fix failing tests before committing"
    exit 1
fi
print_status "PASS" "$GREEN" "Test suite passed"

# Final validation complete
print_status "SUCCESS" "$GREEN" "All mandatory rules passed! ✅"
echo ""
echo "🎉 You are ready to commit your changes!"
echo ""
echo "Summary:"
echo "  ✅ Code Quality Gates (Black, Ruff, MyPy)"
echo "  ✅ File Headers and Documentation"
echo "  ✅ Architecture Compliance"
echo "  ✅ Test Suite"
echo "  ✅ Environment Standards"
echo ""
echo "Commit with confidence! 🚀"