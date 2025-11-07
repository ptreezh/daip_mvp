"""
Test to verify container integration with new debate history tracker
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import tempfile
from daip_live.container import Container


def test_container_integration():
    """Test that the debate history tracker is properly integrated into the container."""
    
    # Create a temporary config file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
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
""")
        config_path = f.name
    
    try:
        # Create container and verify all components can be resolved
        container = Container()
        container.config.from_yaml(config_path)
        
        # Test that all expected components can be created
        db_manager = container.db_manager()
        print(f"✓ Database manager: {type(db_manager).__name__}")
        
        session_manager = container.session_manager()
        print(f"✓ Session manager: {type(session_manager).__name__}")
        
        role_manager = container.role_manager()
        print(f"✓ Role manager: {type(role_manager).__name__}")
        
        model_provider = container.model_provider()
        print(f"✓ Model provider: {type(model_provider).__name__}")
        
        # Test the new debate history tracker component
        debate_history_tracker = container.debate_history_tracker()
        print(f"✓ Debate history tracker: {type(debate_history_tracker).__name__}")
        
        # Verify the tracker works
        assert debate_history_tracker is not None
        print("✓ Debate history tracker successfully retrieved from container")
        
        # Test enhanced debate manager (which uses the tracker)
        enhanced_debate_manager = container.enhanced_debate_manager()
        print(f"✓ Enhanced debate manager: {type(enhanced_debate_manager).__name__}")
        
        # Test debate manager
        debate_manager = container.debate_manager()
        print(f"✓ Debate manager: {type(debate_manager).__name__}")
        
        print("\n✓ All container components resolved successfully")
        
    finally:
        # Clean up temp file
        os.unlink(config_path)


if __name__ == "__main__":
    test_container_integration()
    print("\n🎉 Container Integration Test Passed!")