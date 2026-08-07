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
