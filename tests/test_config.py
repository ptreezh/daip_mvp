import pytest

from daip_live.config import ConfigError, ConfigManager
from daip_live.core.models import AppConfig

VALID_CONFIG_PATH = "tests/config/test_config.yaml"
INVALID_CONFIG_PATH = "tests/config/invalid_config.yaml"
NON_EXISTENT_CONFIG_PATH = "tests/config/non_existent_config.yaml"


def test_load_valid_config():
    """Tests that a valid config file is loaded and parsed correctly."""
    # Arrange
    manager = ConfigManager(config_path=VALID_CONFIG_PATH)

    # Act
    config = manager.get_config()

    # Assert
    assert manager.is_loaded()
    assert isinstance(config, AppConfig)
    assert config.database.path == "test_daip_live.db"
    assert config.llm_provider.default_model == "test_ollama/test_model"
    assert config.knowledge_base.directory == "test_docs/"


def test_load_missing_config_raises_error():
    """Tests that a ConfigError is raised for a missing config file."""
    # Arrange
    manager = ConfigManager(config_path=NON_EXISTENT_CONFIG_PATH)

    # Act & Assert
    with pytest.raises(ConfigError, match="Configuration file not found"):
        manager.get_config()


def test_load_invalid_config_raises_error():
    """Tests that a ConfigError is raised for an invalid config file."""
    # Arrange
    manager = ConfigManager(config_path=INVALID_CONFIG_PATH)

    # Act & Assert
    with pytest.raises(ConfigError, match="Configuration file is invalid"):
        manager.get_config()


def test_get_config_lazy_loads():
    """Tests that get_config() loads the configuration automatically."""
    # Arrange
    manager = ConfigManager(config_path=VALID_CONFIG_PATH)

    # Act
    # Note: We do NOT call manager.load() here
    config = manager.get_config()

    # Assert
    assert manager.is_loaded()
    assert isinstance(config, AppConfig)
    assert config.database.path == "test_daip_live.db"


def test_set_default_model_writes_config(tmp_path):
    """set_default_model 持久化写回 config.yaml 的 default_model。"""
    import yaml

    from daip_live.config import config_manager, set_default_model

    # 用临时 config 文件（含完整 AppConfig 结构避免校验失败）
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "llm_provider:\n"
        "  default_model: ollama/llama3:latest\n"
        "  embedding_model: ollama/nomic-embed-text\n"
        "database:\n"
        "  path: test.db\n"
        "knowledge_base:\n"
        "  directory: docs/\n"
        "  embedding_dimension: 768\n"
        "wiki:\n"
        "  pages_directory: knowledge/wiki/\n",
        encoding="utf-8",
    )

    old_path = config_manager._config_path
    old_config = config_manager._config
    config_manager._config_path = str(cfg_file)
    config_manager._config = None
    try:
        ok = set_default_model("ollama/qwen3.5:4b")
        assert ok is True
        # 验证文件内容（不依赖 get_config 全量校验）
        raw = yaml.safe_load(cfg_file.read_text(encoding="utf-8"))
        assert raw["llm_provider"]["default_model"] == "ollama/qwen3.5:4b"
        # 其余配置不被破坏
        assert raw["llm_provider"]["embedding_model"] == "ollama/nomic-embed-text"
        assert raw["database"]["path"] == "test.db"
    finally:
        config_manager._config_path = old_path
        config_manager._config = old_config
