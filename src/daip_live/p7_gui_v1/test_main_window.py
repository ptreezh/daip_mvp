import pytest
import customtkinter as ctk
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.views.main_window import MainWindow


class TestMainWindow:
    """TDD for Main Window View"""
    
    def test_main_window_initialization(self):
        """RED: Test that MainWindow can be initialized"""
        # Create a mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'  # Default view
        
        # Initialize the main window (without actually displaying it)
        ctk.set_appearance_mode("light")  # Set appearance to avoid issues
        app = ctk.CTk()  # Create the root window
        app.withdraw()  # Hide it to avoid display issues during testing
        
        window = MainWindow(app, mock_vm)
        
        assert window is not None
        assert hasattr(window, '_viewmodel')
        assert hasattr(window, '_parent')
        assert hasattr(window, 'components')
    
    def test_main_window_has_required_components(self):
        """RED: Test that MainWindow has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'
        
        app = ctk.CTk()
        app.withdraw()
        
        window = MainWindow(app, mock_vm)
        window._setup_components()
        
        # Check that required components exist
        assert hasattr(window, '_sidebar_frame')
        assert hasattr(window, '_main_container')
        assert hasattr(window, '_content_area')
        assert hasattr(window, '_navigation_frame')
        
        # Check that components are properly initialized
        assert window._sidebar_frame is not None
        assert window._main_container is not None
        assert window._content_area is not None
        assert window._navigation_frame is not None
    
    def test_menu_buttons_creation(self):
        """RED: Test that menu buttons are properly created"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'
        
        app = ctk.CTk()
        app.withdraw()
        
        window = MainWindow(app, mock_vm)
        window._setup_components()
        
        # Check that menu buttons are created
        assert len(window._menu_buttons) > 0  # Should have at least a few menu buttons
        assert 'chat' in window._menu_buttons
        assert 'roles' in window._menu_buttons
        assert 'sessions' in window._menu_buttons
    
    def test_navigate_to_view(self):
        """RED: Test navigation to different views"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'
        mock_vm.execute_command.return_value = "Switched to chat"
        
        app = ctk.CTk()
        app.withdraw()
        
        window = MainWindow(app, mock_vm)
        window._setup_components()
        
        # Test that navigate method can switch views
        window.navigate_to_view('chat')
        
        # Verify that the ViewModel command was called
        mock_vm.execute_command.assert_called_with('switch_view', 'chat')
    
    def test_component_binding(self):
        """RED: Test that components are bound to ViewModel properties"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'
        mock_vm.subscribe_property_change = Mock()
        
        app = ctk.CTk()
        app.withdraw()
        
        window = MainWindow(app, mock_vm)
        window._setup_components()
        window._bind_to_viewmodel()
        
        # Verify that the viewmodel binding was set up
        assert mock_vm.subscribe_property_change.called
    
    def test_property_change_handling(self):
        """RED: Test handling of ViewModel property changes"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = 'chat'
        
        app = ctk.CTk()
        app.withdraw()
        
        window = MainWindow(app, mock_vm)
        window._setup_components()
        
        # Test the property change handler
        window._on_viewmodel_property_change('current_view', 'roles', 'chat')
        
        # The current view should be updated in the view
        assert window._current_view == 'roles'