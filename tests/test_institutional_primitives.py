"""Unit tests for institutional primitives base classes and registry.
"""

import asyncio
from datetime import datetime
from typing import Any

import pytest

from src.virtual_role_chat.institutional_primitives.base import (
    ExecutionContext,
    ExecutionResult,
    InstitutionalPrimitive,
    PrimitiveInfo,
)
from src.virtual_role_chat.institutional_primitives.registry import (
    PrimitiveRegistry,
    get_global_registry,
    register_primitive,
)


class TestPrimitive(InstitutionalPrimitive):
    """Test primitive for unit testing."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.executed = False
        self.execution_count = 0
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """Test execution that simply echoes inputs."""
        self.executed = True
        self.execution_count += 1
        
        # Simulate some processing time
        await asyncio.sleep(0.01)
        
        return ExecutionResult(
            success=True,
            outputs={
                "result": f"Processed: {inputs.get('data', 'no data')}",
                "execution_count": self.execution_count
            },
            execution_time=0.01
        )
    
    def get_input_schema(self) -> dict[str, Any]:
        """Return test input schema."""
        return {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Input data to process"}
            },
            "required": ["data"]
        }
    
    def get_output_schema(self) -> dict[str, Any]:
        """Return test output schema."""
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "Processed result"},
                "execution_count": {"type": "integer", "description": "Number of executions"}
            },
            "required": ["result", "execution_count"]
        }
    
    def get_name(self) -> str:
        return "Test Primitive"
    
    def get_description(self) -> str:
        return "A test primitive for unit testing"
    
    def get_tags(self) -> list:
        return ["test", "example"]
    
    def get_author(self) -> str:
        return "Test Author"


class InvalidPrimitive:
    """Invalid primitive that doesn't inherit from InstitutionalPrimitive."""
    pass


class TestInstitutionalPrimitive:
    """Test cases for InstitutionalPrimitive base class."""
    
    def test_primitive_creation(self):
        """Test creating a primitive instance."""
        primitive = TestPrimitive()
        assert primitive is not None
        assert not primitive.executed
        assert primitive.execution_count == 0
    
    def test_primitive_creation_with_config(self):
        """Test creating a primitive with configuration."""
        config = {"test_param": "test_value"}
        primitive = TestPrimitive(config)
        assert primitive.config == config
    
    @pytest.mark.asyncio()
    async def test_primitive_execution(self):
        """Test primitive execution."""
        primitive = TestPrimitive()
        context = ExecutionContext(
            workflow_id="test_workflow",
            node_id="test_node"
        )
        inputs = {"data": "test input"}
        
        result = await primitive.execute(inputs, context)
        
        assert result.success
        assert result.outputs["result"] == "Processed: test input"
        assert result.outputs["execution_count"] == 1
        assert primitive.executed
        assert primitive.execution_count == 1
    
    def test_get_primitive_info(self):
        """Test getting primitive information."""
        primitive = TestPrimitive()
        info = primitive.get_primitive_info()
        
        assert isinstance(info, PrimitiveInfo)
        assert info.type == "test"
        assert info.name == "Test Primitive"
        assert info.description == "A test primitive for unit testing"
        assert "test" in info.tags
        assert "example" in info.tags
        assert info.author == "Test Author"
    
    def test_input_validation_success(self):
        """Test successful input validation."""
        primitive = TestPrimitive()
        inputs = {"data": "test input"}
        
        result = primitive.validate_inputs(inputs)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_input_validation_missing_required(self):
        """Test input validation with missing required field."""
        primitive = TestPrimitive()
        inputs = {}  # Missing required 'data' field
        
        result = primitive.validate_inputs(inputs)
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Required field 'data' is missing" in result.errors[0]
    
    def test_input_validation_unexpected_field(self):
        """Test input validation with unexpected field."""
        primitive = TestPrimitive()
        inputs = {"data": "test input", "unexpected": "value"}
        
        result = primitive.validate_inputs(inputs)
        
        assert result.is_valid  # Still valid, just a warning
        assert len(result.warnings) == 1
        assert "Unexpected field 'unexpected'" in result.warnings[0]
    
    def test_output_validation_success(self):
        """Test successful output validation."""
        primitive = TestPrimitive()
        outputs = {"result": "test result", "execution_count": 1}
        
        result = primitive.validate_outputs(outputs)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_output_validation_missing_required(self):
        """Test output validation with missing required field."""
        primitive = TestPrimitive()
        outputs = {"result": "test result"}  # Missing execution_count
        
        result = primitive.validate_outputs(outputs)
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Required output field 'execution_count' is missing" in result.errors[0]


