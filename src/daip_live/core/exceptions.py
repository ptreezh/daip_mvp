"""Defines the custom exception hierarchy for the DAIP-LIVE application."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
import logging


class DAIPError(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize a DAIP error.

        Args:
            message: Error message
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.error_code = self.__class__.__name__

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context
        }


class ModelError(DAIPError):
    """Errors related to the Model Provider (P3)."""

    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.model = model
        self.provider = provider


class ModelConnectionError(ModelError):
    """Represents an error in connecting to the model provider."""
    pass


class ModelAuthenticationError(ModelError):
    """Represents an authentication error with the model provider."""
    pass


class ToolError(DAIPError):
    """Errors related to Tool execution (P4)."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.tool_name = tool_name


class ToolInputError(ToolError):
    """Represents an error due to invalid input for a tool."""
    pass


class ToolPermissionError(ToolError):
    """Represents an error due to insufficient permissions to use a tool."""
    pass


class ValidationError(DAIPError):
    """Error from input/config validation."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.field = field
        self.value = value


class ConfigurationError(DAIPError):
    """Error from configuration."""

    def __init__(
        self,
        message: str,
        key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.key = key


class PermissionDenied(DAIPError):
    """Error from permission system."""

    def __init__(
        self,
        message: str,
        permission: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, context)
        self.permission = permission


# For backwards compatibility
ModelProviderError = ModelError
PermissionError = PermissionDenied


@dataclass
class ErrorContext:
    """Structured error context."""
    component: str
    operation: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class ErrorHandler:
    """Centralized error handler with logging and callbacks."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.callbacks: List[Callable[[DAIPError], None]] = []

    def register_callback(self, callback: Callable[[DAIPError], None]) -> None:
        """Register an error callback.

        Args:
            callback: Function to call on error
        """
        self.callbacks.append(callback)

    def handle(self, error: Exception) -> None:
        """Handle an error.

        Args:
            error: The error to handle
        """
        if isinstance(error, DAIPError):
            self._handle_daip_error(error)
        else:
            self._handle_generic_error(error)

    def _handle_daip_error(self, error: DAIPError) -> None:
        """Handle a DAIP error."""
        self.logger.error(
            f"[{error.error_code}] {error.message}",
            extra={"context": error.context}
        )
        for callback in self.callbacks:
            try:
                callback(error)
            except Exception:
                pass

    def _handle_generic_error(self, error: Exception) -> None:
        """Handle a generic exception."""
        self.logger.error(f"Unexpected error: {error}", exc_info=error)


# Global error handler instance
_global_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _global_handler
    if _global_handler is None:
        _global_handler = ErrorHandler()
    return _global_handler


def handle_error(error: Exception) -> None:
    """Handle an error using the global handler.

    Args:
        error: The error to handle
    """
    get_error_handler().handle(error)
