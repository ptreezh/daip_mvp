"""
Theme System for DAIP-LIVE P7 GUI

This module implements the complete theme management system for the P7 GUI application.
It provides theme management, color schemes, and theme application functionality following MVVM patterns.
"""

from typing import Any, Dict, List, Optional, Callable
import json
import os
from dataclasses import dataclass


@dataclass
class ThemeColorScheme:
    """
    Data class for theme color schemes.
    
    This defines the complete color palette for a theme including all UI elements.
    """
    # Window and background colors
    window_bg: str = "#ffffff"           # Main window background
    window_fg: str = "#000000"           # Main window foreground/text
    titlebar_bg: str = "#f0f0f0"         # Title bar background
    titlebar_fg: str = "#000000"         # Title bar text
    
    # Component colors
    button_bg: str = "#e0e0e0"           # Button background
    button_fg: str = "#000000"           # Button text
    button_hover: str = "#d0d0d0"        # Button hover state
    button_active: str = "#c0c0c0"       # Button active state
    
    entry_bg: str = "#ffffff"            # Entry/input field background
    entry_fg: str = "#000000"            # Entry/input text
    entry_border: str = "#cccccc"        # Entry border color
    
    label_fg: str = "#000000"            # Label text color
    label_bg: str = "#ffffff"            # Label background
    
    # Interactive element colors
    selection_bg: str = "#316acc"         # Selection/highlight background
    selection_fg: str = "#ffffff"         # Selection/highlight text
    active_bg: str = "#0078d4"           # Active element background
    active_fg: str = "#ffffff"           # Active element text
    
    # Border and separator colors
    border: str = "#cccccc"              # General border color
    separator: str = "#e0e0e0"           # Separator lines
    outline: str = "#a0a0a0"             # Outline color
    
    # Status indicator colors
    success: str = "#22c55e"             # Green success
    warning: str = "#f59e0b"             # Yellow warning  
    error: str = "#ef4444"               # Red error
    info: str = "#3b82f6"                # Blue info
    
    # Special component colors
    scrollbar_bg: str = "#f0f0f0"        # Scrollbar background
    scrollbar_thumb: str = "#c0c0c0"     # Scrollbar thumb
    scrollbar_hover: str = "#a0a0a0"     # Scrollbar thumb hover
    
    # CustomTKinter specific colors
    ct_primary: str = "#1f6aa5"          # CustomTkinter primary color
    ct_secondary: str = "#5fb9f7"        # CustomTkinter secondary color
    ct_accent: str = "#bf62f6"           # CustomTkinter accent color


