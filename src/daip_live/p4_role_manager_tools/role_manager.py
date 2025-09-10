import glob
import logging
import os
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from src.daip_live.core.models import Role

log = logging.getLogger(__name__)


class RoleManager:
    """Manages the available AI agent roles and their personas."""

    def __init__(self, roles_dir_path: str = "roles"):
        self._roles: Dict[str, Role] = {}
        self._load_roles_from_directory(roles_dir_path)

    def _load_roles_from_directory(self, dir_path: str):
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

                        role = Role(**role_data)
                        self._roles[role.name] = role

                except yaml.YAMLError as e:
                    log.warning(f"Skipping {file_path} due to YAML parsing error: {e}")
                except ValidationError as e:
                    log.warning(f"Skipping {file_path} due to validation error: {e}")
                except Exception as e:
                    log.warning(f"Skipping {file_path} due to unexpected error: {e}")

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Retrieves a role by its unique name."""
        return self._roles.get(name)

    def list_roles(self) -> list[Role]:
        """Returns a list of all available roles."""
        return list(self._roles.values())
