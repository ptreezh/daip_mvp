"""Real knowledge manager integration tests.

These tests use the real knowledge manager with real components.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from daip_live.core.models import KnowledgeBaseConfig
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.persistence.database import DatabaseManager


@pytest.fixture
def temp_knowledge_dir():
    """Create a temporary knowledge directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    import shutil

    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_path = Path(temp_file.name)
    temp_file.close()
    db = DatabaseManager(db_path=str(temp_path))
    yield db
    # Cleanup (but keep file for knowledge manager)
    return temp_path


@pytest.fixture
def mock_model_provider():
    """Create a mock model provider."""
    provider = Mock()
    # Mock embedding generation
    provider.get_embedding.return_value = [0.1] * 384  # 384-dim embedding
    return provider


@pytest.fixture
def knowledge_manager(temp_knowledge_dir, temp_db, mock_model_provider):
    """Create a knowledge manager with real components."""
    config = KnowledgeBaseConfig(
        directory=str(temp_knowledge_dir),
        embedding_dimension=384,  # Standard embedding dimension
    )

    manager = KnowledgeManager(
        db_manager=temp_db, model_provider=mock_model_provider, config=config
    )
    return manager


@pytest.mark.integration
class TestRealKnowledgeIntegration:
    """Integration tests using real knowledge manager."""

    def test_knowledge_manager_initialization(self, knowledge_manager):
        """Test knowledge manager initializes correctly."""
        assert knowledge_manager is not None
        assert knowledge_manager.config.embedding_dimension == 384
        assert knowledge_manager.config.directory is not None

    def test_knowledge_directory_exists(self, knowledge_manager, temp_knowledge_dir):
        """Test knowledge directory is set correctly."""
        assert knowledge_manager.knowledge_dir == temp_knowledge_dir

    def test_index_file_path(self, knowledge_manager):
        """Test FAISS index file path is set."""
        assert knowledge_manager.index_path.name == "index.faiss"

    def test_config_validation(self, temp_knowledge_dir, temp_db, mock_model_provider):
        """Test config validation."""
        # Test with missing required field
        with pytest.raises(Exception):  # ValidationError
            config = KnowledgeBaseConfig(
                embedding_dimension=384
                # Missing required 'directory'
            )

        # Test with valid config
        config = KnowledgeBaseConfig(
            directory=str(temp_knowledge_dir), embedding_dimension=768
        )
        assert config.embedding_dimension == 768
        assert config.directory == str(temp_knowledge_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
