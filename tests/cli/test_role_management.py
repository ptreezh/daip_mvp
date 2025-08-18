import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typer.testing import CliRunner
import asyncio
import json

# Assuming daip-cli.py is in the project root and src/cli/main.py is the actual app
# Adjust path as necessary if the structure is different
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.cli.main import app, assistant_app # Import app and assistant_app from main.py
from src.core_services.autonomous_role_creation_system import AutonomousRoleCreationSystem, RoleGenerationRequest, RoleGenerationResult, GeneratedRole, RoleRequirement, RoleType, ExpertiseLevel, InteractionStyle, RoleStatus, RoleCapability, RolePersonality
from src.core_services.role_manager import RoleManager, Role
from src.real_demo_system.real_role_manager import RealRoleManager

runner = CliRunner()

# --- Fixtures for Mocks ---

@pytest.fixture
def mock_autonomous_role_creation_system():
    with patch('src.core_services.autonomous_role_creation_system.AutonomousRoleCreationSystem', autospec=True) as MockClass:
        instance = MockClass.return_value
        instance.create_role = AsyncMock()
        yield instance

@pytest.fixture
def mock_role_manager():
    with patch('src.cli.commands.RoleManager', autospec=True) as MockClass:
        instance = MockClass.return_value
        instance.get_role_by_id = MagicMock()
        instance.save_role = MagicMock()
        yield instance

@pytest.fixture
def mock_real_role_manager():
    with patch('src.cli.commands.RealRoleManager', autospec=True) as MockClass:
        instance = MockClass.return_value
        instance.get_role = MagicMock()
        yield instance

# --- Test Cases for `daip-cli roles create` ---

def test_create_role_success(mock_autonomous_role_creation_system):
    # Test Case 2.2.1: Create Role - Success
    mock_autonomous_role_creation_system.create_role.return_value = RoleGenerationResult(
        request_id="req123",
        generated_role=GeneratedRole(
            role_id="new_role_id",
            name="New Role",
            role_type=RoleType.EXPERT,
            domain="general",
            description="A test role.",
            system_prompt="You are a new role.",
            capabilities=[],
            personality=RolePersonality(communication_style="direct", decision_making_approach="rational", problem_solving_method="analytical", creativity_level=0.5, analytical_depth=0.5, risk_tolerance=0.5, collaboration_preference=0.5),
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            interaction_style=InteractionStyle.FORMAL,
            status=RoleStatus.ACTIVE
        ),
        generation_process={},
        quality_assessment={},
        confidence_score=1.0
    )
    result = runner.invoke(app, ["roles", "create", "New Role", "--description", "A test role."])
    assert result.exit_code == 0
    assert "Successfully created role" in result.stdout
    mock_autonomous_role_creation_system.create_role.assert_called_once()
    args, kwargs = mock_autonomous_role_creation_system.create_role.call_args
    assert isinstance(args[0], RoleGenerationRequest)
    assert args[0].requirements.task_description == "A test role."
    assert args[0].requirements.domain == "general" # Default domain

def test_create_role_missing_description():
    # Test Case 2.2.2: Create Role - Missing Description
    result = runner.invoke(app, ["roles", "create", "New Role"])
    assert result.exit_code != 0
    assert "Error: Missing required option '--description'" in result.stderr # Typer's default error message

def test_create_role_with_tags(mock_autonomous_role_creation_system):
    # Test Case 2.2.3: Create Role - With Tags
    mock_autonomous_role_creation_system.create_role.return_value = RoleGenerationResult(
        request_id="req124",
        generated_role=GeneratedRole(
            role_id="tagged_role_id",
            name="Tagged Role",
            role_type=RoleType.EXPERT,
            domain="general",
            description="A role with tags.",
            system_prompt="You are a tagged role.",
            capabilities=[],
            personality=RolePersonality(communication_style="direct", decision_making_approach="rational", problem_solving_method="analytical", creativity_level=0.5, analytical_depth=0.5, risk_tolerance=0.5, collaboration_preference=0.5),
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            interaction_style=InteractionStyle.FORMAL,
            status=RoleStatus.ACTIVE
        ),
        generation_process={},
        quality_assessment={},
        confidence_score=1.0
    )
    result = runner.invoke(app, ["roles", "create", "Tagged Role", "--description", "A role with tags.", "--tags", "tag1,tag2"])
    assert result.exit_code == 0
    assert "Successfully created role" in result.stdout
    mock_autonomous_role_creation_system.create_role.assert_called_once()
    args, kwargs = mock_autonomous_role_creation_system.create_role.call_args
    assert "tag1" in args[0].requirements.required_capabilities # Tags are added as capabilities
    assert "tag2" in args[0].requirements.required_capabilities

# --- Test Cases for `daip-cli roles update` ---