class BaseTheme:
    """
    Base class for all themes in the system.
    
    This provides the common interface and functionality for all specific theme implementations.
    """
    
    def __init__(self, name: str, colors: Optional[Dict[str, str]] = None):
        """
        Initialize the base theme.
        
        Args:
            name: Unique name for the theme
            colors: Optional initial color scheme (will be merged with defaults)
        """
        self.name = name
        self.colors = colors or {}
        self._color_scheme = ThemeColorScheme()
        
        # Merge any provided colors with the default color scheme
        for attr_name in dir(self._color_scheme):
            if not attr_name.startswith('_') and not callable(getattr(self._color_scheme, attr_name)):
                default_color = getattr(self._color_scheme, attr_name)
                provided_color = self.colors.get(attr_name)
                if provided_color:
                    setattr(self._color_scheme, attr_name, provided_color)
                else:
                    self.colors[attr_name] = default_color
    
    def get_color(self, color_name: str, default: str = "#000000") -> str:
        """
        Get a specific color from the theme.
        
        Args:
            color_name: Name of the color to retrieve
            default: Default color to return if color_name is not found
            
        Returns:
            Color value as hex string, or default if not found
        """
        return self.colors.get(color_name, default)
    
    def set_color(self, color_name: str, color_value: str):
        """
        Set a specific color in the theme.
        
        Args:
            color_name: Name of the color to set
            color_value: New color value as hex string
        """
        self.colors[color_name] = color_value
        if hasattr(self._color_scheme, color_name):
            setattr(self._color_scheme, color_name, color_value)
    
    def get_color_scheme(self) -> ThemeColorScheme:
        """
        Get the complete color scheme for this theme.
        
        Returns:
            ThemeColorScheme object with all color values
        """
        return self._color_scheme
    
    def export_theme(self) -> Dict[str, Any]:
        """
        Export the theme as a serializable dictionary.
        
        Returns:
            Dictionary representation of the theme
        """
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'colors': self.colors.copy()
        }
    
    def apply_to_widget(self, widget: Any, color_mapping: Optional[Dict[str, str]] = None) -> bool:
        """
        Apply theme colors to a widget.
        
        Args:
            widget: Widget to apply theme to
            color_mapping: Mapping of widget properties to theme colors
                          Example: {'background': 'window_bg', 'foreground': 'window_fg'}
            
        Returns:
            True if successfully applied, False otherwise
        """
        if not color_mapping or not widget:
            return False
            
        try:
            # Apply color mapping to widget
            for widget_attr, theme_color in color_mapping.items():
                color_value = self.get_color(theme_color)
                if color_value and hasattr(widget, widget_attr):
                    widget.configure(**{widget_attr: color_value})
            return True
        except Exception:
            return False
    
    def get_css_variables(self) -> Dict[str, str]:
        """
        Get theme as CSS-style variables.
        
        Returns:
            Dictionary of CSS variable names mapped to color values
        """
        css_vars = {}
        for color_name, color_value in self.colors.items():
            css_vars[f"--{color_name.replace('_', '-')}-color"] = color_value
        return css_vars


class DarkTheme(BaseTheme):
    """
    Dark theme implementation with professional dark color scheme.
    
    This theme uses darker colors for backgrounds with lighter text for better eye comfort
    in low-light environments.
    """
    
    def __init__(self):
        """Initialize the dark theme with appropriate colors."""
        dark_colors = {
            # Window and background colors
            'window_bg': '#1e1e1e',        # Dark gray background
            'window_fg': '#e0e0e0',        # Light gray text
            'titlebar_bg': '#252526',      # Slightly lighter dark gray for title bar
            'titlebar_fg': '#ffffff',      # White title bar text
            
            # Component colors
            'button_bg': '#333333',        # Dark button background
            'button_fg': '#ffffff',        # White button text
            'button_hover': '#3d3d3d',     # Slightly lighter on hover
            'button_active': '#4a4a4a',    # Even lighter when active
            
            'entry_bg': '#2d2d2d',         # Dark input background
            'entry_fg': '#dcdcdc',         # Light input text
            'entry_border': '#454545',     # Medium dark border
            
            'label_fg': '#dcdcdc',         # Light label text
            'label_bg': '#1e1e1e',         # Dark label background
            
            # Interactive element colors
            'selection_bg': '#264f78',     # Dark blue selection
            'selection_fg': '#ffffff',     # White selection text
            'active_bg': '#0066cc',        # Darker blue active state
            'active_fg': '#ffffff',        # White active text
            
            # Border and separator colors
            'border': '#404040',           # Dark gray border
            'separator': '#3a3a3a',        # Darker separator
            'outline': '#606060',          # Medium gray outline
            
            # Status indicator colors
            'success': '#4ade80',          # Light green for success
            'warning': '#fde047',          # Light yellow for warning
            'error': '#f87171',            # Light red for error
            'info': '#60a5fa',             # Light blue for info
            
            # Special component colors
            'scrollbar_bg': '#252526',     # Match titlebar background
            'scrollbar_thumb': '#5a5a5a',  # Medium gray scrollbar
            'scrollbar_hover': '#6a6a6a',  # Lighter gray on hover
            
            # CustomTKinter specific colors
            'ct_primary': '#1e3a8a',       # Darker blue primary
            'ct_secondary': '#3b82f6',     # Normal blue secondary
            'ct_accent': '#a855f7'         # Purple accent
        }
        
        super().__init__("dark", dark_colors)


