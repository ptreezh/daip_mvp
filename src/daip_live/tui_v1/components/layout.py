"""
Layout Component

This module provides the LayoutComponent class as specified in the newP6
architecture requirements. The layout component provides responsive layout management
and container functionality for other components.

Based on newP6 specification requirements for layout management.
"""

from typing import Any, Dict, Optional, List
from textual.widgets import Static
from textual.containers import Vertical, Horizontal, Container

from .base import TUIComponent


class LayoutComponent(TUIComponent):
    """
    Layout component for newP6 TUI architecture.

    This class provides responsive layout management and container functionality
    as specified in the newP6 architecture requirements.

    Features:
    - Responsive layout adaptation
    - Child component management
    - Flexible layout configuration
    - Size constraints management
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        layout_type: str = "vertical",
        responsive: bool = True,
        padding: int = 0,
        margins: int = 0
    ):
        """
        Initialize the layout component.

        Args:
            component_id: Optional unique identifier
            layout_type: Type of layout ("vertical", "horizontal", "grid")
            responsive: Whether to enable responsive behavior
            padding: Padding around the layout
            margins: Margins around the layout
        """
        super().__init__(component_id)

        # Layout configuration
        self.update_state(
            layout_type=layout_type,
            responsive=responsive,
            padding=padding,
            margins=margins,
            width=100,
            height=100,
            children_count=0
        )

    def render(self):
        """
        Render the layout component as a widget.

        Returns:
            Widget: The rendered layout widget
        """
        layout_type = self.state.get('layout_type', 'vertical')
        padding = self.state.get('padding', 0)

        if layout_type == 'vertical':
            container = Vertical()
        elif layout_type == 'horizontal':
            container = Horizontal()
        else:
            container = Container()

        # Apply styling
        if padding > 0:
            container.styles.margin = padding

        container.id = self.component_id
        return container

    async def mount(self) -> None:
        """Mount the layout component."""
        self._set_mounted(True)

    def update_state(self, **kwargs) -> None:
        """
        Update the component's internal state.

        Args:
            **kwargs: Key-value pairs of state updates
        """
        super().update_state(**kwargs)

    def handle_event(self, event: Any) -> None:
        """
        Handle an event passed to this component.

        Args:
            event: The event to handle
        """
        # Update layout-specific state based on events
        if hasattr(event, 'event_type'):
            if event.event_type.value == 'resize':
                self.update_state(
                    width=event.data.get('width', self.state.get('width')),
                    height=event.data.get('height', self.state.get('height'))
                )
            elif event.event_type.value == 'layout_change':
                self.update_state(
                    layout_type=event.data.get('layout_type', self.state.get('layout_type'))
                )

    def add_child_component(self, child_component: TUIComponent) -> None:
        """
        Add a child component to the layout.

        Args:
            child_component: The child component to add
        """
        self.add_child(child_component)
        self.update_state(children_count=len(self.get_children()))

    def remove_child_component(self, child_component: TUIComponent) -> None:
        """
        Remove a child component from the layout.

        Args:
            child_component: The child component to remove
        """
        self.remove_child(child_component)
        self.update_state(children_count=len(self.get_children()))

    def set_responsive(self, responsive: bool) -> None:
        """
        Set responsive behavior for the layout.

        Args:
            responsive: Whether to enable responsive behavior
        """
        self.update_state(responsive=responsive)

    def set_padding(self, padding: int) -> None:
        """
        Set padding for the layout.

        Args:
            padding: Padding value
        """
        self.update_state(padding=padding)

    def set_margins(self, margins: int) -> None:
        """
        Set margins for the layout.

        Args:
            margins: Margins value
        """
        self.update_state(margins=margins)

    def set_layout_type(self, layout_type: str) -> None:
        """
        Set the layout type.

        Args:
            layout_type: Type of layout ("vertical", "horizontal", "grid")
        """
        self.update_state(layout_type=layout_type)