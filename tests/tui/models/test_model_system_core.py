"""
Core Model System Tests

Essential tests for the production model system functionality.
"""

import tempfile
from pathlib import Path

import pytest

# Import production model system components
from daip_live.tui_v1.models.production_model_system import (
    ModelCapabilities,
    ModelInfo,
    ModelMetrics,
    ModelProvider,
    ModelStatus,
    ModelType,
    ProductionModelSystem,
    TaskComplexity,
    create_production_model_system,
)


class TestModelCapabilities:
    """Test model capabilities specification"""

    def test_model_capabilities_creation(self):
        """Test model capabilities initialization"""
        capabilities = ModelCapabilities(
            max_tokens=4096,
            context_length=8192,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_audio=False,
            multilingual=True,
            reasoning_depth=7,
            creativity_score=8,
            accuracy_score=9,
            speed_score=6,
        )

        assert capabilities.max_tokens == 4096
        assert capabilities.context_length == 8192
        assert capabilities.supports_streaming
        assert capabilities.reasoning_depth == 7
        assert capabilities.creativity_score == 8


class TestModelMetrics:
    """Test model performance metrics"""

    def test_model_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = ModelMetrics()

        assert metrics.total_requests == 0
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 0.0
        assert metrics.total_cost == 0.0
        # Performance score defaults to 0.0 for new metrics
        assert metrics.performance_score == 0.0

    def test_model_metrics_update_success(self):
        """Test updating metrics with successful request"""
        metrics = ModelMetrics()

        metrics.update_request(success=True, response_time=1.5, tokens=100, cost=0.01)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 1.5
        assert metrics.total_cost == 0.01
        assert metrics.performance_score > 90

    def test_model_metrics_update_failure(self):
        """Test updating metrics with failed request"""
        metrics = ModelMetrics()

        metrics.update_request(success=False, response_time=5.0, cost=0.00)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.error_rate == 1.0
        assert metrics.performance_score <= 50


class TestModelInfo:
    """Test model information structure"""

    def test_model_info_creation(self):
        """Test model info creation"""
        capabilities = ModelCapabilities(
            max_tokens=4096,
            context_length=8192,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_audio=False,
            multilingual=True,
            reasoning_depth=7,
            creativity_score=8,
            accuracy_score=9,
            speed_score=6,
        )

        model_info = ModelInfo(
            name="test-model",
            display_name="Test Model",
            provider=ModelProvider.OPENAI,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.00001,
            cost_per_output_token=0.00002,
            description="Test model for unit testing",
            tags=["test", "demo"],
            priority=7,
        )

        assert model_info.name == "test-model"
        assert model_info.display_name == "Test Model"
        assert model_info.provider == ModelProvider.OPENAI
        assert model_info.model_type == ModelType.CHAT
        assert model_info.status == ModelStatus.ACTIVE
        assert model_info.priority == 7
        assert len(model_info.tags) == 2


