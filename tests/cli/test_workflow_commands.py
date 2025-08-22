"""
Tests for the workflow management CLI commands.
"""

import json
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock, AsyncMock

from src.cli.main import app

runner = CliRunner()

# Mock data for a primitive
MOCK_PRIMITIVE_INFO_1 = MagicMock()
MOCK_PRIMITIVE_INFO_1.name = "test_workflow_1"
MOCK_PRIMITIVE_INFO_1.description = "A test workflow for testing."
MOCK_PRIMITIVE_INFO_1.type = "WORKFLOW"

MOCK_PRIMITIVE_INFO_2 = MagicMock()
MOCK_PRIMITIVE_INFO_2.name = "another_workflow"
MOCK_PRIMITIVE_INFO_2.description = "Another test workflow."
MOCK_PRIMITIVE_INFO_2.type = "PRIMITIVE"

@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_list_success(MockPrimitiveRegistry):
    """Test `workflow list` when primitives are available."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_registry.list_primitives.return_value = [MOCK_PRIMITIVE_INFO_1, MOCK_PRIMITIVE_INFO_2]

    # Act
    result = runner.invoke(app, ["workflow", "list"])

    # Assert
    assert result.exit_code == 0
    assert "Available Workflows (Primitives)" in result.stdout
    assert MOCK_PRIMITIVE_INFO_1.name in result.stdout
    assert MOCK_PRIMITIVE_INFO_1.description in result.stdout
    assert MOCK_PRIMITIVE_INFO_2.name in result.stdout
    mock_registry.list_primitives.assert_called_once()

@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_list_empty(MockPrimitiveRegistry):
    """Test `workflow list` when no primitives are available."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_registry.list_primitives.return_value = []

    # Act
    result = runner.invoke(app, ["workflow", "list"])

    # Assert
    assert result.exit_code == 0
    assert "No workflows (primitives) are currently registered." in result.stdout
    mock_registry.list_primitives.assert_called_once()


@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_create_success(MockPrimitiveRegistry):
    """Test `workflow create` successfully."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_registry.validate_primitive.return_value = True
    mock_registry.register_primitive.return_value = True
    workflow_def = {"name": "my_workflow", "steps": []}

    # Act
    with runner.isolated_filesystem():
        with open("workflow.json", "w") as f:
            json.dump(workflow_def, f)
        
        result = runner.invoke(app, ["workflow", "create", "--definition-file", "workflow.json"])

    # Assert
    assert result.exit_code == 0
    assert "Successfully validated and registered workflow 'my_workflow'" in result.stdout
    mock_registry.validate_primitive.assert_called_once_with(workflow_def)
    mock_registry.register_primitive.assert_called_once_with(workflow_def)


def test_workflow_create_file_not_found():
    """Test `workflow create` with a non-existent file."""
    # Act
    result = runner.invoke(app, ["workflow", "create", "--definition-file", "nonexistent.json"])

    # Assert
    assert result.exit_code != 0

@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_create_invalid_json(MockPrimitiveRegistry):
    """Test `workflow create` with an invalid JSON file."""
    # Act
    with runner.isolated_filesystem():
        with open("workflow.json", "w") as f:
            f.write("this is not json")
        
        result = runner.invoke(app, ["workflow", "create", "--definition-file", "workflow.json"])

    # Assert
    assert result.exit_code == 1
    assert "Error: Invalid JSON in definition file" in result.stdout
    MockPrimitiveRegistry.return_value.validate_primitive.assert_not_called()


@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_create_validation_fails(MockPrimitiveRegistry):
    """Test `workflow create` when the definition fails validation."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_registry.validate_primitive.side_effect = ValueError("Missing 'steps' key")
    workflow_def = {"name": "my_workflow"}

    # Act
    with runner.isolated_filesystem():
        with open("workflow.json", "w") as f:
            json.dump(workflow_def, f)
        
        result = runner.invoke(app, ["workflow", "create", "--definition-file", "workflow.json"])

    # Assert
    assert result.exit_code == 1
    assert "Workflow validation failed: Missing 'steps' key" in result.stdout
    mock_registry.validate_primitive.assert_called_once_with(workflow_def)
    mock_registry.register_primitive.assert_not_called()


@patch('src.cli.commands.workflow_commands.WorkflowEngine')
@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_execute_success(MockPrimitiveRegistry, MockWorkflowEngine):
    """Test `workflow execute` successfully."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_engine = MockWorkflowEngine.return_value
    
    mock_registry.get_primitive.return_value = {"name": "my_workflow", "steps": []}
    # Mock the async method
    mock_engine.execute_workflow = AsyncMock(return_value="exec_123")

    # Act
    result = runner.invoke(app, ["workflow", "execute", "my_workflow", "--params", '{"foo": "bar"}'])

    # Assert
    assert result.exit_code == 0
    assert "Workflow 'my_workflow' started successfully." in result.stdout
    assert "Execution ID: exec_123" in result.stdout
    mock_registry.get_primitive.assert_called_once_with("my_workflow")
    mock_engine.execute_workflow.assert_awaited_once()


@patch('src.cli.commands.workflow_commands.PrimitiveRegistry')
def test_workflow_execute_not_found(MockPrimitiveRegistry):
    """Test `workflow execute` when the workflow is not found."""
    # Arrange
    mock_registry = MockPrimitiveRegistry.return_value
    mock_registry.get_primitive.return_value = None

    # Act
    result = runner.invoke(app, ["workflow", "execute", "nonexistent_workflow"])

    # Assert
    assert result.exit_code == 1
    assert "Error: Workflow 'nonexistent_workflow' not found." in result.stdout


def test_workflow_execute_invalid_params():
    """Test `workflow execute` with invalid JSON parameters."""
    # Act
    result = runner.invoke(app, ["workflow", "execute", "my_workflow", "--params", "not-json"])

    # Assert
    assert result.exit_code == 1
    assert "Error: Invalid JSON format for --params." in result.stdout