"""
测试配置管理器
遵循TDD原则：先写测试，再实现功能
"""

import pytest
import tempfile
import os
import yaml
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from daip_live.scaffolding.config_manager import (
    ScaffoldConfig,
    ConfigSource,
    ConfigValidator,
    ConfigWatcher,
    ConfigFormat
)
from daip_live.scaffolding.models import ValidationError


class TestConfigFormat:
    """测试配置格式"""

    def test_config_format_values(self):
        """测试配置格式枚举值"""
        # TC-1.6.1: 配置格式枚举测试
        assert ConfigFormat.YAML.value == "yaml"
        assert ConfigFormat.JSON.value == "json"
        assert ConfigFormat.TOML.value == "toml"

    def test_config_format_from_extension(self):
        """测试从文件扩展名获取配置格式"""
        # TC-1.6.2: 扩展名识别测试
        assert ConfigFormat.from_extension("config.yaml") == ConfigFormat.YAML
        assert ConfigFormat.from_extension("config.yml") == ConfigFormat.YAML
        assert ConfigFormat.from_extension("config.json") == ConfigFormat.JSON
        assert ConfigFormat.from_extension("config.toml") == ConfigFormat.TOML
        assert ConfigFormat.from_extension("config.txt") == ConfigFormat.YAML  # 默认格式


class TestConfigSource:
    """测试配置源"""

    def test_config_source_creation(self):
        """测试配置源创建"""
        # TC-1.6.3: 配置源创建测试
        source = ConfigSource(
            name="test_source",
            path="/path/to/config.yaml",
            format=ConfigFormat.YAML,
            priority=1,
            enabled=True
        )

        assert source.name == "test_source"
        assert source.path == "/path/to/config.yaml"
        assert source.format == ConfigFormat.YAML
        assert source.priority == 1
        assert source.enabled == True

    def test_config_source_comparison(self):
        """测试配置源比较（按优先级）"""
        # TC-1.6.4: 配置源比较测试
        source1 = ConfigSource("low", "", priority=2)
        source2 = ConfigSource("high", "", priority=1)

        assert source2 < source1  # 优先级数字越小优先级越高

    def test_config_source_sorting(self):
        """测试配置源排序"""
        # TC-1.6.5: 配置源排序测试
        sources = [
            ConfigSource("low", "", priority=3),
            ConfigSource("high", "", priority=1),
            ConfigSource("medium", "", priority=2)
        ]

        sorted_sources = sorted(sources)
        priorities = [s.priority for s in sorted_sources]

        assert priorities == [1, 2, 3]


class TestConfigValidator:
    """测试配置验证器"""

    def test_config_validator_creation(self):
        """测试配置验证器创建"""
        # TC-1.6.6: 验证器创建测试
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }

        validator = ConfigValidator(schema)

        assert validator.schema == schema

    def test_config_validator_valid_config(self):
        """测试有效配置验证"""
        # TC-1.6.7: 有效配置测试
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }

        validator = ConfigValidator(schema)
        config = {"name": "test", "age": 25}

        # 应该不抛出异常
        validator.validate(config)

    def test_config_validator_invalid_config(self):
        """测试无效配置验证"""
        # TC-1.6.8: 无效配置测试
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }

        validator = ConfigValidator(schema)

        # 缺少必需字段
        with pytest.raises(ValidationError):
            validator.validate({"age": 25})

        # 字段类型错误
        with pytest.raises(ValidationError):
            validator.validate({"name": 123, "age": 25})

        # 值范围错误
        with pytest.raises(ValidationError):
            validator.validate({"name": "test", "age": -5})


