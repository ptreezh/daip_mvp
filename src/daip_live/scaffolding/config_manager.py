"""
配置管理器
遵循SOLID原则，提供统一的配置管理功能
"""

import copy
import json
import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

# 配置文件解析库
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

try:
    import toml

    TOML_AVAILABLE = True
except ImportError:
    toml = None
    TOML_AVAILABLE = False

from .models import ValidationError


class ConfigFormat(Enum):
    """配置文件格式"""

    YAML = "yaml"
    JSON = "json"
    TOML = "toml"

    @classmethod
    def from_extension(cls, file_path: str) -> "ConfigFormat":
        """从文件扩展名获取配置格式"""
        ext = Path(file_path).suffix.lower()

        if ext in [".yaml", ".yml"]:
            return cls.YAML
        elif ext == ".json":
            return cls.JSON
        elif ext == ".toml":
            return cls.TOML
        else:
            # 默认使用YAML
            return cls.YAML


@dataclass
class ConfigSource:
    """配置源"""

    name: str
    path: str
    format: ConfigFormat = ConfigFormat.YAML
    priority: int = 1
    enabled: bool = True
    last_modified: Optional[float] = None
    content_hash: Optional[str] = None

    def __lt__(self, other):
        """支持按优先级排序（优先级数字越小优先级越高）"""
        if self.__class__ is other.__class__:
            return self.priority < other.priority
        return NotImplemented


@dataclass
class ConfigChange:
    """配置变更记录"""

    key: str
    old_value: Any
    new_value: Any
    timestamp: float
    source: str = "manual"


class ConfigValidator:
    """配置验证器"""

    def __init__(self, schema: dict[str, Any]):
        """初始化验证器

        Args:
            schema: JSON Schema格式的验证模式
        """
        self.schema = schema

    def validate(self, config: dict[str, Any]) -> None:
        """验证配置

        Args:
            config: 要验证的配置字典

        Raises:
            ValidationError: 当配置验证失败时
        """
        # 简化的验证实现
        self._validate_schema(config, self.schema, "")

    def _validate_schema(self, data: Any, schema: dict[str, Any], path: str) -> None:
        """递归验证配置模式"""
        if not isinstance(schema, dict) or "type" not in schema:
            return

        data_type = schema["type"]
        current_path = f"{path}." if path else ""

        if data_type == "object":
            if not isinstance(data, dict):
                raise ValidationError(f"Expected object at {current_path}")

            # 检查必需属性
            required = schema.get("required", [])
            for prop in required:
                if prop not in data:
                    raise ValidationError(
                        f"Required property '{current_path}{prop}' is missing"
                    )

            # 验证属性
            properties = schema.get("properties", {})
            for prop, prop_schema in properties.items():
                if prop in data:
                    self._validate_schema(
                        data[prop], prop_schema, f"{current_path}{prop}"
                    )

        elif data_type == "string":
            if not isinstance(data, str):
                raise ValidationError(f"Expected string at {current_path}")

        elif data_type == "integer":
            if not isinstance(data, int):
                raise ValidationError(f"Expected integer at {current_path}")

            # 检查数值范围
            minimum = schema.get("minimum")
            if minimum is not None and data < minimum:
                raise ValidationError(
                    f"Value {data} at {current_path} is below minimum {minimum}"
                )

            maximum = schema.get("maximum")
            if maximum is not None and data > maximum:
                raise ValidationError(
                    f"Value {data} at {current_path} is above maximum {maximum}"
                )

        elif data_type == "boolean":
            if not isinstance(data, bool):
                raise ValidationError(f"Expected boolean at {current_path}")

        elif data_type == "array":
            if not isinstance(data, list):
                raise ValidationError(f"Expected array at {current_path}")

            # 验证数组项
            items_schema = schema.get("items")
            if items_schema:
                for i, item in enumerate(data):
                    self._validate_schema(item, items_schema, f"{current_path}[{i}]")


