import pytest
from unittest.mock import MagicMock

from src.kernel.tool_executor import ToolExecutor


@pytest.fixture
def mock_tool_function() -> MagicMock:
    """Fixture for a mocked tool function."""
    # The tool executor wraps the result in a dictionary
    return MagicMock(return_value="Success")


@pytest.fixture
def tool_executor() -> ToolExecutor:
    """Fixture for the ToolExecutor instance."""
    return ToolExecutor()


def test_execute_with_correct_arguments(tool_executor: ToolExecutor, mock_tool_function: MagicMock) -> None:
    """Test tool execution with a single tool_call argument."""
    tool_name = "sample_tool"
    tool_args = {"param": "value"}
    tool_definition = {
        "function": {
            "name": tool_name,
            "description": "A sample tool.",
            "parameters": {}
        }
    }
    # Register the mock tool directly with the executor
    tool_executor.register_tool(mock_tool_function, tool_definition)

    # The signature accepts a single dictionary-like argument.
    tool_call = {"name": tool_name, "arguments": tool_args}
    response = tool_executor.execute(tool_call["name"], **tool_call["arguments"])

    # Assert that the correct tool function was called with the correct arguments
    mock_tool_function.assert_called_once_with(**tool_args)
    assert response["status"] == "success"
    assert response["result"] == "Success"