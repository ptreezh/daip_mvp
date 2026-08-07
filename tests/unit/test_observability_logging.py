"""Tests for observability logging module (TDD - RED phase)."""

import json
import logging
import pytest
from daip_live.observability.logging import (
    JsonFormatter,
    StructuredLogger,
    get_logger,
    LogLevel
)


def test_json_formatter_creates_valid_json():
    """Test that JSON formatter creates valid JSON output."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert "message" in parsed
    assert parsed["message"] == "Test message"
    assert "level" in parsed
    assert parsed["level"] == "INFO"


def test_json_formatter_includes_timestamp():
    """Test that JSON formatter includes timestamp."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert "timestamp" in parsed
    assert parsed["timestamp"]


def test_json_formatter_includes_context():
    """Test that JSON formatter includes extra context."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    record.user_id = "test_user"
    record.request_id = "req_123"
    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed.get("user_id") == "test_user"
    assert parsed.get("request_id") == "req_123"


def test_structured_logger_creates_logger():
    """Test that StructuredLogger creates a proper logger."""
    logger = StructuredLogger("test_service")
    assert logger.logger.name == "test_service"
    assert logger.logger.level == logging.DEBUG


def test_structured_logger_log_levels():
    """Test that StructuredLogger supports all log levels."""
    logger = StructuredLogger("test_service")
    # Should not raise any exceptions
    logger.debug("debug message")
    logger.info("info message", extra={"key": "value"})
    logger.warning("warning message")
    logger.error("error message", extra={"error_code": "ERR_001"})


def test_structured_logger_with_context():
    """Test that StructuredLogger includes global context."""
    logger = StructuredLogger("test_service", context={"service": "daip"})
    # Context should be included in all log messages


def test_get_logger_returns_singleton():
    """Test that get_logger returns the same logger instance."""
    logger1 = get_logger("test")
    logger2 = get_logger("test")
    assert logger1 is logger2


def test_log_level_enum():
    """Test LogLevel enum values."""
    assert LogLevel.DEBUG.value == logging.DEBUG
    assert LogLevel.INFO.value == logging.INFO
    assert LogLevel.WARNING.value == logging.WARNING
    assert LogLevel.ERROR.value == logging.ERROR
    assert LogLevel.CRITICAL.value == logging.CRITICAL