def test_update_role_success_name_change(mock_role_manager):
    # Test Case 2.2.4: Update Role - Success (Name Change)
    mock_role = MagicMock(spec=Role)
    mock_role.id = "existing_role_id"
    mock_role.name = "Old Name"
    mock_role.description = "Original description"
    mock_role.capabilities = []
    mock_role.system_prompt = "Old prompt"
    mock_role_manager.get_role_by_id.return_value = mock_role
    mock_role_manager.save_role.return_value = True

    result = runner.invoke(app, ["roles", "update", "existing_role_id", "--name", "Updated Role Name"])
    assert result.exit_code == 0
    assert "Successfully updated role" in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with("existing_role_id")
    mock_role_manager.save_role.assert_called_once()
    updated_role = mock_role_manager.save_role.call_args[0][0]
    assert updated_role.name == "Updated Role Name"
    assert updated_role.description == "Original description" # Ensure other fields are unchanged

def test_update_role_add_tags(mock_role_manager):
    # Test Case 2.2.5: Update Role - Add Tags
    mock_role = MagicMock(spec=Role)
    mock_role.id = "existing_role_id"
    mock_role.name = "Test Role"
    mock_role.description = "Original description"
    mock_role.capabilities = ["existing_tag"]
    mock_role.system_prompt = "Old prompt"
    mock_role_manager.get_role_by_id.return_value = mock_role
    mock_role_manager.save_role.return_value = True

    result = runner.invoke(app, ["roles", "update", "existing_role_id", "--add-tags", "new_tag1,new_tag2"])
    assert result.exit_code == 0
    assert "Successfully updated role" in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with("existing_role_id")
    mock_role_manager.save_role.assert_called_once()
    updated_role = mock_role_manager.save_role.call_args[0][0]
    assert "existing_tag" in updated_role.capabilities
    assert "new_tag1" in updated_role.capabilities
    assert "new_tag2" in updated_role.capabilities

def test_update_role_remove_tags(mock_role_manager):
    # Test Case 2.2.6: Update Role - Remove Tags
    mock_role = MagicMock(spec=Role)
    mock_role.id = "existing_role_id"
    mock_role.name = "Test Role"
    mock_role.description = "Original description"
    mock_role.capabilities = ["tag_to_remove", "another_tag"]
    mock_role.system_prompt = "Old prompt"
    mock_role_manager.get_role_by_id.return_value = mock_role
    mock_role_manager.save_role.return_value = True

    result = runner.invoke(app, ["roles", "update", "existing_role_id", "--remove-tags", "tag_to_remove"])
    assert result.exit_code == 0
    assert "Successfully updated role" in result.stdout
    mock_role_manager.get_role_by_id.assert_called_once_with("existing_role_id")
    mock_role_manager.save_role.assert_called_once()
    updated_role = mock_role_manager.save_role.call_args[0][0]
    assert "tag_to_remove" not in updated_role.capabilities
    assert "another_tag" in updated_role.capabilities

def test_update_role_not_found(mock_role_manager):
    # Test Case 2.2.7: Update Role - Not Found
    mock_role_manager.get_role_by_id.return_value = None
    result = runner.invoke(app, ["roles", "update", "non_existent_id", "--name", "New Name"])
    assert result.exit_code != 0
    assert "Error: Role 'non_existent_id' not found." in result.stderr
    mock_role_manager.get_role_by_id.assert_called_once_with("non_existent_id")
    mock_role_manager.save_role.assert_not_called()

# --- Test Cases for `daip-cli roles view` ---

def test_view_role_success(mock_real_role_manager):
    # Test Case 2.2.8: View Role - Success
    mock_role_data = {
        "id": "view_role_id",
        "name": "Viewer Role",
        "description": "A role for viewing purposes.",
        "system_prompt": "You are a viewer.",
        "capabilities": ["read_data", "generate_reports"],
        "category": "analysis",
        "specialties": ["data_visualization"],
        "experience_years": 5
    }
    mock_real_role_manager.get_role.return_value = mock_role_data

    result = runner.invoke(app, ["roles", "view", "view_role_id"])
    assert result.exit_code == 0
    assert "Role Details: Viewer Role (view_role_id)" in result.stdout
    assert "Description: A role for viewing purposes." in result.stdout
    assert "Capabilities: read_data, generate_reports" in result.stdout
    assert "Category: analysis" in result.stdout
    assert "Experience Years: 5" in result.stdout
    mock_real_role_manager.get_role.assert_called_once_with("view_role_id")

def test_view_role_not_found(mock_real_role_manager):
    # Test Case 2.2.9: View Role - Not Found
    mock_real_role_manager.get_role.return_value = None
    result = runner.invoke(app, ["roles", "view", "non_existent_id"])
    assert result.exit_code != 0
    assert "Error: Role 'non_existent_id' not found." in result.stderr
    mock_real_role_manager.get_role.assert_called_once_with("non_existent_id")
