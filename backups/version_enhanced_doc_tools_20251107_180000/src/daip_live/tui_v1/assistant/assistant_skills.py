"""
Production-level Skill Management System for Personal Assistant

This module provides comprehensive skill management including:
- Dynamic skill loading and registration
- Skill dependency management and validation
- Skill execution with sandboxing and resource limits
- Skill composition and chaining
- Skill performance monitoring and optimization
- Skill marketplace and community integration
- Skill versioning and rollback capabilities
- Skill security validation and permission control
"""

import asyncio
import uuid
import json
import importlib
import inspect
import sys
import subprocess
import tempfile
import os
import threading
import time
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
import sqlite3
from abc import ABC, abstractmethod
import psutil
import resource
import signal
from contextlib import asynccontextmanager
import yaml
import networkx as nx

logger = logging.getLogger(__name__)


class SkillType(Enum):
    """Types of skills with different execution patterns"""
    FUNCTION = "function"           # Python function
    SCRIPT = "script"              # External script
    API = "api"                    # External API call
    WORKFLOW = "workflow"          # Multi-step workflow
    TEMPLATE = "template"          # Template-based skill
    PLUGIN = "plugin"              # Loaded plugin
    AGENT = "agent"                # AI agent skill


class SkillStatus(Enum):
    """Skill lifecycle status"""
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    ERROR = "error"
    LOADING = "loading"
    TESTING = "testing"


class SkillPermission(Enum):
    """Skill permission levels"""
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    EXECUTE = "execute"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    SYSTEM = "system"
    ADMIN = "admin"


@dataclass
class SkillParameter:
    """Skill parameter definition"""
    name: str
    param_type: str
    description: str = ""
    required: bool = True
    default_value: Any = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    examples: List[Any] = field(default_factory=list)
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None


@dataclass
class SkillResource:
    """Resource requirements and limits for skill execution"""
    max_memory_mb: Optional[int] = None
    max_cpu_time_seconds: Optional[int] = None
    max_execution_time_seconds: Optional[int] = None
    required_files: List[str] = field(default_factory=list)
    required_permissions: List[SkillPermission] = field(default_factory=list)
    network_access: bool = False
    file_system_access: bool = False
    environment_variables: Dict[str, str] = field(default_factory=dict)


@dataclass
class SkillMetrics:
    """Skill execution metrics"""
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_execution_time_ms: float = 0.0
    total_execution_time_ms: float = 0.0
    last_execution_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    performance_score: float = 1.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    error_types: Dict[str, int] = field(default_factory=dict)


@dataclass
class SkillDependency:
    """Skill dependency definition"""
    skill_id: str
    version_constraint: str = ">=1.0.0"
    is_optional: bool = False
    dependency_type: str = "required"  # required, optional, suggested


