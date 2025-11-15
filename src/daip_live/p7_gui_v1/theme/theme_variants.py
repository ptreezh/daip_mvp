"""
Dark Theme Implementation for DAIP-LIVE P7 GUI

This module implements the dark theme following the newP7 specification.
"""

from typing import Dict, Any
from .base import BaseTheme


class DarkTheme(BaseTheme):
    """Dark theme implementation with professional dark color scheme."""
    
    def __init__(self):
        """Initialize the dark theme with appropriate colors."""
        dark_colors = {
            # Window and background colors
            'window_bg': '#1e1e1e',        # Dark gray background
            'window_fg': '#e0e0e0',        # Light gray text
            'titlebar_bg': '#252526',     # Slightly lighter dark gray for title bar
            'titlebar_fg': '#ffffff',     # White title bar text
            
            # Component colors
            'button_bg': '#333333',       # Dark button background
            'button_fg': '#ffffff',       # White button text
            'button_hover': '#3d3d3d',    # Slightly lighter on hover
            'button_active': '#4a4a4a',   # Even lighter when active
            
            'entry_bg': '#2d2d2d',        # Dark input background
            'entry_fg': '#dcdcdc',        # Light input text
            'entry_border': '#454545',    # Medium dark border
            
            'label_fg': '#dcdcdc',        # Light label text
            'label_bg': '#1e1e1e',        # Dark label background
            
            # Interactive element colors
            'selection_bg': '#264f78',    # Dark blue selection
            'selection_fg': '#ffffff',    # White selection text
            'active_bg': '#0066cc',       # Darker blue active state
            'active_fg': '#ffffff',       # White active text
            
            # Border and separator colors
            'border': '#404040',          # Dark gray border
            'separator': '#3a3a3a',       # Darker separator
            'outline': '#606060',         # Medium gray outline
            
            # Status indicator colors
            'success': '#4ade80',         # Light green for success
            'warning': '#fde047',         # Light yellow for warning
            'error': '#f87171',           # Light red for error
            'info': '#60a5fa',            # Light blue for info
            
            # Special component colors
            'scrollbar_bg': '#252526',    # Match titlebar background
            'scrollbar_thumb': '#5a5a5a', # Medium gray scrollbar
            'scrollbar_hover': '#6a6a6a', # Lighter gray on hover
            
            # CustomTkinter specific colors
            'ct_primary': '#1e3a8a',      # Darker blue primary
            'ct_secondary': '#3b82f6',    # Normal blue secondary
            'ct_accent': '#a855f7'        # Purple accent
        }
        
        super().__init__("dark", dark_colors)

    def apply_theme(self) -> bool:
        """
        Apply the dark theme to the interface.
        
        Returns:
            True if theme was applied successfully, False otherwise
        """
        # In a real implementation, this would apply the colors to the GUI framework
        # For this implementation, we just mark it as loaded
        self.is_loaded = True
        return True


class LightTheme(BaseTheme):
    """Light theme implementation with clean, bright color scheme."""
    
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
            
            # CustomTkinter specific colors
            'ct_primary': '#1f6aa5',       # Blue primary
            'ct_secondary': '#5fb9f7',     # Light blue secondary
            'ct_accent': '#bf62f6'         # Purple accent
        }
        
        super().__init__("light", light_colors)

    def apply_theme(self) -> bool:
        """
        Apply the light theme to the interface.
        
        Returns:
            True if theme was applied successfully, False otherwise
        """
        # In a real implementation, this would apply the colors to the GUI framework
        # For this implementation, we just mark it as loaded
        self.is_loaded = True
        return True


class CustomTheme(BaseTheme):
    """Custom theme implementation allowing user-defined color schemes."""
    
    def __init__(self, name: str, colors: Dict[str, Any]):
        """
        Initialize the custom theme with user-defined colors.
        
        Args:
            name: Name for the custom theme
            colors: Dictionary of color names to hex values
        """
        # Validate colors are in hex format
        validated_colors = {}
        for color_name, color_value in colors.items():
            # Simple validation - ensure it's a hex color
            if isinstance(color_value, str) and color_value.startswith('#'):
                validated_colors[color_name] = color_value
            else:
                # Use default color if invalid
                validated_colors[color_name] = "#ffffff"
        
        super().__init__(name, validated_colors)

    def apply_theme(self) -> bool:
        """
        Apply the custom theme to the interface.
        
        Returns:
            True if theme was applied successfully, False otherwise
        """
        # In a real implementation, this would apply the colors to the GUI framework
        # For this implementation, we just mark it as loaded
        self.is_loaded = True
        return True