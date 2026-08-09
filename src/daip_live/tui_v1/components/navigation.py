"""
Navigation Component

This module provides the NavigationComponent class as specified in the newP6
architecture requirements. The navigation component handles menu navigation,
keyboard shortcuts, and user interface navigation functionality.

Based on newP6 specification requirements for navigation management.
"""

from typing import Any, Callable, Optional

from textual import events
from textual.containers import Horizontal
from textual.widgets import Label

from .base import TUIComponent


class NavigationComponent(TUIComponent):
    """
    Navigation component for newP6 TUI architecture.

    This class provides navigation functionality and menu management as specified
    in the newP6 architecture requirements.

    Features:
    - Menu navigation and selection
    - Keyboard shortcut handling
    - Navigation state management
    - Focus management
    - Menu item hierarchy support
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        menu_items: Optional[list[dict[str, Any]]] = None,
        keyboard_shortcuts: Optional[dict[str, str]] = None,
        show_menu: bool = True,
    ):
        """
        Initialize the navigation component.

        Args:
            component_id: Optional unique identifier
            menu_items: List of menu items with 'label', 'action', and optional 'shortcut'
            keyboard_shortcuts: Dictionary of shortcut keys to actions
            show_menu: Whether to display the menu
        """  # noqa: E501
        super().__init__(component_id)

        # Default menu items if not provided
        default_menu_items = [
            {"label": "File", "action": "file_menu", "shortcut": "Alt+f"},
            {"label": "Edit", "action": "edit_menu", "shortcut": "Alt+e"},
            {"label": "View", "action": "view_menu", "shortcut": "Alt+v"},
            {"label": "Tools", "action": "tools_menu", "shortcut": "Alt+t"},
            {"label": "Help", "action": "help_menu", "shortcut": "Alt+h"},
        ]

        # Navigation configuration
        self.update_state(
            menu_items=menu_items or default_menu_items,
            keyboard_shortcuts=keyboard_shortcuts or {},
            show_menu=show_menu,
            current_selection=0,
            focused_item=None,
            navigation_history=[],
            breadcrumb_trail=[],
        )

        # Event handlers for menu actions
        self._action_handlers: dict[str, Callable] = {}

    def render(self):
        """
        Render the navigation component as a widget.

        Returns:
            Widget: The rendered navigation widget
        """
        # Create a simple container with basic styling
        container = Horizontal()
        container.styles.height = 3
        container.id = self.component_id

        # Add navigation content as a simple label for testing
        if self.state.get("show_menu", True):
            menu_items = self.state.get("menu_items", [])
            if menu_items:
                current_item = menu_items[self.state.get("current_selection", 0)]
                label = Label(f"Nav: {current_item.get('label', 'Menu')}")
                container._compose_children = lambda: [label]

        return container

    async def mount(self) -> None:
        """Mount the navigation component."""
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
        # Handle navigation-specific events
        if hasattr(event, "event_type"):
            if event.event_type.value == "navigate":
                self.navigate_to(event.data.get("target", ""))
            elif event.event_type.value == "menu_select":
                self.select_menu_item(event.data.get("index", 0))
            elif event.event_type.value == "focus_change":
                self.set_focused_item(event.data.get("item_id"))

        # Handle keyboard events
        if isinstance(event, events.Key):
            self._handle_keyboard_event(event)

    def _handle_keyboard_event(self, event: events.Key) -> None:
        """
        Handle keyboard events for navigation.

        Args:
            event: The keyboard event
        """
        key = event.key
        shortcuts = self.state.get("keyboard_shortcuts", {})

        # Check if key matches a shortcut
        if key in shortcuts:
            action = shortcuts[key]
            self._handle_menu_action(action)

        # Handle navigation keys
        elif key == "left":
            self.navigate_left()
        elif key == "right":
            self.navigate_right()
        elif key == "up":
            self.navigate_up()
        elif key == "down":
            self.navigate_down()
        elif key == "enter":
            self.activate_current_selection()

    def _handle_menu_action(self, action: str) -> None:
        """
        Handle a menu action.

        Args:
            action: The action to handle
        """
        # Add to navigation history
        history = self.state.get("navigation_history", [])
        history.append(action)
        self.update_state(navigation_history=history)

        # Call registered handler if exists
        if action in self._action_handlers:
            self._action_handlers[action]()

        # Emit navigation event
        self._emit_navigation_event(action)

    def register_action_handler(self, action: str, handler: Callable) -> None:
        """
        Register a handler for a menu action.

        Args:
            action: The action name
            handler: The handler function
        """
        self._action_handlers[action] = handler

    def navigate_to(self, target: str) -> None:
        """
        Navigate to a specific target.

        Args:
            target: The navigation target
        """
        # Add to breadcrumb trail
        breadcrumb = self.state.get("breadcrumb_trail", [])
        breadcrumb.append(target)

        self.update_state(
            breadcrumb_trail=breadcrumb,
            navigation_history=self.state.get("navigation_history", [])
            + [f"navigate_to:{target}"],
        )

        self._emit_navigation_event(f"navigate_to:{target}")

    def select_menu_item(self, index: int) -> None:
        """
        Select a menu item by index.

        Args:
            index: The index of the menu item to select
        """
        menu_items = self.state.get("menu_items", [])
        if 0 <= index < len(menu_items):
            self.update_state(current_selection=index)

            # Activate the selected item
            action = menu_items[index].get("action")
            if action:
                self._handle_menu_action(action)

    def navigate_left(self) -> None:
        """Navigate to the left in the menu."""
        current = self.state.get("current_selection", 0)
        menu_items = self.state.get("menu_items", [])

        if menu_items:
            new_selection = (current - 1) % len(menu_items)
            self.update_state(current_selection=new_selection)

    def navigate_right(self) -> None:
        """Navigate to the right in the menu."""
        current = self.state.get("current_selection", 0)
        menu_items = self.state.get("menu_items", [])

        if menu_items:
            new_selection = (current + 1) % len(menu_items)
            self.update_state(current_selection=new_selection)

    def navigate_up(self) -> None:
        """Navigate up in sub-menus or contexts."""
        # This would handle navigation in hierarchical menus
        breadcrumb = self.state.get("breadcrumb_trail", [])
        if len(breadcrumb) > 1:
            breadcrumb.pop()
            self.update_state(breadcrumb_trail=breadcrumb)

    def navigate_down(self) -> None:
        """Navigate down in sub-menus or contexts."""
        # This would handle navigation into sub-menus
        pass

    def activate_current_selection(self) -> None:
        """Activate the currently selected menu item."""
        current = self.state.get("current_selection", 0)
        self.select_menu_item(current)

    def set_focused_item(self, item_id: Optional[str]) -> None:
        """
        Set the focused navigation item.

        Args:
            item_id: The ID of the item to focus, or None to clear focus
        """
        self.update_state(focused_item=item_id)

    def get_current_selection(self) -> int:
        """
        Get the current menu selection index.

        Returns:
            int: Current selection index
        """
        return self.state.get("current_selection", 0)

    def get_menu_items(self) -> list[dict[str, Any]]:
        """
        Get the current menu items.

        Returns:
            List[Dict[str, Any]]: Menu items
        """
        return self.state.get("menu_items", [])

    def get_breadcrumb_trail(self) -> list[str]:
        """
        Get the current breadcrumb trail.

        Returns:
            List[str]: Breadcrumb trail
        """
        return self.state.get("breadcrumb_trail", [])

    def get_navigation_history(self) -> list[str]:
        """
        Get the navigation history.

        Returns:
            List[str]: Navigation history
        """
        return self.state.get("navigation_history", [])

    def add_menu_item(self, item: dict[str, Any]) -> None:
        """
        Add a new menu item.

        Args:
            item: Menu item dictionary with 'label', 'action', and optional 'shortcut'
        """
        menu_items = self.state.get("menu_items", [])
        menu_items.append(item)
        self.update_state(menu_items=menu_items)

    def remove_menu_item(self, index: int) -> None:
        """
        Remove a menu item by index.

        Args:
            index: Index of the menu item to remove
        """
        menu_items = self.state.get("menu_items", [])
        if 0 <= index < len(menu_items):
            menu_items.pop(index)
            self.update_state(menu_items=menu_items)

    def set_keyboard_shortcut(self, key: str, action: str) -> None:
        """
        Set a keyboard shortcut.

        Args:
            key: The key combination
            action: The action to perform
        """
        shortcuts = self.state.get("keyboard_shortcuts", {})
        shortcuts[key] = action
        self.update_state(keyboard_shortcuts=shortcuts)

    def _emit_navigation_event(self, action: str) -> None:
        """
        Emit a navigation event.

        Args:
            action: The navigation action
        """
        # This would integrate with the event system
        # For now, we'll just pass the event to children
        for child in self.get_children():
            child.handle_event(
                {
                    "event_type": "navigation",
                    "action": action,
                    "source": "navigation_component",
                }
            )

    def show_menu(self, show: bool) -> None:
        """
        Show or hide the menu.

        Args:
            show: Whether to show the menu
        """
        self.update_state(show_menu=show)
