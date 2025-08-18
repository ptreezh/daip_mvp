import pytest
import subprocess
import sys
from pathlib import Path

# Define the path to the daip-cli.py script
CLI_SCRIPT = Path(__file__).parent.parent.parent / "daip-cli.py"

@pytest.fixture(autouse=True)
def setup_cli_environment():
    """Ensures the CLI environment is set up for testing."""
    # Add any necessary setup here, e.g., creating dummy data directories
    # For now, we just ensure the CLI_SCRIPT path is correct
    assert CLI_SCRIPT.exists(), f"CLI script not found at {CLI_SCRIPT}"

def run_cli_command(command: list[str]) -> tuple[int, str, str]:
    """Helper function to run a daip-cli command and capture its output.
    Returns (exit_code, stdout, stderr).
    """
    cmd = [sys.executable, str(CLI_SCRIPT)] + command
    process = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return process.returncode, process.stdout, process.stderr

# Test cases for simplified instruction support

def test_pa_chat_command_exists():
    """Test that 'daip-cli pa chat' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["pa", "chat", "--help"])
    assert exit_code == 0
    assert "Interact with the personal assistant." in stdout
    assert "The query for the Personal Assistant." in stdout

def test_pa_status_command_exists():
    """Test that 'daip-cli pa status' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["pa", "status", "--help"])
    assert exit_code == 0
    assert "Check the status of a complex task." in stdout
    assert "The ID of the task to check status for." in stdout

def test_pa_logs_command_exists():
    """Test that 'daip-cli pa logs' command exists and shows help."""
    exit_code, stdout, stderr = run_cli_command(["pa", "logs", "--help"])
    assert exit_code == 0
    assert "View recent log entries from the personal assistant." in stdout
    assert "--limit" in stdout

# Note: For actual functional tests of pa chat, status, logs, you would need to mock
# the underlying services (PersonalAssistantRouter and its dependencies) or run a live system.
# These tests only verify the CLI command structure and help messages.
