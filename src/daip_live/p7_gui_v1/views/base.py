"""
Base View Class

This module provides the base View class for the MVVM architecture.
"""

import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import Any, Dict


class View(ABC):
    """
    Base class for all views in the MVVM architecture.
    
    This class provides common functionality and abstract methods
    that all views should implement.
    """
    
    def __init__(self, parent):
        """
        Initialize the base View.
        
        Args:
            parent: Parent widget/frame for this view
        """
        self._parent = parent
        self._viewmodel = None
        self._bindings = []
    
    @abstractmethod
    def show(self):
        """Show the view."""
        pass
    
    @abstractmethod
    def hide(self):
        """Hide the view."""
        pass
    
    def bind_to_viewmodel(self, viewmodel: Any):
        """
        Bind this view to a ViewModel.
        
        Args:
            viewmodel: ViewModel instance to bind to
        """
        self._viewmodel = viewmodel
    
    def get_viewmodel(self) -> Any:
        """
        Get the bound ViewModel.
        
        Returns:
            Bound ViewModel instance
        """
        return self._viewmodel
    
    def update_view(self, **kwargs):
        """
        Update the view with new data.
        
        Args:
            **kwargs: Arbitrary keyword arguments for updating the view
        """
        # Override in subclasses
        pass
    
    def set_parent(self, parent: ctk.CTkFrame):
        """
        Set the parent frame for this view.
        
        Args:
            parent: New parent frame
        """
        self._parent = parent
    
    def get_parent(self) -> ctk.CTkFrame:
        """
        Get the parent frame.
        
        Returns:
            Parent frame
        """
        return self._parent