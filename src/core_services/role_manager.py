# -*- coding: utf-8 -*-
"""Manages the definitions and capabilities of different roles in the system."""

import logging
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

# Define the base directory for roles
ROLES_DIR = Path("roles")

@dataclass
class Role:
    """Represents a role definition."""

    id: str
    name: str
    description: str
    system_prompt: str
    capabilities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Role object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "capabilities": self.capabilities,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Creates a Role object from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            system_prompt=data["system_prompt"],
            capabilities=data.get("capabilities", []), # Ensure capabilities is a list, default to empty
        )


class RoleManager:
    """Loads, manages, and persists role definitions from individual JSON files."""

    def __init__(self, roles_directory: Path = ROLES_DIR):
        """Initializes the RoleManager by loading roles from JSON files in the specified directory.

        Args:
            roles_directory (Path): The path to the directory containing role JSON files.
        """
        self.roles_directory = roles_directory
        self._roles: Dict[str, Role] = {}
        self._load_roles()
        logging.info(f"RoleManager initialized. Roles directory: {self.roles_directory}")

    def _load_roles(self) -> None:
        """Loads all role definitions from the roles directory."""
        self._roles = {} # Clear existing roles
        self.roles_directory.mkdir(parents=True, exist_ok=True) # Ensure directory exists
        
        loaded_count = 0
        for role_file in self.roles_directory.glob("*.json"):
            try:
                with open(role_file, "r", encoding="utf-8") as f:
                    role_data = json.load(f)
                    role = Role.from_dict(role_data)
                    self._roles[role.id] = role
                    loaded_count += 1
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {role_file}: {e}")
            except KeyError as e:
                logging.error(f"Missing key in role file {role_file}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error loading role from {role_file}: {e}")
        logging.info(f"Successfully loaded {loaded_count} roles from {self.roles_directory}")

    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Retrieves a role by its ID. If not in memory, attempts to load from file."""
        if role_id not in self._roles:
            role_file = self.roles_directory / f"{role_id}.json"
            if role_file.exists():
                try:
                    with open(role_file, "r", encoding="utf-8") as f:
                        role_data = json.load(f)
                        role = Role.from_dict(role_data)
                        self._roles[role.id] = role # Add to in-memory cache
                        logging.info(f"Dynamically loaded role '{role_id}' from file.")
                        return role
                except (json.JSONDecodeError, KeyError, Exception) as e:
                    logging.error(f"Error loading role '{role_id}' from file {role_file}: {e}")
            else:
                logging.warning(f"Role file for '{role_id}' not found at {role_file}.")
        return self._roles.get(role_id)

    def list_roles(self) -> List[Role]:
        """Returns a list of all available roles (reloads from disk to ensure freshness)."""
        self._load_roles() # Ensure the in-memory cache is fresh
        return list(self._roles.values())

    def save_role(self, role: Role) -> bool:
        """Saves a role definition to a JSON file.

        Args:
            role (Role): The role object to save.

        Returns:
            bool: True if the role was saved successfully, False otherwise.
        """
        role_file = self.roles_directory / f"{role.id}.json"
        try:
            with open(role_file, "w", encoding="utf-8") as f:
                json.dump(role.to_dict(), f, indent=4, ensure_ascii=False)
            self._roles[role.id] = role # Update in-memory cache
            logging.info(f"Successfully saved role '{role.id}' to {role_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving role '{role.id}' to {role_file}: {e}")
            return False

    def delete_role(self, role_id: str) -> bool:
        """Deletes a role definition file and removes it from memory.

        Args:
            role_id (str): The ID of the role to delete.

        Returns:
            bool: True if the role was deleted successfully, False otherwise.
        """
        role_file = self.roles_directory / f"{role_id}.json"
        if role_file.exists():
            try:
                role_file.unlink()
                if role_id in self._roles:
                    del self._roles[role_id]
                logging.info(f"Successfully deleted role '{role_id}' and its file.")
                return True
            except Exception as e:
                logging.error(f"Error deleting role file {role_file}: {e}")
                return False
        else:
            logging.warning(f"Attempted to delete non-existent role file for '{role_id}'.")
            return False
