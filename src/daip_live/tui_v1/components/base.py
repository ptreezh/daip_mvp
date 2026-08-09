"""
TUI Component Base Class

This module provides the TUIComponent abstract base class as specified in the newP6
architecture requirements. The component follows the abstract base class pattern
with required lifecycle methods.

Based on newP6 specification requirements for component architecture.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    pass


class TUIComponent(ABC):
    """
    Abstract base class for all TUI components in the newP6 architecture.

    This class defines the component interface and lifecycle management according
    to the newP6 specification requirements. All concrete components must inherit
    from this class and implement the required abstract methods.

    Required Methods:
    - render(): Returns the Widget representation of the component
    - mount(): Async method called when component is mounted
    - update_state(**kwargs): Updates component internal state
    - handle_event(event): Handles events passed to the component

    Design Principles:
    - Single Responsibility: Each component has a single, well-defined purpose
    - Open/Closed: Components are open for extension, closed for modification
    - Dependency Inversion: Components depend on abstractions, not concretions
    """

    def __init__(self, component_id: Optional[str] = None):
        """
        Initialize the component.

        Args:
            component_id: Optional unique identifier for this component
        """
        self._mounted = False
        self._state: dict[str, Any] = {}
        self._component_id = component_id or self.__class__.__name__
        self._parent: Optional[TUIComponent] = None
        self._children: list[TUIComponent] = []

    @abstractmethod
    def render(self):
        """
        Render the component as a Widget.

        Returns:
            Widget: The Textual widget representing this component
        """
        pass

    @abstractmethod
    async def mount(self) -> None:
        """
        Mount the component.

        This method is called when the component is added to the application.
        Components should perform any initialization that requires async context.
        """
        pass

    @abstractmethod
    def update_state(self, **kwargs) -> None:
        """
        Update the component's internal state.

        Args:
            **kwargs: Key-value pairs of state updates
        """
        self._state.update(kwargs)

    @abstractmethod
    def handle_event(self, event: Any) -> None:
        """
        Handle an event passed to this component.

        Args:
            event: The event to handle
        """
        pass

    # Component hierarchy and lifecycle methods
    def add_child(self, child: "TUIComponent") -> None:
        """
        Add a child component to this component.

        Args:
            child: The child component to add
        """
        if child not in self._children:
            child._parent = self
            self._children.append(child)

    def remove_child(self, child: "TUIComponent") -> None:
        """
        Remove a child component from this component.

        Args:
            child: The child component to remove
        """
        if child in self._children:
            child._parent = None
            self._children.remove(child)

    def get_children(self) -> list["TUIComponent"]:
        """Get a copy of the children list."""
        return self._children.copy()

    # Properties
    @property
    def is_mounted(self) -> bool:
        """Check if the component is mounted."""
        return self._mounted

    @property
    def component_id(self) -> str:
        """Get the component's unique identifier."""
        return self._component_id

    @property
    def parent(self) -> Optional["TUIComponent"]:
        """Get the parent component."""
        return self._parent

    @property
    def state(self) -> dict[str, Any]:
        """Get a copy of the component's internal state."""
        return self._state.copy()

    def _set_mounted(self, mounted: bool) -> None:
        """Internal method to set mounted status."""
        self._mounted = mounted

    # String representation for debugging
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id='{self._component_id}', mounted={self._mounted})>"  # noqa: E501
