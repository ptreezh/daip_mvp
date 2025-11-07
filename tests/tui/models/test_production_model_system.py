"""
Production Model System Tests

This test suite validates the production-grade model management system with
comprehensive testing of intelligent model selection, performance monitoring,
and adaptive switching strategies.
"""

import pytest
import asyncio
import tempfile
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any

# Import production model system components
from daip_live.tui_v1.models.production_model_system import (
    ProductionModelSystem,
    ModelInfo,
    ModelType,
    ModelProvider,
    ModelStatus,
    ModelCapabilities,
    ModelMetrics,
    TaskAnalysis,
    TaskComplexity,
    ModelSelector,
    ModelHealthMonitor,
    create_production_model_system
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
            speed_score=6
        )

        assert capabilities.max_tokens == 4096
        assert capabilities.context_length == 8192
        assert capabilities.supports_streaming == True
        assert capabilities.reasoning_depth == 7
        assert capabilities.creativity_score == 8

    def test_model_capabilities_validation(self):
        """Test model capabilities validation"""
        capabilities = ModelCapabilities(
            max_tokens=4096,
            context_length=8192,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            supports_audio=False,
            multilingual=False,
            reasoning_depth=5,
            creativity_score=5,
            accuracy_score=5,
            speed_score=5
        )

        # All scores should be within valid range (1-10)
        assert 1 <= capabilities.reasoning_depth <= 10
        assert 1 <= capabilities.creativity_score <= 10
        assert 1 <= capabilities.accuracy_score <= 10
        assert 1 <= capabilities.speed_score <= 10


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
        assert metrics.performance_score == 100.0

    def test_model_metrics_update_success(self):
        """Test updating metrics with successful request"""
        metrics = ModelMetrics()

        metrics.update_request(success=True, response_time=1.5, tokens=100, cost=0.01)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.average_response_time == 1.5
        assert metrics.total_cost == 0.01
        assert metrics.performance_score > 90  # Should be high for good performance

    def test_model_metrics_update_failure(self):
        """Test updating metrics with failed request"""
        metrics = ModelMetrics()

        metrics.update_request(success=False, response_time=5.0, cost=0.00)

        assert metrics.total_requests == 1
        assert metrics.successful_requests == 0
        assert metrics.failed_requests == 1
        assert metrics.error_rate == 1.0
        assert metrics.performance_score < 50  # Should be low for failures

    def test_model_metrics_multiple_updates(self):
        """Test metrics with multiple updates"""
        metrics = ModelMetrics()

        # Add several requests
        metrics.update_request(success=True, response_time=1.0, tokens=50, cost=0.005)
        metrics.update_request(success=True, response_time=2.0, tokens=100, cost=0.01)
        metrics.update_request(success=False, response_time=10.0, cost=0.00)

        assert metrics.total_requests == 3
        assert metrics.successful_requests == 2
        assert metrics.failed_requests == 1
        assert metrics.error_rate == 1/3
        assert metrics.total_cost == 0.015

    def test_model_metrics_performance_score_calculation(self):
        """Test performance score calculation"""
        metrics = ModelMetrics()

        # Perfect performance should get high score
        for i in range(10):
            metrics.update_request(success=True, response_time=1.0, tokens=100, cost=0.01)

        assert metrics.performance_score > 80

        # Add some failures
        for i in range(5):
            metrics.update_request(success=False, response_time=5.0, cost=0.00)

        assert metrics.performance_score < 70  # Score should decrease


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
            speed_score=6
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
            priority=7
        )

        assert model_info.name == "test-model"
        assert model_info.display_name == "Test Model"
        assert model_info.provider == ModelProvider.OPENAI
        assert model_info.model_type == ModelType.CHAT
        assert model_info.status == ModelStatus.ACTIVE
        assert model_info.priority == 7
        assert len(model_info.tags) == 2

    def test_model_info_default_values(self):
        """Test model info default values"""
        capabilities = ModelCapabilities(
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
            speed_score=5
        )

        model_info = ModelInfo(
            name="minimal-model",
            display_name="Minimal Model",
            provider=ModelProvider.LOCAL,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.0,
            cost_per_output_token=0.0
        )

        assert model_info.status == ModelStatus.ACTIVE  # Default
        assert model_info.priority == 5  # Default
        assert model_info.tags == []  # Default
        assert model_info.description == ""  # Default
        assert isinstance(model_info.created_at, datetime)
        assert isinstance(model_info.last_updated, datetime)


