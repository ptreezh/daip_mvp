"""
Command System

This module provides the Command pattern implementation for the MVVM architecture.
It enables encapsulation of actions that can be executed, validated, and potentially
undone/redone.
"""

from typing import Callable, Any, Optional, Union
from abc import ABC, abstractmethod
import asyncio


class Command(ABC):
    """
    Abstract base class for Command pattern implementation.
    
    Commands encapsulate an action that can be executed with optional parameters
    and validation.
    """
    
    def __init__(
        self, 
        execute_func: Callable, 
        can_execute_func: Optional[Callable[[], bool]] = None
    ):
        """
        Initialize the command.
        
        Args:
            execute_func: Function to execute when command is invoked
            can_execute_func: Optional function to validate if command can execute
        """
        self.execute_func = execute_func
        self.can_execute_func = can_execute_func or (lambda: True)
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the command with given parameters.
        
        Args:
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            Result of command execution
        """
        pass
    
    def can_execute(self) -> bool:
        """
        Check if the command can be executed.
        
        Returns:
            True if command can execute, False otherwise
        """
        return self.can_execute_func()


class SyncCommand(Command):
    """
    Synchronous Command implementation.
    
    This command executes synchronously without async/await support.
    """
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the synchronous command.
        
        Args:
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            Result of command execution
            
        Raises:
            RuntimeError: If command cannot be executed
        """
        if not self.can_execute():
            raise RuntimeError("Command cannot execute")
        
        return self.execute_func(*args, **kwargs)


class AsyncCommand(Command):
    """
    Asynchronous Command implementation.
    
    This command supports async/await for asynchronous operations.
    """
    
    def __init__(
        self, 
        execute_func: Callable, 
        can_execute_func: Optional[Callable[[], bool]] = None,
        sync_fallback: bool = True
    ):
        """
        Initialize the async command.
        
        Args:
            execute_func: Function to execute when command is invoked
            can_execute_func: Optional function to validate if command can execute
            sync_fallback: Whether to fallback to sync execution if not in async context
        """
        super().__init__(execute_func, can_execute_func)
        self.sync_fallback = sync_fallback
    
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the asynchronous command.
        
        Args:
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            Result of command execution
            
        Raises:
            RuntimeError: If command cannot be executed
        """
        if not self.can_execute():
            raise RuntimeError("Command cannot execute")
        
        if asyncio.iscoroutinefunction(self.execute_func):
            return await self.execute_func(*args, **kwargs)
        elif self.sync_fallback:
            # Fall back to sync execution
            return self.execute_func(*args, **kwargs)
        else:
            raise RuntimeError("AsyncCommand requires an async function or sync fallback")


# Convenience alias for backward compatibility or default usage
CommandType = Union[SyncCommand, AsyncCommand]


def create_command(
    execute_func: Callable, 
    can_execute_func: Optional[Callable[[], bool]] = None,
    is_async: bool = False
) -> CommandType:
    """
    Factory function to create appropriate command type.
    
    Args:
        execute_func: Function to execute when command is invoked
        can_execute_func: Optional function to validate if command can execute
        is_async: Whether to create an async command
        
    Returns:
        Appropriate command type instance
    """
    if is_async:
        return AsyncCommand(execute_func, can_execute_func)
    else:
        return SyncCommand(execute_func, can_execute_func)


# For backward compatibility with simple command usage
class SimpleCommand:
    """
    Simple command wrapper for basic usage without validation.
    """
    
    def __init__(self, execute_func: Callable):
        """
        Initialize the simple command.
        
        Args:
            execute_func: Function to execute when command is invoked
        """
        self.execute_func = execute_func
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the command.
        
        Args:
            *args: Positional arguments for the command
            **kwargs: Keyword arguments for the command
            
        Returns:
            Result of command execution
        """
        return self.execute_func(*args, **kwargs)
    
    def can_execute(self) -> bool:
        """
        Simple commands can always execute.
        
        Returns:
            Always True
        """
        return True