"""
Base Command Handler for newP6 TUI

Provides base functionality for all command handlers.
"""

from abc import ABC, abstractmethod
from typing import List

from ..models import CommandResult


class BaseCommandHandler(ABC):
    """Base class for all command handlers"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "Base command handler"

    @abstractmethod
    def handle(self, args: List[str]) -> CommandResult:
        """Handle the command with given arguments"""
        pass

    def validate_args(self, args: List[str], min_args: int = 0, max_args: int = None) -> bool:
        """Validate argument count"""
        if len(args) < min_args:
            return False
        if max_args is not None and len(args) > max_args:
            return False
        return True

    def create_usage_message(self, usage: str) -> str:
        """Create a usage error message"""
        return f"Usage: {usage}"

    def create_error_message(self, error: str) -> str:
        """Create an error message"""
        return f"Error: {error}"