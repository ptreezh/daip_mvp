import glob
import logging
import os
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from daip_live.core.models import Role

log = logging.getLogger(__name__)


class RoleManager:
    """Manages the available AI agent roles and their personas."""

    def __init__(self, roles_dir_path: str = None):
        # If no path is provided, try to get it from the configuration
        if roles_dir_path is None:
            try:
                from daip_live.config_bridge import config_bridge
                config_data = config_bridge.get_config_data()
                roles_dir_path = config_data.get('role_manager', {}).get('roles_dir', 'roles')
            except Exception:
                # Fallback to default if config is not available
                roles_dir_path = 'roles'

        self._roles: Dict[str, Role] = {}
        self._roles_dir_path = self._resolve_roles_path(roles_dir_path)
        self._load_roles_from_directory(self._roles_dir_path)

    def _resolve_roles_path(self, roles_dir_path: str) -> str:
        """Resolve the roles directory path with multiple fallback strategies."""
        import os
        from pathlib import Path

        # First try our advanced path resolver utility
        try:
            from daip_live.utils.path_resolver import get_configured_roles_path
            return str(get_configured_roles_path(roles_dir_path))
        except ImportError:
            # If the utility module is not available, fall back to the original logic
            pass

        # Strategy 1: If it's already an absolute path
        if os.path.isabs(roles_dir_path) and os.path.exists(roles_dir_path):
            return roles_dir_path

        # Strategy 2: Check relative to current working directory
        current_path = Path(roles_dir_path)
        if current_path.exists():
            return str(current_path.resolve())

        # Strategy 3: Check relative to project root
        possible_roots = [
            Path(__file__).parent.parent.parent.parent,  # Project root (4 levels up)
            Path(__file__).parent.parent.parent,         # src/daip_live (3 levels up)
            Path.cwd(),                                  # Current working directory
        ]

        for root_path in possible_roots:
            try:
                abs_roles_path = root_path / roles_dir_path
                if abs_roles_path.exists() and abs_roles_path.is_dir():
                    return str(abs_roles_path.resolve())
            except:
                continue

        # Strategy 4: Search for roles directory in common locations
        search_paths = [
            Path.cwd() / "roles",
            Path.cwd() / "src" / "daip_live" / "roles",
            Path(__file__).parent.parent / "roles",  # Relative to current file
        ]

        for search_path in search_paths:
            if search_path.exists():
                return str(search_path.resolve())

        # If nothing found, return the original path (it will be created if needed)
        return roles_dir_path

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
        # 如果直接找不到角色，先尝试加载一次
        if name not in self._roles:
            # 尝试重新加载角色
            try:
                # 确保使用绝对路径或相对于当前工作目录的路径
                role_file_path = os.path.join(self._get_roles_dir_path(), f'{name}.yaml')
                if os.path.exists(role_file_path):
                    # 从文件加载缺失的角色
                    with open(role_file_path, encoding='utf-8') as f:
                        role_data = yaml.safe_load(f)
                        if isinstance(role_data, dict):
                            role_data["name"] = name
                            role = Role(**role_data)
                            self._roles[role.name] = role
                            return role
            except Exception as e:
                log.warning(f"Failed to load role {name} from file: {e}")

            # 如果文件不存在或加载失败，创建一个默认角色
            from daip_live.core.models import Role
            log.warning(f"Role '{name}' not found, creating a temporary role with default configuration.")
            default_role = Role(
                name=name,
                persona=f"Default persona for {name}. You are an AI assistant playing this role.",
                tools=[],
                model_configs=[
                    {
                        "model_name": "gpt-3.5-turbo",
                        "provider": "openai",
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "frequency_penalty": 0.1,
                        "presence_penalty": 0.2,
                        "is_primary": True
                    }
                ]
            )
            self._roles[name] = default_role
            return default_role

        return self._roles.get(name)

    def _get_roles_dir_path(self):
        """获取角色目录路径，处理相对路径"""
        if os.path.isabs(self._roles_dir_path):
            return self._roles_dir_path
        else:
            # 如果是相对路径，相对于项目根目录
            import os
            # 尝试找到项目根目录（包含roles目录的那个目录）
            current_dir = os.getcwd()
            roles_path = os.path.join(current_dir, self._roles_dir_path)

            # 如果当前目录下有这个路径，使用它
            if os.path.exists(roles_path):
                return roles_path

            # 否则尝试其他可能的位置
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            fallback_path = os.path.join(root_dir, self._roles_dir_path)
            if os.path.exists(fallback_path):
                return fallback_path

            # 如果都找不到，返回相对于当前工作目录的路径
            return roles_path

    def list_roles(self) -> list[Role]:
        """Returns a list of all available roles."""
        return list(self._roles.values())
