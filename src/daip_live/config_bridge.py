"""配置桥接适配器 - 解决 dependency-injector 与 ConfigManager 的兼容性问题"""

from typing import Any, Dict, Optional
import threading
from pathlib import Path


class ConfigurationBridge:
    """
    配置桥接适配器

    作为 dependency-injector 的 providers.Configuration() 和 ConfigManager 之间的桥梁，
    确保配置在完全加载后才被访问，同时保持线程安全。
    """

    _instance: Optional['ConfigurationBridge'] = None
    _lock = threading.Lock()
    _config_manager: Optional[Any] = None
    _config_data: Optional[Dict[str, Any]] = None
    _initialized: bool = False

    def __new__(cls) -> 'ConfigurationBridge':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._config_manager = None
            self._config_data = None

    def set_config_manager(self, config_manager: Any) -> None:
        """设置 ConfigManager 实例"""
        with self._lock:
            self._config_manager = config_manager

    def get_config_data(self) -> Dict[str, Any]:
        """
        获取配置数据，确保配置已加载

        Returns:
            Dict[str, Any]: 配置数据字典，兼容 dependency-injector 的访问方式
        """
        with self._lock:
            if self._config_data is None:
                if self._config_manager is None:
                    # 如果没有配置管理器，返回安全的默认配置
                    self._config_data = self._get_safe_default_config()
                else:
                    try:
                        # 通过 ConfigManager 获取配置并转换为字典
                        config = self._config_manager.get_config()
                        self._config_data = self._config_to_dict(config)
                    except Exception:
                        # 配置加载失败时使用安全的默认配置
                        self._config_data = self._get_safe_default_config()

        return self._config_data

    def _config_to_dict(self, config: Any) -> Dict[str, Any]:
        """将 Pydantic 配置对象转换为字典"""
        if hasattr(config, 'model_dump'):
            # Pydantic v2
            return config.model_dump()
        elif hasattr(config, 'dict'):
            # Pydantic v1
            return config.dict()
        else:
            # 尝试直接转换为字典
            return dict(config)

    def _get_safe_default_config(self) -> Dict[str, Any]:
        """获取安全的默认配置，确保所有必需字段都有值"""
        return {
            'database': {
                'path': 'daip_live.db'
            },
            'llm_provider': {
                'default_model': 'gpt-3.5-turbo',  # 确保有默认值
                'embedding_model': 'text-embedding-ada-002'
            },
            'knowledge_base': {
                'directory': 'knowledge/'
            },
            'role_manager': {
                'roles_dir': 'roles/'
            },
            'wiki': {
                'pages_directory': 'knowledge/wiki/'
            },
            'debate': {
                'logs_directory': 'knowledge/debate/'
            },
            'paper': {
                'download_directory': 'knowledge/paper/'
            }
        }

    def __getattr__(self, name: str) -> Any:
        """
        动态属性访问，模拟 dependency-injector 的配置访问方式

        例如：config.llm_provider.default_model 会被转换为
        self.get_config_data()['llm_provider']['default_model']
        """
        config_data = self.get_config_data()

        # 支持嵌套属性访问，如 config.llm_provider.default_model
        if '.' in name:
            parts = name.split('.')
            value = config_data
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    raise AttributeError(f"Configuration '{name}' not found")
            return value
        else:
            if name in config_data:
                return config_data[name]
            else:
                raise AttributeError(f"Configuration '{name}' not found")

    def reset(self) -> None:
        """重置配置状态，主要用于测试"""
        with self._lock:
            self._config_data = None


# 全局配置桥接实例
config_bridge = ConfigurationBridge()