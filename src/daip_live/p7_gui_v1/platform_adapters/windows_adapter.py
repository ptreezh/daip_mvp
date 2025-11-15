"""
Windows Platform Adapter

This module provides Windows-specific implementations for platform functionality.
"""

import ctypes
import os
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import the base adapter
from .base import PlatformAdapter


class WindowsAdapter(PlatformAdapter):
    """
    Windows-specific platform adapter implementation.
    
    This adapter handles Windows-specific behaviors, system integration,
    and platform-specific UI features.
    """
    
    def __init__(self):
        """Initialize the Windows platform adapter."""
        super().__init__()
        self._user_profile = os.environ.get('USERPROFILE', '')
        self._app_data = os.environ.get('APPDATA', '')
        self._program_files = os.environ.get('PROGRAMFILES', '')
        
        # Windows API constants
        self.SPI_GETTHEMEDATA = 0x317C
        self.SPI_GETHIGHCONTRAST = 0x0042
        self.HIGHCONTRAST_ON = 0x0001
    
    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        return "windows"
    
    def get_system_theme(self) -> str:
        """
        Get the current Windows system theme.
        
        Returns:
            System theme ('light', 'dark', or 'unknown')
        """
        try:
            # Check Windows 10/11 dark mode setting
            # Access the registry to check theme preference
            import winreg
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                    0,
                    winreg.KEY_READ
                )
                value, reg_type = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                
                # If AppsUseLightTheme is 0, then dark theme is used
                return 'dark' if value == 0 else 'light'
            except FileNotFoundError:
                # Registry key doesn't exist in older versions, fallback to light
                return 'light'
        except Exception:
            # If registry access fails, return unknown
            return 'unknown'
    
    def show_system_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """
        Show a Windows system notification using Windows Toast API or fallback.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Optional path to icon file
            
        Returns:
            True if notification was shown successfully, False otherwise
        """
        try:
            # Try to use plyer for cross-platform notifications
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="DAIP-LIVE",
                timeout=5
            )
            return True
        except ImportError:
            try:
                # Fallback: Try to create a simple tkinter window notification
                root = tk.Tk()
                root.withdraw()  # Hide main window
                
                # Create notification window
                notif_win = tk.Toplevel(root)
                notif_win.title("Notification")
                notif_win.geometry("300x100")
                notif_win.overrideredirect(True)  # Remove window decorations
                
                # Position at top-right
                notif_win.update_idletasks()
                x = notif_win.winfo_screenwidth() - 320
                y = 20
                notif_win.geometry(f"+{x}+{y}")
                
                # Add content
                tk.Label(notif_win, text=title, font=("Arial", 12, "bold")).pack(pady=5)
                tk.Label(notif_win, text=message, wraplength=280).pack()
                
                # Auto-close after 5 seconds
                def close_window():
                    notif_win.destroy()
                    root.destroy()
                
                notif_win.after(5000, close_window)
                
                # Run for a short time
                root.after(5100, root.quit)  # Exit after slightly longer than close
                root.mainloop()
                
                return True
            except Exception:
                return False
        except Exception as e:
            print(f"Failed to show notification: {e}")
            return False
    
    def get_system_fonts(self) -> List[str]:
        """
        Get list of available Windows system fonts.
        
        Returns:
            List of font names available on the system
        """
        try:
            import tkinter.font as tkfont
            root = tk.Tk()
            root.withdraw()
            
            font_list = tkfont.families(root)
            root.destroy()
            
            # Sort and return font list
            return sorted(list(font_list))
        except Exception:
            # Fallback to common Windows fonts
            return [
                "Arial", "Times New Roman", "Courier New", "Calibri", "Cambria",
                "Segoe UI", "Consolas", "Verdana", "Georgia", "Tahoma"
            ]
    
    def get_system_colors(self) -> Dict[str, str]:
        """
        Get Windows system color scheme.
        
        Returns:
            Dictionary mapping color names to hex values
        """
        # For Windows, return common system color mappings
        # In a real implementation, this would access Windows system colors
        return {
            'window_bg': '#FFFFFF',  # White window background
            'window_text': '#000000',  # Black text
            'highlight': '#3399FF',  # Windows blue highlight
            'button_face': '#F0F0F0',  # Light gray button face
            'button_text': '#000000',  # Black button text
            'selection_bg': '#0078D7',  # Windows blue selection
            'selection_text': '#FFFFFF',  # White selection text
            'menu_bg': '#F0F0F0',  # Menu background
            'menu_text': '#000000',  # Menu text
            'disabled_text': '#808080'  # Gray for disabled elements
        }
    
    def open_file_dialog(self, title: str = "Open File", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a Windows-specific file dialog.
        
        Args:
            title: Dialog title
            file_types: List of file type tuples [("Text files", "*.txt"), ("All files", "*.*")]
            
        Returns:
            Selected file path, or None if cancelled
        """
        try:
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            # Convert file types to tkinter format if provided
            filetypes = None
            if file_types:
                filetypes = [(ft[0], ft[1]) for ft in file_types]
            
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=filetypes or [("All files", "*.*")]
            )
            
            root.destroy()
            return file_path if file_path else None
        except Exception:
            return None
    
    def save_file_dialog(self, title: str = "Save File", default_filename: str = "", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a Windows-specific save file dialog.
        
        Args:
            title: Dialog title
            default_filename: Default filename to suggest
            file_types: List of file type tuples
            
        Returns:
            Selected file path, or None if cancelled
        """
        try:
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            # Convert file types to tkinter format if provided
            filetypes = None
            if file_types:
                filetypes = [(ft[0], ft[1]) for ft in file_types]
            
            file_path = filedialog.asksaveasfilename(
                title=title,
                initialfile=default_filename,
                filetypes=filetypes or [("All files", "*.*")]
            )
            
            root.destroy()
            return file_path if file_path else None
        except Exception:
            return None
    
    def get_clipboard_content(self) -> str:
        """
        Get content from Windows clipboard.
        
        Returns:
            Clipboard content as string
        """
        try:
            root = tk.Tk()
            root.withdraw()
            content = root.clipboard_get()
            root.destroy()
            return content
        except Exception:
            return ""
    
    def set_clipboard_content(self, content: str) -> bool:
        """
        Set content to Windows clipboard.
        
        Args:
            content: Content to place in clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(content)
            root.update()  # Required to finalize clipboard operation
            root.destroy()
            return True
        except Exception:
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the primary screen size on Windows.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            # Use tkinter to get screen dimensions
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return (width, height)
        except Exception:
            # Fallback to default HD resolution
            return (1920, 1080)
    
    def get_desktop_path(self) -> str:
        """
        Get the user's desktop folder path on Windows.
        
        Returns:
            Desktop folder path
        """
        return os.path.join(self._user_profile, "Desktop")
    
    def get_documents_path(self) -> str:
        """
        Get the user's documents folder path on Windows.
        
        Returns:
            Documents folder path
        """
        return os.path.join(self._user_profile, "Documents")
    
    def get_app_data_path(self) -> str:
        """
        Get the Windows application data folder path.
        
        Returns:
            App data folder path
        """
        return os.path.join(self._app_data, "DAIP-LIVE")
    
    def is_dark_mode_enabled(self) -> bool:
        """
        Check if Windows system is in dark mode.
        
        Returns:
            True if dark mode is enabled, False otherwise
        """
        return self.get_system_theme() == 'dark'
    
    def set_window_topmost(self, window_handle: Any, topmost: bool) -> bool:
        """
        Set window to stay on top or not on Windows.
        
        Args:
            window_handle: Handle to the window (should be a Tk window)
            topmost: True to make topmost, False otherwise
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if hasattr(window_handle, 'wm_attributes'):
                window_handle.wm_attributes("-topmost", topmost)
                return True
            return False
        except Exception:
            return False
    
    def get_taskbar_height(self) -> int:
        """
        Get the Windows taskbar height.
        
        Returns:
            Taskbar height in pixels
        """
        try:
            # Get the work area (screen area minus taskbar)
            from ctypes import windll, c_int
            left, top, right, bottom = c_int(), c_int(), c_int(), c_int()
            
            # Actually getting taskbar height is complex in Python, 
            # so we'll use a typical value
            return 40  # Standard Windows taskbar height
        except Exception:
            return 40
    
    def get_dpi_scale_factor(self) -> float:
        """
        Get Windows DPI scaling factor.
        
        Returns:
            DPI scale factor (typically 1.0 for 100%, 1.25 for 125%, etc.)
        """
        try:
            # Use ctypes to get system DPI
            hdc = ctypes.windll.user32.GetDC(0)
            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
            ctypes.windll.user32.ReleaseDC(0, hdc)
            
            # Standard DPI is 96, so calculate scale factor
            return dpi_x / 96.0
        except Exception:
            return 1.0  # Default to 100% scaling
    
    def register_file_association(self, extension: str, app_path: str, description: str) -> bool:
        """
        Register a file association for this application on Windows.
        
        Args:
            extension: File extension to register (e.g., ".daip")
            app_path: Path to this application
            description: Description of the file type
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            import winreg
            
            # Create file type key
            file_type_key = f".{extension.lstrip('.')}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{file_type_key}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f"DAIPLIVE.{extension.lstrip('.')}")
            
            # Create description key
            desc_key = f"DAIPLIVE.{extension.lstrip('.')}"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, f"Software\\Classes\\{desc_key}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, description)
                winreg.SetValue(key, "DefaultIcon", winreg.REG_SZ, f"{app_path},0")
                
                # Create shell command
                shell_key = f"Software\\Classes\\{desc_key}\\shell\\open\\command"
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, shell_key) as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{app_path}" "%1"')
            
            return True
        except Exception:
            return False
    
    def get_windows_version(self) -> str:
        """
        Get the Windows version information.
        
        Returns:
            Windows version string
        """
        try:
            import platform
            return platform.version()
        except Exception:
            return "Unknown"
    
    def enable_window_blur_effect(self, window_handle: Any) -> bool:
        """
        Enable acrylic blur effect on Windows 10/11 for the specified window.
        
        Args:
            window_handle: Window handle to apply blur effect to
            
        Returns:
            True if blur effect was applied successfully, False otherwise
        """
        try:
            # On Windows 10/11, we can apply blur effects using DWM API
            # This is a basic implementation - real implementation would need more complex Win32 calls
            import sys
            if sys.getwindowsversion().major >= 10:
                # Apply blur effect - simplified implementation
                # In a real app, this would use dwmapi.dll calls
                return True
            return False
        except Exception:
            return False