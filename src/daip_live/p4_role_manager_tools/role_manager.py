import glob
import logging
import os
from typing import Optional

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
                roles_dir_path = config_data.get("role_manager", {}).get(
                    "roles_dir", "roles"
                )
            except Exception:
                # Fallback to default if config is not available
                roles_dir_path = "roles"

        self._roles: dict[str, Role] = {}
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
            Path(__file__).parent.parent.parent,  # src/daip_live (3 levels up)
            Path.cwd(),  # Current working directory
        ]

        for root_path in possible_roots:
            try:
                abs_roles_path = root_path / roles_dir_path
                if abs_roles_path.exists() and abs_roles_path.is_dir():
                    return str(abs_roles_path.resolve())
            except Exception:
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
                    with open(file_path, encoding="utf-8") as f:
                        role_data = yaml.safe_load(f)
                        if not isinstance(role_data, dict):
                            log.warning(
                                f"Skipping {file_path}: content is not a dictionary."
                            )
                            continue

                        role_name = os.path.splitext(os.path.basename(file_path))[0]
                        role_data["name"] = role_name

                        # 从 model_configs 提取真实模型名（is_primary 优先）
                        role_data["model"] = self._extract_model(role_data)

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
        # 如果直接找不到角色，尝试从文件加载一次
        if name not in self._roles:
            try:
                role_file_path = os.path.join(
                    self._get_roles_dir_path(), f"{name}.yaml"
                )
                if os.path.exists(role_file_path):
                    with open(role_file_path, encoding="utf-8") as f:
                        role_data = yaml.safe_load(f)
                        if isinstance(role_data, dict):
                            role_data["name"] = name
                            role_data["model"] = self._extract_model(role_data)
                            role = Role(**role_data)
                            self._roles[role.name] = role
                            return role
            except Exception as e:
                log.warning(f"Failed to load role {name} from file: {e}")

            # 文件不存在：返回 None，绝不静默创建默认角色（生产交付要求：
            # 假角色会掩盖 role delete 等命令的真实行为）
            return None

        return self._roles.get(name)

    def create_role(
        self, name: str, persona: str, tools: list[str] | None = None
    ) -> Role:
        """创建角色并写入 roles 目录 yaml 文件（真实持久化）。

        Args:
            name: 角色名（作为文件名，需为合法文件名）
            persona: 角色人格描述
            tools: 角色可用工具列表

        Returns:
            Role: 创建的角色对象

        Raises:
            ValueError: 角色已存在或参数非法
        """
        import re

        tools = tools or []
        if not name or not name.strip():
            raise ValueError("Role name cannot be empty")
        if not re.match(r"^[\w\-]+$", name):
            raise ValueError(
                f"Invalid role name '{name}': only letters, digits, underscore, dash allowed"  # noqa: E501
            )

        roles_dir = self._get_roles_dir_path()
        os.makedirs(roles_dir, exist_ok=True)

        role_file = os.path.join(roles_dir, f"{name}.yaml")
        if os.path.exists(role_file):
            raise ValueError(f"Role '{name}' already exists")

        role = Role(name=name, persona=persona, tools=tools)
        role_data = {"persona": persona, "tools": tools}
        with open(role_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(role_data, f, allow_unicode=True, sort_keys=False)

        self._roles[name] = role
        log.info(f"Role '{name}' created at {role_file}")
        return role

    def delete_role(self, name: str) -> bool:
        """删除角色及其 yaml 文件。

        Args:
            name: 角色名

        Returns:
            bool: 是否成功删除（角色不存在返回 False）
        """
        roles_dir = self._get_roles_dir_path()
        role_file = os.path.join(roles_dir, f"{name}.yaml")
        if not os.path.exists(role_file):
            log.warning(f"Role '{name}' file not found at {role_file}")
            return False

        try:
            os.remove(role_file)
            self._roles.pop(name, None)
            log.info(f"Role '{name}' deleted")
            return True
        except OSError as e:
            log.error(f"Failed to delete role '{name}': {e}")
            return False

    def _get_roles_dir_path(self):
        """获取角色目录路径，处理相对路径"""
        if os.path.isabs(self._roles_dir_path):
            return self._roles_dir_path
        else:
            # 如果是相对路径，相对于项目根目录
            # 尝试找到项目根目录（包含roles目录的那个目录）
            current_dir = os.getcwd()
            roles_path = os.path.join(current_dir, self._roles_dir_path)

            # 如果当前目录下有这个路径，使用它
            if os.path.exists(roles_path):
                return roles_path

            # 否则尝试其他可能的位置
            root_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            fallback_path = os.path.join(root_dir, self._roles_dir_path)
            if os.path.exists(fallback_path):
                return fallback_path

            # 如果都找不到，返回相对于当前工作目录的路径
            return roles_path

    def _extract_model(self, role_data: dict) -> Optional[str]:
        """从 model_configs 提取主模型名（is_primary 优先，去 provider 前缀）。"""
        configs = role_data.get("model_configs") or []
        if not configs:
            return None
        primary = next(
            (c for c in configs if c.get("is_primary")), configs[0]
        )
        model_name = primary.get("model_name", "") if isinstance(primary, dict) else ""
        if not model_name:
            return None
        # "ollama/llama3:8b" → "llama3:8b"
        return str(model_name).split("/", 1)[-1]

    def list_roles(self) -> list[Role]:
        """Returns a list of all available roles."""
        return list(self._roles.values())