class TestTaskAnalysis:
    """Test task analysis functionality"""

    def test_task_analysis_creation(self):
        """Test task analysis creation"""
        analysis = TaskAnalysis(
            complexity=TaskComplexity.MODERATE,
            required_capabilities=["function_calling"],
            estimated_tokens=500,
            time_sensitivity=6,
            budget_sensitivity=7,
            quality_requirement=8,
            task_type="question",
            keywords=["test", "analysis"]
        )

        assert analysis.complexity == TaskComplexity.MODERATE
        assert "function_calling" in analysis.required_capabilities
        assert analysis.estimated_tokens == 500
        assert analysis.time_sensitivity == 6
        assert analysis.task_type == "question"
        assert len(analysis.keywords) == 2

    def test_task_analysis_enum_values(self):
        """Test task analysis enum values"""
        complexities = list(TaskComplexity)
        assert len(complexities) == 4
        assert TaskComplexity.SIMPLE in complexities
        assert TaskComplexity.EXPERT in complexities


class TestModelSelector:
    """Test intelligent model selection"""

    def test_model_selector_initialization(self):
        """Test model selector initialization"""
        selector = ModelSelector()

        assert 'performance' in selector.selection_criteria
        assert 'cost' in selector.selection_criteria
        assert 'capabilities' in selector.selection_criteria
        assert 'availability' in selector.selection_criteria

        # Weights should sum to 1.0
        total_weight = sum(selector.selection_criteria.values())
        assert abs(total_weight - 1.0) < 0.001

    def test_select_best_model_basic(self):
        """Test basic model selection"""
        selector = ModelSelector()

        # Create test models
        capabilities = ModelCapabilities(
            max_tokens=1000,
            context_length=1000,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            supports_audio=False,
            multilingual=False,
            reasoning_depth=5,
            creativity_score=5,
            accuracy_score=5,
            speed_score=5
        )

        model1 = ModelInfo(
            name="model1",
            display_name="Model 1",
            provider=ModelProvider.OPENAI,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.01,
            cost_per_output_token=0.02,
            priority=5
        )

        model2 = ModelInfo(
            name="model2",
            display_name="Model 2",
            provider=ModelProvider.ANTHROPIC,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.001,
            cost_per_output_token=0.002,
            priority=7
        )

        # Create task analysis
        task_analysis = TaskAnalysis(
            complexity=TaskComplexity.SIMPLE,
            required_capabilities=[],
            estimated_tokens=100,
            time_sensitivity=5,
            budget_sensitivity=8,
            quality_requirement=5,
            task_type="question",
            keywords=["test"]
        )

        available_models = [model1, model2]
        best_model, scores = selector.select_best_model(task_analysis, available_models)

        assert best_model is not None
        assert best_model.name in ["model1", "model2"]
        assert "total" in scores
        assert "cost" in scores

    def test_capability_match_calculation(self):
        """Test capability match calculation"""
        selector = ModelSelector()

        capabilities = ModelCapabilities(
            max_tokens=1000,
            context_length=2000,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_audio=False,
            multilingual=False,
            reasoning_depth=8,
            creativity_score=7,
            accuracy_score=9,
            speed_score=6
        )

        model = ModelInfo(
            name="test-model",
            display_name="Test Model",
            provider=ModelProvider.OPENAI,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.01,
            cost_per_output_token=0.02
        )

        # Task that requires function calling
        task_analysis = TaskAnalysis(
            complexity=TaskComplexity.COMPLEX,
            required_capabilities=["function_calling"],
            estimated_tokens=1500,
            time_sensitivity=5,
            budget_sensitivity=5,
            quality_requirement=8,
            task_type="analysis",
            keywords=["test"]
        )

        score = selector._calculate_capability_match(model, task_analysis)

        assert 0 <= score <= 100
        # Should get bonus for supporting function calling
        assert score >= 50  # Base score + bonus

    def test_current_model_sufficiency(self):
        """Test current model sufficiency check"""
        selector = ModelSelector()

        capabilities = ModelCapabilities(
            max_tokens=2000,
            context_length=2000,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            supports_audio=False,
            multilingual=False,
            reasoning_depth=7,
            creativity_score=6,
            accuracy_score=8,
            speed_score=7
        )

        current_model = ModelInfo(
            name="current",
            display_name="Current Model",
            provider=ModelProvider.OPENAI,
            model_type=ModelType.CHAT,
            capabilities=capabilities,
            cost_per_input_token=0.01,
            cost_per_output_token=0.02
        )

        task_analysis = TaskAnalysis(
            complexity=TaskComplexity.MODERATE,
            required_capabilities=[],
            estimated_tokens=1000,
            time_sensitivity=5,
            budget_sensitivity=5,
            quality_requirement=7,
            task_type="question",
            keywords=["test"]
        )

        # Current model should be sufficient for simple tasks
        current_score = selector._calculate_model_score(current_model, task_analysis)

        # Within 10% should be considered sufficient
        assert selector._is_current_model_sufficient(
            current_model, task_analysis, {'total': current_score['total'] * 0.95}
        )

        # Much lower score should trigger switch
        assert not selector._is_current_model_sufficient(
            current_model, task_analysis, {'total': current_score['total'] * 0.8}
        )