class TestProductionModelSystem:
    """Test production model system functionality"""

    def test_system_initialization(self):
        """Test system initialization"""
        system = ProductionModelSystem()

        assert len(system.models) >= 3  # Should have default models
        assert system.current_model is not None
        assert len(system.usage_history) == 0

    def test_system_initialization_with_config(self):
        """Test system initialization with config path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            system = ProductionModelSystem(str(config_path))

            assert system.config_path == str(config_path)
            assert len(system.models) >= 3  # Should have default models

    def test_register_model(self):
        """Test model registration"""
        system = ProductionModelSystem()

        capabilities = ModelCapabilities(
            max_tokens=2048,
            context_length=4096,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_audio=False,
            multilingual=True,
            reasoning_depth=6,
            creativity_score=7,
            accuracy_score=8,
            speed_score=9,
        )

        new_model = ModelInfo(
            name="custom-model",
            display_name="Custom Model",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.0,
            cost_per_output_token=0.0,
            description="Custom test model",
            priority=9,
        )

        success = system.register_model(new_model)

        assert success
        assert "custom-model" in system.models
        assert system.models["custom-model"].display_name == "Custom Model"

    def test_switch_to_model(self):
        """Test manual model switching"""
        system = ProductionModelSystem()

        # Get initial current model
        initial_model = system.current_model

        # Find another model to switch to
        available_models = system.get_available_models()
        other_model = next(m.name for m in available_models if m.name != initial_model)

        # Switch models
        success = system.switch_to_model(other_model)

        assert success
        assert system.current_model == other_model

        # Check switch history
        assert len(system.usage_history) > 0
        last_switch = system.usage_history[-1]
        assert last_switch["old_model"] == initial_model
        assert last_switch["new_model"] == other_model

    def test_switch_to_nonexistent_model(self):
        """Test switching to non-existent model"""
        system = ProductionModelSystem()

        success = system.switch_to_model("nonexistent-model")
        assert not success
        assert system.current_model != "nonexistent-model"

    def test_get_current_model(self):
        """Test getting current model"""
        system = ProductionModelSystem()

        current = system.get_current_model()
        assert current is not None
        assert current.name == system.current_model
        assert isinstance(current, ModelInfo)

    def test_get_available_models(self):
        """Test getting available models"""
        system = ProductionModelSystem()

        all_models = system.get_available_models()
        assert len(all_models) >= 3

        active_models = system.get_available_models(status_filter=ModelStatus.ACTIVE)
        assert len(active_models) >= 3  # Default models should be active

    def test_update_model_metrics(self):
        """Test updating model metrics"""
        system = ProductionModelSystem()

        model_name = system.current_model
        # Capture initial values, not object reference
        initial_total_requests = system.models[model_name].metrics.total_requests
        initial_successful_requests = system.models[
            model_name
        ].metrics.successful_requests
        initial_failed_requests = system.models[model_name].metrics.failed_requests
        initial_total_cost = system.models[model_name].metrics.total_cost

        # Update with successful request
        system.update_model_metrics(
            model_name=model_name,
            success=True,
            response_time=1.5,
            tokens=100,
            cost=0.01,
        )

        updated_metrics = system.models[model_name].metrics
        assert updated_metrics.total_requests == initial_total_requests + 1
        assert updated_metrics.successful_requests == initial_successful_requests + 1
        assert updated_metrics.failed_requests == initial_failed_requests
        assert updated_metrics.total_cost == initial_total_cost + 0.01

    def test_get_model_recommendations(self):
        """Test getting model recommendations"""
        system = ProductionModelSystem()

        recommendations = system.get_model_recommendations(
            "Simple question about Python programming", limit=3
        )

        assert len(recommendations) <= 3
        assert len(recommendations) > 0

        for model, scores in recommendations:
            assert isinstance(model, ModelInfo)
            assert "total" in scores
            assert "performance" in scores
            assert "cost" in scores

    def test_task_analysis(self):
        """Test task analysis functionality"""
        system = ProductionModelSystem()

        # Test simple task
        analysis = system._analyze_task("What is Python?")
        assert analysis.complexity == TaskComplexity.SIMPLE
        assert analysis.task_type == "question"
        assert len(analysis.keywords) > 0

        # Test complex task
        analysis = system._analyze_task(
            "Generate a comprehensive analysis of machine learning algorithms"
        )
        assert analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]
        assert analysis.estimated_tokens > 100

    def test_task_classification(self):
        """Test task type classification"""
        system = ProductionModelSystem()

        # Test various task types
        assert system._classify_task_type("What is the meaning of life?") == "question"
        assert (
            system._classify_task_type("Generate a story about dragons") == "creative"
        )
        assert system._classify_task_type("Analyze the economic impact") == "general"
        assert (
            system._classify_task_type("Compare Python vs JavaScript") == "comparison"
        )
        assert system._classify_task_type("Write a Python function") == "coding"

    @pytest.mark.asyncio
    async def test_intelligent_switch(self):
        """Test intelligent model switching"""
        system = ProductionModelSystem()

        # Test with simple task (should keep current model if it's good enough)
        success, model, info = await system.intelligent_switch(
            "What is 2+2?", force_switch=False
        )

        assert success
        assert model is not None
        assert "task_analysis" in info
        assert "selection_scores" in info
        assert "reason" in info

    def test_get_system_statistics(self):
        """Test getting system statistics"""
        system = ProductionModelSystem()

        # Add some metrics
        model_name = system.current_model
        for i in range(5):
            success = i < 4  # 4 out of 5 successful
            system.update_model_metrics(
                model_name=model_name,
                success=success,
                response_time=1.0 + i * 0.5,
                tokens=50 + i * 10,
                cost=0.001 * (i + 1),
            )

        stats = system.get_system_statistics()

        assert "total_models" in stats
        assert "active_models" in stats
        assert "current_model" in stats
        assert "total_requests" in stats
        assert "total_cost" in stats
        assert "average_success_rate" in stats
        assert "model_breakdown" in stats
        assert "usage_history" in stats

        assert stats["total_requests"] == 5
        assert stats["average_success_rate"] == 80.0  # 4/5 * 100

    def test_configuration_persistence(self):
        """Test configuration saving and loading"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"

            # Create system and modify it
            system1 = ProductionModelSystem(str(config_path))

            # Add a custom model
            custom_model = ModelInfo(
                name="persistent-model",
                display_name="Persistent Model",
                provider=ModelProvider.LOCAL,
                model_type=ModelType.CHAT,
                capabilities=ModelCapabilities(
                    max_tokens=1000,
                    context_length=1000,
                    supports_streaming=False,
                    supports_function_calling=False,
                    supports_vision=False,
                    supports_audio=False,
                    multilingual=False,
                    reasoning_depth=5,
                    creativity_score=5,
                    accuracy_score=5,
                    speed_score=5,
                ),
                cost_per_input_token=0.0,
                cost_per_output_token=0.0,
                priority=8,
            )
            system1.register_model(custom_model)
            system1.switch_to_model("persistent-model")

            # Create new system (should load saved config)
            system2 = ProductionModelSystem(str(config_path))

            assert system2.current_model == "persistent-model"
            assert "persistent-model" in system2.models

    def test_factory_function(self):
        """Test factory function"""
        system = create_production_model_system()

        assert isinstance(system, ProductionModelSystem)
        assert len(system.models) >= 3
        assert system.current_model is not None


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""

    def test_performance_tracking(self):
        """Test performance tracking over time"""
        system = create_production_model_system()
        model_name = system.current_model

        # Simulate usage over time
        response_times = [0.8, 1.2, 1.5, 2.0, 1.1, 0.9, 1.3, 1.8, 1.4, 1.0]
        success_rates = [
            True,
            True,
            False,
            True,
            True,
            True,
            False,
            True,
            True,
            True,
            True,
        ]

        for i, (rt, success) in enumerate(zip(response_times, success_rates)):
            system.update_model_metrics(
                model_name=model_name,
                success=success,
                response_time=rt,
                tokens=50 + i * 5,
                cost=0.001 + i * 0.0001,
            )

        metrics = system.models[model_name].metrics
        assert metrics.total_requests == 10
        assert metrics.successful_requests == 8
        assert metrics.failed_requests == 2
        assert 0.8 <= metrics.average_response_time <= 2.0
        assert metrics.performance_score > 60  # Should be reasonable

    def test_cost_optimization_selection(self):
        """Test cost optimization in model selection"""
        system = create_production_model_system()

        # Create a budget-sensitive task
        task = "Simple question that doesn't require advanced reasoning"

        # Analyze the task
        task_analysis = system._analyze_task(task)
        assert task_analysis.budget_sensitivity >= 5  # Should detect budget sensitivity

        # Get recommendations
        recommendations = system.get_model_recommendations(task, limit=3)

        assert len(recommendations) > 0

        # For budget-sensitive tasks, cost should be a significant factor
        # (This depends on the actual model configuration)
        for model, scores in recommendations:
            assert "cost" in scores
            assert 0 <= scores["cost"] <= 100

    def test_model_health_status_changes(self):
        """Test model health status changes based on performance"""
        system = create_production_model_system()
        model_name = system.current_model

        # Initially should be active
        assert system.models[model_name].status == ModelStatus.ACTIVE

        # Add many failed requests to trigger degradation
        for i in range(10):
            system.update_model_metrics(
                model_name=model_name, success=False, response_time=10.0, cost=0.00
            )

        # Check if model status changed
        model_info = system.models[model_name]
        assert model_info.status in [ModelStatus.DEGRADED, ModelStatus.ERROR]

        # Add successful requests to recover (need 41+ successful to get error rate below 20%)  # noqa: E501
        for i in range(41):
            system.update_model_metrics(
                model_name=model_name,
                success=True,
                response_time=1.0,
                tokens=100,
                cost=0.001,
            )

        # Status should recover (or at least not be ERROR)
        updated_info = system.models[model_name]
        assert updated_info.status != ModelStatus.ERROR


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
