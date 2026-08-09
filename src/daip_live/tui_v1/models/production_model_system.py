"""
Production Model Management System for newP6 TUI

This module provides a comprehensive, high-quality model management system
designed for single-user local environments with enterprise-grade features
including intelligent model selection, performance monitoring, and adaptive
switching strategies.

Key Features:
- Intelligent model recommendation based on task analysis
- Performance tracking and model health monitoring
- Adaptive switching strategies
- Cost optimization and resource management
- Comprehensive model lifecycle management
"""

import json
import logging
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock, RLock
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Model types with specific capabilities"""

    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    REASONING = "reasoning"
    CODE = "code"
    CREATIVE = "creative"
    ANALYSIS = "analysis"


class ModelProvider(Enum):
    """Model providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    GOOGLE = "google"


class TaskComplexity(Enum):
    """Task complexity levels"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


class ModelStatus(Enum):
    """Model status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class ModelCapabilities:
    """Model capabilities specification"""

    max_tokens: int
    context_length: int
    supports_streaming: bool
    supports_function_calling: bool
    supports_vision: bool
    supports_audio: bool
    multilingual: bool
    reasoning_depth: int  # 1-10 scale
    creativity_score: int  # 1-10 scale
    accuracy_score: int  # 1-10 scale
    speed_score: int  # 1-10 scale