class ConfigWatcher:
    """配置监听器管理"""

    def __init__(self):
        self._watchers: dict[str, list[Callable]] = {}

    def add_watcher(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """添加配置监听器

        Args:
            key: 要监听的配置键
            callback: 回调函数，参数为(key, old_value, new_value)
        """
        if key not in self._watchers:
            self._watchers[key] = []
        self._watchers[key].append(callback)

    def remove_watcher(self, key: str, callback: Callable) -> None:
        """移除配置监听器

        Args:
            key: 配置键
            callback: 要移除的回调函数
        """
        if key in self._watchers:
            try:
                self._watchers[key].remove(callback)
                if not self._watchers[key]:
                    del self._watchers[key]
            except ValueError:
                pass  # 回调函数不存在

    def notify_change(self, key: str, old_value: Any, new_value: Any) -> None:
        """通知配置变更

        Args:
            key: 变更的配置键
            old_value: 旧值
            new_value: 新值
        """
        # 通知精确匹配的监听器
        if key in self._watchers:
            for callback in self._watchers[key]:
                try:
                    callback(key, old_value, new_value)
                except Exception:
                    pass  # 忽略回调函数中的错误

        # 通知模式匹配的监听器
        for watcher_key, callbacks in self._watchers.items():
            if self._key_matches(key, watcher_key) and key != watcher_key:
                for callback in callbacks:
                    try:
                        callback(key, old_value, new_value)
                    except Exception:
                        pass  # 忽略回调函数中的错误

    def _key_matches(self, key: str, pattern: str) -> bool:
        """检查键是否匹配模式"""
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return key.startswith(prefix)
        return False


class ScaffoldConfig:
    """脚手架配置管理器

    遵循单一职责原则，专门负责配置管理
    支持多源配置、动态加载、验证和监听
    """

    # 默认配置
    DEFAULT_CONFIG = {
        "scaffold": {
            "max_file_size": 1024 * 1024,  # 1MB
            "max_files": 1000,
            "default_encoding": "utf-8",
            "backup_enabled": True,
            "auto_create_dirs": True,
        },
        "validation": {
            "min_description_length": 10,
            "max_description_length": 5000,
            "strict_mode": False,
            "validate_paths": True,
        },
        "retry": {
            "max_attempts": 3,
            "base_delay": 1.0,
            "max_delay": 60.0,
            "backoff_factor": 2.0,
            "jitter": True,
        },
        "generation": {
            "timeout": 300,  # 5分钟
            "max_tokens": 4000,
            "temperature": 0.7,
        },
        "file_operations": {
            "chunk_size": 8192,
            "atomic_writes": True,
            "preserve_permissions": True,
        },
    }

    def __init__(self, initial_data: Optional[dict[str, Any]] = None):
        """初始化配置管理器

        Args:
            initial_data: 初始配置数据
        """
        self._data: dict[str, Any] = {}
        self.sources: list[ConfigSource] = []
        self.validator: Optional[ConfigValidator] = None
        self.watcher = ConfigWatcher()
        self.env_prefix: Optional[str] = None
        self._change_history: list[ConfigChange] = []

        # 加载默认配置
        self.load_defaults()

        # 合并初始数据
        if initial_data:
            self.merge(initial_data)

    def load_defaults(self) -> None:
        """加载默认配置"""
        self._data = copy.deepcopy(self.DEFAULT_CONFIG)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持点分隔的嵌套键）

        Args:
            key: 配置键，支持 "section.subsection.key" 格式
            default: 默认值

        Returns:
            Any: 配置值
        """
        keys = key.split(".")
        current = self._data

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, source: str = "manual") -> None:
        """设置配置值

        Args:
            key: 配置键，支持 "section.subsection.key" 格式
            value: 配置值
            source: 配置来源
        """
        keys = key.split(".")
        old_value = self.get(key)

        # 设置嵌套值
        current = self._data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

        # 记录变更
        import time

        change = ConfigChange(
            key=key,
            old_value=old_value,
            new_value=value,
            timestamp=time.time(),
            source=source,
        )
        self._change_history.append(change)

        # 通知监听器
        self.watcher.notify_change(key, old_value, value)

    def has_path(self, key: str) -> bool:
        """检查配置路径是否存在

        Args:
            key: 配置键

        Returns:
            bool: 路径是否存在
        """
        return self.get(key) is not None

    def delete_path(self, key: str) -> None:
        """删除配置路径

        Args:
            key: 要删除的配置键
        """
        keys = key.split(".")
        current = self._data

        try:
            for k in keys[:-1]:
                current = current[k]

            old_value = current.pop(keys[-1], None)

            # 如果父级节点为空，也删除
            self._cleanup_empty_paths(key.split("."))

            # 通知监听器
            self.watcher.notify_change(key, old_value, None)

        except (KeyError, TypeError):
            pass  # 路径不存在

    def _cleanup_empty_paths(self, keys: list[str]) -> None:
        """清理空的路径节点"""
        current = self._data

        for i, key in enumerate(keys[:-1]):
            if key in current and isinstance(current[key], dict):
                if not current[key]:  # 空字典
                    parent_path = keys[:i]
                    if parent_path:
                        parent_current = self._data
                        for k in parent_path:
                            parent_current = parent_current[k]
                        del parent_current[key]
                        self._cleanup_empty_paths(parent_path)
                    else:
                        del self._data[key]
                        break
                current = current[key]

    def merge(self, data: dict[str, Any]) -> None:
        """合并配置数据

        Args:
            data: 要合并的配置数据
        """
        self._deep_merge(self._data, data)

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """深度合并字典"""
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(target[key], value)
            else:
                target[key] = copy.deepcopy(value)

    def to_dict(self) -> dict[str, Any]:
        """将配置转换为字典"""
        return copy.deepcopy(self._data)

    def get_flattened(self) -> dict[str, Any]:
        """获取扁平化的配置字典"""
        return self._flatten_dict(self._data)

    def _flatten_dict(
        self, d: dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> dict[str, Any]:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScaffoldConfig":
        """从字典创建配置

        Args:
            data: 配置字典

        Returns:
            ScaffoldConfig: 配置实例
        """
        return cls(initial_data=data)

    @classmethod
    def load_from_file(
        cls, file_path: str, format: Optional[ConfigFormat] = None
    ) -> "ScaffoldConfig":
        """从文件加载配置

        Args:
            file_path: 配置文件路径
            format: 配置格式，None表示自动检测

        Returns:
            ScaffoldConfig: 配置实例
        """
        if format is None:
            format = ConfigFormat.from_extension(file_path)

        with open(file_path, encoding="utf-8") as f:
            if format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML configuration files")
                data = yaml.safe_load(f)
            elif format == ConfigFormat.JSON:
                data = json.load(f)
            elif format == ConfigFormat.TOML:
                if not TOML_AVAILABLE:
                    raise ImportError("toml is required for TOML configuration files")
                data = toml.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")

        return cls(initial_data=data)

    def save_to_file(
        self, file_path: str, format: Optional[ConfigFormat] = None
    ) -> None:
        """保存配置到文件

        Args:
            file_path: 配置文件路径
            format: 配置格式，None表示自动检测
        """
        if format is None:
            format = ConfigFormat.from_extension(file_path)

        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            if format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML configuration files")
                yaml.dump(self._data, f, default_flow_style=False, allow_unicode=True)
            elif format == ConfigFormat.JSON:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            elif format == ConfigFormat.TOML:
                if not TOML_AVAILABLE:
                    raise ImportError("toml is required for TOML configuration files")
                toml.dump(self._data, f)
            else:
                raise ValueError(f"Unsupported format: {format}")

    def _load_from_file(self, file_path: str) -> dict[str, Any]:
        """从文件加载配置数据（内部方法）"""
        format = ConfigFormat.from_extension(file_path)
        with open(file_path, encoding="utf-8") as f:
            if format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML configuration files")
                return yaml.safe_load(f) or {}
            elif format == ConfigFormat.JSON:
                return json.load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")

    def add_source(self, source: ConfigSource) -> None:
        """添加配置源

        Args:
            source: 配置源
        """
        self.sources.append(source)
        # 按优先级排序
        self.sources.sort()

    def remove_source(self, name: str) -> None:
        """移除配置源

        Args:
            name: 配置源名称
        """
        self.sources = [s for s in self.sources if s.name != name]

    def get_source(self, name: str) -> Optional[ConfigSource]:
        """获取配置源

        Args:
            name: 配置源名称

        Returns:
            Optional[ConfigSource]: 配置源或None
        """
        for source in self.sources:
            if source.name == name:
                return source
        return None

    def reload(self) -> None:
        """从所有配置源重新加载配置"""
        # 重新加载默认配置
        self.load_defaults()

        # 按优先级顺序加载配置源
        for source in sorted(self.sources):
            if source.enabled and os.path.exists(source.path):
                try:
                    data = self._load_from_file(source.path)
                    self.merge(data)
                except Exception:
                    # 记录错误但继续加载其他源
                    pass

    def set_validator(self, validator: ConfigValidator) -> None:
        """设置配置验证器

        Args:
            validator: 配置验证器
        """
        self.validator = validator

    def validate(self) -> None:
        """验证当前配置

        Raises:
            ValidationError: 当配置验证失败时
        """
        if self.validator:
            self.validator.validate(self._data)

    def enable_env_substitution(self, prefix: str) -> None:
        """启用环境变量替换

        Args:
            prefix: 环境变量前缀
        """
        self.env_prefix = prefix
        self._substitute_env_vars()

    def _substitute_env_vars(self) -> None:
        """替换环境变量"""
        if not self.env_prefix:
            return

        # 递归替换配置中的环境变量
        self._substitute_in_dict(self._data)

    def _substitute_in_dict(self, data: dict[str, Any], path: str = "") -> None:
        """在字典中替换环境变量"""
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict):
                self._substitute_in_dict(value, current_path)
            else:
                # 查找环境变量模式（匹配键名）
                env_var_pattern = f"^{self.env_prefix}_([A-Z0-9_]+)$"
                match = re.match(env_var_pattern, key.upper())
                if match:
                    env_name = f"{self.env_prefix}_{match.group(1)}"
                    if env_name in os.environ:
                        # 尝试类型转换
                        str_value = os.environ[env_name]
                        try:
                            # 尝试转换为数字
                            if "." in str_value:
                                data[key] = float(str_value)
                            else:
                                data[key] = int(str_value)
                        except ValueError:
                            # 保持为字符串
                            data[key] = str_value

    def add_watcher(self, key: str, callback: Callable[[str, Any, Any], None]) -> None:
        """添加配置监听器

        Args:
            key: 要监听的配置键
            callback: 回调函数
        """
        self.watcher.add_watcher(key, callback)

    def remove_watcher(self, key: str, callback: Callable) -> None:
        """移除配置监听器

        Args:
            key: 配置键
            callback: 回调函数
        """
        self.watcher.remove_watcher(key, callback)

    def export(self) -> dict[str, Any]:
        """导出配置

        Returns:
            Dict[str, Any]: 配置数据
        """
        return self.to_dict()

    def import_data(self, data: dict[str, Any], merge: bool = True) -> None:
        """导入配置数据

        Args:
            data: 要导入的配置数据
            merge: 是否与现有配置合并，False表示替换
        """
        if merge:
            self.merge(data)
        else:
            self._data = copy.deepcopy(data)

    def create_backup(self) -> dict[str, Any]:
        """创建配置备份

        Returns:
            Dict[str, Any]: 备份的配置数据
        """
        return {
            "config": copy.deepcopy(self._data),
            "sources": copy.deepcopy(self.sources),
            "timestamp": __import__("time").time(),
        }

    def restore_backup(self, backup: dict[str, Any]) -> None:
        """恢复配置备份

        Args:
            backup: 备份数据
        """
        if "config" in backup:
            self._data = copy.deepcopy(backup["config"])
        if "sources" in backup:
            self.sources = copy.deepcopy(backup["sources"])

    def copy(self) -> "ScaffoldConfig":
        """创建配置的深拷贝

        Returns:
            ScaffoldConfig: 配置副本
        """
        new_config = ScaffoldConfig()
        new_config._data = copy.deepcopy(self._data)
        new_config.sources = copy.deepcopy(self.sources)
        new_config.validator = self.validator
        new_config.env_prefix = self.env_prefix
        return new_config

    def search_keys(self, pattern: str) -> list[str]:
        """搜索配置键

        Args:
            pattern: 搜索模式

        Returns:
            List[str]: 匹配的配置键列表
        """
        flattened = self.get_flattened()
        return [key for key in flattened.keys() if pattern in key]

    def search_values(self, pattern: str) -> list[str]:
        """搜索配置值

        Args:
            pattern: 搜索模式

        Returns:
            List[str]: 匹配的配置键列表
        """
        flattened = self.get_flattened()
        return [
            key
            for key, value in flattened.items()
            if isinstance(value, str) and pattern in value
        ]

    def get_change_history(self, limit: Optional[int] = None) -> list[ConfigChange]:
        """获取变更历史

        Args:
            limit: 返回记录数量限制

        Returns:
            List[ConfigChange]: 变更记录列表
        """
        if limit:
            return self._change_history[-limit:]
        return self._change_history.copy()

    def clear_history(self) -> None:
        """清除变更历史"""
        self._change_history.clear()
