import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from daip_live.container import Container
from daip_live.knowledge.manager import KnowledgeManager


@pytest.fixture
def mock_config():
    """Provides a mock configuration dictionary for testing."""
    return {
        "database": {"path": ":memory:"},
        "llm_provider": {"default_model": "mock_model", "embedding_model": "mock_embedding"},
        "knowledge_base": {"directory": "/tmp/docs"},
        "role_manager": {"roles_dir": "/tmp/roles"},
    }


def test_container_import_and_instantiation():
    """
    Tests that the Container can be imported and instantiated.
    """
    container = Container()
    assert container is not None

def test_resolve_core_service(mock_config):
    """
    Tests that a core service can be resolved from the container after
    providing a configuration.
    """
    container = Container()
    container.config.from_dict(mock_config)

    knowledge_manager = container.knowledge_manager()

    assert isinstance(knowledge_manager, KnowledgeManager)
    # Verify that the config was injected correctly
    assert str(knowledge_manager.db_manager.engine.url) == "sqlite:///:memory:"