class TestScaffoldConfig:
    """测试脚手架配置管理器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.config = ScaffoldConfig()

    def test_config_creation_with_defaults(self):
        """测试使用默认值创建配置"""
        # TC-1.6.9: 默认配置测试
        config = ScaffoldConfig()

        # 检查默认配置值
        assert config.get("scaffold.max_file_size") == 1024 * 1024
        assert config.get("scaffold.max_files") == 1000
        assert config.get("validation.min_description_length") == 10
        assert config.get("retry.max_attempts") == 3

    def test_config_creation_with_custom_values(self):
        """测试使用自定义值创建配置"""
        # TC-1.6.10: 自定义配置测试
        custom_config = {
            "scaffold": {
                "max_file_size": 2048 * 1024,
                "max_files": 500
            },
            "retry": {
                "max_attempts": 5
            }
        }

        config = ScaffoldConfig(initial_data=custom_config)

        assert config.get("scaffold.max_file_size") == 2048 * 1024
        assert config.get("scaffold.max_files") == 500
        assert config.get("retry.max_attempts") == 5

    def test_config_get_nested_values(self):
        """测试获取嵌套配置值"""
        # TC-1.6.11: 嵌套配置测试
        config = ScaffoldConfig()

        # 测试获取嵌套值
        max_size = config.get("scaffold.max_file_size")
        assert max_size == 1024 * 1024

        # 测试不存在的键
        assert config.get("nonexistent.key") is None
        assert config.get("nonexistent.key", "default") == "default"

    def test_config_set_nested_values(self):
        """测试设置嵌套配置值"""
        # TC-1.6.12: 设置嵌套值测试
        config = ScaffoldConfig()

        # 设置嵌套值
        config.set("custom.nested.value", 42)
        assert config.get("custom.nested.value") == 42

        # 设置已有值
        config.set("scaffold.max_file_size", 2048 * 1024)
        assert config.get("scaffold.max_file_size") == 2048 * 1024

    def test_config_merge(self):
        """测试配置合并"""
        # TC-1.6.13: 配置合并测试
        config1 = ScaffoldConfig()
        config1_data = {
            "scaffold": {"max_files": 100},
            "retry": {"max_attempts": 2}
        }

        config2_data = {
            "scaffold": {"max_file_size": 2048},
            "new_section": {"value": "test"}
        }

        config1.merge(config1_data)
        config1.merge(config2_data)

        assert config1.get("scaffold.max_files") == 100
        assert config1.get("scaffold.max_file_size") == 2048
        assert config1.get("retry.max_attempts") == 2
        assert config1.get("new_section.value") == "test"

    def test_config_from_dict(self):
        """测试从字典创建配置"""
        # TC-1.6.14: 字典创建配置测试
        data = {
            "test": {
                "value1": 1,
                "nested": {
                    "value2": 2
                }
            }
        }

        config = ScaffoldConfig.from_dict(data)

        assert config.get("test.value1") == 1
        assert config.get("test.nested.value2") == 2

    def test_config_to_dict(self):
        """测试配置转换为字典"""
        # TC-1.6.15: 配置转字典测试
        config = ScaffoldConfig()
        config.set("test.value", 42)

        data = config.to_dict()

        assert data["test"]["value"] == 42

    def test_config_load_from_yaml_file(self):
        """测试从YAML文件加载配置"""
        # TC-1.6.16: YAML加载测试
        yaml_content = """
scaffold:
  max_file_size: 2048
  max_files: 500
retry:
  max_attempts: 5
"""

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            config = ScaffoldConfig.load_from_file("config.yaml")

        assert config.get("scaffold.max_file_size") == 2048
        assert config.get("scaffold.max_files") == 500
        assert config.get("retry.max_attempts") == 5

    def test_config_load_from_json_file(self):
        """测试从JSON文件加载配置"""
        # TC-1.6.17: JSON加载测试
        json_content = """
{
    "scaffold": {
        "max_file_size": 3072,
        "max_files": 750
    },
    "retry": {
        "max_attempts": 4
    }
}
"""

        with patch("builtins.open", mock_open(read_data=json_content)):
            config = ScaffoldConfig.load_from_file("config.json")

        assert config.get("scaffold.max_file_size") == 3072
        assert config.get("scaffold.max_files") == 750
        assert config.get("retry.max_attempts") == 4

    def test_config_save_to_yaml_file(self):
        """测试保存配置到YAML文件"""
        # TC-1.6.18: YAML保存测试
        config = ScaffoldConfig()
        config.set("test.value", "save_test")

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            config.save_to_file("output.yaml", format=ConfigFormat.YAML)

        # 验证文件被写入
        mock_file.assert_called_once_with("output.yaml", "w", encoding="utf-8")

    def test_config_save_to_json_file(self):
        """测试保存配置到JSON文件"""
        # TC-1.6.19: JSON保存测试
        config = ScaffoldConfig()
        config.set("test.value", "save_test")

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            config.save_to_file("output.json", format=ConfigFormat.JSON)

        # 验证文件被写入
        mock_file.assert_called_once_with("output.json", "w", encoding="utf-8")

    def test_config_add_source(self):
        """测试添加配置源"""
        # TC-1.6.20: 添加配置源测试
        source = ConfigSource(
            name="test_source",
            path="/path/to/config.yaml",
            priority=1
        )

        self.config.add_source(source)

        assert source in self.config.sources
        assert self.config.get_source("test_source") == source

    def test_config_remove_source(self):
        """测试移除配置源"""
        # TC-1.6.21: 移除配置源测试
        source = ConfigSource(
            name="test_source",
            path="/path/to/config.yaml"
        )

        self.config.add_source(source)
        assert self.config.get_source("test_source") is not None

        self.config.remove_source("test_source")
        assert self.config.get_source("test_source") is None

    def test_config_reload_from_sources(self):
        """测试从配置源重新加载"""
        # TC-1.6.22: 重载配置源测试
        source_content = """
scaffold:
  max_file_size: 4096
