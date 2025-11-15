import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.role_viewmodel import RoleViewModel


class TestRoleViewModel:
    """TDD for Role Management ViewModel"""
    
    def test_role_viewmodel_initialization(self):
        """RED: Test that RoleViewModel can be initialized"""
        mock_interaction = Mock()
        vm = RoleViewModel(mock_interaction)
        assert vm is not None
        assert hasattr(vm, '_interaction_layer')
        assert hasattr(vm, '_roles')
        assert hasattr(vm, '_current_selection')
    
    def test_role_viewmodel_initial_properties(self):
        """RED: Test initial properties of RoleViewModel"""
        mock_interaction = Mock()
        vm = RoleViewModel(mock_interaction)
        
        # Check initial state
        assert vm.get_property('available_roles') == []
        assert vm.get_property('selected_role') is None
        assert vm.get_property('selected_role_details') is None
        assert vm.get_property('is_loading') is False
        assert vm.get_property('search_query') == ''
    
    @pytest.mark.asyncio
    async def test_load_roles_command(self):
        """RED: Test loading roles functionality"""
        mock_interaction = AsyncMock()
        mock_interaction.get_roles.return_value = [
            {"name": "analyst", "description": "Data analyst role", "system_prompt": "You are a data analyst..."},
            {"name": "developer", "description": "Software developer role", "system_prompt": "You are a software developer..."}
        ]
        
        vm = RoleViewModel(mock_interaction)
        await vm.load_roles()
        
        roles = vm.get_property('available_roles')
        assert len(roles) == 2
        assert roles[0]['name'] == 'analyst'
        assert roles[1]['name'] == 'developer'
        mock_interaction.get_roles.assert_called_once()
    
    def test_select_role_command(self):
        """RED: Test selecting a role functionality"""
        mock_interaction = Mock()
        vm = RoleViewModel(mock_interaction)
        
        # Pre-populate roles
        roles = [
            {"name": "analyst", "description": "Data analyst role", "system_prompt": "You are a data analyst..."},
            {"name": "developer", "description": "Software developer role", "system_prompt": "You are a software developer..."}
        ]
        vm.set_property('available_roles', roles)
        
        # Select a role
        result = vm.select_role('analyst')
        assert result == "Selected role: analyst"
        assert vm.get_property('selected_role') == 'analyst'
        
        # Check that the role details are updated
        selected_details = vm.get_property('selected_role_details')
        assert selected_details is not None
        assert selected_details['name'] == 'analyst'
    
    def test_property_management(self):
        """RED: Test property management functionality"""
        mock_interaction = Mock()
        vm = RoleViewModel(mock_interaction)
        
        # Test setting and getting properties
        vm.set_property('search_query', 'analyst')
        assert vm.get_property('search_query') == 'analyst'
        
        vm.set_property('is_loading', True)
        assert vm.get_property('is_loading') is True
    
    @pytest.mark.asyncio
    async def test_search_roles_functionality(self):
        """RED: Test role search functionality"""
        mock_interaction = Mock()
        vm = RoleViewModel(mock_interaction)
        
        # Mock some roles
        roles = [
            {"name": "senior_analyst", "description": "Senior data analyst role", "system_prompt": "You are a senior data analyst..."},
            {"name": "junior_developer", "description": "Junior software developer role", "system_prompt": "You are a junior developer..."},
            {"name": "product_manager", "description": "Product manager role", "system_prompt": "You manage products..."}
        ]
        vm.set_property('available_roles', roles)
        
        # Test search functionality (this would normally be integrated into the ViewModel)
        assert hasattr(vm, 'filter_roles_by_name')
        assert callable(vm.filter_roles_by_name)