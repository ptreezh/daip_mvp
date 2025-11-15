"""
Data Binding System

This module provides data binding capabilities for the MVVM architecture.
It supports one-way and two-way bindings between observable properties.
"""

from typing import Any, Callable, List, Optional, Union
from abc import ABC, abstractmethod


class IObservable(ABC):
    """
    Interface for observable objects that can notify listeners of changes.
    """
    
    @abstractmethod
    def add_listener(self, listener: Callable) -> None:
        """
        Add a listener that will be called when the observable changes.
        
        Args:
            listener: Callable that receives (old_value, new_value) parameters
        """
        pass
    
    @abstractmethod
    def remove_listener(self, listener: Callable) -> None:
        """
        Remove a listener.
        
        Args:
            listener: The listener to remove
        """
        pass


class ObservableProperty(IObservable):
    """
    An observable property that can notify listeners when its value changes.
    """
    
    def __init__(self, initial_value: Any = None):
        """
        Initialize the observable property.
        
        Args:
            initial_value: Initial value for the property
        """
        self._value = initial_value
        self._listeners: List[Callable] = []
    
    def get(self) -> Any:
        """
        Get the current value of the property.
        
        Returns:
            Current value
        """
        return self._value
    
    def set(self, value: Any) -> None:
        """
        Set a new value and notify listeners.
        
        Args:
            value: New value to set
        """
        old_value = self._value
        self._value = value
        self._notify_listeners(old_value, value)
    
    def add_listener(self, listener: Callable[[Any, Any], None]) -> None:
        """
        Add a listener that will be called when the value changes.
        
        Args:
            listener: Callable that receives (old_value, new_value) parameters
        """
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[Any, Any], None]) -> None:
        """
        Remove a listener.
        
        Args:
            listener: The listener to remove
        """
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self, old_value: Any, new_value: Any) -> None:
        """
        Notify all registered listeners of a value change.
        
        Args:
            old_value: Previous value
            new_value: New value
        """
        for listener in self._listeners[:]:  # Use slice to avoid issues during notification
            try:
                listener(old_value, new_value)
            except Exception:
                # Log the exception or handle it as appropriate for your system
                pass


