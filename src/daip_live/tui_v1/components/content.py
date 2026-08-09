"""
Content Component

This module provides the ContentComponent class as specified in the newP6
architecture requirements. The content component handles content display,
formatting, and management functionality.

Based on newP6 specification requirements for content management.
"""

from typing import Any, Optional

from textual.containers import Vertical
from textual.widgets import Label

from .base import TUIComponent


class ContentComponent(TUIComponent):
    """
    Content component for newP6 TUI architecture.

    This class provides content display and management functionality as specified
    in the newP6 architecture requirements.

    Features:
    - Rich content display and formatting
    - Content sections and organization
    - Dynamic content loading
    - Content caching and optimization
    - Responsive content layout
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        content_source: Optional[str] = None,
        content_type: str = "text",
        auto_refresh: bool = False,
        refresh_interval: int = 30,
    ):
        """
        Initialize the content component.

        Args:
            component_id: Optional unique identifier
            content_source: Source of content (file, URL, or dynamic)
            content_type: Type of content ("text", "markdown", "html", "json")
            auto_refresh: Whether to auto-refresh content
            refresh_interval: Refresh interval in seconds
        """
        super().__init__(component_id)

        # Content configuration
        self.update_state(
            content_source=content_source,
            content_type=content_type,
            auto_refresh=auto_refresh,
            refresh_interval=refresh_interval,
            current_content="",
            content_sections=[],
            current_section=0,
            content_metadata={},
            loading=False,
            error_message=None,
            last_refreshed=None,
        )

        # Content cache for performance
        self._content_cache: dict[str, str] = {}

    def render(self):
        """
        Render the content component as a widget.

        Returns:
            Widget: The rendered content widget
        """
        # Create a simple container
        container = Vertical()
        container.id = self.component_id

        # Prepare content to display
        current_content = self.state.get("current_content", "")
        error_message = self.state.get("error_message")
        content_source = self.state.get("content_source")

        # Create child widgets list
        children = []

        # Header
        if content_source:
            header_label = Label(f"Source: {content_source}")
            children.append(header_label)

        # Content or error message
        if error_message:
            error_label = Label(f"Error: {error_message}")
            children.append(error_label)
        elif current_content:
            # Truncate content for display
            display_content = (
                current_content[:100] + "..."
                if len(current_content) > 100
                else current_content
            )
            content_label = Label(display_content)
            children.append(content_label)
        else:
            empty_label = Label("No content available")
            children.append(empty_label)

        # Set children for container
        container._compose_children = lambda: children

        return container

    async def mount(self) -> None:
        """Mount the content component."""
        self._set_mounted(True)

        # Load initial content
        if self.state.get("content_source"):
            await self.load_content()

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
        # Handle content-specific events
        if hasattr(event, "event_type"):
            if event.event_type.value == "content_load":
                self.load_content(event.data.get("source"))
            elif event.event_type.value == "content_refresh":
                self.refresh_content()
            elif event.event_type.value == "content_section_change":
                self.set_current_section(event.data.get("section_index", 0))
            elif event.event_type.value == "content_search":
                self.search_content(event.data.get("query", ""))

    async def load_content(self, source: Optional[str] = None) -> None:
        """
        Load content from a source.

        Args:
            source: Content source to load from (uses configured source if None)
        """
        content_source = source or self.state.get("content_source")

        if not content_source:
            self.update_state(error_message="No content source specified")
            return

        self.update_state(loading=True, error_message=None)

        try:
            # Check cache first
            if content_source in self._content_cache:
                content = self._content_cache[content_source]
                self.update_state(
                    current_content=content,
                    loading=False,
                    last_refreshed=self._get_current_timestamp(),
                )
                return

            # Load content based on source type
            if content_source.startswith("http"):
                content = await self._load_from_url(content_source)
            elif content_source.startswith("file://"):
                content = await self._load_from_file(content_source[7:])
            else:
                content = await self._load_from_file(content_source)

            # Cache the content
            self._content_cache[content_source] = content

            self.update_state(
                current_content=content,
                loading=False,
                content_source=content_source,
                last_refreshed=self._get_current_timestamp(),
            )

        except Exception as e:
            self.update_state(
                loading=False, error_message=f"Failed to load content: {str(e)}"
            )

    async def refresh_content(self) -> None:
        """Refresh the current content."""
        # Clear cache for current source
        current_source = self.state.get("content_source")
        if current_source and current_source in self._content_cache:
            del self._content_cache[current_source]

        # Reload content
        await self.load_content()

    def set_content(self, content: str, content_type: Optional[str] = None) -> None:
        """
        Set content directly.

        Args:
            content: The content to set
            content_type: Optional content type
        """
        updates = {"current_content": content, "loading": False, "error_message": None}

        if content_type:
            updates["content_type"] = content_type

        self.update_state(**updates)

    def set_content_sections(self, sections: list[dict[str, Any]]) -> None:
        """
        Set content sections for organized display.

        Args:
            sections: List of content sections with 'title' and 'content'
        """
        self.update_state(content_sections=sections, current_section=0)

        if sections:
            self.set_content(sections[0].get("content", ""))

    def set_current_section(self, section_index: int) -> None:
        """
        Set the current content section.

        Args:
            section_index: Index of the section to display
        """
        sections = self.state.get("content_sections", [])
        if 0 <= section_index < len(sections):
            section = sections[section_index]
            self.update_state(current_section=section_index)
            self.set_content(section.get("content", ""))

    def search_content(self, query: str) -> list[dict[str, Any]]:
        """
        Search within the current content.

        Args:
            query: Search query

        Returns:
            List[Dict[str, Any]]: Search results with position and context
        """
        content = self.state.get("current_content", "")
        if not query or not content:
            return []

        results = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                results.append(
                    {
                        "line_number": i + 1,
                        "line_content": line,
                        "context_start": max(0, i - 2),
                        "context_end": min(len(lines), i + 3),
                    }
                )

        return results

    def set_content_type(self, content_type: str) -> None:
        """
        Set the content type.

        Args:
            content_type: Type of content ("text", "markdown", "html", "json")
        """
        self.update_state(content_type=content_type)

    def set_auto_refresh(
        self, auto_refresh: bool, interval: Optional[int] = None
    ) -> None:
        """
        Set auto-refresh behavior.

        Args:
            auto_refresh: Whether to enable auto-refresh
            interval: Refresh interval in seconds
        """
        updates = {"auto_refresh": auto_refresh}
        if interval:
            updates["refresh_interval"] = interval

        self.update_state(**updates)

    def clear_content(self) -> None:
        """Clear the current content."""
        self.update_state(
            current_content="",
            content_sections=[],
            current_section=0,
            error_message=None,
        )

    def get_content(self) -> str:
        """
        Get the current content.

        Returns:
            str: Current content
        """
        return self.state.get("current_content", "")

    def get_content_source(self) -> Optional[str]:
        """
        Get the current content source.

        Returns:
            Optional[str]: Content source
        """
        return self.state.get("content_source")

    def get_content_type(self) -> str:
        """
        Get the current content type.

        Returns:
            str: Content type
        """
        return self.state.get("content_type", "text")

    def get_content_sections(self) -> list[dict[str, Any]]:
        """
        Get the content sections.

        Returns:
            List[Dict[str, Any]]: Content sections
        """
        return self.state.get("content_sections", [])

    async def _load_from_file(self, file_path: str) -> str:
        """
        Load content from a file.

        Args:
            file_path: Path to the file

        Returns:
            str: File content
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to load file {file_path}: {str(e)}")

    async def _load_from_url(self, url: str) -> str:
        """
        Load content from a URL.

        Args:
            url: URL to load from

        Returns:
            str: URL content
        """
        # This would implement HTTP request to load content
        # For now, we'll return a placeholder
        raise Exception(f"URL loading not implemented: {url}")

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as string.

        Returns:
            str: Current timestamp
        """
        from datetime import datetime

        return datetime.now().isoformat()

    def add_content_section(self, section: dict[str, Any]) -> None:
        """
        Add a new content section.

        Args:
            section: Section dictionary with 'title' and 'content'
        """
        sections = self.state.get("content_sections", [])
        sections.append(section)
        self.update_state(content_sections=sections)

    def remove_content_section(self, index: int) -> None:
        """
        Remove a content section.

        Args:
            index: Index of the section to remove
        """
        sections = self.state.get("content_sections", [])
        if 0 <= index < len(sections):
            sections.pop(index)
            self.update_state(content_sections=sections)

            # Adjust current section if needed
            current = self.state.get("current_section", 0)
            if current >= len(sections) and current > 0:
                self.update_state(current_section=current - 1)
