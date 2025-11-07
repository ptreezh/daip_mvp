"""
Command Models for newP6 TUI

Defines data structures for command parsing and handling.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Command:
    """Represents a parsed command with all its components"""
    raw: str
    command: str
    action: Optional[str] = None
    args: List[str] = None
    options: Dict[str, Any] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.options is None:
            self.options = {}

    @property
    def full_command(self) -> str:
        """Get the full command with action (e.g., 'session.show')"""
        if self.action:
            return f"{self.command}.{self.action}"
        return self.command

    def has_option(self, option: str) -> bool:
        """Check if command has a specific option"""
        return option in self.options

    def get_option(self, option: str, default: Any = None) -> Any:
        """Get option value with default"""
        return self.options.get(option, default)


@dataclass
class CommandResult:
    """Represents the result of command execution"""
    success: bool
    message: str
    data: Any = None

    @classmethod
    def success_result(cls, message: str, data: Any = None) -> "CommandResult":
        """Create a successful result"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_result(cls, message: str, data: Any = None) -> "CommandResult":
        """Create an error result"""
        return cls(success=False, message=message, data=data)


@dataclass
class CommandInfo:
    """Information about a registered command"""
    command: str
    description: str
    usage: str
    handler_class: str
    requires_args: bool = False
    allowed_options: List[str] = None

    def __post_init__(self):
        if self.allowed_options is None:
            self.allowed_options = []