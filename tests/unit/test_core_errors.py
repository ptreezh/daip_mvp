"""Tests for unified error handling (TDD - RED phase)."""

import pytest
from daip_live.core.exceptions import (
    DAIPError,
    ModelError,
    ValidationError,
    ConfigurationError,
    ErrorContext,
    ErrorHandler
)


def test_daip_error_creation():
    """Test creating base DAIPError."""
    error = DAIPError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"


def test_daip_error_with_context():
    """Test DAIPError with context."""
    error = DAIPError("Test error", context={"key": "value"})
    assert error.context["key"] == "value"


def test_model_error_creation():
    """Test creating ModelError."""
    error = ModelError("Model failed", model="ollama", provider="local")
    assert error.model == "ollama"
    assert error.provider == "local"


def test_validation_error_creation():
    """Test creating ValidationError."""
    error = ValidationError("Invalid input", field="email")
    assert error.field == "email"


def test_configuration_error_creation():
    """Test creating ConfigurationError."""
    error = ConfigurationError("Missing config", key="api_key")
    assert error.key == "api_key"


def test_error_context_creation():
    """Test creating ErrorContext."""
    context = ErrorContext(
        component="test",
        operation="test_op",
        details={"test": "value"}
    )
    assert context.component == "test"
    assert context.operation == "test_op"


def test_error_handler_creation():
    """Test creating ErrorHandler."""
    handler = ErrorHandler()
    assert handler is not None


def test_error_handler_handle_error():
    """Test ErrorHandler handles errors."""
    handler = ErrorHandler()
    error = DAIPError("Test error")
    # Should not raise
    handler.handle(error)
    # Error should be logged


def test_error_handler_with_callback():
    """Test ErrorHandler with custom callback."""
    handler = ErrorHandler()
    captured = []

    def callback(err):
        captured.append(err)

    handler.register_callback(callback)
    error = DAIPError("Test error")
    handler.handle(error)
    assert len(captured) == 1
    assert captured[0] is error
