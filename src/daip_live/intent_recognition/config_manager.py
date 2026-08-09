"""
增强意图识别系统 - 配置管理

支持动态配置管理，允许运行时调整系统参数
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class EnhancedIntentSystemConfig:
    """
    增强意图识别系统配置
    """

    # 基础配置
    enable_context_aware: bool = True
    enable_debug: bool = False
    enable_enhanced_features: bool = True

    # 性能配置
    response_time_threshold: float = 0.1  # 响应时间阈值（秒）
    context_cache_ttl: int = 300  # 上下文缓存生存时间（秒）
    intent_cache_size: int = 1000  # 意图缓存大小

    # Padatious相关配置
    padatious_enable: bool = True
    padatious_training_path: str = "./padatious_models"

    # 误识别保护配置
    misrecognition_protection_enabled: bool = True
    paper_intent_penalty: float = -0.3
    chat_intent_boost: float = 0.2

    # 语义消歧配置
    semantic_disambiguation_enabled: bool = True

    # 上下文注入配置
    context_injection_enabled: bool = True

    # 日志配置
    log_level: str = "INFO"
    log_performance_metrics: bool = True

    # 融合权重配置
    padatious_weight: float = 0.6
    original_weight: float = 0.4

    # 其他配置
    max_conversation_history: int = 10
    confidence_threshold: float = 0.3
    auto_complete_threshold: float = 0.8


class ConfigManager:
    """
    配置管理器
    支持动态加载、保存和更新配置
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "./intent_system_config.json"
        self.default_config = EnhancedIntentSystemConfig()
        self.logger = logging.getLogger(__name__)  # 在调用其他方法前初始化logger
        self.current_config = self.load_config()

        # 应用日志级别
        self._apply_log_level()

    def load_config(self) -> EnhancedIntentSystemConfig:
        """
        从文件加载配置

        Returns:
            配置对象
        """
        if not os.path.exists(self.config_path):
            self.logger.info(
                f"Config file {self.config_path} not found, using default config"
            )
            self.save_config(self.default_config)
            return self.default_config

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            # 使用默认配置作为基础，然后用文件中的值覆盖
            config = EnhancedIntentSystemConfig(**config_data)
            self.logger.info(f"Config loaded from {self.config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self.default_config

    def save_config(self, config: EnhancedIntentSystemConfig) -> bool:
        """
        保存配置到文件

        Args:
            config: 配置对象

        Returns:
            是否保存成功
        """
        try:
            config_data = asdict(config)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Config saved to {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False

    def get_config(self) -> EnhancedIntentSystemConfig:
        """
        获取当前配置

        Returns:
            当前配置对象
        """
        return self.current_config

    def update_config(self, updates: dict[str, Any]) -> bool:
        """
        更新配置

        Args:
            updates: 配置更新字典

        Returns:
            是否更新成功
        """
        try:
            # 创建新的配置对象，基于当前配置
            new_config = EnhancedIntentSystemConfig(**asdict(self.current_config))

            # 应用更新
            for key, value in updates.items():
                if hasattr(new_config, key):
                    setattr(new_config, key, value)
                else:
                    self.logger.warning(f"Unknown config key: {key}")

            # 验证更新后的配置
            if self._validate_config(new_config):
                self.current_config = new_config
                self._apply_config_changes()
                self.save_config(self.current_config)
                self.logger.info("Configuration updated successfully")
                return True
            else:
                self.logger.error("Configuration validation failed, update rejected")
                return False
        except Exception as e:
            self.logger.error(f"Error updating config: {e}")
            return False

    def _validate_config(self, config: EnhancedIntentSystemConfig) -> bool:
        """
        验证配置的有效性

        Args:
            config: 配置对象

        Returns:
            配置是否有效
        """
        # 验证时间阈值
        if config.response_time_threshold <= 0:
            self.logger.error("Response time threshold must be positive")
            return False

        # 验证缓存大小
        if config.intent_cache_size <= 0:
            self.logger.error("Intent cache size must be positive")
            return False

        # 验证融合权重
        if config.padatious_weight < 0 or config.original_weight < 0:
            self.logger.error("Fusion weights must be non-negative")
            return False

        if abs((config.padatious_weight + config.original_weight) - 1.0) > 0.001:
            self.logger.warning("Fusion weights don't sum to 1.0")

        return True

    def _apply_config_changes(self):
        """
        应用配置变更到系统
        这是一个模板方法，子类可以重写以应用特定的配置变更
        """
        self._apply_log_level()

    def _apply_log_level(self):
        """
        应用日志级别配置
        """
        log_level = getattr(self.current_config, "log_level", "INFO")
        if isinstance(log_level, str):
            numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        else:
            numeric_level = log_level

        logging.getLogger().setLevel(numeric_level)
        self.logger.setLevel(numeric_level)

    def reset_to_defaults(self) -> bool:
        """
        重置为默认配置

        Returns:
            是否重置成功
        """
        try:
            self.current_config = self.default_config
            self._apply_config_changes()
            self.save_config(self.current_config)
            self.logger.info("Configuration reset to defaults")
            return True
        except Exception as e:
            self.logger.error(f"Error resetting config: {e}")
            return False

    def get_config_diff(self) -> dict[str, Any]:
        """
        获取当前配置与默认配置的差异

        Returns:
            配置差异字典
        """
        default_dict = asdict(self.default_config)
        current_dict = asdict(self.current_config)

        diff = {}
        for key in current_dict:
            if key in default_dict and current_dict[key] != default_dict[key]:
                diff[key] = {"current": current_dict[key], "default": default_dict[key]}

        return diff

    def update_multiple_configs(
        self, config_updates: dict[str, Any]
    ) -> dict[str, bool]:
        """
        批量更新多个配置项

        Args:
            config_updates: 配置更新字典

        Returns:
            更新结果字典
        """
        results = {}
        temp_config = EnhancedIntentSystemConfig(**asdict(self.current_config))

        for key, value in config_updates.items():
            try:
                if hasattr(temp_config, key):
                    setattr(temp_config, key, value)
                    results[key] = True
                else:
                    results[key] = False
                    self.logger.warning(f"Unknown config key: {key}")
            except Exception as e:
                results[key] = False
                self.logger.error(f"Error updating config {key}: {e}")

        # 如果所有更新都成功，应用到当前配置
        if all(results.values()) and self._validate_config(temp_config):
            self.current_config = temp_config
            self._apply_config_changes()
            self.save_config(self.current_config)
            self.logger.info("Multiple configuration updates applied successfully")
        else:
            self.logger.error("Some configuration updates failed validation")

        return results


class DynamicConfigurableIntentSystemMixin:
    """
    动态可配置意图系统的混入类
    可以添加到任何意图识别系统类中以提供配置管理功能
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None, **kwargs):
        """
        初始化混入类

        Args:
            config_manager: 配置管理器
            **kwargs: 其他参数
        """
        self.config_manager = config_manager or ConfigManager()
        self.config = self.config_manager.get_config()

        # 从配置初始化参数
        self.response_time_threshold = self.config.response_time_threshold
        self.context_cache_ttl = self.config.context_cache_ttl
        self.intent_cache_size = self.config.intent_cache_size
        self.padatious_weight = self.config.padatious_weight
        self.original_weight = self.config.original_weight
        self.confidence_threshold = self.config.confidence_threshold
        self.auto_complete_threshold = self.config.auto_complete_threshold
        self.max_conversation_history = self.config.max_conversation_history

        # 更新其他组件配置
        self._update_component_configs()

    def _update_component_configs(self):
        """
        更新组件配置
        """
        # 根据配置启用/禁用功能
        self.enable_context_aware = self.config.enable_context_aware
        self.enable_debug = self.config.enable_debug
        self.enable_enhanced_features = self.config.enable_enhanced_features
        self.misrecognition_protection_enabled = (
            self.config.misrecognition_protection_enabled
        )
        self.semantic_disambiguation_enabled = (
            self.config.semantic_disambiguation_enabled
        )
        self.context_injection_enabled = self.config.context_injection_enabled

    def update_system_config(self, updates: dict[str, Any]) -> bool:
        """
        更新系统配置

        Args:
            updates: 配置更新字典

        Returns:
            是否更新成功
        """
        success = self.config_manager.update_config(updates)
        if success:
            # 重新加载配置
            self.config = self.config_manager.get_config()
            self._update_component_configs()
        return success

    def get_current_config(self) -> EnhancedIntentSystemConfig:
        """
        获取当前系统配置

        Returns:
            当前配置对象
        """
        return self.config

    def get_config_diff(self) -> dict[str, Any]:
        """
        获取配置差异

        Returns:
            配置差异字典
        """
        return self.config_manager.get_config_diff()


# 使用示例
def example_usage():
    """
    配置管理使用示例
    """
    # 创建配置管理器
    config_manager = ConfigManager("./my_config.json")

    # 获取当前配置
    config_manager.get_config()

    # 更新配置
    updates = {
        "response_time_threshold": 0.08,  # 80ms
        "log_level": "DEBUG",
    }
    success = config_manager.update_config(updates)

    if success:
        config_manager.get_config()

        # 比较配置差异
        diff = config_manager.get_config_diff()
        if diff:
            for key, values in diff.items():
                pass
    else:
        pass


if __name__ == "__main__":
    example_usage()