class TestPrimitiveRegistry:
    """Test cases for PrimitiveRegistry."""
    
    def setup_method(self):
        """Set up test registry."""
        self.registry = PrimitiveRegistry()
    
    def test_register_primitive_success(self):
        """Test successful primitive registration."""
        result = self.registry.register_primitive("test", TestPrimitive)
        
        assert result is True
        assert self.registry.is_registered("test")
        assert self.registry.get_primitive("test") == TestPrimitive
    
    def test_register_invalid_primitive(self):
        """Test registering invalid primitive."""
        result = self.registry.register_primitive("invalid", InvalidPrimitive)
        
        assert result is False
        assert not self.registry.is_registered("invalid")
    
    def test_register_duplicate_primitive(self):
        """Test registering duplicate primitive type."""
        # Register first time
        result1 = self.registry.register_primitive("test", TestPrimitive)
        assert result1 is True
        
        # Register again with same type
        result2 = self.registry.register_primitive("test", TestPrimitive)
        assert result2 is True  # Should succeed but log warning
    
    def test_get_nonexistent_primitive(self):
        """Test getting non-existent primitive."""
        primitive_class = self.registry.get_primitive("nonexistent")
        assert primitive_class is None
    
    def test_create_primitive_success(self):
        """Test successful primitive creation."""
        self.registry.register_primitive("test", TestPrimitive)
        
        primitive = self.registry.create_primitive("test")
        
        assert primitive is not None
        assert isinstance(primitive, TestPrimitive)
    
    def test_create_primitive_with_config(self):
        """Test primitive creation with configuration."""
        self.registry.register_primitive("test", TestPrimitive)
        config = {"test_param": "test_value"}
        
        primitive = self.registry.create_primitive("test", config)
        
        assert primitive is not None
        assert primitive.config == config
    
    def test_create_nonexistent_primitive(self):
        """Test creating non-existent primitive."""
        primitive = self.registry.create_primitive("nonexistent")
        assert primitive is None
    
    def test_list_primitives(self):
        """Test listing registered primitives."""
        self.registry.register_primitive("test", TestPrimitive)
        
        primitives = self.registry.list_primitives()
        
        assert len(primitives) == 1
        assert primitives[0].type == "test"
        assert primitives[0].name == "Test Primitive"
    
    def test_get_primitive_info(self):
        """Test getting primitive information."""
        self.registry.register_primitive("test", TestPrimitive)
        
        info = self.registry.get_primitive_info("test")
        
        assert info is not None
        assert info.type == "test"
        assert info.name == "Test Primitive"
    
    def test_validate_primitive_definition_success(self):
        """Test successful primitive definition validation."""
        self.registry.register_primitive("test", TestPrimitive)
        
        primitive_def = {
            "type": "test",
            "config": {"test_param": "test_value"}
        }
        
        result = self.registry.validate_primitive(primitive_def)
        
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_primitive_definition_missing_type(self):
        """Test primitive definition validation with missing type."""
        primitive_def = {
            "config": {"test_param": "test_value"}
        }
        
        result = self.registry.validate_primitive(primitive_def)
        
        assert not result.is_valid
        assert any("Required field 'type' is missing" in error for error in result.errors)
    
    def test_validate_primitive_definition_unknown_type(self):
        """Test primitive definition validation with unknown type."""
        primitive_def = {
            "type": "unknown",
            "config": {}
        }
        
        result = self.registry.validate_primitive(primitive_def)
        
        assert not result.is_valid
        assert any("not registered" in error for error in result.errors)
    
    def test_unregister_primitive(self):
        """Test unregistering a primitive."""
        self.registry.register_primitive("test", TestPrimitive)
        assert self.registry.is_registered("test")
        
        result = self.registry.unregister_primitive("test")
        
        assert result is True
        assert not self.registry.is_registered("test")
    
    def test_unregister_nonexistent_primitive(self):
        """Test unregistering non-existent primitive."""
        result = self.registry.unregister_primitive("nonexistent")
        assert result is False
    
    def test_get_primitives_by_tag(self):
        """Test getting primitives by tag."""
        self.registry.register_primitive("test", TestPrimitive)
        
        primitives = self.registry.get_primitives_by_tag("test")
        
        assert len(primitives) == 1
        assert primitives[0].type == "test"
        
        # Test with non-existent tag
        primitives = self.registry.get_primitives_by_tag("nonexistent")
        assert len(primitives) == 0
    
    def test_clear_registry(self):
        """Test clearing the registry."""
        self.registry.register_primitive("test", TestPrimitive)
        assert len(self.registry.list_primitives()) == 1
        
        self.registry.clear()
        
        assert len(self.registry.list_primitives()) == 0
        assert not self.registry.is_registered("test")


class TestGlobalRegistry:
    """Test cases for global registry functions."""
    
    def test_get_global_registry(self):
        """Test getting global registry instance."""
        registry = get_global_registry()
        assert isinstance(registry, PrimitiveRegistry)
        
        # Should return same instance
        registry2 = get_global_registry()
        assert registry is registry2
    
    def test_register_primitive_global(self):
        """Test registering primitive with global function."""
        # Clear global registry first
        get_global_registry().clear()
        
        result = register_primitive("test", TestPrimitive)
        
        assert result is True
        assert get_global_registry().is_registered("test")


class TestExecutionContext:
    """Test cases for ExecutionContext."""
    
    def test_execution_context_creation(self):
        """Test creating execution context."""
        context = ExecutionContext(
            workflow_id="test_workflow",
            node_id="test_node"
        )
        
        assert context.workflow_id == "test_workflow"
        assert context.node_id == "test_node"
        assert context.execution_id is not None
        assert isinstance(context.timestamp, datetime)
        assert isinstance(context.services, dict)
        assert isinstance(context.state, dict)
        assert isinstance(context.metadata, dict)
    
    def test_execution_context_with_services(self):
        """Test creating execution context with services."""
        services = {"test_service": "test_value"}
        context = ExecutionContext(
            workflow_id="test_workflow",
            node_id="test_node",
            services=services
        )
        
        assert context.services == services