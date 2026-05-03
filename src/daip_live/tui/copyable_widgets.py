"""
Extended Copyable widgets for DAIP-LIVE TUI
Extends Textual components with clipboard functionality
"""

from textual.widgets import RichLog, Static
from textual.message import Message
from textual.reactive import reactive
from textual import events
import pyperclip

from .clipboard_helper import copy_content


class CopyableLogWidget(RichLog):
    """Enhanced RichLog widget with copy functionality."""
    
    # Reactive property to track selection state
    is_selected = reactive(False)
    selected_content = reactive("")
    
    def __init__(self, *args, copy_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.copy_enabled = copy_enabled
        self._selected_region_start = None
        self._selected_region_end = None
        self._allow_text_selection = True
    
    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        # Enable mouse support for text selection
        self.can_focus = True
        self.can_focus_children = True
    
    def copy_all_content(self) -> bool:
        """
        Copy all content in the log to clipboard.

        Returns:
            True if successful, False otherwise
        """
        try:
            # For now, we'll simulate copying by returning success
            # In a real implementation, we would extract the actual log content
            if self.copy_enabled:
                # Collect all text content from the log
                all_content = []

                # Access the internal renderables to get the text
                # This might vary depending on how RichLog stores content internally
                from rich.text import Text
                from rich.console import RenderableType
                import re

                # Define enhanced regex pattern to match Rich formatting
                def clean_rich_formatting(text: str) -> str:
                    """Remove Rich formatting tags from text."""
                    # Remove rich-style formatting tags like [bold], [red], [italic], etc.
                    # This pattern matches tags like [bold], [/bold], [red italic], [some_style=param], etc.
                    cleaned = re.sub(r'\[(/?\w+)(?:=(\w+|"[^"]*"))?(?:\s*\w+=(\w+|"[^"]*"))*\]', '', text)
                    return cleaned

                # Get the raw lines from the rich log content
                for line_idx in range(len(self.lines)):
                    line = self.lines[line_idx]
                    if isinstance(line, Text):
                        # Extract plain text without formatting
                        plain_text = line.plain
                        # Additional cleaning in case there are still rich tags
                        clean_text = clean_rich_formatting(plain_text)
                        all_content.append(clean_text)
                    else:
                        # Convert other renderables to string and strip rich formatting
                        content_str = str(line)
                        clean_content = clean_rich_formatting(content_str)
                        all_content.append(clean_content)

                full_content = '\n'.join(all_content)

                if full_content.strip():
                    return copy_content(full_content)
                else:
                    return copy_content("TUI Output Log - Empty or no content to copy")
            return False
        except Exception as e:
            print(f"Error copying log content: {e}")
            return False
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events including copy shortcut."""
        # Handle Ctrl+C for copy
        if event.key == "ctrl+c":
            event.stop()
            success = self.copy_all_content()
            if success:
                # Visual feedback that content was copied
                self.app.notify("内容已复制到剪贴板", timeout=1)
                # We could also temporarily change a status element to show success
    
    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse selection for copy."""
        # This would implement text selection logic in a full implementation
        pass


class CopyableStatic(Static):
    """Enhanced Static widget with copy functionality."""
    
    def __init__(self, *args, copy_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.copy_enabled = copy_enabled
    
    def copy_content(self) -> bool:
        """
        Copy static content to clipboard.

        Returns:
            True if successful, False otherwise
        """
        if not self.copy_enabled:
            return False

        try:
            # Get the content to copy
            import re
            # Define enhanced regex pattern to match Rich formatting
            def clean_rich_formatting(text: str) -> str:
                """Remove Rich formatting tags from text."""
                # Remove rich-style formatting tags like [bold], [red], [italic], etc.
                # This pattern matches tags like [bold], [/bold], [red italic], [some_style=param], etc.
                cleaned = re.sub(r'\[(/?\w+)(?:=(\w+|"[^"]*"))?(?:\s*\w+=(\w+|"[^"]*"))*\]', '', str(text))
                return cleaned

            content = str(self.renderable) if hasattr(self, 'renderable') else str(self)
            clean_content = clean_rich_formatting(content)
            return copy_content(clean_content)
        except Exception as e:
            print(f"Error copying static content: {e}")
            return False

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "ctrl+c" and self.copy_enabled:
            event.stop()
            success = self.copy_content()
            if success:
                self.app.notify("内容已复制到剪贴板", timeout=1)


class CopyRequested(Message):
    """Message sent when copy action is requested."""
    
    def __init__(self, widget_id: str, content: str) -> None:
        super().__init__()
        self.widget_id = widget_id
        self.content = content