class IBinding(ABC):
    """
    Interface for data bindings.
    """
    
    @abstractmethod
    def update_source(self, value: Any) -> None:
        """
        Update the source with a new value.
        
        Args:
            value: New value to set in source
        """
        pass
    
    @abstractmethod
    def update_target(self, value: Any) -> None:
        """
        Update the target with a new value.
        
        Args:
            value: New value to set in target
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """
        Check if the binding is currently active.
        
        Returns:
            True if active, False otherwise
        """
        pass
    
    @abstractmethod
    def destroy(self) -> None:
        """
        Destroy the binding and clean up resources.
        """
        pass


class Binding(IBinding):
    """
    Base class for data bindings between source and target properties.
    """
    
    def __init__(
        self,
        source: ObservableProperty,
        target: ObservableProperty,
        to_target_converter: Optional[Callable[[Any], Any]] = None,
        to_source_converter: Optional[Callable[[Any], Any]] = None,
        mode: str = "two_way"
    ):
        """
        Initialize the binding.
        
        Args:
            source: Source observable property
            target: Target observable property
            to_target_converter: Function to convert source value for target
            to_source_converter: Function to convert target value for source
            mode: Binding mode - "one_way" or "two_way"
        """
        self._source = source
        self._target = target
        self._to_target_converter = to_target_converter or (lambda x: x)
        self._to_source_converter = to_source_converter or (lambda x: x)
        self._mode = mode
        self._active = True
        
        # Bind change listeners
        self._source.add_listener(self._on_source_changed)
        self._target.add_listener(self._on_target_changed)
    
    def _on_source_changed(self, old_value: Any, new_value: Any) -> None:
        """
        Handle source property change.
        
        Args:
            old_value: Previous value
            new_value: New value
        """
        if not self._active:
            return
        
        converted_value = self._to_target_converter(new_value)
        self._target.set(converted_value)
    
    def _on_target_changed(self, old_value: Any, new_value: Any) -> None:
        """
        Handle target property change.
        
        Args:
            old_value: Previous value
            new_value: New value
        """
        if not self._active or self._mode != "two_way":
            return
        
        converted_value = self._to_source_converter(new_value)
        self._source.set(converted_value)
    
    def update_source(self, value: Any) -> None:
        """
        Update the source property.
        
        Args:
            value: New value for source
        """
        if self._active:
            self._source.set(value)
    
    def update_target(self, value: Any) -> None:
        """
        Update the target property.
        
        Args:
            value: New value for target
        """
        if self._active:
            self._target.set(value)
    
    def is_active(self) -> bool:
        """
        Check if the binding is active.
        
        Returns:
            True if active, False otherwise
        """
        return self._active
    
    def destroy(self) -> None:
        """
        Destroy the binding and remove listeners.
        """
        if self._active:
            self._source.remove_listener(self._on_source_changed)
            self._target.remove_listener(self._on_target_changed)
            self._active = False


class DataBinder:
    """
    Main class for creating and managing data bindings.
    """
    
    def __init__(self):
        """Initialize the data binder."""
        self._bindings: List[Binding] = []
    
    def bind_one_way(
        self,
        source: ObservableProperty,
        target: ObservableProperty,
        converter: Optional[Callable[[Any], Any]] = None
    ) -> Binding:
        """
        Create a one-way binding from source to target.
        
        Args:
            source: Source observable property
            target: Target observable property
            converter: Optional converter function
            
        Returns:
            Created binding object
        """
        binding = Binding(
            source=source,
            target=target,
            to_target_converter=converter,
            mode="one_way"
        )
        self._bindings.append(binding)
        return binding
    
    def bind_two_way(
        self,
        source: ObservableProperty,
        target: ObservableProperty,
        to_target_converter: Optional[Callable[[Any], Any]] = None,
        to_source_converter: Optional[Callable[[Any], Any]] = None
    ) -> Binding:
        """
        Create a two-way binding between source and target.
        
        Args:
            source: Source observable property
            target: Target observable property
            to_target_converter: Converter from source to target
            to_source_converter: Converter from target to source
            
        Returns:
            Created binding object
        """
        binding = Binding(
            source=source,
            target=target,
            to_target_converter=to_target_converter,
            to_source_converter=to_source_converter,
            mode="two_way"
        )
        self._bindings.append(binding)
        return binding
    
    def unbind(self, binding: Binding) -> None:
        """
        Remove a binding.
        
        Args:
            binding: Binding to remove
        """
        if binding in self._bindings:
            binding.destroy()
            self._bindings.remove(binding)
    
    def unbind_all(self) -> None:
        """Remove all bindings."""
        for binding in self._bindings[:]:
            binding.destroy()
        self._bindings.clear()
    
    def get_binding_count(self) -> int:
        """
        Get the number of active bindings.
        
        Returns:
            Number of active bindings
        """
        return len(self._bindings)
    
    def get_active_bindings(self) -> List[Binding]:
        """
        Get all active bindings.
        
        Returns:
            List of active binding objects
        """
        return [binding for binding in self._bindings if binding.is_active()]


# Convenience functions for easy binding
def bind_one_way(
    source: ObservableProperty,
    target: ObservableProperty,
    converter: Optional[Callable[[Any], Any]] = None
) -> Binding:
    """
    Convenience function to create a one-way binding.
    
    Args:
        source: Source observable property
        target: Target observable property
        converter: Optional converter function
        
    Returns:
        Created binding object
    """
    binder = DataBinder()
    return binder.bind_one_way(source, target, converter)


def bind_two_way(
    source: ObservableProperty,
    target: ObservableProperty,
    to_target_converter: Optional[Callable[[Any], Any]] = None,
    to_source_converter: Optional[Callable[[Any], Any]] = None
) -> Binding:
    """
    Convenience function to create a two-way binding.
    
    Args:
        source: Source observable property
        target: Target observable property
        to_target_converter: Converter from source to target
        to_source_converter: Converter from target to source
        
    Returns:
        Created binding object
    """
    binder = DataBinder()
    return binder.bind_two_way(source, target, to_target_converter, to_source_converter)