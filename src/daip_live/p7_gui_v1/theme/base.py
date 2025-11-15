"""
Base Theme Class for DAIP-LIVE P7 GUI

This module provides the base theme class for the theme management system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTheme(ABC):
    """
    Abstract base class for all themes in the system.
    
    This provides the common interface and functionality for all specific theme implementations.
    """
    
    def __init__(self, name: str, colors: Dict[str, str]):
        """
        Initialize the base theme.
        
        Args:
            name: Unique name for the theme
            colors: Dictionary of color names to hex values
        """
        self.name = name
        self.colors = colors or {}
        self.is_loaded = False
    
    def get_color(self, color_name: str, default: str = "#ffffff") -> str:
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
    
    def get_all_colors(self) -> Dict[str, str]:
        """
        Get all colors in the theme.
        
        Returns:
            Dictionary of all color names to values
        """
        return self.colors.copy()
    
    @abstractmethod
    def apply_theme(self) -> bool:
        """
        Apply this theme to the interface.
        
        Returns:
            True if theme was applied successfully, False otherwise
        """
        pass
    
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
    
    def __str__(self) -> str:
        """String representation of the theme."""
        return f"{self.__class__.__name__}('{self.name}')"
    
    def __repr__(self) -> str:
        """Detailed string representation of the theme."""
        return f"{self.__class__.__name__}(name='{self.name}', color_count={len(self.colors)})"


# Alias for compatibility
Theme = BaseTheme