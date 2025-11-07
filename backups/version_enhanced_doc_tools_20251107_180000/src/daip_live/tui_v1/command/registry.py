"""
Command Registry for newP6 TUI

Manages registration and retrieval of command handlers.
"""

from typing import Dict, List, Optional, Any


class CommandRegistry:
    """Registry for command handlers"""

    def __init__(self):
        self._handlers: Dict[str, Any] = {}

    def register(self, command: str, handler) -> None:
        """Register a command handler"""
        self._handlers[command] = handler

    def get_handler(self, command: str) -> Optional[Any]:
        """Get a registered command handler"""
        return self._handlers.get(command)

    def list_commands(self) -> List[str]:
        """List all registered commands"""
        return list(self._handlers.keys())

    def has_command(self, command: str) -> bool:
        """Check if a command is registered"""
        return command in self._handlers

    def unregister(self, command: str) -> bool:
        """Unregister a command handler"""
        if command in self._handlers:
            del self._handlers[command]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered commands"""
        self._handlers.clear()

    def count(self) -> int:
        """Get the number of registered commands"""
        return len(self._handlers)