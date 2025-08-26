"""
Test role management commands for the DAIP CLI.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, ANY

# Import the typer app instance from the command implementation file
from src.cli.main import app
from src.debate_system.debate_flow_definition import DebateParticipant, ParticipantRole

runner = CliRunner()

# Mock data
MOCK_ROLE = MagicMock()
MOCK_ROLE.id = "test_role_001"
MOCK_ROLE.name = "Test Role"

MOCK_PARTICIPANT = DebateParticipant(
    participant_id=MOCK_ROLE.id,
    name=MOCK_ROLE.name,
    role=ParticipantRole.OBSERVER
)

MOCK_DEBATE_SESSION = MagicMock()
MOCK_DEBATE_SESSION.id = "debate_001"
MOCK_DEBATE_SESSION.participants = []

MOCK_DEBATE_SESSION_WITH_PARTICIPANT = MagicMock()
MOCK_DEBATE_SESSION_WITH_PARTICIPANT.id = "debate_002"
MOCK_DEBATE_SESSION_WITH_PARTICIPANT.participants = [MOCK_PARTICIPANT]


@patch('src.cli.commands.role_commands.RoleManager')
def test_create_role_success(MockRoleManager):
    """Test creating a role successfully."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_role_manager.create_role.return_value = True

    # Act
    result = runner.invoke(app, ["roles", "create", "New Role", "--description", "A new test role", "--tags", "test,new"])

    # Assert
    assert result.exit_code == 0
    assert "Role 'New Role' created successfully" in result.stdout
    mock_role_manager.create_role.assert_called_once()

@patch('src.cli.commands.role_commands.RoleManager')
def test_create_role_invalid_name(MockRoleManager):
    """Test creating a role with an invalid name."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value

    # Act
    result = runner.invoke(app, ["roles", "create", "  ", "--description", "A role with an invalid name"])

    # Assert
    assert result.exit_code == 1
    assert "Error: Role name must be at least 3 characters long and cannot be empty." in result.stdout
    mock_role_manager.create_role.assert_not_called()

@patch('src.cli.commands.role_commands.RoleManager')
def test_create_role_failure(MockRoleManager):
    """Test role creation failure."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_role_manager.create_role.return_value = False

    # Act
    result = runner.invoke(app, ["roles", "create", "New Role", "--description", "A new test role"])

    # Assert
    assert "Failed to create role 'New Role'" in result.stdout
    mock_role_manager.create_role.assert_called_once()

@patch('src.cli.commands.role_commands.RoleManager')
def test_manage_role_success(MockRoleManager):
    """Test managing a role successfully."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_role_manager.update_role.return_value = True

    # Act
    result = runner.invoke(app, ["roles", "manage", MOCK_ROLE.id, "--update-description", "Updated description"])

    # Assert
    assert result.exit_code == 0
    assert f"Role '{MOCK_ROLE.id}' updated successfully" in result.stdout
    mock_role_manager.update_role.assert_called_once_with(MOCK_ROLE.id, {"description": "Updated description"})

@patch('src.cli.commands.role_commands.RoleManager')
def test_manage_role_invalid_description(MockRoleManager):
    """Test managing a role with an invalid description."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value

    # Act
    result = runner.invoke(app, ["roles", "manage", "any_role", "--update-description", "  "])

    # Assert
    assert result.exit_code == 1
    assert "Error: Description cannot be empty." in result.stdout
    mock_role_manager.update_role.assert_not_called()

