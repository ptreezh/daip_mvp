"""
Platform Adapters for DAIP-LIVE P7 GUI

This module provides platform-specific implementations for cross-platform compatibility.
Each adapter handles platform-specific behaviors, system integration, and UI differences.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PlatformAdapter(ABC):
    """
    Base class for platform-specific adapters.
    
    This abstract class defines the interface that all platform adapters must implement.
    Each platform (Windows, macOS, Linux) will have its own implementation that handles
    platform-specific behaviors like file dialogs, system integration, etc.
    """
    
    def __init__(self):
        """Initialize the platform adapter."""
        self._platform_name = self.get_platform_name()
        self._is_initialized = False
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Get the name of the platform.
        
        Returns:
            Platform name (e.g., 'windows', 'macos', 'linux')
        """
        pass
    
    @abstractmethod
    def get_system_theme(self) -> str:
        """
        Get the current system theme.
        
        Returns:
            System theme ('light', 'dark', or 'unknown')
        """
        pass
    
    @abstractmethod
    def show_system_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """
        Show a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Optional path to icon file
            
        Returns:
            True if notification was shown successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def get_system_fonts(self) -> list:
        """
        Get list of available system fonts.
        
        Returns:
            List of font names available on the system
        """
        pass
    
    @abstractmethod
    def get_system_colors(self) -> Dict[str, str]:
        """
        Get system color scheme.
        
        Returns:
            Dictionary mapping color names to hex values
        """
        pass
    
    @abstractmethod
    def open_file_dialog(self, title: str = "Open File", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a platform-specific file dialog.
        
        Args:
            title: Dialog title
            file_types: List of file type tuples [("Text files", "*.txt"), ("All files", "*.*")]
            
        Returns:
            Selected file path, or None if cancelled
        """
        pass
    
    @abstractmethod
    def save_file_dialog(self, title: str = "Save File", default_filename: str = "", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a platform-specific save file dialog.
        
        Args:
            title: Dialog title
            default_filename: Default filename to suggest
            file_types: List of file type tuples
            
        Returns:
            Selected file path, or None if cancelled
        """
        pass
    
    @abstractmethod
    def get_clipboard_content(self) -> str:
        """
        Get content from system clipboard.
        
        Returns:
            Clipboard content as string
        """
        pass
    
    @abstractmethod
    def set_clipboard_content(self, content: str) -> bool:
        """
        Set content to system clipboard.
        
        Args:
            content: Content to place in clipboard
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_screen_size(self) -> tuple[int, int]:
        """
        Get the primary screen size.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        pass
    
    @abstractmethod
    def get_desktop_path(self) -> str:
        """
        Get the user's desktop folder path.
        
        Returns:
            Desktop folder path
        """
        pass
    
    @abstractmethod
    def get_documents_path(self) -> str:
        """
        Get the user's documents folder path.
        
        Returns:
            Documents folder path
        """
        pass
    
    @abstractmethod
    def get_app_data_path(self) -> str:
        """
        Get the application data folder path.
        
        Returns:
            App data folder path
        """
        pass
    
    @abstractmethod
    def is_dark_mode_enabled(self) -> bool:
        """
        Check if the system is in dark mode.
        
        Returns:
            True if dark mode is enabled, False otherwise
        """
        pass
    
    @abstractmethod
    def set_window_topmost(self, window_handle: Any, topmost: bool) -> bool:
        """
        Set window to stay on top or not.
        
        Args:
            window_handle: Handle to the window
            topmost: True to make topmost, False otherwise
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def initialize(self) -> bool:
        """
        Initialize the platform adapter.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            self._is_initialized = True
            return True
        except Exception:
            self._is_initialized = False
            return False
    
    def is_initialized(self) -> bool:
        """
        Check if the adapter has been initialized.
        
        Returns:
            True if initialized, False otherwise
        """
        return self._is_initialized
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get comprehensive platform information.
        
        Returns:
            Dictionary containing platform information
        """
        return {
            'platform_name': self.get_platform_name(),
            'is_dark_mode': self.is_dark_mode_enabled(),
            'system_fonts': self.get_system_fonts(),
            'system_colors': self.get_system_colors(),
            'screen_size': self.get_screen_size(),
            'initialized': self.is_initialized()
        }


def get_current_platform_adapter() -> PlatformAdapter:
    """
    Get the appropriate platform adapter for the current system.
    
    Returns:
        PlatformAdapter instance for the current platform
    """
    current_platform = sys.platform
    
    if current_platform.startswith("win"):
        from .windows_adapter import WindowsAdapter
        return WindowsAdapter()
    elif current_platform.startswith("darwin"):
        from .macos_adapter import MacOSAdapter
        return MacOSAdapter()
    elif current_platform.startswith("linux"):
        from .linux_adapter import LinuxAdapter
        return LinuxAdapter()
    else:
        # Fallback to generic adapter for unknown platforms
        raise NotImplementedError(f"Platform {current_platform} is not supported yet")


def create_platform_adapter(platform_name: str) -> PlatformAdapter:
    """
    Create a specific platform adapter by name.
    
    Args:
        platform_name: Name of the platform ('windows', 'macos', 'linux')
        
    Returns:
        PlatformAdapter instance for the specified platform
    """
    platform_name = platform_name.lower()
    
    if platform_name == 'windows':
        from .windows_adapter import WindowsAdapter
        return WindowsAdapter()
    elif platform_name == 'macos':
        from .macos_adapter import MacOSAdapter
        return MacOSAdapter()
    elif platform_name == 'linux':
        from .linux_adapter import LinuxAdapter
        return LinuxAdapter()
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")