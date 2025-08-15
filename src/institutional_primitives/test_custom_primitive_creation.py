"""@Time    : 2025-07-25 06:00:00
@Author  : DAIP-LIVE Team
@File    : test_custom_primitive_creation.py
@Description:
    Unit tests for custom primitive creation functionality.
    Tests requirements 7.1, 7.2, 7.3 for task 11.1.
"""
import tempfile
from pathlib import Path

import pytest

from .base import ExecutionContext
from .examples.custom_primitives import (
    DataTransformationPrimitive,
    ExampleCustomPrimitivesPlugin,
    MockExternalServiceAdapter,
    SentimentAnalysisPrimitive,
)
from .plugin_interface import CustomPrimitiveBase, PluginManager, PluginMetadata
from .registry import PrimitiveRegistry
from .service_adapters import (
    AdapterCapability,
    ServiceAdapterManager,
    ServiceType,
)
from .workflow_templates import (
    ParameterType,
    TemplateEngine,
    TemplateLibrary,
    TemplateParameter,
    TemplateParameterValues,
    WorkflowEdge,
    WorkflowNode,
    WorkflowTemplate,
)


class TestPluginInterface:
    """Test plugin interface system (Requirement 7.1)."""
    
    @pytest.fixture()
    def registry(self):
        """Create a primitive registry for testing."""
        return PrimitiveRegistry()
    
    @pytest.fixture()
    def plugin_manager(self, registry):
        """Create a plugin manager for testing."""
        return PluginManager(registry)
    
    def test_custom_primitive_base(self):
        """Test CustomPrimitiveBase functionality."""
        primitive = SentimentAnalysisPrimitive("test_sentiment", {"threshold": 0.5})
        
        # Test basic functionality
        assert primitive.primitive_id == "test_sentiment"
        assert primitive.config["threshold"] == 0.5
        assert primitive.get_primitive_type() == "sentiment_analysis"
        
        # Test plugin metadata
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            author="test",
            description="Test plugin"
        )
        primitive.set_plugin_metadata(metadata)
        assert primitive.plugin_metadata == metadata
        
        # Test service adapters
        mock_adapter = MockExternalServiceAdapter("test_adapter", None)
        primitive.register_service_adapter("test_service", mock_adapter)
        assert primitive.get_service_adapter("test_service") == mock_adapter
        
        # Test plugin info
        plugin_info = primitive.get_plugin_info()
        assert plugin_info["primitive_type"] == "sentiment_analysis"
        assert plugin_info["plugin_metadata"] is not None
        assert "test_service" in plugin_info["service_adapters"]
    
    def test_plugin_interface(self):
        """Test PluginInterface implementation."""
        plugin = ExampleCustomPrimitivesPlugin()
        
        # Test metadata
        metadata = plugin.get_metadata()
        assert metadata.name == "example_custom_primitives"
        assert metadata.version == "1.0.0"
        assert "sentiment_analysis" in metadata.primitive_types
        assert "data_transformation" in metadata.primitive_types
        
        # Test primitive classes
        primitive_classes = plugin.get_primitive_classes()
        assert "sentiment_analysis" in primitive_classes
        assert "data_transformation" in primitive_classes
        assert issubclass(primitive_classes["sentiment_analysis"], CustomPrimitiveBase)
        
        # Test service adapters
        service_adapters = plugin.get_service_adapters()
        assert "mock_external_service" in service_adapters
        
        # Test initialization
        context = {"test": "context"}
        assert plugin.initialize(context) is True
    
    def test_plugin_loader(self, plugin_manager):
        """Test plugin loading functionality."""
        loader = plugin_manager.loader
        
        # Test plugin registration
        plugin = ExampleCustomPrimitivesPlugin()
        metadata = plugin.get_metadata()
        
        # Manually register plugin for testing
        loader._register_plugin(metadata.name, plugin, metadata)
        
        # Verify plugin is loaded
        assert metadata.name in loader.loaded_plugins
        assert metadata.name in loader.plugin_metadata
        
        # Test primitive registration
        primitive_classes = plugin.get_primitive_classes()
        for primitive_type in primitive_classes:
            assert plugin_manager.registry.get_primitive(primitive_type) is not None
        
        # Test service adapter registration
        service_adapters = plugin.get_service_adapters()
        for service_name in service_adapters:
            assert loader.get_service_adapter(service_name) is not None
    
    def test_plugin_manager(self, plugin_manager):
        """Test plugin manager functionality."""
        # Test primitive creation
        plugin = ExampleCustomPrimitivesPlugin()
        metadata = plugin.get_metadata()
        plugin_manager.loader._register_plugin(metadata.name, plugin, metadata)
        
        # Create primitive instance
        primitive_instance = plugin_manager.create_primitive_instance(
            "sentiment_analysis",
            "test_sentiment_001",
            {"threshold": 0.7}
        )
        
        assert primitive_instance is not None
        assert primitive_instance.primitive_id == "test_sentiment_001"
        assert primitive_instance.config["threshold"] == 0.7
        
        # Test system status
        status = plugin_manager.get_system_status()
        assert status["loaded_plugins"] >= 1
        assert status["registered_primitives"] >= 2
        assert "example_custom_primitives" in [p["name"] for p in status["plugins"]]
    
    @pytest.mark.asyncio()
    async def test_custom_primitive_execution(self):
        """Test execution of custom primitives."""
        # Test sentiment analysis primitive
        sentiment_primitive = SentimentAnalysisPrimitive("test_sentiment", {})
        
        context = ExecutionContext(
            execution_id="test_exec",
            workflow_id="test_workflow",
            node_id="test_node"
        )
        
        # Test positive sentiment
        inputs = {"text": "This is a great and wonderful product!"}
        result = await sentiment_primitive.execute(inputs, context)
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5
        assert "details" in result
        
        # Test negative sentiment
        inputs = {"text": "This is terrible and awful!"}
        result = await sentiment_primitive.execute(inputs, context)
        
        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.5
        
        # Test data transformation primitive
        transform_primitive = DataTransformationPrimitive("test_transform", {})
        
        # Test filtering
        inputs = {
            "data": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}],
            "transformation": "filter",
            "parameters": {"criteria": {"key": "age", "value": 25}}
        }
        result = await transform_primitive.execute(inputs, context)
        
        assert len(result["transformed_data"]) == 1
        assert result["transformed_data"][0]["name"] == "Alice"
        assert result["metadata"]["original_count"] == 2


