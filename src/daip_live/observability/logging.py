"""JSON structured logging for observability.

This module provides structured JSON logging with contextual information.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any


class LogLevel(Enum):
    """Log level enumeration."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra context fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno",
                "pathname", "filename", "module", "exc_info",
                "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "message",
                "asctime", "levelname"
            }:
                log_data[key] = value

        return json.dumps(log_data)


class StructuredLogger:
    """Structured logger with JSON formatting."""

    _loggers: Dict[str, "StructuredLogger"] = {}

    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        """Initialize a structured logger.

        Args:
            name: Logger name
            context: Global context to include in all log messages
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.context = context or {}

        # Set up JSON handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)

    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal logging method.

        Args:
            level: Log level
            message: Log message
            **kwargs: Additional context fields
        """
        extra = {**self.context, **kwargs}
        self.logger.log(level.value, message, extra=extra)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)


def get_logger(name: str, context: Optional[Dict[str, Any]] = None) -> StructuredLogger:
    """Get or create a structured logger.

    Args:
        name: Logger name
        context: Global context to include in all log messages

    Returns:
        StructuredLogger instance
    """
    if name not in StructuredLogger._loggers:
        StructuredLogger._loggers[name] = StructuredLogger(name, context)
    return StructuredLogger._loggers[name]
