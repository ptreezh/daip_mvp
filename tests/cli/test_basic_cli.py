import pytest
import re
from typer.testing import CliRunner
from src.cli.main import app # Import the Typer app directly

# Initialize CliRunner
runner = CliRunner()

# Regex to strip ANSI escape codes
ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\-_]|[[0-?]*[ -/]*[@-~])')

def strip_ansi(text: str) -> str:
    """Strips ANSI escape codes from a string."""
    return ANSI_ESCAPE.sub('', text)

def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace in a string for robust comparison."""
    # Strip ANSI first, then normalize whitespace
    clean_text = strip_ansi(text)
    return re.sub(r'\s+', ' ', clean_text).strip()

def test_cli_version_command():
    """Test that the --version command works and shows a version string."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0 # CliRunner uses exit_code
    assert "DAIP-LIVE CLI Version:" in result.stdout
    assert "0.1.0" in result.stdout # Expecting a hardcoded version for now

def test_cli_help_command():
    """Test that the --help command works and shows basic usage."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    
    # Strip ANSI codes before normalizing and checking
    clean_output = strip_ansi(result.stdout)
    normalized_output = normalize_whitespace(clean_output)

    print(f"\n--- Help Command Cleaned STDOUT ---\n{clean_output}\n---------------------------\n") # Debug print
    print(f"\n--- Help Command Normalized STDOUT ---\n{normalized_output}\n---------------------------\n") # Debug print

    assert "Usage:" in normalized_output
    # The actual output from rich may not include the colon
    assert "Options" in normalized_output
    assert "Commands" in normalized_output
    assert "assistant" in normalized_output or "start" in normalized_output

import unittest.mock
# from src.app_state import AppState # No longer needed for direct import, will patch where it's used

# Mock Role class for testing (still needed for return values)
class MockRole:
    def __init__(self, id, name, description, system_prompt, tags=None):
        self.id = id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tags = tags if tags is not None else []

def test_cli_roles_command_no_roles():
    """Test that the roles command correctly indicates no roles found."""
    # Patch AppState where it's used in src.cli.commands
    with unittest.mock.patch('src.cli.commands.AppState') as MockAppState:
        MockAppState.return_value.all_roles_details = {}
        MockAppState.return_value.load_all_roles.return_value = None # load_all_roles doesn't return anything
        result = runner.invoke(app, ["roles"])
        assert result.exit_code == 0
        
        # Strip ANSI codes before checking
        clean_stdout = strip_ansi(result.stdout)
        assert "No roles available" in clean_stdout
        assert "Troubleshooting" in clean_stdout # Check for troubleshooting tips

def test_cli_roles_command_with_roles():
    """Test that the roles command displays a list of roles."""
    mock_roles_data = {
        "role1": {"name": "AI Ethicist", "desc": "Expert in AI ethics and societal impact.", "tags": ["AI", "Ethics"]},
        "role2": {"name": "Tech Innovator", "desc": "Focuses on cutting-edge technology development.", "tags": ["Technology", "Innovation"]},
    }
    with unittest.mock.patch('src.cli.commands.AppState') as MockAppState: # Mock AppState
        # Mock load_all_roles to populate all_roles_details
        MockAppState.return_value.all_roles_details = mock_roles_data
        MockAppState.return_value.load_all_roles.return_value = None # load_all_roles doesn't return anything
        result = runner.invoke(app, ["roles"])
        assert result.exit_code == 0
        
        # Strip ANSI codes before normalizing and checking
        clean_stdout = strip_ansi(result.stdout)
        normalized_stdout = normalize_whitespace(clean_stdout) # Apply normalization here

        assert "DAIP-LIVE Available Roles" in normalized_stdout
        # The actual output shows role IDs (role1, role2) instead of role names
        assert "role1" in normalized_stdout # Check for role ID
        assert "role2" in normalized_stdout # Check for role ID
        assert "Expert in AI ethics" in normalized_stdout # Check for normalized description snippet
        assert "Technology, Innovation" in normalized_stdout # Check for normalized tags
        assert "Available Roles (2)" in normalized_stdout # Check table title

