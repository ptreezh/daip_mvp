"""Defines the custom exception hierarchy for the DAIP-LIVE application."""


class DAIPError(Exception):
    """Base exception for all application-specific errors."""
    pass


class ModelError(DAIPError):
    """Errors related to the Model Provider (P3)."""
    pass


class ModelConnectionError(ModelError):
    """Represents an error in connecting to the model provider."""
    pass


class ModelAuthenticationError(ModelError):
    """Represents an authentication error with the model provider."""
    pass


class ToolError(DAIPError):
    """Errors related to Tool execution (P4)."""
    pass


class ToolInputError(ToolError):
    """Represents an error due to invalid input for a tool."""
    pass


class ToolPermissionError(ToolError):
    """Represents an error due to insufficient permissions to use a tool."""
    pass
