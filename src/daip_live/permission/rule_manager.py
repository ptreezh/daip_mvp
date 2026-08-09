#!/usr/bin/env python3
"""
权限规则管理器接口定义
基于KISS、YAGNI、SOLID原则设计
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import yaml


class PermissionRuleManagerInterface(ABC):
    """权限规则管理器接口"""

    @abstractmethod
    def get_tool_permission(self, tool_name: str) -> str:
        """
        获取工具的权限规则

        Args:
            tool_name: 工具名称

        Returns:
            str: 权限规则 ("allow", "deny", "ask")
        """
        pass

    @abstractmethod
    def set_tool_permission(self, tool_name: str, permission: str) -> None:
        """
        设置工具的权限规则

        Args:
            tool_name: 工具名称
            permission: 权限规则 ("allow", "deny", "ask")
        """
        pass

    @abstractmethod
    def reset_tool_permission(self, tool_name: str) -> None:
        """
        重置工具权限规则为默认值

        Args:
            tool_name: 工具名称
        """
        pass

    @abstractmethod
    def set_default_permission(self, permission: str) -> None:
        """
        设置默认权限策略

        Args:
            permission: 默认权限策略 ("allow", "deny", "ask")
        """
        pass

    @abstractmethod
    def list_permission_rules(self) -> dict[str, str]:
        """
        列出所有权限规则

        Returns:
            Dict[str, str]: 工具名称到权限规则的映射
        """
        pass


class PermissionRuleManager(PermissionRuleManagerInterface):
    """权限规则管理器实现"""

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化权限规则管理器

        Args:
            config_file: 配置文件路径，如果为None则使用默认路径
        """
        self._config_file = config_file or self._get_default_config_file()
        self._default_permission = "ask"
        self._tool_permissions: dict[str, str] = {}
        self._load_config()

    def _get_default_config_file(self) -> str:
        """
        获取默认配置文件路径

        Returns:
            str: 配置文件路径
        """
        # 获取用户主目录
        home_dir = Path.home()
        # 创建.daip目录
        daip_dir = home_dir / ".daip"
        daip_dir.mkdir(exist_ok=True)
        # 返回配置文件路径
        return str(daip_dir / "permissions.yaml")

    def _load_config(self) -> None:
        """
        从配置文件加载权限规则
        """
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}

                # 加载默认权限策略
                permission_rules = config.get("permission_rules", {})
                self._default_permission = permission_rules.get("default", "ask")

                # 加载工具权限规则
                self._tool_permissions = permission_rules.get("tools", {})
            else:
                # 配置文件不存在，使用默认配置
                self._save_config()
        except Exception:
            # 配置加载失败，使用默认配置
            self._default_permission = "ask"
            self._tool_permissions = {}

    def _save_config(self) -> None:
        """
        保存权限规则到配置文件
        """
        try:
            # 创建配置数据
            config = {
                "permission_rules": {
                    "default": self._default_permission,
                    "tools": self._tool_permissions,
                }
            }

            # 确保目录存在
            config_path = Path(self._config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存配置文件
            with open(self._config_file, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except Exception:
            pass

    def get_tool_permission(self, tool_name: str) -> str:
        """
        获取工具的权限规则

        Args:
            tool_name: 工具名称

        Returns:
            str: 权限规则 ("allow", "deny", "ask")
        """
        return self._tool_permissions.get(tool_name, self._default_permission)

    def set_tool_permission(self, tool_name: str, permission: str) -> None:
        """
        设置工具的权限规则

        Args:
            tool_name: 工具名称
            permission: 权限规则 ("allow", "deny", "ask")

        Raises:
            ValueError: 当permission不是有效的权限值时
        """
        if permission not in ["allow", "deny", "ask"]:
            raise ValueError(
                f"无效的权限值: {permission}. 必须是 'allow', 'deny', 或 'ask' 之一."
            )

        self._tool_permissions[tool_name] = permission
        self._save_config()

    def reset_tool_permission(self, tool_name: str) -> None:
        """
        重置工具权限规则为默认值

        Args:
            tool_name: 工具名称
        """
        if tool_name in self._tool_permissions:
            del self._tool_permissions[tool_name]
            self._save_config()

    def set_default_permission(self, permission: str) -> None:
        """
        设置默认权限策略

        Args:
            permission: 默认权限策略 ("allow", "deny", "ask")

        Raises:
            ValueError: 当permission不是有效的权限值时
        """
        if permission not in ["allow", "deny", "ask"]:
            raise ValueError(
                f"无效的权限值: {permission}. 必须是 'allow', 'deny', 或 'ask' 之一."
            )

        self._default_permission = permission
        self._save_config()

    def list_permission_rules(self) -> dict[str, str]:
        """
        列出所有权限规则

        Returns:
            Dict[str, str]: 工具名称到权限规则的映射
        """
        return self._tool_permissions.copy()

    def get_default_permission(self) -> str:
        """
        获取默认权限策略

        Returns:
            str: 默认权限策略
        """
        return self._default_permission


# 工厂类用于创建权限规则管理器实例
class PermissionRuleManagerFactory:
    """权限规则管理器工厂类"""

    @staticmethod
    def create_permission_rule_manager(
        config_file: Optional[str] = None,
    ) -> PermissionRuleManagerInterface:
        """
        创建权限规则管理器实例

        Args:
            config_file: 配置文件路径，如果为None则使用默认路径

        Returns:
            PermissionRuleManagerInterface: 权限规则管理器实例
        """
        return PermissionRuleManager(config_file)
