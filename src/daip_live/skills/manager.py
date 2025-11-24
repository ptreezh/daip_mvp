"""
Skill management system for the Skills layer.
"""
import importlib
import importlib.util
import os
import requests
import tempfile
import zipfile
import logging
from typing import Dict, List, Optional, Type
from pathlib import Path
from ..skills.base import Skill, SkillMetadata


class SkillManager:
    """Manages registration, discovery, and execution of skills."""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
        self._metadata: Dict[str, SkillMetadata] = {}
        self._logger = logging.getLogger(__name__)
    
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
    
    def unregister_skill(self, name: str) -> None:
        """
        Unregister a skill from the manager.
        
        Args:
            name: The name of the skill to unregister
        """
        if name in self._skills:
            del self._skills[name]
            del self._metadata[name]
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Get a registered skill by name.
        
        Args:
            name: The name of the skill to retrieve
            
        Returns:
            The skill if found, None otherwise
        """
        return self._skills.get(name)
    
    def list_skills(self) -> List[str]:
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
    
    def find_skills_by_tag(self, tag: str) -> List[str]:
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
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    # Import the module
                    module_name = filename[:-3]  # Remove .py extension
                    spec = importlib.util.spec_from_file_location(
                        module_name, os.path.join(directory, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for skill classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Skill) and 
                            attr != Skill):
                            # Try to instantiate the skill
                            try:
                                skill_instance = attr()
                                self.register_skill(skill_instance)
                                skills_loaded += 1
                                self._logger.info(f"Loaded skill: {skill_instance.metadata.name}")
                            except Exception as e:
                                self._logger.warning(f"Failed to instantiate skill from {filename}: {e}")
                                pass
                except Exception as e:
                    self._logger.warning(f"Failed to import skill module {filename}: {e}")
                    pass
        
        return skills_loaded
    
    def download_and_install_skill(self, url: str, target_directory: str = None) -> bool:
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
            if url.endswith('.zip'):
                with zipfile.ZipFile(tmp_filename, 'r') as zip_ref:
                    zip_ref.extractall(target_directory)
            else:
                # Save as a Python file
                filename = os.path.basename(url)
                target_path = os.path.join(target_directory, filename)
                os.rename(tmp_filename, target_path)

            # Load the skills from the directory
            loaded_count = self.load_skills_from_directory(target_directory)

            self._logger.info(f"Successfully downloaded and installed {loaded_count} skills from {url}")
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
        """
        from .claude_skill_adapter import ClaudeSkillAdapterManager

        skills_loaded = 0
        skills_dir = Path(directory)

        if not skills_dir.exists():
            self._logger.warning(f"Skills directory not found: {directory}")
            return skills_loaded

        # Initialize Claude Skill Adapter Manager
        adapter_manager = ClaudeSkillAdapterManager(self)

        try:
            loaded_skills = asyncio.run(adapter_manager.load_claude_skills_from_directory(directory))
            skills_loaded = len(loaded_skills)
            self._logger.info(f"Successfully loaded {skills_loaded} Claude skills from {directory}")
        except Exception as e:
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
        from .updated_claude_adapter import ClaudeSkillDefinition, ClaudeSkillAdapter

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
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest_data = json.load(f)

                        with open(tools_file, 'r', encoding='utf-8') as f:
                            tools_data = json.load(f)

                        # Create Claude skill definition
                        skill_def = ClaudeSkillDefinition(
                            name=manifest_data.get("name", skill_dir.name),
                            version=manifest_data.get("version", "1.0"),
                            description=manifest_data.get("description", f"Skill from {skill_dir.name}"),
                            manifest_version=manifest_data.get("manifest_version", "1.0"),
                            author=manifest_data.get("author"),
                            api=manifest_data.get("api"),
                            tags=manifest_data.get("tags", []),
                            tools=tools_data.get("tools", [])
                        )

                        # Create Claude skill adapter
                        adapter = ClaudeSkillAdapter(
                            skill_name=skill_def.name,
                            manifest_data=manifest_data,
                            skill_manager=self
                        )

                        # Register the adapter as a skill
                        self.register_skill(adapter)
                        skills_loaded += 1
                        self._logger.info(f"Loaded Claude skill (traditional): {skill_def.name}")

                    except Exception as e:
                        self._logger.error(f"Failed to load traditional Claude skill from {skill_dir}: {e}")
                        continue
                else:
                    # Check for new format (SKILL.md files)
                    skill_md_files = list(skill_dir.glob("SKILL.md"))
                    if not skill_md_files:
                        skill_md_files = list(skill_dir.glob("*.md"))  # Look for any markdown file

                    for skill_md in skill_md_files:
                        try:
                            # Read the SKILL.md file
                            with open(skill_md, 'r', encoding='utf-8') as f:
                                skill_content = f.read()

                            # Extract skill name from directory name or filename
                            skill_name = skill_dir.name if skill_dir.name != skill_md.stem else skill_md.stem
                            skill_name = f"{skill_name}_{skill_md.stem}".replace("SKILL", "").strip("_")

                            # If there's YAML frontmatter, extract metadata
                            description = f"Skill from {skill_name}"
                            if skill_content.startswith("---"):
                                try:
                                    # Extract YAML frontmatter
                                    end_frontmatter = skill_content.find("---", 3)
                                    if end_frontmatter != -1:
                                        yaml_content = skill_content[3:end_frontmatter].strip()
                                        frontmatter = yaml.safe_load(yaml_content)
                                        if frontmatter and isinstance(frontmatter, dict):
                                            description = frontmatter.get("description", description)
                                            skill_name = frontmatter.get("name", skill_name)
                                except:
                                    pass  # If YAML parsing fails, use default values

                            # Create Claude skill adapter for new format
                            adapter = ClaudeSkillAdapter(
                                skill_name=skill_name,
                                skill_content=skill_content,
                                skill_manager=self
                            )

                            # Register the adapter as a skill
                            self.register_skill(adapter)
                            skills_loaded += 1
                            self._logger.info(f"Loaded Claude skill (new format): {skill_name}")

                        except Exception as e:
                            self._logger.error(f"Failed to load new format Claude skill from {skill_md}: {e}")
                            continue

        return skills_loaded