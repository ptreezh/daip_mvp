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

def test_cli_roles_list_command_no_roles():
    """Test that the 'roles list' command correctly indicates no roles found."""
    with unittest.mock.patch('src.cli.commands.role_commands.RoleManager') as MockRoleManager:
        # Configure the mock instance that the RoleManager constructor will return
        mock_instance = MockRoleManager.return_value
        mock_instance.get_all_roles.return_value = [] # Should return an empty list

        result = runner.invoke(app, ["roles", "list"])
        assert result.exit_code == 0
        
        clean_stdout = strip_ansi(result.stdout)
        assert "No roles available" in clean_stdout
        assert "Troubleshooting" in clean_stdout

def test_cli_roles_list_command_with_roles():
    """Test that the 'roles list' command displays a table of roles."""
    mock_roles_list = [
        MockRole(id="role1", name="AI Ethicist", description="Expert in AI ethics and societal impact.", system_prompt="You are an AI Ethicist.", tags=["AI", "Ethics"]),
        MockRole(id="role2", name="Tech Innovator", description="Focuses on cutting-edge technology development.", system_prompt="You are a Tech Innovator.", tags=["Technology", "Innovation"]),
    ]
    with unittest.mock.patch('src.cli.commands.role_commands.RoleManager') as MockRoleManager:
        mock_instance = MockRoleManager.return_value
        mock_instance.get_all_roles.return_value = mock_roles_list

        result = runner.invoke(app, ["roles", "list"])
        assert result.exit_code == 0
        
        clean_stdout = strip_ansi(result.stdout)
        normalized_stdout = normalize_whitespace(clean_stdout)

        assert "DAIP-LIVE Available Roles (2)" in normalized_stdout
        assert "role1" in normalized_stdout
        assert "AI Ethicist" in normalized_stdout
        assert "Expert in AI ethics and" in normalized_stdout
        assert "societal impact." in normalized_stdout
        assert "AI, Ethics" in normalized_stdout
        assert "role2" in normalized_stdout
        assert "Tech Innovator" in normalized_stdout
        assert "Focuses on cutting-edge" in normalized_stdout
        assert "technology development." in normalized_stdout
        assert "Technology, Innovation" in normalized_stdout

def test_cli_roles_help_command():
    """Test that the roles --help command works."""
    result = runner.invoke(app, ["roles", "--help"])
    assert result.exit_code == 0
    assert "Usage: daip-cli roles [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "Role management commands for DAIP-LIVE." in result.stdout
    assert "Commands" in result.stdout
    assert "create" in result.stdout
    assert "manage" in result.stdout
    assert "invite" in result.stdout
    assert "match" in result.stdout
    assert "stats" in result.stdout

