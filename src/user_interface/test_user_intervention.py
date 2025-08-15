"""@Time    : 2025-07-24 19:30:00
@Author  : DAIP-LIVE Team
@File    : test_user_intervention.py
@Description:
    Tests for user intervention and customization functionality.
"""
import asyncio
import tempfile
from pathlib import Path

import pytest
from rich.console import Console

from .configuration_manager import ConfigurationManager
from .interactive_controller import InteractiveController
from .parameter_manager import ParameterDefinition, ParameterManager, ParameterType
from .workflow_steering import SteeringAction, WorkflowSteering


class TestParameterManager:
    """Test cases for ParameterManager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.console = Console(file=open('/dev/null', 'w'))  # Suppress output
        self.parameter_manager = ParameterManager(console=self.console)
    
    def test_parameter_definition_creation(self):
        """Test parameter definition creation."""
        param_def = ParameterDefinition(
            name="test_param",
            param_type=ParameterType.STRING,
            description="Test parameter",
            default="default_value"
        )
        
        assert param_def.name == "test_param"
        assert param_def.param_type == ParameterType.STRING
        assert param_def.description == "Test parameter"
        assert param_def.default == "default_value"
    
    def test_parameter_validation(self):
        """Test parameter validation."""
        param_def = ParameterDefinition(
            name="numeric_param",
            param_type=ParameterType.INTEGER,
            description="Numeric parameter",
            min_value=1,
            max_value=10,
            default=5
        )
        
        # Valid value
        assert self.parameter_manager._validate_single_parameter(5, param_def) == True
        
        # Invalid values
        assert self.parameter_manager._validate_single_parameter(0, param_def) == False
        assert self.parameter_manager._validate_single_parameter(11, param_def) == False
    
    def test_choice_parameter_validation(self):
        """Test choice parameter validation."""
        param_def = ParameterDefinition(
            name="choice_param",
            param_type=ParameterType.CHOICE,
            description="Choice parameter",
            choices=["option1", "option2", "option3"],
            default="option1"
        )
        
        # Valid choice
        assert self.parameter_manager._validate_single_parameter("option2", param_def) == True
        
        # Invalid choice
        assert self.parameter_manager._validate_single_parameter("invalid", param_def) == False
    
    def test_parameter_preset_creation(self):
        """Test parameter preset creation and loading."""
        parameters = {
            "param1": "value1",
            "param2": 42,
            "param3": True
        }
        
        # Create preset
        result = self.parameter_manager.create_parameter_preset(
            preset_name="test_preset",
            parameters=parameters,
            description="Test preset"
        )
        
        assert result == True
        
        # Load preset
        loaded_params = self.parameter_manager.load_parameter_preset("test_preset")
        assert loaded_params == parameters
    
    def test_parameter_history(self):
        """Test parameter history tracking."""
        # Initially empty
        assert len(self.parameter_manager.parameter_history) == 0
        
        # Add some parameters
        self.parameter_manager.parameter_history["param1"] = "value1"
        self.parameter_manager.parameter_history["param2"] = 42
        
        assert len(self.parameter_manager.parameter_history) == 2
        assert self.parameter_manager.parameter_history["param1"] == "value1"


class TestWorkflowSteering:
    """Test cases for WorkflowSteering."""
    
    def setup_method(self):
        """Setup test environment."""
        self.console = Console(file=open('/dev/null', 'w'))  # Suppress output
        self.workflow_steering = WorkflowSteering(console=self.console)
    
    def test_steering_point_registration(self):
        """Test steering point registration."""
        self.workflow_steering.register_steering_point(
            point_id="test_point",
            name="Test Point",
            description="Test steering point",
            workflow_step="step1",
            available_actions=[SteeringAction.CONTINUE, SteeringAction.PAUSE]
        )
        
        assert "test_point" in self.workflow_steering.steering_points
        
        point = self.workflow_steering.steering_points["test_point"]
        assert point.name == "Test Point"
        assert point.description == "Test steering point"
        assert point.workflow_step == "step1"
        assert SteeringAction.CONTINUE in point.available_actions
        assert SteeringAction.PAUSE in point.available_actions
    
    def test_command_callback_registration(self):
        """Test command callback registration."""
        callback_called = False
        
        def test_callback(command):
            nonlocal callback_called
            callback_called = True
        
        self.workflow_steering.register_command_callback(
            action=SteeringAction.CONTINUE,
            callback=test_callback
        )
        
        assert SteeringAction.CONTINUE in self.workflow_steering.command_callbacks
        assert len(self.workflow_steering.command_callbacks[SteeringAction.CONTINUE]) == 1
    
    def test_checkpoint_management(self):
        """Test checkpoint save and load functionality."""
        # Save checkpoint
        checkpoint_data = {
            "workflow_state": {"step": "test_step", "progress": 0.5},
            "timestamp": 1234567890
        }
        
        self.workflow_steering.workflow_state = checkpoint_data["workflow_state"]
        
        # Simulate checkpoint creation
        checkpoint_name = "test_checkpoint"
        self.workflow_steering.checkpoints[checkpoint_name] = {
            "name": checkpoint_name,
            "description": "Test checkpoint",
            "workflow_state": checkpoint_data["workflow_state"],
            "timestamp": checkpoint_data["timestamp"]
        }
        
        # Verify checkpoint exists
        assert checkpoint_name in self.workflow_steering.checkpoints
        
        # Get available checkpoints
        checkpoints = self.workflow_steering.get_available_checkpoints()
        assert checkpoint_name in checkpoints
        
        # Delete checkpoint
        result = self.workflow_steering.delete_checkpoint(checkpoint_name)
        assert result == True
        assert checkpoint_name not in self.workflow_steering.checkpoints
    
    def test_steering_history(self):
        """Test steering command history."""
        from .workflow_steering import SteeringCommand
        
        # Initially empty
        assert len(self.workflow_steering.get_steering_history()) == 0
        
        # Add command to history
        command = SteeringCommand(
            action=SteeringAction.CONTINUE,
            parameters={"test": "value"},
            message="Test command"
        )
        
        self.workflow_steering.steering_history.append(command)
        
        # Check history
        history = self.workflow_steering.get_steering_history()
        assert len(history) == 1
        assert history[0].action == SteeringAction.CONTINUE
        
        # Clear history
        self.workflow_steering.clear_steering_history()
        assert len(self.workflow_steering.get_steering_history()) == 0


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.console = Console(file=open('/dev/null', 'w'))  # Suppress output
        self.config_manager = ConfigurationManager(
            config_dir=self.temp_dir,
            console=self.console
        )
    
    def test_configuration_creation(self):
        """Test configuration creation."""
        config = {
            "section1": {
                "param1": "value1",
                "param2": 42
            },
            "section2": {
                "param3": True,
                "param4": [1, 2, 3]
            }
        }
        
        # Save configuration
        result = self.config_manager._save_configuration("test_config", config)
        assert result == True
        
        # Load configuration
        loaded_config = self.config_manager.load_configuration("test_config")
        assert loaded_config == config
    
    def test_nested_value_operations(self):
        """Test nested value get/set operations."""
        config = {}
        
        # Set nested value
        self.config_manager._set_nested_value(config, "section.subsection.param", "value")
        
        expected = {
            "section": {
                "subsection": {
                    "param": "value"
                }
            }
        }
        
        assert config == expected
        
        # Get nested value
        value = self.config_manager._get_nested_value(config, "section.subsection.param")
        assert value == "value"
        
        # Get non-existent value with default
        value = self.config_manager._get_nested_value(config, "nonexistent.path", "default")
        assert value == "default"
    
    def test_configuration_list(self):
        """Test configuration listing."""
        # Create test configurations
        configs = {
            "workflow1_config1": {"test": "data1"},
            "workflow1_config2": {"test": "data2"},
            "workflow2_config1": {"test": "data3"}
        }
        
        for name, config in configs.items():
            self.config_manager.configurations[name] = config
        
        # List all configurations
        all_configs = self.config_manager.list_configurations()
        assert len(all_configs) >= 3
        
        # List workflow-specific configurations
        workflow1_configs = self.config_manager.list_configurations("workflow1")
        assert len(workflow1_configs) == 2
        assert "workflow1_config1" in workflow1_configs
        assert "workflow1_config2" in workflow1_configs
    
    def test_configuration_export_import(self):
        """Test configuration export and import."""
        config = {
            "test_section": {
                "param1": "value1",
                "param2": 42
            }
        }
        
        # Add to configurations
        self.config_manager.configurations["test_config"] = config
        
        # Export configuration
        export_path = Path(self.temp_dir) / "exported_config.json"
        result = self.config_manager.export_configuration("test_config", str(export_path))
        assert result == True
        assert export_path.exists()
        
        # Import configuration
        result = self.config_manager.import_configuration(str(export_path), "imported_config")
        assert result == True
        assert "imported_config" in self.config_manager.configurations
        assert self.config_manager.configurations["imported_config"] == config
    
    def test_configuration_deletion(self):
        """Test configuration deletion."""
        config = {"test": "data"}
        
        # Create configuration
        self.config_manager.configurations["delete_test"] = config
        self.config_manager._save_configuration("delete_test", config)
        
        # Verify it exists
        assert "delete_test" in self.config_manager.configurations
        config_file = Path(self.config_manager.config_dir) / "delete_test.json"
        assert config_file.exists()
        
        # Delete configuration
        result = self.config_manager.delete_configuration("delete_test")
        assert result == True
        assert "delete_test" not in self.config_manager.configurations
        assert not config_file.exists()


class TestInteractiveController:
    """Test cases for InteractiveController."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.console = Console(file=open('/dev/null', 'w'))  # Suppress output
        self.controller = InteractiveController(
            console=self.console,
            config_dir=self.temp_dir
        )
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        assert self.controller.parameter_manager is not None
        assert self.controller.workflow_steering is not None
        assert self.controller.configuration_manager is not None
    
    def test_steering_point_setup(self):
        """Test steering point setup."""
        steering_points = [
            {
                "id": "point1",
                "name": "Test Point 1",
                "description": "First test point",
                "workflow_step": "step1",
                "actions": ["continue", "pause"]
            },
            {
                "id": "point2",
                "name": "Test Point 2",
                "description": "Second test point",
                "workflow_step": "step2",
                "actions": ["continue", "modify_parameters"]
            }
        ]
        
        # This would normally be async, but we're testing the setup
        asyncio.run(self.controller.setup_workflow_steering("test_workflow", steering_points))
        
        # Verify steering points were registered
        assert "point1" in self.controller.workflow_steering.steering_points
        assert "point2" in self.controller.workflow_steering.steering_points
    
    def test_configuration_management(self):
        """Test configuration management through controller."""
        config = {
            "section1": {"param1": "value1"},
            "section2": {"param2": 42}
        }
        
        # Save configuration
        result = self.controller.save_workflow_configuration("test_config", config)
        assert result == True
        
        # Load configuration
        loaded_config = self.controller.load_workflow_configuration("test_config")
        assert loaded_config == config
        
        # List configurations
        configs = self.controller.list_workflow_configurations()
        assert "test_config" in configs
    
    def test_parameter_preset_management(self):
        """Test parameter preset management through controller."""
        parameters = {
            "param1": "value1",
            "param2": 42,
            "param3": True
        }
        
        # Create preset
        result = self.controller.create_parameter_preset(
            preset_name="test_preset",
            parameters=parameters,
            description="Test preset"
        )
        assert result == True
        
        # Load preset
        loaded_params = self.controller.load_parameter_preset("test_preset")
        assert loaded_params == parameters
    
    def test_steering_history_tracking(self):
        """Test steering history tracking through controller."""
        # Initially empty
        history = self.controller.get_steering_history()
        assert len(history) == 0
        
        # Add some history (simulate steering commands)
        from .workflow_steering import SteeringCommand
        
        command = SteeringCommand(
            action=SteeringAction.CONTINUE,
            parameters={"test": "value"},
            message="Test command"
        )
        
        self.controller.workflow_steering.steering_history.append(command)
        
        # Check history through controller
        history = self.controller.get_steering_history()
        assert len(history) == 1
        assert history[0]["action"] == "continue"
        assert history[0]["parameters"] == {"test": "value"}


