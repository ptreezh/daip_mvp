import pytest
import customtkinter as ctk
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.views.role_view import RoleView


class TestRoleView:
    """TDD for Role Management View"""
    
    def test_role_view_initialization(self):
        """RED: Test that RoleView can be initialized"""
        # Create a mock ViewModel
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        # Initialize the role view (without actually displaying it)
        app = ctk.CTk()
        app.withdraw()  # Hide it to avoid display issues during testing
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        
        assert role_view is not None
        assert hasattr(role_view, '_viewmodel')
        assert hasattr(role_view, '_parent')
        assert hasattr(role_view, '_role_listbox')
        assert hasattr(role_view, '_role_details_frame')
    
    def test_role_view_has_required_components(self):
        """RED: Test that RoleView has required UI components"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        
        # Check that required components exist
        assert hasattr(role_view, '_role_listbox')  # Listbox for roles
        assert hasattr(role_view, '_role_details_frame')  # Frame for role details
        assert hasattr(role_view, '_role_name_label')  # Label for role name
        assert hasattr(role_view, '_role_description_label')  # Label for role description
        assert hasattr(role_view, '_role_system_prompt_text')  # Text box for system prompt
        assert hasattr(role_view, '_select_button')  # Button to select role
        assert hasattr(role_view, '_search_entry')  # Entry for searching roles
        assert hasattr(role_view, '_refresh_button')  # Button to refresh roles
        
        # Check that components are properly initialized
        assert role_view._role_listbox is not None
        assert role_view._role_details_frame is not None
        assert role_view._select_button is not None
        assert role_view._search_entry is not None
        assert role_view._refresh_button is not None
    
    def test_role_listing_functionality(self):
        """RED: Test that roles can be listed"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'name': 'analyst', 'description': 'Data analyst role', 'system_prompt': 'You are a data analyst...'},
            {'name': 'developer', 'description': 'Software developer role', 'system_prompt': 'You are a software developer...'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        
        # Check that the method exists to populate roles
        assert hasattr(role_view, '_populate_roles_list')
        assert callable(role_view._populate_roles_list)
    
    def test_role_selection_functionality(self):
        """RED: Test role selection functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'name': 'analyst', 'description': 'Data analyst role', 'system_prompt': 'You are a data analyst...'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Selected role: analyst')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        
        # Check that role selection methods exist
        assert hasattr(role_view, 'select_role')
        assert callable(role_view.select_role)
    
    def test_role_search_functionality(self):
        """RED: Test role search functionality"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'name': 'senior_analyst', 'description': 'Senior data analyst role', 'system_prompt': 'You are a senior data analyst...'},
            {'name': 'junior_developer', 'description': 'Junior developer role', 'system_prompt': 'You are a junior developer...'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        
        # Check that search methods exist
        assert hasattr(role_view, '_search_roles')
        assert callable(role_view._search_roles)
    
    def test_viewmodel_binding(self):
        """RED: Test that view is bound to ViewModel"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = []
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        role_view._bind_to_viewmodel()
        
        # Verify that the viewmodel binding was set up
        assert mock_vm.subscribe_property_change.called
    
    def test_role_details_display(self):
        """RED: Test displaying role details"""
        mock_vm = Mock()
        mock_vm.get_property.return_value = [
            {'name': 'analyst', 'description': 'Data analyst role', 'system_prompt': 'You are a data analyst...'}
        ]
        mock_vm.subscribe_property_change = Mock()
        mock_vm.execute_command = Mock(return_value='Operation successful')
        
        app = ctk.CTk()
        app.withdraw()
        
        frame = ctk.CTkFrame(app)
        role_view = RoleView(frame, mock_vm)
        role_view._setup_components()
        
        # Check that the method exists to display role details
        assert hasattr(role_view, '_display_role_details')
        assert callable(role_view._display_role_details)