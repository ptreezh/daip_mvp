"""Tests for the ToolManager."""

from typing import Any, Dict, List

import pytest

from daip_live.core.models import SessionContext, ToolPermissionConfig
from daip_live.p4_role_manager_tools.tool_manager import (
    ToolInputError,
    ToolManager,
    ToolNotFoundError,
    ToolPermissionError,
    ToolPermissionRequest,
    ToolPreconditionError,
    ToolTimeoutError,
)
from daip_live.p4_role_manager_tools.tools import tool


# A simple tool for testing
@tool
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

@tool(tool_type="write", resource_arg="file_path")
def write_file_tool(file_path: str, content: str) -> str:
    """Writes content to a file."""
    return f"Wrote '{content}' to '{file_path}'"

@tool(tool_type="read", resource_arg="file_path")
def read_file_tool(file_path: str) -> str:
    """Reads content from a file."""
    return f"Content of '{file_path}'"


class TestToolManagerDiscovery:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")

    def test_register_tool_success(self):
        """Tests that a valid tool can be registered."""
        self.manager.register_tool(add)
        assert "add" in self.manager._registry

    def test_register_non_tool_fails(self):
        """Tests that registering a non-decorated function fails."""
        def non_tool_func():
            pass
        with pytest.raises(ValueError):
            self.manager.register_tool(non_tool_func)

    def test_discovery_stage_tool_not_found(self):
        """
        Tests Stage 1: Discovery.
        Asserts that executing a non-existent tool raises ToolNotFoundError.
        """
        session_context = SessionContext()
        with pytest.raises(ToolNotFoundError) as excinfo:
            self.manager.execute_tool("subtract", {"a": 10, "b": 5}, session_context)

        assert "Tool 'subtract' not found" in str(excinfo.value)

    def test_full_execution_success_path_simplified(self):
        """
        Tests a simplified happy path through registration, discovery, and execution.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        result = self.manager.execute_tool("add", {"a": 10, "b": 5}, session_context)

        assert result == "15"


class TestToolManagerInputValidation:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")

    def test_validation_stage_missing_argument(self):
        """
        Tests Stage 2: Input Validation.
        Asserts that a missing required argument raises ToolInputError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        with pytest.raises(ToolInputError) as excinfo:
            self.manager.execute_tool("add", {"a": 10}, session_context)

        assert "Input validation failed" in str(excinfo.value)
        assert "Field required" in str(excinfo.value)

    def test_validation_stage_wrong_type(self):
        """
        Tests Stage 2: Input Validation.
        Asserts that an argument with the wrong type raises ToolInputError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        with pytest.raises(ToolInputError) as excinfo:
            self.manager.execute_tool("add", {"a": 10, "b": "five"}, session_context)

        assert "Input validation failed" in str(excinfo.value)
        assert "Input should be a valid integer" in str(excinfo.value)


class TestToolManagerPreconditionCheck:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")

    def test_write_after_read_fails_if_not_read(self):
        """
        Tests Stage 3: Precondition Check (Write-After-Read).
        Asserts that a write tool fails if the resource was not recently read.
        """
        self.manager.register_tool(write_file_tool)
        session_context = SessionContext(recently_read_resources=set())

        with pytest.raises(ToolPreconditionError) as excinfo:
            self.manager.execute_tool("write_file_tool", {"file_path": "test.txt", "content": "hello"}, session_context)

        assert "Resource 'test.txt' was not recently read" in str(excinfo.value)

    def test_write_after_read_succeeds_if_read(self):
        """
        Tests Stage 3: Precondition Check (Write-After-Read).
        Asserts that a write tool succeeds if the resource was recently read.
        """
        self.manager.register_tool(write_file_tool)
        session_context = SessionContext(recently_read_resources={"test.txt"})

        result = self.manager.execute_tool("write_file_tool", {"file_path": "test.txt", "content": "hello"}, session_context)

        assert "Wrote 'hello' to 'test.txt'" in result

    def test_read_tool_adds_to_recently_read_resources(self):
        """
        Tests that a read tool adds its target resource to recently_read_resources.
        """
        self.manager.register_tool(read_file_tool)
        session_context = SessionContext(recently_read_resources=set())

        self.manager.execute_tool("read_file_tool", {"file_path": "read_me.txt"}, session_context)

        assert "read_me.txt" in session_context.recently_read_resources


class TestToolManagerPermissionCheck:
    def setup_method(self):
        self.manager = ToolManager()

    def test_permission_check_deny_fails(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'deny' permission raises ToolPermissionError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to deny 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow", # Default to allow, but specifically deny 'add'
            tools={
                "add": "deny"
            }
        )

        with pytest.raises(ToolPermissionError) as excinfo:
            self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)

        assert "Tool 'add' is denied by policy." in str(excinfo.value)

    def test_permission_check_allow_succeeds(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'allow' permission succeeds.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to allow 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="deny", # Default to deny, but specifically allow 'add'
            tools={
                "add": "allow"
            }
        )

        result = self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)
        assert result == "3"

    def test_permission_check_ask_raises_request(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'ask' permission raises ToolPermissionRequest.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to ask for 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow",
            tools={
                "add": "ask"
            }
        )

        with pytest.raises(ToolPermissionRequest) as excinfo:
            self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)

        assert "Permission required for tool 'add'" in str(excinfo.value)

    def test_permission_check_ask_with_confirmation_succeeds(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'ask' permission succeeds when confirmation is granted.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to ask for 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow",
            tools={
                "add": "ask"
            }
        )

        # Call with confirmation_granted=True
        result = self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context, confirmation_granted=True)
        assert result == "3"


class TestToolManagerInputValidation:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")

    def test_validation_stage_missing_argument(self):
        """
        Tests Stage 2: Input Validation.
        Asserts that a missing required argument raises ToolInputError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        with pytest.raises(ToolInputError) as excinfo:
            self.manager.execute_tool("add", {"a": 10}, session_context)

        assert "Input validation failed" in str(excinfo.value)
        assert "Field required" in str(excinfo.value)

    def test_validation_stage_wrong_type(self):
        """
        Tests Stage 2: Input Validation.
        Asserts that an argument with the wrong type raises ToolInputError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        with pytest.raises(ToolInputError) as excinfo:
            self.manager.execute_tool("add", {"a": 10, "b": "five"}, session_context)

        assert "Input validation failed" in str(excinfo.value)
        assert "Input should be a valid integer" in str(excinfo.value)


class TestToolManagerPreconditionCheck:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")

    def test_write_after_read_fails_if_not_read(self):
        """
        Tests Stage 3: Precondition Check (Write-After-Read).
        Asserts that a write tool fails if the resource was not recently read.
        """
        self.manager.register_tool(write_file_tool)
        session_context = SessionContext(recently_read_resources=set())

        with pytest.raises(ToolPreconditionError) as excinfo:
            self.manager.execute_tool("write_file_tool", {"file_path": "test.txt", "content": "hello"}, session_context)

        assert "Resource 'test.txt' was not recently read" in str(excinfo.value)

    def test_write_after_read_succeeds_if_read(self):
        """
        Tests Stage 3: Precondition Check (Write-After-Read).
        Asserts that a write tool succeeds if the resource was recently read.
        """
        self.manager.register_tool(write_file_tool)
        session_context = SessionContext(recently_read_resources={"test.txt"})

        result = self.manager.execute_tool("write_file_tool", {"file_path": "test.txt", "content": "hello"}, session_context)

        assert "Wrote 'hello' to 'test.txt'" in result

    def test_read_tool_adds_to_recently_read_resources(self):
        """
        Tests that a read tool adds its target resource to recently_read_resources.
        """
        self.manager.register_tool(read_file_tool)
        session_context = SessionContext(recently_read_resources=set())

        self.manager.execute_tool("read_file_tool", {"file_path": "read_me.txt"}, session_context)

        assert "read_me.txt" in session_context.recently_read_resources


class TestToolManagerPermissionCheck:
    def setup_method(self):
        self.manager = ToolManager()

    def test_permission_check_deny_fails(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'deny' permission raises ToolPermissionError.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to deny 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow", # Default to allow, but specifically deny 'add'
            tools={
                "add": "deny"
            }
        )

        with pytest.raises(ToolPermissionError) as excinfo:
            self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)

        assert "Tool 'add' is denied by policy." in str(excinfo.value)

    def test_permission_check_allow_succeeds(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'allow' permission succeeds.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to allow 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="deny", # Default to deny, but specifically allow 'add'
            tools={
                "add": "allow"
            }
        )

        result = self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)
        assert result == "3"

    def test_permission_check_ask_raises_request(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'ask' permission raises ToolPermissionRequest.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to ask for 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow",
            tools={
                "add": "ask"
            }
        )

        with pytest.raises(ToolPermissionRequest) as excinfo:
            self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context)

        assert "Permission required for tool 'add'" in str(excinfo.value)

    def test_permission_check_ask_with_confirmation_succeeds(self):
        """
        Tests Stage 4: Permission Check.
        Asserts that a tool with 'ask' permission succeeds when confirmation is granted.
        """
        self.manager.register_tool(add)
        session_context = SessionContext()

        # Mock ToolPermissionConfig to ask for 'add' tool
        self.manager.tool_permission_config = ToolPermissionConfig(
            default="allow",
            tools={
                "add": "ask"
            }
        )

        # Call with confirmation_granted=True
        result = self.manager.execute_tool("add", {"a": 1, "b": 2}, session_context, confirmation_granted=True)
        assert result == "3"


class TestToolManagerExecutionAndFormatting:
    def setup_method(self):
        self.manager = ToolManager()
        self.manager.tool_permission_config = ToolPermissionConfig(default="allow")
        self.session_context = SessionContext()

    def test_execution_success(self):
        """
        Tests Stage 5: Execution.
        Asserts that a tool executes successfully and returns its result.
        """
        @tool
        def echo(message: str) -> str:
            return message

        self.manager.register_tool(echo)
        result = self.manager.execute_tool("echo", {"message": "hello"}, self.session_context)
        assert result == "hello"

    def test_execution_timeout(self):
        """
        Tests Stage 5: Execution with timeout.
        Asserts that a tool execution exceeding timeout raises ToolTimeoutError.
        """
        @tool
        def long_running_tool() -> str:
            # Simulate a timeout by raising an exception that would be caught by the timeout mechanism
            raise TimeoutError("Tool execution timed out")

        self.manager.register_tool(long_running_tool)

        # Temporarily set a very short timeout for testing purposes
        # In a real scenario, this would be configured externally
        self.manager.tool_timeout = 0.001 # Very short timeout

        with pytest.raises(ToolTimeoutError) as excinfo:
            self.manager.execute_tool("long_running_tool", {}, self.session_context)

        assert "Tool 'long_running_tool' timed out." in str(excinfo.value)

    def test_execution_exception_handling(self):
        """
        Tests Stage 5: Execution with unexpected exception.
        Asserts that an unexpected exception during tool execution is caught and formatted.
        """
        @tool
        def tool_with_error() -> str:
            raise ValueError("Something went wrong")

        self.manager.register_tool(tool_with_error)

        result = self.manager.execute_tool("tool_with_error", {}, self.session_context)
        assert "Error executing tool 'tool_with_error': ValueError('Something went wrong')" in result

    def test_result_formatting_string(self):
        """
        Tests Stage 6: Result Formatting for string results.
        """
        @tool
        def get_string() -> str:
            return "This is a string result."

        self.manager.register_tool(get_string)
        result = self.manager.execute_tool("get_string", {}, self.session_context)
        assert result == "This is a string result."

    def test_result_formatting_non_string(self):
        """
        Tests Stage 6: Result Formatting for non-string results (e.g., dict, list).
        """
        @tool
        def get_dict() -> Dict[str, Any]:
            return {"key": "value", "number": 123}

        self.manager.register_tool(get_dict)
        result = self.manager.execute_tool("get_dict", {}, self.session_context)
        assert result == "{'key': 'value', 'number': 123}"

        @tool
        def get_list() -> List[str]:
            return ["item1", "item2"]

        self.manager.register_tool(get_list)
        result = self.manager.execute_tool("get_list", {}, self.session_context)
        assert result == "['item1', 'item2']"
