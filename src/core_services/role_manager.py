"""Manages the definitions and capabilities of different roles in the system."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import yaml


@dataclass
class Role:
    """Represents a role definition."""

    id: str
    name: str
    description: str
    system_prompt: str
    capabilities: List[str]


class RoleManager:
    """Loads and provides access to role definitions from a configuration file."""

    def __init__(self, config_path: str = "configs/roles.yaml"):
        """Initializes the RoleManager by loading roles from a YAML file.

        Args:
            config_path (str): The path to the role configuration file.
        """
        self._roles: Dict[str, Role] = {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                roles_data = yaml.safe_load(f)
                if not roles_data:
                    logging.warning(f"Role configuration file is empty: {config_path}")
                    return

                for role_dict in roles_data:
                    role = Role(**role_dict)
                    self._roles[role.id] = role
            logging.info(f"Successfully loaded {len(self._roles)} roles from {config_path}")
        except FileNotFoundError:
            logging.error(f"Role configuration file not found at: {config_path}")
        except (yaml.YAMLError, TypeError, KeyError) as e:
            logging.error(f"Error parsing role configuration file {config_path}: {e}")

    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Retrieves a role by its ID."""
        return self._roles.get(role_id)

    def list_roles(self) -> List[Role]:
        """Returns a list of all available roles."""
        return list(self._roles.values())
