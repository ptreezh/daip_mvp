"""
Skill dependency management system with circular dependency detection and chaining support.
"""  # noqa: E501

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .base import SkillMetadata


class DependencyStatus(Enum):
    """Status of skill dependency validation."""

    VALID = "valid"
    MISSING_DEPENDENCY = "missing_dependency"
    CIRCULAR_DEPENDENCY = "circular_dependency"
    DISABLED_DEPENDENCY = "disabled_dependency"


@dataclass
class DependencyValidationResult:
    """Result of dependency validation."""

    status: DependencyStatus
    message: str
    execution_order: list[str] = None
    missing_dependencies: list[str] = None
    circular_path: list[str] = None

    def __post_init__(self):
        if self.execution_order is None:
            self.execution_order = []
        if self.missing_dependencies is None:
            self.missing_dependencies = []
        if self.circular_path is None:
            self.circular_path = []


class SkillDependencyGraph:
    """
    Manages skill dependencies and provides dependency resolution.

    Features:
    - Build dependency graph from skill metadata
    - Detect circular dependencies
    - Topological sort for execution order
    - Validate dependencies against registered skills
    """

    def __init__(self):
        """Initialize the dependency graph."""
        self._graph: dict[str, set[str]] = {}  # skill_name -> set of dependencies
        self._logger = logging.getLogger(__name__)

    def build_graph(self, skills_metadata: dict[str, SkillMetadata]) -> None:
        """
        Build the dependency graph from skill metadata.

        Args:
            skills_metadata: Dictionary mapping skill names to their metadata
        """
        self._graph.clear()

        for skill_name, metadata in skills_metadata.items():
            dependencies = (
                set(metadata.dependencies) if metadata.dependencies else set()
            )
            self._graph[skill_name] = dependencies

        self._logger.debug(f"Built dependency graph with {len(self._graph)} skills")

    def add_skill(self, skill_name: str, dependencies: list[str]) -> None:
        """
        Add a skill to the dependency graph.

        Args:
            skill_name: Name of the skill
            dependencies: List of skill names this skill depends on
        """
        self._graph[skill_name] = set(dependencies)
        self._logger.debug(
            f"Added skill '{skill_name}' with dependencies: {dependencies}"
        )

    def remove_skill(self, skill_name: str) -> None:
        """
        Remove a skill from the dependency graph.

        Args:
            skill_name: Name of the skill to remove
        """
        if skill_name in self._graph:
            del self._graph[skill_name]

            # Remove this skill from other skills' dependencies
            for deps in self._graph.values():
                deps.discard(skill_name)

            self._logger.debug(f"Removed skill '{skill_name}' from dependency graph")

    def get_dependencies(self, skill_name: str) -> set[str]:
        """
        Get the dependencies for a specific skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Set of skill names that this skill depends on
        """
        return self._graph.get(skill_name, set()).copy()

    def get_dependents(self, skill_name: str) -> set[str]:
        """
        Get all skills that depend on the specified skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Set of skill names that depend on this skill
        """
        dependents = set()
        for name, deps in self._graph.items():
            if skill_name in deps:
                dependents.add(name)
        return dependents

    def detect_circular_dependencies(self) -> list[list[str]]:
        """
        Detect circular dependencies in the graph.

        Returns:
            List of circular dependency paths
        """
        visited = set()
        recursion_stack = set()
        cycles = []

        def dfs(skill: str, path: list[str]) -> bool:
            """Depth-first search to detect cycles."""
            visited.add(skill)
            recursion_stack.add(skill)
            path.append(skill)

            for dependency in self._graph.get(skill, set()):
                if dependency not in visited:
                    if dfs(dependency, path):
                        return True
                elif dependency in recursion_stack:
                    # Found a cycle - extract the cycle path
                    cycle_start = path.index(dependency)
                    cycle = path[cycle_start:] + [dependency]
                    cycles.append(cycle)
                    return True

            path.pop()
            recursion_stack.remove(skill)
            return False

        for skill in self._graph:
            if skill not in visited:
                dfs(skill, [])

        return cycles

    def topological_sort(self) -> list[str]:
        """
        Perform topological sort on the dependency graph.

        Returns:
            List of skill names in execution order (dependencies first)
            Returns empty list if graph has circular dependencies
        """
        in_degree: dict[str, int] = dict.fromkeys(self._graph, 0)

        # Calculate in-degree for each node
        for skill, dependencies in self._graph.items():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[skill] += 1

        # Queue of nodes with no incoming edges
        queue = [skill for skill, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort queue for deterministic order
            queue.sort()
            skill = queue.pop(0)
            result.append(skill)

            # Decrease in-degree for dependents
            for dependent in self.get_dependents(skill):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check if topological sort includes all nodes
        if len(result) != len(self._graph):
            # There's a cycle
            return []

        return result

    def validate_dependencies(
        self,
        skills_metadata: dict[str, SkillMetadata],
        enabled_skills: Optional[set[str]] = None,
    ) -> DependencyValidationResult:
        """
        Validate all skill dependencies.

        Args:
            skills_metadata: Dictionary mapping skill names to their metadata
            enabled_skills: Set of enabled skill names (optional, checks all if None)

        Returns:
            DependencyValidationResult with validation status and details
        """
        # Build the dependency graph
        self.build_graph(skills_metadata)

        # Check for missing dependencies
        missing = []
        for skill_name, dependencies in self._graph.items():
            for dep in dependencies:
                if dep not in skills_metadata:
                    missing.append(f"{skill_name} -> {dep}")

        if missing:
            return DependencyValidationResult(
                status=DependencyStatus.MISSING_DEPENDENCY,
                message=f"Missing dependencies: {', '.join(missing)}",
                missing_dependencies=missing,
            )

        # Check for circular dependencies
        cycles = self.detect_circular_dependencies()
        if cycles:
            cycle_strs = [" -> ".join(cycle) for cycle in cycles]
            return DependencyValidationResult(
                status=DependencyStatus.CIRCULAR_DEPENDENCY,
                message=f"Circular dependencies detected: {'; '.join(cycle_strs)}",
                circular_path=cycles[0] if cycles else [],
            )

        # Check for disabled dependencies
        if enabled_skills is not None:
            disabled_deps = []
            for skill_name, dependencies in self._graph.items():
                for dep in dependencies:
                    if skill_name in enabled_skills and dep not in enabled_skills:
                        disabled_deps.append(f"{skill_name} -> {dep}")

            if disabled_deps:
                return DependencyValidationResult(
                    status=DependencyStatus.DISABLED_DEPENDENCY,
                    message=f"Dependencies on disabled skills: {', '.join(disabled_deps)}",  # noqa: E501
                    missing_dependencies=disabled_deps,
                )

        # All validations passed
        execution_order = self.topological_sort()
        return DependencyValidationResult(
            status=DependencyStatus.VALID,
            message="All dependencies are valid",
            execution_order=execution_order,
        )

    def get_execution_order(self, skill_name: str) -> list[str]:
        """
        Get the execution order for a skill and its dependencies.

        Args:
            skill_name: Name of the skill to execute

        Returns:
            List of skill names in execution order (dependencies first)
        """
        visited = set()
        order = []

        def visit(skill: str) -> None:
            """Visit a skill and its dependencies recursively."""
            if skill in visited:
                return

            visited.add(skill)

            # Visit dependencies first
            for dep in self._graph.get(skill, set()):
                visit(dep)

            order.append(skill)

        visit(skill_name)
        return order

    def can_execute(self, skill_name: str, enabled_skills: set[str]) -> bool:
        """
        Check if a skill can be executed given the set of enabled skills.

        Args:
            skill_name: Name of the skill to check
            enabled_skills: Set of enabled skill names

        Returns:
            True if all dependencies are enabled, False otherwise
        """
        if skill_name not in enabled_skills:
            return False

        for dep in self._graph.get(skill_name, set()):
            if dep not in enabled_skills:
                return False

        return True
