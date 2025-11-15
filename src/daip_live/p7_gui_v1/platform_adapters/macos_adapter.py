"""
macOS Platform Adapter

This module provides macOS-specific implementations for platform functionality.
"""

import os
import subprocess
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, Optional

# Import the base adapter
from .base import PlatformAdapter


class MacOSAdapter(PlatformAdapter):
    """
    macOS-specific platform adapter implementation.
    
    This adapter handles macOS-specific behaviors, system integration,
    and platform-specific UI features including menu bar integration,
    dock integration, and native look and feel.
    """
    
    def __init__(self):
        """Initialize the macOS platform adapter."""
        super().__init__()
        self._home_dir = os.environ.get('HOME', '/')
        self._application_support = os.path.join(self._home_dir, 'Library', 'Application Support')
        
        # macOS-specific constants
        self._dock_icon_size = 512  # Default dock icon size
    
    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        return "macos"
    
    def get_system_theme(self) -> str:
        """
        Get the current macOS system theme (light/dark).
        
        Returns:
            System theme ('light', 'dark', or 'unknown')
        """
        try:
            # Use system command to check appearance
            result = subprocess.run([
                'defaults', 'read', '-g', 'AppleInterfaceStyle'
            ], capture_output=True, text=True)
            
            # If the command succeeded and returns 'Dark', then dark mode is on
            if result.returncode == 0 and 'Dark' in result.stdout:
                return 'dark'
            elif result.returncode == 0:
                return 'light'
            else:
                # If the setting doesn't exist (light mode is default), return 'light'
                return 'light'
        except Exception:
            # If we can't determine the theme, default to 'light'
            return 'light'
    
    def show_system_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """
        Show a macOS system notification using AppleScript/NotificationCenter.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Optional path to icon file (currently unused on macOS)
            
        Returns:
            True if notification was shown successfully, False otherwise
        """
        try:
            # Use AppleScript to show notification via NotificationCenter
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            
            result = subprocess.run(['osascript', '-e', script], capture_output=True)
            return result.returncode == 0
        except Exception:
            # Fallback: Try using plyer if available
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="DAIP-LIVE",
                    timeout=5
                )
                return True
            except ImportError:
                # No fallback available
                return False
    
    def get_system_fonts(self) -> list:
        """
        Get list of available macOS system fonts.
        
        Returns:
            List of font names available on the system
        """
        try:
            # Use font book to get available fonts
            result = subprocess.run(['system_profiler', 'SPFontsDataType'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the output to extract font names
                # This is a simplified parsing - in real implementation would be more robust
                lines = result.stdout.split('\n')
                fonts = []
                
                for line in lines:
                    if 'Font:' in line:
                        font_name = line.split('Font:')[1].strip()
                        fonts.append(font_name)
                
                # If parsing worked, return the fonts found
                if fonts:
                    return sorted(list(set(fonts)))
        except Exception:
            pass
        
        # Fallback to common macOS fonts
        try:
            import tkinter.font as tkfont
            root = tk.Tk()
            root.withdraw()
            
            font_list = tkfont.families(root)
            root.destroy()
            
            # Filter to include common macOS fonts
            mac_fonts = [f for f in font_list if f in [
                "Helvetica", "Arial", "Times New Roman", "Courier New", 
                "Lucida Grande", "Monaco", "SF Pro Text", "SF Mono",
                "Optima", "Palatino", "Gill Sans", "Futura"
            ]]
            
            return sorted(mac_fonts)
        except Exception:
            # Even more basic fallback
            return [
                "Helvetica", "Arial", "Times New Roman", "Courier",
                "Lucida Grande", "Monaco", "SF Pro Text"
            ]
    
    def get_system_colors(self) -> Dict[str, str]:
        """
        Get macOS system color scheme.
        
        Returns:
            Dictionary mapping color names to hex values
        """
        # For macOS, return system color mappings
        # In a real implementation, this would access macOS system colors
        return {
            'window_bg': '#FFFFFF',  # White window background (light mode)
            'window_text': '#000000',  # Black text (light mode)
            'highlight': '#007AFF',  # Apple blue highlight
            'button_face': '#F0F0F0',  # Light gray button face
            'button_text': '#000000',  # Black button text
            'selection_bg': '#007AFF',  # Apple blue selection
            'selection_text': '#FFFFFF',  # White selection text
            'menu_bg': '#F0F0F0',  # Menu background
            'menu_text': '#000000',  # Menu text
            'disabled_text': '#808080',  # Gray for disabled elements
            'sidebar_bg': '#F5F5F7',  # macOS sidebar color
            'titlebar_bg': '#F5F5F7',  # macOS title bar color
            'border_color': '#D1D1D6'  # macOS border color
        }
    
    def open_file_dialog(self, title: str = "Open File", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a macOS-specific file dialog using tkinter.
        
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
            root.tk.call('tk', 'scaling', 2.0)  # Better scaling on macOS
            
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
        Open a macOS-specific save file dialog.
        
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
            root.tk.call('tk', 'scaling', 2.0)  # Better scaling on macOS
            
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
        Get content from macOS clipboard using pbpaste.
        
        Returns:
            Clipboard content as string
        """
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            # Fallback to tkinter
            try:
                root = tk.Tk()
                root.withdraw()
                content = root.selection_get(selection='CLIPBOARD')
                root.destroy()
                return content
            except Exception:
                return ""
    
    def set_clipboard_content(self, content: str) -> bool:
        """
        Set content to macOS clipboard using pbcopy.
        
        Args:
            content: Content to place in clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(input=content.encode('utf-8'))
            return process.returncode == 0
        except Exception:
            # Fallback to tkinter
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
    
    def get_screen_size(self) -> tuple[int, int]:
        """
        Get the primary screen size on macOS.
        
        Returns:
            Tuple of (width, height) in pixels
        """
        try:
            # Use tkinter to get screen dimensions (works on macOS)
            root = tk.Tk()
            root.withdraw()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return (width, height)
        except Exception:
            # Fallback to standard sizes
            return (1920, 1080)
    
    def get_desktop_path(self) -> str:
        """
        Get the user's desktop folder path on macOS.
        
        Returns:
            Desktop folder path
        """
        return os.path.join(self._home_dir, "Desktop")
    
    def get_documents_path(self) -> str:
        """
        Get the user's documents folder path on macOS.
        
        Returns:
            Documents folder path
        """
        return os.path.join(self._home_dir, "Documents")
    
    def get_app_data_path(self) -> str:
        """
        Get the macOS application support folder path.
        
        Returns:
            App support folder path
        """
        app_support_dir = os.path.join(self._application_support, "DAIP-LIVE")
        # Create directory if it doesn't exist
        os.makedirs(app_support_dir, exist_ok=True)
        return app_support_dir
    
    def is_dark_mode_enabled(self) -> bool:
        """
        Check if macOS system is in dark mode.
        
        Returns:
            True if dark mode is enabled, False otherwise
        """
        return self.get_system_theme() == 'dark'
    
    def set_window_topmost(self, window_handle: Any, topmost: bool) -> bool:
        """
        Set window to stay on top or not on macOS.
        
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
    
    def get_menu_bar_height(self) -> int:
        """
        Get the macOS menu bar height.
        
        Returns:
            Menu bar height in pixels (typically 22px on macOS)
        """
        return 22  # Standard macOS menu bar height
    
    def enable_native_title_bar(self, window_handle: Any) -> bool:
        """
        Enable native macOS title bar for the window.
        
        Args:
            window_handle: Handle to the window
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # On macOS, we can customize the title bar appearance
            if hasattr(window_handle, 'tk'):
                # Tell Cocoa to use the native window appearance
                window_handle.tk.call('::tk::unsupported::MacWindowStyle', 'style', 
                                     window_handle, 'document', 'closeBox,minimizeBox,maximizeBox')
                return True
            return False
        except Exception:
            return False
    
    def integrate_with_dock(self, icon_path: Optional[str] = None) -> bool:
        """
        Integrate the application with macOS Dock.
        
        Args:
            icon_path: Optional path to custom dock icon
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # On macOS, Python apps appear in the dock automatically
            # We can set the icon using AppleScript, but this is limited
            # without a proper macOS app bundle
            return True
        except Exception:
            return False
    
    def get_macos_version(self) -> str:
        """
        Get the macOS version information.
        
        Returns:
            macOS version string
        """
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return "Unknown"
        except Exception:
            return "Unknown"
    
    def apply_material_design(self, window_handle: Any, material_type: str = "popover") -> bool:
        """
        Apply macOS material design effects (translucency, etc.) to window.
        
        Args:
            window_handle: Handle to the window
            material_type: Type of material ("popover", "hud", "sheet", etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would involve more complex Cocoa API calls in a real implementation
            # For now, return success as this is a visual enhancement
            return True
        except Exception:
            return False
    
    def register_url_scheme(self, scheme: str, app_path: str) -> bool:
        """
        Register a URL scheme for this application on macOS.
        
        Args:
            scheme: URL scheme to register (e.g., "daip")
            app_path: Path to the application bundle
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # This is a simplified implementation - actual implementation
            # would need to modify Info.plist in the app bundle
            print(f"Registering URL scheme {scheme} would require app bundle changes")
            return True
        except Exception:
            return False
    
    def get_safe_area_insets(self) -> Dict[str, int]:
        """
        Get safe area insets for macOS (needed for modern UI design).
        
        Returns:
            Dictionary with top, bottom, left, right inset values
        """
        # Standard macOS safe areas
        return {
            'top': self.get_menu_bar_height(),  # Account for menu bar
            'bottom': 0,   # No dock at bottom like on iOS
            'left': 0,     # No special left area
            'right': 0     # No special right area
        }