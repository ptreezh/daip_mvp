"""
Role-Model Configuration Manager

Manages enhanced role configurations with model-specific settings.
"""

import glob
import logging
import os
from typing import Dict, List, Optional

import yaml
from pydantic import ValidationError

from daip_live.p4_role_manager_tools.role_model_config import (
    EnhancedRole, 
    RoleModelMapping, 
    RoleModelConfig
)
from daip_live.core.models import Role

log = logging.getLogger(__name__)


class RoleModelManager:
    """Manages enhanced role configurations with model support."""

    def __init__(self, roles_dir_path: str = "roles"):
        self._roles: Dict[str, EnhancedRole] = {}
        self._roles_dir_path = roles_dir_path
        self._load_roles_from_directory(roles_dir_path)

    def _load_roles_from_directory(self, dir_path: str):
        """Load enhanced roles from YAML files."""
        if not os.path.isdir(dir_path):
            log.warning(f"Roles directory not found at {dir_path}. No roles loaded.")
            return

        for extension in ["*.yaml", "*.yml"]:
            for file_path in glob.glob(os.path.join(dir_path, extension)):
                try:
                    with open(file_path, encoding='utf-8') as f:
                        role_data = yaml.safe_load(f)
                        if not isinstance(role_data, dict):
                            log.warning(f"Skipping {file_path}: content is not a dictionary.")
                            continue

                        role_name = os.path.splitext(os.path.basename(file_path))[0]
                        role_data["name"] = role_name

                        # Try to create EnhancedRole directly. If it fails, log a detailed error.
                        try:
                            role = EnhancedRole(**role_data)
                            self._roles[role.name] = role
                            log.info(f"Loaded enhanced role: {role.name} with {len(role.model_configs)} model configs")
                        except ValidationError as e:
                            # Provide a much more detailed error log to help users fix their YAML files.
                            error_details = e.errors()
                            log.warning(f"Skipping {file_path} due to validation error. Details: {error_details}")
                            continue

                except yaml.YAMLError as e:
                    log.warning(f"Skipping {file_path} due to YAML parsing error: {e}")
                except ValidationError as e:
                    log.warning(f"Skipping {file_path} due to validation error: {e}")
                except Exception as e:
                    log.warning(f"Skipping {file_path} due to unexpected error: {e}")

    def get_role_by_name(self, name: str) -> Optional[EnhancedRole]:
        """Get an enhanced role by name."""
        return self._roles.get(name)

    def list_roles(self) -> List[EnhancedRole]:
        """List all enhanced roles."""
        return list(self._roles.values())

    def get_role_model_mapping(self, role_name: str, use_debate_config: bool = True) -> Optional[RoleModelMapping]:
        """Get model mapping for a specific role."""
        role = self.get_role_by_name(role_name)
        if not role:
            return None
        
        return RoleModelMapping.from_role(role, use_debate_config)

    def get_debate_model_mappings(self, role_names: List[str]) -> List[RoleModelMapping]:
        """Get model mappings for multiple roles for debate purposes."""
        mappings = []
        for role_name in role_names:
            mapping = self.get_role_model_mapping(role_name, use_debate_config=True)
            if mapping:
                mappings.append(mapping)
        return mappings

    def create_role_model_config(
        self,
        role_name: str,
        model_name: str,
        provider: str,
        is_primary: bool = False,
        **kwargs
    ) -> bool:
        """Create or update a role's model configuration."""
        role = self.get_role_by_name(role_name)
        if not role:
            return False

        # Check if model config already exists
        existing_config = role.get_model_config_by_name(model_name)
        
        if existing_config:
            # Update existing config
            for key, value in kwargs.items():
                if hasattr(existing_config, key):
                    setattr(existing_config, key, value)
            existing_config.is_primary = is_primary
        else:
            # Create new config
            new_config = RoleModelConfig(
                model_name=model_name,
                provider=provider,
                is_primary=is_primary,
                **kwargs
            )
            role.model_configs.append(new_config)

        # If this is the primary, remove primary flag from others
        if is_primary:
            for config in role.model_configs:
                if config.model_name != model_name:
                    config.is_primary = False

        # Save to file
        return self._save_role_to_file(role)

    def _save_role_to_file(self, role: EnhancedRole) -> bool:
        """Save role configuration to YAML file."""
        try:
            file_path = os.path.join(self._roles_dir_path, f"{role.name}.yaml")
            
            # Convert to dict for YAML serialization
            role_dict = role.model_dump(exclude={'name'})
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(role_dict, f, default_flow_style=False, allow_unicode=True)
            
            log.info(f"Saved role {role.name} to {file_path}")
            return True
            
        except Exception as e:
            log.error(f"Failed to save role {role.name}: {e}")
            return False

    def create_sample_role_configs(self):
        """Create sample role configuration files with model settings."""
        sample_configs = {
            "researcher": {
                "persona": "You are a research assistant specializing in academic topics. You provide detailed, well-structured responses with citations and references when possible.",
                "tools": ["search_web", "read_document", "summarize_text"],
                "model_configs": [
                    {
                        "model_name": "gpt-4",
                        "provider": "openai",
                        "max_tokens": 4000,
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.0,
                        "is_primary": True
                    },
                    {
                        "model_name": "claude-3-sonnet",
                        "provider": "anthropic",
                        "max_tokens": 4000,
                        "temperature": 0.2,
                        "is_primary": False
                    }
                ],
                "debate_model_config": {
                    "model_name": "gpt-4",
                    "provider": "openai",
                    "max_tokens": 3000,
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1,
                    "is_primary": True
                }
            },
            "creative_writer": {
                "persona": "You are a creative writer with expertise in storytelling, poetry, and imaginative content. You provide engaging, creative responses with vivid descriptions.",
                "tools": ["write_document", "brainstorm_ideas", "edit_text"],
                "model_configs": [
                    {
                        "model_name": "claude-3-sonnet",
                        "provider": "anthropic",
                        "max_tokens": 4000,
                        "temperature": 0.9,
                        "top_p": 0.95,
                        "frequency_penalty": 0.1,
                        "presence_penalty": 0.1,
                        "is_primary": True
                    }
                ]
            },
            "analyst": {
                "persona": "You are a data analyst specializing in logical reasoning and critical thinking. You provide structured, analytical responses with clear reasoning.",
                "tools": ["analyze_data", "create_charts", "generate_report"],
                "model_configs": [
                    {
                        "model_name": "gpt-4",
                        "provider": "openai",
                        "max_tokens": 4000,
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "frequency_penalty": 0.2,
                        "presence_penalty": 0.1,
                        "is_primary": True
                    }
                ]
            }
        }

        # Ensure roles directory exists
        os.makedirs(self._roles_dir_path, exist_ok=True)

        # Create sample role files
        for role_name, config_data in sample_configs.items():
            file_path = os.path.join(self._roles_dir_path, f"{role_name}.yaml")
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                    log.info(f"Created sample role config: {role_name}")
                except Exception as e:
                    log.error(f"Failed to create sample role {role_name}: {e}")

    def list_available_models(self) -> List[str]:
        """List all unique model names across all roles."""
        models = set()
        for role in self._roles.values():
            for config in role.model_configs:
                models.add(config.model_name)
        return sorted(list(models))