@dataclass
class ModelMetrics:
    """Model performance metrics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    average_tokens_per_second: float = 0.0
    total_cost: float = 0.0
    last_used: Optional[datetime] = None
    uptime_percentage: float = 100.0
    error_rate: float = 0.0
    performance_score: float = 0.0

    def update_request(
        self, success: bool, response_time: float, tokens: int = 0, cost: float = 0.0
    ) -> None:
        """Update metrics with new request data"""
        self.total_requests += 1
        self.last_used = datetime.now()

        if success:
            self.successful_requests += 1
            # Update average response time
            if self.average_response_time == 0:
                self.average_response_time = response_time
            else:
                self.average_response_time = (
                    self.average_response_time * 0.9 + response_time * 0.1
                )

            # Update tokens per second
            if response_time > 0 and tokens > 0:
                tps = tokens / response_time
                if self.average_tokens_per_second == 0:
                    self.average_tokens_per_second = tps
                else:
                    self.average_tokens_per_second = (
                        self.average_tokens_per_second * 0.9 + tps * 0.1
                    )
        else:
            self.failed_requests += 1

        self.total_cost += cost
        self.error_rate = (
            self.failed_requests / self.total_requests if self.total_requests > 0 else 0
        )
        self.performance_score = self._calculate_performance_score()

    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if self.total_requests == 0:
            return 100.0

        success_rate = (self.successful_requests / self.total_requests) * 100
        speed_factor = min(100, 1000 / max(1, self.average_response_time))
        cost_factor = max(
            0, 100 - (self.total_cost / max(1, self.successful_requests)) * 10
        )

        return success_rate * 0.5 + speed_factor * 0.3 + cost_factor * 0.2


@dataclass
class ModelInfo:
    """Comprehensive model information"""

    name: str
    display_name: str
    provider: ModelProvider
    model_type: ModelType
    capabilities: ModelCapabilities
    cost_per_input_token: float
    cost_per_output_token: float
    description: str = ""
    tags: list[str] = field(default_factory=list)
    status: ModelStatus = ModelStatus.ACTIVE
    priority: int = 5  # 1-10, higher is preferred
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    config: dict[str, Any] = field(default_factory=dict)
    metrics: ModelMetrics = field(default_factory=ModelMetrics)


@dataclass
class TaskAnalysis:
    """Task analysis results"""

    complexity: TaskComplexity
    required_capabilities: list[str]
    estimated_tokens: int
    time_sensitivity: int  # 1-10
    budget_sensitivity: int  # 1-10
    quality_requirement: int  # 1-10
    task_type: str
    keywords: list[str]


class ModelSelector:
    """Intelligent model selection algorithm"""

    def __init__(self):
        self.selection_criteria = {
            "performance": 0.3,
            "cost": 0.2,
            "capabilities": 0.3,
            "availability": 0.2,
        }

    def select_best_model(
        self,
        task_analysis: TaskAnalysis,
        available_models: list[ModelInfo],
        current_model: Optional[ModelInfo] = None,
    ) -> tuple[Optional[ModelInfo], dict[str, float]]:
        """Select the best model for the given task"""
        if not available_models:
            return None, {}

        scored_models = []

        for model in available_models:
            if model.status != ModelStatus.ACTIVE:
                continue

            score = self._calculate_model_score(model, task_analysis)
            scored_models.append((model, score))

        # Sort by total score (descending)
        scored_models.sort(key=lambda x: x[1].get("total", 0), reverse=True)

        if not scored_models:
            return None, {}

        best_model, score_details = scored_models[0]

        # Check if current model is good enough to avoid unnecessary switching
        if current_model and self._is_current_model_sufficient(
            current_model, task_analysis, scored_models[0][1]
        ):
            return current_model, score_details

        return best_model, score_details

    def _calculate_model_score(
        self, model: ModelInfo, task_analysis: TaskAnalysis
    ) -> dict[str, float]:
        """Calculate comprehensive model score"""
        scores = {}

        # Performance score
        scores["performance"] = model.metrics.performance_score

        # Cost efficiency
        estimated_cost = (task_analysis.estimated_tokens / 1000) * (
            model.cost_per_input_token + model.cost_per_output_token
        )
        scores["cost"] = max(0, 100 - estimated_cost * 10)

        # Capability match
        capability_score = self._calculate_capability_match(model, task_analysis)
        scores["capabilities"] = capability_score

        # Availability
        availability_score = 100 - (model.metrics.error_rate * 100)
        scores["availability"] = availability_score

        # Calculate weighted total
        total_score = sum(
            scores[key] * weight for key, weight in self.selection_criteria.items()
        )
        scores["total"] = total_score

        return scores

    def _calculate_capability_match(
        self, model: ModelInfo, task_analysis: TaskAnalysis
    ) -> float:
        """Calculate how well model capabilities match task requirements"""
        score = 50.0  # Base score

        # Check specific capabilities
        if "function_calling" in task_analysis.required_capabilities:
            if model.capabilities.supports_function_calling:
                score += 20

        if "streaming" in task_analysis.required_capabilities:
            if model.capabilities.supports_streaming:
                score += 15

        if "vision" in task_analysis.required_capabilities:
            if model.capabilities.supports_vision:
                score += 25

        # Check complexity matching
        complexity_mapping = {
            TaskComplexity.SIMPLE: 3,
            TaskComplexity.MODERATE: 5,
            TaskComplexity.COMPLEX: 7,
            TaskComplexity.EXPERT: 9,
        }
        required_depth = complexity_mapping[task_analysis.complexity]
        if model.capabilities.reasoning_depth >= required_depth:
            score += 15
        else:
            score -= (required_depth - model.capabilities.reasoning_depth) * 5

        # Check context length
        if model.capabilities.context_length >= task_analysis.estimated_tokens:
            score += 10
        else:
            score -= 20

        return max(0, min(100, score))

    def _is_current_model_sufficient(
        self,
        current_model: ModelInfo,
        task_analysis: TaskAnalysis,
        best_score: dict[str, float],
    ) -> bool:
        """Check if current model is sufficient for the task"""
        current_score = self._calculate_model_score(current_model, task_analysis)

        # If current model score is within 10% of best model, keep it
        return current_score["total"] >= best_score["total"] * 0.9


class ModelHealthMonitor:
    """Monitor model health and performance"""

    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.health_checks: dict[str, callable] = {}
        self.last_check_time = datetime.now()
        self._lock = Lock()

    def register_health_check(self, model_name: str, check_func: callable) -> None:
        """Register a health check function for a model"""
        with self._lock:
            self.health_checks[model_name] = check_func

    async def check_model_health(self, model: ModelInfo) -> bool:
        """Check if a model is healthy"""
        # Simple health check based on recent metrics
        if model.metrics.error_rate > 0.1:  # 10% error rate threshold
            return False

        if model.metrics.average_response_time > 30:  # 30 second timeout
            return False

        # Check if model was used recently
        if (
            model.metrics.last_used
            and datetime.now() - model.metrics.last_used > timedelta(hours=1)
        ):
            # Perform health check
            if model.name in self.health_checks:
                try:
                    return await self.health_checks[model.name]()
                except Exception as e:
                    logger.error(f"Health check failed for {model.name}: {e}")
                    return False

        return True

    def update_model_status(self, model: ModelInfo) -> ModelStatus:
        """Update model status based on health and performance"""
        if model.metrics.error_rate > 0.2:
            return ModelStatus.ERROR
        elif model.metrics.error_rate > 0.05:
            return ModelStatus.DEGRADED
        elif model.metrics.performance_score < 50:
            return ModelStatus.DEGRADED
        else:
            return ModelStatus.ACTIVE


class ProductionModelSystem:
    """Production-grade model management system"""

    def __init__(self, config_path: Optional[str] = None):
        self.models: dict[str, ModelInfo] = {}
        self.current_model: Optional[str] = None
        self.selector = ModelSelector()
        self.health_monitor = ModelHealthMonitor()
        self.usage_history: deque = deque(maxlen=1000)
        self.performance_history: dict[str, list[ModelMetrics]] = defaultdict(list)
        self._lock = RLock()

        # Load configuration
        self.config_path = config_path or Path.home() / ".daip" / "model_config.json"
        self._load_configuration()
        self._register_default_models()

        logger.info("Production Model System initialized")

    def register_model(self, model_info: ModelInfo) -> bool:
        """Register a new model"""
        with self._lock:
            if model_info.name in self.models:
                logger.warning(f"Model {model_info.name} already exists, updating...")

            self.models[model_info.name] = model_info

            # Set as current if no current model
            if not self.current_model:
                self.current_model = model_info.name

            logger.info(f"Registered model: {model_info.name}")
            self._save_configuration()
            return True

    def switch_to_model(self, model_name: str, force: bool = False) -> bool:
        """Switch to a specific model"""
        with self._lock:
            if model_name not in self.models:
                logger.error(f"Model {model_name} not found")
                return False

            model = self.models[model_name]

            # Check model health unless forced
            if not force and model.status != ModelStatus.ACTIVE:
                logger.warning(
                    f"Model {model_name} is not active (status: {model.status})"
                )
                return False

            old_model = self.current_model
            self.current_model = model_name

            # Record switch
            self._record_model_switch(old_model, model_name, force)

            logger.info(f"Switched from {old_model} to {model_name}")
            self._save_configuration()
            return True

    async def intelligent_switch(
        self, task_description: str, force_switch: bool = False
    ) -> tuple[bool, Optional[ModelInfo], dict[str, Any]]:
        """Intelligently switch to the best model for the task"""
        # Analyze task
        task_analysis = self._analyze_task(task_description)

        # Get current model
        current_model_info = None
        if self.current_model:
            current_model_info = self.models.get(self.current_model)

        # Select best model
        available_models = [
            model
            for model in self.models.values()
            if model.status == ModelStatus.ACTIVE
        ]

        best_model, score_details = self.selector.select_best_model(
            task_analysis, available_models, current_model_info
        )

        if not best_model:
            return False, None, {"error": "No suitable model available"}

        # Decide whether to switch
        should_switch = (
            force_switch
            or not current_model_info
            or best_model.name != current_model_info.name
        )

        if should_switch:
            success = self.switch_to_model(best_model.name)
            if success:
                return (
                    True,
                    best_model,
                    {
                        "task_analysis": asdict(task_analysis),
                        "selection_scores": score_details,
                        "reason": "Better model selected for task",
                    },
                )
            else:
                return False, current_model_info, {"error": "Failed to switch model"}
        else:
            return (
                True,
                current_model_info,
                {
                    "task_analysis": asdict(task_analysis),
                    "selection_scores": score_details,
                    "reason": "Current model is sufficient",
                },
            )

    def get_current_model(self) -> Optional[ModelInfo]:
        """Get current model information"""
        with self._lock:
            if self.current_model:
                return self.models.get(self.current_model)
            return None

    def get_available_models(
        self, status_filter: Optional[ModelStatus] = None
    ) -> list[ModelInfo]:
        """Get available models"""
        with self._lock:
            models = list(self.models.values())
            if status_filter:
                models = [m for m in models if m.status == status_filter]
            return sorted(models, key=lambda x: x.priority, reverse=True)

    def get_model_recommendations(
        self, task_description: str, limit: int = 5
    ) -> list[tuple[ModelInfo, dict[str, float]]]:
        """Get model recommendations for a task"""
        task_analysis = self._analyze_task(task_description)
        available_models = [
            m for m in self.models.values() if m.status == ModelStatus.ACTIVE
        ]

        recommendations = []
        for model in available_models:
            score = self.selector._calculate_model_score(model, task_analysis)
            recommendations.append((model, score))

        recommendations.sort(key=lambda x: x[1]["total"], reverse=True)
        return recommendations[:limit]

    def update_model_metrics(
        self,
        model_name: str,
        success: bool,
        response_time: float,
        tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """Update model performance metrics"""
        with self._lock:
            if model_name in self.models:
                model = self.models[model_name]
                old_metrics = ModelMetrics(
                    total_requests=model.metrics.total_requests,
                    successful_requests=model.metrics.successful_requests,
                    failed_requests=model.metrics.failed_requests,
                    average_response_time=model.metrics.average_response_time,
                    average_tokens_per_second=model.metrics.average_tokens_per_second,
                    total_cost=model.metrics.total_cost,
                )

                model.metrics.update_request(success, response_time, tokens, cost)

                # Update model status based on performance
                new_status = self.health_monitor.update_model_status(model)
                if new_status != model.status:
                    old_status = model.status
                    model.status = new_status
                    logger.info(
                        f"Model {model_name} status changed: {old_status} -> {new_status}"  # noqa: E501
                    )

                # Store performance history
                self.performance_history[model_name].append(old_metrics)
                if len(self.performance_history[model_name]) > 100:
                    self.performance_history[model_name].pop(0)

    def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics"""
        with self._lock:
            stats = {
                "total_models": len(self.models),
                "active_models": len(
                    [m for m in self.models.values() if m.status == ModelStatus.ACTIVE]
                ),
                "current_model": self.current_model,
                "total_requests": sum(
                    m.metrics.total_requests for m in self.models.values()
                ),
                "total_cost": sum(m.metrics.total_cost for m in self.models.values()),
                "average_success_rate": 0.0,
                "model_breakdown": {},
                "usage_history": list(self.usage_history)[-10:],  # Last 10 switches
                "last_updated": datetime.now().isoformat(),
            }

            # Calculate average success rate
            total_requests = stats["total_requests"]
            if total_requests > 0:
                total_successful = sum(
                    m.metrics.successful_requests for m in self.models.values()
                )
                stats["average_success_rate"] = (
                    total_successful / total_requests
                ) * 100

            # Model breakdown
            for model in self.models.values():
                stats["model_breakdown"][model.name] = {
                    "provider": model.provider.value,
                    "type": model.model_type.value,
                    "status": model.status.value,
                    "requests": model.metrics.total_requests,
                    "success_rate": (
                        (
                            model.metrics.successful_requests
                            / max(1, model.metrics.total_requests)
                        )
                        * 100
                    ),
                    "avg_response_time": model.metrics.average_response_time,
                    "performance_score": model.metrics.performance_score,
                    "total_cost": model.metrics.total_cost,
                }

            return stats

    def _analyze_task(self, task_description: str) -> TaskAnalysis:
        """Analyze task requirements"""
        text = task_description.lower()

        # Determine complexity
        complexity_indicators = {
            "simple": ["simple", "basic", "quick", "easy", "short"],
            "moderate": ["explain", "describe", "analyze", "compare", "list"],
            "complex": ["complex", "detailed", "comprehensive", "in-depth", "thorough"],
            "expert": ["expert", "advanced", "specialized", "technical", "research"],
        }

        complexity_scores = {}
        for level, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text)
            complexity_scores[level] = score

        complexity = max(complexity_scores.items(), key=lambda x: x[1])[0]
        complexity = TaskComplexity(complexity)

        # Determine required capabilities
        required_capabilities = []
        if any(word in text for word in ["function", "tool", "api", "call"]):
            required_capabilities.append("function_calling")
        if any(word in text for word in ["stream", "real-time", "continuous"]):
            required_capabilities.append("streaming")
        if any(word in text for word in ["image", "picture", "visual", "diagram"]):
            required_capabilities.append("vision")

        # Estimate tokens (rough heuristic)
        base_tokens = len(task_description.split()) * 2

        # Adjust for complexity indicators
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            base_tokens *= 2
        elif complexity == TaskComplexity.MODERATE:
            base_tokens *= 1.5

        # Add bonus for comprehensive/detailed tasks
        if any(
            word in text
            for word in ["comprehensive", "detailed", "thorough", "in-depth"]
        ):
            base_tokens += 200

        estimated_tokens = max(100, int(base_tokens))

        # Determine sensitivities
        time_sensitivity = 5  # Default
        if any(word in text for word in ["urgent", "quick", "fast", "immediate"]):
            time_sensitivity = 8
        elif any(word in text for word in ["slow", "careful", "detailed"]):
            time_sensitivity = 3

        budget_sensitivity = 5  # Default
        if any(word in text for word in ["cheap", "budget", "cost-effective"]):
            budget_sensitivity = 8
        elif any(word in text for word in ["premium", "best", "quality"]):
            budget_sensitivity = 2

        quality_requirement = 7  # Default
        if any(word in text for word in ["accurate", "precise", "correct"]):
            quality_requirement = 9
        elif any(word in text for word in ["rough", "estimate", "approximate"]):
            quality_requirement = 5

        # Extract keywords
        keywords = [word for word in task_description.split() if len(word) > 3][:10]

        return TaskAnalysis(
            complexity=complexity,
            required_capabilities=required_capabilities,
            estimated_tokens=estimated_tokens,
            time_sensitivity=time_sensitivity,
            budget_sensitivity=budget_sensitivity,
            quality_requirement=quality_requirement,
            task_type=self._classify_task_type(text),
            keywords=keywords,
        )

    def _classify_task_type(self, text: str) -> str:
        """Classify the type of task"""
        task_patterns = {
            "question": ["what", "how", "why", "when", "where", "who", "?"],
            "generation": ["generate", "create", "write", "compose", "produce"],
            "analysis": ["analyze", "examine", "evaluate", "assess", "review"],
            "comparison": ["compare", "contrast", "difference", "versus", "vs"],
            "explanation": ["explain", "describe", "elaborate", "clarify"],
            "coding": ["code", "program", "function", "algorithm", "script"],
            "creative": ["creative", "story", "poem", "art", "design"],
            "translation": ["translate", "convert", "language"],
            "summarization": ["summarize", "summary", "brief", "condense"],
        }

        scores = {}
        for task_type, patterns in task_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                scores[task_type] = score

        if not scores:
            return "general"

        # Special case: prioritize 'generation' over 'creative' if both are present
        if "generation" in scores and "creative" in scores:
            return "generation"

        return max(scores.items(), key=lambda x: x[1])[0]

    def _record_model_switch(
        self, old_model: Optional[str], new_model: str, forced: bool
    ) -> None:
        """Record model switch in history"""
        switch_record = {
            "timestamp": datetime.now().isoformat(),
            "old_model": old_model,
            "new_model": new_model,
            "forced": forced,
            "reason": "manual" if forced else "automatic",
        }

        self.usage_history.append(switch_record)

    def _register_default_models(self) -> None:
        """Register default models for demonstration"""
        default_models = [
            ModelInfo(
                name="gpt-4",
                display_name="GPT-4",
                provider=ModelProvider.OPENAI,
                model_type=ModelType.CHAT,
                capabilities=ModelCapabilities(
                    max_tokens=8192,
                    context_length=8192,
                    supports_streaming=True,
                    supports_function_calling=True,
                    supports_vision=False,
                    supports_audio=False,
                    multilingual=True,
                    reasoning_depth=8,
                    creativity_score=7,
                    accuracy_score=9,
                    speed_score=6,
                ),
                cost_per_input_token=0.00003,
                cost_per_output_token=0.00006,
                description="Highly capable reasoning model",
                tags=["reasoning", "analysis", "general"],
                priority=8,
            ),
            ModelInfo(
                name="gpt-3.5-turbo",
                display_name="GPT-3.5 Turbo",
                provider=ModelProvider.OPENAI,
                model_type=ModelType.CHAT,
                capabilities=ModelCapabilities(
                    max_tokens=4096,
                    context_length=4096,
                    supports_streaming=True,
                    supports_function_calling=True,
                    supports_vision=False,
                    supports_audio=False,
                    multilingual=True,
                    reasoning_depth=6,
                    creativity_score=6,
                    accuracy_score=7,
                    speed_score=9,
                ),
                cost_per_input_token=0.0000015,
                cost_per_output_token=0.000002,
                description="Fast and cost-effective model",
                tags=["fast", "cost-effective", "general"],
                priority=7,
            ),
            ModelInfo(
                name="claude-3-opus",
                display_name="Claude 3 Opus",
                provider=ModelProvider.ANTHROPIC,
                model_type=ModelType.REASONING,
                capabilities=ModelCapabilities(
                    max_tokens=4096,
                    context_length=200000,
                    supports_streaming=True,
                    supports_function_calling=True,
                    supports_vision=True,
                    supports_audio=False,
                    multilingual=True,
                    reasoning_depth=10,
                    creativity_score=8,
                    accuracy_score=9,
                    speed_score=5,
                ),
                cost_per_input_token=0.000015,
                cost_per_output_token=0.000075,
                description="High-performance reasoning model with large context",
                tags=["reasoning", "large-context", "analysis"],
                priority=9,
            ),
        ]

        for model in default_models:
            self.register_model(model)

    def _save_configuration(self) -> None:
        """Save system configuration to disk"""
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            def model_to_dict(model):
                """Convert ModelInfo to dictionary, handling enums"""
                return {
                    "name": model.name,
                    "display_name": model.display_name,
                    "provider": model.provider.value,
                    "model_type": model.model_type.value,
                    "capabilities": {
                        "max_tokens": model.capabilities.max_tokens,
                        "context_length": model.capabilities.context_length,
                        "supports_streaming": model.capabilities.supports_streaming,
                        "supports_function_calling": model.capabilities.supports_function_calling,  # noqa: E501
                        "supports_vision": model.capabilities.supports_vision,
                        "supports_audio": model.capabilities.supports_audio,
                        "multilingual": model.capabilities.multilingual,
                        "reasoning_depth": model.capabilities.reasoning_depth,
                        "creativity_score": model.capabilities.creativity_score,
                        "accuracy_score": model.capabilities.accuracy_score,
                        "speed_score": model.capabilities.speed_score,
                    },
                    "cost_per_input_token": model.cost_per_input_token,
                    "cost_per_output_token": model.cost_per_output_token,
                    "description": model.description,
                    "tags": model.tags,
                    "status": model.status.value,
                    "priority": model.priority,
                    "created_at": model.created_at.isoformat(),
                    "last_updated": model.last_updated.isoformat(),
                    "config": model.config,
                    "metrics": {
                        "total_requests": model.metrics.total_requests,
                        "successful_requests": model.metrics.successful_requests,
                        "failed_requests": model.metrics.failed_requests,
                        "average_response_time": model.metrics.average_response_time,
                        "average_tokens_per_second": model.metrics.average_tokens_per_second,  # noqa: E501
                        "total_cost": model.metrics.total_cost,
                        "last_used": model.metrics.last_used.isoformat()
                        if model.metrics.last_used
                        else None,
                        "uptime_percentage": model.metrics.uptime_percentage,
                        "error_rate": model.metrics.error_rate,
                        "performance_score": model.metrics.performance_score,
                    },
                }

            config = {
                "current_model": self.current_model,
                "models": {
                    name: model_to_dict(model) for name, model in self.models.items()
                },
                "last_updated": datetime.now().isoformat(),
            }

            # Handle datetime serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            with open(config_path, "w") as f:
                json.dump(config, f, indent=2, default=json_serializer)

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def _load_configuration(self) -> None:
        """Load system configuration from disk"""
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                return

            with open(config_path) as f:
                config = json.load(f)

            self.current_model = config.get("current_model")

            # Load models
            models_data = config.get("models", {})
            for name, model_data in models_data.items():
                # Convert data back to proper objects
                model_data["provider"] = ModelProvider(model_data["provider"])
                model_data["model_type"] = ModelType(model_data["model_type"])
                model_data["status"] = ModelStatus(model_data.get("status", "active"))

                # Reconstruct capabilities
                if "capabilities" in model_data:
                    capabilities_data = model_data.pop("capabilities")
                    model_data["capabilities"] = ModelCapabilities(**capabilities_data)

                # Reconstruct metrics
                if "metrics" in model_data:
                    metrics_data = model_data.pop("metrics")
                    if (
                        "last_used" in metrics_data
                        and metrics_data["last_used"] is not None
                    ):
                        metrics_data["last_used"] = datetime.fromisoformat(
                            metrics_data["last_used"]
                        )
                    model_data["metrics"] = ModelMetrics(**metrics_data)

                # Reconstruct datetimes
                if "created_at" in model_data:
                    model_data["created_at"] = datetime.fromisoformat(
                        model_data["created_at"]
                    )
                if "last_updated" in model_data:
                    model_data["last_updated"] = datetime.fromisoformat(
                        model_data["last_updated"]
                    )

                model = ModelInfo(**model_data)
                self.models[name] = model

            logger.info(f"Loaded configuration: {len(self.models)} models")

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")


# Factory function for easy initialization
def create_production_model_system(
    config_path: Optional[str] = None,
) -> ProductionModelSystem:
    """Create and configure a production model system"""
    system = ProductionModelSystem(config_path)
    logger.info("Production Model System created with default models")
    return system