@pytest.mark.asyncio()
async def test_integration_workflow():
    """Test integration of all components in a workflow scenario."""
    temp_dir = tempfile.mkdtemp()
    console = Console(file=open('/dev/null', 'w'))
    controller = InteractiveController(console=console, config_dir=temp_dir)
    
    # 1. Setup workflow configuration
    config = {
        "generation": {"role_name": "创作者"},
        "fact_extraction": {"min_confidence": 0.7},
        "consensus": {"credibility_threshold": 0.8}
    }
    
    controller.save_workflow_configuration("critical_review_test", config)
    
    # 2. Setup steering points
    steering_points = [
        {
            "id": "generation_complete",
            "name": "Generation Complete",
            "description": "Content generation completed",
            "workflow_step": "generation",
            "actions": ["continue", "modify_parameters"]
        }
    ]
    
    await controller.setup_workflow_steering("critical_review", steering_points)
    
    # 3. Create parameter definitions
    param_defs = [
        ParameterDefinition(
            name="confidence_threshold",
            param_type=ParameterType.FLOAT,
            description="Confidence threshold for facts",
            default=0.7,
            min_value=0.0,
            max_value=1.0
        )
    ]
    
    # 4. Verify everything is set up correctly
    loaded_config = controller.load_workflow_configuration("critical_review_test")
    assert loaded_config == config
    
    assert "generation_complete" in controller.workflow_steering.steering_points
    
    # 5. Test parameter validation
    param_manager = controller.parameter_manager
    assert param_manager._validate_single_parameter(0.8, param_defs[0]) == True
    assert param_manager._validate_single_parameter(1.5, param_defs[0]) == False


if __name__ == "__main__":
    pytest.main([__file__])