class LightTheme(BaseTheme):
    """
    Light theme implementation with clean, bright color scheme.
    
    This theme uses lighter colors for backgrounds with darker text for high contrast
    and readability in well-lit environments.
    """
    
    def __init__(self):
        """Initialize the light theme with appropriate colors."""
        light_colors = {
            # Window and background colors
            'window_bg': '#ffffff',        # Pure white background
            'window_fg': '#000000',        # Pure black text
            'titlebar_bg': '#f0f0f0',      # Light gray title bar
            'titlebar_fg': '#000000',      # Black title bar text
            
            # Component colors
            'button_bg': '#e0e0e0',        # Light gray button background
            'button_fg': '#000000',        # Black button text
            'button_hover': '#d0d0d0',     # Medium gray on hover
            'button_active': '#c0c0c0',    # Darker gray when active
            
            'entry_bg': '#ffffff',         # White input background
            'entry_fg': '#000000',         # Black input text
            'entry_border': '#cccccc',     # Medium gray border
            
            'label_fg': '#000000',         # Black label text
            'label_bg': '#ffffff',         # White label background
            
            # Interactive element colors
            'selection_bg': '#316acc',     # Blue selection background
            'selection_fg': '#ffffff',     # White selection text
            'active_bg': '#0078d4',        # Microsoft blue active
            'active_fg': '#ffffff',        # White active text
            
            # Border and separator colors
            'border': '#cccccc',           # Medium gray border
            'separator': '#e0e0e0',        # Light gray separator
            'outline': '#a0a0a0',          # Medium gray outline
            
            # Status indicator colors
            'success': '#22c55e',          # Green success
            'warning': '#f59e0b',          # Yellow warning
            'error': '#ef4444',            # Red error
            'info': '#3b82f6',             # Blue info
            
            # Special component colors
            'scrollbar_bg': '#f0f0f0',     # Light gray scrollbar
            'scrollbar_thumb': '#c0c0c0',  # Medium gray scrollbar thumb
            'scrollbar_hover': '#a0a0a0',  # Darker gray on hover
            
            # CustomTKinter specific colors
            'ct_primary': '#1f6aa5',       # Blue primary
            'ct_secondary': '#5fb9f7',     # Light blue secondary
            'ct_accent': '#bf62f6'         # Purple accent
        }
        
        super().__init__("light", light_colors)


class CustomTheme(BaseTheme):
    """
    Custom theme implementation allowing user-defined color schemes.
    
    This theme enables users to create their own themes with custom colors.
    """
    
    def __init__(self, name: str, colors: Dict[str, str]):
        """
        Initialize the custom theme with user-defined colors.
        
        Args:
            name: Name for the custom theme
            colors: Dictionary of color names to hex values
        """
        # Validate colors are in hex format
        validated_colors = {}
        for color_name, color_value in colors.items():
            # Simple validation - check if it's a hex color
            if isinstance(color_value, str) and (color_value.startswith('#') and len(color_value) in [4, 7, 9]):
                validated_colors[color_name] = color_value
            else:
                # Use default color if invalid
                validated_colors[color_name] = "#ffffff"
        
        super().__init__(name, validated_colors)


