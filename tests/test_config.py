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