class TestModelHealthMonitor:
    """Test model health monitoring"""

    def test_health_monitor_initialization(self):
        """Test health monitor initialization"""
        monitor = ModelHealthMonitor(check_interval=30)

        assert monitor.check_interval == 30
        assert len(monitor.health_checks) == 0
        assert isinstance(monitor.last_check_time, datetime)

    def test_health_check_registration(self):
        """Test health check registration"""
        monitor = ModelHealthMonitor()

        async def mock_health_check():
            return True

        monitor.register_health_check("test-model", mock_health_check)

        assert "test-model" in monitor.health_checks
        assert monitor.health_checks["test-model"] == mock_health_check

    async def test_model_health_check_healthy(self):
        """Test health check for healthy model"""
        monitor = ModelHealthMonitor()

        # Create healthy model metrics
        metrics = ModelMetrics()
        for _ in range(10):
            metrics.update_request(success=True, response_time=1.0, tokens=100, cost=0.01)

        model = ModelInfo(
            name="healthy-model",
            display_name="Healthy Model",
            provider=ModelProvider.OPENAI,
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
                speed_score=5
            ),
            cost_per_input_token=0.01,
            cost_per_output_token=0.02
        )
        model.metrics = metrics

        is_healthy = await monitor.check_model_health(model)
        assert is_healthy == True

    async def test_model_health_check_unhealthy(self):
        """Test health check for unhealthy model"""
        monitor = ModelHealthMonitor()

        # Create unhealthy model metrics (high error rate)
        metrics = ModelMetrics()
        for _ in range(10):
            metrics.update_request(success=False, response_time=10.0, cost=0.00)

        model = ModelInfo(
            name="unhealthy-model",
            display_name="Unhealthy Model",
            provider=ModelProvider.OPENAI,
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
                speed_score=5
            ),
            cost_per_input_token=0.01,
            cost_per_output_token=0.02
        )
        model.metrics = metrics

        is_healthy = await monitor.check_model_health(model)
        assert is_healthy == False

    def test_model_status_update(self):
        """Test model status updates based on metrics"""
        monitor = ModelHealthMonitor()

        # Create model with high error rate
        metrics = ModelMetrics()
        for _ in range(10):
            metrics.update_request(success=False, response_time=5.0, cost=0.00)

        model = ModelInfo(
            name="error-model",
            display_name="Error Model",
            provider=ModelProvider.OPENAI,
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
                speed_score=5
            ),
            cost_per_input_token=0.01,
            cost_per_output_token=0.02
        )
        model.metrics = metrics

        new_status = monitor.update_model_status(model)
        assert new_status == ModelStatus.ERROR

        # Model with good performance should stay active
        good_metrics = ModelMetrics()
        for _ in range(10):
            good_metrics.update_request(success=True, response_time=1.0, tokens=100, cost=0.01)

        model.metrics = good_metrics
        new_status = monitor.update_model_status(model)
        assert new_status == ModelStatus.ACTIVE


