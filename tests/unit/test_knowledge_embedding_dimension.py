"""Dynamic embedding dimension test for Phase 0-2."""
import pytest
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.core.models import KnowledgeBaseConfig


def test_embedding_dimension_from_config():
    """Test embedding dimension read from config."""
    from unittest.mock import MagicMock
    from daip_live.persistence.database import DatabaseManager

    db = DatabaseManager("sqlite:///:memory:")
    mock_provider = MagicMock()

    config = KnowledgeBaseConfig(
        directory="test_knowledge",
        embedding_dimension=768  # Non-default dimension
    )

    # Should use config dimension
    manager = KnowledgeManager(db, mock_provider, config)
    assert manager.config.embedding_dimension == 768


def test_embedding_dimension_default():
    """Test default embedding dimension when not specified."""
    from daip_live.core.models import KnowledgeBaseConfig

    config = KnowledgeBaseConfig(directory="test_knowledge")
    # Should have default dimension
    assert hasattr(config, 'embedding_dimension')


def test_config_yaml_explicit_embedding_dimension():
    """config.yaml 必须显式声明 embedding_dimension（Wave 0 显式化要求）。

    对齐 src/daip_live/knowledge/manager.py:34 的读取路径；
    默认值 768 已兜底，补键为显式化配置。
    """
    import yaml
    from pathlib import Path

    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    assert config_path.exists(), f"config.yaml not found at {config_path}"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    kb = cfg.get("knowledge_base", {})
    assert "embedding_dimension" in kb, "config.yaml knowledge_base 缺少 embedding_dimension 键"
    assert kb["embedding_dimension"] == 768
