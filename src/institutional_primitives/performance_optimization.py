"""@Time    : 2025-07-25 08:00:00
@Author  : DAIP-LIVE Team
@File    : performance_optimization.py
@Description:
    Performance profiling and optimization system for workflows.
    Implements requirements 7.6, 7.7 - configuration validation and performance optimization.
"""
import logging
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PerformanceMetricType(str, Enum):
    """Types of performance metrics."""

    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    QUEUE_SIZE = "queue_size"
    RESOURCE_UTILIZATION = "resource_utilization"


class BottleneckType(str, Enum):
    """Types of performance bottlenecks."""

    CPU_BOUND = "cpu_bound"
    MEMORY_BOUND = "memory_bound"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    DEPENDENCY_WAIT = "dependency_wait"
    RESOURCE_CONTENTION = "resource_contention"
    ALGORITHMIC_COMPLEXITY = "algorithmic_complexity"


@dataclass
class PerformanceMetric:
    """Individual performance metric measurement."""

    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceProfile:
    """Performance profile for a workflow or component."""

    component_id: str
    component_type: str
    metrics: List[PerformanceMetric] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def add_metric(self, metric: PerformanceMetric) -> None:
        """Add a performance metric."""
        self.metrics.append(metric)

    def get_metrics_by_type(self, metric_type: PerformanceMetricType) -> List[PerformanceMetric]:
        """Get metrics of a specific type."""
        return [m for m in self.metrics if m.metric_type == metric_type]

    def get_average_metric(self, metric_type: PerformanceMetricType) -> Optional[float]:
        """Get average value for a metric type."""
        metrics = self.get_metrics_by_type(metric_type)
        if not metrics:
            return None
        return statistics.mean(m.value for m in metrics)


class BottleneckAnalysis(BaseModel):
    """Analysis of performance bottlenecks."""

    bottleneck_type: BottleneckType
    severity: float = Field(ge=0.0, le=1.0)
    component_id: str
    description: str
    impact_metrics: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    estimated_improvement: Optional[float] = None


class OptimizationRecommendation(BaseModel):
    """Optimization recommendation."""

    recommendation_id: str
    title: str
    description: str
    category: str
    priority: int = Field(ge=1, le=5)  # 1 = highest priority
    estimated_impact: float = Field(ge=0.0, le=1.0)
    implementation_effort: str  # "low", "medium", "high"
    affected_components: List[str] = Field(default_factory=list)
    implementation_steps: List[str] = Field(default_factory=list)


