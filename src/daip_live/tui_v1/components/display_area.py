"""
Display Area Component

This module provides the DisplayAreaComponent class as specified in the newP6
architecture requirements. The display area component provides content rendering
and display functionality with RichLog-like behavior.

Based on newP6 specification requirements for display management.
"""

from typing import Any, Optional

from textual.widgets import RichLog

from .base import TUIComponent


class DisplayAreaComponent(TUIComponent):
    """
    Display area component for newP6 TUI architecture.

    This class provides content display and rendering functionality as specified in the
    newP6 architecture requirements. It behaves similarly to RichLog for displaying
    formatted text and rich content.

    Features:
    - Rich text display with formatting support
    - Auto-scrolling and scroll management
    - Content history and buffer management
    - Search and filtering capabilities
    - Performance-optimized rendering
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        max_lines: int = 10000,
        auto_scroll: bool = True,
        wrap: bool = True,
        show_line_numbers: bool = False,
    ):
        """
        Initialize the display area component.

        Args:
            component_id: Optional unique identifier (should be "main_log" for compatibility)
            max_lines: Maximum number of lines to keep in buffer
            auto_scroll: Whether to auto-scroll to new content
            wrap: Whether to wrap long lines
            show_line_numbers: Whether to show line numbers
        """  # noqa: E501
        super().__init__(component_id)

        # Display configuration
        self.update_state(
            max_lines=max_lines,
            auto_scroll=auto_scroll,
            wrap=wrap,
            show_line_numbers=show_line_numbers,
            content_buffer=[],
            line_count=0,
            search_text="",
            search_results=[],
            current_search_index=0,
        )

        # RichLog widget for rendering
        self._rich_log: Optional[RichLog] = None

    def render(self):
        """
        Render the display area component as a widget.

        Returns:
            Widget: The rendered display area widget
        """
        # Create or get RichLog widget
        if self._rich_log is None:
            self._rich_log = RichLog(
                auto_scroll=self.state.get("auto_scroll", True),
                max_lines=self.state.get("max_lines", 10000),
                wrap=self.state.get("wrap", True),
            )

        # Configure based on state
        if self.state.get("show_line_numbers"):
            # Configure line numbers (RichLog supports this via styles)
            pass

        self._rich_log.id = self.component_id
        return self._rich_log

    async def mount(self) -> None:
        """Mount the display area component."""
        self._set_mounted(True)
        # Restore any buffered content
        self._restore_buffered_content()

    def update_state(self, **kwargs) -> None:
        """
        Update the component's internal state.

        Args:
            **kwargs: Key-value pairs of state updates
        """
        super().update_state(**kwargs)

        # Update RichLog widget if it exists
        if hasattr(self, "_rich_log") and self._rich_log:
            if "auto_scroll" in kwargs:
                self._rich_log.auto_scroll = kwargs["auto_scroll"]
            if "max_lines" in kwargs:
                self._rich_log.max_lines = kwargs["max_lines"]
            if "wrap" in kwargs:
                self._rich_log.wrap = kwargs["wrap"]

    def handle_event(self, event: Any) -> None:
        """
        Handle an event passed to this component.

        Args:
            event: The event to handle
        """
        # Handle display-specific events with robust error handling
        try:
            if event is None:
                return

            if hasattr(event, "event_type") and event.event_type is not None:
                if hasattr(event.event_type, "value"):
                    event_type_value = event.event_type.value
                else:
                    return

                if event_type_value == "content_update":
                    content = ""
                    if hasattr(event, "data") and event.data is not None:
                        content = event.data.get("content", "")
                    self.write(content)
                elif event_type_value == "clear_display":
                    self.clear()
                elif event_type_value == "search":
                    search_text = ""
                    if hasattr(event, "data") and event.data is not None:
                        search_text = event.data.get("text", "")
                    self.search(search_text)
                elif event_type_value == "scroll_to_bottom":
                    self.scroll_to_bottom()
        except Exception:
            # Silently handle errors to maintain system stability
            pass

    def write(self, content: str) -> None:
        """
        Write content to the display area.

        Args:
            content: The content to write
        """
        if not content:
            return

        # Add to buffer
        buffer = self.state.get("content_buffer", [])
        buffer.append(content)

        # Maintain max lines limit
        max_lines = self.state.get("max_lines", 10000)
        while len(buffer) > max_lines:
            buffer.pop(0)

        # Update line count
        line_count = sum(content.count("\n") + 1 for content in buffer)
        self.update_state(content_buffer=buffer, line_count=line_count)

        # Write to RichLog if available
        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.write(content)

    def write_line(self, line: str) -> None:
        """
        Write a single line to the display area.

        Args:
            line: The line to write
        """
        self.write(line + "\n")

    def clear(self) -> None:
        """Clear the display area."""
        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.clear()

        self.update_state(
            content_buffer=[],
            line_count=0,
            search_text="",
            search_results=[],
            current_search_index=0,
        )

    def scroll_to_bottom(self) -> None:
        """Scroll the display area to the bottom."""
        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.scroll_end(animate=False)

    def scroll_to_top(self) -> None:
        """Scroll the display area to the top."""
        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.scroll_home(animate=False)

    def search(self, text: str) -> list[int]:
        """
        Search for text in the display area.

        Args:
            text: Text to search for

        Returns:
            List[int]: Line numbers where text was found
        """
        if not text:
            self.update_state(search_text="", search_results=[], current_search_index=0)
            return []

        buffer = self.state.get("content_buffer", [])
        search_results = []

        for i, content in enumerate(buffer):
            lines = content.split("\n")
            for j, line in enumerate(lines):
                if text.lower() in line.lower():
                    # Calculate overall line number
                    line_number = sum(content[:i].count("\n") for content in buffer[:i])
                    line_number += j
                    search_results.append(line_number)

        self.update_state(
            search_text=text,
            search_results=search_results,
            current_search_index=0 if search_results else -1,
        )

        return search_results

    def navigate_search_results(self, direction: str) -> Optional[int]:
        """
        Navigate through search results.

        Args:
            direction: "next" or "previous"

        Returns:
            Optional[int]: Current search result line number, or None if no results
        """
        search_results = self.state.get("search_results", [])
        if not search_results:
            return None

        current_index = self.state.get("current_search_index", -1)

        if direction == "next":
            current_index = (current_index + 1) % len(search_results)
        elif direction == "previous":
            current_index = (current_index - 1) % len(search_results)

        self.update_state(current_search_index=current_index)
        return search_results[current_index]

    def get_content(self) -> str:
        """
        Get all content from the display area.

        Returns:
            str: All content joined together
        """
        buffer = self.state.get("content_buffer", [])
        return "".join(buffer)

    def get_line_count(self) -> int:
        """
        Get the current number of lines in the display area.

        Returns:
            int: Number of lines
        """
        return self.state.get("line_count", 0)

    def set_max_lines(self, max_lines: int) -> None:
        """
        Set the maximum number of lines to keep.

        Args:
            max_lines: Maximum lines to keep
        """
        self.update_state(max_lines=max_lines)

        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.max_lines = max_lines

    def set_auto_scroll(self, auto_scroll: bool) -> None:
        """
        Set whether to auto-scroll to new content.

        Args:
            auto_scroll: Whether to enable auto-scroll
        """
        self.update_state(auto_scroll=auto_scroll)

        if hasattr(self, "_rich_log") and self._rich_log:
            self._rich_log.auto_scroll = auto_scroll

    def _restore_buffered_content(self) -> None:
        """Restore any buffered content to the RichLog widget."""
        if hasattr(self, "_rich_log") and self._rich_log:
            buffer = self.state.get("content_buffer", [])
            for content in buffer:
                self._rich_log.write(content)

    def get_widget(self) -> Optional[RichLog]:
        """
        Get the underlying RichLog widget.

        Returns:
            Optional[RichLog]: The RichLog widget, or None if not yet rendered
        """
        return self._rich_log
