import pytest
import subprocess
import sys
from pathlib import Path

# Define the path to the daip-cli.py script
CLI_SCRIPT = Path(__file__).parent.parent.parent / "daip-cli.py"

@pytest.fixture(autouse=True)
def setup_cli_environment():
    """Ensures the CLI environment is set up for testing."""
    assert CLI_SCRIPT.exists(), f"CLI script not found at {CLI_SCRIPT}"

def run_cli_command(command: list[str]) -> tuple[int, str, str]:
    """Helper function to run a daip-cli command and capture its output.
    Returns (exit_code, stdout, stderr).
    """
    cmd = [sys.executable, str(CLI_SCRIPT)] + command
    process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return process.returncode, process.stdout, process.stderr

# Test cases for simplified commands

def test_intv_command_exists():
    """Test that 'daip-cli intv' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["intv", "--help"])
    assert exit_code == 0
    assert "Provide an intervention to the current assistant session." in stdout
    assert "--content" in stdout
    assert "--intent" in stdout

def test_cons_command_exists():
    """Test that 'daip-cli cons' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["cons", "--help"])
    assert exit_code == 0
    assert "Get consensus information for the current session." in stdout

def test_disag_command_exists():
    """Test that 'daip-cli disag' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["disag", "--help"])
    assert exit_code == 0
    assert "Get key disagreement points for the current session." in stdout

def test_sess_command_exists():
    """Test that 'daip-cli sess' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["sess", "--help"])
    assert exit_code == 0
    assert "List all sessions." in stdout

# Note: Functional tests for these commands will require mocking underlying services
# or setting up a more complex test environment.
