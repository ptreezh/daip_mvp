import pytest
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.viewmodel.databinding import DataBinder, ObservableProperty


class TestDataBinder:
    """TDD for Data Binding functionality"""
    
    def test_observable_property_initialization(self):
        """RED: Test that ObservableProperty can be initialized"""
        prop = ObservableProperty("test_value")
        assert prop.get() == "test_value"
    
    def test_observable_property_get_set(self):
        """RED: Test ObservableProperty get/set functionality"""
        prop = ObservableProperty("initial")
        
        # Get initial value
        assert prop.get() == "initial"
        
        # Set new value
        prop.set("new_value")
        assert prop.get() == "new_value"
    
    def test_observable_property_change_notification(self):
        """RED: Test ObservableProperty change notification"""
        prop = ObservableProperty("initial")
        notification = {"called": False, "old_value": None, "new_value": None}
        
        def callback(old_value, new_value):
            notification["called"] = True
            notification["old_value"] = old_value
            notification["new_value"] = new_value
        
        prop.add_listener(callback)
        prop.set("changed")
        
        assert notification["called"] is True
        assert notification["old_value"] == "initial"
        assert notification["new_value"] == "changed"
    
    def test_one_way_binding(self):
        """RED: Test one-way data binding functionality"""
        source_prop = ObservableProperty("initial_source")
        target_prop = ObservableProperty("initial_target")
        
        binder = DataBinder()
        binder.bind_one_way(source_prop, target_prop)
        
        # Change source - target should update
        source_prop.set("new_source_value")
        
        assert target_prop.get() == "new_source_value"
    
    def test_two_way_binding(self):
        """RED: Test two-way data binding functionality"""
        prop1 = ObservableProperty("value1")
        prop2 = ObservableProperty("value2")
        
        binder = DataBinder()
        binder.bind_two_way(prop1, prop2)
        
        # Change first property - second should update
        prop1.set("new_value1")
        assert prop2.get() == "new_value1"
        
        # Change second property - first should update
        prop2.set("new_value2")
        assert prop1.get() == "new_value2"
    
    def test_binding_with_converter(self):
        """RED: Test binding with value converter"""
        source_prop = ObservableProperty(10)  # number
        target_prop = ObservableProperty("0")  # string
        
        # Converter: number to string
        to_target_converter = lambda x: str(x)
        # Converter: string to number  
        to_source_converter = lambda x: int(x) if x.isdigit() else 0
        
        binder = DataBinder()
        binder.bind_two_way(source_prop, target_prop, 
                           to_target_converter=to_target_converter,
                           to_source_converter=to_source_converter)
        
        # Change source (number) -> target should get string
        source_prop.set(42)
        assert target_prop.get() == "42"
        
        # Change target (string) -> source should get number
        target_prop.set("100")
        assert source_prop.get() == 100