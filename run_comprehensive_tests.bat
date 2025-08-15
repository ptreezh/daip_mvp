@echo off
REM DAIP-MVP Comprehensive Test Runner
REM This script runs the complete automated testing suite

echo Starting DAIP-MVP Comprehensive Automated Testing...
echo ====================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required directories exist
if not exist "personal_intelligence_hub" (
    echo Error: personal_intelligence_hub directory not found
    pause
    exit /b 1
)

if not exist "src" (
    echo Error: src directory not found
    pause
    exit /b 1
)

if not exist "src\debate_system" (
    echo Error: src\debate_system directory not found
    pause
    exit /b 1
)

REM Create test reports directory
if not exist "test_reports" mkdir test_reports

REM Install test requirements if needed
echo Checking test requirements...
pip show selenium >nul 2>&1
if errorlevel 1 (
    echo Installing test requirements...
    pip install -r test_requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install test requirements
        pause
        exit /b 1
    )
)

REM Run the comprehensive test
echo.
echo Running comprehensive automated tests...
echo This may take several minutes...
echo.

python tests\ddd\test_runner.py

if errorlevel 1 (
    echo.
    echo Tests completed with failures
    echo Check test_reports directory for detailed results
) else (
    echo.
    echo All tests passed successfully!
)

echo.
echo Test execution completed
pause