class ConfigurationValidationResult(BaseModel):
    """Result of configuration validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    performance_concerns: List[str] = Field(default_factory=list)
    dependency_issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class PerformanceProfiler:
    """Performance profiler for workflows and components.
    
    This class provides performance monitoring, bottleneck identification,
    and optimization recommendations.
    """

    def __init__(self):
        """Initialize the performance profiler."""
        self.profiles: Dict[str, PerformanceProfile] = {}
        self.active_profiles: Dict[str, PerformanceProfile] = {}
        self.bottleneck_analyzers: List[Callable] = []
        self.optimization_rules: List[Callable] = []

        # Initialize built-in analyzers
        self._initialize_analyzers()

        logger.info("PerformanceProfiler initialized")

    def _initialize_analyzers(self) -> None:
        """Initialize built-in performance analyzers."""
        self.bottleneck_analyzers.extend([
            self._analyze_execution_time_bottlenecks,
            self._analyze_memory_bottlenecks,
            self._analyze_throughput_bottlenecks
        ])

        self.optimization_rules.extend([
            self._recommend_parallel_execution,
            self._recommend_caching,
            self._recommend_resource_optimization
        ])

    def start_profiling(self, component_id: str, component_type: str) -> str:
        """Start profiling a component.
        
        Args:
            component_id: ID of the component to profile
            component_type: Type of component (workflow, primitive, etc.)
            
        Returns:
            Profile session ID

        """
        profile = PerformanceProfile(
            component_id=component_id,
            component_type=component_type
        )

        session_id = f"{component_id}_{int(time.time())}"
        self.active_profiles[session_id] = profile

        logger.info(f"Started profiling: {component_id} (session: {session_id})")
        return session_id

    def record_metric(
        self,
        session_id: str,
        metric_type: PerformanceMetricType,
        value: float,
        unit: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Record a performance metric.
        
        Args:
            session_id: Profile session ID
            metric_type: Type of metric
            value: Metric value
            unit: Unit of measurement
            context: Additional context information

        """
        if session_id not in self.active_profiles:
            logger.warning(f"Profile session not found: {session_id}")
            return

        metric = PerformanceMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            context=context or {}
        )

        self.active_profiles[session_id].add_metric(metric)

    def end_profiling(self, session_id: str) -> Optional[PerformanceProfile]:
        """End profiling session and return the profile.
        
        Args:
            session_id: Profile session ID
            
        Returns:
            Completed performance profile

        """
        if session_id not in self.active_profiles:
            logger.warning(f"Profile session not found: {session_id}")
            return None

        profile = self.active_profiles[session_id]
        profile.end_time = datetime.now()

        # Store completed profile
        self.profiles[session_id] = profile
        del self.active_profiles[session_id]

        logger.info(f"Ended profiling session: {session_id}")
        return profile

    def analyze_bottlenecks(self, session_id: str) -> List[BottleneckAnalysis]:
        """Analyze performance bottlenecks for a profile.
        
        Args:
            session_id: Profile session ID
            
        Returns:
            List of identified bottlenecks

        """
        if session_id not in self.profiles:
            logger.warning(f"Profile not found: {session_id}")
            return []

        profile = self.profiles[session_id]
        bottlenecks = []

        # Run all bottleneck analyzers
        for analyzer in self.bottleneck_analyzers:
            try:
                analyzer_bottlenecks = analyzer(profile)
                bottlenecks.extend(analyzer_bottlenecks)
            except Exception as e:
                logger.error(f"Bottleneck analyzer failed: {e}")

        # Sort by severity
        bottlenecks.sort(key=lambda x: x.severity, reverse=True)

        logger.info(f"Identified {len(bottlenecks)} bottlenecks for {session_id}")
        return bottlenecks

    def generate_optimization_recommendations(
        self,
        session_id: str,
        bottlenecks: List[BottleneckAnalysis] = None
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations.
        
        Args:
            session_id: Profile session ID
            bottlenecks: Optional list of bottlenecks (will analyze if not provided)
            
        Returns:
            List of optimization recommendations

        """
        if session_id not in self.profiles:
            logger.warning(f"Profile not found: {session_id}")
            return []

        profile = self.profiles[session_id]

        if bottlenecks is None:
            bottlenecks = self.analyze_bottlenecks(session_id)

        recommendations = []

        # Run optimization rules
        for rule in self.optimization_rules:
            try:
                rule_recommendations = rule(profile, bottlenecks)
                recommendations.extend(rule_recommendations)
            except Exception as e:
                logger.error(f"Optimization rule failed: {e}")

        # Sort by priority and impact
        recommendations.sort(key=lambda x: (x.priority, -x.estimated_impact))

        logger.info(f"Generated {len(recommendations)} optimization recommendations")
        return recommendations

    def _analyze_execution_time_bottlenecks(self, profile: PerformanceProfile) -> List[BottleneckAnalysis]:
        """Analyze execution time bottlenecks."""
        bottlenecks = []

        execution_metrics = profile.get_metrics_by_type(PerformanceMetricType.EXECUTION_TIME)
        if not execution_metrics:
            return bottlenecks

        # Calculate statistics
        times = [m.value for m in execution_metrics]
        avg_time = statistics.mean(times)
        max_time = max(times)

        # Check for slow execution
        if avg_time > 5.0:  # More than 5 seconds average
            severity = min(avg_time / 10.0, 1.0)
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type=BottleneckType.CPU_BOUND,
                severity=severity,
                component_id=profile.component_id,
                description=f"High average execution time: {avg_time:.2f}s",
                impact_metrics=["execution_time"],
                recommendations=[
                    "Consider parallel processing",
                    "Optimize algorithms",
                    "Add caching for repeated operations"
                ],
                estimated_improvement=0.3
            ))

        # Check for high variance
        if len(times) > 1:
            std_dev = statistics.stdev(times)
            if std_dev > avg_time * 0.5:  # High variance
                bottlenecks.append(BottleneckAnalysis(
                    bottleneck_type=BottleneckType.RESOURCE_CONTENTION,
                    severity=0.6,
                    component_id=profile.component_id,
                    description=f"High execution time variance: {std_dev:.2f}s",
                    impact_metrics=["execution_time"],
                    recommendations=[
                        "Investigate resource contention",
                        "Implement load balancing",
                        "Add resource pooling"
                    ],
                    estimated_improvement=0.2
                ))

        return bottlenecks

    def _analyze_memory_bottlenecks(self, profile: PerformanceProfile) -> List[BottleneckAnalysis]:
        """Analyze memory usage bottlenecks."""
        bottlenecks = []

        memory_metrics = profile.get_metrics_by_type(PerformanceMetricType.MEMORY_USAGE)
        if not memory_metrics:
            return bottlenecks

        # Check for high memory usage
        memory_values = [m.value for m in memory_metrics]
        max_memory = max(memory_values)
        avg_memory = statistics.mean(memory_values)

        if max_memory > 1000:  # More than 1GB
            severity = min(max_memory / 2000, 1.0)
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type=BottleneckType.MEMORY_BOUND,
                severity=severity,
                component_id=profile.component_id,
                description=f"High memory usage: {max_memory:.0f}MB",
                impact_metrics=["memory_usage"],
                recommendations=[
                    "Implement memory pooling",
                    "Add data streaming",
                    "Optimize data structures"
                ],
                estimated_improvement=0.4
            ))

        return bottlenecks

    def _analyze_throughput_bottlenecks(self, profile: PerformanceProfile) -> List[BottleneckAnalysis]:
        """Analyze throughput bottlenecks."""
        bottlenecks = []

        throughput_metrics = profile.get_metrics_by_type(PerformanceMetricType.THROUGHPUT)
        if not throughput_metrics:
            return bottlenecks

        # Check for low throughput
        throughput_values = [m.value for m in throughput_metrics]
        avg_throughput = statistics.mean(throughput_values)

        if avg_throughput < 10:  # Less than 10 operations per second
            severity = max(0.3, 1.0 - (avg_throughput / 10))
            bottlenecks.append(BottleneckAnalysis(
                bottleneck_type=BottleneckType.IO_BOUND,
                severity=severity,
                component_id=profile.component_id,
                description=f"Low throughput: {avg_throughput:.1f} ops/sec",
                impact_metrics=["throughput"],
                recommendations=[
                    "Implement batch processing",
                    "Add connection pooling",
                    "Optimize I/O operations"
                ],
                estimated_improvement=0.5
            ))

        return bottlenecks

    def _recommend_parallel_execution(
        self,
        profile: PerformanceProfile,
        bottlenecks: List[BottleneckAnalysis]
    ) -> List[OptimizationRecommendation]:
        """Recommend parallel execution optimizations."""
        recommendations = []

        # Check if CPU-bound bottlenecks exist
        cpu_bottlenecks = [b for b in bottlenecks if b.bottleneck_type == BottleneckType.CPU_BOUND]

        if cpu_bottlenecks and profile.component_type == "workflow":
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"parallel_{profile.component_id}",
                title="Implement Parallel Execution",
                description="Convert sequential operations to parallel execution to improve performance",
                category="parallelization",
                priority=2,
                estimated_impact=0.6,
                implementation_effort="medium",
                affected_components=[profile.component_id],
                implementation_steps=[
                    "Identify independent operations",
                    "Implement parallel execution patterns",
                    "Add synchronization mechanisms",
                    "Test parallel execution"
                ]
            ))

        return recommendations

    def _recommend_caching(
        self,
        profile: PerformanceProfile,
        bottlenecks: List[BottleneckAnalysis]
    ) -> List[OptimizationRecommendation]:
        """Recommend caching optimizations."""
        recommendations = []

        # Check execution time metrics for repeated operations
        execution_metrics = profile.get_metrics_by_type(PerformanceMetricType.EXECUTION_TIME)

        if len(execution_metrics) > 5:  # Multiple executions suggest caching opportunity
            avg_time = statistics.mean(m.value for m in execution_metrics)

            if avg_time > 1.0:  # Operations taking more than 1 second
                recommendations.append(OptimizationRecommendation(
                    recommendation_id=f"cache_{profile.component_id}",
                    title="Implement Result Caching",
                    description="Add caching for expensive operations to reduce execution time",
                    category="caching",
                    priority=1,
                    estimated_impact=0.7,
                    implementation_effort="low",
                    affected_components=[profile.component_id],
                    implementation_steps=[
                        "Identify cacheable operations",
                        "Implement cache layer",
                        "Add cache invalidation logic",
                        "Monitor cache hit rates"
                    ]
                ))

        return recommendations

    def _recommend_resource_optimization(
        self,
        profile: PerformanceProfile,
        bottlenecks: List[BottleneckAnalysis]
    ) -> List[OptimizationRecommendation]:
        """Recommend resource optimization."""
        recommendations = []

        # Check for memory bottlenecks
        memory_bottlenecks = [b for b in bottlenecks if b.bottleneck_type == BottleneckType.MEMORY_BOUND]

        if memory_bottlenecks:
            recommendations.append(OptimizationRecommendation(
                recommendation_id=f"memory_{profile.component_id}",
                title="Optimize Memory Usage",
                description="Reduce memory consumption through better data management",
                category="resource_optimization",
                priority=2,
                estimated_impact=0.4,
                implementation_effort="medium",
                affected_components=[profile.component_id],
                implementation_steps=[
                    "Profile memory usage patterns",
                    "Implement data streaming",
                    "Add memory pooling",
                    "Optimize data structures"
                ]
            ))

        return recommendations


class ConfigurationValidator:
    """Validator for workflow and component configurations.
    
    This class provides comprehensive validation of configurations,
    including dependency checking and performance impact analysis.
    """

    def __init__(self):
        """Initialize the configuration validator."""
        self.validation_rules: List[Callable] = []
        self.dependency_checkers: List[Callable] = []

        # Initialize built-in validators
        self._initialize_validators()

        logger.info("ConfigurationValidator initialized")

    def _initialize_validators(self) -> None:
        """Initialize built-in validation rules."""
        self.validation_rules.extend([
            self._validate_basic_structure,
            self._validate_parameter_types,
            self._validate_resource_limits,
            self._validate_performance_settings
        ])

        self.dependency_checkers.extend([
            self._check_service_dependencies,
            self._check_primitive_dependencies,
            self._check_circular_dependencies
        ])

    def validate_configuration(self, config: Dict[str, Any]) -> ConfigurationValidationResult:
        """Validate a configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Validation result

        """
        result = ConfigurationValidationResult(is_valid=True)

        # Run validation rules
        for rule in self.validation_rules:
            try:
                rule_result = rule(config)
                result.errors.extend(rule_result.get("errors", []))
                result.warnings.extend(rule_result.get("warnings", []))
                result.performance_concerns.extend(rule_result.get("performance_concerns", []))
            except Exception as e:
                logger.error(f"Validation rule failed: {e}")
                result.errors.append(f"Validation rule error: {str(e)}")

        # Run dependency checks
        for checker in self.dependency_checkers:
            try:
                checker_result = checker(config)
                result.dependency_issues.extend(checker_result.get("issues", []))
                result.warnings.extend(checker_result.get("warnings", []))
            except Exception as e:
                logger.error(f"Dependency checker failed: {e}")
                result.dependency_issues.append(f"Dependency check error: {str(e)}")

        # Determine overall validity
        result.is_valid = len(result.errors) == 0 and len(result.dependency_issues) == 0

        # Generate recommendations
        if result.warnings or result.performance_concerns:
            result.recommendations.extend(self._generate_validation_recommendations(result))

        return result

    def _validate_basic_structure(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate basic configuration structure."""
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["name", "version", "type"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Check field types
        if "name" in config and not isinstance(config["name"], str):
            errors.append("Field 'name' must be a string")

        if "version" in config and not isinstance(config["version"], str):
            errors.append("Field 'version' must be a string")

        # Check for deprecated fields
        deprecated_fields = ["legacy_mode", "old_api"]
        for field in deprecated_fields:
            if field in config:
                warnings.append(f"Deprecated field '{field}' should be removed")

        return {"errors": errors, "warnings": warnings}

    def _validate_parameter_types(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate parameter types and values."""
        errors = []
        warnings = []

        if "parameters" in config:
            parameters = config["parameters"]
            if not isinstance(parameters, dict):
                errors.append("Parameters must be a dictionary")
            else:
                for param_name, param_value in parameters.items():
                    # Check for common parameter validation
                    if param_name.endswith("_threshold") and isinstance(param_value, (int, float)):
                        if not (0.0 <= param_value <= 1.0):
                            warnings.append(f"Threshold parameter '{param_name}' should be between 0.0 and 1.0")

                    if param_name.endswith("_count") and isinstance(param_value, int):
                        if param_value < 0:
                            errors.append(f"Count parameter '{param_name}' must be non-negative")

        return {"errors": errors, "warnings": warnings}

    def _validate_resource_limits(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate resource limits and constraints."""
        errors = []
        warnings = []
        performance_concerns = []

        if "resources" in config:
            resources = config["resources"]

            # Check memory limits
            if "memory_limit" in resources:
                memory_limit = resources["memory_limit"]
                if isinstance(memory_limit, int) and memory_limit > 8192:  # 8GB
                    performance_concerns.append(f"High memory limit: {memory_limit}MB may cause performance issues")

            # Check CPU limits
            if "cpu_limit" in resources:
                cpu_limit = resources["cpu_limit"]
                if isinstance(cpu_limit, (int, float)) and cpu_limit > 4.0:
                    warnings.append(f"High CPU limit: {cpu_limit} cores may not be available")

            # Check timeout settings
            if "timeout" in resources:
                timeout = resources["timeout"]
                if isinstance(timeout, int) and timeout > 3600:  # 1 hour
                    warnings.append(f"Very long timeout: {timeout}s may cause resource exhaustion")

        return {"errors": errors, "warnings": warnings, "performance_concerns": performance_concerns}

    def _validate_performance_settings(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate performance-related settings."""
        errors = []
        warnings = []
        performance_concerns = []

        # Check parallel execution settings
        if "parallel_execution" in config:
            parallel_config = config["parallel_execution"]

            if "max_workers" in parallel_config:
                max_workers = parallel_config["max_workers"]
                if isinstance(max_workers, int):
                    if max_workers > 20:
                        performance_concerns.append(f"High worker count: {max_workers} may cause resource contention")
                    elif max_workers < 1:
                        errors.append("max_workers must be at least 1")

        # Check caching settings
        if "caching" in config:
            cache_config = config["caching"]

            if "cache_size" in cache_config:
                cache_size = cache_config["cache_size"]
                if isinstance(cache_size, int) and cache_size > 1000:
                    performance_concerns.append(f"Large cache size: {cache_size} may consume significant memory")

        return {"errors": errors, "warnings": warnings, "performance_concerns": performance_concerns}

    def _check_service_dependencies(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Check service dependencies."""
        issues = []
        warnings = []

        if "dependencies" in config:
            dependencies = config["dependencies"]

            if "services" in dependencies:
                services = dependencies["services"]

                # Check for common service dependencies
                required_services = ["llm_interface", "memory_service"]
                for service in required_services:
                    if service not in services:
                        warnings.append(f"Recommended service dependency missing: {service}")

                # Check for circular dependencies (simplified check)
                if len(services) > 10:
                    warnings.append("Large number of service dependencies may indicate design issues")

        return {"issues": issues, "warnings": warnings}

    def _check_primitive_dependencies(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Check primitive dependencies."""
        issues = []
        warnings = []

        if "primitives" in config:
            primitives = config["primitives"]

            # Check for unknown primitive types
            known_primitives = [
                "fact_extraction", "evidence_aggregation", "consensus_calculation",
                "synthesis", "validation", "generation"
            ]

            for primitive in primitives:
                if primitive not in known_primitives:
                    warnings.append(f"Unknown primitive type: {primitive}")

        return {"issues": issues, "warnings": warnings}

    def _check_circular_dependencies(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Check for circular dependencies."""
        issues = []
        warnings = []

        # Simplified circular dependency check
        if "workflow" in config and "nodes" in config["workflow"]:
            nodes = config["workflow"]["nodes"]
            edges = config["workflow"].get("edges", [])

            # Build adjacency list
            graph = {}
            for node in nodes:
                graph[node["id"]] = []

            for edge in edges:
                if edge["from"] in graph and edge["to"] in graph:
                    graph[edge["from"]].append(edge["to"])

            # Simple cycle detection (DFS-based)
            visited = set()
            rec_stack = set()

            def has_cycle(node):
                if node in rec_stack:
                    return True
                if node in visited:
                    return False

                visited.add(node)
                rec_stack.add(node)

                for neighbor in graph.get(node, []):
                    if has_cycle(neighbor):
                        return True

                rec_stack.remove(node)
                return False

            for node in graph:
                if node not in visited:
                    if has_cycle(node):
                        issues.append("Circular dependency detected in workflow")
                        break

        return {"issues": issues, "warnings": warnings}

    def _generate_validation_recommendations(self, result: ConfigurationValidationResult) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []

        if result.performance_concerns:
            recommendations.append("Consider performance testing with current configuration")
            recommendations.append("Monitor resource usage during execution")

        if result.warnings:
            recommendations.append("Review and address configuration warnings")

        if len(result.dependency_issues) == 0 and len(result.errors) == 0:
            recommendations.append("Configuration appears valid for deployment")

        return recommendations


class PerformanceOptimizationManager:
    """High-level manager for performance optimization.
    
    This class provides a unified interface for performance profiling,
    bottleneck analysis, and optimization recommendations.
    """

    def __init__(self):
        """Initialize the performance optimization manager."""
        self.profiler = PerformanceProfiler()
        self.validator = ConfigurationValidator()
        self.optimization_history: List[Dict[str, Any]] = []

        logger.info("PerformanceOptimizationManager initialized")

    def validate_and_optimize_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and provide optimization suggestions.
        
        Args:
            config: Configuration to validate and optimize
            
        Returns:
            Validation results and optimization suggestions

        """
        # Validate configuration
        validation_result = self.validator.validate_configuration(config)

        # Generate optimization suggestions based on configuration
        optimization_suggestions = self._generate_config_optimizations(config, validation_result)

        return {
            "validation": validation_result.dict(),
            "optimization_suggestions": optimization_suggestions,
            "timestamp": datetime.now().isoformat()
        }

    def _generate_config_optimizations(
        self,
        config: Dict[str, Any],
        validation_result: ConfigurationValidationResult
    ) -> List[Dict[str, Any]]:
        """Generate optimization suggestions based on configuration."""
        suggestions = []

        # Resource optimization suggestions
        if "resources" in config:
            resources = config["resources"]

            if "memory_limit" in resources and resources["memory_limit"] > 4096:
                suggestions.append({
                    "type": "resource_optimization",
                    "title": "Consider Memory Optimization",
                    "description": "High memory limit detected. Consider implementing memory streaming or data pagination.",
                    "priority": "medium"
                })

        # Parallel execution suggestions
        if "workflow" in config and "nodes" in config["workflow"]:
            node_count = len(config["workflow"]["nodes"])
            if node_count > 5:
                suggestions.append({
                    "type": "parallelization",
                    "title": "Enable Parallel Execution",
                    "description": f"Workflow has {node_count} nodes. Consider parallel execution for independent operations.",
                    "priority": "high"
                })

        # Caching suggestions
        if validation_result.performance_concerns:
            suggestions.append({
                "type": "caching",
                "title": "Implement Caching",
                "description": "Performance concerns detected. Consider adding caching for expensive operations.",
                "priority": "high"
            })

        return suggestions

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        return {
            "active_profiles": len(self.profiler.active_profiles),
            "completed_profiles": len(self.profiler.profiles),
            "optimization_history_count": len(self.optimization_history),
            "available_analyzers": len(self.profiler.bottleneck_analyzers),
            "available_rules": len(self.profiler.optimization_rules),
            "validation_rules": len(self.validator.validation_rules),
            "dependency_checkers": len(self.validator.dependency_checkers)
        }