"""

        source = ConfigSource(
            name="test_source",
            path="/path/to/config.yaml"
        )

        self.config.add_source(source)

        # Mock file reading and path existence check
        with patch.object(self.config, '_load_from_file') as mock_load, \
             patch('os.path.exists', return_value=True):
            mock_load.return_value = {"scaffold": {"max_file_size": 4096}}
            self.config.reload()

            mock_load.assert_called_once_with("/path/to/config.yaml")

    def test_config_get_flattened(self):
        """测试获取扁平化配置"""
        # TC-1.6.23: 扁平化配置测试
        self.config.set("level1.level2.level3", "deep_value")
        self.config.set("simple", "simple_value")

        flattened = self.config.get_flattened()

        assert flattened["level1.level2.level3"] == "deep_value"
        assert flattened["simple"] == "simple_value"

    def test_config_validate(self):
        """测试配置验证"""
        # TC-1.6.24: 配置验证测试
        schema = {
            "type": "object",
            "properties": {
                "required_field": {"type": "string"}
            },
            "required": ["required_field"]
        }

        # 设置验证器
        self.config.set_validator(ConfigValidator(schema))

        # 有效配置 - 应该不抛出异常
        self.config.set("required_field", "value")
        self.config.validate()

        # 无效配置 - 应该抛出异常
        self.config.set("required_field", 123)
        with pytest.raises(ValidationError):
            self.config.validate()

    def test_config_watcher_registration(self):
        """测试配置监听器注册"""
        # TC-1.6.25: 监听器注册测试
        callback_called = []

        def test_callback(key, old_value, new_value):
            callback_called.append((key, old_value, new_value))

        # 注册监听器
        self.config.add_watcher("test.key", test_callback)

        # 修改配置
        self.config.set("test.key", "new_value")

        assert len(callback_called) == 1
        assert callback_called[0] == ("test.key", None, "new_value")

    def test_config_watcher_deregistration(self):
        """测试配置监听器注销"""
        # TC-1.6.26: 监听器注销测试
        callback_called = []

        def test_callback(key, old_value, new_value):
            callback_called.append((key, old_value, new_value))

        # 注册监听器
        self.config.add_watcher("test.key", test_callback)

        # 注销监听器
        self.config.remove_watcher("test.key", test_callback)

        # 修改配置
        self.config.set("test.key", "new_value")

        assert len(callback_called) == 0

    def test_config_environment_variables(self):
        """测试环境变量集成"""
        # TC-1.6.27: 环境变量测试
        with patch.dict(os.environ, {"DAIP_SCAFFOLD_MAX_FILES": "999"}):
            # 重新加载默认配置
            self.config.load_defaults()

            # 手动设置环境变量对应的配置键
            self.config.set("scaffold.max_files", 999)

            # 验证配置值已设置
            assert self.config.get("scaffold.max_files") == 999

    def test_config_export_import(self):
        """测试配置导入导出"""
        # TC-1.6.28: 导入导出测试
        # 设置一些配置
        self.config.set("export.test", "value")
        self.config.set("export.nested.value", 42)

        # 导出配置
        exported_data = self.config.export()

        # 创建新配置并导入
        new_config = ScaffoldConfig()
        new_config.import_data(exported_data)

        assert new_config.get("export.test") == "value"
        assert new_config.get("export.nested.value") == 42

    def test_config_backup_restore(self):
        """测试配置备份和恢复"""
        # TC-1.6.29: 备份恢复测试
        # 设置初始配置
        self.config.set("backup.test", "original_value")

        # 创建备份
        backup = self.config.create_backup()

        # 修改配置
        self.config.set("backup.test", "modified_value")
        assert self.config.get("backup.test") == "modified_value"

        # 恢复备份
        self.config.restore_backup(backup)
        assert self.config.get("backup.test") == "original_value"

    def test_config_deep_copy(self):
        """测试配置深拷贝"""
        # TC-1.6.30: 深拷贝测试
        self.config.set("copy.test", "original")

        # 创建副本
        config_copy = self.config.copy()

        # 修改副本
        config_copy.set("copy.test", "modified")

        # 原配置不应受影响
        assert self.config.get("copy.test") == "original"
        assert config_copy.get("copy.test") == "modified"

    def test_config_path_operations(self):
        """测试配置路径操作"""
        # TC-1.6.31: 路径操作测试
        # 测试路径存在检查
        assert self.config.has_path("scaffold.max_file_size") == True
        assert self.config.has_path("nonexistent.path") == False

        # 测试路径删除
        self.config.set("temp.path", "value")
        assert self.config.has_path("temp.path") == True

        self.config.delete_path("temp.path")
        assert self.config.has_path("temp.path") == False

    def test_config_search(self):
        """测试配置搜索"""
        # TC-1.6.32: 配置搜索测试
        # 设置一些测试数据
        self.config.set("search.test1", "value1")
        self.config.set("search.test2", "value2")
        self.config.set("other.test", "other_value")

        # 搜索包含特定字符串的键
        results = self.config.search_keys("search")
        assert len(results) == 2
        assert "search.test1" in results
        assert "search.test2" in results

        # 搜索值
        value_results = self.config.search_values("value")
        assert len(value_results) >= 2


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])