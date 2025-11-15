"""
Linux Platform Adapter

This module provides Linux-specific implementations for platform functionality.
"""

import os
import tkinter as tk
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import subprocess

# Import the base adapter
from .base import PlatformAdapter


class LinuxAdapter(PlatformAdapter):
    """
    Linux-specific platform adapter implementation.
    
    This adapter handles Linux-specific behaviors, system integration,
    and platform-specific UI features including desktop environment
    integration and native look and feel.
    """
    
    def __init__(self):
        """Initialize the Linux platform adapter."""
        super().__init__()
        self._home_dir = os.environ.get('HOME', '/')
        self._xdg_config_home = os.environ.get('XDG_CONFIG_HOME', os.path.join(self._home_dir, '.config'))
        self._xdg_data_home = os.environ.get('XDG_DATA_HOME', os.path.join(self._home_dir, '.local', 'share'))
        self._xdg_cache_home = os.environ.get('XDG_CACHE_HOME', os.path.join(self._home_dir, '.cache'))
        
        # Linux-specific constants
        self._supported_desktop_environments = ['gnome', 'kde', 'xfce', 'lxde', 'mate', 'cinnamon']
    
    def get_platform_name(self) -> str:
        """Get the name of the platform."""
        return "linux"
    
    def get_system_theme(self) -> str:
        """
        Get the current Linux system theme.
        
        Returns:
            System theme ('light', 'dark', or 'unknown')
        """
        try:
            # Check GNOME settings
            result = subprocess.run([
                'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                theme_name = result.stdout.strip().strip("'\"")
                # If theme name contains 'dark', assume dark mode
                if 'dark' in theme_name.lower():
                    return 'dark'
                elif 'light' in theme_name.lower():
                    return 'light'
                else:
                    # Check for KDE dark theme settings
                    kde_result = subprocess.run([
                        'kreadconfig5', '--file', 'kdeglobals', '--group', 'Colors:Window', '--key', 'BackgroundNormal'
                    ], capture_output=True, text=True)
                    
                    if kde_result.returncode == 0:
                        kde_color = kde_result.stdout.strip()
                        # Simplified check - KDE dark themes often have lower RGB values
                        # In a real implementation, we'd parse the RGB values
                        if 'window' in kde_color.lower():
                            return 'dark' if '255' not in kde_color else 'light'
                    
                    return 'unknown'
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Fallback: check environment variables for theme info
            gtk_theme = os.environ.get('GTK_THEME', '').lower()
            if 'dark' in gtk_theme:
                return 'dark'
            elif 'light' in gtk_theme:
                return 'light'
        
        return 'unknown'
    
    def show_system_notification(self, title: str, message: str, icon: Optional[str] = None) -> bool:
        """
        Show a Linux system notification using notify-send.
        
        Args:
            title: Notification title
            message: Notification message
            icon: Optional path to icon file
            
        Returns:
            True if notification was shown successfully, False otherwise
        """
        try:
            cmd = ['notify-send', title, message]
            if icon:
                cmd.extend(['-i', icon])
            
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.CalledProcessError):
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
        Get list of available Linux system fonts.
        
        Returns:
            List of font names available on the system
        """
        try:
            # Use fc-list to get available fonts
            result = subprocess.run(['fc-list', ':family'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse font names from fc-list output
                font_lines = result.stdout.split('\n')
                fonts = set()
                
                for line in font_lines:
                    if ':' in line:
                        family = line.split(':')[0]
                        # Clean up font name
                        family = family.replace(',', '').strip()
                        if family:
                            fonts.add(family)
                
                return sorted(list(fonts))
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        # Fallback to common Linux fonts
        try:
            import tkinter.font as tkfont
            root = tk.Tk()
            root.withdraw()
            
            font_list = tkfont.families(root)
            root.destroy()
            
            # Filter to include common Linux fonts
            linux_fonts = [f for f in font_list if f in [
                "Sans", "Serif", "Mono", "Ubuntu", "DejaVu", "Liberation",
                "Noto", "Open Sans", "Roboto", "Cantarell", "Fira Sans"
            ]]
            
            return sorted(linux_fonts)
        except Exception:
            # Even more basic fallback
            return [
                "Sans", "Serif", "Mono", "Ubuntu", "DejaVu Sans",
                "Liberation Sans", "Noto Sans"
            ]
    
    def get_system_colors(self) -> Dict[str, str]:
        """
        Get Linux system color scheme.
        
        Returns:
            Dictionary mapping color names to hex values
        """
        # For Linux, return system color mappings
        # In a real implementation, this would access GTK theme colors
        return {
            'window_bg': '#FFFFFF',  # White window background
            'window_text': '#000000',  # Black text
            'highlight': '#4A90E2',  # GNOME blue highlight
            'button_face': '#F0F0F0',  # Light gray button face
            'button_text': '#000000',  # Black button text
            'selection_bg': '#4A90E2',  # GNOME blue selection
            'selection_text': '#FFFFFF',  # White selection text
            'menu_bg': '#F0F0F0',  # Menu background
            'menu_text': '#000000',  # Menu text
            'disabled_text': '#808080',  # Gray for disabled elements
            'sidebar_bg': '#F5F5F5',  # GNOME sidebar color
            'titlebar_bg': '#ECECEC',  # GNOME title bar color
            'border_color': '#CCCCCC'  # GNOME border color
        }
    
    def open_file_dialog(self, title: str = "Open File", file_types: Optional[list] = None) -> Optional[str]:
        """
        Open a Linux-specific file dialog using tkinter.
        
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
        Open a Linux-specific save file dialog.
        
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
        Get content from Linux clipboard.
        
        Returns:
            Clipboard content as string
        """
        try:
            # Try xclip first (most common)
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                # Then try xsel
                result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
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
        Set content to Linux clipboard.
        
        Args:
            content: Content to place in clipboard
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try xclip first
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(input=content.encode('utf-8'))
            return process.returncode == 0
        except (FileNotFoundError, subprocess.CalledProcessError):
            try:
                # Then try xsel
                process = subprocess.Popen(['xsel', '--clipboard', '--input'], stdin=subprocess.PIPE)
                process.communicate(input=content.encode('utf-8'))
                return process.returncode == 0
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
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
        Get the primary screen size on Linux.
        
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
            # Fallback to standard sizes
            return (1920, 1080)
    
    def get_desktop_path(self) -> str:
        """
        Get the user's desktop folder path on Linux.
        
        Returns:
            Desktop folder path
        """
        return os.path.join(self._home_dir, "Desktop")
    
    def get_documents_path(self) -> str:
        """
        Get the user's documents folder path on Linux.
        
        Returns:
            Documents folder path
        """
        return os.path.join(self._home_dir, "Documents")
    
    def get_app_data_path(self) -> str:
        """
        Get the Linux application data folder path using XDG specification.
        
        Returns:
            App data folder path
        """
        app_data_dir = os.path.join(self._xdg_data_home, "DAIP-LIVE")
        # Create directory if it doesn't exist
        os.makedirs(app_data_dir, exist_ok=True)
        return app_data_dir
    
    def is_dark_mode_enabled(self) -> bool:
        """
        Check if Linux system is in dark mode.
        
        Returns:
            True if dark mode is enabled, False otherwise
        """
        return self.get_system_theme() == 'dark'
    
    def set_window_topmost(self, window_handle: Any, topmost: bool) -> bool:
        """
        Set window to stay on top or not on Linux.
        
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
    
    def get_desktop_environment(self) -> str:
        """
        Get the current Linux desktop environment.
        
        Returns:
            Desktop environment name ('gnome', 'kde', 'xfce', etc.) or 'unknown'
        """
        try:
            # Check DESKTOP_SESSION environment variable
            desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
            if desktop_session:
                for de in self._supported_desktop_environments:
                    if de in desktop_session:
                        return de
            
            # Check XDG_CURRENT_DESKTOP
            xdg_current = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if xdg_current:
                for de in self._supported_desktop_environments:
                    if de in xdg_current:
                        return de
            
            # Check for specific environment variables
            if os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return 'gnome'
            if os.environ.get('KDE_FULL_SESSION'):
                return 'kde'
                
        except Exception:
            pass
        
        return 'unknown'
    
    def get_linux_distribution_info(self) -> Dict[str, str]:
        """
        Get Linux distribution information.
        
        Returns:
            Dictionary with distribution info
        """
        try:
            import platform
            distro_info = {}
            
            # Get platform info
            distro_info['system'] = platform.system()
            distro_info['release'] = platform.release()
            distro_info['version'] = platform.version()
            
            # Try to get specific distribution info
            try:
                import distro
                distro_info['name'] = distro.name(pretty=True)
                distro_info['id'] = distro.id()
                distro_info['version'] = distro.version()
                distro_info['codename'] = distro.codename()
            except ImportError:
                # Fallback without distro package
                distro_info['name'] = 'Linux (requires distro package)'
                distro_info['id'] = 'linux'
                distro_info['version'] = platform.release()
                distro_info['codename'] = 'unknown'
            
            return distro_info
        except Exception:
            return {
                'system': 'Linux',
                'name': 'Unknown Distribution',
                'id': 'unknown',
                'version': 'unknown',
                'codename': 'unknown'
            }
    
    def integrate_with_desktop(self, app_name: str, icon_path: Optional[str] = None) -> bool:
        """
        Integrate the application with Linux desktop environment.
        
        Args:
            app_name: Name of the application
            icon_path: Optional path to application icon
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            # Create desktop entry file
            desktop_entries_dir = os.path.join(self._xdg_data_home, 'applications')
            os.makedirs(desktop_entries_dir, exist_ok=True)
            
            desktop_file_content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Comment=DAIP-LIVE Artificial Intelligence Platform
Exec=python -m daip_live.p7_gui_v1.main
Icon={icon_path or ''}
Terminal=false
Categories=Utility;
"""
            
            desktop_file_path = os.path.join(desktop_entries_dir, f"{app_name.lower().replace(' ', '_')}.desktop")
            with open(desktop_file_path, 'w') as f:
                f.write(desktop_file_content)
            
            # Make executable
            os.chmod(desktop_file_path, 0o755)
            
            return True
        except Exception:
            return False
    
    def get_system_tray_available(self) -> bool:
        """
        Check if system tray is available on the current Linux desktop.
        
        Returns:
            True if system tray is available, False otherwise
        """
        desktop_env = self.get_desktop_environment()
        
        # Most modern desktop environments support system tray
        # except for some minimal configurations
        if desktop_env in ['gnome']:
            # GNOME traditionally has limitations with system trays
            # But some extensions may enable them
            try:
                # Check if system tray extension is enabled
                result = subprocess.run([
                    'gsettings', 'get', 'org.gnome.shell', 'enabled-extensions'
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and 'systemtray' in result.stdout.lower():
                    return True
                return False
            except Exception:
                pass
        
        # For other desktop environments, assume system tray is available
        return desktop_env != 'unknown'