class TestWorkflowTemplates:
    """Test template-based workflow definition (Requirement 7.2)."""
    
    @pytest.fixture()
    def template_engine(self):
        """Create a template engine for testing."""
        return TemplateEngine()
    
    @pytest.fixture()
    def sample_template(self):
        """Create a sample workflow template."""
        return WorkflowTemplate(
            name="sentiment_analysis_workflow",
            version="1.0.0",
            description="Workflow for analyzing sentiment of text content",
            author="test_author",
            parameters=[
                TemplateParameter(
                    name="confidence_threshold",
                    type=ParameterType.FLOAT,
                    description="Minimum confidence threshold",
                    default=0.7,
                    constraints={"min": 0.0, "max": 1.0}
                ),
                TemplateParameter(
                    name="language",
                    type=ParameterType.STRING,
                    description="Language of the text",
                    default="en",
                    constraints={"choices": ["en", "es", "fr", "de"]}
                )
            ],
            nodes=[
                WorkflowNode(
                    id="sentiment_node",
                    type="sentiment_analysis",
                    config={"threshold": "${confidence_threshold}"},
                    inputs=["text_input"],
                    outputs=["sentiment_result"]
                ),
                WorkflowNode(
                    id="filter_node",
                    type="data_transformation",
                    config={"language": "${language}"},
                    inputs=["sentiment_result"],
                    outputs=["filtered_result"]
                )
            ],
            edges=[
                WorkflowEdge(
                    from_node="sentiment_node",
                    to_node="filter_node",
                    data_mapping={"sentiment_result": "sentiment_result"}
                )
            ],
            tags=["sentiment", "analysis", "nlp"],
            category="text_processing"
        )
    
    def test_template_creation(self, sample_template):
        """Test workflow template creation."""
        assert sample_template.name == "sentiment_analysis_workflow"
        assert sample_template.version == "1.0.0"
        assert len(sample_template.parameters) == 2
        assert len(sample_template.nodes) == 2
        assert len(sample_template.edges) == 1
        
        # Test parameter access
        threshold_param = sample_template.get_parameter("confidence_threshold")
        assert threshold_param is not None
        assert threshold_param.type == ParameterType.FLOAT
        assert threshold_param.default == 0.7
        
        # Test node access
        sentiment_node = sample_template.get_node("sentiment_node")
        assert sentiment_node is not None
        assert sentiment_node.type == "sentiment_analysis"
    
    def test_template_validation(self, sample_template):
        """Test template structure validation."""
        errors = sample_template.validate_structure()
        assert len(errors) == 0  # Should be valid
        
        # Test invalid template
        invalid_template = WorkflowTemplate(
            name="invalid_template",
            version="1.0.0",
            description="Invalid template for testing",
            author="test",
            nodes=[
                WorkflowNode(id="node1", type="test", config={})
            ],
            edges=[
                WorkflowEdge(from_node="node1", to_node="nonexistent_node")
            ]
        )
        
        errors = invalid_template.validate_structure()
        assert len(errors) > 0
        assert any("unknown" in error.lower() for error in errors)
    
    def test_template_engine_registration(self, template_engine, sample_template):
        """Test template registration in engine."""
        success = template_engine.register_template(sample_template)
        assert success is True
        
        # Test template retrieval
        retrieved_template = template_engine.get_template("sentiment_analysis_workflow", "1.0.0")
        assert retrieved_template is not None
        assert retrieved_template.name == sample_template.name
        
        # Test latest version retrieval
        latest_template = template_engine.get_template("sentiment_analysis_workflow")
        assert latest_template is not None
        assert latest_template.version == "1.0.0"
    
    def test_parameter_validation(self, template_engine, sample_template):
        """Test parameter validation."""
        template_engine.register_template(sample_template)
        
        # Test valid parameters
        valid_params = TemplateParameterValues()
        valid_params.set("confidence_threshold", 0.8)
        valid_params.set("language", "en")
        
        errors = template_engine.validate_parameters(sample_template, valid_params)
        assert len(errors) == 0
        
        # Test invalid parameters
        invalid_params = TemplateParameterValues()
        invalid_params.set("confidence_threshold", 1.5)  # Above max
        invalid_params.set("language", "invalid")  # Not in choices
        invalid_params.set("unknown_param", "value")  # Unknown parameter
        
        errors = template_engine.validate_parameters(sample_template, invalid_params)
        assert len(errors) >= 3
    
    def test_template_instantiation(self, template_engine, sample_template):
        """Test workflow instantiation from template."""
        template_engine.register_template(sample_template)
        
        # Create parameter values
        params = TemplateParameterValues()
        params.set("confidence_threshold", 0.8)
        params.set("language", "es")
        
        # Instantiate template
        instance = template_engine.instantiate_template(
            "sentiment_analysis_workflow",
            params,
            "test_instance_001"
        )
        
        assert instance is not None
        assert instance.instance_id == "test_instance_001"
        assert instance.template_name == "sentiment_analysis_workflow"
        assert instance.parameter_values.get("confidence_threshold") == 0.8
        assert instance.parameter_values.get("language") == "es"
        
        # Check parameter substitution in nodes
        sentiment_node = next(node for node in instance.nodes if node.id == "sentiment_node")
        assert sentiment_node.config["threshold"] == 0.8
        
        filter_node = next(node for node in instance.nodes if node.id == "filter_node")
        assert filter_node.config["language"] == "es"
    
    def test_template_file_operations(self, template_engine, sample_template):
        """Test template file save/load operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test YAML save/load
            yaml_path = Path(temp_dir) / "test_template.yaml"
            success = template_engine.save_template_to_file(sample_template, str(yaml_path), "yaml")
            assert success is True
            assert yaml_path.exists()
            
            loaded_template = template_engine.load_template_from_file(str(yaml_path))
            assert loaded_template is not None
            assert loaded_template.name == sample_template.name
            
            # Test JSON save/load
            json_path = Path(temp_dir) / "test_template.json"
            success = template_engine.save_template_to_file(sample_template, str(json_path), "json")
            assert success is True
            assert json_path.exists()
            
            loaded_template = template_engine.load_template_from_file(str(json_path))
            assert loaded_template is not None
            assert loaded_template.name == sample_template.name
    
    def test_template_library(self, template_engine, sample_template):
        """Test template library functionality."""
        library = TemplateLibrary(template_engine)
        template_engine.register_template(sample_template)
        
        # Test search functionality
        results = library.search_templates(query="sentiment")
        assert len(results) >= 1
        assert any(t.name == "sentiment_analysis_workflow" for t in results)
        
        results = library.search_templates(category="text_processing")
        assert len(results) >= 1
        
        results = library.search_templates(tags=["nlp"])
        assert len(results) >= 1
        
        # Test category and tag extraction
        categories = library.get_template_categories()
        assert "text_processing" in categories
        
        tags = library.get_template_tags()
        assert "sentiment" in tags
        assert "analysis" in tags


class TestServiceAdapters:
    """Test service adapter registration (Requirement 7.3)."""
    
    @pytest.fixture()
    def adapter_manager(self):
        """Create a service adapter manager for testing."""
        manager = ServiceAdapterManager()
        manager.register_standard_adapters()
        return manager
    
    @pytest.mark.asyncio()
    async def test_service_adapter_creation(self, adapter_manager):
        """Test service adapter creation and initialization."""
        # Register custom adapter
        success = adapter_manager.register_custom_adapter("mock_service", MockExternalServiceAdapter)
        assert success is True
        
        # Create adapter instance
        config = {
            "endpoint": "https://api.example.com",
            "api_key": "test_key"
        }
        
        adapter = await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "test_mock_001",
            config
        )
        
        assert adapter is not None
        assert adapter.instance_id == "test_mock_001"
        assert adapter.is_initialized is True
        
        # Test adapter metadata
        metadata = adapter.get_metadata()
        assert metadata.name == "mock_external_service"
        assert metadata.service_type == ServiceType.CUSTOM
        assert AdapterCapability.READ in metadata.capabilities
    
    @pytest.mark.asyncio()
    async def test_service_adapter_execution(self, adapter_manager):
        """Test service adapter request execution."""
        # Register and create adapter
        adapter_manager.register_custom_adapter("mock_service", MockExternalServiceAdapter)
        
        config = {"endpoint": "https://api.example.com"}
        adapter = await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "test_mock_002",
            config
        )
        
        # Execute service request
        response = await adapter_manager.execute_service_request(
            "test_mock_002",
            "query_data",
            {"query": "Item 1"}
        )
        
        assert response.success is True
        assert response.data is not None
        assert len(response.data) >= 1
        assert response.data[0]["name"] == "Item 1"
        assert response.duration_ms is not None
    
    @pytest.mark.asyncio()
    async def test_adapter_discovery(self, adapter_manager):
        """Test adapter discovery by type and capability."""
        # Register and create multiple adapters
        adapter_manager.register_custom_adapter("mock_service", MockExternalServiceAdapter)
        
        await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "mock_001",
            {"endpoint": "https://api1.example.com"}
        )
        
        await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "mock_002",
            {"endpoint": "https://api2.example.com"}
        )
        
        # Find adapters by type
        custom_adapters = adapter_manager.find_adapters(service_type=ServiceType.CUSTOM)
        assert len(custom_adapters) >= 2
        
        # Find adapters by capability
        read_adapters = adapter_manager.find_adapters(capability=AdapterCapability.READ)
        assert len(read_adapters) >= 2
    
    @pytest.mark.asyncio()
    async def test_health_check(self, adapter_manager):
        """Test adapter health checking."""
        # Register and create adapter
        adapter_manager.register_custom_adapter("mock_service", MockExternalServiceAdapter)
        
        await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "health_test_001",
            {"endpoint": "https://api.example.com"}
        )
        
        # Perform health check
        health_results = await adapter_manager.health_check_all()
        
        assert "total_adapters" in health_results
        assert "healthy_adapters" in health_results
        assert "adapter_status" in health_results
        assert health_results["adapter_status"]["health_test_001"] is True
    
    def test_system_status(self, adapter_manager):
        """Test system status reporting."""
        status = adapter_manager.get_system_status()
        
        assert "registered_classes" in status
        assert "active_instances" in status
        assert "auto_initialize" in status
        assert "adapter_classes" in status
        assert "adapter_instances" in status
        
        # Should have standard adapters registered
        assert status["registered_classes"] >= 3
        assert "fact_source" in status["adapter_classes"]
        assert "validation_service" in status["adapter_classes"]
        assert "synthesis_engine" in status["adapter_classes"]


class TestIntegration:
    """Test integration between all components."""
    
    @pytest.fixture()
    def integrated_system(self):
        """Create an integrated system with all components."""
        registry = PrimitiveRegistry()
        plugin_manager = PluginManager(registry)
        template_engine = TemplateEngine()
        adapter_manager = ServiceAdapterManager()
        adapter_manager.register_standard_adapters()
        
        return {
            "registry": registry,
            "plugin_manager": plugin_manager,
            "template_engine": template_engine,
            "adapter_manager": adapter_manager
        }
    
    @pytest.mark.asyncio()
    async def test_end_to_end_workflow(self, integrated_system):
        """Test end-to-end workflow with custom primitives, templates, and adapters."""
        plugin_manager = integrated_system["plugin_manager"]
        template_engine = integrated_system["template_engine"]
        adapter_manager = integrated_system["adapter_manager"]
        
        # 1. Load custom primitives via plugin
        plugin = ExampleCustomPrimitivesPlugin()
        metadata = plugin.get_metadata()
        plugin_manager.loader._register_plugin(metadata.name, plugin, metadata)
        
        # 2. Create service adapter
        adapter_manager.register_custom_adapter("mock_service", MockExternalServiceAdapter)
        adapter = await adapter_manager.create_and_initialize_adapter(
            "mock_service",
            "integration_test",
            {"endpoint": "https://api.example.com"}
        )
        
        # 3. Create workflow template using custom primitives
        template = WorkflowTemplate(
            name="integration_test_workflow",
            version="1.0.0",
            description="Integration test workflow",
            author="test",
            parameters=[
                TemplateParameter(
                    name="text_input",
                    type=ParameterType.STRING,
                    description="Text to analyze",
                    default="This is a great product!"
                )
            ],
            nodes=[
                WorkflowNode(
                    id="sentiment_analysis",
                    type="sentiment_analysis",
                    config={},
                    inputs=["text_input"],
                    outputs=["sentiment_result"]
                )
            ],
            edges=[]
        )
        
        template_engine.register_template(template)
        
        # 4. Instantiate and execute workflow
        params = TemplateParameterValues()
        params.set("text_input", "This is an amazing and wonderful experience!")
        
        instance = template_engine.instantiate_template(
            "integration_test_workflow",
            params,
            "integration_instance"
        )
        
        assert instance is not None
        
        # 5. Execute primitive from instantiated workflow
        primitive_instance = plugin_manager.create_primitive_instance(
            "sentiment_analysis",
            "integration_primitive",
            {}
        )
        
        context = ExecutionContext(
            execution_id="integration_exec",
            workflow_id="integration_workflow",
            node_id="sentiment_analysis"
        )
        
        result = await primitive_instance.execute(
            {"text": params.get("text_input")},
            context
        )
        
        assert result["sentiment"] == "positive"
        assert result["confidence"] > 0.5
        
        # 6. Test service adapter integration
        service_response = await adapter_manager.execute_service_request(
            "integration_test",
            "query_data",
            {"query": "Item"}
        )
        
        assert service_response.success is True
        assert len(service_response.data) >= 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])