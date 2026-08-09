"""
Command Processing Module for newP6 TUI

Provides command parsing, registration, and handling functionality.
"""

from .models import Command, CommandInfo, CommandResult
from .parser import CommandParser
from .registry import CommandRegistry

# Export main classes
__all__ = [
    "Command",
    "CommandResult",
    "CommandInfo",
    "CommandParser",
    "CommandRegistry",
]
