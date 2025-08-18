import subprocess
import pytest
import re

# Assuming daip-cli.py is in the project root
CLI_PATH = "daip-cli.py"

def run_cli_command(command: list[str]) -> subprocess.CompletedProcess:
    """Helper function to run CLI commands."""
    cmd = ["python", CLI_PATH] + command
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result

def normalize_whitespace(text: str) -> str:
    """Normalizes whitespace in a string for robust comparison."""
    return re.sub(r'\s+', ' ', text).strip()

def test_cli_version_command():
    """Test that the --version command works and shows a version string."""
    result = run_cli_command(["--version"])
    assert result.returncode == 0
    assert "DAIP-LIVE CLI Version:" in result.stdout
    assert "0.1.0" in result.stdout # Expecting a hardcoded version for now

def test_cli_help_command():
    """Test that the --help command works and shows basic usage."""
    result = run_cli_command(["--help"])
    assert result.returncode == 0
    normalized_output = normalize_whitespace(result.stdout)
    assert "Usage:" in normalized_output
    assert "Options:" in normalized_output
    assert "Commands:" in normalized_output
    assert "assistant" in normalized_output or "start" in normalized_output

import unittest.mock
from src.core_services.role_manager import RoleManager # Assuming this path

# Mock Role class for testing
class MockRole:
    def __init__(self, id, name, description, system_prompt, tags=None):
        self.id = id
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tags = tags if tags is not None else []

def test_cli_roles_command_no_roles():
    """Test that the roles command correctly indicates no roles found."""
    with unittest.mock.patch('src.core_services.role_manager.RoleManager') as MockRoleManager:
        MockRoleManager.return_value.list_roles.return_value = []
        result = run_cli_command(["roles"])
        assert result.returncode == 0
        assert "No roles available" in result.stdout
        assert "Troubleshooting" in result.stdout # Check for troubleshooting tips

def test_cli_roles_command_with_roles():
    """Test that the roles command displays a list of roles."""
    mock_roles_data = [
        MockRole("role1", "AI Ethicist", "Expert in AI ethics and societal impact.", "You are an AI Ethicist.", ["AI", "Ethics"]),
        MockRole("role2", "Tech Innovator", "Focuses on cutting-edge technology development.", "You are a Tech Innovator.", ["Technology", "Innovation"]),
    ]
    with unittest.mock.patch('src.core_services.role_manager.RoleManager') as MockRoleManager:
        MockRoleManager.return_value.list_roles.return_value = mock_roles_data
        result = run_cli_command(["roles"])
        assert result.returncode == 0
        assert "DAIP-LIVE Available Roles" in result.stdout
        assert "AI Ethicist" in result.stdout
        assert "Tech Innovator" in result.stdout
        assert "Expert in AI ethics" in result.stdout # Check for description snippet
        assert "Technology, Innovation" in result.stdout # Check for tags
        assert "Available Roles (2)" in result.stdout # Check table title
