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