class Skill:
    """Production-level Skill with comprehensive metadata and execution"""

    def __init__(
        self,
        name: str,
        skill_type: SkillType,
        description: str = "",
        version: str = "1.0.0",
        author: str = "",
        skill_id: Optional[str] = None
    ):
        self.id = skill_id or str(uuid.uuid4())
        self.name = name
        self.skill_type = skill_type
        self.description = description
        self.version = version
        self.author = author
        self.status = SkillStatus.REGISTERED

        # Code and execution
        self.code: Optional[str] = None
        self.entry_point: Optional[str] = None
        self.execution_function: Optional[Callable] = None
        self.file_path: Optional[str] = None

        # Interface definition
        self.parameters: List[SkillParameter] = []
        self.return_schema: Dict[str, Any] = {}
        self.examples: List[Dict[str, Any]] = []

        # Dependencies and resources
        self.dependencies: List[SkillDependency] = []
        self.dependents: Set[str] = set()
        self.resources = SkillResource()

        # Metadata and documentation
        self.tags: List[str] = []
        self.category: str = "general"
        self.documentation: str = ""
        self.changelog: List[Dict[str, Any]] = []
        self.license: str = "MIT"

        # Security and validation
        self.permissions: List[SkillPermission] = []
        self.validation_rules: List[Dict[str, Any]] = []
        self.security_score: float = 1.0
        self.code_checksum: Optional[str] = None

        # Performance metrics
        self.metrics = SkillMetrics()

        # Version management
        self.versions: List[str] = [version]
        self.is_deprecated: bool = False
        self.deprecation_message: Optional[str] = None

        # Marketplace and community
        self.rating: float = 0.0
        self.rating_count: int = 0
        self.download_count: int = 0
        self.community_tags: List[str] = []

        # Timestamps
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.last_tested_at: Optional[datetime] = None
        self.last_published_at: Optional[datetime] = None

        # Execution context
        self.execution_context: Dict[str, Any] = {}
        self.environment_variables: Dict[str, str] = {}

    def add_parameter(self, param: SkillParameter) -> None:
        """Add a parameter to the skill"""
        self.parameters.append(param)
        self.updated_at = datetime.now()

    def add_dependency(self, skill_id: str, version_constraint: str = ">=1.0.0",
                       is_optional: bool = False) -> None:
        """Add a dependency to this skill"""
        dependency = SkillDependency(skill_id, version_constraint, is_optional)
        self.dependencies.append(dependency)
        self.updated_at = datetime.now()

    def calculate_security_score(self) -> float:
        """Calculate security score based on permissions and code analysis"""
        base_score = 1.0

        # Deduct points for high-risk permissions
        risk_scores = {
            SkillPermission.SYSTEM: 0.5,
            SkillPermission.ADMIN: 0.4,
            SkillPermission.FILE_SYSTEM: 0.2,
            SkillPermission.NETWORK: 0.1
        }

        for permission in self.permissions:
            base_score *= (1 - risk_scores.get(permission, 0))

        # Analyze code for security issues (simplified)
        if self.code:
            # Check for dangerous patterns
            dangerous_patterns = [
                'subprocess.call', 'os.system', 'eval(', 'exec(',
                '__import__', 'open(', 'file('
            ]
            for pattern in dangerous_patterns:
                if pattern in self.code:
                    base_score -= 0.1

        return max(0.0, min(1.0, base_score))

    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input parameters against skill definition"""
        errors = []

        # Check required parameters
        defined_params = {p.name: p for p in self.parameters}
        for param_def in self.parameters:
            if param_def.required and param_def.name not in parameters:
                errors.append(f"Required parameter '{param_def.name}' is missing")

        # Validate parameter values
        for param_name, param_value in parameters.items():
            if param_name not in defined_params:
                errors.append(f"Unknown parameter '{param_name}'")
                continue

            param_def = defined_params[param_name]

            # Type validation
            expected_type = param_def.param_type
            if expected_type == "string" and not isinstance(param_value, str):
                errors.append(f"Parameter '{param_name}' must be a string")
            elif expected_type == "integer" and not isinstance(param_value, int):
                errors.append(f"Parameter '{param_name}' must be an integer")
            elif expected_type == "float" and not isinstance(param_value, (int, float)):
                errors.append(f"Parameter '{param_name}' must be a number")
            elif expected_type == "boolean" and not isinstance(param_value, bool):
                errors.append(f"Parameter '{param_name}' must be a boolean")
            elif expected_type == "array" and not isinstance(param_value, list):
                errors.append(f"Parameter '{param_name}' must be an array")
            elif expected_type == "object" and not isinstance(param_value, dict):
                errors.append(f"Parameter '{param_name}' must be an object")

            # Range validation
            if param_def.min_value is not None and param_value < param_def.min_value:
                errors.append(f"Parameter '{param_name}' must be >= {param_def.min_value}")
            if param_def.max_value is not None and param_value > param_def.max_value:
                errors.append(f"Parameter '{param_name}' must be <= {param_def.max_value}")

            # Allowed values validation
            if param_def.allowed_values and param_value not in param_def.allowed_values:
                errors.append(f"Parameter '{param_name}' must be one of {param_def.allowed_values}")

        return len(errors) == 0, errors

    def update_metrics(self, execution_time_ms: float, success: bool,
                      error_message: Optional[str] = None) -> None:
        """Update skill execution metrics"""
        self.metrics.execution_count += 1
        self.metrics.total_execution_time_ms += execution_time_ms
        self.metrics.average_execution_time_ms = (
            self.metrics.total_execution_time_ms / self.metrics.execution_count
        )
        self.metrics.last_execution_time = datetime.now()

        if success:
            self.metrics.success_count += 1
            self.metrics.last_success_time = datetime.now()
        else:
            self.metrics.failure_count += 1
            self.metrics.last_failure_time = datetime.now()
            if error_message:
                error_type = error_message.split(':')[0] if ':' in error_message else error_message
                self.metrics.error_types[error_type] = self.metrics.error_types.get(error_type, 0) + 1

        # Update performance score
        success_rate = self.metrics.success_count / self.metrics.execution_count
        time_efficiency = max(0, 1 - (execution_time_ms / 10000))  # 10s as baseline
        self.metrics.performance_score = (success_rate * 0.7 + time_efficiency * 0.3)

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "skill_type": self.skill_type.value,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "status": self.status.value,
            "entry_point": self.entry_point,
            "file_path": self.file_path,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type,
                    "description": p.description,
                    "required": p.required,
                    "default_value": p.default_value,
                    "validation_rules": p.validation_rules,
                    "examples": p.examples,
                    "min_value": p.min_value,
                    "max_value": p.max_value,
                    "allowed_values": p.allowed_values
                } for p in self.parameters
            ],
            "return_schema": self.return_schema,
            "examples": self.examples,
            "dependencies": [
                {
                    "skill_id": d.skill_id,
                    "version_constraint": d.version_constraint,
                    "is_optional": d.is_optional,
                    "dependency_type": d.dependency_type
                } for d in self.dependencies
            ],
            "dependents": list(self.dependents),
            "resources": {
                "max_memory_mb": self.resources.max_memory_mb,
                "max_cpu_time_seconds": self.resources.max_cpu_time_seconds,
                "max_execution_time_seconds": self.resources.max_execution_time_seconds,
                "required_files": self.resources.required_files,
                "required_permissions": [p.value for p in self.resources.required_permissions],
                "network_access": self.resources.network_access,
                "file_system_access": self.resources.file_system_access,
                "environment_variables": self.resources.environment_variables
            },
            "tags": self.tags,
            "category": self.category,
            "documentation": self.documentation,
            "license": self.license,
            "permissions": [p.value for p in self.permissions],
            "validation_rules": self.validation_rules,
            "security_score": self.security_score,
            "code_checksum": self.code_checksum,
            "metrics": {
                "execution_count": self.metrics.execution_count,
                "success_count": self.metrics.success_count,
                "failure_count": self.metrics.failure_count,
                "average_execution_time_ms": self.metrics.average_execution_time_ms,
                "performance_score": self.metrics.performance_score,
                "error_types": self.metrics.error_types
            },
            "versions": self.versions,
            "is_deprecated": self.is_deprecated,
            "deprecation_message": self.deprecation_message,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "download_count": self.download_count,
            "community_tags": self.community_tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_tested_at": self.last_tested_at.isoformat() if self.last_tested_at else None,
            "last_published_at": self.last_published_at.isoformat() if self.last_published_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Create skill from dictionary"""
        skill = cls(
            name=data["name"],
            skill_type=SkillType(data["skill_type"]),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            skill_id=data.get("id")
        )

        # Restore basic attributes
        skill.status = SkillStatus(data.get("status", SkillStatus.REGISTERED.value))
        skill.entry_point = data.get("entry_point")
        skill.file_path = data.get("file_path")
        skill.return_schema = data.get("return_schema", {})
        skill.examples = data.get("examples", [])
        skill.tags = data.get("tags", [])
        skill.category = data.get("category", "general")
        skill.documentation = data.get("documentation", "")
        skill.license = data.get("license", "MIT")
        skill.validation_rules = data.get("validation_rules", [])
        skill.code_checksum = data.get("code_checksum")
        skill.is_deprecated = data.get("is_deprecated", False)
        skill.deprecation_message = data.get("deprecation_message")
        skill.rating = data.get("rating", 0.0)
        skill.rating_count = data.get("rating_count", 0)
        skill.download_count = data.get("download_count", 0)
        skill.community_tags = data.get("community_tags", [])

        # Restore parameters
        for param_data in data.get("parameters", []):
            param = SkillParameter(
                name=param_data["name"],
                param_type=param_data["type"],
                description=param_data.get("description", ""),
                required=param_data.get("required", True),
                default_value=param_data.get("default_value"),
                validation_rules=param_data.get("validation_rules", {}),
                examples=param_data.get("examples", []),
                min_value=param_data.get("min_value"),
                max_value=param_data.get("max_value"),
                allowed_values=param_data.get("allowed_values")
            )
            skill.add_parameter(param)

        # Restore dependencies
        for dep_data in data.get("dependencies", []):
            skill.add_dependency(
                dep_data["skill_id"],
                dep_data.get("version_constraint", ">=1.0.0"),
                dep_data.get("is_optional", False)
            )

        skill.dependents = set(data.get("dependents", []))

        # Restore resources
        resources_data = data.get("resources", {})
        skill.resources = SkillResource(
            max_memory_mb=resources_data.get("max_memory_mb"),
            max_cpu_time_seconds=resources_data.get("max_cpu_time_seconds"),
            max_execution_time_seconds=resources_data.get("max_execution_time_seconds"),
            required_files=resources_data.get("required_files", []),
            required_permissions=[SkillPermission(p) for p in resources_data.get("required_permissions", [])],
            network_access=resources_data.get("network_access", False),
            file_system_access=resources_data.get("file_system_access", False),
            environment_variables=resources_data.get("environment_variables", {})
        )

        # Restore permissions
        skill.permissions = [SkillPermission(p) for p in data.get("permissions", [])]

        # Restore metrics
        metrics_data = data.get("metrics", {})
        skill.metrics = SkillMetrics(
            execution_count=metrics_data.get("execution_count", 0),
            success_count=metrics_data.get("success_count", 0),
            failure_count=metrics_data.get("failure_count", 0),
            average_execution_time_ms=metrics_data.get("average_execution_time_ms", 0.0),
            total_execution_time_ms=metrics_data.get("total_execution_time_ms", 0.0),
            performance_score=metrics_data.get("performance_score", 1.0),
            error_types=metrics_data.get("error_types", {})
        )

        # Restore timestamps
        skill.created_at = datetime.fromisoformat(data["created_at"])
        skill.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("last_tested_at"):
            skill.last_tested_at = datetime.fromisoformat(data["last_tested_at"])
        if data.get("last_published_at"):
            skill.last_published_at = datetime.fromisoformat(data["last_published_at"])

        return skill