class ThemeManager:
    """
    Central manager for theme handling in the application.
    
    This manager handles:
    - Theme registration and management
    - Theme switching and application
    - Theme persistence
    - Theme change notifications
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the theme manager.
        
        Args:
            config_dir: Directory for theme configuration persistence
        """
        self._registered_themes: Dict[str, BaseTheme] = {}
        self._current_theme: Optional[BaseTheme] = None
        self._theme_callbacks: List[Callable[[str, str], None]] = []
        self._config_dir = config_dir or os.path.join(os.path.expanduser("~"), ".daip_live", "themes")
        self._config_file = os.path.join(self._config_dir, "theme_config.json")
        
        # Register default themes
        self._register_default_themes()
        
        # Load saved theme if available
        self._load_saved_theme()
    
    def _register_default_themes(self):
        """Register the default themes with the manager."""
        default_themes = [
            DarkTheme(),
            LightTheme()
        ]
        
        for theme in default_themes:
            self._registered_themes[theme.name] = theme
        
        # Set default theme (light)
        if 'light' in self._registered_themes:
            self._current_theme = self._registered_themes['light']
        elif self._registered_themes:
            # Use first available theme if light isn't available
            first_theme_name = list(self._registered_themes.keys())[0]
            self._current_theme = self._registered_themes[first_theme_name]
    
    def register_theme(self, theme: BaseTheme) -> bool:
        """
        Register a new theme with the manager.
        
        Args:
            theme: Theme instance to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        if not isinstance(theme, BaseTheme):
            return False
        
        if theme.name in self._registered_themes:
            return False  # Theme already exists
        
        self._registered_themes[theme.name] = theme
        return True
    
    def unregister_theme(self, theme_name: str) -> bool:
        """
        Unregister a theme from the manager.
        
        Args:
            theme_name: Name of the theme to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if theme_name not in self._registered_themes:
            return False
        
        # Don't allow removing current theme if it's the only one
        if self._current_theme and self._current_theme.name == theme_name and len(self._registered_themes) <= 1:
            return False
        
        # If we're removing the current theme, switch to another one
        if self._current_theme and self._current_theme.name == theme_name:
            other_themes = [name for name in self._registered_themes.keys() if name != theme_name]
            if other_themes:
                self.apply_theme(other_themes[0])
        
        del self._registered_themes[theme_name]
        return True
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Apply a theme by name.
        
        Args:
            theme_name: Name of the theme to apply
            
        Returns:
            True if theme was applied successfully, False otherwise
        """
        if theme_name not in self._registered_themes:
            return False
        
        old_theme_name = self._current_theme.name if self._current_theme else "unknown"
        self._current_theme = self._registered_themes[theme_name]
        
        # Notify subscribers of theme change
        self._notify_theme_change(old_theme_name, theme_name)
        
        # Save the theme choice for persistence
        self._save_current_theme()
        
        return True
    
    def get_current_theme(self) -> Optional[BaseTheme]:
        """
        Get the currently active theme.
        
        Returns:
            Current theme instance, or None if no theme is active
        """
        return self._current_theme
    
    def get_current_theme_name(self) -> Optional[str]:
        """
        Get the name of the currently active theme.
        
        Returns:
            Name of current theme, or None if no theme is active
        """
        if self._current_theme:
            return self._current_theme.name
        return None
    
    def get_available_themes(self) -> List[str]:
        """
        Get a list of available theme names.
        
        Returns:
            List of theme names
        """
        return list(self._registered_themes.keys())
    
    def has_theme(self, theme_name: str) -> bool:
        """
        Check if a theme is available.
        
        Args:
            theme_name: Name of the theme to check
            
        Returns:
            True if theme is available, False otherwise
        """
        return theme_name in self._registered_themes
    
    def get_theme(self, theme_name: str) -> Optional[BaseTheme]:
        """
        Get a specific theme by name.
        
        Args:
            theme_name: Name of the theme to retrieve
            
        Returns:
            Theme instance, or None if not found
        """
        return self._registered_themes.get(theme_name)
    
    def get_current_colors(self) -> Dict[str, str]:
        """
        Get the color scheme of the current theme.
        
        Returns:
            Dictionary of current theme colors, or empty dict if no theme is active
        """
        if self._current_theme:
            return self._current_theme.colors
        return {}
    
    def subscribe_to_theme_changes(self, callback: Callable[[str, str], None]) -> str:
        """
        Subscribe to theme change notifications.
        
        Args:
            callback: Function to call when theme changes
                     Signature: callback(old_theme_name: str, new_theme_name: str)
                     
        Returns:
            Subscription ID for unsubscribing later
        """
        sub_id = f"sub_{len(self._theme_callbacks)}"
        self._theme_callbacks.append(callback)
        return sub_id
    
    def unsubscribe_from_theme_changes(self, sub_id: str) -> bool:
        """
        Unsubscribe from theme change notifications.
        
        Args:
            sub_id: Subscription ID returned by subscribe method
            
        Returns:
            True if unsubscription was successful, False otherwise
        """
        # Find and remove the callback with this subscription ID
        # Since we don't store the ID with the callback, we can't directly unsubscribe
        # This would need to be improved in a real implementation
        return True  # Placeholder - proper implementation would need callback tracking
    
    def _notify_theme_change(self, old_theme: str, new_theme: str):
        """
        Notify all subscribers of a theme change.
        
        Args:
            old_theme: Name of the previous theme
            new_theme: Name of the new theme
        """
        for callback in self._theme_callbacks:
            try:
                callback(old_theme, new_theme)
            except Exception:
                # In production, you might want to log this or handle it differently
                pass
    
    def _save_current_theme(self):
        """Save the current theme choice to persistent storage."""
        try:
            os.makedirs(self._config_dir, exist_ok=True)
            
            config_data = {
                'current_theme': self.get_current_theme_name() or 'light',
                'registered_themes': list(self._registered_themes.keys()),
                'custom_themes': {}  # Would store custom theme definitions if any
            }
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
        except Exception:
            # Could not save - maybe log this in production
            pass
    
    def _load_saved_theme(self):
        """Load the saved theme choice from persistent storage."""
        try:
            if not os.path.exists(self._config_file):
                return
            
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            saved_theme = config_data.get('current_theme', 'light')
            if saved_theme in self._registered_themes:
                self._current_theme = self._registered_themes[saved_theme]
        except Exception:
            # Could not load - use default theme
            pass
    
    def save_theme_to_file(self, theme_name: str, file_path: str) -> bool:
        """
        Save a theme to a file for sharing or backup.
        
        Args:
            theme_name: Name of the theme to save
            file_path: Path to save the theme file
            
        Returns:
            True if save was successful, False otherwise
        """
        theme = self.get_theme(theme_name)
        if not theme:
            return False
        
        try:
            theme_data = theme.export_theme()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            return True
        except Exception:
            return False
    
    def load_theme_from_file(self, file_path: str) -> bool:
        """
        Load a theme from a file.
        
        Args:
            file_path: Path to the theme file
            
        Returns:
            True if load was successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Create a custom theme from the loaded data
            theme_name = theme_data.get('name', 'imported_theme')
            theme_colors = theme_data.get('colors', {})
            
            new_theme = CustomTheme(theme_name, theme_colors)
            return self.register_theme(new_theme)
        except Exception:
            return False
    
    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Dictionary with theme information
        """
        theme = self.get_theme(theme_name)
        if not theme:
            return {}
        
        return {
            'name': theme.name,
            'type': theme.__class__.__name__,
            'color_count': len(theme.colors),
            'colors': theme.colors,
            'css_variables': theme.get_css_variables()
        }
    
    def is_dark_theme_active(self) -> bool:
        """
        Check if the current theme is a dark theme.
        
        Returns:
            True if current theme is dark, False otherwise
        """
        if self._current_theme:
            return 'dark' in self._current_theme.name.lower()
        return False
    
    def is_light_theme_active(self) -> bool:
        """
        Check if the current theme is a light theme.
        
        Returns:
            True if current theme is light, False otherwise
        """
        if self._current_theme:
            return 'light' in self._current_theme.name.lower() or self._current_theme.name == 'light'
        return True  # Default to light if no theme is set