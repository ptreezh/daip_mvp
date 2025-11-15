"""
ViewModel Base Implementation with All Required Methods

This module provides the complete ViewModel base class that includes all methods needed for
proper MVVM architecture integration with views.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional, Union
from dataclasses import dataclass, field


@dataclass
class PropertyChangedEventArgs:
    """Event args for property change notifications."""
    property_name: str
    old_value: Any
    new_value: Any
    viewmodel: 'ViewModel'


class ViewModel(ABC):
    """
    Base ViewModel class implementing the MVVM pattern.
    
    This class provides:
    - Property management with change notifications
    - Command registration and execution
    - State management for GUI components
    - Event handling and subscriptions
    """
    
    def __init__(self):
        """Initialize the ViewModel with empty property and command stores."""
        # Dictionary to store properties
        self._properties: Dict[str, Any] = {}
        
        # Dictionary to store registered commands
        self._commands: Dict[str, Dict[str, Callable]] = {}
        
        # Dictionary to store property change listeners
        self._property_listeners: Dict[str, List[Callable[[PropertyChangedEventArgs], None]]] = {}
        
        # List of property change subscriptions - tuple of (property_name, callback_function)
        self._property_subscriptions: List[tuple] = []
        
        # List of command subscriptions - tuple of (command_name, callback_function)
        self._command_subscriptions: List[tuple] = []
        
        # Initialize with default attributes
        self._is_initialized = True
        
        # Add default properties that are commonly used
        self.set_property('current_view', 'chat')
        self.set_property('is_loading', False)
        self.set_property('error_message', None)
        self.set_property('notification', None)
        
        # Define type hints for attributes that will be used elsewhere
        self._property_subscriptions: List[tuple] = []
        self._property_listeners: Dict[str, List] = {}
        
    def set_property(self, name: str, value: Any) -> bool:
        """
        Set a property value and notify listeners of changes.
        
        Args:
            name: Property name to set
            value: New value for the property
            
        Returns:
            True if property was changed, False if unchanged
        """
        old_value = self._properties.get(name)
        
        # Only notify if value actually changed
        if old_value != value or name not in self._properties:
            self._properties[name] = value
            
            # Notify property change listeners
            if name in self._property_listeners:
                event_args = PropertyChangedEventArgs(
                    property_name=name,
                    old_value=old_value,
                    new_value=value,
                    viewmodel=self
                )
                
                for listener in self._property_listeners[name][:]:  # Use slice to prevent mutation during iteration
                    try:
                        listener(event_args)
                    except Exception as e:
                        # In production, you might log this
                        pass
            
            # Notify general property change subscriptions
            for sub_property, callback in self._property_subscriptions:
                if sub_property is None or sub_property == name:  # None means all properties
                    try:
                        callback(name, value, old_value)
                    except Exception as e:
                        # In production, you might log this
                        pass
            
            return True
        
        return False
    
    def get_property(self, name: str, default: Any = None) -> Any:
        """
        Get a property value.
        
        Args:
            name: Property name to get
            default: Default value if property doesn't exist
            
        Returns:
            Property value or default if not found
        """
        return self._properties.get(name, default)
    
    def has_property(self, name: str) -> bool:
        """
        Check if a property exists.
        
        Args:
            name: Property name to check
            
        Returns:
            True if property exists, False otherwise
        """
        return name in self._properties
    
    def register_command(self, name: str, execute_func: Callable, can_execute_func: Optional[Callable[[], bool]] = None) -> None:
        """
        Register a command with the ViewModel.
        
        Args:
            name: Command name
            execute_func: Function to execute when command is called
            can_execute_func: Optional function to determine if command can execute
        """
        self._commands[name] = {
            'execute': execute_func,
            'can_execute': can_execute_func or (lambda: True)
        }
    
    def execute_command(self, name: str, *args, **kwargs) -> Any:
        """
        Execute a registered command.
        
        Args:
            name: Command name to execute
            *args: Arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command
            
        Returns:
            Result of command execution
        """
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not registered")
        
        command_info = self._commands[name]
        
        if not command_info['can_execute']():
            raise RuntimeError(f"Command '{name}' cannot be executed")
        
        return command_info['execute'](*args, **kwargs)
    
    def can_execute_command(self, name: str) -> bool:
        """
        Check if a command can be executed.
        
        Args:
            name: Command name to check
            
        Returns:
            True if command can be executed, False otherwise
        """
        if name not in self._commands:
            return False
        
        command_info = self._commands[name]
        return command_info['can_execute']()
    
    def subscribe_property_change(self, property_name: str, callback: Callable[[str, Any, Any], None]) -> str:
        """
        Subscribe to property change notifications.
        
        Args:
            property_name: Name of property to subscribe to (use None for all properties)
            callback: Function to call when property changes
                    Signature: callback(property_name: str, new_value: Any, old_value: Any)
                    
        Returns:
            Subscription ID for unsubscribing later
        """
        subscription_id = f"sub_{len(self._property_subscriptions)}_{property_name}"
        self._property_subscriptions.append((property_name, callback))
        return subscription_id
    
    def unsubscribe_property_change(self, subscription_id: str) -> bool:
        """
        Unsubscribe from property change notifications.
        
        Args:
            subscription_id: ID returned by subscribe_property_change
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        original_length = len(self._property_subscriptions)
        self._property_subscriptions = [
            sub for sub in self._property_subscriptions 
            if not sub[1].__str__().startswith(subscription_id.split('_')[1])
        ]
        return len(self._property_subscriptions) < original_length
    
    def add_property_listener(self, property_name: str, listener: Callable[[PropertyChangedEventArgs], None]) -> None:
        """
        Add a property change listener for specific property.
        
        Args:
            property_name: Property name to listen for
            listener: Function to call when property changes
        """
        if property_name not in self._property_listeners:
            self._property_listeners[property_name] = []
        
        self._property_listeners[property_name].append(listener)
    
    def remove_property_listener(self, property_name: str, listener: Callable[[PropertyChangedEventArgs], None]) -> bool:
        """
        Remove a property change listener.
        
        Args:
            property_name: Property name that was listened to
            listener: Listener function to remove
            
        Returns:
            True if removal was successful, False if listener not found
        """
        if property_name in self._property_listeners:
            if listener in self._property_listeners[property_name]:
                self._property_listeners[property_name].remove(listener)
                return True
        return False
    
    def get_all_properties(self) -> Dict[str, Any]:
        """
        Get a copy of all properties.
        
        Returns:
            Dictionary copy of all properties
        """
        return self._properties.copy()
    
    def set_multiple_properties(self, updates: Dict[str, Any]) -> List[str]:
        """
        Set multiple properties at once.
        
        Args:
            updates: Dictionary of property names to values
            
        Returns:
            List of property names that changed
        """
        changed_properties = []
        for name, value in updates.items():
            if self.set_property(name, value):
                changed_properties.append(name)
        return changed_properties
    
    def clear_property(self, name: str) -> bool:
        """
        Remove a property from the ViewModel.
        
        Args:
            name: Property name to remove
            
        Returns:
            True if property was removed, False if it didn't exist
        """
        if name in self._properties:
            old_value = self._properties.pop(name)
            
            # Notify listeners that property was removed
            if name in self._property_listeners:
                event_args = PropertyChangedEventArgs(
                    property_name=name,
                    old_value=old_value,
                    new_value=None,
                    viewmodel=self
                )
                
                for listener in self._property_listeners[name][:]:
                    try:
                        listener(event_args)
                    except Exception as e:
                        pass
            
            # Notify general subscriptions
            for sub_property, callback in self._property_subscriptions:
                if sub_property is None or sub_property == name:
                    try:
                        callback(name, None, old_value)
                    except Exception as e:
                        pass
            
            return True
        return False
    
    def clear_all_properties(self) -> None:
        """Clear all properties from the ViewModel."""
        for name in list(self._properties.keys()):
            self.clear_property(name)
    
    def get_command_names(self) -> List[str]:
        """
        Get list of registered command names.
        
        Returns:
            List of command names
        """
        return list(self._commands.keys())
    
    def register_property_binding(self, source_property: str, target_callback: Callable[[Any], None]) -> str:
        """
        Register a property binding callback.
        
        Args:
            source_property: Property name to bind to
            target_callback: Callback to trigger when property changes
            
        Returns:
            Binding ID for removing the binding later
        """
        def binding_callback(name, new_val, old_val):
            if name == source_property:
                target_callback(new_val)
        
        binding_id = f"bind_{len(self._property_subscriptions)}"
        self._property_subscriptions.append((source_property, binding_callback))
        return binding_id
    
    def remove_property_binding(self, binding_id: str) -> bool:
        """
        Remove a property binding.
        
        Args:
            binding_id: ID returned by register_property_binding
            
        Returns:
            True if removal was successful, False otherwise
        """
        return self.unsubscribe_property_change(binding_id)
    
    def execute_async_command(self, name: str, *args, **kwargs) -> asyncio.Future:
        """
        Execute an async command and return a Future.
        
        Args:
            name: Command name to execute
            *args: Arguments to pass to the command
            **kwargs: Keyword arguments to pass to the command
            
        Returns:
            Future for async command result
        """
        if name not in self._commands:
            raise ValueError(f"Command '{name}' not registered")
        
        command_info = self._commands[name]
        
        if not command_info['can_execute']():
            raise RuntimeError(f"Command '{name}' cannot be executed")
        
        # Check if the execute function is async
        import inspect
        if inspect.iscoroutinefunction(command_info['execute']):
            return asyncio.create_task(command_info['execute'](*args, **kwargs))
        else:
            # For sync functions, wrap in async
            loop = asyncio.get_event_loop()
            return loop.run_in_executor(None, command_info['execute'], *args)
    
    def update_property_with_transform(self, name: str, transform_func: Callable[[Any], Any]) -> bool:
        """
        Update a property by applying a transformation function to its current value.
        
        Args:
            name: Property name to update
            transform_func: Function to transform the current value
            
        Returns:
            True if property was changed, False if unchanged
        """
        current_value = self.get_property(name)
        new_value = transform_func(current_value)
        return self.set_property(name, new_value)
    
    def conditional_set_property(self, name: str, value: Any, condition: Callable[[Any], bool]) -> bool:
        """
        Conditionally set a property based on a condition function.
        
        Args:
            name: Property name to set
            value: Value to set
            condition: Function that takes current value and returns True if property should be set
            
        Returns:
            True if property was set, False if condition was not met
        """
        current_value = self.get_property(name)
        if condition(current_value):
            return self.set_property(name, value)
        return False
    
    def increment_property(self, name: str, amount: Union[int, float] = 1) -> bool:
        """
        Increment a numeric property by a specified amount.
        
        Args:
            name: Property name to increment
            amount: Amount to increment by (default 1)
            
        Returns:
            True if property was incremented, False if not numeric or property doesn't exist
        """
        current_value = self.get_property(name, 0)
        if isinstance(current_value, (int, float)) and isinstance(amount, (int, float)):
            return self.set_property(name, current_value + amount)
        return False
    
    def get_dirty_properties(self, original_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get properties that differ from original values.
        
        Args:
            original_values: Dictionary of original property values
            
        Returns:
            Dictionary of dirty properties with their current values
        """
        dirty = {}
        for name, current_value in self.get_all_properties().items():
            if name not in original_values or original_values[name] != current_value:
                dirty[name] = current_value
        return dirty
    
    def save_state(self) -> Dict[str, Any]:
        """
        Save the current state of the ViewModel.
        
        Returns:
            Dictionary representing the current state
        """
        return {
            'properties': self.get_all_properties(),
            'property_listeners': {k: len(v) for k, v in self._property_listeners.items()},  # Just count for serialization
            'commands': list(self._commands.keys()),  # Just names for serialization
            'subscriptions': len(self._property_subscriptions)
        }
    
    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Load state into the ViewModel.
        
        Args:
            state: State dictionary to load
        """
        if 'properties' in state:
            for name, value in state['properties'].items():
                self.set_property(name, value)
    
    def is_property_dirty(self, name: str, original_value: Any) -> bool:
        """
        Check if a specific property is dirty (different from original value).
        
        Args:
            name: Property name to check
            original_value: Original value for comparison
            
        Returns:
            True if property is dirty, False otherwise
        """
        current_value = self.get_property(name)
        return current_value != original_value


# Convenience function for creating ViewModels
def create_viewmodel(cls, *args, **kwargs) -> ViewModel:
    """
    Create a ViewModel instance with proper initialization.
    
    Args:
        cls: ViewModel class to instantiate
        *args: Arguments to pass to constructor
        **kwargs: Keyword arguments to pass to constructor
        
    Returns:
        Initialized ViewModel instance
    """
    instance = cls(*args, **kwargs)
    return instance