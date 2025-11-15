"""
ViewModel Base Class

This module provides the base ViewModel class following the MVVM pattern.
It handles property management, command registration, and change notifications.
"""

from typing import Any, Dict, Callable, List, Optional
from abc import ABC


class ViewModel(ABC):
    """
    Base ViewModel class implementing the MVVM pattern.
    
    This class provides:
    - Property management with change notifications
    - Command registration and execution
    - State management for GUI components
    """
    
    def __init__(self):
        """Initialize the ViewModel with empty property and command stores."""
        # Dictionary to store properties
        self._properties: Dict[str, Any] = {}
        
        # Dictionary to store registered commands
        self._commands: Dict[str, Callable] = {}
        
        # Dictionary to store property change listeners
        self._property_listeners: Dict[str, List[Callable]] = {}
        
        # List of property change subscriptions
        self._property_subscriptions: List[tuple] = []
        
        # Initialize with default attributes
        self._is_initialized = True
    
    def set_property(self, name: str, value: Any) -> None:
        """
        Set a property value and notify listeners of the change.
        
        Args:
            name: Property name
            value: Property value to set
        """
        old_value = self._properties.get(name)
        self._properties[name] = value
        
        # Notify listeners of the property change
        if name in self._property_listeners:
            for listener in self._property_listeners[name]:
                listener(name, value, old_value)
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """
        Get a property value.
        
        Args:
            name: Property name to retrieve
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default
        """
        return self._properties.get(name, default)
    
    def register_command(self, name: str, command: Callable) -> None:
        """
        Register a command that can be executed by name.
        
        Args:
            name: Command name
            command: Callable command function
        """
        self._commands[name] = command
    
    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """
        Execute a registered command by name.
        
        Args:
            name: Command name to execute
            *args: Arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command
            
        Returns:
            Command execution result
        """
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not registered")
        
        command = self._commands[name]
        return command(*args, **kwargs)
    
    def subscribe_to_property_change(
        self, 
        property_name: str, 
        listener: Callable[[str, Any, Any], None]
    ) -> None:
        """
        Subscribe to property change notifications.
        
        Args:
            property_name: Name of property to listen for
            listener: Callback function to call on property change
                    Signature: listener(property_name, new_value, old_value)
        """
        if property_name not in self._property_listeners:
            self._property_listeners[property_name] = []
        
        self._property_listeners[property_name].append(listener)
    
    def get_all_properties(self) -> Dict[str, Any]:
        """
        Get a copy of all properties.
        
        Returns:
            Copy of properties dictionary
        """
        return self._properties.copy()
    
    def has_property(self, name: str) -> bool:
        """
        Check if a property exists.
        
        Args:
            name: Property name to check
            
        Returns:
            True if property exists, False otherwise
        """
        return name in self._properties
    
    def remove_property(self, name: str) -> bool:
        """
        Remove a property.
        
        Args:
            name: Property name to remove
            
        Returns:
            True if property was removed, False if it didn't exist
        """
        if name in self._properties:
            # Notify listeners with None as new value
            old_value = self._properties[name]
            if name in self._property_listeners:
                for listener in self._property_listeners[name]:
                    listener(name, None, old_value)
            
            del self._properties[name]
            return True
        return False
    
    def clear_all_properties(self) -> None:
        """Clear all properties."""
        for name in list(self._properties.keys()):
            self.remove_property(name)