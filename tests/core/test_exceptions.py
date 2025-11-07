import pytest

from daip_live.core.exceptions import (
    DAIPError,
    ModelAuthenticationError,
    ModelConnectionError,
    ModelError,
    ToolError,
    ToolInputError,
    ToolPermissionError,
)


def test_raise_daip_error():
    """Tests that a base DAIPError can be raised and caught."""
    with pytest.raises(DAIPError):
        raise DAIPError("A generic DAIP error occurred.")


def test_exception_hierarchy():
    """Tests that the custom exceptions inherit from the correct base classes."""
    assert issubclass(ModelError, DAIPError)
    assert issubclass(ToolError, DAIPError)
    assert issubclass(ModelConnectionError, ModelError)
    assert issubclass(ModelAuthenticationError, ModelError)
    assert issubclass(ToolInputError, ToolError)
    assert issubclass(ToolPermissionError, ToolError)


def test_catch_specific_exception():
    """Tests that a specific exception can be caught by its more generic base class."""
    with pytest.raises(DAIPError):  # Catching the base error
        raise ToolInputError("Invalid input provided.")

    with pytest.raises(ModelError): # Catching the intermediate error
        raise ModelConnectionError("Could not connect.")
