"""
Test to verify container integration with new debate history tracker
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile

from daip_live.container import Container


def test_container_integration():
    """Test that the debate history tracker is properly integrated into the container."""  # noqa: E501

    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("""
database:
  path: ":memory:"
llm_provider:
  default_model: "mock-model"
  embedding_model: "mock-embedding"
knowledge_base:
  directory: "./test_knowledge"
role_manager:
  roles_dir: "./test_roles"
wiki:
  pages_directory: "./test_wiki"
""")
        config_path = f.name

    try:
        # Create container and verify all components can be resolved
        container = Container()
        # 源码权威: Container 无 config 属性，用 config_manager provider 覆盖
        from daip_live.config import ConfigManager

        container.config_manager.override(ConfigManager(config_path))

        # Test that all expected components can be created
        container.db_manager()

        container.session_manager()

        container.role_manager()

        container.model_provider()

        # Test the new debate history tracker component
        debate_history_tracker = container.debate_history_tracker()

        # Verify the tracker works
        assert debate_history_tracker is not None

        # Test enhanced debate manager (which uses the tracker)
        container.enhanced_debate_manager()

        # Test debate manager
        container.debate_manager()

    finally:
        # Clean up temp file
        os.unlink(config_path)


if __name__ == "__main__":
    test_container_integration()
