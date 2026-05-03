"""
Clipboard Helper for DAIP-LIVE TUI
Provides cross-platform clipboard functionality
"""

import pyperclip
import sys
import platform
from typing import Optional, Union


class ClipboardHelper:
    """Helper class for cross-platform clipboard operations."""
    
    def __init__(self):
        """Initialize clipboard helper."""
        self.platform = platform.system()
        
    def copy_to_clipboard(self, content: Union[str, list, dict]) -> bool:
        """
        Copy content to system clipboard.
        
        Args:
            content: Content to copy (string, list, or dict)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert content to string if needed
            if isinstance(content, (list, dict)):
                import json
                content_str = json.dumps(content, ensure_ascii=False, indent=2)
            else:
                content_str = str(content)
                
            # Use pyperclip to copy to clipboard
            pyperclip.copy(content_str)
            return True
            
        except Exception as e:
            print(f"Clipboard copy failed: {e}", file=sys.stderr)
            return False
    
    def get_clipboard_content(self) -> Optional[str]:
        """
        Get content from system clipboard.
        
        Returns:
            Content from clipboard or None if unavailable
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Clipboard paste failed: {e}", file=sys.stderr)
            return None
    
    def is_available(self) -> bool:
        """
        Check if clipboard functionality is available.
        
        Returns:
            True if clipboard is available, False otherwise
        """
        try:
            # Test by trying to access clipboard
            pyperclip.paste()
            return True
        except:
            return False


# Singleton instance
clipboard_helper = ClipboardHelper()


def copy_content(content: Union[str, list, dict]) -> bool:
    """
    Convenience function to copy content to clipboard.
    
    Args:
        content: Content to copy
        
    Returns:
        True if successful, False otherwise
    """
    return clipboard_helper.copy_to_clipboard(content)