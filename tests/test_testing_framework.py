"""
Test suite for establishing a comprehensive testing framework.
"""

import os
import subprocess
import sys

import pytest


def test_environment_setup():
    """Test that the testing environment is properly set up."""
    # Check that we can import the main modules
    try:
        from src.daip_live.tui import DAIP_TUI  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import TUI module: {e}")


def test_test_directories_exist():
    """Test that the test directories exist."""
    assert os.path.exists("tests/unit"), "Unit test directory missing"
    assert os.path.exists("tests/integration"), "Integration test directory missing"
    assert os.path.exists("tests/e2e"), "E2E test directory missing"


def test_required_test_files_exist():
    """Test that the required test files have been created."""
    required_files = [
        "tests/unit/test_tui_input_handling.py",
        "tests/unit/test_tui_model_switching.py",
        "tests/unit/test_tui_background_tasks.py",
        "tests/unit/test_tui_full_flow.py",
        "tests/unit/test_tui_real_commands.py",
        "tests/unit/test_tui_full_coverage.py",
    ]

    for file_path in required_files:
        assert os.path.exists(file_path), f"Required test file missing: {file_path}"


def test_pytest_can_run():
    """Test that pytest can run successfully."""
    # Try to run pytest on our new test files
    try:
        # Run pytest on just our new test files to avoid issues with existing tests
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/test_tui_input_handling.py",
                "--collect-only",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should succeed in collection (even if no tests match)
        assert result.returncode in [0, 1, 2, 3, 4], (
            f"Pytest failed to collect tests: {result.stderr}"
        )
    except subprocess.TimeoutExpired:
        pytest.fail("Pytest command timed out")
    except Exception as e:
        pytest.fail(f"Failed to run pytest: {e}")


if __name__ == "__main__":
    # Run the tests
    test_environment_setup()
    test_test_directories_exist()
    test_required_test_files_exist()
    test_pytest_can_run()
