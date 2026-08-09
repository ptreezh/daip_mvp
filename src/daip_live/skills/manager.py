"""
Skill management system for the Skills layer.
"""

import asyncio
import importlib
import importlib.util
import logging
import os
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import requests

from ..skills.base import Skill, SkillInput, SkillMetadata, SkillOutput
from .cache import SkillCache
from .dependency import (
    DependencyValidationResult,
    SkillDependencyGraph,
)


class SkillManager:
    """Manages registration, discovery, and execution of skills."""

    def __init__(
        self,
        enable_cache: bool = True,
        cache_max_size: int = 100,
        cache_default_ttl: Optional[float] = None,
    ):
        """
        Initialize the SkillManager.

        Args:
            enable_cache: Whether to enable skill execution caching
            cache_max_size: Maximum number of cached entries
            cache_default_ttl: Default TTL for cached entries in seconds (None = no expiration)
        """  # noqa: E501
        self._skills: dict[str, Skill] = {}
        self._metadata: dict[str, SkillMetadata] = {}
        self._logger = logging.getLogger(__name__)

        # Initialize skill cache
        self._cache = SkillCache(
            max_size=cache_max_size, default_ttl=cache_default_ttl, enabled=enable_cache
        )

        # Initialize dependency graph
        self._dependency_graph = SkillDependencyGraph()

    def register_skill(self, skill: Skill) -> None:
        """
        Register a skill with the manager.

        Args:
            skill: The skill to register
        """
        name = skill.metadata.name
        if name in self._skills:
            raise ValueError(f"Skill with name '{name}' already registered")

        self._skills[name] = skill
        self._metadata[name] = skill.metadata

        # Add to dependency graph
        self._dependency_graph.add_skill(name, skill.metadata.dependencies or [])

    def unregister_skill(self, name: str) -> None:
        """
        Unregister a skill from the manager.

        Args:
            name: The name of the skill to unregister
        """
        if name in self._skills:
            del self._skills[name]
            del self._metadata[name]

            # Remove from dependency graph
            self._dependency_graph.remove_skill(name)

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a registered skill by name.

        Args:
            name: The name of the skill to retrieve

        Returns:
            The skill if found, None otherwise
        """
        return self._skills.get(name)

    def list_skills(self) -> list[str]:
        """
        List all registered skill names.

        Returns:
            List of skill names
        """
        return list(self._skills.keys())

    def get_metadata(self, name: str) -> Optional[SkillMetadata]:
        """
        Get metadata for a specific skill.

        Args:
            name: The name of the skill

        Returns:
            SkillMetadata if skill exists, None otherwise
        """
        return self._metadata.get(name)

    def find_skills_by_tag(self, tag: str) -> list[str]:
        """
        Find skills that have a specific tag.

        Args:
            tag: The tag to search for

        Returns:
            List of skill names that have the tag
        """
        matching_skills = []
        for name, metadata in self._metadata.items():
            if tag in metadata.tags:
                matching_skills.append(name)
        return matching_skills

    def execute(
        self,
        skill_name: str,
        input: SkillInput,
        use_cache: bool = True,
        cache_ttl: Optional[float] = None,
    ) -> SkillOutput:
        """
        Execute a skill with caching support.

        Args:
            skill_name: Name of the skill to execute
            input: Skill input data
            use_cache: Whether to use cached results if available
            cache_ttl: Optional override for cache TTL

        Returns:
            SkillOutput containing the result

        Raises:
            ValueError: If skill is not found or not enabled
        """
        skill = self.get_skill(skill_name)
        if skill is None:
            raise ValueError(f"Skill '{skill_name}' not found")

        if not skill.is_enabled:
            raise ValueError(f"Skill '{skill_name}' is disabled")

        # Check cache if enabled and requested
        if use_cache and self._cache.enabled:
            cached_output = self._cache.get(skill_name, input, ttl=cache_ttl)
            if cached_output is not None:
                self._logger.debug(f"Cache hit for skill '{skill_name}'")
                return cached_output

        # Execute the skill
        self._logger.debug(f"Executing skill '{skill_name}'")
        output = skill.execute(input)

        # Cache the result if caching is enabled
        if use_cache and self._cache.enabled:
            self._cache.put(skill_name, input, output, ttl=cache_ttl)

        return output

    def get_cache(self) -> SkillCache:
        """
        Get the skill cache instance.

        Returns:
            SkillCache instance
        """
        return self._cache

    def invalidate_skill_cache(
        self, skill_name: str, input: Optional[SkillInput] = None
    ) -> int:
        """
        Invalidate cached results for a specific skill.

        Args:
            skill_name: Name of the skill
            input: Specific input to invalidate (optional)

        Returns:
            Number of entries invalidated
        """
        return self._cache.invalidate(skill_name, input)

    def clear_all_cache(self) -> None:
        """Clear all cached skill execution results."""
        self._cache.clear()
        self._logger.info("All skill cache cleared")

    def cleanup_expired_cache(self) -> int:
        """
        Remove expired entries from the cache.

        Returns:
            Number of entries removed
        """
        removed = self._cache.cleanup_expired()
        if removed > 0:
            self._logger.info(f"Cleaned up {removed} expired cache entries")
        return removed

    # Dependency Management Methods

    def validate_dependencies(
        self, enabled_skills: Optional[set[str]] = None
    ) -> DependencyValidationResult:
        """
        Validate all skill dependencies.

        Args:
            enabled_skills: Set of enabled skill names (optional)

        Returns:
            DependencyValidationResult with validation status
        """
        if enabled_skills is None:
            enabled_skills = {
                name for name, skill in self._skills.items() if skill.is_enabled
            }

        return self._dependency_graph.validate_dependencies(
            self._metadata, enabled_skills
        )

    def get_dependency_graph(self) -> SkillDependencyGraph:
        """
        Get the dependency graph instance.

        Returns:
            SkillDependencyGraph instance
        """
        return self._dependency_graph

    def get_execution_order(self, skill_name: str) -> list[str]:
        """
        Get the execution order for a skill and its dependencies.

        Args:
            skill_name: Name of the skill to execute

        Returns:
            List of skill names in execution order (dependencies first)

        Raises:
            ValueError: If skill is not found
        """
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not found")

        return self._dependency_graph.get_execution_order(skill_name)

    def can_execute(self, skill_name: str) -> bool:
        """
        Check if a skill can be executed given current state.

        Args:
            skill_name: Name of the skill to check

        Returns:
            True if skill exists and all dependencies are enabled, False otherwise
        """
        skill = self.get_skill(skill_name)
        if skill is None or not skill.is_enabled:
            return False

        enabled_skills = {
            name for name, skill in self._skills.items() if skill.is_enabled
        }
        return self._dependency_graph.can_execute(skill_name, enabled_skills)

    def execute_chain(
        self,
        skill_name: str,
        input: SkillInput,
        stop_on_failure: bool = False,
        use_cache: bool = True,
        require_all_dependencies: bool = True,
    ) -> dict[str, SkillOutput]:
        """
        Execute a skill and its dependencies in the correct order.

        Args:
            skill_name: Name of the skill to execute
            input: Skill input data (passed to all skills in chain)
            stop_on_failure: If True, stops execution on first failure
            use_cache: Whether to use cached results
            require_all_dependencies: If True, raises error when dependencies are disabled/missing;
                                     If False, executes available skills only

        Returns:
            Dictionary mapping skill names to their outputs

        Raises:
            ValueError: If skill is not found or require_all_dependencies=True and skill cannot be executed
        """  # noqa: E501
        # Validate skill exists
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not found")

        # Check if all dependencies are available
        if require_all_dependencies and not self.can_execute(skill_name):
            raise ValueError(
                f"Skill '{skill_name}' cannot be executed (missing or disabled dependencies)"  # noqa: E501
            )

        # Get execution order
        execution_order = self._dependency_graph.get_execution_order(skill_name)

        # Execute each skill in order
        results: dict[str, SkillOutput] = {}
        failures: list[str] = []

        for name in execution_order:
            try:
                # Check if skill is enabled
                skill = self.get_skill(name)
                if not skill or not skill.is_enabled:
                    self._logger.warning(f"Skipping disabled skill in chain: {name}")
                    failures.append(name)
                    if stop_on_failure:
                        break
                    continue

                # Check if all dependencies were successful
                dependencies = self._dependency_graph.get_dependencies(name)
                dependencies_met = True
                for dep in dependencies:
                    if dep not in results:
                        # Dependency failed or was skipped
                        self._logger.warning(
                            f"Skipping skill '{name}' because dependency '{dep}' failed"
                        )
                        failures.append(name)
                        dependencies_met = False
                        break

                if not dependencies_met:
                    if stop_on_failure:
                        break
                    continue

                self._logger.debug(f"Executing skill in chain: {name}")
                output = self.execute(name, input, use_cache=use_cache)
                results[name] = output
            except Exception as e:
                self._logger.error(f"Failed to execute skill '{name}' in chain: {e}")
                failures.append(name)

                if stop_on_failure:
                    break

        if failures:
            self._logger.warning(
                f"Failed to execute skills in chain: {', '.join(failures)}"
            )

        return results

    def execute_chain_with_output_transform(
        self,
        skill_name: str,
        initial_input: SkillInput,
        output_transform=None,
        stop_on_failure: bool = False,
        use_cache: bool = True,
    ) -> dict[str, SkillOutput]:
        """
        Execute a skill chain where each skill's output becomes input for the next.

        Args:
            skill_name: Final skill to execute
            initial_input: Initial input for the chain
            output_transform: Optional function to transform output into next input
            stop_on_failure: If True, stops execution on first failure
            use_cache: Whether to use cached results

        Returns:
            Dictionary mapping skill names to their outputs
        """
        # Validate skill
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not found")

        if not self.can_execute(skill_name):
            raise ValueError(
                f"Skill '{skill_name}' cannot be executed (missing or disabled dependencies)"  # noqa: E501
            )

        # Get execution order
        execution_order = self._dependency_graph.get_execution_order(skill_name)

        # Execute each skill with transformed input
        results: dict[str, SkillOutput] = {}
        current_input = initial_input
        failures: list[str] = []

        for name in execution_order:
            try:
                self._logger.debug(f"Executing skill in chain with transform: {name}")
                output = self.execute(name, current_input, use_cache=use_cache)
                results[name] = output

                # Transform output into next input
                if output_transform is not None:
                    current_input = output_transform(output)
                else:
                    # Default: use output as next input's data
                    current_input = SkillInput(
                        data=output.result, context=output.metadata
                    )

            except Exception as e:
                self._logger.error(f"Failed to execute skill '{name}' in chain: {e}")
                failures.append(name)

                if stop_on_failure:
                    break

        if failures:
            self._logger.warning(
                f"Failed to execute skills in chain: {', '.join(failures)}"
            )

        return results

    def load_skills_from_directory(self, directory: str) -> int:
        """
        Dynamically load skills from a directory.

        Args:
            directory: The directory to load skills from

        Returns:
            Number of skills loaded
        """
        skills_loaded = 0

        if not os.path.exists(directory):
            self._logger.warning(f"Skills directory not found: {directory}")
            return skills_loaded

        # This is a simplified implementation
        # In a real system, you would need more sophisticated plugin loading
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    # Import the module
                    module_name = filename[:-3]  # Remove .py extension
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(directory, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for skill classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, Skill)
                            and attr != Skill
                        ):
                            # Try to instantiate the skill
                            try:
                                skill_instance = attr()
                                self.register_skill(skill_instance)
                                skills_loaded += 1
                                self._logger.info(
                                    f"Loaded skill: {skill_instance.metadata.name}"
                                )
                            except Exception as e:
                                self._logger.warning(
                                    f"Failed to instantiate skill from {filename}: {e}"
                                )
                                pass
                except Exception as e:
                    self._logger.warning(
                        f"Failed to import skill module {filename}: {e}"
                    )
                    pass

        return skills_loaded

    def download_and_install_skill(
        self, url: str, target_directory: str = None
    ) -> bool:
        """
        Download and install a skill from a URL.

        Args:
            url: The URL to download the skill from
            target_directory: The directory to install the skill to

        Returns:
            True if successful, False otherwise
        """
        if target_directory is None:
            target_directory = os.path.join("data", "skills")

        try:
            # Create target directory if it doesn't exist
            os.makedirs(target_directory, exist_ok=True)

            # Download the file
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_filename = tmp_file.name

            # If it's a zip file, extract it
            if url.endswith(".zip"):
                with zipfile.ZipFile(tmp_filename, "r") as zip_ref:
                    zip_ref.extractall(target_directory)
            else:
                # Save as a Python file
                filename = os.path.basename(url)
                target_path = os.path.join(target_directory, filename)
                os.rename(tmp_filename, target_path)

            # Load the skills from the directory
            loaded_count = self.load_skills_from_directory(target_directory)

            self._logger.info(
                f"Successfully downloaded and installed {loaded_count} skills from {url}"  # noqa: E501
            )
            return loaded_count > 0

        except Exception as e:
            self._logger.error(f"Failed to download and install skill from {url}: {e}")
            return False

    def load_claude_skills_from_directory(self, directory: str) -> int:
        """
        Load Claude Skills from a directory containing manifest.json and tools.json files.

        Args:
            directory: The directory containing Claude Skills

        Returns:
            Number of skills loaded
        """  # noqa: E501
        from .claude_skill_adapter import ClaudeSkillAdapterManager

        skills_loaded = 0
        skills_dir = Path(directory)

        if not skills_dir.exists():
            self._logger.warning(f"Skills directory not found: {directory}")
            return skills_loaded

        # Initialize Claude Skill Adapter Manager
        adapter_manager = ClaudeSkillAdapterManager(self)

        try:
            loaded_skills = asyncio.run(
                adapter_manager.load_claude_skills_from_directory(directory)
            )
            skills_loaded = len(loaded_skills)
            self._logger.info(
                f"Successfully loaded {skills_loaded} Claude skills from {directory}"
            )
        except Exception:
            # Handle case where asyncio.run is not appropriate
            # Create a simple manifest.json and tools.json parser
            skills_loaded = self._load_claude_skills_simple(directory)

        return skills_loaded

    def _load_claude_skills_simple(self, directory: str) -> int:
        """
        Simple loading of Claude Skills without async requirements.
        Supports both traditional (manifest.json/tools.json) and new (SKILL.md) formats.

        Args:
            directory: The directory containing Claude Skills

        Returns:
            Number of skills loaded
        """
        import json

        import yaml

        from .updated_claude_adapter import ClaudeSkillAdapter, ClaudeSkillDefinition

        skills_loaded = 0
        skills_dir = Path(directory)

        if not skills_dir.exists():
            self._logger.warning(f"Skills directory not found: {directory}")
            return skills_loaded

        # Iterate through each subdirectory in the skills directory
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                # Check for traditional format (manifest.json + tools.json)
                manifest_file = skill_dir / "manifest.json"
                tools_file = skill_dir / "tools.json"

                if manifest_file.exists() and tools_file.exists():
                    # Load traditional format
                    try:
                        # Load manifest and tools files
                        with open(manifest_file, encoding="utf-8") as f:
                            manifest_data = json.load(f)

                        with open(tools_file, encoding="utf-8") as f:
                            tools_data = json.load(f)

                        # Create Claude skill definition
                        skill_def = ClaudeSkillDefinition(
                            name=manifest_data.get("name", skill_dir.name),
                            version=manifest_data.get("version", "1.0"),
                            description=manifest_data.get(
                                "description", f"Skill from {skill_dir.name}"
                            ),
                            manifest_version=manifest_data.get(
                                "manifest_version", "1.0"
                            ),
                            author=manifest_data.get("author"),
                            api=manifest_data.get("api"),
                            tags=manifest_data.get("tags", []),
                            tools=tools_data.get("tools", []),
                        )

                        # Create Claude skill adapter
                        adapter = ClaudeSkillAdapter(
                            skill_name=skill_def.name,
                            manifest_data=manifest_data,
                            skill_manager=self,
                        )

                        # Register the adapter as a skill
                        self.register_skill(adapter)
                        skills_loaded += 1
                        self._logger.info(
                            f"Loaded Claude skill (traditional): {skill_def.name}"
                        )

                    except Exception as e:
                        self._logger.error(
                            f"Failed to load traditional Claude skill from {skill_dir}: {e}"  # noqa: E501
                        )
                        continue
                else:
                    # Check for new format (SKILL.md files)
                    skill_md_files = list(skill_dir.glob("SKILL.md"))
                    if not skill_md_files:
                        skill_md_files = list(
                            skill_dir.glob("*.md")
                        )  # Look for any markdown file

                    for skill_md in skill_md_files:
                        try:
                            # Read the SKILL.md file
                            with open(skill_md, encoding="utf-8") as f:
                                skill_content = f.read()

                            # Extract skill name from directory name or filename
                            skill_name = (
                                skill_dir.name
                                if skill_dir.name != skill_md.stem
                                else skill_md.stem
                            )
                            skill_name = f"{skill_name}_{skill_md.stem}".replace(
                                "SKILL", ""
                            ).strip("_")

                            # If there's YAML frontmatter, extract metadata
                            description = f"Skill from {skill_name}"
                            if skill_content.startswith("---"):
                                try:
                                    # Extract YAML frontmatter
                                    end_frontmatter = skill_content.find("---", 3)
                                    if end_frontmatter != -1:
                                        yaml_content = skill_content[
                                            3:end_frontmatter
                                        ].strip()
                                        frontmatter = yaml.safe_load(yaml_content)
                                        if frontmatter and isinstance(
                                            frontmatter, dict
                                        ):
                                            description = frontmatter.get(
                                                "description", description
                                            )
                                            skill_name = frontmatter.get(
                                                "name", skill_name
                                            )
                                except Exception:
                                    pass  # If YAML parsing fails, use default values

                            # Create Claude skill adapter for new format
                            adapter = ClaudeSkillAdapter(
                                skill_name=skill_name,
                                skill_content=skill_content,
                                skill_manager=self,
                            )

                            # Register the adapter as a skill
                            self.register_skill(adapter)
                            skills_loaded += 1
                            self._logger.info(
                                f"Loaded Claude skill (new format): {skill_name}"
                            )

                        except Exception as e:
                            self._logger.error(
                                f"Failed to load new format Claude skill from {skill_md}: {e}"  # noqa: E501
                            )
                            continue

        return skills_loaded
