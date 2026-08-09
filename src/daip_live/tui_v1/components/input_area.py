"""
Input Area Component

This module provides the InputAreaComponent class as specified in the newP6
architecture requirements. The input area component handles user input and provides
command input functionality with auto-completion support.

Based on newP6 specification requirements for input management.
"""

from typing import Any, Callable, Optional

from textual.containers import Vertical
from textual.widgets import Input

from .base import TUIComponent


class InputAreaComponent(TUIComponent):
    """
    Input area component for newP6 TUI architecture.

    This class provides user input functionality with auto-completion and command
    processing as specified in the newP6 architecture requirements.

    Features:
    - User input handling
    - Auto-completion support
    - Command history
    - Input validation
    - Multi-line input support
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        placeholder: str = "Enter command...",
        multiline: bool = False,
        max_length: Optional[int] = None,
        auto_complete: bool = True,
    ):
        """
        Initialize the input area component.

        Args:
            component_id: Optional unique identifier (should be "user_input" for compatibility)
            placeholder: Placeholder text for the input
            multiline: Whether to support multi-line input
            max_length: Maximum input length
            auto_complete: Whether to enable auto-completion
        """  # noqa: E501
        super().__init__(component_id)

        # Input configuration
        self.update_state(
            placeholder=placeholder,
            multiline=multiline,
            max_length=max_length,
            auto_complete=auto_complete,
            input_text="",
            suggestions=[],
            history=[],
            history_index=-1,
            is_focused=False,
        )

        # Auto-completion suggestions (can be populated dynamically)
        self._suggestions_callback: Optional[Callable] = None

    def render(self):
        """
        Render the input area component as a widget.

        Returns:
            Widget: The rendered input area widget
        """
        # Create input widget
        input_widget = Input(
            placeholder=self.state.get("placeholder", "Enter command..."),
            password=False,
            max_length=self.state.get("max_length"),
        )

        # For multi-line support, create a container
        if self.state.get("multiline", False):
            container = Vertical()
            container.add(input_widget)
            container.id = self.component_id
            return container
        else:
            input_widget.id = self.component_id
            return input_widget

    async def mount(self) -> None:
        """Mount the input area component."""
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
        # Handle input-specific events
        if hasattr(event, "event_type"):
            if event.event_type.value == "input_focus":
                self.update_state(is_focused=True)
            elif event.event_type.value == "input_blur":
                self.update_state(is_focused=False)
            elif event.event_type.value == "input_change":
                self.update_state(input_text=event.data.get("text", ""))
                # Trigger auto-completion if enabled
                if self.state.get("auto_complete"):
                    self._update_suggestions(event.data.get("text", ""))

    def set_suggestions_callback(self, callback: Callable[[str], list[str]]) -> None:
        """
        Set the callback function for generating auto-completion suggestions.

        Args:
            callback: Function that takes input text and returns suggestions
        """
        self._suggestions_callback = callback

    def _update_suggestions(self, input_text: str) -> None:
        """
        Update auto-completion suggestions based on input text.

        Args:
            input_text: Current input text
        """
        suggestions = []

        if self._suggestions_callback:
            suggestions = self._suggestions_callback(input_text)
        else:
            # Default basic suggestions
            basic_commands = ["help", "quit", "clear", "status"]
            suggestions = [
                cmd for cmd in basic_commands if cmd.startswith(input_text.lower())
            ]

        self.update_state(suggestions=suggestions)

    def get_input_text(self) -> str:
        """
        Get the current input text.

        Returns:
            str: Current input text
        """
        return self.state.get("input_text", "")

    def set_input_text(self, text: str) -> None:
        """
        Set the input text.

        Args:
            text: The input text to set
        """
        self.update_state(input_text=text)

    def clear_input(self) -> None:
        """Clear the input text."""
        self.update_state(input_text="", suggestions=[])

    def get_suggestions(self) -> list[str]:
        """
        Get current auto-completion suggestions.

        Returns:
            List[str]: Current suggestions
        """
        return self.state.get("suggestions", [])

    def add_to_history(self, command: str) -> None:
        """
        Add a command to the input history.

        Args:
            command: The command to add
        """
        history = self.state.get("history", [])
        if command and command not in history:
            history.append(command)
            # Keep history size manageable
            if len(history) > 1000:
                history.pop(0)
            self.update_state(history=history, history_index=-1)

    def navigate_history(self, direction: str) -> Optional[str]:
        """
        Navigate through command history.

        Args:
            direction: "up" or "down"

        Returns:
            Optional[str]: The selected command, or None if no history
        """
        history = self.state.get("history", [])
        if not history:
            return None

        current_index = self.state.get("history_index", -1)

        if direction == "up" and current_index > 0:
            current_index -= 1
        elif direction == "down" and current_index < len(history) - 1:
            current_index += 1

        if current_index >= 0 and current_index < len(history):
            selected_command = history[current_index]
            self.update_state(history_index=current_index, input_text=selected_command)
            return selected_command

        return None

    def is_focused(self) -> bool:
        """
        Check if the input area is currently focused.

        Returns:
            bool: True if focused, False otherwise
        """
        return self.state.get("is_focused", False)

    def set_placeholder(self, placeholder: str) -> None:
        """
        Set the placeholder text.

        Args:
            placeholder: The placeholder text
        """
        self.update_state(placeholder=placeholder)

    def set_multiline(self, multiline: bool) -> None:
        """
        Set whether multi-line input is enabled.

        Args:
            multiline: Whether to enable multi-line input
        """
        self.update_state(multiline=multiline)