@patch('src.cli.commands.role_commands.RoleManager')
def test_manage_role_not_found(MockRoleManager):
    """Test managing a role that does not exist."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_role_manager.update_role.return_value = False

    # Act
    result = runner.invoke(app, ["roles", "manage", "nonexistent_role", "--update-description", "Updated description"])

    # Assert
    assert "Failed to update role 'nonexistent_role'" in result.stdout
    mock_role_manager.update_role.assert_called_once_with("nonexistent_role", {"description": "Updated description"})


@patch('src.cli.commands.role_commands.DebateStateManager')
@patch('src.cli.commands.role_commands.RoleManager')
def test_invite_role_success(MockRoleManager, MockDebateStateManager):
    """Test inviting a role to a debate successfully."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_debate_manager = MockDebateStateManager.return_value

    mock_role_manager.get_role_by_id.return_value = MOCK_ROLE
    mock_debate_manager.storage.load_session.return_value = MOCK_DEBATE_SESSION
    mock_debate_manager.storage.save_session.return_value = True

    # Act
    result = runner.invoke(app, ["roles", "invite", MOCK_ROLE.id, "--debate-id", MOCK_DEBATE_SESSION.id])

    # Assert
    assert result.exit_code == 0
    assert f"Successfully invited role '{MOCK_ROLE.name}' ({MOCK_ROLE.id}) to debate '{MOCK_DEBATE_SESSION.id}'" in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with(MOCK_ROLE.id)
    mock_debate_manager.storage.load_session.assert_called_once_with(MOCK_DEBATE_SESSION.id)
    mock_debate_manager.storage.save_session.assert_called_once_with(ANY) # Check that save was called with the modified session

@patch('src.cli.commands.role_commands.DebateStateManager')
@patch('src.cli.commands.role_commands.RoleManager')
def test_invite_role_invalid_debate_id(MockRoleManager, MockDebateStateManager):
    """Test invitation with an invalid debate ID."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_debate_manager = MockDebateStateManager.return_value

    mock_role_manager.get_role_by_id.return_value = MOCK_ROLE
    mock_debate_manager.storage.load_session.return_value = None  # Simulate debate not found

    # Act
    result = runner.invoke(app, ["roles", "invite", MOCK_ROLE.id, "--debate-id", "nonexistent_debate"])

    # Assert
    assert result.exit_code == 1
    assert "Error: Debate with ID 'nonexistent_debate' not found." in result.stdout
    mock_debate_manager.storage.load_session.assert_called_once_with("nonexistent_debate")
    mock_debate_manager.storage.save_session.assert_not_called()

@patch('src.cli.commands.role_commands.DebateStateManager')
@patch('src.cli.commands.role_commands.RoleManager')
def test_invite_role_invalid_role_id(MockRoleManager, MockDebateStateManager):
    """Test invitation with an invalid role ID."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_debate_manager = MockDebateStateManager.return_value

    mock_role_manager.get_role_by_id.return_value = None # Simulate role not found

    # Act
    result = runner.invoke(app, ["roles", "invite", "nonexistent_role", "--debate-id", MOCK_DEBATE_SESSION.id])

    # Assert
    assert result.exit_code == 1
    assert "Error: Role with ID 'nonexistent_role' not found." in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with("nonexistent_role")
    mock_debate_manager.storage.load_session.assert_not_called()

@patch('src.cli.commands.role_commands.DebateStateManager')
@patch('src.cli.commands.role_commands.RoleManager')
def test_invite_role_duplicate(MockRoleManager, MockDebateStateManager):
    """Test inviting a role that is already in the debate."""
    # Arrange
    mock_role_manager = MockRoleManager.return_value
    mock_debate_manager = MockDebateStateManager.return_value

    mock_role_manager.get_role_by_id.return_value = MOCK_ROLE
    # Simulate a session that already contains the participant
    mock_debate_manager.storage.load_session.return_value = MOCK_DEBATE_SESSION_WITH_PARTICIPANT

    # Act
    result = runner.invoke(app, ["roles", "invite", MOCK_ROLE.id, "--debate-id", MOCK_DEBATE_SESSION_WITH_PARTICIPANT.id])

    # Assert
    assert result.exit_code == 1
    # Note: The check in the command uses `p.participant_id`, so our mock participant needs that attribute.
    assert f"Error: Role '{MOCK_ROLE.name}' is already a participant in debate '{MOCK_DEBATE_SESSION_WITH_PARTICIPANT.id}'." in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with(MOCK_ROLE.id)
    mock_debate_manager.storage.load_session.assert_called_once_with(MOCK_DEBATE_SESSION_WITH_PARTICIPANT.id)
    mock_debate_manager.storage.save_session.assert_not_called()

def test_roles_help_command():
    """Test the `roles help` command."""
    result = runner.invoke(app, ["roles", "help"])
    assert result.exit_code == 0
    assert "Role Management Commands Help" in result.stdout
    assert "daip-cli roles create" in result.stdout
