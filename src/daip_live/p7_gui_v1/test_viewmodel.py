import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.viewmodel.base import ViewModel


class TestViewModel:
    """TDD for ViewModel base functionality"""
    
    def test_viewmodel_initialization(self):
        """RED: Test that ViewModel can be initialized"""
        vm = ViewModel()
        assert vm is not None
        assert hasattr(vm, '_properties')
        assert hasattr(vm, '_commands')
        assert hasattr(vm, '_property_listeners')
    
    def test_viewmodel_property_set_get(self):
        """RED: Test property setting and getting functionality"""
        vm = ViewModel()
        
        # Set a property
        vm.set_property("test_prop", "test_value")
        
        # Get the property
        value = vm.get_property("test_prop")
        
        assert value == "test_value"
    
    def test_viewmodel_property_default_value(self):
        """RED: Test property with default value"""
        vm = ViewModel()
        
        # Get non-existent property with default
        value = vm.get_property("non_existent", "default_value")
        
        assert value == "default_value"
    
    def test_viewmodel_command_registration(self):
        """RED: Test command registration functionality"""
        vm = ViewModel()
        mock_command = Mock(return_value="executed")
        
        # Register command
        vm.register_command("test_cmd", mock_command)
        
        # Execute command
        result = vm.execute_command("test_cmd")
        
        assert result == "executed"
        mock_command.assert_called_once()
    
    def test_viewmodel_command_with_parameters(self):
        """RED: Test command execution with parameters"""
        vm = ViewModel()
        mock_command = Mock(return_value="result")
        
        vm.register_command("param_cmd", mock_command)
        result = vm.execute_command("param_cmd", "param1", "param2")
        
        mock_command.assert_called_once_with("param1", "param2")
        assert result == "result"
    
    def test_viewmodel_property_notification(self):
        """RED: Test property change notification"""
        vm = ViewModel()
        notification_event = {"received": False, "name": None, "new_value": None, "old_value": None}
        
        def on_property_change(name, new_value, old_value):
            notification_event["received"] = True
            notification_event["name"] = name
            notification_event["new_value"] = new_value
            notification_event["old_value"] = old_value
        
        vm.subscribe_to_property_change("test_prop", on_property_change)
        vm.set_property("test_prop", "new_value")
        
        assert notification_event["received"] is True
        assert notification_event["name"] == "test_prop"
        assert notification_event["new_value"] == "new_value"
        assert notification_event["old_value"] is None  # Initial value was None