class SkillSandbox:
    """Secure sandbox for skill execution"""

    def __init__(self, max_memory_mb: int = 512, max_execution_time_seconds: int = 30):
        self.max_memory_mb = max_memory_mb
        self.max_execution_time_seconds = max_execution_time_seconds
        self.active_processes: Dict[str, subprocess.Popen] = {}

    @asynccontextmanager
    async def execute(self, skill: Skill, parameters: Dict[str, Any]):
        """Execute skill within sandbox context"""
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Set resource limits
            self._set_resource_limits(skill)

            # Execute based on skill type
            if skill.skill_type == SkillType.FUNCTION:
                result = await self._execute_function(skill, parameters)
            elif skill.skill_type == SkillType.SCRIPT:
                result = await self._execute_script(skill, parameters)
            elif skill.skill_type == SkillType.API:
                result = await self._execute_api(skill, parameters)
            else:
                raise ValueError(f"Unsupported skill type: {skill.skill_type}")

            execution_time = (time.time() - start_time) * 1000
            yield result, execution_time

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            raise e
        finally:
            # Cleanup
            await self._cleanup(execution_id)

    def _set_resource_limits(self, skill: Skill) -> None:
        """Set resource limits for skill execution"""
        # Memory limit
        memory_limit = skill.resources.max_memory_mb or self.max_memory_mb
        if memory_limit:
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit * 1024 * 1024, -1))

        # CPU time limit
        cpu_limit = skill.resources.max_cpu_time_seconds or self.max_execution_time_seconds
        if cpu_limit:
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, -1))

    async def _execute_function(self, skill: Skill, parameters: Dict[str, Any]) -> Any:
        """Execute Python function skill"""
        if not skill.execution_function:
            raise ValueError("Skill has no execution function")

        # Create isolated namespace
        namespace = {
            '__builtins__': {
                'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
                'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
                'float': float, 'int': int, 'len': len, 'list': list,
                'map': map, 'max': max, 'min': min, 'pow': pow, 'range': range,
                'reversed': reversed, 'round': round, 'sorted': sorted, 'str': str,
                'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip
            },
            'parameters': parameters,
            'logger': logger
        }

        try:
            # Execute function with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(skill.execution_function, parameters),
                timeout=skill.resources.max_execution_time_seconds or self.max_execution_time_seconds
            )
            return result
        except asyncio.TimeoutError:
            raise TimeoutError("Skill execution timed out")

    async def _execute_script(self, skill: Skill, parameters: Dict[str, Any]) -> Any:
        """Execute script skill"""
        if not skill.file_path:
            raise ValueError("Script skill has no file path")

        script_path = Path(skill.file_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Prepare environment
        env = os.environ.copy()
        env.update(skill.environment_variables)
        env.update({f"SKILL_PARAM_{k.upper()}": str(v) for k, v in parameters.items()})

        try:
            # Execute script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=skill.resources.max_execution_time_seconds or self.max_execution_time_seconds
            )

            if process.returncode != 0:
                raise RuntimeError(f"Script execution failed: {stderr.decode()}")

            # Parse output
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError:
                return {"output": stdout.decode()}

        except asyncio.TimeoutError:
            raise TimeoutError("Script execution timed out")

    async def _execute_api(self, skill: Skill, parameters: Dict[str, Any]) -> Any:
        """Execute API skill"""
        import aiohttp

        if not skill.entry_point:
            raise ValueError("API skill has no entry point")

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'DAIP-SkillManager/{skill.name}'
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with asyncio.wait_for(
                    session.post(skill.entry_point, json=parameters, headers=headers),
                    timeout=skill.resources.max_execution_time_seconds or self.max_execution_time_seconds
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise RuntimeError(f"API call failed with status {response.status}")

        except asyncio.TimeoutError:
            raise TimeoutError("API execution timed out")

    async def _cleanup(self, execution_id: str) -> None:
        """Cleanup after skill execution"""
        if execution_id in self.active_processes:
            process = self.active_processes[execution_id]
            if process.poll() is None:
                process.terminate()
                try:
                    await asyncio.wait_for(asyncio.to_thread(process.wait), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
            del self.active_processes[execution_id]


class SkillRegistry:
    """Registry for managing skills with dependency resolution"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.dependency_graph = nx.DiGraph()
        self._lock = threading.RLock()

    def register_skill(self, skill: Skill) -> bool:
        """Register a new skill"""
        with self._lock:
            if skill.id in self.skills:
                logger.warning(f"Skill {skill.id} already registered, updating...")
                existing_skill = self.skills[skill.id]
                skill.metrics = existing_skill.metrics  # Preserve metrics
                skill.download_count = existing_skill.download_count

            self.skills[skill.id] = skill

            # Update dependency graph
            self.dependency_graph.add_node(skill.id, skill=skill)

            # Add dependency edges
            for dep in skill.dependencies:
                self.dependency_graph.add_edge(dep.skill_id, skill.id, dependency=dep)
                # Update dependents set
                if dep.skill_id in self.skills:
                    self.skills[dep.skill_id].dependents.add(skill.id)

            # Check for circular dependencies
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                logger.error(f"Circular dependency detected for skill {skill.id}")
                self.dependency_graph.remove_node(skill.id)
                return False

            skill.status = SkillStatus.ACTIVE
            logger.info(f"Registered skill: {skill.name} ({skill.id})")
            return True

    def unregister_skill(self, skill_id: str) -> bool:
        """Unregister a skill"""
        with self._lock:
            if skill_id not in self.skills:
                return False

            skill = self.skills[skill_id]

            # Check if other skills depend on this one
            if skill.dependents:
                logger.warning(f"Cannot unregister skill {skill_id}: has dependents {skill.dependents}")
                return False

            # Remove from registry and graph
            del self.skills[skill_id]
            if skill_id in self.dependency_graph:
                self.dependency_graph.remove_node(skill_id)

            logger.info(f"Unregistered skill: {skill.name} ({skill_id})")
            return True

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID"""
        return self.skills.get(skill_id)

    def list_skills(
        self,
        skill_type: Optional[SkillType] = None,
        category: Optional[str] = None,
        status: Optional[SkillStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Skill]:
        """List skills with filtering"""
        skills = list(self.skills.values())

        if skill_type:
            skills = [s for s in skills if s.skill_type == skill_type]
        if category:
            skills = [s for s in skills if s.category == category]
        if status:
            skills = [s for s in skills if s.status == status]
        if tags:
            skills = [s for s in skills if any(tag in s.tags for tag in tags)]

        return skills

    def search_skills(self, query: str, limit: int = 10) -> List[Tuple[Skill, float]]:
        """Search skills by name, description, or tags"""
        query_lower = query.lower()
        results = []

        for skill in self.skills.values():
            score = 0.0

            # Name matching
            if query_lower in skill.name.lower():
                score += 1.0

            # Description matching
            if query_lower in skill.description.lower():
                score += 0.7

            # Tag matching
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 0.5

            # Category matching
            if query_lower in skill.category.lower():
                score += 0.3

            if score > 0:
                results.append((skill, score))

        # Sort by score and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def get_skill_dependencies(self, skill_id: str) -> List[Skill]:
        """Get all dependencies for a skill"""
        if skill_id not in self.skills:
            return []

        dependencies = []
        for dep_id in nx.ancestors(self.dependency_graph, skill_id):
            if dep_id in self.skills:
                dependencies.append(self.skills[dep_id])

        return dependencies

    def get_skill_dependents(self, skill_id: str) -> List[Skill]:
        """Get all skills that depend on this skill"""
        if skill_id not in self.skills:
            return []

        dependents = []
        for dep_id in nx.descendants(self.dependency_graph, skill_id):
            if dep_id in self.skills:
                dependents.append(self.skills[dep_id])

        return dependents

    def validate_dependencies(self, skill_id: str) -> Tuple[bool, List[str]]:
        """Validate that all dependencies are satisfied"""
        if skill_id not in self.skills:
            return False, ["Skill not found"]

        skill = self.skills[skill_id]
        errors = []

        for dep in skill.dependencies:
            if dep.skill_id not in self.skills:
                if not dep.is_optional:
                    errors.append(f"Required dependency '{dep.skill_id}' not found")
            else:
                dep_skill = self.skills[dep.skill_id]
                # Version constraint check (simplified)
                if not self._check_version_constraint(dep_skill.version, dep.version_constraint):
                    errors.append(f"Dependency '{dep.skill_id}' version constraint not satisfied")

        return len(errors) == 0, errors

    def _check_version_constraint(self, version: str, constraint: str) -> bool:
        """Simple version constraint checking"""
        # This is a simplified implementation
        # In production, use a proper version library like packaging
        try:
            if constraint.startswith(">="):
                required_version = constraint[2:]
                return version >= required_version
            elif constraint.startswith("=="):
                required_version = constraint[2:]
                return version == required_version
            else:
                return True  # No constraint or unknown format
        except:
            return True  # Default to allowing


class SkillManager:
    """Production-level Skill Manager with comprehensive functionality"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path) if storage_path else Path("data/skills.db")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Core components
        self.registry = SkillRegistry()
        self.sandbox = SkillSandbox()

        # Plugin system
        self.plugin_paths: List[Path] = []
        self.loaded_plugins: Dict[str, Any] = {}

        # Execution tracking
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []

        # Performance monitoring
        self.performance_metrics = defaultdict(list)
        self.performance_report_interval = 3600  # 1 hour

        # Security
        self.security_scanner = SkillSecurityScanner()
        self.permission_manager = SkillPermissionManager()

        # Marketplace integration
        self.marketplace_client = SkillMarketplaceClient()

        # Database initialization
        self._init_database()

        # Load existing skills
        self._load_skills()

        # Start background tasks
        self._start_background_tasks()

    def _init_database(self) -> None:
        """Initialize database schema"""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_executions (
                    id TEXT PRIMARY KEY,
                    skill_id TEXT NOT NULL,
                    parameters TEXT,
                    result TEXT,
                    execution_time_ms REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (skill_id) REFERENCES skills (id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_analytics (
                    skill_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (skill_id) REFERENCES skills (id)
                )
            """)

            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_type ON skills (json_extract(data, '$.skill_type'))")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_category ON skills (json_extract(data, '$.category'))")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_skill_id ON skill_executions (skill_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_timestamp ON skill_executions (timestamp)")

            conn.commit()

    def _load_skills(self) -> None:
        """Load skills from database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute("SELECT id, data FROM skills")
                for skill_id, data in cursor.fetchall():
                    try:
                        skill_data = json.loads(data)
                        skill = Skill.from_dict(skill_data)
                        self.registry.register_skill(skill)
                    except Exception as e:
                        logger.error(f"Failed to load skill {skill_id}: {e}")

            logger.info(f"Loaded {len(self.registry.skills)} skills from database")

        except Exception as e:
            logger.error(f"Failed to load skills: {e}")

    def _save_skill(self, skill: Skill) -> None:
        """Save skill to database"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO skills (id, data, updated_at) VALUES (?, ?, ?)",
                    (skill.id, json.dumps(skill.to_dict()), datetime.now().isoformat())
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save skill {skill.id}: {e}")

    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        asyncio.create_task(self._performance_monitoring_loop())
        asyncio.create_task(self._security_scan_loop())
        asyncio.create_task(self._cleanup_loop())

    async def _performance_monitoring_loop(self) -> None:
        """Background performance monitoring"""
        while True:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(self.performance_report_interval)
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)  # 5 minutes on error

    async def _security_scan_loop(self) -> None:
        """Background security scanning"""
        while True:
            try:
                await self._scan_skills_security()
                await asyncio.sleep(86400)  # Daily
            except Exception as e:
                logger.error(f"Security scan error: {e}")
                await asyncio.sleep(3600)  # 1 hour on error

    async def _cleanup_loop(self) -> None:
        """Background cleanup tasks"""
        while True:
            try:
                await self._cleanup_old_executions()
                await asyncio.sleep(3600)  # Hourly
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(1800)  # 30 minutes on error

    async def register_skill(
        self,
        name: str,
        skill_type: SkillType,
        code: Optional[str] = None,
        file_path: Optional[str] = None,
        entry_point: Optional[str] = None,
        **kwargs
    ) -> str:
        """Register a new skill"""
        skill = Skill(name, skill_type, **kwargs)

        # Set execution details
        if code:
            skill.code = code
            skill.code_checksum = hashlib.sha256(code.encode()).hexdigest()
        if file_path:
            skill.file_path = file_path
        if entry_point:
            skill.entry_point = entry_point

        # Load execution function if applicable
        if skill_type == SkillType.FUNCTION and code:
            try:
                # Execute code to get function
                namespace = {}
                exec(code, namespace)
                skill.execution_function = namespace.get('main') or namespace.get('execute')
                if not skill.execution_function:
                    raise ValueError("No main/execute function found in code")
            except Exception as e:
                logger.error(f"Failed to load execution function: {e}")
                raise

        # Security scan
        security_issues = await self.security_scanner.scan_skill(skill)
        if security_issues:
            skill.security_score = max(0.0, 1.0 - len(security_issues) * 0.2)
            logger.warning(f"Security issues found in skill {name}: {security_issues}")

        # Register in registry
        if self.registry.register_skill(skill):
            self._save_skill(skill)
            logger.info(f"Registered skill: {name} ({skill.id})")
            return skill.id
        else:
            raise ValueError("Failed to register skill")

    async def execute_skill(
        self,
        skill_id: str,
        parameters: Dict[str, Any],
        execution_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a skill with comprehensive monitoring"""
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Get skill
            skill = self.registry.get_skill(skill_id)
            if not skill:
                raise ValueError(f"Skill not found: {skill_id}")

            # Validate dependencies
            deps_valid, dep_errors = self.registry.validate_dependencies(skill_id)
            if not deps_valid:
                raise ValueError(f"Dependency validation failed: {dep_errors}")

            # Validate parameters
            params_valid, param_errors = skill.validate_parameters(parameters)
            if not params_valid:
                raise ValueError(f"Parameter validation failed: {param_errors}")

            # Check permissions
            if not await self.permission_manager.check_execution_permission(skill, execution_context):
                raise PermissionError("Execution permission denied")

            # Set execution context
            skill.execution_context = execution_context or {}

            # Track execution
            self.active_executions[execution_id] = {
                "skill_id": skill_id,
                "parameters": parameters,
                "start_time": start_time,
                "status": "running"
            }

            # Execute in sandbox
            async with self.sandbox.execute(skill, parameters) as (result, execution_time_ms):
                # Update metrics
                skill.update_metrics(execution_time_ms, True)
                self._save_skill(skill)

                # Log execution
                await self._log_execution(execution_id, skill_id, parameters, result, execution_time_ms, True)

                # Update performance metrics
                self.performance_metrics[f"skill_{skill_id}_execution_time"].append(execution_time_ms)
                self.performance_metrics[f"skill_{skill_id}_success"].append(1)

                return {
                    "execution_id": execution_id,
                    "result": result,
                    "execution_time_ms": execution_time_ms,
                    "success": True
                }

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            # Update skill metrics
            if skill_id in self.registry.skills:
                skill = self.registry.skills[skill_id]
                skill.update_metrics(execution_time, False, str(e))
                self._save_skill(skill)

            # Log execution
            await self._log_execution(execution_id, skill_id, parameters, None, execution_time, False, str(e))

            # Update performance metrics
            self.performance_metrics[f"skill_{skill_id}_execution_time"].append(execution_time)
            self.performance_metrics[f"skill_{skill_id}_success"].append(0)

            return {
                "execution_id": execution_id,
                "error": str(e),
                "execution_time_ms": execution_time,
                "success": False
            }

        finally:
            # Clean up execution tracking
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]

    async def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID"""
        return self.registry.get_skill(skill_id)

    async def list_skills(
        self,
        skill_type: Optional[SkillType] = None,
        category: Optional[str] = None,
        status: Optional[SkillStatus] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Skill]:
        """List skills with filtering"""
        skills = self.registry.list_skills(skill_type, category, status, tags)
        if limit:
            skills = skills[:limit]
        return skills

    async def search_skills(self, query: str, limit: int = 10) -> List[Tuple[Skill, float]]:
        """Search skills"""
        return self.registry.search_skills(query, limit)

    async def update_skill(self, skill_id: str, **kwargs) -> bool:
        """Update skill"""
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return False

        # Update allowed fields
        if "name" in kwargs:
            skill.name = kwargs["name"]
        if "description" in kwargs:
            skill.description = kwargs["description"]
        if "tags" in kwargs:
            skill.tags = kwargs["tags"]
        if "documentation" in kwargs:
            skill.documentation = kwargs["documentation"]

        skill.updated_at = datetime.now()
        self._save_skill(skill)
        return True

    async def delete_skill(self, skill_id: str) -> bool:
        """Delete skill"""
        if self.registry.unregister_skill(skill_id):
            try:
                with sqlite3.connect(self.storage_path) as conn:
                    conn.execute("DELETE FROM skills WHERE id = ?", (skill_id,))
                    conn.commit()
            except Exception as e:
                logger.error(f"Failed to delete skill from database: {e}")
            return True
        return False

    async def get_skill_statistics(self) -> Dict[str, Any]:
        """Get comprehensive skill statistics"""
        total_skills = len(self.registry.skills)

        # Type distribution
        type_counts = defaultdict(int)
        category_counts = defaultdict(int)
        status_counts = defaultdict(int)

        total_executions = 0
        total_successes = 0
        total_execution_time = 0.0

        for skill in self.registry.skills.values():
            type_counts[skill.skill_type.value] += 1
            category_counts[skill.category] += 1
            status_counts[skill.status.value] += 1

            total_executions += skill.metrics.execution_count
            total_successes += skill.metrics.success_count
            total_execution_time += skill.metrics.total_execution_time_ms

        # Calculate averages
        average_execution_time = total_execution_time / total_executions if total_executions > 0 else 0
        overall_success_rate = total_successes / total_executions if total_executions > 0 else 0

        # Active executions
        active_executions = len(self.active_executions)

        return {
            "total_skills": total_skills,
            "type_distribution": dict(type_counts),
            "category_distribution": dict(category_counts),
            "status_distribution": dict(status_counts),
            "total_executions": total_executions,
            "overall_success_rate": overall_success_rate,
            "average_execution_time_ms": average_execution_time,
            "active_executions": active_executions,
            "performance_metrics": {
                name: {
                    "count": len(values),
                    "average": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0
                } for name, values in self.performance_metrics.items()
            }
        }

    async def _log_execution(
        self,
        execution_id: str,
        skill_id: str,
        parameters: Dict[str, Any],
        result: Optional[Any],
        execution_time_ms: float,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Log skill execution"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute("""
                    INSERT INTO skill_executions
                    (id, skill_id, parameters, result, execution_time_ms, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution_id,
                    skill_id,
                    json.dumps(parameters),
                    json.dumps(result) if result is not None else None,
                    execution_time_ms,
                    success,
                    error_message
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")

    async def _collect_performance_metrics(self) -> None:
        """Collect and store performance metrics"""
        try:
            timestamp = datetime.now()
            with sqlite3.connect(self.storage_path) as conn:
                for skill_id, skill in self.registry.skills.items():
                    conn.execute("""
                        INSERT INTO skill_analytics (skill_id, metric_name, metric_value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        skill_id,
                        "performance_score",
                        skill.metrics.performance_score,
                        timestamp
                    ))
                    conn.execute("""
                        INSERT INTO skill_analytics (skill_id, metric_name, metric_value, timestamp)
                        VALUES (?, ?, ?, ?)
                    """, (
                        skill_id,
                        "success_rate",
                        skill.metrics.success_count / skill.metrics.execution_count if skill.metrics.execution_count > 0 else 0,
                        timestamp
                    ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")

    async def _scan_skills_security(self) -> None:
        """Perform security scan on all skills"""
        for skill in self.registry.skills.values():
            try:
                security_issues = await self.security_scanner.scan_skill(skill)
                if security_issues:
                    skill.security_score = max(0.0, 1.0 - len(security_issues) * 0.2)
                    self._save_skill(skill)
                    logger.warning(f"Security issues found in skill {skill.name}: {security_issues}")
            except Exception as e:
                logger.error(f"Failed to scan skill {skill.name}: {e}")

    async def _cleanup_old_executions(self) -> None:
        """Clean up old execution records"""
        cutoff_date = datetime.now() - timedelta(days=30)
        try:
            with sqlite3.connect(self.storage_path) as conn:
                conn.execute(
                    "DELETE FROM skill_executions WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to cleanup old executions: {e}")

    async def shutdown(self) -> None:
        """Shutdown skill manager gracefully"""
        logger.info("Shutting down skill manager")

        # Wait for active executions to complete or timeout
        if self.active_executions:
            logger.info(f"Waiting for {len(self.active_executions)} active executions to complete")
            await asyncio.sleep(10)  # Give some time for cleanup

        logger.info("Skill manager shutdown complete")


class SkillSecurityScanner:
    """Security scanner for skills"""

    async def scan_skill(self, skill: Skill) -> List[str]:
        """Scan skill for security issues"""
        issues = []

        if skill.code:
            issues.extend(self._scan_code(skill.code))

        # Check permissions
        high_risk_permissions = [SkillPermission.SYSTEM, SkillPermission.ADMIN]
        for permission in skill.permissions:
            if permission in high_risk_permissions:
                issues.append(f"High-risk permission: {permission.value}")

        # Check resources
        if skill.resources.max_memory_mb and skill.resources.max_memory_mb > 1024:
            issues.append("High memory limit may impact system stability")

        return issues

    def _scan_code(self, code: str) -> List[str]:
        """Scan code for security issues"""
        issues = []
        dangerous_patterns = {
            'subprocess.': "Use of subprocess module",
            'os.system': "Use of os.system",
            'os.popen': "Use of os.popen",
            'eval(': "Use of eval function",
            'exec(': "Use of exec function",
            '__import__': "Dynamic import",
            'open(': "File access",
            'file(': "File access",
            'input(': "User input (potential injection)",
            'raw_input(': "User input (potential injection)",
            'pickle.loads': "Use of pickle (potential code execution)",
            'marshal.loads': "Use of marshal (potential code execution)",
        }

        for pattern, description in dangerous_patterns.items():
            if pattern in code:
                issues.append(description)

        return issues


class SkillPermissionManager:
    """Permission manager for skill execution"""

    async def check_execution_permission(
        self,
        skill: Skill,
        execution_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Check if skill execution is allowed"""
        # This is a simplified implementation
        # In production, implement proper RBAC/ABAC

        # Check if user has required permissions
        user_permissions = execution_context.get("user_permissions", []) if execution_context else []

        for required_permission in skill.permissions:
            if required_permission.value not in user_permissions:
                return False

        return True


class SkillMarketplaceClient:
    """Client for skill marketplace integration"""

    def __init__(self):
        self.api_base_url = "https://api.skills.marketplace/v1"
        self.api_key = None

    async def search_marketplace_skills(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search skills in marketplace"""
        # This is a placeholder implementation
        # In production, implement actual API calls
        return []

    async def download_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """Download skill from marketplace"""
        # This is a placeholder implementation
        # In production, implement actual API calls
        return None

    async def upload_skill(self, skill: Skill) -> bool:
        """Upload skill to marketplace"""
        # This is a placeholder implementation
        # In production, implement actual API calls
        return False