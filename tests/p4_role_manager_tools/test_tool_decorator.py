"""Tests for the @tool decorator."""

from pydantic import BaseModel

from daip_live.p4_role_manager_tools.tools import tool


def test_decorator_creates_pydantic_model():
    """
    Tests that the @tool decorator correctly inspects a function signature
    and dynamically creates a Pydantic model for its arguments.
    """

    @tool
    def add(a: int, b: int = 5) -> int:
        """Adds two numbers together."""
        return a + b

    # 1. Check if the input_schema was created and is a Pydantic model
    assert hasattr(add, "input_schema")
    assert isinstance(add.input_schema, type)
    assert issubclass(add.input_schema, BaseModel)

    # 2. Inspect the fields of the generated model
    schema_fields = add.input_schema.model_fields
    assert "a" in schema_fields
    assert "b" in schema_fields

    # 3. Check the type and default value of the fields
    assert schema_fields["a"].annotation is int
    assert schema_fields["a"].is_required()

    assert schema_fields["b"].annotation is int
    assert schema_fields["b"].default == 5

    # 4. Check that the original function's metadata is preserved
    assert add.__name__ == "add"
    assert add.__doc__ == "Adds two numbers together."


def test_decorator_handles_no_arguments():
    """
    Tests that the decorator works correctly on a function with no arguments.
    """

    @tool
    def get_time() -> str:
        """Returns the current time."""
        return "now"

    assert hasattr(get_time, "input_schema")
    assert isinstance(get_time.input_schema, type)
    assert issubclass(get_time.input_schema, BaseModel)
    assert len(get_time.input_schema.model_fields) == 0