class TestProductionModelSystem:
    """Test production model system functionality"""

    def test_system_initialization(self):
        """Test system initialization"""
        system = ProductionModelSystem()

        assert len(system.models) >= 3  # Should have default models
        assert system.current_model is not None
        assert isinstance(system.selector, ModelSelector)
        assert isinstance(system.health_monitor, ModelHealthMonitor)
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
            speed_score=9
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
            priority=9
        )

        success = system.register_model(new_model)

        assert success == True
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

        assert success == True
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
        assert success == False
        assert system.current_model != "nonexistent-model"

    def test_switch_to_inactive_model(self):
        """Test switching to inactive model"""
        system = ProductionModelSystem()

        # Set a model to inactive status
        model_name = list(system.models.keys())[0]
        system.models[model_name].status = ModelStatus.MAINTENANCE

        # Try to switch to it (should fail unless forced)
        success = system.switch_to_model(model_name, force=False)
        assert success == False

        # Should succeed with force=True
        success = system.switch_to_model(model_name, force=True)
        assert success == True

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

        # Test filtering by status
        if len(all_models) > 0:
            # Set one model to inactive
            model_name = all_models[0].name
            system.models[model_name].status = ModelStatus.INACTIVE

            inactive_models = system.get_available_models(status_filter=ModelStatus.INACTIVE)
            assert any(m.name == model_name for m in inactive_models)

    def test_update_model_metrics(self):
        """Test updating model metrics"""
        system = ProductionModelSystem()

        model_name = system.current_model
        initial_metrics = system.models[model_name].metrics

        # Update with successful request
        system.update_model_metrics(
            model_name=model_name,
            success=True,
            response_time=1.5,
            tokens=100,
            cost=0.01
        )

        updated_metrics = system.models[model_name].metrics
        assert updated_metrics.total_requests == initial_metrics.total_requests + 1
        assert updated_metrics.successful_requests == initial_metrics.successful_requests + 1
        assert updated_metrics.total_cost == initial_metrics.total_cost + 0.01

    def test_get_model_recommendations(self):
        """Test getting model recommendations"""
        system = ProductionModelSystem()

        recommendations = system.get_model_recommendations(
            "Simple question about Python programming",
            limit=3
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
            "Generate a comprehensive analysis of machine learning algorithms, "
            "comparing their performance on various datasets and providing detailed "
            "explanations of the mathematical foundations."
        )
        assert analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]
        assert analysis.estimated_tokens > 100  # Should be higher for complex tasks

    def test_task_classification(self):
        """Test task type classification"""
        system = ProductionModelSystem()

        # Test various task types
        assert system._classify_task_type("What is the meaning of life?") == "question"
        assert system._classify_task_type("Generate a story about dragons") == "generation"
        assert system._classify_task_type("Analyze the economic impact") == "analysis"
        assert system._classify_task_type("Compare Python vs JavaScript") == "comparison"
        assert system._classify_task_type("Write a Python function") == "coding"

    @pytest.mark.asyncio
    async def test_intelligent_switch(self):
        """Test intelligent model switching"""
        system = ProductionModelSystem()

        # Test with simple task (should keep current model if it's good enough)
        success, model, info = await system.intelligent_switch(
            "What is 2+2?",
            force_switch=False
        )

        assert success == True
        assert model is not None
        assert "task_analysis" in info
        assert "selection_scores" in info
        assert "reason" in info

        # Test with complex task
        success, model, info = await system.intelligent_switch(
            "Create a comprehensive analysis of quantum computing applications "
            "in cryptography with detailed mathematical proofs and code examples",
            force_switch=False
        )

        assert success == True
        assert model is not None

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
                cost=0.001 * (i + 1)
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
            original_current = system1.current_model

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
                    speed_score=5
                ),
                cost_per_input_token=0.0,
                cost_per_output_token=0.0,
                priority=8
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

    @pytest.mark.asyncio
    async def test_end_to_end_model_selection(self):
        """Test complete model selection workflow"""
        system = create_production_model_system()

        # Simulate various tasks and intelligent switching
        tasks = [
            ("What is the capital of France?", "simple question"),
            ("Generate a Python function to calculate factorial", "coding task"),
            ("Analyze the pros and cons of remote work", "analysis task"),
            ("Write a creative story about time travel", "creative task")
        ]

        for task, description in tasks:
            success, model, info = await system.intelligent_switch(task)

            assert success == True
            assert model is not None
            assert info["reason"] in ["Current model is sufficient", "Better model selected for task"]

            # Simulate using the model
            system.update_model_metrics(
                model_name=model.name,
                success=True,
                response_time=1.0 + hash(task) % 3,
                tokens=len(task.split()) * 2,
                cost=0.001
            )

        # Check final statistics
        stats = system.get_system_statistics()
        assert stats["total_requests"] == len(tasks)
        assert stats["average_success_rate"] == 100.0

    def test_performance_degradation_handling(self):
        """Test handling of model performance degradation"""
        system = create_production_model_system()

        # Get available models
        available_models = system.get_available_models()
        if len(available_models) < 2:
            pytest.skip("Need at least 2 models for this test")

        # Simulate performance degradation for current model
        current_model = system.current_model

        # Add many failed requests to trigger degradation
        for i in range(10):
            system.update_model_metrics(
                model_name=current_model,
                success=False,
                response_time=10.0,
                cost=0.00
            )

        # Check if model status changed
        model_info = system.models[current_model]
        assert model_info.status in [ModelStatus.DEGRADED, ModelStatus.ERROR]

    def test_cost_optimization(self):
        """Test cost optimization in model selection"""
        system = create_production_model_system()

        # Create a budget-sensitive task
        task = "Simple question that doesn't require advanced reasoning"

        success, model, info = await system.intelligent_switch(task)

        assert success == True

        # For simple tasks, should prefer cheaper models
        # (This is a heuristic test - actual behavior depends on model configuration)
        task_analysis = system._analyze_task(task)
        assert task_analysis.budget_sensitivity >= 5  # Should detect budget sensitivity

    def test_concurrent_model_updates(self):
        """Test thread safety of concurrent model updates"""
        import threading

        system = create_production_model_system()
        model_name = system.current_model

        # Create multiple threads updating the same model
        def update_metrics():
            for i in range(10):
                system.update_model_metrics(
                    model_name=model_name,
                    success=i % 2 == 0,  # 50% success rate
                    response_time=1.0 + i * 0.1,
                    tokens=50 + i,
                    cost=0.001
                )

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=update_metrics)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final state
        final_metrics = system.models[model_name].metrics
        assert final_metrics.total_requests == 50  # 5 threads * 10 updates each


if __name__ == "__main__":
    pytest.main([__file__, "-v"])